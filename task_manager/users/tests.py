import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from tasks.models import Task

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="John321", password="password!321")


@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_status, expected_users_in_db", (
    # Correct data
    ({"username": "user123", "password": "password123321", "password_confirmation": "password123321"}, 201, 1),
    # Data without passwords
    ({"username": "user321"}, 400, 0),
    # Data without username
    ({"password": "PASORD", "password_confirmation": "PASORD"}, 400, 0),
    # Data with different passwords
    ({"username": "user1", "password": "pas321", "password_confirmation": "pas123"}, 400, 0))
)
def test_user_registration(api_client, data, expected_status, expected_users_in_db):
    url = "/api/users/registration/"
    response = api_client.post(url, data, format="json")

    assert response.status_code == expected_status
    assert User.objects.count() == expected_users_in_db


@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_status", (
    # Correct data
    ({"username": "John321", "password": "password!321"}, 200),
    # User doesn't exist
    ({"username": "Apple34", "password": "Banana"}, 401),
    # Wrong password
    ({"username": "John321", "password": "password?123"}, 401))
)
def test_user_login(api_client, test_user, data, expected_status):
    url = "/api/users/login/"
    response = api_client.post(url, data, format="json")

    assert response.status_code == expected_status

    if response.status_code == 200:
        assert "access" in response.data
        assert "refresh" in response.data 


@pytest.mark.django_db
@pytest.mark.parametrize("is_token_valid, expected_status", (
    # Valid token
    (True, 200),
    # Expired token
    (False, 401))
)
def test_token_refresh(api_client, test_user, is_token_valid, expected_status):
    url = "/api/users/token/refresh/"

    if is_token_valid:
        refresh_token = str(RefreshToken.for_user(test_user))
        data = {"refresh": refresh_token}
    else:
        data = {"refresh": "fake_token"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == expected_status

    if response.status_code == 200:
        assert "access" in response.data


@pytest.mark.django_db
def test_delete_account_with_correct_password(api_client, test_user):
    Task.objects.create(
        title = "Title1",
        description = "123",
        deadline = timezone.now() + timedelta(days=10),
        status = "IP",
        priority = "M",
        user = test_user
    )

    url = "/api/users/delete-account/"
    api_client.force_authenticate(user=test_user)
    data = {"password": "password!321"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 204
    assert Task.objects.count() == 0
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_delete_account_with_wrong_password(api_client, test_user):
    url = "/api/users/delete-account/"
    api_client.force_authenticate(user=test_user)
    data = {"password": "wrong_password"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_change_password(api_client, test_user):
    url = "/api/users/change-password/"
    api_client.force_authenticate(user=test_user)
    data = {"password": "password!321", 
            "new_password": "password!123", 
            "new_password_confirmation": "password!123"
    }
    response = api_client.patch(url, data, format="json")
    test_user.refresh_from_db()

    assert response.status_code == 200
    assert test_user.check_password("password!123")


@pytest.mark.django_db
@pytest.mark.parametrize("data", (
    # The new passwords are not the same
    {"password": "password!321", "new_password": "pass123", "new_password_confirmation": "pass45"},
    # The old password is incorrect
    {"password": "password", "new_password": "pass123", "new_password_confirmation": "pass123"}
))
def test_change_password_incorrect_input_data(api_client, test_user, data):
    url = "/api/users/change-password/"
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(url, data, format="json")
    test_user.refresh_from_db()

    assert response.status_code == 400
    assert test_user.check_password("password!321")
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


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
def test_user_login(api_client, data, expected_status):
    User.objects.create_user(username="John321", password="password!321")
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
def test_token_refresh(api_client, is_token_valid, expected_status):
    user = User.objects.create_user(username="John321", password="password!321")
    url = "/api/users/token/refresh/"

    if is_token_valid:
        refresh_token = str(RefreshToken.for_user(user))
        data = {"refresh": refresh_token}
    else:
        data = {"refresh": "fake_token"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == expected_status

    if response.status_code == 200:
        assert "access" in response.data
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Task

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="testpassword!")

@pytest.fixture
def test_task(db, test_user):
    return Task.objects.create(
        title = "Title1",
        description = "123",
        deadline = timezone.now() + timedelta(days=10),
        status = "IP",
        priority = "M",
        user = test_user
    )


@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_status, expected_tasks_in_db",(
    # Full correct data
    ({"title": "Title1", "description": "Task description", 
      "deadline": timezone.now() + timedelta(days=30),
      "status": "IP", "priority": "M"}, 201, 1),
    # Minimum correct data
    ({"title": "Title2", "description": "", 
      "status": "TD", "priority": "L"}, 201, 1),
    # Without required data 
    ({"title": "Title3", "description": "",
      "priority": "H"}, 400, 0),
    # Incorrect data
    ({"title": "Title4", "description": "abc",
      "deadline": timezone.now() - timedelta(days=2),
      "status": "Finished", "priority": "K"}, 400, 0))    
)
def test_create_task_authenticated(api_client, test_user, data, expected_status, expected_tasks_in_db):
    url = "/api/tasks/"
    api_client.force_authenticate(user=test_user)
    response = api_client.post(url, data, format="json") 

    assert response.status_code == expected_status
    assert Task.objects.count() == expected_tasks_in_db

    if expected_tasks_in_db == 1:
        new_task = Task.objects.first()
        assert new_task.user == test_user


@pytest.mark.django_db
def test_create_task_unauthenticated(api_client, test_user):
    url = "/api/tasks/"
    data = {"title": "Title1", "description": "Task description", 
      "deadline": timezone.now() + timedelta(days=30),
      "status": "IP", "priority": "M"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == 401
    assert Task.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_status", (
    # Correct data
    ({"description": "description321", "deadline": timezone.now() + timedelta(days=30)}, 200),
    # Incorrect data
    ({"status": "Finished"}, 400))
)
def test_update_task_authenticated(api_client, test_task, data, expected_status):
    url = f"/api/tasks/{test_task.id}/"
    api_client.force_authenticate(user=test_task.user)
    response = api_client.patch(url, data, format="json")

    assert response.status_code == expected_status

    if expected_status == 200:
        test_task.refresh_from_db()
        assert test_task.description == "description321"


@pytest.mark.django_db
def test_update_task_unauthenticated(api_client, test_task):
    url = f"/api/tasks/{test_task.id}/"
    data = {"description": "description321", "deadline": timezone.now() + timedelta(days=30)}
    response = api_client.patch(url, data, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_task_authenticated(api_client, test_task):
    url = f"/api/tasks/{test_task.id}/"
    api_client.force_authenticate(user=test_task.user)
    response = api_client.delete(url)

    assert response.status_code == 204
    assert Task.objects.count() == 0


@pytest.mark.django_db
def test_delete_task_unauthenticated(api_client, test_task):
    url = f"/api/tasks/{test_task.id}/"
    response = api_client.delete(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_task_detail(api_client, test_task):
    url = f"/api/tasks/{test_task.id}/"
    api_client.force_authenticate(user=test_task.user)
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == test_task.id
    assert response.data["title"] == test_task.title
    assert response.data["status"] == test_task.status


@pytest.mark.django_db
def test_get_task_detail_by_other_user(api_client, test_task):
    other_user = User.objects.create_user(username="other_user", password="12345")

    url = f"/api/tasks/{test_task.id}/"
    api_client.force_authenticate(user=other_user)
    response = api_client.get(url)

    assert response.status_code == 404
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
      "deadline": timezone.now() + timedelta(days=2),
      "status": "Finished", "priority": "K"}, 400, 0))    
)
def test_create_task_authenticated(api_client, test_user, data, expected_status, expected_tasks_in_db):
    url = "/api/tasks/creation/"
    api_client.force_authenticate(user=test_user)
    response = api_client.post(url, data, format="json") 

    assert response.status_code == expected_status
    assert Task.objects.count() == expected_tasks_in_db

    if expected_tasks_in_db == 1:
        new_task = Task.objects.first()
        assert new_task.user == test_user
    
from django.urls import path
from .views import TaskCreationView

urlpatterns = [
    path("creation/", TaskCreationView.as_view(), name="creation"),
]
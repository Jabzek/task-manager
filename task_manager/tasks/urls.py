from django.urls import path
from .views import TaskCreationView, TaskDetailView

urlpatterns = [
    path("creation/", TaskCreationView.as_view(), name="creation"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
]
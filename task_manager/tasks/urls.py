from django.urls import path
from .views import TaskDetailView, TaskListView

urlpatterns = [
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("", TaskListView.as_view(), name="task_list")
]
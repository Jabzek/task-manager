from django.db import models
from users.models import User

class Task(models.Model):
    task_status = {"TD": "To Do",
               "IP": "In Progress",
               "D": "Done"}

    task_priority = {"L": "Low",
                 "M": "Medium",
                 "H": "High"}

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)    
    status = models.CharField(max_length=2, choices=task_status)
    priority = models.CharField(max_length=1, choices=task_priority)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
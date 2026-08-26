from rest_framework import serializers
from .models import Task

class TaskCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "deadline", "status", "priority", "created_at")
        read_only_fields = ("id", "created_at")
from rest_framework import serializers
from django.utils import timezone 
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "deadline", "status", "priority", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("The deadline can not be from past.")
        return value
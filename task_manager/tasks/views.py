from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import TaskSerializer
from .models import Task

class TaskCreationView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class TaskDetailView(APIView):
    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        serializer = TaskSerializer(instance=task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        serializer = TaskSerializer(instance=task)
        return Response(serializer.data, status=status.HTTP_200_OK)
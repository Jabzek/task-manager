from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from rest_framework.pagination import PageNumberPagination
from .serializers import TaskSerializer, TaskListSerializer
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


class StandardResultSetPagination(PageNumberPagination):
    page_size = 15


class TaskListView(APIView):
    def get(self, request):
        queryset = Task.objects.filter(user=request.user)

        statuses = request.query_params.getlist("status")
        if statuses:
            queryset = queryset.filter(status__in=statuses)

        priorities = request.query_params.getlist("priority")
        if priorities:
            queryset = queryset.filter(priority__in=priorities)

        queryset = queryset.order_by(
            Case(
                When(status="D", then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "deadline",
            "status"
        )

        paginator = StandardResultSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = TaskListSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)
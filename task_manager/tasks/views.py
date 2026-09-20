from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import TaskSerializer, TaskListSerializer
from .models import Task

class TaskDetailView(APIView):
    @extend_schema(
        description="Partial task editing. Allows you to change selected fields without overwriting the entire object.",
        request=TaskSerializer,
        responses={200: TaskSerializer}
    )
    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        serializer = TaskSerializer(instance=task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        description="Permanently deletes the task from the database.",
        responses={204: None}
    )
    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @extend_schema(
        description="Returns full details of the selected task based on its ID.",
        responses={200: TaskSerializer}
    )
    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, user=request.user)
        serializer = TaskSerializer(instance=task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StandardResultSetPagination(PageNumberPagination):
    page_size = 15


class TaskListView(APIView):
    @extend_schema(
        description="Downloading and filtering the tasks list. Returns a" \
        " paged list of tasks for the logged in user.",
        parameters=[
            OpenApiParameter(name="status", description="Filter by status", type=OpenApiTypes.STR, many=True),
            OpenApiParameter(name="priority", description="Filter by priorities", type=OpenApiTypes.STR, many=True),
            OpenApiParameter(name="page", description="Page number (pagination)", type=OpenApiTypes.INT)
        ],
        responses=TaskListSerializer(many=True)
    )
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


    @extend_schema(
        description="Create a new task.",
        request=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
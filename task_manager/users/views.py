from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        description="Creates a new user account in the system. This endpoint is public and does not require a JWT token.",
        request=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        user_data = request.data
        serializer = UserSerializer(data=user_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
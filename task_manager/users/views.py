from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .serializers import UserCreateSerializer, AccountDeleteSerializer

class RegistrationView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        description="Creates a new user account in the system. This endpoint is public and does not require a JWT token.",
        request=UserCreateSerializer,
        responses={201: UserCreateSerializer}
    )
    def post(self, request):
        user_data = request.data
        serializer = UserCreateSerializer(data=user_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    @extend_schema(
        description="Deletes the user account.",
        request=AccountDeleteSerializer,
        responses={204: None}
    )
    def post(self, request):
        serializer = AccountDeleteSerializer(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data.get("password")
            user = request.user

            if not user.check_password(password):
                return Response(
                    {"detail": "Provided password is not correct."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
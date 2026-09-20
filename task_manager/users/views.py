from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        user_data = request.data
        serializer = UserSerializer(data=user_data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "The account has been created"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
from django.urls import path
from .views import RegistrationView, DeleteAccountView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account")
]
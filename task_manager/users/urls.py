from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/registration/", RegisterView.as_view(), name="registration"),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh")
]
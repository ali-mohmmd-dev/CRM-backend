from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CreateUserSerializer,
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class RegisterOrganizationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class CreateUserView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

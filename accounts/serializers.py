from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Organization

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'organization_name', 'phone_number']

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name')
        password = validated_data.pop('password')

        if Organization.objects.filter(name=org_name).exists():
            raise serializers.ValidationError({
                'organization_name': (
                    'An organization with this name already exists. '
                    'Please contact your administrator to be invited.'
                ),
            })

        organization = Organization.objects.create(name=org_name)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            organization=organization,
        )
        user.set_password(password)
        user.save()
        return user


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            organization=validated_data.get('organization'),
        )
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'organization']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

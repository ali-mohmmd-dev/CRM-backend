from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name','created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'organization_name', 'phone_number']

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name')
        password = validated_data.pop('password')

        # Create or get organization (logic can be adjusted based on requirements)
        organization, created = Organization.objects.get_or_create(name=org_name)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            organization=organization
        )
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'organization']

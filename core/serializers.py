from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Organization, Staff, Work, Customer, Lead

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
        if Organization.objects.filter(name=org_name).exists():
            raise serializers.ValidationError({"organization_name": "An organization with this name already exists. Please contact your administrator to be invited."})
            
        organization = Organization.objects.create(name=org_name)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            organization=organization
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
            organization=validated_data.get('organization')
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


class StaffSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'role', 'phone', 'createdAt']


class WorkSerializer(serializers.ModelSerializer):
    assignedTo = serializers.PrimaryKeyRelatedField(
        source='assigned_to',
        queryset=Staff.objects.none(),
        allow_null=True,
        required=False,
    )
    dueDate = serializers.DateField(source='due_date')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Work
        fields = [
            'id',
            'title',
            
            'description',
            'assignedTo',
            'status',
            'priority',
            'dueDate',
            'createdAt',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.organization_id:
            self.fields['assignedTo'].queryset = Staff.objects.filter(
                organization=request.user.organization
            )


class CustomerSerializer(serializers.ModelSerializer):
    lastContact = serializers.DateField(source='last_contact', allow_null=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'company',
            'email',
            'phone',
            'status',
            'lastContact',
            'notes',
            'createdAt',
        ]


class LeadSerializer(serializers.ModelSerializer):
    calledAt = serializers.DateTimeField(source='called_at', allow_null=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    value = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'company',
            'email',
            'phone',
            'source',
            'status',
            'called',
            'calledAt',
            'notes',
            'value',
            'createdAt',
        ]

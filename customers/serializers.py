from rest_framework import serializers

from .models import Customer


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

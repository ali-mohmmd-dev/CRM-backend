from rest_framework import serializers

from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'role', 'phone', 'createdAt']

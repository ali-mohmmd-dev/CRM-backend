from rest_framework import serializers

from .models import Lead


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

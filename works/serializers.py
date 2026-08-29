from rest_framework import serializers

from staff.models import Staff

from .models import Work


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

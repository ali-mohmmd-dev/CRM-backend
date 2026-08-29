from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import OrganizationScopedViewSet, publish_after_commit
from events import EventNames

from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(OrganizationScopedViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    @action(detail=True, methods=['post'], url_path='mark-called')
    def mark_called(self, request, pk=None):
        lead = self.get_object()
        lead.called = True
        lead.called_at = timezone.now()
        if lead.status == Lead.STATUS_NEW:
            lead.status = Lead.STATUS_CONTACTED
        lead.save(update_fields=['called', 'called_at', 'status', 'updated_at'])
        publish_after_commit(
            'leads',
            EventNames.LEAD_CALLED,
            lead.organization_id,
            {
                'lead_id': lead.id,
                'organization_id': lead.organization_id,
                'status': lead.status,
                'called_at': lead.called_at.isoformat(),
            },
            key=str(lead.id),
        )
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=['post'], url_path='convert-to-customer')
    def convert_to_customer(self, request, pk=None):
        lead = self.get_object()
        lead.status = Lead.STATUS_CONVERTED
        lead.save(update_fields=['status', 'updated_at'])
        publish_after_commit(
            'leads',
            EventNames.LEAD_CONVERTED,
            lead.organization_id,
            {
                'lead_id': lead.id,
                'organization_id': lead.organization_id,
                'name': lead.name,
                'company': lead.company,
                'email': lead.email,
                'phone': lead.phone,
                'notes': lead.notes,
                'last_contact': timezone.localdate().isoformat(),
            },
            key=str(lead.id),
        )
        return Response(LeadSerializer(lead).data, status=status.HTTP_202_ACCEPTED)

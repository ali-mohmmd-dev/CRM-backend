from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import OrganizationScopedViewSet, publish_after_commit
from events import EventNames

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(OrganizationScopedViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        customer = self.get_object()
        customer.last_contact = timezone.localdate()
        customer.save(update_fields=['last_contact', 'updated_at'])
        publish_after_commit(
            'customers',
            EventNames.CUSTOMER_FOLLOWED_UP,
            customer.organization_id,
            {
                'customer_id': customer.id,
                'organization_id': customer.organization_id,
                'last_contact': customer.last_contact.isoformat(),
            },
            key=str(customer.id),
        )
        return Response(self.get_serializer(customer).data)

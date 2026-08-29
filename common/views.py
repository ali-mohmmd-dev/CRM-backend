from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from events import publish


def publish_after_commit(topic_key, event_type, organization_id, payload, *, key=None):
    def _publish():
        try:
            publish(topic_key, event_type, organization_id, payload, key=key)
        except Exception:
            pass

    transaction.on_commit(_publish)


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.organization_id:
            return self.queryset.none()
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

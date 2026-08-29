from common.views import OrganizationScopedViewSet, publish_after_commit
from events import EventNames

from .models import Work
from .serializers import WorkSerializer


class WorkViewSet(OrganizationScopedViewSet):
    queryset = Work.objects.select_related('assigned_to')
    serializer_class = WorkSerializer

    def perform_create(self, serializer):
        work = serializer.save(organization=self.request.user.organization)
        publish_after_commit(
            'works',
            EventNames.WORK_CREATED,
            work.organization_id,
            {
                'work_id': work.id,
                'organization_id': work.organization_id,
                'title': work.title,
                'status': work.status,
                'assigned_to_id': work.assigned_to_id,
            },
            key=str(work.id),
        )

    def perform_update(self, serializer):
        previous = self.get_object()
        previous_assigned_to_id = previous.assigned_to_id
        previous_status = previous.status
        work = serializer.save()

        if previous_assigned_to_id != work.assigned_to_id:
            publish_after_commit(
                'works',
                EventNames.WORK_ASSIGNED,
                work.organization_id,
                {
                    'work_id': work.id,
                    'organization_id': work.organization_id,
                    'assigned_to_id': work.assigned_to_id,
                    'previous_assigned_to_id': previous_assigned_to_id,
                },
                key=str(work.id),
            )

        if previous_status != work.status:
            publish_after_commit(
                'works',
                EventNames.WORK_STATUS_CHANGED,
                work.organization_id,
                {
                    'work_id': work.id,
                    'organization_id': work.organization_id,
                    'status': work.status,
                    'previous_status': previous_status,
                },
                key=str(work.id),
            )

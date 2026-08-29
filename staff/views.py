from common.views import OrganizationScopedViewSet

from .models import Staff
from .serializers import StaffSerializer


class StaffViewSet(OrganizationScopedViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

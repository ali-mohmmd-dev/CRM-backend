from rest_framework.routers import DefaultRouter

from .views import StaffViewSet

router = DefaultRouter()
router.register('staff', StaffViewSet, basename='staff')

urlpatterns = router.urls

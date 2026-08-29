from rest_framework.routers import DefaultRouter

from .views import WorkViewSet

router = DefaultRouter()
router.register('works', WorkViewSet, basename='works')

urlpatterns = router.urls

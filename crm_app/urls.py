from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CalendarView,
    CustomerViewSet,
    DashboardActivityView,
    DashboardStatsView,
    LeadViewSet,
    StaffViewSet,
    WorkViewSet,
)

router = DefaultRouter()
router.register('staff', StaffViewSet, basename='staff')
router.register('works', WorkViewSet, basename='works')
router.register('customers', CustomerViewSet, basename='customers')
router.register('leads', LeadViewSet, basename='leads')

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/activity/', DashboardActivityView.as_view(), name='dashboard-activity'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
]

urlpatterns += router.urls

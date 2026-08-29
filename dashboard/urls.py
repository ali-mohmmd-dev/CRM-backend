from django.urls import path

from .views import CalendarView, DashboardActivityView, DashboardStatsView

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/activity/', DashboardActivityView.as_view(), name='dashboard-activity'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
]

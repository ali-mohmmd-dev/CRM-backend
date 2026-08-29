from datetime import datetime

from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import Customer
from leads.models import Lead
from leads.serializers import LeadSerializer
from staff.models import Staff
from works.models import Work
from works.serializers import WorkSerializer


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = request.user.organization
        works = Work.objects.filter(organization=organization)
        leads = Lead.objects.filter(organization=organization)
        total_works = works.count()
        total_leads = leads.count()
        completed_works = works.filter(status=Work.STATUS_COMPLETED).count()
        converted_leads = leads.filter(status=Lead.STATUS_CONVERTED).count()

        return Response({
            'totalStaff': Staff.objects.filter(organization=organization).count(),
            'totalWorks': total_works,
            'completedWorks': completed_works,
            'pendingWorks': works.filter(status=Work.STATUS_PENDING).count(),
            'totalCustomers': Customer.objects.filter(organization=organization).count(),
            'totalLeads': total_leads,
            'convertedLeads': converted_leads,
            'uncalledLeads': leads.filter(called=False).count(),
            'workCompletionRate': round((completed_works / total_works) * 100) if total_works else 0,
            'leadConversionRate': round((converted_leads / total_leads) * 100) if total_leads else 0,
        })


class DashboardActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = request.user.organization
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        lead_counts = {
            row['created_at__month']: row['count']
            for row in Lead.objects.filter(organization=organization)
            .values('created_at__month')
            .annotate(count=Count('id'))
        }
        customer_counts = {
            row['created_at__month']: row['count']
            for row in Customer.objects.filter(organization=organization)
            .values('created_at__month')
            .annotate(count=Count('id'))
        }
        work_counts = {
            row['created_at__month']: row['count']
            for row in Work.objects.filter(organization=organization)
            .values('created_at__month')
            .annotate(count=Count('id'))
        }

        return Response([
            {
                'month': months[index - 1],
                'leads': lead_counts.get(index, 0),
                'customers': customer_counts.get(index, 0),
                'works': work_counts.get(index, 0),
            }
            for index in range(1, 13)
        ])


class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = request.user.organization
        selected_date = request.query_params.get('date')
        works = Work.objects.filter(organization=organization)
        leads = Lead.objects.filter(organization=organization)

        dates_with_items = set()
        dates_with_items.update(works.values_list('due_date', flat=True))
        for created_at, called_at in leads.values_list('created_at', 'called_at'):
            dates_with_items.add(created_at.date())
            if called_at:
                dates_with_items.add(called_at.date())

        if selected_date:
            parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            parsed_date = timezone.localdate()

        selected_works = works.filter(due_date=parsed_date)
        selected_leads = leads.filter(created_at__date=parsed_date) | leads.filter(called_at__date=parsed_date)

        return Response({
            'date': parsed_date.isoformat(),
            'works': WorkSerializer(selected_works, many=True).data,
            'leads': LeadSerializer(selected_leads.distinct(), many=True).data,
            'datesWithItems': sorted(date.isoformat() for date in dates_with_items if date),
        })

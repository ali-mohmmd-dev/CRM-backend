from datetime import datetime

from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Staff, Work, Customer, Lead
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    CreateUserSerializer,
    StaffSerializer,
    WorkSerializer,
    CustomerSerializer,
    LeadSerializer,
)

class RegisterOrganizationView(generics.CreateAPIView):
    """
    API endpoint that allows a user to register a new organization/company.
    This creates both the Organization and the Admin User for that organization.
    """
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class CreateUserView(generics.CreateAPIView):
    """
    API endpoint to allow an organization member (or admin) to create a new user 
    for their own organization.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        # Automatically assign the new user to the creator's organization
        serializer.save(organization=self.request.user.organization)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.organization_id:
            return self.queryset.none()
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class StaffViewSet(OrganizationScopedViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class WorkViewSet(OrganizationScopedViewSet):
    queryset = Work.objects.select_related('assigned_to')
    serializer_class = WorkSerializer


class CustomerViewSet(OrganizationScopedViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        customer = self.get_object()
        customer.last_contact = timezone.localdate()
        customer.save(update_fields=['last_contact', 'updated_at'])
        return Response(self.get_serializer(customer).data)


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
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=['post'], url_path='convert-to-customer')
    def convert_to_customer(self, request, pk=None):
        lead = self.get_object()
        customer, _ = Customer.objects.get_or_create(
            organization=lead.organization,
            email=lead.email,
            defaults={
                'name': lead.name,
                'company': lead.company,
                'phone': lead.phone,
                'status': Customer.STATUS_ACTIVE,
                'last_contact': timezone.localdate(),
                'notes': lead.notes,
            },
        )
        lead.status = Lead.STATUS_CONVERTED
        lead.save(update_fields=['status', 'updated_at'])
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


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

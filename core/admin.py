from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Customer, Lead, Organization, Staff, User, Work


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('CRM', {'fields': ('organization', 'phone_number')}),
    )
    list_display = ('username', 'email', 'organization', 'is_staff', 'is_active')
    list_filter = UserAdmin.list_filter + ('organization',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'phone', 'organization')
    list_filter = ('organization', 'role')
    search_fields = ('name', 'email', 'role')


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'priority', 'due_date', 'organization')
    list_filter = ('organization', 'status', 'priority', 'due_date')
    search_fields = ('title', 'description')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'last_contact', 'organization')
    list_filter = ('organization', 'status', 'last_contact')
    search_fields = ('name', 'company', 'email')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'called', 'value', 'organization')
    list_filter = ('organization', 'status', 'called', 'source')
    search_fields = ('name', 'company', 'email', 'source')

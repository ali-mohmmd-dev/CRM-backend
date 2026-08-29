from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Organization, User


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

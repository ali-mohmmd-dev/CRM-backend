from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'last_contact', 'organization')
    list_filter = ('organization', 'status', 'last_contact')
    search_fields = ('name', 'company', 'email')

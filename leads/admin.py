from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'called', 'value', 'organization')
    list_filter = ('organization', 'status', 'called', 'source')
    search_fields = ('name', 'company', 'email', 'source')

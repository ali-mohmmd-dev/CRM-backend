from django.contrib import admin

from .models import Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'priority', 'due_date', 'organization')
    list_filter = ('organization', 'status', 'priority', 'due_date')
    search_fields = ('title', 'description')

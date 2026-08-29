from django.db import models

from common.models import OrganizationOwnedModel


class Work(OrganizationOwnedModel):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'staff.Staff',
        on_delete=models.SET_NULL,
        related_name='works',
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField()

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title

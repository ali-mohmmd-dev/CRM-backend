from django.db import models

from common.models import OrganizationOwnedModel


class Lead(OrganizationOwnedModel):
    STATUS_NEW = 'new'
    STATUS_CONTACTED = 'contacted'
    STATUS_QUALIFIED = 'qualified'
    STATUS_CONVERTED = 'converted'
    STATUS_LOST = 'lost'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_CONTACTED, 'Contacted'),
        (STATUS_QUALIFIED, 'Qualified'),
        (STATUS_CONVERTED, 'Converted'),
        (STATUS_LOST, 'Lost'),
    ]

    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    source = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    called = models.BooleanField(default=False)
    called_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'email'],
                name='unique_lead_email_per_organization',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.company})'

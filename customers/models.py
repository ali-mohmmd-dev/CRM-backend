from django.db import models

from common.models import OrganizationOwnedModel


class Customer(OrganizationOwnedModel):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_PROSPECT = 'prospect'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_PROSPECT, 'Prospect'),
    ]

    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROSPECT)
    last_contact = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['company', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'email'],
                name='unique_customer_email_per_organization',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.company})'

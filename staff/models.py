from django.db import models

from common.models import OrganizationOwnedModel


class Staff(OrganizationOwnedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'email'],
                name='unique_staff_email_per_organization',
            )
        ]

    def __str__(self):
        return self.name

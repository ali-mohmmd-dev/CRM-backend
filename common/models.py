from django.db import models


class OrganizationOwnedModel(models.Model):
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

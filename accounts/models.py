from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

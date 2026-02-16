from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Link user to an organization
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True
    )
    
    # Add any other custom user fields here
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

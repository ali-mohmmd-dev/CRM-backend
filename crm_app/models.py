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


class OrganizationOwnedModel(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
        Staff,
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

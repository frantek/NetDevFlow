from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extends the standard User model to support roles required by the rubric (LO3).
    """
    ROLE_CHOICES = [
        ('MANAGER', 'Infrastructure Manager'),
        ('TECHNICIAN', 'Field Technician'),
        ('READONLY', 'Read-Only Auditor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='READONLY')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Device(models.Model):
    """
    Represents a physical or virtual network asset.
    The central node for the NetDevFlow inventory.
    """
    DEVICE_TYPES = [
        ('SERVER', 'Server'),
        ('SWITCH', 'Switch'),
        ('ROUTER', 'Router'),
        ('FIREWALL', 'Firewall'),
        ('STORAGE', 'Storage Array'),
    ]

    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('MAINTENANCE', 'Maintenance'),
        ('OFFLINE', 'Offline'),
        ('DECOMMISSIONED', 'Decommissioned'),
    ]

    hostname = models.CharField(max_length=255, unique=True, help_text="FQDN or unique hostname")
    model_name = models.CharField(max_length=100, verbose_name="Hardware Model")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='SERVER')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONLINE')
    location = models.CharField(max_length=255, help_text="Rack ID, Row, or Data Center Room")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hostname']

    def __str__(self):
        return f"{self.hostname} ({self.get_device_type_display()})"


class IPAddress(models.Model):
    """
    Manages IP allocations for devices. 
    One device can have multiple IPs (e.g. Management, Traffic, Storage).
    """
    address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, unique=True)
    subnet_mask = models.CharField(max_length=20, default="255.255.255.0")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='ip_addresses')
    is_primary = models.BooleanField(default=False, help_text="Main management IP")

    def clean(self):
        """Custom validation to ensure only one primary IP per device (LO1.4 Logic)."""
        if self.is_primary:
            exists = IPAddress.objects.filter(device=self.device, is_primary=True).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError("This device already has a primary IP address assigned.")

    def __str__(self):
        return self.address


class MaintenanceTicket(models.Model):
    """
    Tracks incidents and maintenance logs for specific hardware assets.
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low / Routine'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical / Outage'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=15, choices=SEVERITY_CHOICES, default='LOW')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='tickets')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id}: {self.title} ({self.device.hostname})"

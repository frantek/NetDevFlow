from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    # Use GenericIPAddressField for built-in IPv4/IPv6 validation (LO8 optimization)
    address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, unique=True)
    subnet_mask = models.CharField(max_length=20, default="255.255.255.0")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='ip_addresses')
    is_primary = models.BooleanField(default=False, help_text="Main management IP")

    def clean(self):
        """Custom validation to ensure only one primary IP per device."""
        if self.is_primary:
            exists = IPAddress.objects.filter(device=self.device, is_primary=True).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError("This device already has a primary IP address assigned.")

    def __str__(self):
        return self.address


class MaintenanceTicket(models.Model):
    """
    Tracks incidents and maintenance logs for specific hardware assets.
    Provides the audit trail for hardware repairs.
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
    
    # Relational link to the Device (LO7 Requirement)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='tickets')
    
    # Linked to User for accountability
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id}: {self.title} ({self.device.hostname})"

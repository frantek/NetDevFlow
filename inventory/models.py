from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Role-Based Access Profile ---


class Profile(models.Model):
    """Extends User model with role support.

    Supports LO3 requirements: Managers, Technicians, Auditors.
    """

    ROLE_CHOICES = [
        ('MANAGER', 'Infrastructure Manager'),
        ('TECHNICIAN', 'Field Technician'),
        ('READONLY', 'Read-Only Auditor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='READONLY'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Defensive signal to create profile when a new User is created.
    Uses get_or_create to prevent IntegrityErrors when using Admin Inlines.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # Ensure profile exists for existing users (e.g., legacy)
        if not hasattr(instance, 'profile'):
            Profile.objects.get_or_create(user=instance)


# --- DCIM Hierarchy Models (LO7 & Professional Domain) ---


class DataCenter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    physical_address = models.TextField(blank=True)
    contact_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Row(models.Model):
    name = models.CharField(max_length=50)
    data_center = models.ForeignKey(
        DataCenter, on_delete=models.CASCADE, related_name='rows'
    )

    def __str__(self):
        return f"{self.data_center.name} - Row {self.name}"


class Rack(models.Model):
    name = models.CharField(max_length=50)
    row = models.ForeignKey(
        Row, on_delete=models.CASCADE, related_name='racks'
    )
    ru_capacity = models.PositiveIntegerField(
        default=42, verbose_name="Rack Units (U)"
    )

    def __str__(self):
        return (
            f"{self.row.data_center.name} | {self.row.name} | Rack {self.name}"
        )

    def get_available_units(self):
        """Calculates free RU space in the rack."""
        occupied = sum(device.size for device in self.devices.all())
        return self.ru_capacity - occupied


# --- Enhanced Asset Model ---


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
        ('PATCH_PANEL', 'Patch Panel'),
    ]

    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('MAINTENANCE', 'Maintenance'),
        ('OFFLINE', 'Offline'),
        ('DECOMMISSIONED', 'Decommissioned'),
    ]

    hostname = models.CharField(max_length=255, unique=True)
    model_name = models.CharField(max_length=100)  # noqa: E501
    device_type = models.CharField(
        max_length=20, choices=DEVICE_TYPES, default='SERVER'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ONLINE'
    )

    # DCIM Placement
    rack = models.ForeignKey(
        Rack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices',
    )
    position = models.PositiveIntegerField(
        null=True, blank=True, help_text="Starting RU (bottom-up)"
    )
    size = models.PositiveIntegerField(
        default=1, help_text="Height in Rack Units (U)"
    )

    # Visual Documentation
    device_image = models.ImageField(
        upload_to='device_photos/', blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hostname']

    def clean(self):
        """Validation for Rack Unit collisions (LO1.4)."""
        if self.rack and self.position:
            if self.position + self.size - 1 > self.rack.ru_capacity:
                msg = (
                    f'Device exceeds rack capacity '
                    f'{self.rack.ru_capacity}U.'
                )
                raise ValidationError(msg)

            # Check for overlaps
            overlaps = Device.objects.filter(rack=self.rack).exclude(
                pk=self.pk
            )
            for other in overlaps:
                pos_ok = (
                    self.position + self.size <= other.position
                    or self.position >= other.position + other.size
                )
                if not pos_ok:
                    msg = f"Collision with {
                        other.hostname} at RU {
                        other.position}."
                    raise ValidationError(msg)

    def __str__(self):
        return f"{self.hostname} ({self.size}U)"


# --- IPAM & Ticketing ---


class IPAddress(models.Model):
    """
    Manages IP allocations for devices.
    One device can have multiple IPs (e.g. Management, Traffic, Storage).
    """

    address = models.GenericIPAddressField(
        protocol='both', unpack_ipv4=True, unique=True
    )
    subnet_mask = models.CharField(max_length=20, default="255.255.255.0")
    vrf = models.ForeignKey(
        'VRF',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ips',
    )
    device = models.ForeignKey(
        'Device',
        on_delete=models.CASCADE,
        related_name='ip_addresses',
        null=True,
        blank=True,
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"

    def __str__(self):
        return f"{self.address} ({self.vrf.name if self.vrf else 'Global'})"


class VRF(models.Model):
    """Virtual Routing and Forwarding for multi-tenant isolation."""

    name = models.CharField(max_length=100, unique=True)
    rd = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Route Distinguisher",
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "VRF"
        verbose_name_plural = "VRFs"

    def __str__(self):
        return f"{self.name} (RD: {self.rd})" if self.rd else self.name


class VLAN(models.Model):
    """Layer 2 Broadcast Domains, scoped per Site (DataCenter)."""

    vid = models.PositiveIntegerField(verbose_name="VLAN ID")
    name = models.CharField(max_length=100)
    data_center = models.ForeignKey(
        DataCenter,
        on_delete=models.CASCADE,
        related_name='vlans',
        null=True,
        blank=True,
    )

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESERVED', 'Reserved'),
        ('DEPRECATED', 'Deprecated'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ACTIVE'
    )

    class Meta:
        unique_together = ('vid', 'data_center')
        ordering = ['vid']

    def __str__(self):
        dc_name = self.data_center.name if self.data_center else 'Global'
        return f"VLAN {self.vid}: {self.name} ({dc_name})"


class Prefix(models.Model):
    """Subnet containers (e.g., 10.0.0.0/24) for IPAM organization."""

    prefix = models.CharField(
        max_length=50, help_text="CIDR format: 192.168.1.0/24"
    )
    vrf = models.ForeignKey(
        VRF,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prefixes',
    )
    vlan = models.ForeignKey(
        VLAN,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prefixes',
    )
    site = models.ForeignKey(
        DataCenter,
        on_delete=models.CASCADE,
        related_name='prefixes',
        null=True,
        blank=True,
    )

    STATUS_CHOICES = [
        ('CONTAINER', 'Container'),
        ('ACTIVE', 'Active'),
        ('RESERVED', 'Reserved'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ACTIVE'
    )

    class Meta:
        verbose_name_plural = "Prefixes"

    def __str__(self):
        return f"{self.prefix} ({self.vrf.name if self.vrf else 'Global'})"


# --- Ticket Threading & Maintenance Models ---


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
    severity = models.CharField(
        max_length=15, choices=SEVERITY_CHOICES, default='LOW'
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='OPEN'
    )
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='tickets'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets',
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def latest_activity(self):
        """Returns the latest update or initial description."""
        last_update = self.updates.order_by('-created_at').first()
        return last_update.comment if last_update else self.description

    def get_timeline(self):
        """
        Returns a sorted list of all activity (Root description + Updates).
        Useful for rendering a GitHub-style issue thread.
        """
        timeline = [
            {
                'author': self.created_by,
                'content': self.description,
                'timestamp': self.created_at,
                'is_root': True,
            }
        ]
        for update in self.updates.all():
            timeline.append(
                {
                    'author': update.author,
                    'content': update.comment,
                    'timestamp': update.created_at,
                    'is_root': False,
                }
            )
        # Sort by timestamp to ensure chronological order
        return sorted(timeline, key=lambda x: x['timestamp'])

    def __str__(self):
        return f"#{self.id}: {self.title}"


class TicketUpdate(models.Model):
    """
    Represents a single update or comment in a ticket's timeline.
    This enables the GitHub-style issue thread functionality.
    """

    ticket = models.ForeignKey(
        MaintenanceTicket, on_delete=models.CASCADE, related_name='updates'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(
        help_text="The content of the update (Markdown supported)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Update by {self.author.username} on #{self.ticket.id}"

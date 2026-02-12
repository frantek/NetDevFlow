from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.contrib import messages
from .models import Profile, Device, IPAddress, MaintenanceTicket

# --- Inlines for a better UX (LO1.1 Principles) ---

class IPAddressInline(admin.TabularInline):
    """
    Provides a streamlined interface for managing IP allocations directly 
    on the Device detail page. This reduces navigation overhead for engineers.
    """
    model = IPAddress
    extra = 1  # Provides one empty slot for quick adding to encourage proper documentation
    fields = ('address', 'subnet_mask', 'is_primary')


class MaintenanceTicketInline(admin.TabularInline):
    """
    Integrates the repair history into the Device view. This ensures technicians 
    see the operational context and recent faults before modifying hardware.
    """
    model = MaintenanceTicket
    extra = 0
    fields = ('title', 'severity', 'status', 'assigned_to')
    readonly_fields = ('created_at',)
    can_delete = False  # Preservation of audit trail as per project requirements


# --- Model Admin Registrations ---

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    The primary control center for the NetDevFlow inventory.
    Features custom actions for bulk status updates and a deep-dive 
    interface for hardware auditing.
    """
    list_display = ('hostname', 'get_primary_ip', 'device_type', 'status', 'location', 'updated_at')
    list_filter = ('device_type', 'status', 'location')
    search_fields = ('hostname', 'model_name', 'location', 'ip_addresses__address')
    list_editable = ('status',)  # Allows rapid inventory updates directly from the list view
    inlines = [IPAddressInline, MaintenanceTicketInline]
    
    # Organize fields into logical sections to improve form clarity
    fieldsets = (
        ('Hardware Identity', {
            'fields': ('hostname', 'model_name', 'device_type'),
            'description': 'Core identifiers used to track this asset across the network.'
        }),
        ('Deployment Info', {
            'fields': ('status', 'location'),
            'classes': ('collapse',),  # Collapsible section for a cleaner UI
        }),
    )

    # Custom Action (LO1.4 Logic Integration)
    actions = ['mark_as_maintenance', 'mark_as_online']

    @admin.action(description="Set selected devices to Maintenance status")
    def mark_as_maintenance(self, request, queryset):
        """Bulk update logic to shift hardware into maintenance mode."""
        updated = queryset.update(status='MAINTENANCE')
        self.message_user(request, f"{updated} devices successfully moved to maintenance.", messages.SUCCESS)

    @admin.action(description="Set selected devices to Online status")
    def mark_as_online(self, request, queryset):
        """Bulk update logic to return hardware to production."""
        updated = queryset.update(status='ONLINE')
        self.message_user(request, f"{updated} devices are now online.", messages.SUCCESS)

    def get_primary_ip(self, obj):
        """
        Custom method to display the primary IP address in the device list.
        Demonstrates data aggregation for better UX (LO1.1).
        """
        primary = obj.ip_addresses.filter(is_primary=True).first()
        if primary:
            return primary.address
        return format_html('<span style="color: red;">No Primary IP</span>')
    get_primary_ip.short_description = 'Management IP'


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    """
    Specialized view for the IPAM (IP Address Management) layer.
    Focuses on address space integrity and allocation tracking.
    """
    list_display = ('address', 'device', 'subnet_mask', 'is_primary')
    list_filter = ('is_primary', 'subnet_mask')
    search_fields = ('address', 'device__hostname')
    list_select_related = ('device',)  # Optimization for list loading (LO8.3)


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    """
    The auditing interface for maintenance logs. 
    Prioritizes visibility of critical faults and staff accountability.
    """
    list_display = ('id', 'colored_severity', 'title', 'device', 'status', 'assigned_to', 'created_at')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('title', 'description', 'device__hostname')
    raw_id_fields = ('device',)  # Essential for performance when managing thousands of assets
    date_hierarchy = 'created_at'  # Breadcrumb navigation for time-based logs

    def colored_severity(self, obj):
        """Visual cue to highlight high-priority issues directly in the admin list."""
        colors = {
            'CRITICAL': 'red',
            'WARNING': 'orange',
            'LOW': 'green',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severity, 'black'),
            obj.get_severity_display()
        )
    colored_severity.short_description = 'Priority'


# --- Profile Integration with User Admin (LO3) ---

class ProfileInline(admin.StackedInline):
    """
    Integrates the custom Profile role into the standard User admin page.
    This fulfills the requirement for managed user permissions and access levels.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Role & Permissions'


class UserAdmin(BaseUserAdmin):
    """
    Customized User Admin to prevent IntegrityErrors by only showing 
    the Profile inline on the 'Change' page, not the 'Add' page.
    """
    def get_inlines(self, request, obj=None):
        # obj is None when creating a new user (Add page)
        # obj is present when editing an existing user (Change page)
        if obj:
            return [ProfileInline]
        return []

    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('profile__role', 'is_staff', 'is_superuser')

    def get_role(self, obj):
        """Extracts the role from the linked Profile model for the list view."""
        return obj.profile.role
    get_role.short_description = 'Network Access Role'

# Re-register User with the new CustomUserAdmin to centralize administration
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

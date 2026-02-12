from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Device, IPAddress, MaintenanceTicket

# --- Inlines for a better UX (LO1.1 Principles) ---

class IPAddressInline(admin.TabularInline):
    """Allows managing IP addresses directly on the Device admin page."""
    model = IPAddress
    extra = 1  # Provides one empty slot for quick adding


class MaintenanceTicketInline(admin.TabularInline):
    """Allows viewing/adding tickets directly on the Device admin page."""
    model = MaintenanceTicket
    extra = 0
    fields = ['title', 'severity', 'status', 'assigned_to']
    readonly_fields = ['created_at']


# --- Model Admin Registrations ---

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Advanced configuration for Device management.
    Includes filtering, searching, and inlines for IPs and Tickets.
    """
    list_display = ('hostname', 'device_type', 'status', 'location', 'updated_at')
    list_filter = ('device_type', 'status', 'location')
    search_fields = ('hostname', 'model_name', 'location')
    inlines = [IPAddressInline, MaintenanceTicketInline]
    
    # Organize fields into logical sections
    fieldsets = (
        ('Hardware Identity', {
            'fields': ('hostname', 'model_name', 'device_type')
        }),
        ('Deployment Info', {
            'fields': ('status', 'location')
        }),
    )


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'device', 'subnet_mask', 'is_primary')
    list_filter = ('is_primary', 'subnet_mask')
    search_fields = ('address', 'device__hostname')


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'device', 'severity', 'status', 'assigned_to', 'created_at')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('title', 'description', 'device__hostname')
    raw_id_fields = ('device',)  # Better for performance if inventory grows large


# --- Profile Integration with User Admin (LO3) ---

class ProfileInline(admin.StackedInline):
    """Integrates the custom Profile role into the standard User admin page."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Role Profile'


class UserAdmin(BaseUserAdmin):
    """Custom User Admin to show the Profile role inline."""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')

    def get_role(self, obj):
        return obj.profile.role
    get_role.short_description = 'Access Role'

# Re-register User with the new CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

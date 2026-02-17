from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import (
    DataCenter,
    Device,
    IPAddress,
    MaintenanceTicket,
    Profile,
    Rack,
    Row,
)

# --- Inlines for DCIM UX (LO1.1 Principles) ---


class IPAddressInline(admin.TabularInline):
    """Manage IP allocations directly on the Device detail page."""

    model = IPAddress
    extra = 1
    fields = ('address', 'subnet_mask', 'is_primary')


class MaintenanceTicketInline(admin.TabularInline):
    """Repair history integrated into the Device view.

    Provides operational context for technicians.
    """

    model = MaintenanceTicket
    extra = 0
    fields = ('title', 'severity', 'status', 'assigned_to')
    readonly_fields = ('created_at',)
    can_delete = False


class DeviceInline(admin.TabularInline):
    """Allows technicians to see/edit hardware in a specific rack."""

    model = Device
    extra = 0
    fields = ('hostname', 'position', 'size', 'status')
    ordering = ('-position',)


class RackInline(admin.TabularInline):
    """Shows all racks within a specific row."""

    model = Rack
    extra = 1


# --- DCIM Hierarchy Registrations ---


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info', 'rack_count')
    search_fields = ('name',)

    def rack_count(self, obj):
        return Rack.objects.filter(row__data_center=obj).count()

    rack_count.short_description = 'Total Racks'


@admin.register(Row)
class RowAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_center', 'rack_count')
    list_filter = ('data_center',)
    inlines = [RackInline]

    def rack_count(self, obj):
        return obj.racks.count()


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_location',
        'ru_capacity',
        'occupied_units',
        'utilization_bar',
    )
    list_filter = ('row__data_center', 'row')
    inlines = [DeviceInline]

    def get_location(self, obj):
        return f"{obj.row.data_center.name} / {obj.row.name}"

    get_location.short_description = 'Location'

    def occupied_units(self, obj):
        return sum(d.size for d in obj.devices.all())

    def utilization_bar(self, obj):
        occupied = self.occupied_units(obj)
        percent = (
            (occupied / obj.ru_capacity) * 100 if obj.ru_capacity > 0 else 0
        )
        color = 'green' if percent < 70 else 'orange' if percent < 90 else 'red'  # noqa: E501
        # noqa: E501
        html_start = (
            '<div style="width:100px; background:#eee; border-radius:3px;">'
        )
        return format_html(
            html_start +
            '<div style="width:{}px; background:{}; height:10px; '
            'border-radius:3px;"></div></div>',
            percent,
            color,
        )

    utilization_bar.short_description = 'U-Space Util'


# --- Enhanced Asset Management ---


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    The Big Boss HQ for hardware assets. Now includes DCIM physical tracking.
    """

    list_display = (
        'hostname',
        'image_tag',
        'device_type',
        'status',
        'get_rack_pos',
        'size',
        'updated_at',
    )
    list_filter = ('device_type', 'status', 'rack__row__data_center', 'rack')
    search_fields = (
        'hostname',
        'model_name',
        'rack__name',
        'ip_addresses__address',
    )
    list_editable = ('status',)
    inlines = [IPAddressInline, MaintenanceTicketInline]

    fieldsets = (
        (
            'Hardware Identity',
            {
                'fields': (
                    'hostname',
                    'model_name',
                    'device_type',
                    'device_image',
                )
            },
        ),
        (
            'Physical Placement (DCIM)',
            {
                'fields': ('rack', 'position', 'size'),
                'description': 'Specify where this unit sits in the physical rack.',  # noqa: E501
            },
        ),
        (
            'Deployment Status',
            {
                'fields': ('status',),
            },
        ),
    )

    def image_tag(self, obj):
        if obj.device_image:
            img_html = (
                '<img src="{}" style="width: 45px; height:auto; '
                'border-radius:4px;" />'
            )
            return format_html(
                img_html,
                obj.device_image.url,
            )
        return "-"

    image_tag.short_description = 'Preview'

    def get_rack_pos(self, obj):
        if obj.rack:
            return f"{obj.rack.name} [RU {obj.position}]"
        return format_html('<span style="color: #999;">Unracked</span>')

    get_rack_pos.short_description = 'Rack Position'


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'device', 'subnet_mask', 'is_primary')
    list_select_related = ('device',)


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'colored_severity',
        'title',
        'device',
        'status',
        'assigned_to',
        'created_at',
    )
    list_filter = ('severity', 'status', 'created_at')
    raw_id_fields = ('device',)

    def colored_severity(self, obj):
        colors = {'CRITICAL': 'red', 'WARNING': 'orange', 'LOW': 'green'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severity, 'black'),
            obj.get_severity_display(),
        )


# --- Profile & User Auth ---


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0  # Don't show extra blank Profile forms


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_role', 'is_staff')

    def get_role(self, obj):
        return obj.profile.role

    get_role.short_description = 'Network Access Role'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

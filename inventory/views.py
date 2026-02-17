import ipaddress
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import DeviceForm, IPAddressForm, PrefixForm, TicketForm, VLANForm, VRFForm
from .models import (
    VLAN,
    VRF,
    DataCenter,
    Device,
    IPAddress,
    MaintenanceTicket,
    Prefix,
    Profile,
    Rack,
    Row,
    TicketUpdate,
)

# --- Role-Based Access Mixins ---


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role == 'MANAGER'


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role in ['TECHNICIAN', 'MANAGER']


class TechRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profile.role in ['TECHNICIAN', 'MANAGER']


# --- Dashboard View ---


def dashboard(request):
    """
    Main HQ Dashboard providing a high-level overview of infrastructure health and network segments.
    """
    context = {
        'total_devices': Device.objects.count(),
        'online_count': Device.objects.filter(status='ONLINE').count(),
        'critical_tickets': MaintenanceTicket.objects.filter(severity='CRITICAL', status='OPEN').count(),
        'recent_tickets': MaintenanceTicket.objects.select_related('device').all()[:5],
        'dc_stats': DataCenter.objects.annotate(rack_count=Count('rows__racks')),
        # New IPAM metrics for the Big Boss
        'vrf_count': VRF.objects.count(),
        'vlan_count': VLAN.objects.count(),
        'prefix_count': Prefix.objects.count(),
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def rack_view(request, rack_id):
    """
    Renders a visual representation of a Rack and its RU slots.
    """
    rack = get_object_or_404(Rack, pk=rack_id)
    devices = rack.devices.all().order_by('-position')

    # Build a list representing each slot (Top to Bottom)
    rack_slots = []
    occupied_positions = {}
    for device in devices:
        for ru in range(device.position, device.position + device.size):
            occupied_positions[ru] = device

    for ru in range(rack.ru_capacity, 0, -1):
        device = occupied_positions.get(ru)
        # Handle multi-U units to avoid duplicate visual rows
        if device and ru == (device.position + device.size - 1):
            rack_slots.append({'ru': ru, 'device': device, 'is_start': True})
        elif device:
            rack_slots.append({'ru': ru, 'device': device, 'is_start': False})
        else:
            rack_slots.append({'ru': ru, 'device': None, 'is_start': True})

    return render(request, 'inventory/rack_view.html', {'rack': rack, 'slots': rack_slots})


# --- Kanban Board Views (LO2.2 & Trello-style logic) ---


@login_required
def kanban_board(request):
    """
    Renders the Kanban board with tickets sorted by status columns.
    """
    tickets = MaintenanceTicket.objects.select_related('device', 'assigned_to').all()
    context = {
        'tickets_open': tickets.filter(status='OPEN'),
        'tickets_progress': tickets.filter(status='IN_PROGRESS'),
        'tickets_resolved': tickets.filter(status='RESOLVED'),
        'tickets_closed': tickets.filter(status='CLOSED'),
    }
    return render(request, 'inventory/kanban.html', context)


@login_required
def update_ticket_status(request, pk):
    """
    Handles AJAX POST requests to update ticket status via drag-and-drop.
    """
    if request.method == 'POST':
        # Defensive Check: Ensure profile exists before checking role
        try:
            if request.user.profile.role == 'READONLY':
                return JsonResponse({'status': 'error', 'message': 'Permission denied: Read-only access'}, status=403)
        except (ObjectDoesNotExist, AttributeError):
            return JsonResponse({'status': 'error', 'message': 'User profile misconfigured'}, status=403)

        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            ticket = get_object_or_404(MaintenanceTicket, pk=pk)

            # Basic validation of incoming status
            valid_statuses = [choice[0] for choice in MaintenanceTicket.STATUS_CHOICES]
            if new_status in valid_statuses:
                ticket.status = new_status
                ticket.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


# --- Role-Based Access Mixins (LO3) ---


class ManagerRequiredMixin(UserPassesTestMixin):
    """Restricts access to users with the 'MANAGER' role. Defensive against missing profiles."""

    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.profile.role == 'MANAGER'
        except (ObjectDoesNotExist, AttributeError):
            return False


class TechOrManagerRequiredMixin(UserPassesTestMixin):
    """Restricts access to Technicians or Managers. Defensive against missing profiles."""

    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.profile.role in ['TECHNICIAN', 'MANAGER']
        except (ObjectDoesNotExist, AttributeError):
            return False


# --- Device CRUD (LO2) ---


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'inventory/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return Device.objects.prefetch_related('ip_addresses').all()


class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    template_name = 'inventory/device_detail.html'


class DeviceCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = Device
    template_name = 'inventory/device_form.html'
    fields = ['hostname', 'model_name', 'device_type', 'status', 'rack', 'position', 'size', 'device_image']
    success_url = reverse_lazy('device_list')

    def form_valid(self, form):
        messages.success(self.request, f"Asset {form.instance.hostname} integrated into DCIM.")
        return super().form_valid(form)


class DeviceUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    """Allows updating physical placement or hardware specs (LO2)."""

    model = Device
    template_name = 'inventory/device_form.html'
    fields = ['hostname', 'model_name', 'device_type', 'status', 'rack', 'position', 'size', 'device_image']

    def get_success_url(self):
        return reverse_lazy('device_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.info(self.request, f"Configuration for {form.instance.hostname} updated.")
        return super().form_valid(form)


class DeviceDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    """Restricted to Managers to prevent accidental data loss (LO3)."""

    model = Device
    template_name = 'inventory/device_confirm_delete.html'
    success_url = reverse_lazy('device_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Hardware asset decommissioned and removed from inventory.")
        return super().delete(request, *args, **kwargs)


# --- Data Center CRUD ---


class DataCenterListView(LoginRequiredMixin, ListView):
    model = DataCenter
    template_name = 'inventory/datacenter_list.html'
    context_object_name = 'datacenters'

    def get_queryset(self):
        return DataCenter.objects.annotate(
            row_count=Count('rows', distinct=True), rack_count=Count('rows__racks', distinct=True)
        )


class DataCenterCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = DataCenter
    template_name = 'inventory/datacenter_form.html'
    fields = ['name', 'physical_address', 'contact_info']
    success_url = reverse_lazy('datacenter_list')

    def form_valid(self, form):
        messages.success(self.request, f"Data Center '{form.instance.name}' commissioned.")
        return super().form_valid(form)


class DataCenterUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = DataCenter
    template_name = 'inventory/datacenter_form.html'
    fields = ['name', 'physical_address', 'contact_info']
    success_url = reverse_lazy('datacenter_list')


class DataCenterDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = DataCenter
    template_name = 'inventory/datacenter_confirm_delete.html'
    success_url = reverse_lazy('datacenter_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Data Center decommissioned and removed from hierarchy.")
        return super().delete(request, *args, **kwargs)


# --- CRUD Views: Racks (DCIM Lifecycle) ---


class RackListView(LoginRequiredMixin, ListView):
    """Overview of all physical racks in the infrastructure."""

    model = Rack
    template_name = 'inventory/rack_list.html'
    context_object_name = 'racks'
    queryset = Rack.objects.select_related('row__data_center').annotate(device_count=Count('devices'))


class RackCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    """Provision a new rack within a Data Center Row."""

    model = Rack
    template_name = 'inventory/rack_form.html'
    fields = ['name', 'row', 'ru_capacity']
    success_url = reverse_lazy('rack_list')

    def form_valid(self, form):
        messages.success(self.request, f"Rack {form.instance.name} provisioned successfully.")
        return super().form_valid(form)


class RackUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    """Update rack specifications or physical row assignment."""

    model = Rack
    template_name = 'inventory/rack_form.html'
    fields = ['name', 'row', 'ru_capacity']
    success_url = reverse_lazy('rack_list')

    def form_valid(self, form):
        messages.info(self.request, f"Rack {form.instance.name} configuration updated.")
        return super().form_valid(form)


class RackDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    """Decommission a rack. Restricted to Managers."""

    model = Rack
    template_name = 'inventory/rack_confirm_delete.html'
    success_url = reverse_lazy('rack_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Rack decommissioned. All unlinked devices are now unassigned.")
        return super().delete(request, *args, **kwargs)


# --- CRUD Views: Racks ---


class RackListView(LoginRequiredMixin, ListView):
    model = Rack
    template_name = 'inventory/rack_list.html'
    context_object_name = 'racks'
    queryset = Rack.objects.select_related('row__data_center').annotate(device_count=Count('devices'))


class RackCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = Rack
    template_name = 'inventory/rack_form.html'
    fields = ['name', 'row', 'ru_capacity']
    success_url = reverse_lazy('rack_list')


class RackUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    model = Rack
    template_name = 'inventory/rack_form.html'
    fields = ['name', 'row', 'ru_capacity']
    success_url = reverse_lazy('rack_list')


class RackDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Rack
    template_name = 'inventory/rack_confirm_delete.html'
    success_url = reverse_lazy('rack_list')


# --- CRUD Views: Rows (NEW - Hierarchy Management) ---


class RowListView(LoginRequiredMixin, ListView):
    """Overview of Data Center Rows."""

    model = Row
    template_name = 'inventory/row_list.html'
    context_object_name = 'rows'
    queryset = Row.objects.select_related('data_center').annotate(rack_count=Count('racks'))


class RowCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = Row
    template_name = 'inventory/row_form.html'
    fields = ['name', 'data_center']
    success_url = reverse_lazy('row_list')

    def form_valid(self, form):
        messages.success(self.request, f"Row {form.instance.name} added to the data center.")
        return super().form_valid(form)


class RowUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    model = Row
    template_name = 'inventory/row_form.html'
    fields = ['name', 'data_center']
    success_url = reverse_lazy('row_list')


class RowDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Row
    template_name = 'inventory/row_confirm_delete.html'
    success_url = reverse_lazy('row_list')


# --- Ticket CRUD (LO2) ---


class TicketCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = MaintenanceTicket
    fields = ['title', 'description', 'severity', 'device', 'assigned_to']
    success_url = reverse_lazy('kanban_board')
    template_name = 'inventory/ticket_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if form.instance.severity == 'CRITICAL':
            device = form.instance.device
            device.status = 'MAINTENANCE'
            device.save()
            messages.error(self.request, f"ALERT: {device.hostname} moved to MAINTENANCE status.")

        messages.info(self.request, "Ticket created successfully.")
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    """
    Enhanced View to handle GitHub-style threading.
    Updates the Ticket metadata and creates a new TicketUpdate sub-post.
    """

    model = MaintenanceTicket
    template_name = 'inventory/ticket_form.html'
    # We exclude 'description' here because we don't want to edit the root post
    fields = ['status', 'severity', 'assigned_to', 'device']
    success_url = reverse_lazy('kanban_board')

    def form_valid(self, form):
        # 1. Save the metadata changes (Status, Severity, etc.)
        response = super().form_valid(form)

        # 2. Extract the 'comment' from the POST data
        comment_text = self.request.POST.get('comment')

        if comment_text and comment_text.strip():
            # 3. Create the new sub-post (TicketUpdate)
            TicketUpdate.objects.create(ticket=self.object, author=self.request.user, comment=comment_text)
            messages.success(self.request, "Progress update posted to the thread.")
        else:
            messages.info(self.request, "Ticket metadata updated.")

        return response


# --- IPAM Logic (NEW: LO2 & LO7) ---
# --- IP Address Management (IPAM) ---


class IPAddressListView(LoginRequiredMixin, ListView):
    model = IPAddress
    template_name = 'inventory/ip_list.html'
    context_object_name = 'ips'
    queryset = IPAddress.objects.select_related('vrf', 'device').all()


class IPAddressCreateView(LoginRequiredMixin, TechRequiredMixin, CreateView):
    model = IPAddress
    form_class = IPAddressForm
    template_name = 'inventory/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def get_context_data(self, **kwargs):
        """Inject prefixes enriched with VRF and VLAN data for better selection context."""
        context = super().get_context_data(**kwargs)
        # Optimized lookup including VLAN and VRF for the select form
        context['prefixes'] = Prefix.objects.select_related('vrf', 'vlan', 'site').all()
        return context

    def get_initial(self):
        initial = super().get_initial()
        prefix_id = self.request.GET.get('prefix')
        if prefix_id:
            prefix = get_object_or_404(Prefix, pk=prefix_id)
            initial['vrf'] = prefix.vrf
        return initial

    def form_valid(self, form):
        messages.success(self.request, f"IP {form.instance.address} successfully assigned.")
        return super().form_valid(form)


class IPAddressUpdateView(LoginRequiredMixin, TechRequiredMixin, UpdateView):
    model = IPAddress
    form_class = IPAddressForm
    template_name = 'inventory/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def get_context_data(self, **kwargs):
        """Ensure prefixes are available when editing an existing allocation."""
        context = super().get_context_data(**kwargs)
        # Including VLAN and VRF context for technicians
        context['prefixes'] = Prefix.objects.select_related('vrf', 'vlan', 'site').all()
        return context

    def form_valid(self, form):
        messages.info(self.request, f"Allocation for {form.instance.address} updated.")
        return super().form_valid(form)


class IPAddressDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = IPAddress
    template_name = 'inventory/ip_confirm_delete.html'
    success_url = reverse_lazy('ip_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "IP Address decommissioned and released to the pool.")
        return super().delete(request, *args, **kwargs)


class GetAvailableIPsView(LoginRequiredMixin, View):
    """
    API view to return available IPs within a prefix.
    Used by the front-end to populate selection forms.
    """

    def get(self, request, prefix_id):
        prefix_obj = get_object_or_404(Prefix, pk=prefix_id)
        try:
            network = ipaddress.ip_network(prefix_obj.prefix)
            # Fetch all currently assigned IPs in the system
            used_ips = set(IPAddress.objects.values_list('address', flat=True))

            # Logic: If we are updating an existing IP, we must allow the current IP
            # to be visible in the 'available' list.
            exclude_ip = request.GET.get('exclude')
            if exclude_ip and exclude_ip in used_ips:
                used_ips.remove(exclude_ip)

            available_ips = []
            # Only return the first 100 available to prevent browser hang on large subnets
            for ip in network.hosts():
                ip_str = str(ip)
                if ip_str not in used_ips:
                    available_ips.append(ip_str)
                    if len(available_ips) >= 100:
                        break

            return JsonResponse(
                {
                    'status': 'success',
                    'available_ips': available_ips,
                    'network': str(network.network_address),
                    'mask': str(network.netmask),
                }
            )
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid Prefix format'}, status=400)


# --- VLAN Management ---


class VLANListView(LoginRequiredMixin, ListView):
    model = VLAN
    template_name = 'inventory/vlan_list.html'
    context_object_name = 'vlans'
    queryset = VLAN.objects.select_related('data_center').all()


class VLANCreateView(LoginRequiredMixin, TechRequiredMixin, CreateView):
    model = VLAN
    form_class = VLANForm
    template_name = 'inventory/vlan_form.html'
    success_url = reverse_lazy('vlan_list')


class VLANUpdateView(LoginRequiredMixin, TechRequiredMixin, UpdateView):
    model = VLAN
    form_class = VLANForm
    template_name = 'inventory/vlan_form.html'
    success_url = reverse_lazy('vlan_list')


class VLANDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = VLAN
    template_name = 'inventory/vlan_confirm_delete.html'
    success_url = reverse_lazy('vlan_list')


# --- VRF Management ---


class VRFListView(LoginRequiredMixin, ListView):
    model = VRF
    template_name = 'inventory/vrf_list.html'
    context_object_name = 'vrfs'


class VRFCreateView(LoginRequiredMixin, TechRequiredMixin, CreateView):
    model = VRF
    form_class = VRFForm
    template_name = 'inventory/vrf_form.html'
    success_url = reverse_lazy('vrf_list')


class VRFUpdateView(LoginRequiredMixin, TechRequiredMixin, UpdateView):
    model = VRF
    form_class = VRFForm
    template_name = 'inventory/vrf_form.html'
    success_url = reverse_lazy('vrf_list')


class VRFDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = VRF
    template_name = 'inventory/vrf_confirm_delete.html'
    success_url = reverse_lazy('vrf_list')


# --- Prefix Management ---


class PrefixListView(LoginRequiredMixin, ListView):
    model = Prefix
    template_name = 'inventory/prefix_list.html'
    context_object_name = 'prefixes'
    queryset = Prefix.objects.select_related('vrf', 'vlan', 'site').all()


class PrefixCreateView(LoginRequiredMixin, TechRequiredMixin, CreateView):
    model = Prefix
    form_class = PrefixForm
    template_name = 'inventory/prefix_form.html'
    success_url = reverse_lazy('prefix_list')

    def form_valid(self, form):
        messages.success(self.request, f"Prefix {form.instance.prefix} successfully created.")
        return super().form_valid(form)


class PrefixUpdateView(LoginRequiredMixin, TechRequiredMixin, UpdateView):
    """View used by the 'prefix_update' URL pattern."""

    model = Prefix
    form_class = PrefixForm
    template_name = 'inventory/prefix_form.html'
    success_url = reverse_lazy('prefix_list')

    def form_valid(self, form):
        messages.info(self.request, f"Prefix {form.instance.prefix} has been updated.")
        return super().form_valid(form)


class PrefixDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Prefix
    template_name = 'inventory/prefix_confirm_delete.html'
    success_url = reverse_lazy('prefix_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Prefix has been decommissioned.")
        return super().delete(request, *args, **kwargs)


# --- Custom Error Handlers (LO1.1 & UX Enhancement) ---


def error_403(request, exception=None):
    """Custom 403 Forbidden error page."""
    return render(request, '403.html', status=403)


def error_500(request):
    """Custom 500 Internal Server Error page."""
    return render(request, '500.html', status=500)

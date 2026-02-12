from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from .models import Device, IPAddress, MaintenanceTicket, Profile

# --- Dashboard View (Read Operation) ---

def dashboard(request):
    """
    Aggregates stats for the main overview (LO1.4 Custom Logic).
    """
    context = {
        'total_devices': Device.objects.count(),
        'online_count': Device.objects.filter(status='ONLINE').count(),
        'critical_tickets': MaintenanceTicket.objects.filter(severity='CRITICAL', status='OPEN').count(),
        'recent_tickets': MaintenanceTicket.objects.all()[:5],
        'device_types': Device.objects.values('device_type').annotate(count=Count('device_type')),
    }
    return render(request, 'inventory/dashboard.html', context)

# --- Role-Based Access Mixins (LO3) ---

class ManagerRequiredMixin(UserPassesTestMixin):
    """Restricts access to users with the 'MANAGER' role."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role == 'MANAGER'

class TechOrManagerRequiredMixin(UserPassesTestMixin):
    """Restricts access to Technicians or Managers (Not Read-Only)."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role in ['TECHNICIAN', 'MANAGER']

# --- Device CRUD (LO2) ---

class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'inventory/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        # AI Suggestion (LO8.3): prefetch_related to optimize N+1 query performance
        return Device.objects.prefetch_related('ip_addresses').all()

class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    template_name = 'inventory/device_detail.html'

class DeviceCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = Device
    fields = ['hostname', 'model_name', 'device_type', 'status', 'location']
    success_url = reverse_lazy('device_list')

    def form_valid(self, form):
        messages.success(self.request, f"Device {form.instance.hostname} successfully added to inventory.")
        return super().form_valid(form)

class DeviceDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Device
    success_url = reverse_lazy('device_list')

    def delete(self, request, *args, **kwargs):
        device = self.get_object()
        messages.warning(request, f"Device {device.hostname} has been removed from inventory.")
        return super().delete(request, *args, **kwargs)

# --- Ticket CRUD (LO2) ---

class TicketCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = MaintenanceTicket
    fields = ['title', 'description', 'severity', 'device', 'assigned_to']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Custom Logic (LO1.4): If ticket is critical, automatically update device status
        if form.instance.severity == 'CRITICAL':
            device = form.instance.device
            device.status = 'MAINTENANCE'
            device.save()
            messages.error(self.request, f"ALERT: Device {device.hostname} moved to MAINTENANCE due to critical ticket.")
        
        messages.info(self.request, "Maintenance ticket created successfully.")
        return super().form_valid(form)

class TicketUpdateView(LoginRequiredMixin, TechOrManagerRequiredMixin, UpdateView):
    model = MaintenanceTicket
    fields = ['status', 'description', 'assigned_to']
    template_name = 'inventory/ticket_form.html'
    
    def get_success_url(self):
        return reverse_lazy('device_detail', kwargs={'pk': self.object.device.id})

    def form_valid(self, form):
        messages.success(self.request, f"Ticket #{self.object.id} has been updated.")
        return super().form_valid(form)

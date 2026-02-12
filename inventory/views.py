import json
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Device, IPAddress, MaintenanceTicket, Profile

# --- Dashboard View ---

def dashboard(request):
    """
    Aggregates stats for the main overview.
    """
    context = {
        'total_devices': Device.objects.count(),
        'online_count': Device.objects.filter(status='ONLINE').count(),
        'critical_tickets': MaintenanceTicket.objects.filter(severity='CRITICAL', status='OPEN').count(),
        'recent_tickets': MaintenanceTicket.objects.all()[:5],
        'device_types': Device.objects.values('device_type').annotate(count=Count('device_type')),
    }
    return render(request, 'inventory/dashboard.html', context)

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
    fields = ['hostname', 'model_name', 'device_type', 'status', 'location']
    success_url = reverse_lazy('device_list')

    def form_valid(self, form):
        messages.success(self.request, f"Device {form.instance.hostname} successfully added.")
        return super().form_valid(form)

class DeviceDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Device
    success_url = reverse_lazy('device_list')

    def delete(self, request, *args, **kwargs):
        device = self.get_object()
        messages.warning(request, f"Device {device.hostname} decommissioned.")
        return super().delete(request, *args, **kwargs)

# --- Ticket CRUD (LO2) ---

class TicketCreateView(LoginRequiredMixin, TechOrManagerRequiredMixin, CreateView):
    model = MaintenanceTicket
    fields = ['title', 'description', 'severity', 'device', 'assigned_to']
    success_url = reverse_lazy('kanban_board')

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
    model = MaintenanceTicket
    fields = ['status', 'description', 'assigned_to']
    template_name = 'inventory/ticket_form.html'
    
    def get_success_url(self):
        return reverse_lazy('kanban_board')

    def form_valid(self, form):
        messages.success(self.request, f"Ticket #{self.object.id} updated.")
        return super().form_valid(form)

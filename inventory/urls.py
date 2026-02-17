from django.urls import path
from . import views

urlpatterns = [
    # Main Views
    path('', views.dashboard, name='dashboard'),
    path('kanban/', views.kanban_board, name='kanban_board'),

    # Device Routes
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/<int:pk>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('devices/add/', views.DeviceCreateView.as_view(), name='device_create'),
    path('devices/<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_confirm_delete'),
    path('devices/<int:pk>/edit/', views.DeviceUpdateView.as_view(), name='device_update'),

    # IPAM (IP Address Management)
    path('ips/', views.IPAddressListView.as_view(), name='ip_list'),
    path('ips/add/', views.IPAddressCreateView.as_view(), name='ip_create'),
    path('ips/<int:pk>/edit/', views.IPAddressUpdateView.as_view(), name='ip_update'),
    path('ips/<int:pk>/delete/', views.IPAddressDeleteView.as_view(), name='ip_delete'),

    # IPAM API: Dynamic available IP lookup for the allocation form
    path('ips/available/<int:prefix_id>/', views.GetAvailableIPsView.as_view(), name='get_available_ips'),

    path('vlans/', views.VLANListView.as_view(), name='vlan_list'),
    path('vlans/add/', views.VLANCreateView.as_view(), name='vlan_create'),
    path('vlans/<int:pk>/edit/', views.VLANUpdateView.as_view(), name='vlan_update'),
    path('vlans/<int:pk>/delete/', views.VLANDeleteView.as_view(), name='vlan_delete'),
    
    path('vrfs/', views.VRFListView.as_view(), name='vrf_list'),
    path('vrfs/add/', views.VRFCreateView.as_view(), name='vrf_create'),
    path('vrfs/<int:pk>/edit/', views.VRFUpdateView.as_view(), name='vrf_update'),
    path('vrfs/<int:pk>/delete/', views.VRFDeleteView.as_view(), name='vrf_delete'),
    
    path('prefixes/', views.PrefixListView.as_view(), name='prefix_list'),
    path('prefixes/add/', views.PrefixCreateView.as_view(), name='prefix_create'),
    path('prefixes/<int:pk>/edit/', views.PrefixUpdateView.as_view(), name='prefix_update'),
    path('prefixes/<int:pk>/delete/', views.PrefixDeleteView.as_view(), name='prefix_delete'),

    # --- Rack Management (DCIM Hierarchy) ---
     # Data Center (DCIM Root)
    path('datacenters/', views.DataCenterListView.as_view(), name='datacenter_list'),
    path('datacenters/add/', views.DataCenterCreateView.as_view(), name='datacenter_create'),
    path('datacenters/<int:pk>/edit/', views.DataCenterUpdateView.as_view(), name='datacenter_update'),
    path('datacenters/<int:pk>/delete/', views.DataCenterDeleteView.as_view(), name='datacenter_delete'),

    path('racks/', views.RackListView.as_view(), name='rack_list'),
    path('racks/<int:rack_id>/view/', views.rack_view, name='rack_view'),
    path('racks/add/', views.RackCreateView.as_view(), name='rack_create'),
    path('racks/<int:pk>/edit/', views.RackUpdateView.as_view(), name='rack_update'),
    path('racks/<int:pk>/delete/', views.RackDeleteView.as_view(), name='rack_confirm_delete'),

    # Row Management
    path('rows/', views.RowListView.as_view(), name='row_list'),
    path('rows/add/', views.RowCreateView.as_view(), name='row_create'),
    path('rows/<int:pk>/edit/', views.RowUpdateView.as_view(), name='row_update'),
    path('rows/<int:pk>/delete/', views.RowDeleteView.as_view(), name='row_confirm_delete'),

    # Ticket Routes
    path('tickets/add/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    
    # AJAX Status Update for Kanban Drag-and-Drop
    path('tickets/<int:pk>/update-status/', views.update_ticket_status, name='update_ticket_status'),
]
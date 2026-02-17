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

    # Ticket Routes
    path('tickets/add/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    
    # AJAX Status Update for Kanban Drag-and-Drop
    path('tickets/<int:pk>/update-status/', views.update_ticket_status, name='update_ticket_status'),
]
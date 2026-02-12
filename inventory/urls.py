from django.urls import path
from . import views

urlpatterns = [
    # Dashboard (Functional View with Custom Stats Logic)
    path('', views.dashboard, name='dashboard'),

    # Device Inventory Management (CBVs)
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/<int:pk>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('devices/add/', views.DeviceCreateView.as_view(), name='device_create'),
    path('devices/<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_delete'),

    # Maintenance Ticket Management (CRUD)
    path('tickets/add/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
]

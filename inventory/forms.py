from django import forms
from .models import Device, IPAddress, MaintenanceTicket

class DeviceForm(forms.ModelForm):
    """
    Form for creating and updating network devices.
    Includes Bootstrap styling for all fields.
    """
    class Meta:
        model = Device
        fields = ['hostname', 'model_name', 'device_type', 'status', 'location']
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. core-switch-01'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cisco Nexus 9000'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Center A, Rack 4'}),
        }

class TicketForm(forms.ModelForm):
    """
    Form for logging and updating maintenance incidents.
    Linked to specific devices in the inventory.
    """
    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'severity', 'status', 'device', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the issue'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed technical logs...'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimization: Order device dropdown by hostname
        self.fields['device'].queryset = Device.objects.all().order_by('hostname')

class IPAddressForm(forms.ModelForm):
    """
    Form for assigning IP addresses to devices.
    Uses GenericIPAddressField validation from the model.
    """
    class Meta:
        model = IPAddress
        fields = ['address', 'subnet_mask', 'device', 'is_primary']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 192.168.1.1'}),
            'subnet_mask': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 255.255.255.0'}),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

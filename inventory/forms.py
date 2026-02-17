from django import forms
from .models import Device, IPAddress, MaintenanceTicket, DataCenter, Row, Rack

class DeviceForm(forms.ModelForm):
    """
    Advanced DCIM form featuring physical placement and dimension tracking.
    """
    class Meta:
        model = Device
        fields = ['hostname', 'model_name', 'device_type', 'status', 'rack', 'position', 'size', 'device_image']
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FQDN/Hostname'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cisco C240 M5'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rack': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 42}),
            'device_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order racks by full DC path
        self.fields['rack'].queryset = Rack.objects.select_related('row__data_center').order_by('row__data_center__name', 'row__name', 'name')

class IPAddressForm(forms.ModelForm):
    """
    Dedicated IPAM form for assigning and validating network addresses.
    """
    class Meta:
        model = IPAddress
        fields = ['address', 'subnet_mask', 'device', 'is_primary']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 192.168.1.50'}),
            'subnet_mask': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 255.255.255.0'}),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_address(self):
        address = self.cleaned_data.get('address')
        # Add custom logic here if you want to restrict specific ranges (LO2.4)
        return address

class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        fields = ['name', 'row', 'ru_capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'row': forms.Select(attrs={'class': 'form-select'}),
            'ru_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
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

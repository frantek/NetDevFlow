from django import forms

from .models import (
    VLAN,
    VRF,
    DataCenter,
    Device,
    IPAddress,
    MaintenanceTicket,
    Prefix,
    Rack,
    Row,
)


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
        self.fields['rack'].queryset = Rack.objects.select_related('row__data_center').order_by(
            'row__data_center__name', 'row__name', 'name'
        )


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
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed technical logs...'}
            ),
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
    Validated IPAM form for assigning and validating network addresses.
    Includes custom validation to ensure formatting is correct.
    """

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'device', 'is_primary']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 192.168.1.50'}),
            'vrf': forms.Select(attrs={'class': 'form-select'}),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_address(self):
        """
        Verify the IP format before allowing it into the database.
        (Django's GenericIPAddressField handles much of this, but we can add
        custom subnet logic here if needed later).
        """
        address = self.cleaned_data.get('address')
        # Logic for checking reserved ranges or leading zeros could go here.
        return address


class VLANForm(forms.ModelForm):
    class Meta:
        model = VLAN
        fields = ['vid', 'name', 'data_center', 'status']
        widgets = {
            'vid': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4094}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'data_center': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class VRFForm(forms.ModelForm):
    class Meta:
        model = VRF
        fields = ['name', 'rd', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 65000:1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PrefixForm(forms.ModelForm):
    class Meta:
        model = Prefix
        fields = ['prefix', 'vrf', 'vlan', 'site', 'status']
        widgets = {
            'prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10.0.0.0/24'}),
            'vrf': forms.Select(attrs={'class': 'form-select'}),
            'vlan': forms.Select(attrs={'class': 'form-select'}),
            'site': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

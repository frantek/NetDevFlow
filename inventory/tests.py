import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Device, IPAddress, VLAN, VRF, Prefix, DataCenter, Row, Rack, MaintenanceTicket

class NetDevFlowTestWrapper(TestCase):
    """
    Comprehensive test suite for NetDevFlow.
    Covers LO1.2 (Models), LO2.2 (CRUD), LO3 (Security), LO7 (Relationships), and LO4 (QA).
    """

    def setUp(self):
        # 1. Setup Users with specific roles for LO3 (RBAC) testing
        self.manager = User.objects.create_user(username='manager_boss', password='password123')
        self.manager.profile.role = 'MANAGER'
        self.manager.profile.save()

        self.tech = User.objects.create_user(username='tech_field', password='password123')
        self.tech.profile.role = 'TECHNICIAN'
        self.tech.profile.save()

        self.readonly = User.objects.create_user(username='guest_viewer', password='password123')
        self.readonly.profile.role = 'READONLY'
        self.readonly.profile.save()

        self.pending = User.objects.create_user(username='new_signup', password='password123')
        self.pending.profile.role = 'PENDING'
        self.pending.profile.save()

        # 2. Setup Physical Hierarchy (DCIM - LO7)
        self.dc = DataCenter.objects.create(name="Site-A", physical_address="1 Primary Way")
        self.row = Row.objects.create(name="Row-01", data_center=self.dc)
        self.rack = Rack.objects.create(name="Rack-A1", row=self.row, ru_capacity=42)

        # 3. Setup Logical Hierarchy (IPAM)
        self.vrf = VRF.objects.create(name="Production", rd="65000:1")
        self.vlan = VLAN.objects.create(vid=10, name="Server-Network", data_center=self.dc)
        self.prefix = Prefix.objects.create(prefix="10.0.10.0/24", vrf=self.vrf, vlan=self.vlan, status="ACTIVE")

        # 4. Create a base device for recurring tests
        self.device = Device.objects.create(
            hostname="SRV-PROD-01",
            model_name="PowerEdge R740",
            device_type="SERVER",
            status="ONLINE",
            rack=self.rack,
            position=1,
            size=2
        )

    # --- MODEL & LOGIC TESTS (LO1.2 & LO7) ---

    def test_device_model_logic(self):
        """Verify device creation and string representation."""
        self.assertEqual(self.device.hostname, "SRV-PROD-01")
        # Verifies the implementation including size: "Hostname (SizeU)"
        self.assertEqual(str(self.device), "SRV-PROD-01 (2U)")

    def test_ip_relationship(self):
        """Verify IP addresses link correctly to devices."""
        ip = IPAddress.objects.create(
            address="10.0.10.50",
            subnet_mask="255.255.255.0",
            device=self.device,
            is_primary=True
        )
        self.assertEqual(ip.device.hostname, "SRV-PROD-01")
        self.assertIn(ip, self.device.ip_addresses.all())

    def test_maintenance_ticket_logic(self):
        """Verify tickets link to devices and default to OPEN."""
        ticket = MaintenanceTicket.objects.create(
            title="Fan Failure",
            description="Replace chassis fan",
            device=self.device,
            severity="CRITICAL",
            created_by=self.tech
        )
        self.assertEqual(ticket.device.hostname, "SRV-PROD-01")
        self.assertEqual(ticket.status, "OPEN")

    # --- VIEW & DASHBOARD TESTS (LO2.2) ---

    def test_dashboard_access_levels(self):
        """Verify guest vs authenticated dashboard views."""
        # Guest View
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Internal Access Required")

        # Authenticated View
        self.client.login(username='tech_field', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Command Center")
        self.assertContains(response, "Online Assets")

    # --- EXTENDED CRUD TESTS (LO2.2) ---

    def test_device_crud_lifecycle(self):
        """Tests Create, Read, Update, Delete for Device model."""
        self.client.login(username='tech_field', password='password123')

        # CREATE
        create_url = reverse('device_create')
        data = {
            'hostname': 'SRV-TEST-01',
            'model_name': 'R740',
            'device_type': 'SERVER',
            'status': 'ONLINE',
            'rack': self.rack.id,
            'position': 10,
            'size': 1
        }
        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Device.objects.filter(hostname='SRV-TEST-01').exists())

        # UPDATE
        device = Device.objects.get(hostname='SRV-TEST-01')
        update_url = reverse('device_update', args=[device.id])
        data['status'] = 'MAINTENANCE'
        self.client.post(update_url, data)
        device.refresh_from_db()
        self.assertEqual(device.status, 'MAINTENANCE')

        # DELETE (Manager Required)
        self.client.login(username='manager_boss', password='password123')
        delete_url = reverse('device_confirm_delete', args=[device.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Device.objects.filter(hostname='SRV-TEST-01').exists())

    def test_vlan_lifecycle(self):
        """Tests the full lifecycle of a VLAN."""
        self.client.login(username='tech_field', password='password123')
        
        # Create
        self.client.post(reverse('vlan_create'), {'vid': 20, 'name': 'IoT', 'data_center': self.dc.id, 'status': 'ACTIVE'})
        self.assertTrue(VLAN.objects.filter(vid=20).exists())

        # Update
        vlan = VLAN.objects.get(vid=20)
        self.client.post(reverse('vlan_update', args=[vlan.id]), {'vid': 20, 'name': 'IoT-Secure', 'data_center': self.dc.id, 'status': 'RESERVED'})
        vlan.refresh_from_db()
        self.assertEqual(vlan.name, 'IoT-Secure')

    # --- SECURITY & PERMISSION TESTS (LO3) ---

    def test_unauthorized_deletion(self):
        """Verify that Technicians cannot delete hardware or network objects."""
        self.client.login(username='tech_field', password='password123')
        
        # Attempt to delete the base device
        url = reverse('device_confirm_delete', args=[self.device.id])
        response = self.client.get(url)
        # Should return 403 Forbidden because of the ManagerRequiredMixin
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Device.objects.filter(id=self.device.id).exists())

    def test_readonly_restriction(self):
        """Verify that ReadOnly users cannot create or edit anything."""
        self.client.login(username='guest_viewer', password='password123')
        
        # Attempt to create VLAN
        response = self.client.post(reverse('vlan_create'), {'vid': 99, 'name': 'Unauthorized'})
        self.assertEqual(response.status_code, 403)

    def test_pending_user_block(self):
        """Verify LO3.1: Pending users are restricted to the dashboard."""
        self.client.login(username='new_signup', password='password123')
        
        # Accessing Inventory list
        response = self.client.get(reverse('device_list'))
        # VerificationRequiredMixin renders dashboard.html with "Access Restricted" notice
        self.assertTemplateUsed(response, 'inventory/dashboard.html')
        self.assertContains(response, "Access Restricted")

    # --- SPECIALIZED API & LOGIC TESTS ---

    def test_kanban_status_update_api(self):
        """Verify AJAX endpoint for Kanban updates (LO2.2 Update)."""
        ticket = MaintenanceTicket.objects.create(
            title="Update Status",
            device=self.device,
            created_by=self.tech,
            status="OPEN"
        )
        self.client.login(username='tech_field', password='password123')
        url = reverse('update_ticket_status', args=[ticket.id])
        response = self.client.post(
            url, 
            data=json.dumps({'status': 'IN_PROGRESS'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'IN_PROGRESS')

    def test_dynamic_ip_api(self):
        """Verify IPAM logic for available IP lookups."""
        # Use an IP so it's taken
        IPAddress.objects.create(address="10.0.10.1", device=None, vrf=self.vrf)
        self.client.login(username='tech_field', password='password123')
        
        url = reverse('get_available_ips', args=[self.prefix.id])
        response = self.client.get(url)
        data = response.json()
        
        self.assertEqual(data['status'], 'success')
        # 10.0.10.1 should not be in the available list
        self.assertNotIn("10.0.10.1", data['available_ips'])

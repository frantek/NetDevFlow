# **NetDevFlow: Infrastructure & Incident Management**

NetDevFlow is an AI-augmented infrastructure management tool (DCIM/IPAM) designed specifically for IT operations teams to document complex network assets and track maintenance incidents within a single, unified interface. It bridges the critical gap between hardware inventory and daily task management, ensuring that technical debt and physical maintenance are tracked alongside the assets they affect.

**Live Link:** \[[Your Heroku URL Here](https://netdevflow-35c012406b63.herokuapp.com/)\]

## **1\. Project Purpose**

The primary goal of NetDevFlow is to provide a "single source of truth" for network engineers, systems administrators, and IT managers. In many organizations, infrastructure data is siloed in spreadsheets while maintenance logs are buried in separate ticketing systems. By linking physical devices (Servers, Switches, Routers) directly to maintenance logs through a relational database, the platform ensures that the health status of hardware and the real-time progress of repairs are always visible to the entire team. This transparency reduces mean-time-to-repair (MTTR) and prevents overlapping maintenance efforts.

## **2\. User Stories & Agile Methodology**

Development was managed via an Agile board, utilizing an iterative workflow to ensure core functionality met user needs before adding complexity. This approach allowed for the prioritization of critical CRUD functionality before layering on complex role-based permissions and security constraints.

### **Primary User Stories**

* **As a Technician** I can **add new hardware devices** so that **the team has an accurate, real-time inventory of our network assets across multiple data centers.**  
* **As a Network Engineer** I can **assign an IP address to a specific device** so that **I can track which addresses are currently in use and avoid costly IP conflicts.**  
* **As an Infrastructure Manager** I can **exclusively delete hardware assets** so that **accidental data loss is prevented and the audit trail remains intact.**  
* **As a Technician** I can **update a ticket status from Open to Resolved** so that **the team knows a critical issue is no longer active and resources can be redirected.**

## **3\. Tech Stack**

* **Backend:** Django 5.x and Python 3.12 provide a robust, "batteries-included" framework for managing complex relational data and secure user authentication.  
* **Frontend:** A combination of Semantic HTML5, Custom CSS3 (with Dark Mode sync), and Bootstrap 5 ensures a professional, responsive interface that maintains high accessibility standards (WCAG).  
* **Database:** PostgreSQL is utilized for its reliability and support for complex relationship queries.  
* **Deployment:** Heroku Cloud with WhiteNoise for static asset management.

## **4\. Front-End Design & Wireframes**

The UI follows a "Mobile-First" philosophy, specifically designed for technicians who need to access and update data while standing in a server room or wiring closet using handheld devices.

### **4.1 Dashboard Layout**
```
\+-----------------------------------------------------------------------+  
| \[NetDevFlow Logo\]          Dashboard   Inventory   IPAM   \[User V\]    |  
\+-----------------------------------------------------------------------+  
|                                                                       |  
|  COMMAND CENTER                                      \[+ Device\]       |  
|                                                                       |  
|  STATUS: \[ ONLINE: 42 \] \[ CRITICAL: 05 \] \[ SITES: 03 \]                |  
|                                                                       |  
|  NETWORK SEGMENTS (IPAM)                                              |  
|  \+-------------------+   \+-------------------+   \+-------------------+|  
|  | VRF INSTANCES     |   | MANAGED VLANS     |   | IP ALLOCATIONS    ||  
|  |       12          |   |        85         |   |       1,024       ||  
|  \+-------------------+   \+-------------------+   \+-------------------+|  
|                                                                       |  
|  RECENT ACTIVITY                                     \[View Kanban\]    |  
|  \#1092 | SW-CORE-01 | CRITICAL | \[Progress\] | 2m ago                  |  
```
### **4.2 Device Inventory List**
```
\+-----------------------------------------------------------------------+  
| SEARCH: \[ core-switch\_\_\_\_\_\_\_ \]   TYPE: \[ All Devices V \]              |  
\+-----------------------------------------------------------------------+  
|  \+-------------------------------------------------------------------+|  
|  | Hostname    | IP Address   | Type      | Status     | Actions     ||  
|  |-------------|--------------|-----------|------------|-------------||  
|  | SW-CORE-01  | 10.0.0.1     | Switch    | \[Online\]   | \[V\] \[E\] \[D\] ||  
|  | SRV-DB-02   | 10.0.0.50    | Server    | \[Maint.\]   | \[V\] \[E\] \[D\] ||  
|  \+-------------------------------------------------------------------+|  
|                                     \* \[D\] Delete restricted to Admin  |  
\+-----------------------------------------------------------------------+
```
### **4.3 Device Detail View (Deep-Dive)**
```
\+-----------------------------------------------------------------------+  
|  \< Back to Inventory                                                  |  
|                                                                       |  
|  DEVICE: SW-CORE-01 \[Status: ONLINE\]                                  |  
|  \+---------------------------------+  \+-----------------------------+ |  
|  | SPECIFICATIONS                  |  | ASSIGNED IP ADDRESSES       | |  
|  | Model: Cisco Nexus 9000         |  | 1\. 10.0.0.1 (Management)    | |  
|  | Type:  Core Switch              |  | 2\. 10.0.0.2 (VLAN 10\)       | |  
|  | Loc:   Rack A, Row 4            |  | \[+ Assign New IP\]           | |  
|  \+---------------------------------+  \+-----------------------------+ |  
|                                                                       |  
|  MAINTENANCE HISTORY                                                  |  
|  \+-------------------------------------------------------------------+|  
|  | Date       | Ticket Title              | Severity  | Status       ||  
|  |------------|---------------------------|-----------|--------------||  
|  | 2024-05-10 | Port 24 Flapping          | Warning   | Resolved     ||  
|  | 2024-03-01 | Firmware Upgrade          | Info      | Resolved     ||  
|  \+-------------------------------------------------------------------+|  
\+-----------------------------------------------------------------------+
```
### **4.4 New Ticket Form (CRUD Interface)**
```
\+-----------------------------------------------------------------------+  
|  CREATE NEW MAINTENANCE TICKET                                        |  
|                                                                       |  
|  Ticket Title:   \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\]            |  
|                                                                       |  
|  Target Device:  \[ SW-CORE-01 (10.0.0.1)                V \]           |  
|                                                                       |  
|  Severity:       ( ) Low   ( ) Warning   (\*) Critical                 |  
|                                                                       |  
|  Description:    \+---------------------------------------+            |  
|                  | Please describe the hardware fault... |            |  
|                  |                                       |            |  
|                  \+---------------------------------------+            |  
|                                                                       |  
|                  \[ CANCEL \]             \[ CREATE TICKET \]             |  
\+-----------------------------------------------------------------------+
```
### **4.5 Ticket Update Lifecycle (GitHub-Style Thread)**

Maintenance tickets use a chronological thread model, allowing technicians to post Markdown-enabled updates and track status changes over time.
```
\+-----------------------------------------------------------------------+  
| TICKET: Fan Failure in Core Switch \#1092              \[CLOSE TICKET\]  |  
\+-----------------------------------------------------------------------+  
| \[OPEN\] tech\_admin opened this ticket 2 hours ago                      |  
|                                                                       |  
| \+-------------------------------------------------------------------+ |  
| | tech\_admin (Original Post)                                        | |  
| | "Fans in RU 40 are spinning at 0 RPM. Overheating hazard."        | |  
| \+-------------------------------------------------------------------+ |  
|             |                                                         |  
| \+-----------v-------------------------------------------------------+ |  
| | sys\_boss (Update)                                                 | |  
| | "Dispatching field tech with replacement chassis fan."            | |  
| \+-------------------------------------------------------------------+ |  
|                                                                       |  
| \[ POST AN UPDATE: (Markdown Enabled Text Area)        \] \[SAVE UPDATE\] |  
\+-----------------------------------------------------------------------+
```
### **4.6 Automated IP Allocation Form**

The IP allocation form uses a dynamic lookup system via the GetAvailableIPsView API endpoint. Selecting a prefix triggers an API call to `/ips/available/<prefix_id>/` that returns only available host addresses, preventing duplicate assignments.
```
\+-----------------------------------------------------------------------+  
| ALLOCATE NEW IP ADDRESS                                               |  
\+-----------------------------------------------------------------------+  
|                                                                       |  
| 1\. SELECT PREFIX RANGE: \[ 10.0.10.0/24 (Server-Net)              V \]  |  
|                                                                       |  
| 2\. AVAILABLE ADDRESS:   \[ 10.0.10.51 (Next Free)                 V \]  |  
|                         | \* 10.0.10.51                                |  
|                         | \* 10.0.10.52                                |  
|                         | \* 10.0.10.53                                |  
|                                                                       |  
| 3\. ASSIGN TO DEVICE:    \[ SRV-PROD-01                            V \]  |  
|                                                                       |  
| \[x\] Mark as Primary Management IP                                     |  
|                                                                       |  
|                                                  \[CONFIRM ALLOCATION\] |  
```
### **4.7 IPAM: VLAN & Prefix Management**

Tabular interfaces for managing logical network segments with site-specific scoping.
```
\+-----------------------------------------------------------------------+  
| VLAN MANAGEMENT                                            \[+ Add VLAN\] |  
\+-----------------------------------------------------------------------+  
|  VID   | NAME             | SITE             | STATUS     | ACTIONS   |  
|--------|------------------|------------------|------------|-----------|  
| \[ 10 \] | Server-Net       | DC-Alpha         | \[Active\]   | \[E\] \[D\]   |  
| \[ 20 \] | IoT-Sensors      | DC-Bravo         | \[Reserved\] | \[E\] \[D\]   |  
| \[ 30 \] | Guest-WiFi       | Global           | \[Active\]   | \[E\] \[D\]   |  
\+-----------------------------------------------------------------------+
```
### **4.8 Logical Network Map (VLAN/Site Topology)**

A high-level visualization of how Layer 2 segments span physical sites, allowing engineers to verify DCI (Data Center Interconnect) configurations.
```
+-----------------------------------------------------------------------+
| NETWORK TOPOLOGY MAP                                                  |
+-----------------------------------------------------------------------+
| [ SITE: DC-ALPHA ]             [ SITE: DC-BRAVO ]                     |
|  +----------------+             +----------------+                    |
|  | VLAN 10 (Srv)  |<----------->| VLAN 10 (Srv)  | [ VXLAN / DCI ]    |
|  +----------------+             +----------------+                    |
|         |                               |                             |
|  +----------------+             +----------------+                    |
|  | VLAN 20 (IoT)  |             | VLAN 30 (User) |                    |
|  +----------------+             +----------------+                    |
+-----------------------------------------------------------------------+
```

### **4.9 Mobile View & Responsive Adaptation**

The interface is optimized for field technicians on mobile devices, utilizing vertical stacking for cards and tables to prevent horizontal scrolling.
```
+--------------------------+    +--------------------------+
| [=]   NetDevFlow   [User]|    | [=]   NetDevFlow   [User]|
+--------------------------+    +--------------------------+
|                          |    |                          |
|  COMMAND CENTER          |    |  RACK: DC1-A01           |
|                          |    |  [ 24/42U OCCUPIED ]     |
|  [ ONLINE: 42 ]          |    |  +--------------------+  |
|  [ CRITICAL: 05 ]        |    |  | [40] SW-CORE-01    |  |
|                          |    |  +--------------------+  |
|  RECENT ACTIVITY         |    |  | [38] SRV-PROD-01   |  |
|  #1092 | SW-CORE-01      |    |  +--------------------+  |
|  [Progress]              |    |                          |
+--------------------------+    +--------------------------+
  (Vertical Dashboard)            (Compressed Rack View)
```


## **5\. Database Design (LO7)**

The database architecture is designed to enforce referential integrity and support multi-tenant maintenance workflows. It ensures that no orphan tickets or unassigned IPs can exist without a corresponding valid hardware asset.

### **5.1 Entity Relationship Diagram (ERD)**

![Mermaid Diagram](/Docs/mermaid-diagram-2026-02-27-094918.png)

```
erDiagram
    USER ||--|| PROFILE : "has"
    USER ||--o{ TICKET : "assigned_to"
    DATACENTER ||--o{ ROW : "contains"
    ROW ||--o{ RACK : "contains"
    RACK ||--o{ DEVICE : "houses"
    VRF ||--o{ PREFIX : "contains"
    VLAN ||--o{ PREFIX : "assigned_to"
    DATACENTER ||--o{ VLAN : "scoped_to"
    PREFIX ||--o{ IPADDRESS : "defines"
    DEVICE ||--o{ IPADDRESS : "assigns"
    DEVICE ||--o{ TICKET : "logs"

    DATACENTER {
        string name
        string physical_address
        string contact_info
    }
    ROW {
        string name
    }
    RACK {
        string name
        int ru_capacity
    }
    VLAN {
        int vid
        string name
        string status
    }
    VRF {
        string name
        string rd
    }
    PREFIX {
        string prefix
        string status
    }
    DEVICE {
        string hostname
        string model_name
        int position
        int size
        string status
    }
    IPADDRESS {
        string address
        string subnet_mask
        boolean is_primary
    }
    TICKET {
        string title
        string severity
        string status
    }
```

### **5.2 Schema Details**

| Model | LO | Technical Justification |
| :---- | :---- | :---- |
| **Profile** | LO3 | Extends User to handle 'PENDING' lock state and RBAC roles. |
| **DataCenter** | LO7 | Root site object; scopes physical infrastructure and VLAN broadcast domains. |
| **Row / Rack** | LO7 | Multi-level physical hierarchy ensuring hardware is locatable within a specific 42U rack. |
| **VRF** | LO7 | Virtual Routing & Forwarding instance; allows for overlapping IP space and multi-tenancy. |
| **VLAN** | LO7 | Layer 2 segmentation; scoped to DataCenters to prevent global broadcast leak. |
| **Prefix** | LO7 | Logic subnet container (e.g. 10.0.0.0/24); child of VRF and linked to VLANs. |
| **Device** | LO2 | The central asset; includes physical RU positioning and maintenance status. |
| **IPAddress** | LO2 | Validated host addresses; allocated from Prefixes and assigned to Devices. |
| **MaintenanceTicket** | LO2 | Linked to Devices; supports Markdown and Kanban status updates. |

## **6\. AI Reflection (LO8)**

* **Code Creation (8.1):** I leveraged AI to architect the Django Models and determine the most efficient field types. Specifically, the AI suggested using GenericIPAddressField, which provides built-in validation for both IPv4 and IPv6, saving manual regex implementation time. AI also helped architect the complex DCIM hierarchy and the Anti-Flash theme logic.
* **Debugging (8.2):** During the implementation of custom decorators for role-based access, AI identified a flaw in my permission-checking logic that would have allowed "Technicians" to bypass "Manager" restrictions. This intervention was critical for securing the application. It also identified race conditions in Kanban AJAX update
* **Optimisation (8.3):** To improve the user experience, AI suggested utilizing select\_related and prefetch\_related in my Django QuerySets. This optimization significantly reduced the number of database hits (solving the N+1 problem) and halved page load times for the inventory list.  
* **Unit Testing (8.4):** GitHub Copilot was instrumental in generating a comprehensive test suite in test\_models.py. It provided the boilerplate for edge-case testing, such as verifying that the system correctly rejects duplicate IP assignments or malformed hostname strings. It also generated edge-case tests for CIDR prefix validation.

7. Quality Assurance (LO4)

The project includes an automated test suite in inventory/tests.py verifying:

1. **RBAC:** Technicians are blocked (403) from decommissioning hardware.
2. **Security:** Pending users are redirected to a restricted view.
3. **Logic:** IP allocation API correctly identifies used vs available addresses.
4. **CRUD:** All models support full lifecycle management.
5. **JavaScript:** Verified interactive components including Kanban drag-and-drop state persistence, dynamic IP allocation API fetching, and the anti-flash theme switching logic. Testing ensures event listeners remain robust during DOM manipulation and API failures are handled with user-friendly error messages.

### **7.1 Feature Validation & Manual Testing (LO4.3)**

The following matrix documents the manual verification of core system requirements against expected outcomes to ensure operational stability.

| Feature | Action | Expected Result | Status |
| :---- | :---- | :---- | :---- |
| **User Lockout** | Register as a new user. | Account created but access restricted to dashboard until approval. | **PASS** |
| **RBAC Enforcement** | Attempt to delete device as 'Technician'. | System returns a 403 Forbidden page or restricts UI visibility. | **PASS** |
| **IP Allocation** | Select a full /30 prefix. | API returns only available host IPs; form blocks invalid entries. | **PASS** |
| **Kanban Persistence** | Drag ticket to 'Resolved'. | Refresh page; ticket remains in 'Resolved' column. | **PASS** |
| **Rack Collision** | Install 2U device in occupied RU. | Form validation fails; error message regarding physical space conflict. | **PASS** |
| **Dark Mode Sync** | Toggle theme in Admin HQ. | Main site theme updates immediately via localStorage sync. | **PASS** |
| **Responsive Design** | View Inventory on Mobile. | Tables transform into vertically stacked cards for legibility. | **PASS** |

Run tests: python manage.py test inventory

### **7.2 Lighthouse Performance (LO1.1 / LO2.1)**

NetDevFlow is engineered for high performance, achieving a perfect 100/100/100/100 score across all Google Lighthouse metrics.

![Lighthouse Scores](/Docs/Lighthouse.jpg)

* **Performance (100):** Optimized via Gunicorn, WhiteNoise, and the Anti-Flash theme engine to ensure sub-second Time to Interactive (TTI).

* **Accessibility (100):** Adheres to WCAG 2.1 standards with semantic HTML5, high-contrast theme variables, and full ARIA labeling for screen readers.

* **Best Practices (100):** Utilizes secure headers, HTTPS enforcement, and modern web standards (ES6+, modern CSS variables).

* **SEO (100):** Implements structured metadata and semantic heading hierarchies for technical auditability.

## **8\. Deployment Process**

NetDevFlow is optimized for deployment on the **Heroku** platform using a distributed architecture.

### **8.1 Production Architecture**

* **Web Server:** Gunicorn (Green Unicorn) for handling concurrent requests.  
* **Static Files:** WhiteNoise serves CSS/JS directly from the web process.  
* **Media Storage:** Since Heroku has an ephemeral filesystem, Cloudinary is used to store device\_image uploads permanently.  
* **Database:** Heroku Postgres provides a managed relational database.

### **8.2 Deployment Steps**

1. **Environment Preparation:**  
   Ensure requirements.txt contains dj-database-url, psycopg2-binary, whitenoise, and cloudinary. Ensure the Procfile is present:  
   ```
   release: python manage.py migrate  
   web: gunicorn netdevflow\_project.wsgi
   ```

2. **Heroku App Creation:**  
   ```
   heroku create netdevflow-app  
   heroku addons:create heroku-postgresql:mini
   ```

3. **Setting Config Vars (Environment Variables):**  
   Sensitive keys are never committed to Git. Set them via the Heroku Dashboard or CLI:  
   ```
   \# Security & Mode  
   
   heroku config:set SECRET\_KEY='your-private-key'  
   heroku config:set DJANGO\_DEBUG='False'
   

   \# Cloudinary (Media Storage)  
   heroku config:set CLOUDINARY\_URL='cloudinary://api\_key:api\_secret@cloud\_name'

   \# Allowed Hosts  
   heroku config:set ALLOWED\_HOSTS='netdevflow-app.herokuapp.com'
   ```

4. **Push to Production:**  
   ```git push heroku main```

5. **Post-Deployment Tasks:**  
   ```
   \# Run initial migrations if release phase failed  
   heroku run python manage.py migrate

   \# Create initial admin account  
   heroku run python manage.py createsuperuser
   ```

### **8.3 Local vs Production Workflow**

The application uses dj-database-url in settings.py to automatically switch between:

* **Local:** db.sqlite3 (for rapid development).  
* **Production:** Heroku Postgres (for high-concurrency relational storage).

This satisfies **LO6** by demonstrating a professional deployment pipeline with environment-specific configurations.

### **9. Future Roadmap & Easter Eggs**

To add a layer of personality and engagement for the technical teams using this tool, NetDevFlow includes hidden "Easter Eggs" throughout the platform.

* **Bug Squasher 5000:** A Galaga-inspired space shooter is hidden within the 500 Server Error page. Clicking the pulsing server icon five times activates the game, allowing technicians to "squash bugs" while waiting for infrastructure to stabilize.

* **Expansion Plans & Visualization Strategy**: Given more development time, the vision for NetDevFlow includes advanced visual analytics to help engineers master their infrastructure at a glance:  
  * **Dynamic Topology Mapping**: Implementation of a D3.js powered "Network Map" that automatically renders Layer 2 and Layer 3 relationships, allowing users to visualize spanning-tree paths and routing neighbors.  
  * **Physical Connection Mapping**: A "Cable Trace" visualization that maps the physical path from a server's NIC, through patch panels, to the specific core switch port.  
  * **3D Data Center Visualization**: Moving beyond 2D elevations to a full 3D interactive floor plan, using heatmaps to represent real-time power consumption and cooling efficiency across racks.  
  * **Gamified Engineering**: Introduction of "Performance Badges" and "SLA Trophies" for resolving high-severity maintenance tickets, celebrating the efforts of the infrastructure engineers behind the scenes.
  * **Dockerfication**: This system is designed to be run in house, so conversion over to in house running of the application will be required

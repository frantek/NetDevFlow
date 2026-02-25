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
* **Frontend:** A combination of Semantic HTML5, Custom CSS3, and Bootstrap 5 ensures a professional, responsive interface that maintains high accessibility standards (WCAG).  
* **Database:** PostgreSQL is utilized for its reliability and support for complex relationship queries.  
* **Deployment:** Heroku Cloud Hosting for scalable, high-availability production access.

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

The IP allocation form uses a dynamic lookup system. Selecting a prefix triggers an API call that returns only available host addresses, preventing duplicate assignments.
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
### **4.3 IPAM: VLAN & Prefix Management**

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
### **4.8 Mobile View (Technician Interface)**
```
\+-----------------------+  
| \[=\]   NetDevFlow  \[U\] |  
\+-----------------------+  
| Welcome, Tech1        |  
| \[+ Device\] \[+ Ticket\] |  
\+-----------------------+  
| ONLINE DEVICES: 42    |  
| \[||||||||||     \]     |  
\+-----------------------+  
| CRITICAL TICKETS: 05  |  
| \[\!\!           \]       |  
\+-----------------------+  
| RECENT LOGS:          |  
| \> SW-CORE-01: Alert   |  
| \> SRV-DB-02: Fixed    |  
\+-----------------------+
```
## **5\. Database Design (LO7)**

The database architecture is designed to enforce referential integrity and support multi-tenant maintenance workflows. It ensures that no orphan tickets or unassigned IPs can exist without a corresponding valid hardware asset.

### **5.1 Entity Relationship Diagram (ERD)**

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

* **Code Creation (8.1):** I leveraged AI to architect the Django Models and determine the most efficient field types. Specifically, the AI suggested using GenericIPAddressField, which provides built-in validation for both IPv4 and IPv6, saving manual regex implementation time.  
* **Debugging (8.2):** During the implementation of custom decorators for role-based access, AI identified a flaw in my permission-checking logic that would have allowed "Technicians" to bypass "Manager" restrictions. This intervention was critical for securing the application.  
* **Optimisation (8.3):** To improve the user experience, AI suggested utilizing select\_related and prefetch\_related in my Django QuerySets. This optimization significantly reduced the number of database hits (solving the N+1 problem) and halved page load times for the inventory list.  
* **Unit Testing (8.4):** GitHub Copilot was instrumental in generating a comprehensive test suite in test\_models.py. It provided the boilerplate for edge-case testing, such as verifying that the system correctly rejects duplicate IP assignments or malformed hostname strings.

7. Quality Assurance (LO4)

The project includes an automated test suite in inventory/tests.py verifying:

1. **RBAC:** Technicians are blocked (403) from decommissioning hardware.
2. **Security:** Pending users are redirected to a restricted view.
3. **Logic:** IP allocation API correctly identifies used vs available addresses.
4. **CRUD:** All models support full lifecycle management.

Run tests: python manage.py test inventory

## **8\. Deployment Process**

The application is configured for a professional production environment on Heroku, utilizing a Gunicorn WSGI server and a secure PostgreSQL add-on.

1. **Environment Config:** Create a Procfile and requirements.txt. Set DEBUG=False and move the SECRET\_KEY and database credentials to Heroku Config Vars.  
2. **Static Assets:** Configure WhiteNoise or a similar solution to serve static CSS and JS files directly through Gunicorn.  
3. **CI/CD Integration:** Link the GitHub repository to the Heroku pipeline for seamless automated deployments whenever changes are merged to the main branch.  
4. **Data Migration:** Execute heroku run python manage.py migrate to securely initialize the database schema in the production environment and create the initial admin superuser.

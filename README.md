# **NetDevFlow: Infrastructure & Incident Management**

NetDevFlow is an AI-augmented infrastructure management tool (DCIM/IPAM) designed specifically for IT operations teams to document complex network assets and track maintenance incidents within a single, unified interface. It bridges the critical gap between hardware inventory and daily task management, ensuring that technical debt and physical maintenance are tracked alongside the assets they affect.

**Live Link:** \[Your Heroku URL Here\]

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
| \[NetDevFlow Logo\]          Dashboard   Inventory   Tickets   \[User V\] |  
\+-----------------------------------------------------------------------+  
|                                                                       |  
|  Welcome back, Admin\!                          \[+ Device\]  \[+ Ticket\] |  
|                                                                       |  
|  \+-------------------+   \+-------------------+   \+-------------------+|  
|  | ONLINE DEVICES    |   | CRITICAL TICKETS  |   | AVAILABLE IPS     ||  
|  |       42          |   |        05 (Alert) |   |       112         ||  
|  | \[||||||||||     \] |   | \[\!\!           \]   |   | \[||||||       \]   ||  
|  \+-------------------+   \+-------------------+   \+-------------------+|  
|                                                                       |  
|  SYSTEM LOG: Switch-04 status changed to "Maintenance" (10m ago)      |  
\+-----------------------------------------------------------------------+
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
### **4.5 Mobile View (Technician Interface)**
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
## **5\. Database Schema (LO7)**

The database architecture is designed to enforce referential integrity, ensuring that no orphan tickets or unassigned IPs can exist without a corresponding device.

| Model | Fields | Relationship | Technical Justification |
| :---- | :---- | :---- | :---- |
| **User** | username, role, is\_staff | \- | Extends Django Auth to support Granular Role-Based Access Control (RBAC). |
| **Device** | hostname, model, type, status, location | \- | The central node of the schema; acts as the primary parent for all metadata. |
| **IPAddress** | address, subnet, device, is\_active | ForeignKey(Device) | Uses a ForeignKey to allow one device to hold multiple IP interfaces (e.g., Management and Production). |
| **Ticket** | title, severity, status, description, device | ForeignKey(Device) | Establishes a permanent audit trail for hardware; tickets cannot be deleted without record. |

## **6\. AI Reflection (LO8)**

* **Code Creation (8.1):** I leveraged AI to architect the Django Models and determine the most efficient field types. Specifically, the AI suggested using GenericIPAddressField, which provides built-in validation for both IPv4 and IPv6, saving manual regex implementation time.  
* **Debugging (8.2):** During the implementation of custom decorators for role-based access, AI identified a flaw in my permission-checking logic that would have allowed "Technicians" to bypass "Manager" restrictions. This intervention was critical for securing the application.  
* **Optimisation (8.3):** To improve the user experience, AI suggested utilizing select\_related and prefetch\_related in my Django QuerySets. This optimization significantly reduced the number of database hits (solving the N+1 problem) and halved page load times for the inventory list.  
* **Unit Testing (8.4):** GitHub Copilot was instrumental in generating a comprehensive test suite in test\_models.py. It provided the boilerplate for edge-case testing, such as verifying that the system correctly rejects duplicate IP assignments or malformed hostname strings.

## **7\. Deployment Process**

The application is configured for a professional production environment on Heroku, utilizing a Gunicorn WSGI server and a secure PostgreSQL add-on.

1. **Environment Config:** Create a Procfile and requirements.txt. Set DEBUG=False and move the SECRET\_KEY and database credentials to Heroku Config Vars.  
2. **Static Assets:** Configure WhiteNoise or a similar solution to serve static CSS and JS files directly through Gunicorn.  
3. **CI/CD Integration:** Link the GitHub repository to the Heroku pipeline for seamless automated deployments whenever changes are merged to the main branch.  
4. **Data Migration:** Execute heroku run python manage.py migrate to securely initialize the database schema in the production environment and create the initial admin superuser.

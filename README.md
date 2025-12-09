# DormHub - Smart Rental and Room Management System

## Project Overview & Problem Statement  
DormHub is a comprehensive dormitory and residential management system developed using **Python** and the **Flet** UI framework. It provides dual portals for Landlords/Admins and Residents to streamline daily operations and communication.

The project addresses the challenges of manual management for landlords by offering tools for room assignment, financial oversight, maintenance tracking, and centralized communication. For residents, it simplifies tracking rent, submitting requests, and accessing necessary information.

## Feature List & Scope  
| Feature / Module | In Scope (✓) / Out of Scope (✗) | Notes / Limitations |
|------------------|-------------------------------|---------------------|
| Admin (Landlord) Portal | ✓ | Comprehensive management including Rooms, Residents, Payments, Maintenance, and Announcements. |
| Resident Portal | ✓ | Details for My Room, Rent Payments, Maintenance Requests, Community Announcements, and Profile Settings. |
| User Authentication | ✓ | Secure login/registration for both roles; Resident registration requires a 6-digit **Landlord** **Access** **Key**. |
| Data Visualization | ✓ | Dynamic charts in the Overview section showing occupancy trends and financial summaries. |
| Real-time Updates | ✓ | Background tasks automatically fetch and refresh core data every 5 seconds. |
| Payment Integration | ✗ | No live payment gateway implemented; payments are currently recorded manually. |

## Architecture Diagram  
```
[ Flet UI layer ]  ↔  [ Python Page/Section Logic (AdminPage, ResidentPage) ]  ↔  [ Database (MySQL/aiomysql) ]
                     ↕
        [ Emerging Tech: Dynamic Data Updates & Visualization ]
```
**Folder Structure:**  
- `/src/pages` – Contains main page handlers (admin_page.py, resident_page.py, login_page.py). 
- `/src/pages/section` – Contains the individual content views (e.g., overview.py, rooms.py, maintenance.py).  
- `/src/utils` – Utility functions for reusable UI elements.
- `/src/assets` – Images and icons used in the application. 
- `/src/database.py` – Handles all MySQL database connection and CRUD operations.
- `main.py` – Application entry point. 

## Data Model  
The core data is persisted in a MySQL database. All dynamic user and resident-specific metadata (e.g., room assignment, payment history, access key) are stored as a JSON string within the data column of the users table.

Example JSON schema for a menu item:  

```json
{
  "role": "resident", 
  "access_key": "N/A", 
  "linked_admin_id": 1, 
  "room_id": "101", 
  "move_in_date": "1701700000",
  "due_date": "1704300000",
  "payment_history": [ ... ], 
  "unpaid_dues": [ ... ], 
  "phone_number": "1234567890"
}
```

## Emerging Tech Explanation  
DormHub integrates **Dynamic Data Visualization** and **Real-time UI Updates** as a core feature.

**Why chosen:** To provide Admins with actionable insights into occupancy, revenue, and outstanding tasks via interactive charts that reflect the latest data.  

**Integration:** The Overview screen executes an asynchronous background loop (update_data_loop in overview.py) that fetches fresh data from the MySQL database and updates chart controls (e.g., LineChart, BarChart) every 5 seconds. This ensures that visual analytics and statistics are nearly real-time. 
 

## Setup & Run Instructions  
The project uses uv and flet for dependency management and application execution.

1. **Database Setup (Prerequisite)** The application is configured to connect to a MySQL database with hardcoded connection parameters.

- **Server:** localhost
- **User:** root
- **Password:** (empty string)
- **Database:** dormhub_database

Ensure your local MySQL instance is running. The necessary tables (users, rooms, requests, announcements, comments) will be created automatically upon the first successful run.


2. **Create and Navigate** 
```bash
git clone https://github.com/0xDei/DormHub.git
cd DormHub
```  

3. **Install Dependencies** using uv (recommended, dependencies are defined in pyproject.toml):
```bash
uv sync
```  
*OR* using poetry:
```bash
poetry install
```  

4. **Run** **the** **Application** as desktop application:  
```bash
uv run flet run
# OR
poetry run flet run
```  
**Supported Platforms:** Windows, Linux (Python 3.13 recommended)  


## Team Roles & Contribution Matrix  
| Contributor | Role / Responsibilities | Contributions / Modules |
|-------------|------------------------|------------------------|
| Deiven Joseph Pimentel | Backend logic / Core logic / Lead Developer/ Data model | Core Admin/Resident Data Logic, Database,  UI Implementation, Design og Admin/Resident Portals |
| Joshua Sario| UI Design / Frontend Development / Documentation | UI Implementation, Some sections in both Admin and Resident Panel, Documentation & README |
| Luis Albaño | Testing / Documentaion | Test scripts, Documentation|

## Risk / Constraints & Future Enhancements  
**Risks / Constraints:**  
- **Security Risk:** User passwords (including Admin) are currently stored as plain text in the database. This must be upgraded to use password hashing for production deployment.
- **Dependency:** Requires a running MySQL server instance and assumes default local connection settings.
- **Payment:** Payments must be recorded manually by the Admin or Resident; no automated payment gateway is integrated.

**Future Enhancements:**  
- Implement secure password hashing to protect user credentials. 
- Integrate a Payment Gateway for automated rent payment tracking. 
- Expand the analytics in the Overview dashboard (e.g., occupancy predictions).

## Individual Reflection  

**Deiven Joseph Pimentel (Backend logic / Core logic):**  
As the backend and data lead, my focus was on the complex interaction between Flet's asynchronous environment and the MySQL database. The main technical challenge was designing a fluid database schema using MySQL while embedding dynamic application data as JSON strings within the users table. I successfully implemented core financial logic, including the calculation of Maintenance Badge Counts and the automated Overdue Payment generation logic, ensuring data integrity was maintained despite multiple dependencies. This role significantly sharpened my skills in scalable database design and developing reliable core business logic.

**Joshua Sario (UI Design / Frontend Development):**  
My primary role was translating the functional requirements into a cohesive and intuitive graphical user interface using Flet. The key challenge was ensuring a clear distinction and consistent navigation between the Admin and Resident Portals, while creating reusable components like create_info_card. I am particularly proud of implementing the Dynamic Data Visualization in the Admin Overview, linking the live database updates to update the Flet chart controls. This project cemented my understanding of modular Flet architecture and user-centric design principles.

**Luis Albaño (Testing / Quality Assurance):**  
I was responsible for ensuring the application's reliability and security validation. My focus was on developing test plans for critical features, notably verifying the Access Key registration security and the Access Control between user roles. The most complex testing involved validating the multi-step financial logic—specifically, ensuring that recording a payment correctly clears Unpaid Dues and advances the Next Due Date. This experience reinforced the importance of thorough end-to-end testing, especially when handling financial data and maintaining data consistency across different user views.

---

## Acknowledgments  
**Acknowledgments:**

- Developed using the **Flet** framework
- MySQL and the aiomysql library for database connectivity
- Flet framework and open-source inspirations  


# **User Manual of DormHub**

### **1. Root Page**
The application root page prompts the user to select their portal

**Admin Dashboard:** For landlords to manage the property, residents, and finances. Resident **Dashboard:** For tenants to view their room, pay rent, and submit requests.

![Root Page](src\assets\main.png)

## **As Admin**

In the root page, select **Continue as Admin**

### Register Admin
On the Login page, click **Register here** and fill out required field the click **Register Admin**

![src/assets/admin_register.png]

### Login Admin
After register, log in as admin using email address and password then click **Log In**

![src/assets/admin_login.png]


### Overview Section

After successful logging in as Admin, you will be linked to overview section

Displays total beds, resident count, estimated monthly income, and pending maintenance tasks. Data visualizations (charts) update every after activity.

![src/assets/admin_overview.png]


### Rooms Section

View, create, and edit rooms. Set bed capacity, monthly rent, and status override (maintenance). Tracks current occupancy automatically.

![src/assets/admin_rooms.png]

#### Add Room
To add room, click to **Add Room** button at the top right
![src/assets/admin_room_add.png]

#### Edit Room
In editing room, click the **Edit** button
![src/assets/admin_room_edit.png]

#### Delete Room
For deletion, click **Delete**
![src/assets/admin_room_delete.png]


### Residents Section

View and search residents linked to your admin account. Filter by Assigned or Unassigned rooms. Allows linking/unlinking residents to rooms, updating contact info, and setting move-in dates.

![src/assets/admin_residents.png]

#### Filter Residents
To filter residents, choose option on the dropdown menu
![src/assets/admin_resident_sort.png]

#### Search Resident
In searching resident, just type resident's username in the search bar
![src/assets/admin_resident_search.png]

#### Edit Resident
To edit resident, click the pen icon button
![src/assets/admin_resident_edit.png]

#### Delete Resident
Delete resident by clicking trash icon button
![src/assets/admin_resident_delete.png]


### Payments Section

Tracks monthly collected revenue and total outstanding dues. System automatically creates new overdue dues and advances the next due date. Allows manually Recording Payments for residents.

![src/assets/admin_payments.png]

#### Record Payment
Record Payment using the **Record Payment** button
![src/assets/admin_payment_record.png]

#### Filter Residents
To filter residents according to their payment status, click the dropdown menu
![src/assets/admin_payment_sort.png]

#### Search Resident
Search resident by typing their username in search bar
![src/assets/admin_payment_search.png]

#### Check Resident's Payment History
Click the clock icon to check resident's payment history
![src/assets/admin_payment_history.png]


### Maintenance Section

View all maintenance requests submitted by linked residents. Filter by status (pending, in-progress, completed). Allows updating the status of a request.

![src/assets/admin_maintenance.png]

#### Filter Requests
Filter requests by status by choosing status in dropdown menu
![src/assets/admin_maintenance_sort.png]

#### Update Requests
Update requests status using dropdown menu
![src/assets/admin_maintenance_edit.png]


### Announcements Section

Create new posts for residents. View existing posts, comments (replying as "Landlord"), and resident engagement (likes).

![src/assets/admin_announcements.png]

#### Add New Post
Add new post using **New Post** button
![src/assets/admin_announcement_new.png]

#### Check Comments
Check comments by clicking **View Comments**
![src/assets/admin_annoucement_comment.png]


### Access Key Section
Displays unique 6-digit Landlord Access Key and provides a quick option to copy it for sharing with new residents.

![src/assets/admin_accesskey.png]


### Log out as Admin
To log out admin, click the **Logout** button
![src/assets/admin_logout.png]



## **As Resident**

In the root page, choose **Continue as Resident**

### Register Resident
On the Login page, click Register here.

Fill out the required fields, including the **Landlord Access Key**.

The system validates the key to link the Resident account to the correct Admin.

![src/assets/resident_register.png]

### Login Resident
Login registered resident using **username** and **password**

![src/assets/resident_login.png]


### My Room Section

These should be the landing page when you succesfully logged in

This section displays next payment due, rent amount, active maintenance requests, bed count, move-in date, and roommate list. 

![src/assets/resident_myroom.png]

#### View Room
You can view room by clicking the room image
![src/assets/resident_myroom_view.png]


### Announcements Section

View posts from the linked Admin. Features unread badge count, the ability to like posts, and full commenting/replying functionality.

![src/assets/resident_announcements.png]

#### Like Announcement
You can like an announcement by hitting the heart icon
![src/assets/resident_announcement_like.png]

#### Add Comment on Announcement
Add comment on announcement using message icon button
![src/assets/resident_announcement_comment.png]


### Payment Section

Displays Upcoming Payment information (due date and amount), Unpaid Dues, and Payment History (on-time or late status). Allows voluntarily adding a manual payment record.

![src/assets/resident_payment.png]

#### Add Payment
Manually add payment using **Add Payment** button
![src/assets/resident_payment_addpayment.png]


### Requests Section

Submit new maintenance requests to the Admin. Track the status (Pending, In-Progress, Completed) and urgency (Low, Medium, High) of all submitted requests.

![src/assets/resident_request.png]

#### Add New Request
To add new request, click the **New Request** button
![src/assets/resident_request_new.png]


### Settings Section

Change Username/Email (Profile) and Password (Security). Toggle Notifications to manage alerts.

![src/assets/resident_settings.png]

#### Change Username/Email Address
![src/assets/resident_settings_username.png]

#### Change Password
![src/assets/resident_settings_password.png]


### Log out as User
Click **Logout** button to log out as user
![src/assets/resident_logout.png]






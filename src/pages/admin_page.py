import flet as ft
from pages.sections.overview import Overview
from pages.sections.rooms import Rooms
from pages.sections.residents import Residents
from pages.sections.admin_payment import AdminPayment
from pages.sections.maintenance import Maintenance
from pages.sections.admin_announcements import AdminAnnouncements
# IMPORT NEW SECTION
from pages.sections.access_key import AccessKeySection 
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton
import json

class AdminPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.view = None
        self.data = {}
        self.navbar = None
        self.username = "Administrator"
        self.email = None 
        self.admin_access_key = "" # Field to store the 6-digit key
        # NEW: Maintenance count for the navbar badge
        self.maintenance_count = 0 

    def update_maintenance_badge(self):
        """Finds the Maintenance button and sets its badge count directly."""
        if self.navbar and self.navbar.buttons:
            for btn in self.navbar.buttons:
                # Check if it's the Maintenance button
                if isinstance(btn, NavBarButton) and btn.text == "Maintenance":
                    btn.set_badge_count(self.maintenance_count)
                    # Force the entire navbar container to re-render to reflect changes inside its button controls
                    self.navbar.update() 
                    break
                    
    async def update_data(self):
        # Fetch fresh user data to get username/email/AccessKey
        active_user_id = self.page.data.get_active_user()
        if active_user_id is None: return # Safety check if user is somehow logged out

        user_res = await self.page.data.get_user_by_id(active_user_id)
        if user_res:
            user_record = user_res[0]
            self.username = user_record[1]
            self.email = user_record[2]
            try:
                # --- FIX APPLIED HERE: Extract access_key from the data column ---
                user_data = json.loads(user_record[4])
                self.admin_access_key = user_data.get("access_key", "") # Retrieve the key
            except:
                self.admin_access_key = ""

        # Update other data lists
        self.data.update({"residents": await self.page.data.get_all_users()})
        self.data.update({"rooms": await self.page.data.get_all_rooms()})
        all_requests = await self.page.data.get_all_requests()
        self.data.update({"requests": all_requests})
        
        # --- NEW MAINTENANCE COUNT LOGIC ---
        all_users = await self.page.data.get_all_users()
        current_admin_id = active_user_id
        
        # 1. Identify all users linked to this admin
        linked_user_ids = {current_admin_id} 
        for user in all_users:
            user_id = user[0]
            try:
                u_data = json.loads(user[4])
                if u_data.get("role") == "resident" and u_data.get("linked_admin_id") == current_admin_id:
                    linked_user_ids.add(user_id)
            except:
                continue

        # 2. Count non-completed requests from linked users
        maintenance_count = 0
        for req in all_requests:
            # req: (id, room_id, issue, current_status, urgency, user_id, date_created, date_updated)
            req_user_id = req[5]
            status = req[3]
            
            # Count if the request is from a linked user AND is not completed
            if req_user_id in linked_user_ids and status != "completed":
                maintenance_count += 1
                
        self.maintenance_count = maintenance_count
        
        # After recalculating the count, update the badge only if the navbar is built.
        if self.navbar:
            self.update_maintenance_badge()
        # --- END NEW MAINTENANCE COUNT LOGIC ---


    async def show(self):
        # We MUST update data first to ensure self.admin_access_key is populated
        await self.update_data()
        
        self.navbar = NavBar(
            isAdmin=True, current_page=self,
            buttons=[
                NavBarButton(ft.Icons.INSERT_CHART_OUTLINED_ROUNDED, "Overview", lambda e: self.change_tab(Overview(self), "Overview"), True),
                NavBarButton(ft.Icons.HOME_ROUNDED, "Rooms", lambda e: self.change_tab(Rooms(self), "Rooms")),
                NavBarButton(ft.Icons.PEOPLE_OUTLINE_ROUNDED, "Residents", lambda e: self.change_tab(Residents(self), "Residents")),
                NavBarButton(ft.Icons.PAYMENTS_OUTLINED, "Payments", lambda e: self.change_tab(AdminPayment(self), "Payments")),
                # APPLY THE MAINTENANCE COUNT HERE
                NavBarButton(ft.Icons.BUILD_CIRCLE_OUTLINED, "Maintenance", lambda e: self.change_tab(Maintenance(self), "Maintenance"), badge_count=self.maintenance_count),
                NavBarButton(ft.Icons.CAMPAIGN_OUTLINED, "Announcements", lambda e: self.change_tab(AdminAnnouncements(self), "Announcements")),
                # ADD THE NEW ACCESS KEY SECTION
                NavBarButton(ft.Icons.KEY_OUTLINED, "Access Key", lambda e: self.change_tab(AccessKeySection(self), "Access Key")),
            ]
        )
        
        initial_section = Overview(self)
        
        self.view = ft.View(
            "/active-admin", 
            [
                ft.Row(
                    [self.navbar, initial_section], 
                    spacing=0, 
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH, 
                    expand=True
                )
            ], 
            bgcolor="#FFFBEB", 
            padding=ft.padding.only(top=-4)
        )
        return self.view

    def change_tab(self, section, button_text):
        """Switches the content section and updates navbar highlighting."""
        self.navbar.highlight_tab(button_text)
        self.page.run_task(self.show_section, section)

    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)
        await self.update_data()
        self.view.update()
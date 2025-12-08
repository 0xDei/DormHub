import flet as ft
import json
import time 
from pages.sections.my_room import MyRoom
from pages.sections.payment import Payment
from pages.sections.requests import Requests
from pages.sections.resident_announcements import ResidentAnnouncements
from pages.sections.settings import Settings # Import Settings
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class ResidentPage:
    def __init__(self, page: ft.Page, user_id):
        super().__init__()
        self.page = page
        self.id = user_id
        self.username = None; self.email = None; self.password = None; self.data = None
        self.unread_count = 0 
        self.announcements_btn = None 

    async def update_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        if not res: return
        self.username = res[0][1]; self.email = res[0][2]; self.password = res[0][3]
        try: self.data = json.loads(res[0][4])
        # FIX: Ensure 'roommate_data' is initialized in case of corrupted/new data
        except: self.data = {"room_id": "N/A", "move_in_date": "N/A", "due_date": "N/A", "payment_history": [], "unpaid_dues": [], "phone_number": "N/A", "linked_admin_id": "N/A", "roommate_data": []}
        
        for k in ["room_id", "move_in_date", "due_date", "phone_number", "linked_admin_id"]: 
            if k not in self.data: self.data[k] = "N/A"
        for k in ["payment_history", "unpaid_dues"]:
            if k not in self.data: self.data[k] = []
        if "last_checked_announcements" not in self.data:
            self.data["last_checked_announcements"] = 0
        # FIX: Also ensure roommate_data exists here
        if "roommate_data" not in self.data:
            self.data["roommate_data"] = []

        # --- Count Unread Announcements ---
        try:
            # Pass the linked_admin_id to filter announcements
            admin_id = self.data.get("linked_admin_id")
            posts = await self.page.data.get_announcements(admin_user_id=admin_id)
            
            self.unread_count = 0
            if posts:
                last_checked = self.data.get("last_checked_announcements", 0)
                for p in posts:
                    # Date is now at index 4 (p[4]), not p[3]
                    if int(p[4]) > last_checked:
                        self.unread_count += 1
        except Exception as e:
            print(f"Error checking unread: {e}")
            self.unread_count = 0

        if self.data["room_id"] != "N/A":
            reqs = await self.page.data.custom_query("SELECT * FROM requests WHERE room_id=%s AND user_id=%s", (self.data["room_id"], self.id))
            self.data["requests_data"] = [{"id": r[0], "issue": json.loads(r[2]), "status": r[3], "urgency": r[4], "date_created": r[6]} for r in reqs]
            
            room = await self.page.data.custom_query("SELECT residents, monthly_rent, bed_count, current_status, thumbnail FROM rooms WHERE id=%s", (self.data["room_id"],))
            if room:
                self.data.update({"monthly_rent": room[0][1], "bed_count": room[0][2], "room_status": room[0][3], "thumbnail": room[0][4]})
                try:
                    all_users = await self.page.data.get_all_users()
                    roommates_list = []
                    roommate_data_list = [] # List to store full user data for MyRoom

                    for u in all_users:
                        # Skip self
                        if u[0] == self.id: continue
                        
                        u_data = json.loads(u[4])
                        # Only include users with the same room_id
                        if str(u_data.get("room_id")) == str(self.data["room_id"]):
                            roommates_list.append(u[1]) # Username
                            roommate_data_list.append(u_data) # Full data for phone, etc.

                    self.data["roommates"] = roommates_list
                    # FIX: Populate the missing roommate_data field
                    self.data["roommate_data"] = roommate_data_list 
                except: self.data["roommates"] = []; self.data["roommate_data"] = []
        else:
            # FIX: Initialize the missing roommate_data field for unassigned rooms
            self.data.update({"requests_data": [], "monthly_rent": 0, "thumbnail": "placeholder.jpg", "roommates": [], "roommate_data": []})

    async def show(self):
        # Load data first so unread count is accurate
        await self.update_data()

        # Create Announcements Button
        self.announcements_btn = NavBarButton(
            ft.Icons.CAMPAIGN_OUTLINED, 
            "Announcements", 
            lambda e: self.change_tab(ResidentAnnouncements(self), "Announcements"),
            badge_count=self.unread_count
        )

        self.navbar = NavBar(isAdmin=False, current_page=self, buttons=[
            NavBarButton(ft.Icons.BED, "My Room", lambda e: self.change_tab(MyRoom(self), "My Room"), True),
            self.announcements_btn, 
            NavBarButton(ft.Icons.CREDIT_CARD_ROUNDED, "Payments", lambda e: self.change_tab(Payment(self), "Payments")),
            NavBarButton(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, "Requests", lambda e: self.change_tab(Requests(self), "Requests")),
            NavBarButton(ft.Icons.SETTINGS_OUTLINED, "Settings", lambda e: self.change_tab(Settings(self), "Settings")) # Added Button
        ])
        
        initial_section = MyRoom(self)
        
        self.view = ft.View(
            "/active-resident",
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
        self.navbar.highlight_tab(button_text)
        
        if button_text == "Announcements":
            self.page.run_task(self.mark_announcements_read)
            
        self.page.run_task(self.show_section, section)

    async def mark_announcements_read(self):
        self.announcements_btn.set_badge_count(0)
        self.unread_count = 0
        self.data["last_checked_announcements"] = int(time.time())
        await self.page.data.update_user(self.id, self.username, self.email, self.password, self.data)

    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: 
            self.view.controls[0].controls[1] = section
        else: 
            self.view.controls[0].controls.append(section)
        await self.update_data()
        self.view.update()
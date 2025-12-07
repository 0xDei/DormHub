import flet as ft
import json
from pages.sections.my_room import MyRoom
from pages.sections.payment import Payment
from pages.sections.requests import Requests
from pages.sections.resident_announcements import ResidentAnnouncements
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class ResidentPage:
    def __init__(self, page: ft.Page, user_id):
        self.page = page
        self.id = user_id
        self.username = None; self.email = None; self.password = None; self.data = None

    async def update_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        if not res: return
        self.username = res[0][1]; self.email = res[0][2]; self.password = res[0][3]
        try: self.data = json.loads(res[0][4])
        except: self.data = {"room_id": "N/A", "move_in_date": "N/A", "due_date": "N/A", "payment_history": [], "unpaid_dues": [], "phone_number": "N/A"}
        
        for k in ["room_id", "move_in_date", "due_date", "phone_number"]: 
            if k not in self.data: self.data[k] = "N/A"
        for k in ["payment_history", "unpaid_dues"]:
            if k not in self.data: self.data[k] = []

        if self.data["room_id"] != "N/A":
            reqs = await self.page.data.custom_query("SELECT * FROM requests WHERE room_id=%s AND user_id=%s", (self.data["room_id"], self.id))
            # FIXED: Changed key 'date' to 'date_created'
            self.data["requests_data"] = [{
                "id": r[0], 
                "issue": json.loads(r[2]), 
                "status": r[3], 
                "urgency": r[4], 
                "date_created": r[6] 
            } for r in reqs]
            
            room = await self.page.data.custom_query("SELECT residents, monthly_rent, bed_count, current_status, thumbnail FROM rooms WHERE id=%s", (self.data["room_id"],))
            if room:
                self.data.update({"monthly_rent": room[0][1], "bed_count": room[0][2], "room_status": room[0][3], "thumbnail": room[0][4]})
                try:
                    all_users = await self.page.data.get_all_users()
                    self.data["roommates"] = [u[1] for u in all_users if u[0] != self.id and json.loads(u[4]).get("room_id") == self.data["room_id"]]
                except: self.data["roommates"] = []
        else:
            self.data.update({"requests_data": [], "monthly_rent": 0, "thumbnail": "placeholder.jpg", "roommates": []})

    async def show(self):
        self.navbar = NavBar(isAdmin=False, current_page=self, buttons=[
            
            NavBarButton(ft.Icons.BED, "My Room", lambda e: self.page.run_task(self.show_section, MyRoom(self)), True),
            NavBarButton(ft.Icons.CREDIT_CARD_ROUNDED, "Payments", lambda e: self.page.run_task(self.show_section, Payment(self))),
            NavBarButton(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, "Requests", lambda e: self.page.run_task(self.show_section, Requests(self))),
            NavBarButton(ft.Icons.CAMPAIGN_OUTLINED, "Announcements", lambda e: self.page.run_task(self.show_section, ResidentAnnouncements(self))),
        ])
        self.view = ft.View("/active-resident", [ft.Row([self.navbar], spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH, expand=True)], bgcolor="#FFFBEB", padding=ft.padding.only(top=-4))
        return self.view

    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)
        await self.update_data(); self.view.update()
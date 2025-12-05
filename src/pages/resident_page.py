import flet as ft
import json
from datetime import datetime

from pages.sections.my_room import MyRoom
from pages.sections.payment import Payment
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class ResidentPage:
    def __init__(self, page: ft.Page, user_id):
        self.page = page
        self.id = user_id
        self.username = None
        self.email = None
        self.password = None
        self.user_data = None
        self.view = None
        self.data = None
        self.navbar = None


    async def load_async(self):
        res = await self.page.data.get_user_by_id(self.id)
        self.username = res[0][1]        
        self.email = res[0][2]        
        self.password = res[0][3]
        self.data = json.loads(res[0][4])

        res = await self.page.data.custom_query("SELECT residents, monthly_rent, bed_count FROM rooms WHERE id = %s", (int(self.data["room_id"]),))
        
        self.data.update({"monthly_rent": res[0][1]})
        self.data.update({"bed_count": res[0][2]})

        roommates = []
        roommate_data = []
        for roommate_id in json.loads(res[0][0]):
            if roommate_id != self.id:
                user_info = await self.page.data.custom_query("SELECT username, data FROM users WHERE id = %s", (roommate_id,))
                roommates.append(user_info[0][0])
                roommate_data.append(json.loads(user_info[0][1]))

        self.data.update({"roommates": roommates})
        self.data.update({"roommate_data": roommate_data})

        self.navbar = NavBar(
            isAdmin=False, 
            current_page=self,
            buttons=[
                NavBarButton(ft.Icons.BED, "My Room", lambda e: self.page.run_task(self.show_section, MyRoom(self)), True),
                NavBarButton(ft.Icons.CREDIT_CARD_ROUNDED, "Payments", lambda e: self.page.run_task(self.show_section, Payment(self))),
                NavBarButton(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, "Requests", lambda e: self.page.run_task(self.show_section, ft.Container()))
            ]
        )
        
        self.view = ft.View(
            "/page-resident",
            [
                ft.Row([self.navbar], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
            ],
            bgcolor="#FFFBEB",
            padding=ft.padding.only(top=-4)
        )


    async def update_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        self.username = res[0][1]        
        self.email = res[0][2]        
        self.password = res[0][3]
        self.data = json.loads(res[0][4])

        res = await self.page.data.custom_query("SELECT residents, monthly_rent, bed_count FROM rooms WHERE id = %s", (int(self.data["room_id"]),))
        
        self.data.update({"monthly_rent": res[0][1]})
        self.data.update({"bed_count": res[0][2]})

        roommates = []
        roommate_data = []
        for roommate_id in json.loads(res[0][0]):
            if roommate_id != self.id:
                user_info = await self.page.data.custom_query("SELECT username, data FROM users WHERE id = %s", (roommate_id,))
                roommates.append(user_info[0][0])
                roommate_data.append(json.loads(user_info[0][1]))

        self.data.update({"roommates": roommates})
        self.data.update({"roommate_data": roommate_data})



    async def show(self):
        self.page.views.append(self.view)
        self.page.update()

    
    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)
        await self.update_data()
        self.view.update()
    

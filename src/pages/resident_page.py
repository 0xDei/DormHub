import flet as ft
import json

from pages.sections.my_room import MyRoom
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

        self.navbar = NavBar(
            isAdmin=False, 
            resident_page=self,
            buttons=[
                NavBarButton(ft.Icons.BED, "My Room", lambda e: self.page.run_task(self.show_section, MyRoom(self))),
                NavBarButton(ft.Icons.CREDIT_CARD_ROUNDED, "Payments", lambda e: self.page.run_task(self.show_section, ft.Text("Test"))),
                NavBarButton(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, "Requests", lambda e: self.page.run_task(self.show_section, ft.Container()))
            ]
        )

        self.view = ft.View(
            "/page-resident",
            [
                ft.Row([self.navbar], spacing=0)
            ],
            bgcolor="#FFFBEB",
            padding=0,
        )


    async def update_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        self.data = json.loads(res[0][4])


    async def show(self):
        self.page.views.append(self.view)
        self.page.update()

    
    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)

        self.view.update()
    

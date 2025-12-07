import flet as ft
import json
from datetime import datetime

from pages.sections.overview import Overview
from pages.sections.rooms import Rooms
from pages.sections.residents import Residents
from pages.sections.admin_payment import AdminPayment
from pages.sections.maintenance import Maintenance
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class AdminPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = None
        self.data = {}
        self.navbar = None
        self.current_section = None


    async def update_data(self):
       self.data.update({"residents": await self.page.data.get_all_users()})
       self.data.update({"rooms": await self.page.data.get_all_rooms()})
       self.data.update({"requests": await self.page.data.get_all_requests()})

    async def show(self):
        self.navbar = NavBar(
            isAdmin=True, 
            current_page=self,
            buttons=[
                NavBarButton(ft.Icons.INSERT_CHART_OUTLINED_ROUNDED, "Overview", lambda e: self.page.run_task(self.show_section, Overview(self)), True, "#FFEDD4", "#F66B2C"),
                NavBarButton(ft.Icons.HOME_ROUNDED, "Rooms", lambda e: self.page.run_task(self.show_section, Rooms(self)), False, "#FFEDD4", "#F66B2C"),
                NavBarButton(ft.Icons.PEOPLE_OUTLINE_ROUNDED, "Residents", lambda e: self.page.run_task(self.show_section, Residents(self)), False, "#FFEDD4", "#F66B2C"),
                NavBarButton(ft.Icons.PAYMENTS_OUTLINED, "Payments", lambda e: self.page.run_task(self.show_section, AdminPayment(self)), False, "#FFEDD4", "#F66B2C"),
                NavBarButton(ft.Icons.BUILD_CIRCLE_OUTLINED, "Maintenance", lambda e: self.page.run_task(self.show_section, Maintenance(self)), False, "#FFEDD4", "#F66B2C")
            ]
        )
        
        self.view = ft.View(
            "/active-admin",
            [
                ft.Row(
                    [self.navbar], 
                    spacing=0, 
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH, # Stretch sidebar to bottom
                    expand=True
                )
            ],
            bgcolor="#FFFBEB",
            padding=ft.padding.only(top=-4)
        )
        return self.view

    
    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)
        await self.update_data()
        self.view.update()
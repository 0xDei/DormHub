import flet as ft
import json
from datetime import datetime

from pages.sections.section import Section
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class AdminPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = None
        self.data = None
        self.navbar = None


    async def load_async(self):
        self.navbar = NavBar(
            isAdmin=True, 
            current_page=self,
            buttons=[
                NavBarButton(ft.Icons.INSERT_CHART_OUTLINED_ROUNDED, "Overview", lambda e: self.page.run_task(self.show_section, Section()), True),
                NavBarButton(ft.Icons.HOME_ROUNDED, "Rooms", lambda e: self.page.run_task(self.show_section, Section())),
                NavBarButton(ft.Icons.PEOPLE_OUTLINE_ROUNDED, "Residents", lambda e: self.page.run_task(self.show_section, Section()))
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
        print("update")


    async def show(self):
        return self.view

    
    async def show_section(self, section):
        if len(self.view.controls[0].controls) > 1: self.view.controls[0].controls[1] = section
        else: self.view.controls[0].controls.append(section)
        await self.update_data()
        self.view.update()
    

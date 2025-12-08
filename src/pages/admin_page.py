import flet as ft
from pages.sections.overview import Overview
from pages.sections.rooms import Rooms
from pages.sections.residents import Residents
from pages.sections.admin_payment import AdminPayment
from pages.sections.maintenance import Maintenance
from pages.sections.admin_announcements import AdminAnnouncements
# Removed: from pages.sections.settings import Settings 
from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class AdminPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.view = None
        self.data = {}
        self.navbar = None
        self.username = "Administrator"
        self.email = "admin@dormhub.com" 

    async def update_data(self):
       self.data.update({"residents": await self.page.data.get_all_users()})
       self.data.update({"rooms": await self.page.data.get_all_rooms()})
       self.data.update({"requests": await self.page.data.get_all_requests()})

    async def show(self):
        self.navbar = NavBar(
            isAdmin=True, current_page=self,
            buttons=[
                NavBarButton(ft.Icons.INSERT_CHART_OUTLINED_ROUNDED, "Overview", lambda e: self.change_tab(Overview(self), "Overview"), True),
                NavBarButton(ft.Icons.HOME_ROUNDED, "Rooms", lambda e: self.change_tab(Rooms(self), "Rooms")),
                NavBarButton(ft.Icons.PEOPLE_OUTLINE_ROUNDED, "Residents", lambda e: self.change_tab(Residents(self), "Residents")),
                NavBarButton(ft.Icons.PAYMENTS_OUTLINED, "Payments", lambda e: self.change_tab(AdminPayment(self), "Payments")),
                NavBarButton(ft.Icons.BUILD_CIRCLE_OUTLINED, "Maintenance", lambda e: self.change_tab(Maintenance(self), "Maintenance")),
                NavBarButton(ft.Icons.CAMPAIGN_OUTLINED, "Announcements", lambda e: self.change_tab(AdminAnnouncements(self), "Announcements")),
            ]
        )
        
        # --- FIX: Set Overview as the initial section ---
        initial_section = Overview(self)
        
        self.view = ft.View(
            "/active-admin", 
            [
                ft.Row(
                    [self.navbar, initial_section], # Add the initial section here
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
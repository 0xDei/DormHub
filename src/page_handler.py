import flet as ft

from pages.login_page import LoginPage
from pages.resident_page import ResidentPage
from utils.element_factory import *


class PageHandler:
    def __init__(self, page: ft.Page):
        self.page = page

        self.login_page = None
        self.active_portal = None

    async def set_root_page(self):
        admin_card = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Image(src="../assets/admin.png", color="#FF6900"), border_radius=50, padding=12, bgcolor="#FFEDD4"),
                    ft.Text("Admin Dashboard", weight=ft.FontWeight.BOLD, size=16, color="#FF6900"),
                    ft.Text("Manage rooms, residents bookings, maintenance, and finances", size=12, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ft.FilledButton("Continue as Admin", width=320, height=30, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/login-admin"))
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            width=340,
            height=210,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=[
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                )
            ]
        )

        resident_card = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Image(src="../assets/resident.png", color="#FE9A00"), border_radius=50, padding=12, bgcolor="#FEF3C6"),
                    ft.Text("Resident Dashboard", weight=ft.FontWeight.BOLD, size=16, color="#FE9A00"),
                    ft.Text("View your room, pay rent, submit requests, and connect with housemates", size=12, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ft.FilledButton("Continue as Resident", width=320, height=30, bgcolor="#FE9A00", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/login-resident"))
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            width=340,
            height=210,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=[
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                )
            ]
        )

        cards_row = ft.Row(
            [
                admin_card,
                resident_card
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )

        self.page.views.append(
            ft.View(
                "/",
                [
                    ft.Container(get_icon(), margin=ft.margin.only(top=100)),
                    cards_row
                ],
                spacing=40,
                bgcolor="#FFFBEB",
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

        if self.page.data.connected == False: await self.page.data.connect(self.page)


    async def show_login_page(self, login_type=1):
        if self.page.data.connected == False: return print("Not connected!")

        if self.login_page == None: self.login_page = LoginPage(self.page, login_type)
        elif login_type != self.login_page.get_type():  self.login_page.change_type(login_type)
        
        await self.login_page.show()

    
    async def show_resident_page(self):
        if self.page.data.connected == False: return print("Not connected!")

        active_user = self.page.data.get_active_user()
        if active_user == None:
            create_banner(self.page, ft.Colors.RED_100, ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, color=ft.Colors.RED), "Error: No user logged in! Going back to root page.", ft.Colors.RED)
            self.page.go("/")
            return

        self.active_portal = ResidentPage(self.page, self.page.data.get_active_user())
        await self.active_portal.load_data()
        await self.active_portal.show()


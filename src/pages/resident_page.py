import flet as ft
import json

from element_factory import *

class ResidentPage:
    def __init__(self, page: ft.Page, user_id):
        self.page = page
        self.id = user_id
        self.username = None
        self.email = None
        self.password = None
        self.user_data = None

        # json.dumps(string) to encode

    async def load_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        self.username = res[0][1]        
        self.email = res[0][2]        
        self.password = res[0][3]
        self.user_data = json.loads(res[0][4]) if res[0][4] != 'none' else {}

    async def show(self):
        account_button = ft.Container(
            ft.Row(
                [
                    ft.Container(
                        ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE),
                        padding=4,
                        border_radius=50,
                        bgcolor="#FF6900"
                    ),
                    ft.Column([ft.Text(self.username, size=14, weight=ft.FontWeight.W_400), ft.Text("Room 09", size=10, weight=ft.FontWeight.W_100)], spacing=0)
                ],
            ),
            bgcolor="#FEFBE8",
            padding=ft.padding.only(top=7, left=10, right=10, bottom=7),
            border_radius=10,
            margin=ft.margin.only(top=10)
        )
        
        buttons = ft.Container(
            ft.Column(
                [
                    create_navbar_button(self.page, ft.Icons.BED, "My Room", lambda e: print("clicked"))
                ]
            )
        )

        navbar = ft.Container(
            ft.Column(
                [
                    get_navbar_icon(1),
                    account_button,
                    ft.Container(ft.Divider(2), margin=ft.margin.only(top=10, bottom=20)),
                    buttons
                ]
            ),
            width=200,
            height=720,
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.only(top=15, left=10, right=10, bottom=15)
        )

        self.page.views.append(
            ft.View(
                "/page-resident",
                [
                    navbar
                ],
                bgcolor="#FFFBEB",
                padding=5
            )
        )

        self.page.update()
    

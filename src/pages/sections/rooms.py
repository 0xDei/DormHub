import flet as ft
from datetime import datetime

from pages.sections.section import Section
from utils.element_factory import create_info_card

class Rooms(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page

        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Room Management", color="#FF6900", size=16, weight=ft.FontWeight.W_500),
                        ft.Text("Manage beds and room availability", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
                ft.Container(
                    ft.FilledButton(
                        "Add Room", 
                        icon=ft.Icons.ADD, 
                        icon_color=ft.Colors.WHITE, 
                        bgcolor="#FF6900", 
                        color=ft.Colors.WHITE, 
                        elevation=0, 
                        width=120, 
                        height=30, 
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, padding=10),
                        on_click=self.show_add_room
                    )
                )
            ]
        )

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            
                        ],
                        spacing=20,
                        padding=ft.padding.only(bottom=20),
                        expand=True
                    )
                ],
                spacing=15,
                expand=True
            ),
            expand=True
        )

    async def show_add_room(self, e):
        print("adding room")
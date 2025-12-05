import flet as ft

from pages.sections.section import Section
from utils.element_factory import create_info_card

class MyRoom(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page
        
        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Welcome Home,", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                        ft.Text(self.resident_page.username + "!", color="#FF6900", size=16, weight=ft.FontWeight.BOLD)
                    ],
                    spacing=3.5
                ),
                ft.Text("Room " + self.resident_page.data["room_id"], size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1
        )

        top_info = ft.Row(
            [
                create_info_card(
                    "Next Payment Due", 
                    [
                        ft.Text("Dec 1, 2025"),
                        ft.Text("₱ 3,000/month", size=8)
                    ],
                    ft.Icon(ft.Icons.ATTACH_MONEY, color="#E79031"),
                    "right",
                    "#FEF3C6",
                    250,
                    100
                )
            ]
        )
        room_info = ft.Container()
        room_mate = ft.Container()
        reminders = ft.Container()

        self.content = ft.Column(
            [
                header,
                top_info,
                room_info,
                room_mate,
                reminders
            ]
        )
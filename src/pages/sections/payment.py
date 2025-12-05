import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section

class Payment(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page

        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Payment Center", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.CREDIT_CARD_ROUNDED, size=24, color="#3BA9E6")
                    ],
                    spacing=3.5
                ),
                ft.Text("Manage your rent payments and view history", size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1
        )

        unpaid_count = len(self.resident_page.data["unpaid_dues"])
        if unpaid_count == 0: time = int(self.resident_page.data["due_date"])
        else: time = int(self.resident_page.data["unpaid_dues"][0])
    
        current_time = int(datetime.now().timestamp())
        if (current_time + 2629743) < time: time = int(self.resident_page["payment_history"][0])
        
        date = datetime.fromtimestamp(time)
        due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
        
        card_title = ft.Text("Upcoming Payment", size=14, color="#feae33", weight=ft.FontWeight.BOLD)
        bgcolor = "#fff5e6"
        border_color = "#fec266"
        due_info = [
            ft.Text(f"₱ {self.resident_page.data['monthly_rent']:,}", size=18, weight=ft.FontWeight.W_700),
            ft.Text(due_date, size=12, color=ft.Colors.GREY_600)
        ]

        if True:
            card_title = ft.Text("Unpaid Due!", size=14, color="#ff3333", weight=ft.FontWeight.BOLD)
            status_icon = ft.Icon(ft.Icons.ERROR_ROUNDED, size=32, color="#ff3333")
            satus_bgcolor = "#150ffe6e6"
            bgcolor = "#150ffe6e6"
            border_color = "#ff6666"
        elif (current_time + 2629743) < time:
            card_title = ft.Text("You're all paid!", size=24, color="#038f00", weight=ft.FontWeight.BOLD)
            status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=32, color="#038f00")
            satus_bgcolor = "#150e6f7e6"
            bgcolor = "#150e6f7e6"
            border_color = "#8068d166"
            due_info = [ft.Container()]
        else:
            status_icon = ft.Icon(ft.Icons.ACCESS_TIME_FILLED_ROUNDED, size=32, color="#feae33")
            satus_bgcolor = "#fff5e6"

        next_due_card = ft.Container(
            ft.Row(
                [
                    ft.Column(
                        [
                            card_title,
                            *due_info
                        ],
                        expand=True,
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        status_icon,
                        bgcolor=satus_bgcolor,
                        border=ft.border.all(1.8, border_color),
                        border_radius=7, 
                        width=32 * 1.5,
                        height=32 * 1.5
                    )
                ]
            ),
            padding=ft.padding.only(left=20, right=20, top=18, bottom=20),
            height=110,
            bgcolor=bgcolor,
            border_radius=10,
            border=ft.border.all(2, border_color),
            expand=True
        )

        info_cards = ft.Container(

        )

        history = ft.Container(

        )

        unpaid = ft.Container(

        )

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            next_due_card,
                            info_cards,
                            history,
                            unpaid                     
                        ],
                        spacing=30,
                        padding=ft.padding.only(bottom=20),
                        expand=True
                    )
                ],
                spacing=15,
                expand=True
            ),
            expand=True
        )

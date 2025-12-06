import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

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
        else: time = int(self.resident_page.data["unpaid_dues"][0]["date"])
        
        date = datetime.fromtimestamp(time)
        due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
        
        card_title = ft.Text("Upcoming Payment", size=14, color="#feae33", weight=ft.FontWeight.BOLD)
        bgcolor = "#fff5e6"
        border_color = "#fec266"
        due_info = [
            ft.Text(f"₱ {self.resident_page.data['monthly_rent']:,}", size=18, weight=ft.FontWeight.W_700),
            ft.Text(due_date, size=12, color=ft.Colors.GREY_600)
        ]

        current_time = int(datetime.now().timestamp())

        if unpaid_count >= 1:
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

        next_due_date = datetime.fromtimestamp(int(self.resident_page.data["due_date"]))
        next_due_date_formatted = f"{next_due_date.strftime('%b')} {next_due_date.day}, {next_due_date.year}"
        info_cards = ft.Row(
            [
                create_info_card(
                    "Unpaid Payments", 
                    [
                        ft.Row([
                            ft.Text(str(unpaid_count), text_align=ft.TextAlign.CENTER, size=16),
                            ft.Text(f"x {self.resident_page.data['monthly_rent']:,}", size=12, color=ft.Colors.GREY_400)
                        ], spacing=3.5)
                    ],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#ff3333", size=28),
                    "left",
                    "#ffe6e6",
                    250,
                    90
                ),
                create_info_card(
                    "Next Due Date", 
                    [
                        ft.Text(next_due_date_formatted, text_align=ft.TextAlign.CENTER, size=16)
                    ],
                    ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color="#4D84FC", size=28),
                    "left",
                    "#DBEAFE",
                    250,
                    90
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            expand=True
        )

        ph_contents = []
        for ph_info in self.resident_page.data["payment_history"][::-1]:
            if ph_info["remark"] == "late":
                leading_icon = ft.Container(
                    ft.Icon(ft.Icons.TIMER_OUTLINED, color="#DB805C", size=24),
                    bgcolor="#FFEDD4",
                    border_radius=7, 
                    width=24 * 1.5,
                    height=24 * 1.5
                )
                remark = create_remark("late", color="#DB805C", bgcolor="#FFEDD4")
            else:
                leading_icon = ft.Container(
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="#00cc0a", size=24),
                    bgcolor="#b3ffb6",
                    border_radius=7, 
                    width=24 * 1.5,
                    height=24 * 1.5
                )
                remark = create_remark("on time", color="#00cc0a", bgcolor="#b3ffb6")

            date = datetime.fromtimestamp(ph_info["date"])
            ph_contents.append(
                ft.Container(
                    ft.Row(
                        [
                            ft.Container(leading_icon),
                            ft.Column(
                                [
                                    ft.Text(f"{date.strftime('%b')} {date.year}", size=14, weight=ft.FontWeight.W_500),
                                    ft.Text(date.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500)
                                ], spacing=0, expand=True
                            ),
                            remark,
                            ft.Text(f"₱ {ph_info['amount']:,}", size=12, weight=ft.FontWeight.W_900)
                        ]
                    ),
                    padding=10,
                    border=ft.border.all(1.5, "#FEF3C6"),
                    border_radius=10
                )
            )

        if len(ph_contents) == 0: ph_contents.append(ft.Container(ft.Text("You have no payment history", color=ft.Colors.GREY_300), expand=True, alignment=ft.alignment.center, margin=ft.margin.only(top=50)))

        history = ft.Container(
            ft.Column(
                [
                    ft.Text("Payment History", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                    ft.ListView(ph_contents, expand=True, spacing=7)
                ],
                spacing=15
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            height=350,
            padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
            border=ft.border.all(2, "#FEF3C6")
        )

        up_contents = []
        for up_info in self.resident_page.data["unpaid_dues"][::-1]:
            leading_icon = ft.Container(
                ft.Icon(ft.Icons.MONEY_OFF_CSRED_ROUNDED, color="#b32424", size=24),
                bgcolor="#ffc2c2",
                border_radius=7, 
                width=24 * 1.5,
                height=24 * 1.5
            )

            date = datetime.fromtimestamp(up_info["date"])
            up_contents.append(
                ft.Container(
                    ft.Row(
                        [
                            ft.Container(leading_icon),
                            ft.Column(
                                [
                                    ft.Text(f"{date.strftime('%b')} {date.year}", size=14, weight=ft.FontWeight.W_500),
                                    ft.Text(date.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500)
                                ], spacing=0, expand=True
                            ),
                            ft.Text(f"₱ {up_info['amount']:,}", size=12, weight=ft.FontWeight.W_900)
                        ]
                    ),
                    padding=10,
                    border=ft.border.all(1.5, "#40cc2929"),
                    border_radius=10
                )
            )

        if len(up_contents) == 0: up_contents.append(ft.Container(ft.Text("You have no unpaid payments", color=ft.Colors.GREY_300), expand=True, alignment=ft.alignment.center, margin=ft.margin.only(top=50)))

        unpaid = ft.Container(
            ft.Column(
                [
                    ft.Text("Unpaid Payments", color="#cc2929", size=14, weight=ft.FontWeight.W_500),
                    ft.ListView(up_contents, expand=True, spacing=7)
                ],
                spacing=15
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            height=350,
            padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
            border=ft.border.all(2, "#FEF3C6")
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

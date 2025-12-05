import flet as ft
from datetime import datetime

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
                ft.Text("Room " + str(self.resident_page.data["room_id"]), size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1
        )

        date = datetime.fromtimestamp(int(self.resident_page.data["due_date"]))
        due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
        
        top_info = ft.Row(
            [
                create_info_card(
                    "Next Payment Due", 
                    [
                        ft.Text(due_date, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"₱ {self.resident_page.data['monthly_rent']:,}", size=10)
                    ],
                    ft.Icon(ft.Icons.ATTACH_MONEY, color="#E79031", size=28),
                    "right",
                    "#FEF3C6",
                    250,
                    90
                ),
                create_info_card(
                    "Active Requests", 
                    [
                        ft.Text(str(len(self.resident_page.data["requests"])), size=24, text_align=ft.TextAlign.CENTER),
                    ],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#F98851", size=28),
                    "right",
                    "#FFECD3",
                    250,
                    90
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            expand=True
        )

        roommates = self.resident_page.data["roommates"]
        if len(roommates) == 0: roommates_text = ft.Text("None")
        elif len(roommates) > 1:  roommates_text = ft.Text(f"{roommates[0]}\n +{len(roommates) - 1} more")
        else: roommates_text = ft.Text(roommates[0])

        date = datetime.fromtimestamp(self.resident_page.data["move_in_date"])
        move_in_date = f"{date.strftime('%b')} {date.day}, {date.year}"

        room_info = ft.Container(
            ft.Column(
                [
                    ft.Text("Your Room", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                    ft.ListView([ft.Image(src="../assets/placeholder.jpg", expand=True, height=300, fit=ft.ImageFit.FILL, border_radius=10)], height=300, expand=True),
                    ft.Divider(2, color="#FEF3C6"),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Bed Count", size=12, color=ft.Colors.GREY_600),
                                    ft.Row([ft.Icon(ft.Icons.BED_OUTLINED, color="#E78B28", size=16), ft.Text(str(self.resident_page.data["bed_count"]))], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                [
                                    ft.Text("Monthly Rent", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(f"₱ {self.resident_page.data["monthly_rent"]:,}")
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                [
                                    ft.Text("Roommates", size=12, color=ft.Colors.GREY_600),
                                    roommates_text
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                [
                                    ft.Text("Move-in Date", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(move_in_date)
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER, 
                        spacing=50
                    ),
                ]
            ),
            bgcolor=ft.Colors.WHITE,
            height=430,
            border_radius=15,
            padding=ft.padding.only(left=20, top=17, right=20, bottom=20)
        )

        roommate_cards = []
        for i, roommate in enumerate(self.resident_page.data["roommates"]):
            card = ft.Container(
                ft.Row(
                    [
                        ft.Container(
                            ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE, size=32),
                            padding=10,
                            border_radius=50,
                            bgcolor="#FF6900"
                        ),
                        ft.Column([ft.Text(roommate, size=16, weight=ft.FontWeight.BOLD), ft.Text(self.resident_page.data["roommate_data"][i]["phone_number"])], spacing=0)
                    ]
                ),
                padding=ft.padding.only(top=7, left=10, right=10, bottom=7),
                border_radius=10,
                margin=ft.margin.only(top=10),
                expand=True
            )

            roommate_cards.append(card)

        if len(roommate_cards) == 0: roommate_cards.append(ft.Container(ft.Text("You have no roommates")))

        room_mate = ft.Container(
            ft.Column(
                [
                    ft.Text("Your Roommates", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                    ft.ListView(roommate_cards, expand=True)
                ]
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
            border=ft.border.all(2, "#FEF3C6")
        )

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            ft.Container(top_info, margin=ft.margin.only(bottom=-10)),
                            room_info,
                            room_mate
                        ],
                        spacing=30,
                        padding=ft.padding.only(bottom=20),
                        expand=True
                    )
                ],
                expand=True
            ),
            expand=True
        )
import flet as ft
from datetime import datetime

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Requests(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page

        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Maintenance Requests", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.EDIT_DOCUMENT, size=24, color=ft.Colors.GREY_500)
                    ],
                    spacing=3.5
                ),
                ft.Text("Submit and track your maintenance requests", size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1
        )

        pending_requests = []
        in_progress_requests = []
        completed_requests = []

        requests_list_contents = []
        for request_info in self.resident_page.data["requests_data"]:
            match request_info["status"]:
                case "in-progress": 
                    in_progress_requests.append(request_info)
                    icon = ft.Icons.ACCESS_TIME_ROUNDED
                    color = "#4D84FC"
                    bgcolor = "#DBEAFE"
                case "pending": 
                    pending_requests.append(request_info)
                    icon = ft.Icons.ERROR_OUTLINE_ROUNDED
                    color = "#C28239"
                    bgcolor = "#FEF9C3"
                case "completed": 
                    completed_requests.append(request_info)
                    icon = ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
                    color = "#00cc0a"
                    bgcolor = "#b3ffb6"
            
            match request_info["urgency"]:
                case "low":
                    ur_color = "#808899"
                    ur_bgcolor = "#F3F4F6"
                case "medium":
                    ur_color = "#E18526"
                    ur_bgcolor = "#FFEDD4"
                case "high":
                    ur_color = "#D66875"
                    ur_bgcolor = "#FFE2E2"

            leading_icon = ft.Container(
                ft.Icon(icon, color=color, size=24),
                bgcolor=bgcolor,
                border_radius=7, 
                width=24 * 1.5,
                height=24 * 1.5
            )
            urgency = create_remark(request_info["urgency"], ur_color, ur_bgcolor)
            status = create_remark(request_info["status"], color, bgcolor)

            date_created = datetime.fromtimestamp(int(request_info["date_created"]))
            date_updated = datetime.fromtimestamp(int(request_info["date_updated"]))
            
            requests_list_contents.append(
                ft.Container(
                    ft.Row(
                        [
                            ft.Container(leading_icon),
                            ft.Column(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(request_info["issue"]["title"], size=14, weight=ft.FontWeight.W_500),
                                            ft.Text(request_info["issue"]["desc"], size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_400),
                                        ],
                                        spacing=-2
                                    ),
                                    ft.Row(
                                        [
                                            ft.Row([ft.Text("Created:", size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_400), ft.Text(date_created.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_300)], spacing=5),
                                            ft.Row([ft.Text("Updated:", size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_400), ft.Text(date_updated.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_300)], spacing=5)
                                        ],
                                        spacing=10
                                    )
                                    
                                ], spacing=10, expand=True
                            ),
                            ft.Container(
                                ft.Row(
                                    [
                                        urgency,
                                        status
                                    ]
                                ),
                                padding=ft.padding.only(top=-40)
                            )
                        ],
                    ),
                    padding=10,
                    border=ft.border.all(1.5, "#FEF3C6"),
                    border_radius=10
                )
            )

        info_cards = ft.Row(
            [
                create_info_card(
                    "Pending", 
                    [
                        ft.Text(f"{len(pending_requests)} requests", text_align=ft.TextAlign.CENTER, size=16)
                    ],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#C28239", size=28),
                    "left",
                    "#FEF9C3",
                    200,
                    87
                ),
                create_info_card(
                    "In Progress", 
                    [
                        ft.Text(f"{len(in_progress_requests)} requests", text_align=ft.TextAlign.CENTER, size=16)
                    ],
                    ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, color="#4D84FC", size=28),
                    "left",
                    "#DBEAFE",
                    200,
                    87
                ),
                create_info_card(
                    "Completed", 
                    [
                        ft.Text(f"{len(completed_requests)} requests", text_align=ft.TextAlign.CENTER, size=16)
                    ],
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="#00cc0a", size=28),
                    "left",
                    "#b3ffb6",
                    200,
                    87
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        requests_list = ft.Container(
            ft.Column(
                [
                    ft.Text("Your Requests", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                    ft.ListView(requests_list_contents, expand=True, spacing=7)
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
                            info_cards,
                            requests_list
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
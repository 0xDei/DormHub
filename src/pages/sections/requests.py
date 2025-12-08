import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Requests(Section):
    def __init__(self, resident_page):
        super().__init__()
        self.resident_page = resident_page
        
        # Header
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Maintenance Requests", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                                ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=24, color="#3BA9E6")
                            ],
                            spacing=3.5,
                        ),
                        ft.Text("Submit and track maintenance issues", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
                ft.Container(
                    ft.FilledButton(
                        "New Request",
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.WHITE,
                        bgcolor="#FE9A00",
                        color=ft.Colors.WHITE,
                        elevation=0,
                        width=150,
                        height=35,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=7),
                            text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)
                        ),
                        on_click=self.show_add_request
                    )
                )
            ]
        )

        # Stats Logic
        pending_count = 0
        inprogress_count = 0
        completed_count = 0
        
        requests_data = self.resident_page.data.get("requests_data", [])
        
        for req in requests_data:
            if req["status"] == "pending": pending_count += 1
            elif req["status"] == "in-progress": inprogress_count += 1
            elif req["status"] == "completed": completed_count += 1

        # Responsive Stats Cards
        col_setting = {"xs": 12, "sm": 4}
        stats = ft.ResponsiveRow(
            [
                create_info_card("Pending", [ft.Text(str(pending_count), size=20, weight="bold")], ft.Icon(ft.Icons.ERROR_OUTLINE, color="orange"), "left", "#FEF9C3", 0, 90, col=col_setting),
                create_info_card("In Progress", [ft.Text(str(inprogress_count), size=20, weight="bold")], ft.Icon(ft.Icons.ACCESS_TIME, color="blue"), "left", "#DBEAFE", 0, 90, col=col_setting),
                create_info_card("Completed", [ft.Text(str(completed_count), size=20, weight="bold")], ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="green"), "left", "#b3ffb6", 0, 90, col=col_setting),
            ],
            spacing=10, run_spacing=10
        )

        # Request List
        self.request_list = ft.ListView(spacing=10, expand=True)

        if not requests_data:
            self.request_list.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.ASSIGNMENT_LATE_OUTLINED, size=48, color=ft.Colors.GREY_300),
                        ft.Text("No requests found", color=ft.Colors.GREY_400)
                    ], horizontal_alignment="center"),
                    alignment=ft.alignment.center,
                    expand=True,
                    margin=ft.margin.only(top=50)
                )
            )
        else:
            # Sort by newest first
            requests_data.sort(key=lambda x: int(x.get("date_created", 0)), reverse=True)
            
            for req in requests_data:
                # Color coding
                status_color = "orange"
                if req["status"] == "in-progress": status_color = "blue"
                elif req["status"] == "completed": status_color = "green"
                
                urgency_color = "grey"
                if req["urgency"] == "medium": urgency_color = "orange"
                elif req["urgency"] == "high": urgency_color = "red"

                # Date formatting
                try:
                    dt = datetime.fromtimestamp(int(req["date_created"]))
                    date_str = dt.strftime("%b %d, %Y")
                except:
                    date_str = "N/A"

                card = ft.Container(
                    ft.Row([
                        ft.Container(
                            ft.Icon(ft.Icons.BUILD, color="white", size=20),
                            bgcolor=status_color,
                            border_radius=8,
                            padding=8
                        ),
                        ft.Column([
                            ft.Text(req["issue"].get("title", "Issue"), weight="bold", size=14),
                            ft.Text(req["issue"].get("desc", ""), size=12, color="grey", overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=2, expand=True),
                        ft.Column([
                            create_remark(req["urgency"].upper(), urgency_color, "#f0f0f0"),
                            ft.Text(date_str, size=10, color="grey")
                        ], horizontal_alignment="end", spacing=2)
                    ], alignment="spaceBetween"),
                    bgcolor="white",
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(1, "#eee")
                )
                self.request_list.controls.append(card)

        self.content = ft.Container(
            ft.Column([
                header,
                stats,
                ft.Container(
                    ft.Column([
                        ft.Text("My History", color="#E78B28", weight="bold"),
                        self.request_list
                    ]),
                    bgcolor="white",
                    padding=15,
                    border_radius=10,
                    expand=True,
                    border=ft.border.all(2, "#FEF3C6")
                )
            ], spacing=15),
            padding=10,
            expand=True
        )

    async def show_add_request(self, e):
        title = ft.TextField(label="Title", hint_text="e.g. Leaky Faucet")
        desc = ft.TextField(label="Description", multiline=True, min_lines=3)
        urgency = ft.Dropdown(
            label="Urgency",
            options=[
                ft.dropdown.Option("low"),
                ft.dropdown.Option("medium"),
                ft.dropdown.Option("high"),
            ],
            value="low"
        )

        async def submit(e):
            if not title.value: 
                title.error_text = "Required"; title.update(); return
            
            await self.resident_page.page.data.create_request(
                self.resident_page.data["room_id"],
                title.value,
                desc.value,
                urgency.value,
                self.resident_page.id
            )
            self.resident_page.page.close(dlg)
            self.resident_page.page.run_task(self.resident_page.show_section, Requests(self.resident_page))

        dlg = ft.AlertDialog(
            title=ft.Text("New Request"),
            content=ft.Container(
                ft.Column([title, desc, urgency], tight=True, spacing=15),
                width=400
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.resident_page.page.close(dlg)),
                ft.FilledButton("Submit", bgcolor="#FF6900", on_click=submit)
            ]
        )
        self.resident_page.page.open(dlg)
import flet as ft
import json
from datetime import datetime
import traceback

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark, create_banner

class Maintenance(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.page = admin_page.page
        self.all_requests = []

        # Header
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Maintenance Requests", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                                ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=24, color=ft.Colors.GREY_500)
                            ],
                            spacing=3.5,
                        ),
                        ft.Text("Track and update resident maintenance issues", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
            ]
        )

        # Status Filter
        self.status_filter = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "All Requests"),
                ft.dropdown.Option("pending", "Pending"),
                ft.dropdown.Option("in-progress", "In Progress"),
                ft.dropdown.Option("completed", "Completed"),
            ],
            value="all",
            border_radius=10,
            bgcolor="#F3F3F5",
            border_width=0,
            width=150,
            on_change=self.on_filter_change
        )

        # Stats placeholders
        self.total_pending = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
        self.total_inprogress = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
        self.total_completed = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)

        stats = ft.Row(
            [
                create_info_card(
                    "Pending",
                    [self.total_pending],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#C28239", size=28),
                    "left",
                    "#FEF9C3",
                    200,
                    87
                ),
                create_info_card(
                    "In Progress",
                    [self.total_inprogress],
                    ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, color="#4D84FC", size=28),
                    "left",
                    "#DBEAFE",
                    200,
                    87
                ),
                create_info_card(
                    "Completed",
                    [self.total_completed],
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

        # Requests list
        self.requests_list = ft.ListView(spacing=7, expand=True)

        list_container = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("All Requests", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                            self.status_filter
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.requests_list
                ],
                spacing=15,
                expand=True # Important: Ensure column fills the container
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            height=550,
            padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
            border=ft.border.all(2, "#FEF3C6")
        )

        self.content = ft.Container(
            ft.Column(
                [
                    header,
                    ft.ListView(
                        [stats, list_container],
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

        # Load data
        self.page.run_task(self.load_data)

    def on_filter_change(self, e):
        self.page.run_task(self.filter_requests)

    async def load_data(self):
        try:
            # Fetch all requests and users
            requests = await self.page.data.get_all_requests()
            users = await self.page.data.get_all_users()
            
            # Map user IDs to usernames
            user_map = {user[0]: user[1] for user in users}

            self.all_requests = []
            pending_count = 0
            inprogress_count = 0
            completed_count = 0

            if requests:
                for req in requests:
                    # req: (id, room_id, issue, current_status, urgency, user_id, date_created, date_updated)
                    try:
                        issue_str = req[2]
                        issue = json.loads(issue_str) if issue_str else {}
                        
                        status = req[3] or "pending"
                        urgency = req[4] or "low"
                        
                        if status == "pending": pending_count += 1
                        elif status == "in-progress": inprogress_count += 1
                        elif status == "completed": completed_count += 1

                        self.all_requests.append({
                            "id": req[0],
                            "room_id": req[1],
                            "title": issue.get("title", "No Title"),
                            "desc": issue.get("desc", "No Description"),
                            "status": status,
                            "urgency": urgency,
                            "username": user_map.get(req[5], "Unknown User"),
                            "date_created": req[6]
                        })
                    except Exception as e:
                        print(f"Error parsing request {req[0]}: {e}")
                        traceback.print_exc()

            # Update stats
            self.total_pending.value = str(pending_count)
            self.total_inprogress.value = str(inprogress_count)
            self.total_completed.value = str(completed_count)
            
            # Initial display
            await self.filter_requests()
            
        except Exception as e:
            print(f"Error loading maintenance data: {e}")
            traceback.print_exc()

    async def filter_requests(self):
        filter_val = self.status_filter.value
        filtered = []
        
        # Sort by date (newest first)
        try:
            sorted_requests = sorted(self.all_requests, key=lambda x: int(x["date_created"] or 0), reverse=True)
        except:
            sorted_requests = self.all_requests

        for r in sorted_requests:
            if filter_val != "all" and r["status"] != filter_val:
                continue
            filtered.append(r)

        self.display_requests(filtered)

    def display_requests(self, requests):
        self.requests_list.controls.clear()

        if not requests:
            self.requests_list.controls.append(
                ft.Container(
                    ft.Text("No requests found", color=ft.Colors.GREY_400),
                    alignment=ft.alignment.center,
                    expand=True,
                    margin=ft.margin.only(top=20)
                )
            )
        else:
            for r in requests:
                # Define styles based on urgency
                ur_color = "#808899"
                ur_bgcolor = "#F3F4F6"
                if r["urgency"] == "medium":
                    ur_color = "#E18526"
                    ur_bgcolor = "#FFEDD4"
                elif r["urgency"] == "high":
                    ur_color = "#D66875"
                    ur_bgcolor = "#FFE2E2"

                # Define styles based on status
                st_color = "#C28239"
                if r["status"] == "in-progress": st_color = "#4D84FC"
                elif r["status"] == "completed": st_color = "#00cc0a"

                # Date formatting
                try:
                    dt = datetime.fromtimestamp(int(r["date_created"]))
                    date_str = dt.strftime("%b %d, %Y")
                except:
                    date_str = "N/A"

                # Dropdown for status update
                status_dd = ft.Dropdown(
                    value=r["status"],
                    options=[
                        ft.dropdown.Option("pending", "Pending"),
                        ft.dropdown.Option("in-progress", "In Progress"),
                        ft.dropdown.Option("completed", "Completed"),
                    ],
                    text_size=12,
                    dense=True, # Used dense instead of height for compact look
                    width=130,
                    content_padding=10,
                    border_radius=8,
                    color=st_color,
                    border_color=ft.Colors.TRANSPARENT,
                    bgcolor="#F3F3F5",
                    on_change=lambda e, req_id=r["id"]: self.page.run_task(self.update_status, req_id, e.control.value)
                )

                card = ft.Container(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(ft.Icons.BUILD, color=ft.Colors.WHITE, size=20),
                                bgcolor=st_color,
                                border_radius=7,
                                width=36,
                                height=36,
                                padding=5
                            ),
                            ft.Column(
                                [
                                    ft.Text(r["title"], size=14, weight=ft.FontWeight.W_500),
                                    ft.Text(f"Room {r['room_id']} • {r['username']}", size=11, color=ft.Colors.GREY_600),
                                ],
                                spacing=0,
                                expand=True
                            ),
                            ft.Column(
                                [
                                    create_remark(r["urgency"].upper(), ur_color, ur_bgcolor),
                                    ft.Text(date_str, size=10, color=ft.Colors.GREY_400)
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.END
                            ),
                            status_dd
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=10,
                    border=ft.border.all(1.5, "#FEF3C6"),
                    border_radius=10
                )
                self.requests_list.controls.append(card)

        self.page.update()

    async def update_status(self, request_id, new_status):
        try:
            await self.page.data.update_request_status(request_id, new_status)
            create_banner(self.page, ft.Colors.BLUE_100, ft.Icon(ft.Icons.CHECK, color=ft.Colors.BLUE), "Status updated!", ft.Colors.BLUE)
            await self.load_data()
        except Exception as e:
            print(f"Error updating status: {e}")
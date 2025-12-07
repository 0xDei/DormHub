import flet as ft
from datetime import datetime
import json
import random # used for chart simulation of past months

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Overview(Section):
    def __init__(self, admin_page):
        super().__init__()
        
        # Inherit tight padding from Section (removed manual override)
        self.admin_page = admin_page

        # --- UI Containers ---
        self.info_cards_container = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10, # Reduced spacing
            expand=True
        )
        
        self.charts_container = ft.Row(
            spacing=10, # Reduced spacing
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        self.bottom_section_container = ft.Row(
            spacing=10, # Reduced spacing
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        header = ft.Row(
            [
                ft.Text("Welcome back, Admin!", color="#FF6900", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("👋", size=24)
            ],
            spacing=5
        )

        self.content = ft.Container(
            ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            self.info_cards_container, 
                            ft.Container(height=5), # Reduced Spacer
                            self.charts_container,
                            ft.Container(height=5), # Reduced Spacer
                            self.bottom_section_container
                        ],
                        spacing=10,
                        padding=ft.padding.only(bottom=10),
                        expand=True
                    )
                ],
                spacing=10,
                expand=True
            ),
            expand=True,
            bgcolor="#FFFBEB",
            # Reduced inner padding so content goes closer to the edge
            padding=ft.padding.all(10),
            border_radius=10
        )
        
        # Load data asynchronously
        self.admin_page.page.run_task(self.load_overview_data)

    async def load_overview_data(self):
        """Load all data from database and update the overview"""
        try:
            # 1. Fetch Data
            rooms_data = await self.admin_page.page.data.get_all_rooms()
            requests_data = await self.admin_page.page.data.get_all_requests()
            users_data = await self.admin_page.page.data.get_all_users()
            
            # 2. Process Stats
            total_beds = 0
            occupied_beds = 0
            monthly_income = 0
            
            # Process Rooms
            for room in rooms_data:
                # room: (id, amenities, residents, bed_count, monthly_rent, current_status, thumbnail)
                bed_count = room[3]
                rent = room[4]
                status = room[5]
                
                total_beds += bed_count
                if status == "occupied":
                    occupied_beds += bed_count
                    monthly_income += (bed_count * rent)
            
            occupancy_rate = int((occupied_beds / total_beds * 100)) if total_beds > 0 else 0

            # Process Requests (Pending Tasks)
            pending_tasks = 0
            urgent_tasks_count = 0
            urgent_maintenance_list = []
            
            for req in requests_data:
                # req: (id, room_id, issue, current_status, urgency, user_id, date_created, date_updated)
                status = req[3]
                urgency = req[4]
                
                if status != "completed":
                    pending_tasks += 1
                    if urgency in ["high", "urgent"]:
                        urgent_tasks_count += 1
                        try:
                            issue_data = json.loads(req[2])
                            title = issue_data.get("title", "Issue")
                        except:
                            title = "Maintenance Issue"
                            
                        urgent_maintenance_list.append({
                            "title": title,
                            "room": f"Room {req[1]}",
                            "urgency": urgency
                        })

            # Process Recent Activity (Aggregate Payments, Move-ins, Requests)
            activities = []
            
            # - Move-ins & Payments from Users
            for user in users_data:
                # user: (id, username, email, password, data)
                try:
                    u_data = json.loads(user[4])
                    # Move-in activity
                    if u_data.get("move_in_date") != "N/A":
                        ts = int(u_data.get("move_in_date"))
                        activities.append({
                            "type": "move-in",
                            "title": "New resident moved in",
                            "desc": f"Room {u_data.get('room_id', '?')}",
                            "timestamp": ts,
                            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
                            "color": ft.Colors.GREEN
                        })
                    
                    # Payment activity
                    for payment in u_data.get("payment_history", []):
                        activities.append({
                            "type": "payment",
                            "title": "Rent payment received",
                            "desc": f"₱ {payment.get('amount', 0):,}",
                            "timestamp": payment.get("date"),
                            "icon": ft.Icons.ATTACH_MONEY,
                            "color": ft.Colors.GREEN
                        })
                except:
                    pass

            # - Requests activity
            for req in requests_data:
                activities.append({
                    "type": "request",
                    "title": "Maintenance request submitted",
                    "desc": f"Room {req[1]}",
                    "timestamp": int(req[6]),
                    "icon": ft.Icons.ACCESS_TIME,
                    "color": ft.Colors.ORANGE
                })

            # Sort activities by newest first and take top 4
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            recent_activities = activities[:4]

            # 3. Build UI Elements
            
            # helper to make cards flexible
            def flexible_card(card):
                card.width = None # Remove fixed width
                card.expand = True # Allow it to grow
                return card

            # --- Top Stats Cards ---
            self.info_cards_container.controls = [
                flexible_card(self.create_stat_card("Total Beds", str(total_beds), "+4 this month", ft.Icons.HOME_OUTLINED, "#FFEDD4", "#FF6900")),
                flexible_card(self.create_stat_card("Residents", str(occupied_beds), f"{occupancy_rate}% occupancy", ft.Icons.PEOPLE_OUTLINE, "#FEF3C6", "#E68C2A")),
                flexible_card(self.create_stat_card("Monthly Income", f"₱ {monthly_income:,}", "+9% from last month", ft.Icons.ATTACH_MONEY, "#DBFCE7", "#14AD4E")),
                flexible_card(self.create_stat_card("Pending Tasks", str(pending_tasks), f"{urgent_tasks_count} urgent", ft.Icons.ERROR_OUTLINE, "#FFE2E2", "#EC2C33")),
            ]

            # --- Charts (Simulated History + Real Current Data) ---
            # Occupancy Line Chart
            # Simulating a gentle upward trend ending in current occupancy
            trend_data = [
                max(0, occupied_beds - 15), 
                max(0, occupied_beds - 12), 
                max(0, occupied_beds - 8), 
                max(0, occupied_beds - 5), 
                max(0, occupied_beds - 2), 
                occupied_beds
            ]
            
            occupancy_chart = self.create_chart_container(
                "Occupancy Trend",
                ft.LineChart(
                    data_series=[
                        ft.LineChartData(
                            data_points=[
                                ft.LineChartDataPoint(0, trend_data[0]),
                                ft.LineChartDataPoint(1, trend_data[1]),
                                ft.LineChartDataPoint(2, trend_data[2]),
                                ft.LineChartDataPoint(3, trend_data[3]),
                                ft.LineChartDataPoint(4, trend_data[4]),
                                ft.LineChartDataPoint(5, trend_data[5]),
                            ],
                            stroke_width=3,
                            color="#FF6900",
                            curved=True,
                            stroke_cap_round=True,
                        )
                    ],
                    border=ft.border.all(0, ft.Colors.TRANSPARENT),
                    horizontal_grid_lines=ft.ChartGridLines(
                        interval=10, color=ft.Colors.with_opacity(0.2, ft.Colors.GREY), width=1
                    ),
                    vertical_grid_lines=ft.ChartGridLines(
                        interval=1, color=ft.Colors.with_opacity(0.2, ft.Colors.GREY), width=1
                    ),
                    left_axis=ft.ChartAxis(
                        labels=[ft.ChartAxisLabel(value=i, label=ft.Text(str(i), size=10)) for i in range(0, total_beds + 10, 15)],
                        labels_size=20,
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(0, ft.Text("Jan", size=10)),
                            ft.ChartAxisLabel(1, ft.Text("Feb", size=10)),
                            ft.ChartAxisLabel(2, ft.Text("Mar", size=10)),
                            ft.ChartAxisLabel(3, ft.Text("Apr", size=10)),
                            ft.ChartAxisLabel(4, ft.Text("May", size=10)),
                            ft.ChartAxisLabel(5, ft.Text("Jun", size=10)),
                        ],
                        labels_size=20,
                    ),
                    min_y=0,
                    max_y=total_beds + 10,
                    expand=True,
                )
            )

            # Revenue Bar Chart
            # Simulating revenue roughly proportional to occupancy
            revenue_data = [
                monthly_income * 0.85,
                monthly_income * 0.88,
                monthly_income * 0.92,
                monthly_income * 0.95,
                monthly_income * 0.94,
                monthly_income
            ]

            revenue_chart = self.create_chart_container(
                "Monthly Revenue",
                ft.BarChart(
                    bar_groups=[
                        # border_radius removed to make bars rectangular
                        ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[0], width=25, color="#FE9A00", border_radius=0)]),
                        ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[1], width=25, color="#FE9A00", border_radius=0)]),
                        ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[2], width=25, color="#FE9A00", border_radius=0)]),
                        ft.BarChartGroup(x=3, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[3], width=25, color="#FE9A00", border_radius=0)]),
                        ft.BarChartGroup(x=4, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[4], width=25, color="#FE9A00", border_radius=0)]),
                        ft.BarChartGroup(x=5, bar_rods=[ft.BarChartRod(from_y=0, to_y=revenue_data[5], width=25, color="#FE9A00", border_radius=0)]),
                    ],
                    border=ft.border.all(0, ft.Colors.TRANSPARENT),
                    left_axis=ft.ChartAxis(labels_size=30, labels=[ft.ChartAxisLabel(value=i, label=ft.Text(f"{i//1000}k", size=10)) for i in range(0, int(monthly_income * 1.2), 15000)]),
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(0, ft.Text("Jan", size=10)),
                            ft.ChartAxisLabel(1, ft.Text("Feb", size=10)),
                            ft.ChartAxisLabel(2, ft.Text("Mar", size=10)),
                            ft.ChartAxisLabel(3, ft.Text("Apr", size=10)),
                            ft.ChartAxisLabel(4, ft.Text("May", size=10)),
                            ft.ChartAxisLabel(5, ft.Text("Jun", size=10)),
                        ],
                        labels_size=20,
                    ),
                    horizontal_grid_lines=ft.ChartGridLines(
                        color=ft.Colors.with_opacity(0.2, ft.Colors.GREY), width=1, dash_pattern=[3, 3]
                    ),
                    expand=True,
                )
            )

            self.charts_container.controls = [occupancy_chart, revenue_chart]

            # --- Bottom Section (Activity & Urgent Tasks) ---
            
            # Activity List
            activity_items = []
            for act in recent_activities:
                # Calculate relative time string
                now = datetime.now().timestamp()
                diff = now - act["timestamp"]
                if diff < 3600: time_str = f"{int(diff/60)} mins ago"
                elif diff < 86400: time_str = f"{int(diff/3600)} hours ago"
                else: time_str = f"{int(diff/86400)} days ago"

                activity_items.append(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(act["icon"], color=act["color"], size=18),
                                bgcolor=ft.Colors.with_opacity(0.1, act["color"]),
                                padding=8,
                                border_radius=50
                            ),
                            ft.Column(
                                [
                                    ft.Text(act["title"], size=12, weight=ft.FontWeight.W_500),
                                    ft.Text(act["desc"], size=10, color=ft.Colors.GREY_500)
                                ],
                                spacing=2,
                                expand=True
                            ),
                            ft.Text(time_str, size=10, color=ft.Colors.GREY_400)
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )

            recent_activity_card = self.create_section_card(
                "Recent Activity",
                ft.Column(activity_items, spacing=15) if activity_items else ft.Text("No recent activity", size=12, color=ft.Colors.GREY_400)
            )

            # Urgent Maintenance List
            maintenance_items = []
            for item in urgent_maintenance_list:
                tag_color = "#FF3333" if item["urgency"] == "urgent" else "#FF9800"
                maintenance_items.append(
                    ft.Container(
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(item["title"], size=12, weight=ft.FontWeight.W_600),
                                        ft.Text(item["room"], size=10, color=ft.Colors.GREY_500)
                                    ],
                                    spacing=2,
                                    expand=True
                                ),
                                ft.Container(
                                    ft.Text(item["urgency"], color=ft.Colors.WHITE, size=10, weight=ft.FontWeight.BOLD),
                                    bgcolor=tag_color,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor="#FFF5E5" if item["urgency"] != "urgent" else "#FFE5E5", # Subtle bg for rows
                        padding=10,
                        border_radius=8
                    )
                )

            urgent_maintenance_card = self.create_section_card(
                "Urgent Maintenance",
                ft.Column(maintenance_items, spacing=10) if maintenance_items else ft.Text("No urgent issues! Good job.", size=12, color=ft.Colors.GREY_400)
            )

            self.bottom_section_container.controls = [recent_activity_card, urgent_maintenance_card]

            self.admin_page.page.update()
            
        except Exception as e:
            print(f"Error loading overview data: {e}")
            import traceback
            traceback.print_exc()

    # --- Helper Methods for UI Styling ---

    def create_stat_card(self, title, value, subtext, icon, bg_color, icon_color):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(title, size=12, color=ft.Colors.GREY_600),
                            ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(subtext, size=10, color=ft.Colors.GREY_500)
                        ],
                        spacing=5,
                        expand=True
                    ),
                    ft.Container(
                        ft.Icon(icon, color=icon_color, size=24),
                        bgcolor="white",
                        border_radius=10,
                        padding=10,
                        border=ft.border.all(1, icon_color)
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=15, # Reduced padding
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

    def create_chart_container(self, title, chart):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, color="#FF6900", weight=ft.FontWeight.BOLD),
                    ft.Container(chart, height=200, expand=True) # Set fixed height for chart area
                ],
                spacing=10
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=15, # Reduced padding
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

    def create_section_card(self, title, content):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, color="#FF6900", weight=ft.FontWeight.BOLD),
                    content
                ],
                spacing=10
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=15, # Reduced padding
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )
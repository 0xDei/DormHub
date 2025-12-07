import flet as ft
from datetime import datetime
import json
import calendar
import asyncio

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Overview(Section):
    def __init__(self, admin_page):
        super().__init__()
        
        self.padding = ft.padding.all(10)
        self.admin_page = admin_page
        self.running = False # Flag to control the update loop

        # --- UI Containers (Responsive) ---
        self.info_cards_container = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10, 
        )
        
        self.charts_container = ft.ResponsiveRow(
            spacing=20,
            run_spacing=20,
        )

        self.bottom_section_container = ft.ResponsiveRow(
            spacing=20,
            run_spacing=20,
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
                            ft.Container(height=5),
                            self.charts_container,
                            ft.Container(height=5),
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
            padding=ft.padding.all(10),
            border_radius=10
        )
        
    def did_mount(self):
        """Called when the control is added to the page."""
        self.running = True
        self.admin_page.page.run_task(self.update_data_loop)

    def will_unmount(self):
        """Called when the control is removed from the page."""
        self.running = False

    async def update_data_loop(self):
        """Background task to refresh data periodically."""
        while self.running:
            await self.load_overview_data()
            try:
                # Wait for 5 seconds before next update
                await asyncio.sleep(5)
            except Exception:
                break

    async def load_overview_data(self):
        """Load all data from database and update the overview"""
        if not self.running: return

        try:
            # 1. Fetch Data
            rooms_data = await self.admin_page.page.data.get_all_rooms()
            requests_data = await self.admin_page.page.data.get_all_requests()
            users_data = await self.admin_page.page.data.get_all_users()
            
            # Helper to parse room rent
            room_rents = {str(r[0]): r[4] for r in rooms_data}

            # 2. Process Stats
            total_beds = 0
            for room in rooms_data:
                total_beds += room[3] # bed_count

            residents_count = 0
            projected_income = 0
            actual_income_this_month = 0
            
            now = datetime.now()
            start_of_month = datetime(now.year, now.month, 1).timestamp()

            activities = []
            resident_move_ins = [] # List of timestamps for occupancy trend

            for user in users_data:
                try:
                    u_data = json.loads(user[4])
                    room_id = str(u_data.get("room_id", "N/A"))
                    
                    if room_id != "N/A":
                        residents_count += 1
                        projected_income += room_rents.get(room_id, 0)
                        
                        # Collect Move-in Date for Trend Calculation
                        move_in_str = u_data.get("move_in_date", "N/A")
                        if move_in_str != "N/A":
                            resident_move_ins.append(int(move_in_str))
                    
                    # Payment History
                    for pay in u_data.get("payment_history", []):
                        p_date = pay.get("date", 0)
                        p_amount = pay.get("amount", 0)
                        
                        if p_date >= start_of_month:
                            actual_income_this_month += p_amount
                        
                        activities.append({
                            "type": "payment",
                            "title": f"Payment received from {user[1]}",
                            "desc": f"₱ {p_amount:,}",
                            "timestamp": p_date,
                            "icon": ft.Icons.ATTACH_MONEY,
                            "color": ft.Colors.GREEN
                        })

                    # Move-in Activity Log
                    move_in = u_data.get("move_in_date", "N/A")
                    if move_in != "N/A":
                        activities.append({
                            "type": "move-in",
                            "title": f"{user[1]} moved in",
                            "desc": f"Room {room_id}",
                            "timestamp": int(move_in),
                            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
                            "color": ft.Colors.BLUE
                        })

                except Exception as ex:
                    print(f"Error parsing user {user[0]}: {ex}")

            # Requests Stats
            requests_count = 0
            urgent_count = 0
            urgent_maintenance_list = []
            
            for req in requests_data:
                status = req[3]
                urgency = req[4]
                date_created = int(req[6])
                
                if status != "completed":
                    requests_count += 1
                    if urgency in ["high", "urgent"]:
                        urgent_count += 1
                        try:
                            title = json.loads(req[2]).get("title", "Maintenance Issue")
                        except: title = "Issue"
                        
                        urgent_maintenance_list.append({
                            "title": title,
                            "room": f"Room {req[1]}",
                            "urgency": urgency
                        })
                
                activities.append({
                    "type": "request",
                    "title": "Maintenance Request",
                    "desc": f"Room {req[1]} - {status}",
                    "timestamp": date_created,
                    "icon": ft.Icons.BUILD_CIRCLE_OUTLINED,
                    "color": ft.Colors.ORANGE
                })

            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            recent_activities = activities[:5]

            # 3. Calculate Occupancy Trend Data (Last 6 Months)
            trend_points = []
            trend_labels = []
            
            # Loop backwards from 5 to 0 (5 months ago to today)
            for i in range(5, -1, -1):
                # Calculate month and year
                target_month = now.month - i
                target_year = now.year
                
                # Adjust for year wraparound (e.g. Jan - 1 month = Dec previous year)
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                # Get the last second of that target month to count everyone who moved in by then
                _, last_day = calendar.monthrange(target_year, target_month)
                month_end_ts = datetime(target_year, target_month, last_day, 23, 59, 59).timestamp()
                
                # Count residents who moved in <= this timestamp
                # Note: This simple logic assumes residents don't move out (since we don't track move-out dates yet)
                count = sum(1 for mid in resident_move_ins if mid <= month_end_ts)
                
                trend_points.append(count)
                # Label ex: "Nov", "Dec"
                trend_labels.append(datetime(target_year, target_month, 1).strftime("%b"))


            # 4. Build UI Elements
            bed_count_safe = max(total_beds, 1) 
            percent = (residents_count / bed_count_safe) * 100

            # --- Top Stats Cards ---
            card_col = {"xs": 12, "sm": 6, "md": 3}

            self.info_cards_container.controls = [
                self.create_stat_card("Total Beds", str(total_beds), "Capacity", ft.Icons.HOME_OUTLINED, "#FFEDD4", "#FF6900", col=card_col),
                self.create_stat_card("Residents", str(residents_count), f"{percent:.0f}% Occupancy", ft.Icons.PEOPLE_OUTLINE, "#FEF3C6", "#E68C2A", col=card_col),
                self.create_stat_card("Est. Monthly Income", f"₱ {projected_income:,}", "Based on occupancy", ft.Icons.ATTACH_MONEY, "#DBFCE7", "#14AD4E", col=card_col),
                self.create_stat_card("Pending Tasks", str(requests_count), f"{urgent_count} Urgent", ft.Icons.ERROR_OUTLINE, "#FFE2E2", "#EC2C33", col=card_col),
            ]

            # --- Charts ---
            
            # Occupancy Trend (Line Chart)
            # Create Chart Data Points
            line_data_points = []
            for i, val in enumerate(trend_points):
                line_data_points.append(
                    ft.LineChartDataPoint(i, val)
                )

            max_occ = max(max(trend_points) if trend_points else 0, total_beds, 1) + 2
            
            # Generate Custom Axis Labels based on month names
            bottom_axis_labels = []
            for i, label in enumerate(trend_labels):
                bottom_axis_labels.append(
                    ft.ChartAxisLabel(value=i, label=ft.Text(label, size=10, weight=ft.FontWeight.BOLD))
                )

            chart_col = {"xs": 12, "md": 6}

            occupancy_chart = self.create_chart_container(
                "Occupancy Trend",
                ft.LineChart(
                    data_series=[
                        ft.LineChartData(
                            data_points=line_data_points,
                            stroke_width=3,
                            color="#FF6900",
                            curved=True,
                            stroke_cap_round=True,
                            below_line_bgcolor=ft.Colors.with_opacity(0.1, "#FF6900")
                        )
                    ],
                    bottom_axis=ft.ChartAxis(
                        labels=bottom_axis_labels,
                        labels_size=20,
                    ),
                    left_axis=ft.ChartAxis(labels_size=25),
                    border=ft.border.all(0, ft.Colors.TRANSPARENT),
                    horizontal_grid_lines=ft.ChartGridLines(
                        interval=1, color=ft.Colors.with_opacity(0.2, ft.Colors.GREY), width=1
                    ),
                    min_y=0,
                    max_y=max_occ,
                    expand=True,
                    tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK)
                ),
                col=chart_col
            )

            # Revenue (Bar Chart)
            max_rev = max(projected_income, actual_income_this_month, 1)
            step_rev = max(1000, int(max_rev // 4))
            labels_rev = [ft.ChartAxisLabel(i, ft.Text(f"{i//1000}k", size=10)) for i in range(0, int(max_rev * 1.2), step_rev)]

            revenue_chart = self.create_chart_container(
                "Financial Overview (This Month)",
                ft.BarChart(
                    bar_groups=[
                        ft.BarChartGroup(
                            x=0,
                            bar_rods=[ft.BarChartRod(from_y=0, to_y=actual_income_this_month, width=40, color="#0099FF", border_radius=0, tooltip=f"Collected: {actual_income_this_month}")]
                        ),
                        ft.BarChartGroup(
                            x=1,
                            bar_rods=[ft.BarChartRod(from_y=0, to_y=projected_income, width=40, color="#7C3AED", border_radius=0, tooltip=f"Projected: {projected_income}")]
                        ),
                    ],
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(0, ft.Text("Collected")),
                            ft.ChartAxisLabel(1, ft.Text("Projected")),
                        ]
                    ),
                    left_axis=ft.ChartAxis(labels=labels_rev, labels_size=40),
                    border=ft.border.all(0, ft.Colors.TRANSPARENT),
                    horizontal_grid_lines=ft.ChartGridLines(
                        color=ft.Colors.with_opacity(0.2, ft.Colors.GREY), width=1, dash_pattern=[3, 3]
                    ),
                    tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                    max_y=max_rev * 1.2,
                    expand=True
                ),
                col=chart_col
            )

            self.charts_container.controls = [occupancy_chart, revenue_chart]

            # --- Bottom Section ---
            activity_col = {"xs": 12, "md": 6}
            
            activity_display_items = []
            if not recent_activities:
                activity_display_items.append(ft.Text("No recent activity", color=ft.Colors.GREY_400))
            else:
                for act in recent_activities:
                    now_ts = datetime.now().timestamp()
                    diff = now_ts - act["timestamp"]
                    
                    if diff < 60: time_str = "Just now"
                    elif diff < 3600: time_str = f"{int(diff/60)}m ago"
                    elif diff < 86400: time_str = f"{int(diff/3600)}h ago"
                    else: time_str = f"{int(diff/86400)}d ago"

                    activity_display_items.append(
                        ft.Container(
                            ft.Row(
                                [
                                    ft.Container(
                                        ft.Icon(act["icon"], color=act["color"], size=16),
                                        bgcolor=ft.Colors.with_opacity(0.1, act["color"]),
                                        padding=8,
                                        border_radius=50
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(act["title"], size=12, weight=ft.FontWeight.W_600),
                                            ft.Text(act["desc"], size=10, color=ft.Colors.GREY_500)
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                    ft.Text(time_str, size=10, color=ft.Colors.GREY_400)
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.only(bottom=5)
                        )
                    )

            recent_activity_card = self.create_section_card(
                "Recent Activity",
                ft.Column(activity_display_items, spacing=10),
                col=activity_col
            )

            maintenance_display_items = []
            if not urgent_maintenance_list:
                maintenance_display_items.append(ft.Text("No urgent issues! Good job.", size=12, color=ft.Colors.GREY_400))
            else:
                for item in urgent_maintenance_list:
                    tag_color = "#FF3333" if item["urgency"] == "urgent" else "#FF9800"
                    maintenance_display_items.append(
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
                                        ft.Text(item["urgency"].upper(), color=ft.Colors.WHITE, size=10, weight=ft.FontWeight.BOLD),
                                        bgcolor=tag_color,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=12
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            bgcolor="#FFF5E5",
                            padding=10,
                            border_radius=8
                        )
                    )

            urgent_maintenance_card = self.create_section_card(
                "Urgent Maintenance",
                ft.Column(maintenance_display_items, spacing=10),
                col=activity_col
            )

            self.bottom_section_container.controls = [recent_activity_card, urgent_maintenance_card]

            if self.running:
                self.admin_page.page.update()
            
        except Exception as e:
            print(f"Error loading overview data: {e}")
            import traceback
            traceback.print_exc()

    # --- Helper Methods for UI Styling ---

    def create_stat_card(self, title, value, subtext, icon, bg_color, icon_color, col=None):
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
            padding=15,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            col=col
        )

    def create_chart_container(self, title, chart, col=None):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, color="#FF6900", weight=ft.FontWeight.BOLD),
                    ft.Container(chart, height=200, expand=True)
                ],
                spacing=10
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=15,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            col=col
        )

    def create_section_card(self, title, content, col=None):
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
            padding=15,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            col=col
        )
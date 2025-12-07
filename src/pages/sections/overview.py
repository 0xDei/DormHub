import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Overview(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page

        # Create placeholder containers that will be updated with data
        self.info_cards_container = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            expand=True
        )
        
        self.charts_container = ft.Row(
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )

        header = ft.Row(
            [
                ft.Text("Welcome Back, Admin", color="#FF6900", size=16, weight=ft.FontWeight.W_500),
                ft.Icon(ft.Icons.WAVING_HAND_ROUNDED, size=24, color=ft.Colors.YELLOW)
            ],
            spacing=3.5
        )

        self.content = ft.Container(
            ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            self.info_cards_container, 
                            self.charts_container
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
        
        # Load data asynchronously
        self.admin_page.page.run_task(self.load_overview_data)

    async def load_overview_data(self):
        """Load all data from database and update the overview"""
        try:
            # Fetch data from database
            rooms_data = await self.admin_page.page.data.get_all_rooms()
            requests_data = await self.admin_page.page.data.get_all_requests()
            users_data = await self.admin_page.page.data.get_all_users()
            
            # Calculate statistics
            bed_count = 0
            occupied_beds = 0
            available_beds = 0
            estimated_income = 0

            for room_tuple in rooms_data:
                # room_tuple: (id, amenities, residents, bed_count, monthly_rent, current_status, thumbnail)
                room_bed_count = room_tuple[3]  # bed_count
                room_status = room_tuple[5]  # current_status
                monthly_rent = room_tuple[4]  # monthly_rent
                
                bed_count += room_bed_count
                
                # Count beds based on room status
                if room_status == "occupied":
                    occupied_beds += room_bed_count
                    estimated_income += room_bed_count * monthly_rent
                elif room_status == "available":
                    available_beds += room_bed_count
                # maintenance rooms are not counted as available or occupied
            
            # residents_count is same as occupied_beds
            residents_count = occupied_beds
            
            requests_count = 0
            urgent_count = 0
            
            for request_tuple in requests_data:
                # request_tuple: (id, room_id, issue, current_status, urgency, user_id, date_created, date_updated)
                if request_tuple[3] == "completed": continue
                requests_count += 1
                if request_tuple[4] == "high": urgent_count += 1

            # Calculate occupancy percentage
            bed_count_safe = max(bed_count, 1)
            percent = (residents_count / bed_count_safe) * 100


            self.info_cards_container.controls = [
                create_info_card(
                    "Total Beds", 
                    [
                        ft.Row(
                            [
                                ft.Text(bed_count, size=14, weight=ft.FontWeight.BOLD),
                                ft.Column([
                                    ft.Text(f"{percent:.1f}%", size=10, color=ft.Colors.GREY_500), 
                                    ft.Text("occupied", size=10, color=ft.Colors.GREY_500)
                                ], spacing=-5)
                            ],
                            spacing=5
                        )
                    ],
                    ft.Icon(ft.Icons.BED_OUTLINED, color="#FF6900", size=24),
                    "left",
                    "#FFEDD4",
                    150,
                    90
                ),
                create_info_card(
                    "Residents", 
                    [
                        ft.Text(residents_count, size=14, weight=ft.FontWeight.BOLD),
                    ],
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE_ROUNDED, color="#E68C2A", size=24),
                    "left",
                    "#FEF3C6",
                    150,
                    90
                ),
                create_info_card(
                    "Income", 
                    [
                        ft.Text("₱ " + f"{estimated_income:,}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"per month", size=10, color=ft.Colors.GREY_500)
                    ],
                    ft.Icon(ft.Icons.ATTACH_MONEY, color="#14AD4E", size=24),
                    "left",
                    "#DBFCE7",
                    150,
                    90
                ),
                create_info_card(
                    "Requests", 
                    [
                        ft.Text(requests_count, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{urgent_count} urgent", size=10, color=ft.Colors.GREY_500)
                    ],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#EC2C33", size=24),
                    "left",
                    "#FFE2E2",
                    150,
                    90
                )
            ]

            # Create occupancy chart
            occupied = occupied_beds
            available = available_beds

            max_occ = max(occupied, available, 1)
            step = max(1, max_occ // 4)
            labels = [ft.ChartAxisLabel(i, ft.Text(str(i))) for i in range(0, max_occ + 1, step)]
            if labels[-1].value != max_occ: 
                labels.append(ft.ChartAxisLabel(max_occ, ft.Text(str(max_occ))))

            occupancy_chart = ft.Container(
                width=300,
                content=ft.Column(
                    [
                        ft.Text("Occupancy", size=14, weight=ft.FontWeight.W_600),
                        ft.BarChart(
                            bar_groups=[
                                ft.BarChartGroup(
                                    x=0,
                                    bar_rods=[ft.BarChartRod(from_y=0, to_y=occupied, width=22, color="#FF6900")]
                                ),
                                ft.BarChartGroup(
                                    x=1,
                                    bar_rods=[ft.BarChartRod(from_y=0, to_y=available, width=22, color="#14AD4E")]
                                ),
                            ],
                            bottom_axis=ft.ChartAxis(
                                labels=[
                                    ft.ChartAxisLabel(0, ft.Text("Occupied")),
                                    ft.ChartAxisLabel(1, ft.Text("Available")),
                                ]
                            ),
                            left_axis=ft.ChartAxis(
                                labels=labels,
                                labels_size=22,
                            ),
                            animate=400,
                            expand=True
                        )
                    ]
                ),
                padding=15,
                bgcolor="#FFF5E5",
                border_radius=10
            )

            # Calculate total collected income
            total_income = 0
            for user_tuple in users_data:
                # user_tuple: (id, username, email, password, data)
                try:
                    data = json.loads(user_tuple[4]) if user_tuple[4] else {}
                    payments = data.get("payment_history", [])
                    for p in payments:
                        amt = p.get("amount", 0)
                        total_income += amt
                except Exception as e:
                    print(f"Error parsing user data: {e}")
                    pass

            max_y = max(total_income, estimated_income, 1)
            step = max(1_000, int(max_y // 4))
            labels = [ft.ChartAxisLabel(i, ft.Text(f"{i//1000}k")) for i in range(0, max_y + 1, step)]
            if labels[-1].value != max_y: 
                labels.append(ft.ChartAxisLabel(max_y, ft.Text(f"{max_y//1000}k")))

            income_chart = ft.Container(
                width=300,
                content=ft.Column(
                    [
                        ft.Text("Income Overview", size=14, weight=ft.FontWeight.W_600),
                        ft.BarChart(
                            bar_groups=[
                                ft.BarChartGroup(
                                    x=0,
                                    bar_rods=[ft.BarChartRod(from_y=0, to_y=total_income, width=22, color="#0099FF")]
                                ),
                                ft.BarChartGroup(
                                    x=1,
                                    bar_rods=[ft.BarChartRod(from_y=0, to_y=estimated_income, width=22, color="#7C3AED")]
                                ),
                            ],
                            bottom_axis=ft.ChartAxis(
                                labels=[
                                    ft.ChartAxisLabel(0, ft.Text("Collected")),
                                    ft.ChartAxisLabel(1, ft.Text("Projected")),
                                ]
                            ),
                            left_axis=ft.ChartAxis(
                                labels=labels,
                                labels_size=28,
                            ),
                            animate=400,
                            expand=True
                        )
                    ]
                ),
                padding=15,
                bgcolor="#E0F2FF",
                border_radius=10
            )

            self.charts_container.controls = [
                occupancy_chart,
                income_chart
            ]

            self.admin_page.page.update()
            print("Overview data loaded successfully!")
            
        except Exception as e:
            print(f"Error loading overview data: {e}")
            import traceback
            traceback.print_exc()
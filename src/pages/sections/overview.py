import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class Overview(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page

        header = ft.Row(
            [
                ft.Text("Welcome Back, Admin", color="#FF6900", size=16, weight=ft.FontWeight.W_500),
                ft.Icon(ft.Icons.WAVING_HAND_ROUNDED, size=24, color=ft.Colors.YELLOW)
            ],
            spacing=3.5
        )

        bed_count = 0
        residents_count = 0
        estimated_income = 0

        for room_info in self.admin_page.data["rooms"]:
            bed_count += room_info[3]
            room_res_count = len(json.loads(room_info[2]))
            residents_count += room_res_count
            estimated_income += room_res_count * room_info[4]
            
        requests_count = 0
        urgent_count = 0
        
        for request_info in self.admin_page.data["requests"]:
            if request_info[2] == "completed": continue
            requests_count += 1
            if request_info[3] == "high": urgent_count += 1

        bed_count_safe = max(bed_count, 1)
        percent = (residents_count / bed_count_safe) * 100

        info_cards = ft.Row(
                [
                    create_info_card(
                        "Total Beds", 
                        [
                            ft.Row(
                                [
                                    ft.Text(bed_count, size=14, weight=ft.FontWeight.BOLD),
                                    ft.Column([ft.Text(f"{percent:.1f}%", size=10, color=ft.Colors.GREY_500), ft.Text("occupied", size=10, color=ft.Colors.GREY_500)], spacing=-5)
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
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                expand=True
            )

        occupied = residents_count
        available = max(bed_count - occupied, 0)

        max_occ = max(occupied, bed_count_safe, 1)
        step = max(1, max_occ // 4)
        labels = [ft.ChartAxisLabel(i, ft.Text(str(i))) for i in range(0, max_occ + 1, step)]
        if labels[-1].value != max_occ: labels.append(ft.ChartAxisLabel(max_occ, ft.Text(str(max_occ))))

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

        total_income = 0
        for resident in self.admin_page.data["residents"]:
            try:
                data = json.loads(resident[4])
                payments = data.get("payment_history", [])
                for p in payments:
                    amt = p.get("amount", 0)
                    total_income += amt
            except: pass

        max_y = max(total_income, estimated_income, 1)
        step = max(1_000, int(max_y // 4))
        labels = [ft.ChartAxisLabel(i, ft.Text(f"{i//1000}k")) for i in range(0, max_y + 1, step)]
        if labels[-1].value != max_y: labels.append(ft.ChartAxisLabel(max_y, ft.Text(f"{max_y//1000}k")))

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

        charts_row = ft.Row(
            [
                occupancy_chart,
                income_chart
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            info_cards, charts_row
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
        
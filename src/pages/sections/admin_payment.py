import flet as ft
import json
from datetime import datetime
import math

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class AdminPayment(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.payment_data_list = [] # Store processed data for sorting

        # Header
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Payment Monitoring", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                                ft.Icon(ft.Icons.MONEY_OFF_ROUNDED, size=24, color=ft.Colors.RED_400)
                            ],
                            spacing=3.5,
                        ),
                        ft.Text("Monitor overdue payments and upcoming rent due dates", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                )
            ]
        )

        # Stats placeholders
        self.total_unpaid_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
        self.total_amount_text = ft.Text("₱ 0", size=20, weight=ft.FontWeight.BOLD)

        stats = ft.Row(
            [
                create_info_card(
                    "Residents with Dues",
                    [self.total_unpaid_text],
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE_ROUNDED, color="#C28239", size=28),
                    "left",
                    "#FEF9C3",
                    200,
                    87
                ),
                create_info_card(
                    "Total Outstanding",
                    [self.total_amount_text],
                    ft.Icon(ft.Icons.ATTACH_MONEY, color="#ff3333", size=28),
                    "left",
                    "#ffe6e6",
                    250,
                    87
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        # List for residents sorted by due date
        self.payment_list = ft.ListView(spacing=7, expand=True)

        list_container = ft.Container(
            ft.Column(
                [
                    ft.Text("Rent Due Dates (Sorted by Urgency)", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                    self.payment_list
                ],
                spacing=15
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
        self.admin_page.page.run_task(self.load_data)

    async def load_data(self):
        try:
            users = await self.admin_page.page.data.get_all_users()
            self.payment_data_list = []
            
            # Stats counters
            residents_with_dues = 0
            total_outstanding_amount = 0
            
            current_ts = datetime.now().timestamp()

            for user in users:
                try:
                    # user: (id, username, email, password, data)
                    user_data = json.loads(user[4])
                    room_id = user_data.get("room_id", "N/A")
                    
                    # Skip users without a room
                    if room_id == "N/A": continue

                    # 1. Calculate Outstanding Dues (Previous months)
                    unpaid_dues = user_data.get("unpaid_dues", [])
                    user_outstanding = sum(item.get('amount', 0) for item in unpaid_dues)
                    
                    if user_outstanding > 0:
                        residents_with_dues += 1
                        total_outstanding_amount += user_outstanding

                    # 2. Process Next Due Date
                    due_date_str = user_data.get("due_date", "N/A")
                    days_remaining = 9999 # Default high value for "Not Set"
                    due_date_display = "Not Set"
                    
                    if due_date_str != "N/A":
                        try:
                            due_ts = int(due_date_str)
                            dt = datetime.fromtimestamp(due_ts)
                            due_date_display = dt.strftime("%b %d, %Y")
                            
                            # Calculate days difference
                            diff_seconds = due_ts - current_ts
                            days_remaining = math.ceil(diff_seconds / (24 * 3600))
                        except:
                            pass

                    self.payment_data_list.append({
                        "username": user[1],
                        "room_id": room_id,
                        "monthly_rent": user_data.get("monthly_rent", 0),
                        "outstanding": user_outstanding,
                        "due_date_display": due_date_display,
                        "days_remaining": days_remaining
                    })

                except Exception as e:
                    print(f"Error parsing user {user[0]}: {e}")
                    continue

            # Update Stats UI
            self.total_unpaid_text.value = str(residents_with_dues)
            self.total_amount_text.value = f"₱ {total_outstanding_amount:,}"

            # Sort Logic: 
            # 1. Residents with outstanding dues (Overdue) come first (handled by negative days_remaining effectively if we considered old dues, but here we sort by next due date primarily)
            # Actually, to make it most useful: 
            # Sort by 'days_remaining' ASCENDING. 
            # Negative = Overdue/Past Due. 0 = Due Today. Positive = Upcoming.
            self.payment_data_list.sort(key=lambda x: x['days_remaining'])

            # Build List UI
            self.payment_list.controls.clear()
            
            if not self.payment_data_list:
                self.payment_list.controls.append(
                    ft.Container(
                        ft.Text("No residents with assigned rooms found.", color=ft.Colors.GREY_400),
                        alignment=ft.alignment.center,
                        expand=True,
                        margin=ft.margin.only(top=50)
                    )
                )
            else:
                for item in self.payment_data_list:
                    days = item['days_remaining']
                    
                    # Determine Status Style
                    if days < 0:
                        status_text = f"Overdue by {abs(days)} day(s)"
                        status_color = "#D66875" # Red
                        bg_color = "#FFE2E2"
                        icon = ft.Icons.WARNING_ROUNDED
                    elif days == 0:
                        status_text = "Due Today"
                        status_color = "#E18526" # Orange
                        bg_color = "#FFEDD4"
                        icon = ft.Icons.ACCESS_TIME_FILLED
                    elif days <= 7:
                        status_text = f"Due in {days} day(s)"
                        status_color = "#E18526" # Orange
                        bg_color = "#FFEDD4"
                        icon = ft.Icons.ACCESS_TIME
                    else:
                        status_text = f"Due in {days} days"
                        status_color = "#00cc0a" # Green
                        bg_color = "#b3ffb6"
                        icon = ft.Icons.CALENDAR_MONTH

                    if item['due_date_display'] == "Not Set":
                        status_text = "Date Not Set"
                        status_color = ft.Colors.GREY_500
                        bg_color = ft.Colors.GREY_100
                        icon = ft.Icons.HELP_OUTLINE

                    # Main Card Content
                    card = ft.Container(
                        ft.Row(
                            [
                                # User Icon
                                ft.Container(
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=20),
                                    bgcolor=status_color if item['due_date_display'] != "Not Set" else ft.Colors.GREY_400,
                                    border_radius=7,
                                    width=36,
                                    height=36,
                                    alignment=ft.alignment.center
                                ),
                                # Name & Room
                                ft.Column(
                                    [
                                        ft.Text(item['username'], size=14, weight=ft.FontWeight.W_600),
                                        ft.Text(f"Room {item['room_id']}", size=11, color=ft.Colors.GREY_600),
                                    ],
                                    spacing=0,
                                    expand=True
                                ),
                                # Due Date Info
                                ft.Column(
                                    [
                                        ft.Row([
                                            ft.Text(status_text, size=12, color=status_color, weight=ft.FontWeight.BOLD),
                                            ft.Icon(icon, size=14, color=status_color)
                                        ], spacing=5, alignment=ft.MainAxisAlignment.END),
                                        ft.Text(f"Due: {item['due_date_display']}", size=10, color=ft.Colors.GREY_500)
                                    ],
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.END
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10,
                        border=ft.border.all(1, bg_color),
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE
                    )
                    self.payment_list.controls.append(card)

            self.admin_page.page.update()

        except Exception as e:
            print(f"Error loading payment data: {e}")
            import traceback
            traceback.print_exc()
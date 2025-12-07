import flet as ft
import json
from datetime import datetime

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark

class AdminPayment(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.unpaid_residents = []

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
                        ft.Text("Monitor overdue payments and resident balances", size=12, weight=ft.FontWeight.W_500)
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

        # List for residents with unpaid dues
        self.payment_list = ft.ListView(spacing=7, expand=True)

        list_container = ft.Container(
            ft.Column(
                [
                    ft.Text("Overdue Residents", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
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
            self.unpaid_residents = []
            total_outstanding = 0
            
            for user in users:
                try:
                    # user: (id, username, email, password, data)
                    user_data = json.loads(user[4])
                    unpaid_dues = user_data.get("unpaid_dues", [])
                    
                    if len(unpaid_dues) > 0:
                        user_total = sum(item.get('amount', 0) for item in unpaid_dues)
                        total_outstanding += user_total
                        
                        self.unpaid_residents.append({
                            "id": user[0],
                            "username": user[1],
                            "room_id": user_data.get("room_id", "N/A"),
                            "unpaid_count": len(unpaid_dues),
                            "total_due": user_total,
                            "dues": unpaid_dues
                        })
                except Exception as e:
                    print(f"Error parsing user {user[0]}: {e}")
                    continue

            # Update stats
            self.total_unpaid_text.value = str(len(self.unpaid_residents))
            self.total_amount_text.value = f"₱ {total_outstanding:,}"
            
            # Update List
            self.payment_list.controls.clear()
            
            if not self.unpaid_residents:
                self.payment_list.controls.append(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=64, color=ft.Colors.GREEN_300),
                                ft.Text("No overdue payments!", color=ft.Colors.GREY_400)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        margin=ft.margin.only(top=50)
                    )
                )
            else:
                for r in self.unpaid_residents:
                    # Get the earliest due date
                    earliest_date = "N/A"
                    if r["dues"]:
                        try:
                            # Sort dues by date to find oldest
                            sorted_dues = sorted(r["dues"], key=lambda x: x.get("date", 0))
                            ts = sorted_dues[0].get("date")
                            dt = datetime.fromtimestamp(int(ts))
                            earliest_date = dt.strftime("%b %d, %Y")
                        except:
                            pass

                    card = ft.Container(
                        ft.Row(
                            [
                                ft.Container(
                                    ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE, size=24),
                                    bgcolor="#ff3333",
                                    border_radius=7,
                                    width=36,
                                    height=36
                                ),
                                ft.Column(
                                    [
                                        ft.Text(r['username'], size=14, weight=ft.FontWeight.W_500),
                                        ft.Text(f"Room {r['room_id']}", size=11, color=ft.Colors.GREY_600),
                                    ],
                                    spacing=0,
                                    expand=True
                                ),
                                ft.Column(
                                    [
                                        ft.Text(f"₱ {r['total_due']:,}", size=14, weight=ft.FontWeight.BOLD, color="#b32424"),
                                        ft.Text(f"{r['unpaid_count']} month(s) overdue", size=10, color=ft.Colors.GREY_600),
                                    ],
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.END
                                ),
                                create_remark(f"Since {earliest_date}", "#b32424", "#ffe6e6")
                            ]
                        ),
                        padding=10,
                        border=ft.border.all(1.5, "#ffe6e6"),
                        border_radius=10
                    )
                    self.payment_list.controls.append(card)

            self.admin_page.page.update()

        except Exception as e:
            print(f"Error loading payment data: {e}")
            import traceback
            traceback.print_exc()
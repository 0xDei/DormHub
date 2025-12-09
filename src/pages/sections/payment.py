import flet as ft
from datetime import datetime
import json
import calendar

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark, create_banner

class Payment(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page

        header_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Payment Center", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.CREDIT_CARD_ROUNDED, size=24, color="#3BA9E6")
                    ],
                    spacing=3.5
                ),
                ft.Text("Manage your rent payments and view history", size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1,
            expand=True
        )

        add_button = ft.Container(
            ft.FilledButton(
                "Add Payment",
                icon=ft.Icons.ADD,
                icon_color=ft.Colors.WHITE,
                bgcolor="#FE9A00",
                color=ft.Colors.WHITE,
                elevation=0,
                width=140,
                height=30,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=7),
                    text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)
                ),
                on_click=self.show_add_payment
            )
        )

        header = ft.Row([header_content, add_button])

        if self.resident_page.data["room_id"] != "N/A":
            unpaid_count = len(self.resident_page.data.get("unpaid_dues", []))
            
            try:
                if unpaid_count == 0:
                    if self.resident_page.data["due_date"] != "N/A":
                        time = int(self.resident_page.data["due_date"])
                    else:
                        time = int(datetime.now().timestamp()) + 2629743  # 1 month from now
                else:
                    time = int(self.resident_page.data["unpaid_dues"][0]["date"])
                
                date = datetime.fromtimestamp(time)
                due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
            except:
                due_date = "Not Set"
                time = int(datetime.now().timestamp()) + 2629743
            
            card_title = ft.Text("Upcoming Payment", size=14, color="#feae33", weight=ft.FontWeight.BOLD)
            bgcolor = "#fff5e6"
            border_color = "#fec266"
            due_info = [
                ft.Text(f"₱ {self.resident_page.data.get('monthly_rent', 0):,}", size=18, weight=ft.FontWeight.W_700),
                ft.Text(due_date, size=12, color=ft.Colors.GREY_600)
            ]

            current_time = int(datetime.now().timestamp())

            if unpaid_count >= 1:
                card_title = ft.Text("Unpaid Due!", size=14, color="#ff3333", weight=ft.FontWeight.BOLD)
                status_icon = ft.Icon(ft.Icons.ERROR_ROUNDED, size=32, color="#ff3333")
                status_bgcolor = "#ffe6e6"
                bgcolor = "#ffe6e6"
                border_color = "#ff6666"
            elif (current_time + 86400) > time: # If due date is passed or today
                 # Simple check if current time > due time. 
                 # Adjust logic as needed. If strictly > due date is overdue.
                 pass

            next_due_card = ft.Container(
                ft.Row(
                    [
                        ft.Column(
                            [
                                card_title,
                                *due_info
                            ],
                            expand=True,
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(
                            ft.Icon(ft.Icons.ACCESS_TIME_FILLED_ROUNDED, size=32, color="#feae33"), # Default icon
                            bgcolor="#fff5e6",
                            border=ft.border.all(1.8, "#fec2c2"), # simplified
                            border_radius=7, 
                            width=32 * 1.5,
                            height=32 * 1.5
                        )
                    ]
                ),
                padding=ft.padding.only(left=20, right=20, top=18, bottom=20),
                height=110,
                bgcolor=bgcolor,
                border_radius=10,
                border=ft.border.all(2, border_color),
                expand=True
            )

            try:
                if self.resident_page.data["due_date"] != "N/A":
                    next_due_date = datetime.fromtimestamp(int(self.resident_page.data["due_date"]))
                    next_due_date_formatted = f"{next_due_date.strftime('%b')} {next_due_date.day}, {next_due_date.year}"
                else:
                    next_due_date_formatted = "Not Set"
            except:
                next_due_date_formatted = "Not Set"

            info_cards = ft.Row(
                [
                    create_info_card(
                        "Unpaid Payments", 
                        [
                            ft.Row([
                                ft.Text(str(unpaid_count), text_align=ft.TextAlign.CENTER, size=16),
                                ft.Text(f"x {self.resident_page.data.get('monthly_rent', 0):,}", size=12, color=ft.Colors.GREY_400)
                            ], spacing=3.5)
                        ],
                        ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#ff3333", size=28),
                        "left",
                        "#ffe6e6",
                        250,
                        90
                    ),
                    create_info_card(
                        "Next Due Date", 
                        [
                            ft.Text(next_due_date_formatted, text_align=ft.TextAlign.CENTER, size=16)
                        ],
                        ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color="#4D84FC", size=28),
                        "left",
                        "#DBEAFE",
                        250,
                        90
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                expand=True
            )

            ph_contents = []
            payment_history = self.resident_page.data.get("payment_history", [])
            
            for ph_info in payment_history[::-1]:
                if ph_info.get("remark") == "late":
                    leading_icon = ft.Container(
                        ft.Icon(ft.Icons.TIMER_OUTLINED, color="#DB805C", size=24),
                        bgcolor="#FFEDD4",
                        border_radius=7, 
                        width=24 * 1.5,
                        height=24 * 1.5
                    )
                    remark = create_remark("late", color="#DB805C", bgcolor="#FFEDD4")
                else:
                    leading_icon = ft.Container(
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="#00cc0a", size=24),
                        bgcolor="#b3ffb6",
                        border_radius=7, 
                        width=24 * 1.5,
                        height=24 * 1.5
                    )
                    remark = create_remark("on time", color="#00cc0a", bgcolor="#b3ffb6")

                try:
                    date = datetime.fromtimestamp(ph_info.get("date", int(datetime.now().timestamp())))
                    ph_contents.append(
                        ft.Container(
                            ft.Row(
                                [
                                    ft.Container(leading_icon),
                                    ft.Column(
                                        [
                                            ft.Text(f"{date.strftime('%b')} {date.year}", size=14, weight=ft.FontWeight.W_500),
                                            ft.Text(date.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500)
                                        ], spacing=0, expand=True
                                    ),
                                    remark,
                                    ft.Text(f"₱ {ph_info.get('amount', 0):,}", size=12, weight=ft.FontWeight.W_900)
                                ]
                            ),
                            padding=10,
                            border=ft.border.all(1.5, "#FEF3C6"),
                            border_radius=10
                        )
                    )
                except:
                    pass

            if len(ph_contents) == 0: 
                ph_contents.append(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=64, color=ft.Colors.GREY_300),
                                ft.Text("No payment history", size=16, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True, 
                        alignment=ft.alignment.center, 
                        margin=ft.margin.only(top=50)
                    )
                )

            history = ft.Container(
                ft.Column(
                    [
                        ft.Text("Payment History", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                        ft.ListView(ph_contents, expand=True, spacing=7)
                    ],
                    spacing=15
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                height=350,
                padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
                border=ft.border.all(2, "#FEF3C6")
            )

            up_contents = []
            unpaid_dues = self.resident_page.data.get("unpaid_dues", [])
            
            for up_info in unpaid_dues[::-1]:
                leading_icon = ft.Container(
                    ft.Icon(ft.Icons.MONEY_OFF_CSRED_ROUNDED, color="#b32424", size=24),
                    bgcolor="#ffc2c2",
                    border_radius=7, 
                    width=24 * 1.5,
                    height=24 * 1.5
                )

                try:
                    date = datetime.fromtimestamp(up_info.get("date", int(datetime.now().timestamp())))
                    up_contents.append(
                        ft.Container(
                            ft.Row(
                                [
                                    ft.Container(leading_icon),
                                    ft.Column(
                                        [
                                            ft.Text(f"{date.strftime('%b')} {date.year}", size=14, weight=ft.FontWeight.W_500),
                                            ft.Text(date.strftime("%m/%d/%Y"), size=10, color=ft.Colors.GREY_500)
                                        ], spacing=0, expand=True
                                    ),
                                    ft.Text(f"₱ {up_info.get('amount', 0):,}", size=12, weight=ft.FontWeight.W_900)
                                ]
                            ),
                            padding=10,
                            border=ft.border.all(1.5, "#cc2929"),
                            border_radius=10
                        )
                    )
                except:
                    pass

            if len(up_contents) == 0: 
                up_contents.append(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=64, color=ft.Colors.GREEN_300),
                                ft.Text("No unpaid payments", size=16, color=ft.Colors.GREEN_400, weight=ft.FontWeight.W_500)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True, 
                        alignment=ft.alignment.center, 
                        margin=ft.margin.only(top=50)
                    )
                )

            unpaid = ft.Container(
                ft.Column(
                    [
                        ft.Text("Unpaid Payments", color="#cc2929", size=14, weight=ft.FontWeight.W_500),
                        ft.ListView(up_contents, expand=True, spacing=7)
                    ],
                    spacing=15
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                height=350,
                padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
                border=ft.border.all(2, "#FEF3C6")
            )
        else:
            next_due_card = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.HOME_OUTLINED, size=64, color=ft.Colors.GREY_300),
                        ft.Text("No Room Assigned", size=18, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
                        ft.Text("Contact admin to get assigned to a room", size=12, color=ft.Colors.GREY_300)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                expand=True, 
                alignment=ft.alignment.center
            )
            info_cards = ft.Container()
            history = ft.Container()
            unpaid = ft.Container()

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            next_due_card,
                            info_cards,
                            history,
                            unpaid                     
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

    def add_months(self, sourcedate, months):
        """Adds months to a date, preserving day of month where possible."""
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second)

    async def show_add_payment(self, e):
        amount_tf = ft.TextField(
            label="Amount", 
            hint_text="Enter payment amount", 
            prefix_text="₱ ",
            border_radius=10, 
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string="")
        )

        popup = ft.AlertDialog(
            title=ft.Text("Add Payment"),
            content=ft.Container(
                ft.Column([amount_tf], tight=True),
                width=300
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.resident_page.page.close(popup)),
                ft.FilledButton("Pay", bgcolor="#FF6900", on_click=lambda e: self.resident_page.page.run_task(self.check_add_payment, amount_tf, popup))
            ]
        )
        self.resident_page.page.open(popup)

    async def check_add_payment(self, amount_tf, popup):
        if not amount_tf.value:
            amount_tf.error_text = "Please enter an amount"
            amount_tf.update()
            return
        
        try:
            amount = int(amount_tf.value)
            if amount <= 0:
                amount_tf.error_text = "Amount must be greater than 0"
                amount_tf.update()
                return
            
            # Fetch fresh data
            data = self.resident_page.data
            payment_history = data.get("payment_history", [])
            unpaid_dues = data.get("unpaid_dues", [])
            monthly_rent = data.get("monthly_rent", 0)
            
            # Add to history
            new_payment = {
                "date": int(datetime.now().timestamp()),
                "amount": amount,
                "remark": "on time"
            }
            payment_history.append(new_payment)
            
            # Pay off dues (oldest first)
            if unpaid_dues:
                new_payment["remark"] = "late"
                unpaid_dues.sort(key=lambda x: x.get("date", 0))
                remaining = amount
                new_unpaid = []
                for due in unpaid_dues:
                    if remaining <= 0:
                        new_unpaid.append(due)
                        continue
                    due_amt = due.get("amount", 0)
                    if remaining >= due_amt:
                        remaining -= due_amt
                    else:
                        due["amount"] = due_amt - remaining
                        remaining = 0
                        new_unpaid.append(due)
                data["unpaid_dues"] = new_unpaid

            if monthly_rent > 0:
                months_paid = amount // monthly_rent
                
                if months_paid >= 1 and data.get("due_date") != "N/A":
                    try:
                        current_due_ts = int(data["due_date"])
                        current_due_dt = datetime.fromtimestamp(current_due_ts)
                        
                        new_due_dt = self.add_months(current_due_dt, months_paid)
                        
                        data["due_date"] = str(int(new_due_dt.timestamp()))
                    except Exception as e:
                        print(f"Error updating due date: {e}")

            data["payment_history"] = payment_history
            
            # Save to DB
            await self.resident_page.page.data.update_user(
                self.resident_page.id, 
                self.resident_page.username, 
                self.resident_page.email, 
                self.resident_page.password, 
                data
            )
            
            self.resident_page.page.close(popup)
            create_banner(self.resident_page.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN), "Payment added successfully!", ft.Colors.GREEN)
            
            self.resident_page.page.run_task(self.resident_page.show_section, Payment(self.resident_page))

        except Exception as e:
            print(f"Error adding payment: {e}")
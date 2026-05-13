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
                ft.Text("Manage your rent and utility payments", size=12, weight=ft.FontWeight.W_500)
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
                # FIX 3: async on_click must be wrapped with run_task
                on_click=lambda e: self.resident_page.page.run_task(self.show_add_payment, e)
            )
        )

        header = ft.Row([header_content, add_button])

        # FIX 2: Always set self.content; show a "no room" state if not assigned
        if self.resident_page.data.get("room_id", "N/A") == "N/A":
            self.content = ft.Container(
                ft.Column(
                    [
                        header,
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Icon(ft.Icons.BED_OUTLINED, size=64, color="grey"),
                                    ft.Text("You are not assigned to a room yet.", color="grey", size=13),
                                    ft.Text("Contact your admin for room assignment.", color="grey", size=11)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=6
                            ),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ],
                    expand=True,
                    spacing=15
                ),
                expand=True,
                padding=10
            )
            return

        # ── Resident has a room ──────────────────────────────────────────────
        data = self.resident_page.data
        unpaid_dues = data.get("unpaid_dues", [])
        unpaid_count = len(unpaid_dues)

        # ── Rent due card ────────────────────────────────────────────────────
        try:
            if unpaid_count == 0:
                if data.get("due_date", "N/A") != "N/A":
                    time = int(data["due_date"])
                else:
                    time = int(datetime.now().timestamp()) + 2629743
            else:
                time = int(unpaid_dues[0]["date"])

            date = datetime.fromtimestamp(time)
            due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
        except:
            due_date = "Not Set"
            time = int(datetime.now().timestamp()) + 2629743

        card_title = ft.Text("Next Due Date", size=14, color="#feae33", weight=ft.FontWeight.BOLD)
        bgcolor = "#fff5e6"
        border_color = "#fec266"
        due_info = [
            ft.Text(f"₱ {data.get('monthly_rent', 0):,}", size=18, weight=ft.FontWeight.W_700),
            ft.Text(due_date, size=12, color=ft.Colors.GREY_600)
        ]

        if unpaid_count >= 1:
            card_title = ft.Text("Unpaid Balance Found!", size=14, color="#ff3333", weight=ft.FontWeight.BOLD)
            bgcolor = "#ffe6e6"
            border_color = "#ff6666"

        next_due_card = ft.Container(
            ft.Row(
                [
                    ft.Column(
                        [card_title, *due_info],
                        expand=True,
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        ft.Icon(ft.Icons.PAYMENT_ROUNDED, size=32, color="#feae33"),
                        bgcolor="#fff5e6",
                        border=ft.border.all(1.8, "#fec2c2"),
                        border_radius=7,
                        width=48, height=48, alignment=ft.alignment.center
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

        # ── Separate billing cards for Water and Electricity ─────────────────
        water_due = sum(d.get("amount", 0) for d in unpaid_dues if d.get("type") == "water")
        electricity_due = sum(d.get("amount", 0) for d in unpaid_dues if d.get("type") == "electricity")

        def billing_card(label, icon, amount, color, light):
            return ft.Container(
                ft.Row(
                    [
                        ft.Container(
                            ft.Icon(icon, size=24, color=color),
                            bgcolor=light,
                            border_radius=8,
                            width=42, height=42,
                            alignment=ft.alignment.center
                        ),
                        ft.Column(
                            [
                                ft.Text(label, size=11, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
                                ft.Text(
                                    f"₱ {amount:,}" if amount > 0 else "Paid / No Bill",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ff3333" if amount > 0 else "green"
                                )
                            ],
                            spacing=1, expand=True
                        )
                    ],
                    spacing=12
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.border.all(1.5, "#e0e0e0"),
                expand=True
            )

        billing_row = ft.Row(
            [
                billing_card("Water Bill", ft.Icons.WATER_DROP_ROUNDED, water_due, "#3BA9E6", "#e8f4fd"),
                billing_card("Electricity Bill", ft.Icons.BOLT_ROUNDED, electricity_due, "#FE9A00", "#fff5e6"),
            ],
            spacing=10
        )

        # ── Payment history ──────────────────────────────────────────────────
        # FIX 1: ph_contents was built but never wrapped in a widget called 'history'
        payment_history = data.get("payment_history", [])

        type_icons = {
            "rent":        (ft.Icons.HOME_ROUNDED,       "#FE9A00", "#fff5e6"),
            "water":       (ft.Icons.WATER_DROP_ROUNDED, "#3BA9E6", "#e8f4fd"),
            "electricity": (ft.Icons.BOLT_ROUNDED,       "#9C27B0", "#f3e5f5"),
        }
        method_colors = {
            "cash":      "#4CAF50",
            "gcash":     "#0077FF",
            "maya":      "#00B4D8",
            "maribank":  "#1A237E",
            "shopeepay": "#EE4D2D",
        }

        ph_contents = []
        for ph_info in payment_history[::-1]:
            pay_type   = ph_info.get("type",   "rent")
            pay_method = ph_info.get("method", "cash")
            icon, icon_color, icon_bg = type_icons.get(pay_type, (ft.Icons.RECEIPT_ROUNDED, "#888", "#eee"))
            badge_color = method_colors.get(pay_method, "#888")

            ts = ph_info.get("date", 0)
            try:
                d = datetime.fromtimestamp(ts)
                date_str = f"{d.strftime('%b')} {d.day}, {d.year}"
            except:
                date_str = "Unknown date"

            ph_contents.append(
                ft.Container(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(icon, size=20, color=icon_color),
                                bgcolor=icon_bg,
                                border_radius=8,
                                width=38, height=38,
                                alignment=ft.alignment.center
                            ),
                            ft.Column(
                                [
                                    ft.Text(f"{pay_type.upper()} Payment", size=13, weight=ft.FontWeight.W_600),
                                    ft.Row(
                                        [
                                            ft.Container(
                                                ft.Text(pay_method.upper(), size=9, color="white", weight=ft.FontWeight.BOLD),
                                                bgcolor=badge_color,
                                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                border_radius=4
                                            ),
                                            ft.Text(date_str, size=10, color=ft.Colors.GREY_500)
                                        ],
                                        spacing=6
                                    )
                                ],
                                spacing=2, expand=True
                            ),
                            ft.Text(f"₱ {ph_info.get('amount', 0):,}", size=13, weight=ft.FontWeight.W_900)
                        ],
                        spacing=10
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    border=ft.border.all(1.5, "#F0F0F0"),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE
                )
            )

        if not ph_contents:
            ph_contents.append(
                ft.Container(
                    ft.Text("No payment history yet.", color="grey", size=12),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )

        # FIX 1: Properly build 'history' widget from ph_contents
        history = ft.Container(
            ft.Column(
                [
                    ft.Text("Payment History", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    ft.Column(ph_contents, spacing=8)
                ],
                spacing=10
            ),
            padding=ft.padding.only(top=5)
        )

        self.content = ft.Container(
            ft.Column(
                [
                    header,
                    ft.ListView(
                        [next_due_card, ft.Container(height=8), billing_row, ft.Container(height=4), history],
                        spacing=10,
                        padding=ft.padding.only(bottom=20),
                        expand=True
                    )
                ],
                spacing=15,
                expand=True
            ),
            expand=True,
            padding=10
        )

    async def show_add_payment(self, e):
        type_dd = ft.Dropdown(
            label="Payment For",
            options=[
                ft.dropdown.Option("rent",        "Monthly Rent"),
                ft.dropdown.Option("water",       "Water Bill"),
                ft.dropdown.Option("electricity", "Electricity Bill"),
            ],
            value="rent"
        )

        # E-wallet options added; no real integration — UI only
        method_dd = ft.Dropdown(
            label="Payment Method",
            options=[
                ft.dropdown.Option("cash",      "Cash"),
                ft.dropdown.Option("gcash",     "GCash"),
                ft.dropdown.Option("maya",      "Maya (PayMaya)"),
                ft.dropdown.Option("maribank",  "Maribank"),
            ],
            value="cash"
        )

        # FIX 4: Add input_filter so only digits are accepted
        amount_tf = ft.TextField(
            label="Amount",
            prefix_text="₱ ",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(r'^[0-9]*$')
        )

        ewallet_note = ft.Container(
            ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color="#3BA9E6"),
                    ft.Text("E-wallet payments are recorded manually for now.", size=10, color=ft.Colors.GREY_600, expand=True)
                ],
                spacing=6
            ),
            padding=ft.padding.only(top=4)
        )

        popup = ft.AlertDialog(
            title=ft.Text("Add Payment"),
            content=ft.Container(
                ft.Column([type_dd, method_dd, amount_tf, ewallet_note], tight=True, spacing=10),
                width=380
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.resident_page.page.close(popup)),
                ft.FilledButton(
                    "Confirm Payment",
                    bgcolor="#FF6900",
                    on_click=lambda e: self.resident_page.page.run_task(
                        self.check_add_payment, amount_tf, type_dd, method_dd, popup
                    )
                )
            ]
        )
        self.resident_page.page.open(popup)

    async def check_add_payment(self, amount_tf, type_dd, method_dd, popup):
        if not amount_tf.value or not amount_tf.value.strip():
            amount_tf.error_text = "Please enter an amount"
            amount_tf.update()
            return

        try:
            amount = int(amount_tf.value)
            if amount < 1:
                raise ValueError
        except ValueError:
            amount_tf.error_text = "Enter a valid amount"
            amount_tf.update()
            return

        data = self.resident_page.data

        new_payment = {
            "date":   int(datetime.now().timestamp()),
            "amount": amount,
            "type":   type_dd.value,
            "method": method_dd.value,
            "remark": "on time"
        }

        data.setdefault("payment_history", []).append(new_payment)

        # Clear matching unpaid dues for the selected payment type
        unpaid_dues = data.get("unpaid_dues", [])
        remaining = amount
        new_unpaid = []
        for due in unpaid_dues:
            if due.get("type", "rent") == type_dd.value and remaining > 0:
                due_amt = due.get("amount", 0)
                if remaining >= due_amt:
                    remaining -= due_amt
                    continue
                else:
                    due["amount"] = due_amt - remaining
                    remaining = 0
            new_unpaid.append(due)
        data["unpaid_dues"] = new_unpaid

        try:
            await self.resident_page.page.data.update_user(
                self.resident_page.id,
                self.resident_page.username,
                self.resident_page.email,
                self.resident_page.password,
                data
            )
            self.resident_page.page.close(popup)
            create_banner(
                self.resident_page.page,
                ft.Colors.GREEN_100,
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="green"),
                "Payment recorded successfully!",
                "green"
            )
            self.resident_page.page.run_task(self.resident_page.show_section, Payment(self.resident_page))
        except Exception as ex:
            print(f"Error saving payment: {ex}")
            amount_tf.error_text = "Failed to save. Please try again."
            amount_tf.update()
import flet as ft
import json
from datetime import datetime
import math
import calendar

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark, create_banner

class AdminPayment(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.payment_data_list = [] # Store processed data for sorting

        # Header with Record Payment Button
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
                ),
                ft.Container(
                    ft.FilledButton(
                        "Record Payment",
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.WHITE,
                        bgcolor="#FE9A00",
                        color=ft.Colors.WHITE,
                        elevation=0,
                        width=160,
                        height=30,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=7),
                            text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)
                        ),
                        on_click=self.show_record_payment_dialog
                    )
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
            
            residents_with_dues = 0
            total_outstanding_amount = 0
            current_ts = datetime.now().timestamp()

            for user in users:
                try:
                    user_data = json.loads(user[4])
                    room_id = user_data.get("room_id", "N/A")
                    if room_id == "N/A": continue

                    unpaid_dues = user_data.get("unpaid_dues", [])
                    user_outstanding = sum(item.get('amount', 0) for item in unpaid_dues)
                    
                    if user_outstanding > 0:
                        residents_with_dues += 1
                        total_outstanding_amount += user_outstanding

                    due_date_str = user_data.get("due_date", "N/A")
                    days_remaining = 9999
                    due_date_display = "Not Set"
                    
                    if due_date_str != "N/A":
                        try:
                            due_ts = int(due_date_str)
                            dt = datetime.fromtimestamp(due_ts)
                            due_date_display = dt.strftime("%b %d, %Y")
                            diff_seconds = due_ts - current_ts
                            days_remaining = math.ceil(diff_seconds / (24 * 3600))
                        except: pass

                    self.payment_data_list.append({
                        "username": user[1],
                        "room_id": room_id,
                        "monthly_rent": user_data.get("monthly_rent", 0),
                        "outstanding": user_outstanding,
                        "due_date_display": due_date_display,
                        "days_remaining": days_remaining
                    })

                except Exception as e:
                    continue

            self.total_unpaid_text.value = str(residents_with_dues)
            self.total_amount_text.value = f"₱ {total_outstanding_amount:,}"
            self.payment_data_list.sort(key=lambda x: x['days_remaining'])

            self.payment_list.controls.clear()
            
            if not self.payment_data_list:
                self.payment_list.controls.append(
                    ft.Container(ft.Text("No residents with assigned rooms found.", color=ft.Colors.GREY_400), alignment=ft.alignment.center, expand=True, margin=ft.margin.only(top=50))
                )
            else:
                for item in self.payment_data_list:
                    days = item['days_remaining']
                    if days < 0:
                        status_text = f"Overdue by {abs(days)} day(s)"
                        status_color = "#D66875"; bg_color = "#FFE2E2"; icon = ft.Icons.WARNING_ROUNDED
                    elif days == 0:
                        status_text = "Due Today"
                        status_color = "#E18526"; bg_color = "#FFEDD4"; icon = ft.Icons.ACCESS_TIME_FILLED
                    elif days <= 7:
                        status_text = f"Due in {days} day(s)"
                        status_color = "#E18526"; bg_color = "#FFEDD4"; icon = ft.Icons.ACCESS_TIME
                    else:
                        status_text = f"Due in {days} days"
                        status_color = "#00cc0a"; bg_color = "#b3ffb6"; icon = ft.Icons.CALENDAR_MONTH

                    if item['due_date_display'] == "Not Set":
                        status_text = "Date Not Set"; status_color = ft.Colors.GREY_500; bg_color = ft.Colors.GREY_100; icon = ft.Icons.HELP_OUTLINE

                    card = ft.Container(
                        ft.Row([
                            ft.Container(ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=20), bgcolor=status_color if item['due_date_display'] != "Not Set" else ft.Colors.GREY_400, border_radius=7, width=36, height=36, alignment=ft.alignment.center),
                            ft.Column([ft.Text(item['username'], size=14, weight=ft.FontWeight.W_600), ft.Text(f"Room {item['room_id']}", size=11, color=ft.Colors.GREY_600)], spacing=0, expand=True),
                            ft.Column([ft.Text(f"₱ {item['outstanding']:,}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED) if item['outstanding'] > 0 else ft.Container()], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Column([ft.Row([ft.Text(status_text, size=12, color=status_color, weight=ft.FontWeight.BOLD), ft.Icon(icon, size=14, color=status_color)], spacing=5, alignment=ft.MainAxisAlignment.END), ft.Text(f"Due: {item['due_date_display']}", size=10, color=ft.Colors.GREY_500)], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10, border=ft.border.all(1, bg_color), border_radius=10, bgcolor=ft.Colors.WHITE
                    )
                    self.payment_list.controls.append(card)

            self.admin_page.page.update()

        except Exception as e:
            print(f"Error loading payment data: {e}")

    async def show_record_payment_dialog(self, e):
        users = await self.admin_page.page.data.get_all_users()
        resident_options = []
        for user in users:
            try:
                data = json.loads(user[4])
                if data.get("room_id", "N/A") != "N/A":
                    resident_options.append(ft.dropdown.Option(key=str(user[0]), text=f"{user[1]} (Room {data['room_id']})"))
            except: pass
            
        if not resident_options:
            create_banner(self.admin_page.page, ft.Colors.RED_100, ft.Icon(ft.Icons.ERROR, color="red"), "No residents with assigned rooms found.", ft.Colors.RED)
            return

        resident_dd = ft.Dropdown(label="Select Resident", options=resident_options, border_radius=10, width=300)
        amount_tf = ft.TextField(label="Amount", hint_text="Enter amount", prefix_text="₱ ", border_radius=10, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string=""), width=300)

        popup = ft.AlertDialog(
            title=ft.Text("Record Resident Payment"),
            content=ft.Container(ft.Column([ft.Text("Select a resident:", size=12, color=ft.Colors.GREY_600), resident_dd, amount_tf], tight=True, spacing=15), width=350, padding=10),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Record Payment", bgcolor="#FF6900", on_click=lambda e: self.admin_page.page.run_task(self.process_payment, resident_dd, amount_tf, popup))
            ]
        )
        self.admin_page.page.open(popup)

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second)

    async def process_payment(self, resident_dd, amount_tf, popup):
        if not resident_dd.value:
            resident_dd.error_text = "Please select a resident"; resident_dd.update(); return
        if not amount_tf.value:
            amount_tf.error_text = "Please enter an amount"; amount_tf.update(); return
            
        user_id = int(resident_dd.value)
        amount = int(amount_tf.value)
        
        if amount <= 0:
            amount_tf.error_text = "Amount must be greater than 0"; amount_tf.update(); return

        try:
            user_res = await self.admin_page.page.data.get_user_by_id(user_id)
            if not user_res:
                self.admin_page.page.close(popup); return
            
            user = user_res[0]
            data = json.loads(user[4])
            payment_history = data.get("payment_history", [])
            unpaid_dues = data.get("unpaid_dues", [])
            monthly_rent = data.get("monthly_rent", 0)
            
            new_payment = {"date": int(datetime.now().timestamp()), "amount": amount, "remark": "admin recorded"}
            payment_history.append(new_payment)
            
            if unpaid_dues:
                unpaid_dues.sort(key=lambda x: x.get("date", 0))
                remaining = amount
                new_unpaid = []
                for due in unpaid_dues:
                    if remaining <= 0: new_unpaid.append(due); continue
                    due_amt = due.get("amount", 0)
                    if remaining >= due_amt: remaining -= due_amt
                    else: due["amount"] = due_amt - remaining; remaining = 0; new_unpaid.append(due)
                data["unpaid_dues"] = new_unpaid
            
            # Update Due Date logic
            if monthly_rent > 0:
                months_paid = amount // monthly_rent
                if months_paid >= 1 and data.get("due_date") != "N/A":
                    try:
                        current_due_dt = datetime.fromtimestamp(int(data["due_date"]))
                        new_due_dt = self.add_months(current_due_dt, months_paid)
                        data["due_date"] = str(int(new_due_dt.timestamp()))
                    except: pass

            data["payment_history"] = payment_history
            await self.admin_page.page.data.update_user(user[0], user[1], user[2], user[3], data)
            
            self.admin_page.page.close(popup)
            create_banner(self.admin_page.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color="green"), f"Payment recorded for {user[1]}!", ft.Colors.GREEN)
            await self.load_data()
            
        except Exception as e:
            print(f"Error processing payment: {e}")
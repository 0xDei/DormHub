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
        self.all_payment_records = [] # Store all processed data for fast local filtering

        # --- Search & Filter Controls ---
        self.search_field = ft.TextField(
            hint_text="Search resident...",
            prefix_icon=ft.Icons.SEARCH,
            height=40,
            content_padding=10,
            border_radius=10,
            bgcolor="#F3F3F5",
            border_width=0,
            expand=True,
            on_change=self.on_search_change
        )

        self.filter_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "All Status"),
                ft.dropdown.Option("overdue", "Overdue / Unpaid"),
                ft.dropdown.Option("paid", "Paid / Up-to-date"),
            ],
            value="all",
            dense=True, 
            content_padding=10,
            border_radius=10,
            bgcolor="#F3F3F5",
            border_width=0,
            width=160,
            on_change=self.on_filter_change
        )

        # --- Header ---
        header_top = ft.Row(
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
                        ft.Text("Track resident balances, revenue, and due dates", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
                ft.Container(
                    ft.FilledButton(
                        "Record Payment",
                        icon=ft.Icons.ADD_CARD_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        bgcolor="#FE9A00",
                        color=ft.Colors.WHITE,
                        elevation=0,
                        height=35,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)
                        ),
                        on_click=self.show_record_payment_dialog
                    )
                )
            ]
        )

        # --- Financial Stats ---
        self.revenue_text = ft.Text("₱ 0", size=20, weight=ft.FontWeight.BOLD)
        self.unpaid_text = ft.Text("₱ 0", size=20, weight=ft.FontWeight.BOLD)

        stats = ft.Row(
            [
                create_info_card(
                    "Revenue (This Month)",
                    [self.revenue_text],
                    ft.Icon(ft.Icons.ATTACH_MONEY, color="#14AD4E", size=28),
                    "left",
                    "#DBFCE7",
                    200,
                    87
                ),
                create_info_card(
                    "Total Unpaid Dues",
                    [self.unpaid_text],
                    ft.Icon(ft.Icons.MONEY_OFF_ROUNDED, color="#C28239", size=28),
                    "left",
                    "#FFE2E2",
                    200,
                    87
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        # --- List Area ---
        self.payment_list = ft.ListView(spacing=8, expand=True)

        list_container = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Resident Status", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row([self.search_field, self.filter_dropdown], spacing=10),
                    self.payment_list
                ],
                spacing=15,
                expand=True
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
                    header_top,
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

    def on_search_change(self, e):
        self.filter_data()

    def on_filter_change(self, e):
        self.filter_data()

    async def load_data(self):
        try:
            users = await self.admin_page.page.data.get_all_users()
            self.all_payment_records = []
            
            total_collected_month = 0
            total_outstanding_amount = 0
            
            now = datetime.now()
            start_of_month = datetime(now.year, now.month, 1).timestamp()
            current_ts = now.timestamp()

            for user in users:
                try:
                    user_data = json.loads(user[4])
                    room_id = user_data.get("room_id", "N/A")
                    
                    if room_id == "N/A": continue

                    # 1. Calculate Outstanding
                    unpaid_dues = user_data.get("unpaid_dues", [])
                    user_outstanding = sum(item.get('amount', 0) for item in unpaid_dues)
                    total_outstanding_amount += user_outstanding

                    # 2. Calculate Monthly Revenue (from history)
                    payment_history = user_data.get("payment_history", [])
                    for pay in payment_history:
                        if pay.get('date', 0) >= start_of_month:
                            total_collected_month += pay.get('amount', 0)

                    # 3. Calculate Next Due Date
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

                    self.all_payment_records.append({
                        "id": user[0],
                        "username": user[1],
                        "email": user[2],
                        "room_id": room_id,
                        "outstanding": user_outstanding,
                        "due_date_display": due_date_display,
                        "days_remaining": days_remaining,
                        "payment_history": payment_history
                    })

                except Exception as e:
                    print(f"Error parsing user {user[0]}: {e}")
                    continue

            # Update Stats UI
            self.revenue_text.value = f"₱ {total_collected_month:,}"
            self.unpaid_text.value = f"₱ {total_outstanding_amount:,}"
            
            self.revenue_text.update()
            self.unpaid_text.update()

            self.filter_data() 

        except Exception as e:
            print(f"Error loading payment data: {e}")

    def filter_data(self):
        search_query = self.search_field.value.lower() if self.search_field.value else ""
        filter_type = self.filter_dropdown.value

        filtered_list = []
        for item in self.all_payment_records:
            # Search Filter
            if search_query and search_query not in item['username'].lower() and search_query not in f"room {item['room_id']}".lower():
                continue
            
            # Category Filter
            if filter_type == "overdue":
                if item['outstanding'] == 0: continue
            elif filter_type == "paid":
                if item['outstanding'] > 0: continue
            
            filtered_list.append(item)

        # Sort: Residents with outstanding dues FIRST, then by due date urgency
        filtered_list.sort(key=lambda x: (-x['outstanding'], x['days_remaining']))

        self.display_list(filtered_list)

    def display_list(self, records):
        self.payment_list.controls.clear()
        
        if not records:
            self.payment_list.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=48, color=ft.Colors.GREY_300),
                        ft.Text("No records found.", color=ft.Colors.GREY_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True,
                    margin=ft.margin.only(top=50)
                )
            )
            self.admin_page.page.update()
            return

        for item in records:
            days = item['days_remaining']
            outstanding = item['outstanding']
            
            # --- Styling Logic (No badges, just colors/text) ---
            if outstanding > 0:
                status_text = "Overdue Balance"
                status_color = "#D66875" # Red
                bg_color = "#FFE2E2"
                icon_bg = "#D66875"
                card_border_color = "#ffc2c2"
            else:
                status_text = "Up to Date"
                status_color = ft.Colors.GREY_500
                bg_color = ft.Colors.WHITE
                icon_bg = "#FF6900"
                card_border_color = "#FEF3C6"
                
            # --- Due Date Text Logic ---
            due_text_color = ft.Colors.GREY_600
            due_icon = ft.Icons.CALENDAR_MONTH
            
            if item['due_date_display'] == "Not Set":
                time_status = "Date Not Set"
            elif outstanding > 0:
                 if days < 0:
                    time_status = f"Overdue by {abs(days)} day(s)"
                    due_text_color = "#D66875"
                 else:
                     time_status = "Payment Due Now"
            elif days == 0:
                time_status = "Due Today"
                due_text_color = "#E18526"
                due_icon = ft.Icons.ACCESS_TIME_FILLED
            elif days <= 7:
                time_status = f"Due in {days} day(s)"
                due_text_color = "#E18526"
                due_icon = ft.Icons.ACCESS_TIME
            else:
                time_status = f"Due in {days} days"
                due_text_color = "#00cc0a"

            # --- Card Construction ---
            card = ft.Container(
                ft.Row(
                    [
                        # Left: Icon & User Info
                        ft.Row([
                            ft.Container(
                                ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=24),
                                bgcolor=icon_bg,
                                border_radius=10,
                                width=45, height=45,
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Text(item['username'], size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Room {item['room_id']}", size=12, color=ft.Colors.GREY_600),
                            ], spacing=2)
                        ]),

                        # Right: Financials & Actions
                        ft.Row([
                             # Outstanding Amount (if any)
                            ft.Column(
                                [
                                    ft.Text(f"₱ {outstanding:,}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED) if outstanding > 0 else ft.Container(),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            
                            # Due Date
                            ft.Column([
                                ft.Row([ft.Text(time_status, size=11, color=due_text_color, weight=ft.FontWeight.W_600)], alignment=ft.MainAxisAlignment.END),
                                ft.Row([ft.Icon(due_icon, size=12, color=ft.Colors.GREY_500), ft.Text(f"Due: {item['due_date_display']}", size=11, color=ft.Colors.GREY_500)], alignment=ft.MainAxisAlignment.END, spacing=3)
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
                            
                            # Buttons
                            ft.IconButton(
                                icon=ft.Icons.EMAIL_OUTLINED,
                                tooltip="Email Reminder",
                                icon_color=ft.Colors.BLUE_600,
                                on_click=lambda e, email=item['email']: self.page.launch_url(f"mailto:{email}")
                            ),
                            ft.IconButton(
                                icon=ft.Icons.HISTORY,
                                tooltip="View History",
                                icon_color=ft.Colors.GREY_700,
                                on_click=lambda e, r=item: self.admin_page.page.run_task(self.show_history_dialog, r)
                            )
                        
                        ], spacing=15, alignment=ft.MainAxisAlignment.END, expand=True)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=12,
                border=ft.border.all(1, card_border_color),
                border_radius=10,
                bgcolor=ft.Colors.WHITE
            )
            self.payment_list.controls.append(card)

        self.admin_page.page.update()

    async def show_history_dialog(self, record):
        history_items = []
        
        sorted_history = sorted(record['payment_history'], key=lambda x: x.get('date', 0), reverse=True)
        total_paid_lifetime = sum(p.get('amount', 0) for p in sorted_history)

        if not sorted_history:
            history_items.append(ft.Container(ft.Text("No payment history available.", color=ft.Colors.GREY_500), padding=20, alignment=ft.alignment.center))
        else:
            for payment in sorted_history:
                try:
                    dt = datetime.fromtimestamp(payment['date'])
                    date_str = dt.strftime("%b %d, %Y - %I:%M %p")
                    amount_str = f"₱ {payment['amount']:,}"
                    remark = payment.get('remark', 'payment').upper()
                    
                    history_items.append(
                        ft.Container(
                            ft.Row([
                                ft.Column([
                                    ft.Text(date_str, weight=ft.FontWeight.W_600, size=13),
                                    ft.Text(remark, size=10, color=ft.Colors.GREY_500)
                                ]),
                                ft.Text(f"+ {amount_str}", color="green", weight="bold", size=14)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=10,
                            border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
                        )
                    )
                except: pass

        dlg = ft.AlertDialog(
            title=ft.Text(f"History: {record['username']}"),
            content=ft.Container(
                ft.Column(
                    [
                        ft.Container(
                            ft.Row([ft.Text("Total Lifetime Paid:", size=12), ft.Text(f"₱ {total_paid_lifetime:,}", weight="bold", color="green")], alignment="spaceBetween"),
                            padding=ft.padding.only(bottom=10)
                        ),
                        ft.Divider(height=1),
                        ft.Column(history_items, scroll=ft.ScrollMode.AUTO, expand=True)
                    ], 
                    spacing=5
                ),
                width=350,
                height=400,
                bgcolor=ft.Colors.WHITE,
                border_radius=10
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.admin_page.page.close(dlg))]
        )
        self.admin_page.page.open(dlg)

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
        amount_tf = ft.TextField(label="Payment Amount", prefix_text="₱ ", border_radius=10, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string=""), width=300)

        popup = ft.AlertDialog(
            title=ft.Text("Record Payment"),
            content=ft.Container(ft.Column([
                ft.Text("Add a payment manually for a resident.", size=12, color=ft.Colors.GREY_600),
                resident_dd, amount_tf
            ], tight=True, spacing=15), width=350, padding=10),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Submit Payment", bgcolor="#FF6900", on_click=lambda e: self.admin_page.page.run_task(self.process_payment, resident_dd, amount_tf, popup))
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
            resident_dd.error_text = "Required"; resident_dd.update(); return
        if not amount_tf.value:
            amount_tf.error_text = "Required"; amount_tf.update(); return
            
        user_id = int(resident_dd.value)
        amount = int(amount_tf.value)
        
        if amount <= 0:
            amount_tf.error_text = "Must be > 0"; amount_tf.update(); return

        try:
            user_res = await self.admin_page.page.data.get_user_by_id(user_id)
            if not user_res: self.admin_page.page.close(popup); return
            
            user = user_res[0]
            data = json.loads(user[4])
            payment_history = data.get("payment_history", [])
            unpaid_dues = data.get("unpaid_dues", [])
            monthly_rent = data.get("monthly_rent", 0)
            
            # Record Payment
            new_payment = {"date": int(datetime.now().timestamp()), "amount": amount, "remark": "Admin Recorded"}
            payment_history.append(new_payment)
            
            # Clear Dues
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
            
            # Advance Due Date
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
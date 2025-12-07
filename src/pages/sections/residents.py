import flet as ft
import json
import calendar
from datetime import datetime
import math

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_remark, create_banner

class Residents(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.page = admin_page.page
        self.all_residents = []

        # Search field
        self.search_field = ft.TextField(
            hint_text="Search by name or email...",
            hint_style=ft.TextStyle(color="#B8B8C1"),
            border_radius=10,
            border_width=0,
            bgcolor="#F3F3F5",
            prefix_icon=ft.Icon(ft.Icons.SEARCH, color="#B8B8C1"),
            width=300,
            on_change=self.on_search_change
        )

        # Room filter
        self.room_filter = ft.Dropdown(
            hint_text="Filter by room",
            options=[
                ft.dropdown.Option("all", "All Rooms"),
                ft.dropdown.Option("assigned", "Assigned"),
                ft.dropdown.Option("unassigned", "Unassigned"),
            ],
            value="all",
            border_radius=10,
            bgcolor="#F3F3F5",
            border_width=0,
            width=150,
            on_change=self.on_filter_change
        )

        # Header
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Residents Management", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                                ft.Icon(ft.Icons.PEOPLE_OUTLINE_ROUNDED, size=24, color=ft.Colors.GREY_500)
                            ],
                            spacing=3.5,
                        ),
                        ft.Text("Manage resident accounts and room assignments", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
                ft.Container(
                    ft.FilledButton(
                        "Add Resident", 
                        icon=ft.Icons.PERSON_ADD_ALT_1_ROUNDED, 
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
                        on_click=self.show_add_resident
                    )
                )
            ]
        )

        # Stats
        self.total_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
        self.assigned_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
        self.unassigned_text = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)

        stats = ft.Row(
            [
                create_info_card(
                    "Total Residents",
                    [self.total_text],
                    ft.Icon(ft.Icons.PEOPLE_ROUNDED, color="#4D84FC", size=28),
                    "left",
                    "#DBEAFE",
                    200,
                    87
                ),
                create_info_card(
                    "Assigned",
                    [self.assigned_text],
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="#00cc0a", size=28),
                    "left",
                    "#b3ffb6",
                    200,
                    87
                ),
                create_info_card(
                    "Unassigned",
                    [self.unassigned_text],
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#C28239", size=28),
                    "left",
                    "#FEF9C3",
                    200,
                    87
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        # Residents list
        self.residents_list = ft.ListView(spacing=7, expand=True)

        residents_container = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("All Residents", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                            ft.Row([self.search_field, self.room_filter], spacing=10)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.residents_list
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
                        [stats, residents_container],
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
        self.page.run_task(self.load_data)

    def on_search_change(self, e):
        self.page.run_task(self.filter_residents)

    def on_filter_change(self, e):
        self.page.run_task(self.filter_residents)

    def show_add_resident(self, e):
        self.page.run_task(self.show_add_dialog)

    # Helper for accurate date calculation
    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second)

    async def load_data(self):
        try:
            users = await self.page.data.get_all_users()
            self.all_residents = []
            
            for user in users:
                data = json.loads(user[4])
                self.all_residents.append({
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "password": user[3],
                    "room_id": data.get("room_id", "N/A"),
                    "phone": data.get("phone_number", "N/A"),
                    "due_date": data.get("due_date", "N/A"),
                    "data": data
                })

            await self.update_stats()
            # Initial sort and display
            await self.filter_residents()
        except Exception as e:
            print(f"Error: {e}")

    async def update_stats(self):
        total = len(self.all_residents)
        assigned = sum(1 for r in self.all_residents if r["room_id"] != "N/A")
        
        self.total_text.value = str(total)
        self.assigned_text.value = str(assigned)
        self.unassigned_text.value = str(total - assigned)
        self.page.update()

    async def display_residents(self, residents):
        self.residents_list.controls.clear()

        if not residents:
            self.residents_list.controls.append(
                ft.Container(
                    ft.Text("No residents found", color=ft.Colors.GREY_400),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            for r in residents:
                # Room Badge
                badge = create_remark(
                    f"Room {r['room_id']}" if r['room_id'] != "N/A" else "Unassigned",
                    "#00cc0a" if r['room_id'] != "N/A" else "#808899",
                    "#b3ffb6" if r['room_id'] != "N/A" else "#F3F4F6"
                )

                card = ft.Container(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE, size=24),
                                bgcolor="#FF6900",
                                border_radius=7,
                                width=36,
                                height=36
                            ),
                            ft.Column(
                                [
                                    ft.Text(r['username'], size=14, weight=ft.FontWeight.W_500),
                                    ft.Text(r['email'], size=11, color=ft.Colors.GREY_600),
                                ],
                                spacing=0,
                                expand=True
                            ),
                            badge,
                            # Phone Button
                            ft.IconButton(
                                icon=ft.Icons.PHONE_OUTLINED,
                                icon_color=ft.Colors.GREEN_600,
                                tooltip="Call/Text" if r['phone'] != "N/A" else "No phone number",
                                disabled=r['phone'] == "N/A",
                                on_click=lambda e, phone=r['phone']: self.page.launch_url(f"tel:{phone}")
                            ),
                            # Email Button
                            ft.IconButton(
                                icon=ft.Icons.EMAIL_OUTLINED,
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Send Email",
                                on_click=lambda e, email=r['email']: self.page.launch_url(f"mailto:{email}")
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_color="#4D84FC",
                                on_click=lambda e, res=r: self.page.run_task(self.show_edit_dialog, res)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color="#D66875",
                                on_click=lambda e, res=r: self.page.run_task(self.show_delete_dialog, res)
                            ),
                        ]
                    ),
                    padding=10,
                    border=ft.border.all(1.5, "#FEF3C6"),
                    border_radius=10
                )
                self.residents_list.controls.append(card)

        self.page.update()

    async def filter_residents(self):
        query = (self.search_field.value or "").lower()
        filter_val = self.room_filter.value

        filtered = []
        for r in self.all_residents:
            if query and query not in r['username'].lower() and query not in r['email'].lower():
                continue
            if filter_val == "assigned" and r['room_id'] == "N/A":
                continue
            if filter_val == "unassigned" and r['room_id'] != "N/A":
                continue
            filtered.append(r)

        await self.display_residents(filtered)

    async def show_add_dialog(self):
        username_f = ft.TextField(label="Username", border_radius=10)
        email_f = ft.TextField(label="Email", border_radius=10)
        password_f = ft.TextField(label="Password", border_radius=10, password=True, can_reveal_password=True)
        phone_f = ft.TextField(label="Phone", border_radius=10)

        # Date Picker for Move-in Date
        selected_date = [None]
        
        def on_date_change(e):
            if date_picker.value:
                selected_date[0] = date_picker.value
                date_button.text = date_picker.value.strftime("%b %d, %Y")
                date_button.update()

        date_picker = ft.DatePicker(
            on_change=on_date_change,
        )
        
        # Use page.open() to prevent "has no attribute 'pick_date'" error
        date_button = ft.ElevatedButton(
            "Select Move-in Date",
            icon=ft.Icons.CALENDAR_MONTH,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                color=ft.Colors.BLACK,
                bgcolor="#F3F3F5",
                elevation=0
            ),
            width=290,
            height=45,
            on_click=lambda _: self.page.open(date_picker)
        )

        async def add_action(e):
            try:
                if not username_f.value or not email_f.value or not password_f.value:
                    return

                await self.page.data.create_user(
                    username_f.value.strip(),
                    email_f.value.strip(),
                    password_f.value,
                    phone_f.value.strip() if phone_f.value else "N/A"
                )

                # Update phone and dates if provided
                user = await self.page.data.get_user_by_email(email_f.value.strip())
                if user:
                    data = json.loads(user[0][4])
                    
                    if selected_date[0]:
                        move_in_dt = selected_date[0]
                        ts = int(move_in_dt.timestamp())
                        data["move_in_date"] = str(ts)
                        
                        # Calculate exact one month later for first payment
                        new_due_dt = self.add_months(move_in_dt, 1)
                        data["due_date"] = str(int(new_due_dt.timestamp()))

                    await self.page.data.update_user(user[0][0], user[0][1], user[0][2], user[0][3], data)

                self.page.close(dlg)
                create_banner(self.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN), "Resident added!", ft.Colors.GREEN)
                await self.load_data()
            except Exception as e:
                print(f"Error: {e}")

        dlg = ft.AlertDialog(
            title=ft.Text("Add Resident"),
            content=ft.Column(
                [
                    username_f, 
                    email_f, 
                    password_f, 
                    phone_f,
                    ft.Text("Move-in Date", size=12, color=ft.Colors.GREY_600),
                    date_button
                ], 
                tight=True, 
                spacing=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.FilledButton("Add", bgcolor="#FF6900", on_click=lambda e: self.page.run_task(add_action, e))
            ]
        )
        self.page.open(dlg)

    async def show_edit_dialog(self, resident):
        username_f = ft.TextField(label="Username", value=resident['username'], border_radius=10)
        email_f = ft.TextField(label="Email", value=resident['email'], border_radius=10)
        phone_f = ft.TextField(label="Phone", value=resident['phone'], border_radius=10)

        rooms = await self.page.data.get_all_rooms()
        room_opts = [ft.dropdown.Option("N/A", "No Room")]
        for room in rooms:
            room_opts.append(ft.dropdown.Option(str(room[0]), f"Room {room[0]}"))

        room_dd = ft.Dropdown(
            label="Room",
            value=str(resident['room_id']),
            options=room_opts,
            border_radius=10
        )

        # Date Picker for Move-in Date
        current_ts = resident['data'].get("move_in_date", "N/A")
        initial_date = None
        button_text = "Select Move-in Date"
        selected_date = [None]

        if current_ts != "N/A":
            try:
                initial_date = datetime.fromtimestamp(int(current_ts))
                button_text = initial_date.strftime("%b %d, %Y")
                selected_date[0] = initial_date
            except:
                pass

        def on_date_change(e):
            if date_picker.value:
                selected_date[0] = date_picker.value
                date_button.text = date_picker.value.strftime("%b %d, %Y")
                date_button.update()

        date_picker = ft.DatePicker(
            value=initial_date,
            on_change=on_date_change,
        )

        date_button = ft.ElevatedButton(
            button_text,
            icon=ft.Icons.CALENDAR_MONTH,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                color=ft.Colors.BLACK,
                bgcolor="#F3F3F5",
                elevation=0
            ),
            width=290,
            height=45,
            on_click=lambda _: self.page.open(date_picker)
        )

        async def update_action(e):
            try:
                data = resident['data'].copy()
                data['phone_number'] = phone_f.value.strip() if phone_f.value else "N/A"
                data['room_id'] = room_dd.value if room_dd.value != "N/A" else "N/A"
                
                if selected_date[0]:
                    move_in_dt = selected_date[0]
                    ts = int(move_in_dt.timestamp())
                    data['move_in_date'] = str(ts)
                    # Set Next Due Date to 1 month after move-in
                    new_due_dt = self.add_months(move_in_dt, 1)
                    data['due_date'] = str(int(new_due_dt.timestamp()))

                await self.page.data.update_user(
                    resident['id'],
                    username_f.value.strip(),
                    email_f.value.strip(),
                    resident['password'],
                    data
                )

                self.page.close(dlg)
                create_banner(self.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN), "Resident updated!", ft.Colors.GREEN)
                await self.load_data()
            except Exception as e:
                print(f"Error: {e}")

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Resident"),
            content=ft.Column(
                [
                    username_f, 
                    email_f, 
                    phone_f, 
                    room_dd,
                    ft.Text("Move-in Date", size=12, color=ft.Colors.GREY_600),
                    date_button
                ], 
                tight=True, 
                spacing=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.FilledButton("Update", bgcolor="#FF6900", on_click=lambda e: self.page.run_task(update_action, e))
            ]
        )
        self.page.open(dlg)

    async def show_delete_dialog(self, resident):
        async def delete_action(e):
            try:
                await self.page.data.delete_user(resident['id'])
                self.page.close(dlg)
                create_banner(self.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN), "Resident deleted!", ft.Colors.GREEN)
                await self.load_data()
            except Exception as e:
                print(f"Error: {e}")

        dlg = ft.AlertDialog(
            title=ft.Text("Delete Resident"),
            content=ft.Text(f"Delete {resident['username']}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.FilledButton("Delete", bgcolor="#D66875", on_click=lambda e: self.page.run_task(delete_action, e))
            ]
        )
        self.page.open(dlg)
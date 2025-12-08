import flet as ft
from flet import FilePickerUploadFile
import json
import os, shutil

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_banner

class Rooms(Section):
    def __init__(self, admin_page):
        super().__init__()
        self.admin_page = admin_page
        
        self.rooms_list = ft.Column(spacing=15, expand=True)

        header = ft.Row(
            [
                ft.Column([
                    ft.Text("Room Management", color="#E78B28", size=16, weight="w500"),
                    ft.Text("Manage beds and room availability", size=12, weight="w500")
                ], spacing=1, expand=True),
                ft.FilledButton("Add Room", icon=ft.Icons.ADD, bgcolor="#FF6900", on_click=self.show_add_room)
            ]
        )

        self.content = ft.Container(
            ft.Column([header, ft.ListView([self.rooms_list], spacing=20, padding=ft.padding.only(bottom=20), expand=True)], spacing=15, expand=True),
            expand=True, padding=10
        )

        self.admin_page.page.run_task(self.load_rooms)

    async def load_rooms(self):
        try:
            self.rooms_list.controls.clear()
            
            # Fetch both Rooms and Users to calculate accurate status
            rooms_data = await self.admin_page.page.data.get_all_rooms()
            users_data = await self.admin_page.page.data.get_all_users()
            
            # Count residents per room
            room_occupancy = {}
            for user in users_data:
                try:
                    u_data = json.loads(user[4])
                    room_id = str(u_data.get("room_id", "N/A"))
                    if room_id != "N/A":
                        room_occupancy[room_id] = room_occupancy.get(room_id, 0) + 1
                except:
                    pass

            if not rooms_data:
                self.rooms_list.controls.append(
                    ft.Container(
                        ft.Column([
                            ft.Icon(ft.Icons.BED_OUTLINED, size=64, color="grey"),
                            ft.Text("No rooms available", color="grey")
                        ], horizontal_alignment="center"),
                        alignment=ft.alignment.center, padding=50
                    )
                )
            else:
                for r in rooms_data:
                    # Calculate dynamic status
                    room_id_str = str(r[0])
                    current_residents = room_occupancy.get(room_id_str, 0)
                    bed_count = r[3]
                    db_status = r[5]
                    
                    # Logic: Keep 'maintenance', otherwise calc based on occupancy
                    if db_status == "maintenance":
                        status = "maintenance"
                    elif current_residents >= bed_count:
                        status = "occupied"
                    else:
                        status = "available"

                    room = {
                        'id': r[0], 
                        'bed_count': bed_count, 
                        'monthly_rent': r[4], 
                        'status': status, 
                        'thumbnail': r[6],
                        'current_residents': current_residents # Store for display
                    }
                    self.rooms_list.controls.append(self.create_room_card(room))
            
            self.admin_page.page.update()
        except Exception as e: 
            print(f"Error loading rooms: {e}")

    def create_room_card(self, room):
        status_colors = {"available": "green", "occupied": "red", "maintenance": "orange"}
        color = status_colors.get(room['status'], "grey")
        
        thumb = f"assets/room_thumbnails/{room['thumbnail']}"
        if not os.path.exists(thumb): thumb = "assets/placeholder.jpg"
        
        # Display "X/Y Beds" instead of just "Y Beds"
        occupancy_text = f"{room['current_residents']}/{room['bed_count']} Beds"

        return ft.Card(
            ft.Container(
                ft.Row([
                    ft.Image(src=thumb, width=150, height=150, fit=ft.ImageFit.COVER, border_radius=10),
                    ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Text(f"Room #{room['id']}", size=18, weight="bold"),
                                ft.Container(ft.Text(room['status'].upper(), size=10, color="white", weight="bold"), bgcolor=color, padding=5, border_radius=5)
                            ], alignment="spaceBetween"),
                            
                            ft.Row([ft.Icon(ft.Icons.BED, size=16), ft.Text(occupancy_text)]),
                            ft.Row([ft.Icon(ft.Icons.PAYMENTS, size=16), ft.Text(f"₱ {room['monthly_rent']:,}")]),
                            
                            ft.Row([
                                ft.TextButton("Edit", icon=ft.Icons.EDIT, on_click=lambda e: self.admin_page.page.run_task(self.edit_room, room)),
                                ft.TextButton("Delete", icon=ft.Icons.DELETE, style=ft.ButtonStyle(color="red"), on_click=lambda e: self.admin_page.page.run_task(self.delete_room, room))
                            ], spacing=10)
                        ], spacing=10, expand=True),
                        padding=15, expand=True
                    )
                ], spacing=15),
                padding=10
            ),
            elevation=2
        )

    async def edit_room(self, room):
        async def on_result(e):
            if e.files: upload_pic.controls[0].value = e.files[0].path; self.admin_page.page.update()

        file_picker = ft.FilePicker(on_result=on_result)
        self.admin_page.page.overlay.append(file_picker)

        upload_pic = ft.Row([ft.TextField(room['thumbnail'], label="Select Thumbnail", disabled=True, expand=True), ft.ElevatedButton("Select", on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"]))], alignment="center")

        bed_count = ft.Dropdown(label="Bed Count", options=[ft.DropdownOption(i, str(i)) for i in range(1, 11)], value=room['bed_count'], expand=True)
        
        # Admin can force maintenance, but available/occupied are mostly auto-calculated. 
        # Providing option to set manual status override if needed.
        status = ft.Dropdown(label="Status Override", options=[ft.DropdownOption("available"), ft.DropdownOption("occupied"), ft.DropdownOption("maintenance")], value=room['status'], expand=True)

        monthly_rent = ft.TextField(label="Monthly Rent", prefix_text="₱ ", value=str(room['monthly_rent']), keyboard_type="number", input_filter=ft.InputFilter(r'^[0-9]*$'), expand=True)

        popup = ft.AlertDialog(
            title=ft.Text(f"Edit Room #{room['id']}"),
            content=ft.Container(ft.Column([upload_pic, ft.Row([status, bed_count]), monthly_rent], tight=True, spacing=20), width=450),
            actions=[
                ft.FilledButton("Cancel", style=ft.ButtonStyle(bgcolor="#E6E8EE", color="black"), on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Update Room", bgcolor="#FF6900", on_click=lambda e: self.admin_page.page.run_task(self.check_edit_room, room['id'], file_picker, status, bed_count, monthly_rent, popup, room['thumbnail']))
            ]
        )
        self.admin_page.page.open(popup)

    async def check_edit_room(self, room_id, file_picker, status, bed_count, monthly_rent, popup, current_thumbnail):
        if not monthly_rent.value or int(monthly_rent.value) < 1:
            monthly_rent.error_text = "Invalid Rent"; monthly_rent.update(); return

        file_name = current_thumbnail
        if file_picker.result and file_picker.result.files:
            f = file_picker.result.files[0]
            file_name = f.name
            os.makedirs("assets/room_thumbnails", exist_ok=True)
            shutil.copy2(f.path, f"assets/room_thumbnails/{file_name}")

        await self.admin_page.page.data.custom_query(
            "UPDATE rooms SET bed_count=%s, monthly_rent=%s, current_status=%s, thumbnail=%s WHERE id=%s",
            (int(bed_count.value), int(monthly_rent.value), status.value, file_name, room_id)
        )
        
        self.admin_page.page.close(popup)
        create_banner(self.admin_page.page, ft.Colors.BLUE_100, ft.Icon(ft.Icons.EDIT, color="blue"), f"Room #{room_id} updated!", "blue")
        await self.load_rooms()

    async def show_add_room(self, e):
        async def on_result(e):
            if e.files: upload_pic.controls[0].value = e.files[0].path; self.admin_page.page.update()

        file_picker = ft.FilePicker(on_result=on_result)
        self.admin_page.page.overlay.append(file_picker)

        upload_pic = ft.Row([ft.TextField("placeholder.jpg", label="Thumbnail", disabled=True, expand=True), ft.ElevatedButton("Select", on_click=lambda _: file_picker.pick_files(allow_multiple=False))], alignment="center")
        
        bed_count = ft.Dropdown(label="Beds", options=[ft.DropdownOption(i, str(i)) for i in range(1, 11)], value=1, expand=True)
        status = ft.Dropdown(label="Status", options=[ft.DropdownOption("available"), ft.DropdownOption("maintenance")], value="available", expand=True)
        monthly_rent = ft.TextField(label="Rent", prefix_text="₱ ", value="", keyboard_type="number", input_filter=ft.InputFilter(r'^[0-9]*$'), expand=True)

        popup = ft.AlertDialog(
            title=ft.Text("Create Room"),
            content=ft.Container(ft.Column([upload_pic, ft.Row([status, bed_count]), monthly_rent], tight=True, spacing=20), width=450),
            actions=[
                ft.FilledButton("Cancel", style=ft.ButtonStyle(bgcolor="#E6E8EE", color="black"), on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Create", bgcolor="#FF6900", on_click=lambda e: self.admin_page.page.run_task(self.check_add_room, file_picker, status, bed_count, monthly_rent, popup))
            ]
        )
        self.admin_page.page.open(popup)

    async def check_add_room(self, file_picker, status, bed_count, monthly_rent, popup):
        if not monthly_rent.value: return

        file_name = "placeholder.jpg"
        if file_picker.result and file_picker.result.files:
            f = file_picker.result.files[0]
            file_name = f.name
            os.makedirs("assets/room_thumbnails", exist_ok=True)
            shutil.copy2(f.path, f"assets/room_thumbnails/{file_name}")

        await self.admin_page.page.data.create_room(int(bed_count.value), int(monthly_rent.value), status.value, file_name)
        self.admin_page.page.close(popup)
        create_banner(self.admin_page.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.ADD_HOME, color="green"), "Room created!", "green")
        await self.load_rooms()

    async def delete_room(self, room):
        def confirm(e):
            self.admin_page.page.run_task(self.process_delete, room['id'], dlg)

        dlg = ft.AlertDialog(
            title=ft.Text("Delete Room?"),
            content=ft.Text(f"Delete Room #{room['id']}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(dlg)),
                ft.FilledButton("Delete", bgcolor="red", on_click=confirm)
            ]
        )
        self.admin_page.page.open(dlg)

    async def process_delete(self, rid, dlg):
        try:
            await self.admin_page.page.data.custom_query("DELETE FROM rooms WHERE id=%s", (rid,))
            self.admin_page.page.close(dlg)
            create_banner(self.admin_page.page, ft.Colors.RED_100, ft.Icon(ft.Icons.DELETE, color="red"), "Room deleted!", "red")
            await self.load_rooms()
        except Exception as e: print(e)
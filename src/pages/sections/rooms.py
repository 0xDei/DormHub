import flet as ft
from datetime import datetime
import os, shutil
from flet import FilePickerUploadFile
import json

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_banner

class Rooms(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page
        self.rooms_list = ft.Column(spacing=15, expand=True)

        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Room Management", color="#FF6900", size=16, weight=ft.FontWeight.W_500),
                        ft.Text("Manage beds and room availability", size=12, weight=ft.FontWeight.W_500)
                    ],
                    spacing=1,
                    expand=True
                ),
                ft.Container(
                    ft.FilledButton(
                        "Add Room", 
                        icon=ft.Icons.ADD, 
                        icon_color=ft.Colors.WHITE, 
                        bgcolor="#FF6900", 
                        color=ft.Colors.WHITE, 
                        elevation=0, 
                        width=120, 
                        height=30, 
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD), alignment=ft.alignment.center, padding=10),
                        on_click=self.show_add_room
                    )
                )
            ]
        )

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            self.rooms_list
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

        # Load rooms when initialized
        self.admin_page.page.run_task(self.load_rooms)

    async def load_rooms(self):
        """Load and display all rooms from the database"""
        try:
            print("Loading rooms...")  # Debug
            
            self.rooms_list.controls.clear()
            
            # Get rooms from database (async call)
            rooms_data = await self.admin_page.page.data.get_all_rooms()
            print(f"Raw rooms data: {rooms_data}")  # Debug
            
            if not rooms_data or len(rooms_data) == 0:
                # Show empty state
                self.rooms_list.controls.append(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.BED_OUTLINED, size=64, color=ft.Colors.GREY_400),
                                ft.Text("No rooms available", size=16, color=ft.Colors.GREY_600),
                                ft.Text("Click 'Add Room' to create your first room", size=12, color=ft.Colors.GREY_500)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        alignment=ft.alignment.center,
                        padding=50
                    )
                )
            else:
                # Convert database tuples to dictionaries
                for room_tuple in rooms_data:
                    # Database returns: (id, amenities, residents, bed_count, monthly_rent, current_status, thumbnail)
                    room = {
                        'id': room_tuple[0],
                        'amenities': json.loads(room_tuple[1]) if room_tuple[1] else [],
                        'residents': json.loads(room_tuple[2]) if room_tuple[2] else [],
                        'bed_count': room_tuple[3],
                        'monthly_rent': room_tuple[4],
                        'status': room_tuple[5],
                        'thumbnail': room_tuple[6]
                    }
                    print(f"Creating card for room: {room}")  # Debug
                    room_card = self.create_room_card(room)
                    self.rooms_list.controls.append(room_card)
            
            self.admin_page.page.update()
            print("Rooms loaded successfully!")  # Debug
            
        except Exception as e:
            print(f"Error loading rooms: {e}")  # Debug
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Error loading rooms: {str(e)}")

    def show_error_message(self, message):
        """Display error message in the rooms list"""
        self.rooms_list.controls.clear()
        self.rooms_list.controls.append(
            ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
                        ft.Text("Error Loading Rooms", size=16, color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
                        ft.Text(message, size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                padding=50
            )
        )
        self.admin_page.page.update()

    def create_room_card(self, room):
        """Create a card display for a room"""
        try:
            room_id = room['id']
            status = room['status']
            bed_count = room['bed_count']
            monthly_rent = room['monthly_rent']
            thumbnail = room['thumbnail']
            
            # Determine status color
            status_colors = {
                "available": ft.Colors.GREEN,
                "occupied": ft.Colors.RED,
                "maintenance": ft.Colors.ORANGE
            }
            status_color = status_colors.get(status, ft.Colors.GREY)
            
            thumbnail_path = f"assets/room_thumbnails/{thumbnail}"
            # If specific thumbnail doesn't exist, use placeholder
            if not os.path.exists(thumbnail_path):
                thumbnail_path = "assets/placeholder.jpg"
            
            return ft.Card(
                ft.Container(
                    ft.Row(
                        [
                            # Thumbnail
                            ft.Container(
                                ft.Image(
                                    src=thumbnail_path,
                                    width=150,
                                    height=150,
                                    fit=ft.ImageFit.COVER,
                                    border_radius=ft.border_radius.all(10),
                                    error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=50, color=ft.Colors.GREY)
                                ),
                                width=150,
                                height=150,
                                bgcolor=ft.Colors.GREY_200,
                                border_radius=ft.border_radius.all(10)
                            ),
                            # Room Details
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text(f"Room #{room_id}", size=18, weight=ft.FontWeight.BOLD),
                                                ft.Container(
                                                    ft.Text(
                                                        status.upper(),
                                                        size=10,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.WHITE
                                                    ),
                                                    bgcolor=status_color,
                                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                                    border_radius=ft.border_radius.all(5)
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        ),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.BED, size=16, color=ft.Colors.GREY_600),
                                                ft.Text(f"{bed_count} Bed(s)", size=14, color=ft.Colors.GREY_700)
                                            ],
                                            spacing=5
                                        ),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.PAYMENTS, size=16, color=ft.Colors.GREY_600),
                                                ft.Text(f"₱ {float(monthly_rent):,.2f} / month", size=14, color=ft.Colors.GREY_700)
                                            ],
                                            spacing=5
                                        ),
                                        ft.Row(
                                            [
                                                ft.TextButton(
                                                    "Edit",
                                                    icon=ft.Icons.EDIT,
                                                    style=ft.ButtonStyle(
                                                        color={"": ft.Colors.BLUE_700}
                                                    ),
                                                    on_click=lambda e, r=room: self.admin_page.page.run_task(self.edit_room, r)
                                                ),
                                                ft.TextButton(
                                                    "Delete",
                                                    icon=ft.Icons.DELETE,
                                                    style=ft.ButtonStyle(
                                                        color={"": ft.Colors.RED_700}
                                                    ),
                                                    on_click=lambda e, r=room: self.admin_page.page.run_task(self.delete_room, r)
                                                )
                                            ],
                                            spacing=10
                                        )
                                    ],
                                    spacing=10,
                                    expand=True
                                ),
                                padding=15,
                                expand=True
                            )
                        ],
                        spacing=15
                    ),
                    padding=10
                ),
                elevation=2
            )
        except Exception as e:
            print(f"Error creating room card: {e}")
            return ft.Container(ft.Text(f"Error displaying room: {str(e)}", color=ft.Colors.RED))

    async def edit_room(self, room):
        """Handle room editing"""
        print(f"Edit room: {room}")
        
        async def on_result(e):
            if e.files == None: return
            upload_pic.controls[0].value = e.files[0].path
            self.admin_page.page.update()

        file_picker = ft.FilePicker(on_result=on_result)
        self.admin_page.page.overlay.append(file_picker)

        # Pre-fill with current room data
        upload_pic = ft.Row([
            ft.TextField(room['thumbnail'], label="Select Thumbnail", disabled=True), 
            ft.ElevatedButton("Select", height=47, width=70, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"]))
        ], alignment=ft.MainAxisAlignment.CENTER)

        options = []
        for num in range(1, 10):
            options.append(ft.DropdownOption(num, num))

        bed_count = ft.Dropdown(label="Bed Count", options=options, width=182.5, value=room['bed_count'])
        status = ft.Dropdown(label="Status", options=[
            ft.DropdownOption("maintenance"),
            ft.DropdownOption("occupied"),
            ft.DropdownOption("available")
        ], width=182.5, value=room['status'])

        monthly_rent = ft.TextField(
            label="Monthly Rent", 
            prefix_text="₱ ", 
            width=375, 
            value=str(room['monthly_rent']), 
            keyboard_type=ft.KeyboardType.NUMBER, 
            input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string="")
        )

        popup = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                ft.Column(
                    [
                        ft.Container(ft.Text(f"Edit Room #{room['id']}", size=24, color=ft.Colors.BLACK), margin=ft.margin.only(bottom=30)),
                        upload_pic,
                        ft.Row(
                            [
                                status, bed_count
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row([monthly_rent], alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                margin=ft.margin.only(top=30),
                width=470
            ),
            actions=[
                ft.FilledButton("Cancel", expand=True, height=45, width=200, bgcolor="#E6E8EE", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=14)), color=ft.Colors.BLACK, on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Update Room", expand=True, height=35, width=200, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.admin_page.page.run_task(self.check_edit_room, room['id'], file_picker, status, bed_count, monthly_rent, popup, room['thumbnail']))
            ],
            shape=ft.RoundedRectangleBorder(radius=15),
            actions_alignment=ft.MainAxisAlignment.CENTER
        )

        self.admin_page.page.open(popup)
        self.admin_page.page.update()

    async def check_edit_room(self, room_id, file_picker, status, bed_count, monthly_rent, popup, current_thumbnail):
        """Validate and update room data"""
        monthly_rent.error_text = ""

        if monthly_rent.value == "" or int(monthly_rent.value) < 1:
            monthly_rent.error_text = "[!] Rent must be at least ₱ 1.00"
            self.admin_page.page.update()
            return

        # Handle thumbnail update
        if file_picker.result != None and file_picker.result.files != None:
            selected_file = file_picker.result.files[0]
            file_name = selected_file.name
            source_path = selected_file.path
            
            destination_folder = "assets/room_thumbnails"
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, file_name)
            shutil.copy2(source_path, destination_path)
        else:
            # Keep existing thumbnail
            file_name = current_thumbnail

        # Update room in database
        await self.admin_page.page.data.custom_query(
            "UPDATE rooms SET bed_count=%s, monthly_rent=%s, current_status=%s, thumbnail=%s WHERE id=%s",
            (int(bed_count.value), int(monthly_rent.value), status.value, file_name, room_id)
        )
        
        self.admin_page.page.close(popup)
        create_banner(self.admin_page.page, ft.Colors.BLUE_100, ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE), f"Room #{room_id} updated successfully!", ft.Colors.BLUE_500)
        
        # Reload rooms after editing
        await self.load_rooms()

    async def delete_room(self, room):
        """Handle room deletion"""
        room_id = room['id']
        
        async def confirm_delete(e):
            try:
                # Delete room from database
                await self.admin_page.page.data.custom_query(
                    "DELETE FROM rooms WHERE id = %s",
                    (room_id,)
                )
                self.admin_page.page.close(confirm_dialog)
                create_banner(self.admin_page.page, ft.Colors.RED_100, ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED), f"Room #{room_id} deleted successfully!", ft.Colors.RED_500)
                await self.load_rooms()
            except Exception as ex:
                print(f"Error deleting room: {ex}")
                self.admin_page.page.close(confirm_dialog)
                create_banner(self.admin_page.page, ft.Colors.RED_100, ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED), f"Error deleting room: {str(ex)}", ft.Colors.RED_500)
        
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Room?"),
            content=ft.Text(f"Are you sure you want to delete Room #{room_id}? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(confirm_dialog)),
                ft.FilledButton("Delete", bgcolor=ft.Colors.RED, on_click=lambda e: self.admin_page.page.run_task(confirm_delete, e))
            ]
        )
        
        self.admin_page.page.open(confirm_dialog)
        self.admin_page.page.update()

    async def show_add_room(self, e):
        async def on_result(e):
            if e.files == None: return
            upload_pic.controls[0].value = e.files[0].path
            self.admin_page.page.update()

        file_picker = ft.FilePicker(on_result=on_result)
        self.admin_page.page.overlay.append(file_picker)

        upload_pic = ft.Row([ft.TextField("placeholder.jpg", label="Select Thumbnail", disabled=True), ft.ElevatedButton("Select", height=47, width=70, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"]))], alignment=ft.MainAxisAlignment.CENTER)

        options = []
        for num in range(1, 10):
            options.append(ft.DropdownOption(num, num))

        bed_count = ft.Dropdown(label="Bed Count", options=options, width=182.5, value=1)
        status = ft.Dropdown(label="Status", options=[
            ft.DropdownOption("maintenance"),
            ft.DropdownOption("occupied"),
            ft.DropdownOption("available")
        ], width=182.5, value="available")

        monthly_rent = ft.TextField(
            label="Monthly Rent", 
            prefix_text="₱ ", 
            width=375, 
            keyboard_type=ft.KeyboardType.NUMBER, 
            input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string="")
        )

        popup = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                ft.Column(
                    [
                        ft.Container(ft.Text("Create Room", size=24, color=ft.Colors.BLACK), margin=ft.margin.only(bottom=30)),
                        upload_pic,
                        ft.Row(
                            [
                                status, bed_count
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row([monthly_rent], alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                margin=ft.margin.only(top=30),
                width=470
            ),
            actions=[
                ft.FilledButton("Cancel", expand=True, height=45, width=200, bgcolor="#E6E8EE", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=14)), color=ft.Colors.BLACK, on_click=lambda e: self.admin_page.page.close(popup)),
                ft.FilledButton("Create Room", expand=True, height=35, width=200, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.admin_page.page.run_task(self.check_add_room, file_picker, status, bed_count, monthly_rent, popup))
            ],
            shape=ft.RoundedRectangleBorder(radius=15),
            actions_alignment=ft.MainAxisAlignment.CENTER
        )

        self.admin_page.page.open(popup)
        self.admin_page.page.update()

    async def check_add_room(self, file_picker, status, bed_count, monthly_rent, popup):
        monthly_rent.error_text = ""

        if monthly_rent.value == "" or int(monthly_rent.value) < 1:
            monthly_rent.error_text = "[!] Rent must be at least ₱ 1.00"
            self.admin_page.page.update()
            return

        
        if file_picker.result != None and file_picker.result.files != None:
            selected_file = file_picker.result.files[0]
            file_name = selected_file.name
            source_path = selected_file.path
        else:
            file_name = "placeholder.jpg"
            source_path = "assets/placeholder.jpg"

        destination_folder = "assets/room_thumbnails"
        os.makedirs(destination_folder, exist_ok=True)

        destination_path = os.path.join(destination_folder, file_name)
        shutil.copy2(source_path, destination_path)

        await self.admin_page.page.data.create_room(int(bed_count.value), int(monthly_rent.value), status.value, file_name)
        self.admin_page.page.close(popup)
        create_banner(self.admin_page.page, ft.Colors.GREEN_100,ft.Icon(ft.Icons.ADD_HOME_ROUNDED, color=ft.Colors.GREEN), f"Successfully created a Room!", ft.Colors.GREEN_500)
        
        # Reload rooms after adding
        await self.load_rooms()
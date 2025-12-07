import flet as ft
from datetime import datetime
import os, shutil
from flet import FilePickerUploadFile

from pages.sections.section import Section
from utils.element_factory import create_info_card, create_banner

class Rooms(Section):
    def __init__(self, admin_page):
        super().__init__()

        self.admin_page = admin_page

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

        rooms_list = ft.Container()

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            rooms_list
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


    async def show_add_room(self, e):
        async def on_result(e):
            upload_pic.controls[0].value = e.files[0].path
            self.admin_page.page.update()

        file_picker = ft.FilePicker(on_result=on_result)
        self.admin_page.page.overlay.append(file_picker)

        upload_pic = ft.Row([ft.TextField("/placeholder.png", label="Select Thumbnail", disabled=True), ft.ElevatedButton("Select", height=47, width=70, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"]))], alignment=ft.MainAxisAlignment.CENTER)

        options = []
        for num in range(1, 10):
            options.append(ft.DropdownOption(num, num))

        bed_count = ft.Dropdown(label="Bed Count", options=options, width=182.5, value=1)
        status = ft.Dropdown(label="Status", options=[
            ft.DropdownOption("maintenance"),
            ft.DropdownOption("occupied"),
            ft.DropdownOption("available")
        ], width=182.5, value="available")

        monthly_rent = ft.TextField(label="Monthly Rent", prefix_text="₱ ", width=375, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r'^[0-9]*$', allow=True, replacement_string=""))

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

        selected_file = file_picker.result.files[0]
        source_path = selected_file.path
        destination_folder = "assets/room_thumbnails"
        os.makedirs(destination_folder, exist_ok=True)

        destination_path = os.path.join(destination_folder, selected_file.name)
        shutil.copy2(source_path, destination_path)

        await self.admin_page.page.data.create_room(int(bed_count.value), int(monthly_rent.value), status.value, selected_file.name)
        self.admin_page.page.close(popup)
        create_banner(self.admin_page.page, ft.Colors.GREEN_100,ft.Icon(ft.Icons.ADD_HOME_ROUNDED, color=ft.Colors.GREEN), f"Successfully created a Room!", ft.Colors.GREEN_500)
        self.admin_page.page.update()
        await self.admin_page.show_section(Rooms(self.admin_page))
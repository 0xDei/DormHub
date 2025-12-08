import flet as ft
from datetime import datetime

from pages.sections.section import Section
from utils.element_factory import create_info_card

class MyRoom(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page
        
        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Welcome Home,", color="#E78B28", size=16, weight=ft.FontWeight.W_500),
                        ft.Text(self.resident_page.username + "!", color="#FF6900", size=16, weight=ft.FontWeight.BOLD)
                    ],
                    spacing=3.5
                ),
                ft.Text("Room " + str(self.resident_page.data["room_id"]), size=12, weight=ft.FontWeight.W_500)
            ],
            spacing=1
        )
        
        if self.resident_page.data["room_id"] != "N/A":
            # Handle due date safely
            try:
                if self.resident_page.data["due_date"] != "N/A":
                    date = datetime.fromtimestamp(int(self.resident_page.data["due_date"]))
                    due_date = f"{date.strftime('%b')} {date.day}, {date.year}"
                else:
                    due_date = "Not Set"
            except:
                due_date = "Not Set"
            
            active_requests = 0
            if "requests_data" in self.resident_page.data:
                for request_info in self.resident_page.data["requests_data"]:
                    if request_info["status"] == "completed": continue
                    active_requests += 1

            top_info = ft.Row(
                [
                    create_info_card(
                        "Next Payment Due", 
                        [
                            ft.Text(due_date, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"₱ {self.resident_page.data.get('monthly_rent', 0):,}", size=10)
                        ],
                        ft.Icon(ft.Icons.ATTACH_MONEY, color="#E79031", size=28),
                        "right",
                        "#FEF3C6",
                        250,
                        90
                    ),
                    create_info_card(
                        "Active Requests", 
                        [
                            ft.Text("None" if active_requests == 0 else active_requests, size=24, text_align=ft.TextAlign.CENTER),
                        ],
                        ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#F98851", size=28),
                        "right",
                        "#FFECD3",
                        250,
                        90
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                expand=True
            )

            roommates = self.resident_page.data.get("roommates", [])
            if len(roommates) == 0: 
                roommates_text = ft.Text("None")
            elif len(roommates) > 1:  
                roommates_text = ft.Text(f"{roommates[0]}\n +{len(roommates) - 1} more")
            else: 
                roommates_text = ft.Text(roommates[0])

            # Handle move-in date safely
            try:
                if self.resident_page.data["move_in_date"] != "N/A":
                    date = datetime.fromtimestamp(int(self.resident_page.data["move_in_date"]))
                    move_in_date = f"{date.strftime('%b')} {date.day}, {date.year}"
                else:
                    move_in_date = "Not Set"
            except:
                move_in_date = "Not Set"

            # Determine image source
            thumbnail = self.resident_page.data.get("thumbnail", "placeholder.jpg")
            image_src = f"../assets/room_thumbnails/{thumbnail}"

            room_info = ft.Container(
                ft.Column(
                    [
                        ft.Text("Your Room", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                        ft.ListView([
                            # --- MODIFICATION START ---
                            ft.GestureDetector(
                                content=ft.Image(
                                    src=image_src, 
                                    expand=True, 
                                    height=300, 
                                    fit=ft.ImageFit.COVER, 
                                    border_radius=10
                                ),
                                # Run task to open the dialog when the image is tapped
                                on_tap=lambda e, src=image_src: self.resident_page.page.run_task(self.show_full_image_dialog, src)
                            )
                            # --- MODIFICATION END ---
                        ], height=300, expand=True),
                        ft.Divider(2, color="#FEF3C6"),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("Bed Count", size=12, color=ft.Colors.GREY_600),
                                        ft.Row([ft.Icon(ft.Icons.BED_OUTLINED, color="#E78B28", size=16), ft.Text(str(self.resident_page.data.get("bed_count", 0)))], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                                    ],
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Monthly Rent", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(f"₱ {self.resident_page.data.get('monthly_rent', 0):,}")
                                    ],
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Roommates", size=12, color=ft.Colors.GREY_600),
                                        roommates_text
                                    ],
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Move-in Date", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(move_in_date)
                                    ],
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER, 
                            spacing=50
                        ),
                    ]
                ),
                bgcolor=ft.Colors.WHITE,
                height=430,
                border_radius=15,
                padding=ft.padding.only(left=20, top=17, right=20, bottom=20)
            )

            roommate_cards = []
            roommates_list = self.resident_page.data.get("roommates", [])
            roommate_data_list = self.resident_page.data.get("roommate_data", [])
            
            for i, roommate in enumerate(roommates_list):
                phone = "N/A"
                if i < len(roommate_data_list):
                    phone = roommate_data_list[i].get("phone_number", "N/A")
                
                card = ft.Container(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE, size=32),
                                padding=10,
                                border_radius=50,
                                bgcolor="#FF6900"
                            ),
                            ft.Column([ft.Text(roommate, size=16, weight=ft.FontWeight.BOLD), ft.Text(phone)], spacing=0)
                        ]
                    ),
                    padding=ft.padding.only(top=7, left=10, right=10, bottom=7),
                    border_radius=10,
                    margin=ft.margin.only(top=10),
                    expand=True
                )

                roommate_cards.append(card)

            if len(roommate_cards) == 0: 
                roommate_cards.append(ft.Container(ft.Text("You have no roommates", color=ft.Colors.GREY_300), expand=True, alignment=ft.alignment.center))

            room_mate = ft.Container(
                ft.Column(
                    [
                        ft.Text("Your Roommates", color="#E78B28", size=14, weight=ft.FontWeight.W_500),
                        ft.ListView(roommate_cards, expand=True)
                    ]
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=ft.padding.only(left=20, top=17, right=20, bottom=20),
                border=ft.border.all(2, "#FEF3C6")
            )
        else:
            top_info = ft.Container(
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
            room_info = ft.Container()
            room_mate = ft.Container()

        self.content = ft.Container(
                ft.Column(
                [
                    header,
                    ft.ListView(
                        [
                            ft.Container(top_info, margin=ft.margin.only(bottom=-10)),
                            room_info,
                            room_mate
                        ],
                        spacing=30,
                        padding=ft.padding.only(bottom=20),
                        expand=True
                    )
                ],
                expand=True
            ),
            expand=True
        )

    # --- NEW FUNCTION TO DISPLAY IMAGE IN A DIALOG ---
    async def show_full_image_dialog(self, image_src):
        """Displays the room image in a modal dialog."""
        
        # Determine the Room ID for the title
        room_id = self.resident_page.data.get("room_id", "N/A")
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"Room #{room_id} View"),
            content=ft.Container(
                ft.Image(src=image_src, fit=ft.ImageFit.CONTAIN),
                width=500,  # Set maximum width
                height=400, # Set maximum height
                expand=True
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.resident_page.page.close(dlg))],
            content_padding=0 # Remove padding around the image container
        )
        self.resident_page.page.open(dlg)
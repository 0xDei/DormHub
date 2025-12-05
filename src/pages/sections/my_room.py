import flet as ft

from pages.sections.section import Section

class MyRoom(Section):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page
        
        header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Welcome Home,", color="#E78B28", size=16, weight=ft.FontWeight.W_600),
                        ft.Text(self.resident_page.username + "!", color="#FF6900", size=16, weight=ft.FontWeight.BOLD)
                    ],
                    spacing=3.5
                ),
                ft.Text("Room " + self.resident_page.data["room_id"])
            ]
        )

        self.content = ft.Column(
            [
                header
            ]
        )
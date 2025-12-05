import flet as ft

from utils.element_factory import get_navbar_icon

class NavBar(ft.Container):
    def __init__(self, isAdmin=True, resident_page=None, buttons=[]):
        super().__init__()

        self.resident_page = resident_page
        self.buttons = buttons

        self.width = 200
        self.height = 685
        self.padding = ft.padding.only(top=18, left=13, right=13, bottom=18)
        self.bgcolor = ft.Colors.WHITE

        account_button = ft.Container()
        if isAdmin == False:
            account_button = ft.Container(
                ft.Row(
                    [
                        ft.Container(
                            ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE),
                            padding=4,
                            border_radius=50,
                            bgcolor="#FF6900"
                        ),
                        ft.Column([ft.Text(self.resident_page.username, size=14, weight=ft.FontWeight.W_400), ft.Text("Room " + self.resident_page.data["room_id"], size=10, weight=ft.FontWeight.W_100)], spacing=0)
                    ],
                ),
                bgcolor="#FEFBE8",
                padding=ft.padding.only(top=7, left=10, right=10, bottom=7),
                border_radius=10,
                margin=ft.margin.only(top=10)
            )

        self.content = ft.Column(
            [
                get_navbar_icon(1),
                account_button,
                ft.Container(ft.Divider(2), margin=ft.margin.only(top=10, bottom=20)),
                *self.buttons,
                ft.Container(expand=True),
                ft.Divider(2),
                ft.Container(margin=ft.margin.only(top=10), content=ft.FilledButton("Logout", icon=ft.Icons.EXIT_TO_APP_ROUNDED, icon_color=ft.Colors.RED, bgcolor="#FEF9F9", color=ft.Colors.RED, elevation=0, width=180, height=30, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_700), alignment=ft.alignment.center_left, padding=10)))
            ]
        )
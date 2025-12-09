import flet as ft
from pages.components.navbar_button import NavBarButton
from utils.element_factory import get_navbar_icon, create_banner

class NavBar(ft.Container):
    def __init__(self, isAdmin=True, current_page=None, buttons=[]):
        super().__init__()

        self.current_page = current_page
        self.buttons = buttons

        self.width = 200
        self.padding = ft.padding.only(top=18, left=13, right=13, bottom=18)
        self.bgcolor = ft.Colors.WHITE

        account_button = ft.Container()
        if isAdmin == False:
            self.username_text = ft.Text(self.current_page.username, size=14, weight=ft.FontWeight.W_400)
            
            account_button = ft.Container(
                ft.Row(
                    [
                        ft.Container(
                            ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ft.Colors.WHITE),
                            padding=4,
                            border_radius=50,
                            bgcolor="#FF6900"
                        ),
                        ft.Column(
                            [
                                self.username_text, 
                                ft.Text("Room " + str(self.current_page.data["room_id"]), size=10, weight=ft.FontWeight.W_100)
                            ], 
                            spacing=0
                        )
                    ]
                ),
                bgcolor="#FEFBE8",
                padding=ft.padding.only(top=7, left=10, right=10, bottom=7),
                border_radius=10,
                margin=ft.margin.only(top=10)
            )

        self.content = ft.Column(
            [
                get_navbar_icon(isAdmin),
                account_button,
                ft.Container(ft.Divider(2), margin=ft.margin.only(top=10, bottom=20)),
                *self.buttons,
                ft.Container(expand=True),
                ft.Divider(2),
                ft.Container(margin=ft.margin.only(top=10), content=ft.FilledButton("Logout", on_click=self.logout, icon=ft.Icons.EXIT_TO_APP_ROUNDED, icon_color=ft.Colors.RED, bgcolor="#FEF9F9", color=ft.Colors.RED, elevation=0, width=180, height=30, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_700), alignment=ft.alignment.center_left, padding=10)))
            ],
            expand=True 
        )

    def highlight_tab(self, button_text):
        """Updates all buttons to highlight the selected one and deselect others."""
        for btn in self.buttons:
            if isinstance(btn, NavBarButton):
                if btn.text == button_text:
                    btn.select()
                else:
                    btn.deselect()
    
    def update_user_display(self):
        """Refreshes the displayed username in the navbar."""
        if hasattr(self, 'username_text'):
            self.username_text.value = self.current_page.username
            self.username_text.update()

    async def logout(self, e):
        def go_to_menu(e):
            self.current_page.page.data.set_active_user(None)
            self.current_page.page.go("/", True)

        popup = ft.AlertDialog(
            modal=True,
            title=ft.Text("Logout"),
            content=ft.Text("Are you sure you want to log out?", color=ft.Colors.GREY_700),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.current_page.page.close(popup)),
                ft.TextButton("Logout", on_click=go_to_menu)
            ],
        )

        self.current_page.page.open(popup)
        self.current_page.page.update()
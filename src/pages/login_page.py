import flet as ft
from element_factory import *

class LoginPage:
    def __init__(self, page: ft.Page, type=1):
        self.page = page
        self.type = type

    def show(self):
        emailTF = ft.TextField(label="Admin Username or Email" if self.type == 0 else "Username or Email", hint_text="Enter admin username or email" if self.type == 0 else "Enter your username or email", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color="#B8B8C1"), height=45, width=340)
        passwordTF = ft.TextField(label="Admin Password" if self.type == 0 else "Password", hint_text="Enter admin password" if self.type == 0 else "Enter your password", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), height=45, width=340)

        login_card = ft.Container(
            ft.Column(
                [
                    ft.Text("Log in as Admin" if self.type == 0 else "Log in as Resident", weight=ft.FontWeight.BOLD, size=24, color=ft.Colors.BLACK),
                    ft.Container(ft.Column(
                            [
                                emailTF, passwordTF
                            ],
                            spacing=25
                        ),
                        margin=ft.margin.only(top=50)
                    ),
                    ft.Container(ft.Column(
                            [
                                ft.FilledButton("Log In", width=340, height=45, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/")),
                                ft.Row([ft.Text("Don't have an account?"), ft.GestureDetector(content=ft.Text("Sign Up", color="#7189FF"), on_tap=lambda e: print("clicked"))], spacing=3) if self.type == 1 else ft.Row()
                            ]
                        ),
                        margin=ft.margin.only(top=60)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=35, left=20, right=20, bottom=45),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            shadow=[
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                )
            ],
            width=370
        )

        self.page.views.append(
            ft.View(
                "/login-admin" if self.type == 0 else "/login-resident",
                [
                    ft.Row([get_icon(64, True, 18, 16, 24, 18, ft.margin.only(bottom=30)), login_card])
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                bgcolor="#FFFAEA"
            )
        )
        self.page.update()

    def get_type(self):
        return self.type

    def change_type(self, type):
        self.type = type
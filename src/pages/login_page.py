import flet as ft
import re

from utils.element_factory import *

class LoginPage:
    def __init__(self, page: ft.Page, type=1):
        self.page = page
        self.type = type


    async def show(self):
        emailTF = ft.TextField(label="Admin Email" if self.type == 0 else "Email", hint_text="Enter admin email" if self.type == 0 else "Enter your email", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color="#B8B8C1"), width=340, autofocus=True, on_submit=lambda e: self.page.run_task(self.check_login, emailTF, passwordTF))
        passwordTF = ft.TextField(label="Admin Password" if self.type == 0 else "Password", hint_text="Enter admin password" if self.type == 0 else "Enter your password", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), width=340, password=True, can_reveal_password=True, on_submit=lambda e: self.page.run_task(self.check_login, emailTF, passwordTF))

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
                                ft.FilledButton("Log In", width=340, height=45, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.run_task(self.check_login, emailTF, passwordTF)),
                                ft.Row([ft.Text("Don't have an account?"), ft.GestureDetector(content=ft.Text("Sign Up", color="#7189FF"), on_tap=lambda e: self.page.run_task(self.show_sign_up))], spacing=3) if self.type == 1 else ft.Row()
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
                    ft.Row(
                        [
                            get_icon(64, True, 18, 16, 24, 18, ft.margin.only(bottom=30)), 
                            login_card
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=70
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                bgcolor="#FFFBEB"
            )
        )
        self.page.update()


    async def check_login(self, emailTF, passwordTF):
        email = emailTF.value
        password = passwordTF.value

        if self.type == 0:
            print("Coming soon...")
            return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if email.strip() == "" or not re.fullmatch(regex, email):
            emailTF.error_text = "Please enter a valid email!"
            self.page.update()
            return
        emailTF.error_text = ""
        self.page.update()

        user_data = await self.page.data.get_user_by_email(email)

        if len(user_data) == 0 or user_data[0][3] != password:
            create_banner(self.page, ft.Colors.RED_100, ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, color=ft.Colors.RED), "No user found! Double check your email or password.", ft.Colors.RED)

            emailTF.error_text = "No user found!"
            passwordTF.error_text = "Incorrect email or password!"

            passwordTF.value = ""
            self.page.update()
            return
        emailTF.error_text = ""
        passwordTF.error_text = ""

        self.page.data.set_active_user(user_data[0][0])
        self.page.go("/active-resident")
        self.page.update()

    
    async def show_sign_up(self):
        usernameTF = ft.TextField(label="Username", hint_text="Enter your desired username", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color="#B8B8C1"), width=370, autofocus=True)
        emailTF = ft.TextField(label="Email", hint_text="Enter your email", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color="#B8B8C1"), width=370, autofocus=True)
        passwordTF = ft.TextField(label="Password", hint_text="Enter a secure password", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), width=370, password=True, can_reveal_password=True)
        confirm_passwordTF = ft.TextField(label="Confirm password", hint_text="Confirm your password", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), width=370, password=True, can_reveal_password=True)

        async def sign_up(e):
            username = usernameTF.value.strip()
            email = emailTF.value.strip()
            password = passwordTF.value
            confirm_password = confirm_passwordTF.value

            usernameTF.error_text = ""
            emailTF.error_text = ""
            passwordTF.error_text = ""
            confirm_passwordTF.error_text = ""

            has_error = False

            if len(username) < 3 or len(username) > 24:
                usernameTF.error_text = "[!] Username must be > 3 but < 24 characters long"
                has_error = True

            res = await self.page.data.get_user_by_name(username)
            if len(res) > 0:
                usernameTF.error_text = "[!] Username already exists"
                has_error = True

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if email == "" or not re.fullmatch(regex, email):
                emailTF.error_text = "[!] Please enter a valid email"
                has_error = True

            res = await self.page.data.get_user_by_email(email)
            if len(res) > 0:
                emailTF.error_text = "[!] Email already in use"
                has_error = True

            if len(password) < 6:
                passwordTF.error_text = "[!] Password must 6 or more characters long"
                has_error = True

            if password != confirm_password:
                confirm_passwordTF.error_text = "[!] Password does not match"
                has_error = True


            if has_error:
                self.page.update()
                return

            await self.page.data.create_user(username, email, password)
            self.page.close(popup)
            create_banner(self.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.PERSON_ADD_ALT_1_OUTLINED, color=ft.Colors.GREEN), f"Account creation success!\n Welcome, {username}", ft.Colors.GREEN_500)
            self.page.update()

        popup = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.PERSON_ADD_ALT_1_ROUNDED, size=48),
            content=ft.Container(
                ft.Column(
                    [
                        ft.Text("Create Account", size=24, color=ft.Colors.BLACK),
                        usernameTF, emailTF, passwordTF, confirm_passwordTF
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                width=400,
                alignment=ft.alignment.center
            ),
            actions=[
                ft.Column(
                    [
                        ft.FilledButton("Cancel", width=370, height=30, bgcolor="#E6E8EE", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16)), color=ft.Colors.BLACK, on_click=lambda e: self.page.close(popup)),
                        ft.FilledButton("Create Account", width=370, height=30, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=sign_up),
                    ]
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=15),
            actions_alignment=ft.MainAxisAlignment.CENTER
        )

        self.page.open(popup)
        self.page.update()


    def get_type(self):
        return self.type


    def change_type(self, type):
        self.type = type
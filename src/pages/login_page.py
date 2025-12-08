import flet as ft
import re
import asyncio
import math

from utils.element_factory import *

class LoginPage:
    def __init__(self, page: ft.Page, type=1):
        self.page = page
        self.type = type  # 0 = Admin, 1 = Resident

        self.admin_email = "admin@gmail.com"
        self.admin_password = "admin123"
        
        # State for UI controls
        self.card_container = None
        self.login_view = None
        self.register_view = None
        self.is_registering = False

    async def show(self):
        # --- 1. BUILD LOGIN VIEW (Front of Card) ---
        if self.type == 0:
            login_field = ft.TextField(
                label="Admin Email", 
                hint_text="Enter admin email", 
                hint_style=ft.TextStyle(color="#B8B8C1"), 
                text_style=ft.TextStyle(color=ft.Colors.BLACK), 
                border_radius=10, 
                border_width=0, 
                bgcolor="#F3F3F5", 
                prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color="#B8B8C1"), 
                width=340, 
                on_submit=lambda e: self.page.run_task(self.check_login, login_field, passwordTF)
            )
        else:
            login_field = ft.TextField(
                label="Username", 
                hint_text="Enter your username", 
                hint_style=ft.TextStyle(color="#B8B8C1"), 
                text_style=ft.TextStyle(color=ft.Colors.BLACK), 
                border_radius=10, 
                border_width=0, 
                bgcolor="#F3F3F5", 
                prefix_icon=ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color="#B8B8C1"), 
                width=340, 
                on_submit=lambda e: self.page.run_task(self.check_login, login_field, passwordTF)
            )

        passwordTF = ft.TextField(
            label="Password", 
            hint_text="Enter your password", 
            hint_style=ft.TextStyle(color="#B8B8C1"), 
            text_style=ft.TextStyle(color=ft.Colors.BLACK), 
            border_radius=10, 
            border_width=0, 
            bgcolor="#F3F3F5", 
            prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), 
            width=340, 
            password=True, 
            can_reveal_password=True, 
            on_submit=lambda e: self.page.run_task(self.check_login, login_field, passwordTF)
        )

        login_footer = ft.Row()
        if self.type == 1:
            login_footer = ft.Row(
                [
                    ft.Text("New User?"), 
                    ft.GestureDetector(
                        content=ft.Text("Register here", color="#7189FF", weight=ft.FontWeight.BOLD), 
                        on_tap=lambda e: self.page.run_task(self.flip_card, e)
                    )
                ], 
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER
            )

        self.login_view = ft.Column(
            [
                ft.Text("Log in as Admin" if self.type == 0 else "Log in as Resident", weight=ft.FontWeight.BOLD, size=24, color=ft.Colors.BLACK),
                ft.Container(
                    ft.Column([login_field, passwordTF], spacing=25),
                    margin=ft.margin.only(top=50)
                ),
                ft.Container(
                    ft.Column(
                        [
                            ft.FilledButton(
                                "Log In", 
                                width=340, height=45, 
                                bgcolor="#FF6900", 
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), 
                                color=ft.Colors.WHITE, 
                                on_click=lambda e: self.page.run_task(self.check_login, login_field, passwordTF)
                            ),
                            login_footer
                        ],
                        spacing=15
                    ),
                    margin=ft.margin.only(top=40)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # --- 2. BUILD REGISTER VIEW (Back of Card) ---
        # Only needed for residents
        if self.type == 1:
            reg_user_tf = ft.TextField(label="Username", border_radius=10, bgcolor="#F3F3F5", border_width=0, prefix_icon=ft.Icon(ft.Icons.PERSON, color="#B8B8C1"), width=340)
            reg_email_tf = ft.TextField(label="Email", border_radius=10, bgcolor="#F3F3F5", border_width=0, prefix_icon=ft.Icon(ft.Icons.EMAIL, color="#B8B8C1"), width=340)
            # Added Phone Number Field
            reg_phone_tf = ft.TextField(
                label="Phone Number", 
                border_radius=10, 
                bgcolor="#F3F3F5", 
                border_width=0, 
                prefix_icon=ft.Icon(ft.Icons.PHONE, color="#B8B8C1"), 
                width=340,
                keyboard_type=ft.KeyboardType.PHONE,
                input_filter=ft.InputFilter(regex_string=r'^[0-9+]*$', allow=True, replacement_string="")
            )
            # Added Access Key Field
            reg_access_key_tf = ft.TextField(
                label="Landlord Access Key (Admin Email)", 
                hint_text="Enter the Admin's email for access",
                border_radius=10, 
                bgcolor="#F3F3F5", 
                border_width=0, 
                prefix_icon=ft.Icon(ft.Icons.KEY_OUTLINED, color="#B8B8C1"), 
                width=340
            )
            reg_pass_tf = ft.TextField(label="Password", border_radius=10, bgcolor="#F3F3F5", border_width=0, password=True, can_reveal_password=True, prefix_icon=ft.Icon(ft.Icons.LOCK, color="#B8B8C1"), width=340)
            reg_confirm_tf = ft.TextField(label="Confirm Password", border_radius=10, bgcolor="#F3F3F5", border_width=0, password=True, can_reveal_password=True, prefix_icon=ft.Icon(ft.Icons.LOCK_CLOCK, color="#B8B8C1"), width=340)

            self.register_view = ft.Column(
                [
                    ft.Text("Register New User", weight=ft.FontWeight.BOLD, size=24, color=ft.Colors.BLACK),
                    ft.Container(
                        # ADDED reg_access_key_tf
                        ft.Column([reg_user_tf, reg_email_tf, reg_phone_tf, reg_access_key_tf, reg_pass_tf, reg_confirm_tf], spacing=15),
                        margin=ft.margin.only(top=30)
                    ),
                    ft.Container(
                        ft.Column(
                            [
                                ft.FilledButton(
                                    "Create Account", 
                                    width=340, height=45, 
                                    bgcolor="#FF6900", 
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), 
                                    color=ft.Colors.WHITE, 
                                    # ADDED reg_access_key_tf to sign_up call
                                    on_click=lambda e: self.page.run_task(self.sign_up, reg_user_tf, reg_email_tf, reg_phone_tf, reg_access_key_tf, reg_pass_tf, reg_confirm_tf)
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Already have an account?"), 
                                        ft.GestureDetector(
                                            content=ft.Text("Log in", color="#7189FF", weight=ft.FontWeight.BOLD), 
                                            on_tap=lambda e: self.page.run_task(self.flip_card, e)
                                        )
                                    ], 
                                    spacing=5,
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            ],
                            spacing=15
                        ),
                        margin=ft.margin.only(top=30)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )

        # --- 3. MAIN CARD CONTAINER ---
        self.card_container = ft.Container(
            content=self.login_view, 
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
            width=370,
            # Animation properties for the flip
            scale=ft.Scale(scale=1),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        return ft.View(
            "/login-admin" if self.type == 0 else "/login-resident",
            [
                ft.Row(
                    [
                        get_icon(64, True, 18, 16, 24, 18, ft.margin.only(bottom=30)), 
                        self.card_container
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=70
                )
            ],
            appbar=ft.AppBar(
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, 
                    icon_color=ft.Colors.GREY_700,
                    on_click=lambda _: self.page.go("/")
                ),
                bgcolor=ft.Colors.TRANSPARENT,
                elevation=0
            ),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor="#FFFBEB"
        )

    async def flip_card(self, e):
        """Simulates a flip by shrinking X-scale to 0, swapping content, and expanding back."""
        # 1. Shrink width to 0 (Turn to edge)
        self.card_container.scale = ft.Scale(scale_x=0, scale_y=1)
        self.card_container.update()
        
        await asyncio.sleep(0.3) # Wait for animation to finish
        
        # 2. Swap Content
        if self.is_registering:
            self.card_container.content = self.login_view
            self.is_registering = False
        else:
            self.card_container.content = self.register_view
            self.is_registering = True
        
        # 3. Expand width back to 1 (Turn to face)
        self.card_container.scale = ft.Scale(scale_x=1, scale_y=1)
        self.card_container.update()

    async def check_login(self, loginTF, passwordTF):
        login_val = loginTF.value.strip()
        password = passwordTF.value

        if login_val == "":
            loginTF.error_text = "Please enter your username!" if self.type == 1 else "Please enter your email!"
            self.page.update()
            return
        
        # --- ADMIN LOGIN (EMAIL) ---
        if self.type == 0:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if not re.fullmatch(regex, login_val):
                loginTF.error_text = "Please enter a valid email!"
                self.page.update()
                return

            if login_val != self.admin_email or password != self.admin_password:
                create_banner(self.page, ft.Colors.RED_100, ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, color=ft.Colors.RED), "No user found! Double check your email or password.", ft.Colors.RED)
                loginTF.error_text = "No user found!"
                passwordTF.error_text = "Incorrect email or password!"
                passwordTF.value = ""
                self.page.update()
                return
            
            loginTF.error_text = ""
            passwordTF.error_text = ""
            self.page.go("/active-admin")
            self.page.update()
            return

        # --- RESIDENT LOGIN (USERNAME) ---
        if self.type == 1:
            user_data = await self.page.data.get_user_by_name(login_val)

            if len(user_data) == 0 or user_data[0][3] != password:
                create_banner(self.page, ft.Colors.RED_100, ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, color=ft.Colors.RED), "No user found! Double check your username or password.", ft.Colors.RED)
                loginTF.error_text = "No user found!"
                passwordTF.error_text = "Incorrect username or password!"
                passwordTF.value = ""
                self.page.update()
                return
            
            loginTF.error_text = ""
            passwordTF.error_text = ""

            self.page.data.set_active_user(user_data[0][0])
            self.page.go("/active-resident")
            self.page.update()

    # UPDATED: Added access_key_tf parameter
    async def sign_up(self, user_tf, email_tf, phone_tf, access_key_tf, pass_tf, confirm_tf):
        username = user_tf.value.strip()
        email = email_tf.value.strip()
        phone = phone_tf.value.strip()
        access_key = access_key_tf.value.strip()
        password = pass_tf.value
        confirm_password = confirm_tf.value

        user_tf.error_text = ""
        email_tf.error_text = ""
        phone_tf.error_text = ""
        access_key_tf.error_text = ""
        pass_tf.error_text = ""
        confirm_tf.error_text = ""
        has_error = False
        
        # --- 1. ACCESS KEY VALIDATION (New) ---
        if access_key != self.admin_email:
            access_key_tf.error_text = "Invalid Landlord Access Key"
            has_error = True

        if len(username) < 3 or len(username) > 24:
            user_tf.error_text = "Username must be > 3 and < 24 chars"
            has_error = True

        res = await self.page.data.get_user_by_name(username)
        if len(res) > 0:
            user_tf.error_text = "Username already exists"
            has_error = True

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if email == "" or not re.fullmatch(regex, email):
            email_tf.error_text = "Please enter a valid email"
            has_error = True

        res = await self.page.data.get_user_by_email(email)
        if len(res) > 0:
            email_tf.error_text = "Email already in use"
            has_error = True
            
        if len(phone) < 10:
            phone_tf.error_text = "Enter valid phone number"
            has_error = True

        if len(password) < 6:
            pass_tf.error_text = "Password must be 6+ chars"
            has_error = True

        if password != confirm_password:
            confirm_tf.error_text = "Passwords do not match"
            has_error = True

        if has_error:
            self.page.update()
            return

        # Pass phone number to create_user
        await self.page.data.create_user(username, email, password, phone)
        
        # Reset fields and flip back
        user_tf.value = ""
        email_tf.value = ""
        phone_tf.value = ""
        access_key_tf.value = ""
        pass_tf.value = ""
        confirm_tf.value = ""
        
        await self.flip_card(None) # Go back to login
        create_banner(self.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.PERSON_ADD_ALT_1_OUTLINED, color=ft.Colors.GREEN), f"Account created! Please log in as {username}", ft.Colors.GREEN_500)
        self.page.update()

    def get_type(self):
        return self.type

    def change_type(self, type):
        self.type = type
import flet as ft

class PageHandler:
    def __init__(self, page: ft.Page):
        self.page = page


    def get_icon(self, icon_size=24, isColumn=True, radius=10, pad=8, text1_size=12, text2_size=9, marg=ft.margin.only(0, 0, 0, 0)):
        icon = ft.Container(
            ft.Image(
                src=f"assets/icon{icon_size}.png",
                color=ft.Colors.WHITE
            ),
            bgcolor="#FF6900",
            border_radius=radius,
            padding=pad
        )

        text1 = ft.Text("DormHub", color="#FF6900", size=text1_size)
        text2 = ft.Text("Your cozy dorm management system", color=ft.Colors.BLACK, size=text2_size)

        return ft.Container(
            ft.Column(
                [
                    ft.Column([icon, text1], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    text2
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            margin=marg
        )


    def set_root_page(self):
        admin_card = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Image(src="assets/admin.png", color="#FF6900"), border_radius=50, padding=12, bgcolor="#FFEDD4"),
                    ft.Text("Admin Dashboard", weight=ft.FontWeight.BOLD, size=16, color="#FF6900"),
                    ft.Text("Manage rooms, residents bookings, maintenance, and finances", size=12, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ft.FilledButton("Continue as Admin", width=320, height=30, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/login-admin"))
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            width=340,
            height=210,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=[
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                )
            ]
        )

        resident_card = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Image(src="assets/resident.png", color="#FE9A00"), border_radius=50, padding=12, bgcolor="#FEF3C6"),
                    ft.Text("Resident Dashboard", weight=ft.FontWeight.BOLD, size=16, color="#FE9A00"),
                    ft.Text("View your room, pay rent, submit requests, and connect with housemates", size=12, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ft.FilledButton("Continue as Resident", width=320, height=30, bgcolor="#FE9A00", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/login-resident"))
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            width=340,
            height=210,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=[
                ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                )
            ]
        )

        cards_row = ft.Row(
            [
                admin_card,
                resident_card
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )

        self.page.views.append(
            ft.View(
                "/",
                [
                    ft.Container(self.get_icon(), margin=ft.margin.only(top=100)),
                    cards_row
                ],
                spacing=40,
                bgcolor="#FFFAEA",
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()


    def show_login_page(self, type=1):
        login_card = ft.Container(
            ft.Column(
                [
                    ft.Text("Log in as Admin" if type == 0 else "Log in as Resident", weight=ft.FontWeight.BOLD, size=24, color=ft.Colors.BLACK),
                    ft.Container(ft.Column(
                            [
                                ft.TextField(label="Admin Username or Email" if type == 0 else "Username or Email", hint_text="Enter admin username or email" if type == 0 else "Enter your username or email", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.EMAIL_OUTLINED, color="#B8B8C1"), height=45, width=340),
                                ft.TextField(label="Admin Password" if type == 0 else "Password", hint_text="Enter admin password" if type == 0 else "Enter your password", hint_style=ft.TextStyle(color="#B8B8C1"), text_style=ft.TextStyle(color=ft.Colors.BLACK), border_radius=10, border_width=0, bgcolor="#F3F3F5", prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINED, color="#B8B8C1"), height=45, width=340),
                            ],
                            spacing=25
                        ),
                        margin=ft.margin.only(top=50)
                    ),
                    ft.Container(ft.Column(
                            [
                                ft.FilledButton("Log In", width=340, height=45, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE, on_click=lambda e: self.page.go("/")),
                                ft.Row([ft.Text("Don't have an account?"), ft.GestureDetector(content=ft.Text("Sign Up", color="#7189FF"), on_tap=lambda e: print("clicked"))], spacing=3) if type == 1 else ft.Row()
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
                "/login-admin" if type == 0 else "/login-resident",
                [
                    ft.Row([self.get_icon(64, True, 18, 16, 24, 18, ft.margin.only(bottom=30)), login_card])
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                bgcolor="#FFFAEA"
            )
        )
        self.page.update()

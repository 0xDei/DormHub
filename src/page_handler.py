import flet as ft

def get_icon(icon_size=24, isColumn=True):
    icon = ft.Container(
        ft.Image(
            src=f"assets/icon{icon_size}.png",
            color=ft.Colors.WHITE
        ),
        bgcolor="#FF6900",
        border_radius=10,
        padding=8
    )

    text1 = ft.Text("DormHub", color="#FF6900", size=icon_size/2)
    text2 = ft.Text("Your cozy dorm management system", color=ft.Colors.BLACK, size=icon_size/2.5)

    return ft.Column(
        [
            ft.Column([icon, text1], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            text2
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def set_root_page(page: ft.Page):

    admin_card = ft.Container(
        ft.Column(
            [
                ft.Container(ft.Image(src="assets/admin.png", color="#FF6900"), border_radius=50, padding=12, bgcolor="#FFEDD4"),
                ft.Text("Admin Dashboard", weight=ft.FontWeight.BOLD, size=16, color="#FF6900"),
                ft.Text("Manage rooms, residents bookings, maintenance, and finances", size=12, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                ft.FilledButton("Continue as Admin", width=320, height=30, bgcolor="#FF6900", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE)
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
                ft.FilledButton("Continue as Resident", width=320, height=30, bgcolor="#FE9A00", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7), text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)), color=ft.Colors.WHITE)
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

    page.views.append(
        ft.View(
            "/",
            [
                ft.Container(get_icon(), margin=ft.margin.only(top=100)),
                cards_row
            ],
            spacing=40,
            bgcolor="#FFFAEA",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()
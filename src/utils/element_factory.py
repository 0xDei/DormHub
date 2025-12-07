import flet as ft
from pages.components.navbar_button import NavBarButton

active_banner = None

# this might be unecessary and makes things more complicated
def get_icon(icon_size=64, isColumn=True, radius=16, pad=16, text1_size=20, text2_size=16, marg=ft.margin.only(0, 0, 0, 0)):
    icon = ft.Container(
        ft.Image(
            src=f"../assets/icon{icon_size}.png",
            color=ft.Colors.WHITE
        ),
        bgcolor="#FF6900",
        border_radius=radius,
        padding=pad
    )

    text1 = ft.Text("DormHub", color="#FF6900", size=text1_size, weight=ft.FontWeight.W_700)
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

def get_navbar_icon(isAdmin):
    icon = ft.Container(
        ft.Image(
            src=f"../assets/icon24.png",
            color=ft.Colors.WHITE
        ),
        bgcolor="#FF6900" if isAdmin else "#FE9A00",
        border_radius=10,
        padding=8
    )

    text1 = ft.Text("DormHub", color="#FF6900" if isAdmin else "#FE9A00", size=14, weight=ft.FontWeight.W_700)
    text2 = ft.Text("Admin Portal" if isAdmin else "Resident Portal", size=10)

    return ft.Container(
        ft.Row(
            [
                icon,
                ft.Column(
                    [text1, text2],
                    spacing=0
                )
            ]
        )
    )

def create_info_card(name, content, icon, icon_placement, bgcolor, width, height):

    card_name = ft.Column([ft.Text(name, size=12, color=ft.Colors.GREY_600), *content], spacing=0, expand=True)
    card_icon = ft.Container(icon, bgcolor=bgcolor, border_radius=7, width=icon.size * 1.5, height=icon.size * 1.5)
    
    row_content = [card_icon, card_name]
    if icon_placement == "right": row_content = [card_name, card_icon]    

    return ft.Container(
        ft.Row(row_content),
        padding=ft.padding.only(left=20, right=20, top=18, bottom=20),
        border_radius=10,
        width=width,
        height=height,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(2, "#FEF3C6")
    )

def create_remark(remark, color, bgcolor):
    return ft.Container(ft.Text(remark, weight=ft.FontWeight.BOLD, size=12, color=color, text_align=ft.TextAlign.CENTER), padding=ft.padding.only(left=8, right=8), height=17, bgcolor=bgcolor, border_radius=50, alignment=ft.alignment.center)

def create_banner(page, color, icon, text, buttonColor):
    global active_banner

    close_active_banner(page)
    banner = ft.Banner(bgcolor=color, leading=icon, content=ft.Text(text), actions=[ft.TextButton(text="Dismiss", style=ft.ButtonStyle(color=buttonColor), on_click=lambda e: page.close(banner))])
    page.open(banner)

    active_banner = banner

def close_active_banner(page):
    global active_banner

    if active_banner != None: 
        page.close(active_banner)
        active_banner = None

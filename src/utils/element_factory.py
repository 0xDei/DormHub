import flet as ft

def get_icon(icon_size=24, isColumn=True, radius=10, pad=8, text1_size=12, text2_size=9, marg=ft.margin.only(0, 0, 0, 0)):
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
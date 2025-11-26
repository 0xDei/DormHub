import flet as ft
from database import get_token

main_icon = ft.Container([
        ft.Icons.HOUSE
    ],
    bgcolor = "#FF6900",
    width = 32,
    height = 32 
)

def set_root_page(page: ft.Page):
    if get_token() is None:
        page.views.append(
            ft.View(
                "/",
                [
                    main_icon
                ]
            )
        )
    else:
        print("TODO")
    
    page.update()
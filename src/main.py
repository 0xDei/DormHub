import flet as ft

from database import Database
from page_handler import PageHandler
from utils.element_factory import close_active_banner

def main(page: ft.Page):
    page.title = "DormHub"
    page.window.width = 900
    page.window.height = 720
    page.window.resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT

    page.data = Database()
    ph = PageHandler(page)

    async def route_change(route):
        try:
            page.views.clear()
            close_active_banner(page)

            match page.route:
                case '/':
                    page.views.append(await ph.set_root_page())
                case "/login-admin": 
                    page.views.append(await ph.show_login_page(0))
                case "/login-resident": 
                    page.views.append(await ph.show_login_page(1))
                case "/active-admin": 
                    page.views.append(await ph.show_admin_page())
                case "/active-resident": 
                    page.views.append(await ph.show_resident_page())

            page.update()
        except Exception as e: print("Error: ", e)


    def view_pop(e):
        page.views.pop()
        if len(page.views) == 0:
            return
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)
    page.update()

if __name__ == "__main__":
    ft.app(main)
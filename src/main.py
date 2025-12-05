import flet as ft

from database import Database
from page_handler import PageHandler
from utils.element_factory import close_active_banner

def main(page: ft.Page):
    page.title = "DormHub"
    page.window.width = 900
    page.window.height = 720
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT

    page.data = Database()
    page.data.set_active_user(2)
    ph = PageHandler(page)

    async def rout_change(route):
        try:
            page.views.clear()
            close_active_banner(page)
            await ph.set_root_page()
            if page.route == "/login-admin": await ph.show_login_page(0)
            if page.route == "/login-resident": await ph.show_login_page(1)

            if page.route == "/active-admin": await ph.show_admin_page()
            if page.route == "/active-resident": await ph.show_resident_page()
        except Exception as e: print("Error: ", e)


    def view_pop():
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = rout_change
    page.on_view_pop = view_pop

    page.go(page.route)
    page.update()

if __name__ == "__main__":
    ft.app(main)
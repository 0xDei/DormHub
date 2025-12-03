import flet as ft
from page_handler import PageHandler


def main(page: ft.Page):
    page.title = "DormHub"
    page.bgcolor = "#FFFAEA"
    page.window.width = 1280
    page.window.height = 720
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT

    ph = PageHandler(page)

    def rout_change(route):
        try:
            page.views.clear()
            ph.set_root_page()
            if page.route == "/login-admin": ph.show_login_page(0)
            if page.route == "/login-resident": ph.show_login_page(1)
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
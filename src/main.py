import flet as ft
import page_handler as ph


def main(page: ft.Page):
    page.title = "DormHub"
    page.window.bgcolor = "#FFFAEA"

    def rout_change(route):
        page.views.clear()
        ph.set_root_page(page)

        if page.route == "/login-admin":
            print("Todo: Admin")
        if page.route == "/login-user":
            print("Todo: User")

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
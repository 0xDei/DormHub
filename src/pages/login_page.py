import flet as ft

class LoginPage:
    def __init__(self, page: ft.Page):
        self.page = page
        
        self.page.title = "DormHub: Login"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.center()
        
        
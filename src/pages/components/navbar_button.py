import flet as ft

active_button = None

class NavBarButton(ft.Container):
    def __init__(self, icon=None, name="Button", callback=None):

        super().__init__()

        self.is_selected = False

        self.callback = callback
        self.padding=ft.padding.only(top=7, left=10, right=10, bottom=7)
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = 7
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE)
        self.margin = ft.margin.only(bottom=-5)

        self.content = ft.Row(
            [
                icon if isinstance(icon, ft.Image) else ft.Icon(icon, size=24, color=ft.Colors.GREY_700),
                ft.Text(name, size=12, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_600)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.on_hover = self.hover
        self.on_click = self.click


    def hover(self, e):
        if self.is_selected: return

        self.bgcolor = "#FEF3C6" if e.data == "true" else ft.Colors.WHITE
        
        self.content.controls[0].color = "#E78B28" if e.data == "true" else ft.Colors.GREY_700
        self.content.controls[1].color = "#E78B28" if e.data == "true" else ft.Colors.GREY_600

        self.update()


    def click(self, e):
        global active_button
        if self.is_selected: return

        if active_button != None: active_button.set_active(False)
        self.set_active(True)

        if self.callback != None: self.callback.__call__(e)


    def set_active(self, is_active):
        global active_button
        
        self.is_selected = is_active

        self.bgcolor = "#FEF3C6" if is_active else ft.Colors.WHITE
        self.content.controls[0].color = "#E78B28" if is_active else ft.Colors.GREY_700
        self.content.controls[1].color = "#E78B28" if is_active else ft.Colors.GREY_600
        
        if is_active: active_button = self

        self.update()
        
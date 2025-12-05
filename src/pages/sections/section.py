import flet as ft

class Section(ft.Container):
    def __init__(self):
        super().__init__()
        
        self.bgcolor=ft.Colors.BLACK
        self.height = 685
        self.expand = True
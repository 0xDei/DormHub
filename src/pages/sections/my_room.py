import flet as ft

class MyRoom(ft.Container):
    def __init__(self, resident_page):
        super().__init__()

        self.resident_page = resident_page

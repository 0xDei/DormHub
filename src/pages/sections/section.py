import flet as ft

class Section(ft.Container):
    def __init__(self):
        super().__init__()
        
        self.margin = ft.margin.only(top=10)
        self.padding = ft.padding.only(left=30, right=30)
        self.expand = True
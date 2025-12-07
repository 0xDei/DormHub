import flet as ft

class Section(ft.Container):
    def __init__(self):
        super().__init__()
        
        self.margin = ft.margin.only(top=10)
        # Reduced padding to minimal to fit content better
        self.padding = ft.padding.all(10)
        self.expand = True
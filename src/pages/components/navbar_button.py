import flet as ft

class NavBarButton(ft.Container):
    def __init__(self, icon, text, func, selected=False, selected_bg="#FEFBE8", selected_icon="#FF6900", badge_count=0):
        super().__init__()
        self.func = func
        self.callback = func
        self.icon = icon
        self.text = text
        self.selected = selected
        self.selected_bg = selected_bg
        self.selected_icon = selected_icon
        self.badge_count = badge_count

        self.padding = 10
        self.border_radius = 10
        self.ink = True
        
        self.icon_color = ft.Colors.GREY_400
        self.text_color = ft.Colors.GREY_400
        self.bg_color = ft.Colors.TRANSPARENT

        if self.selected:
            self.icon_color = self.selected_icon
            self.text_color = ft.Colors.BLACK
            self.bg_color = self.selected_bg

        self.bgcolor = self.bg_color
        
        # Numeric Badge
        self.badge = ft.Container(
            content=ft.Text(
                str(self.badge_count) if self.badge_count < 99 else "99+", 
                color="white", 
                size=10, 
                weight=ft.FontWeight.BOLD
            ),
            bgcolor="red", 
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            visible=self.badge_count > 0,
            alignment=ft.alignment.center,
            # FIXED: Offset (x, y) moves the badge relative to its size
            # y=-0.5 moves it up by 50% of its height (superscript effect)
            offset=ft.Offset(0, -0.5) 
        )

        self.content = ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(self.icon, color=self.icon_color),
                        ft.Text(self.text, color=self.text_color, size=14, weight=ft.FontWeight.W_600)
                    ],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.badge 
            ],
            # Use START to place items (Icon+Text and Badge) next to each other
            alignment=ft.MainAxisAlignment.START, 
            spacing=0, # Tight spacing
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.on_click = self.click

    def click(self, e):
        if self.callback != None: self.callback.__call__(e)

    def set_badge_count(self, count):
        """Updates the badge count visibility and text."""
        self.badge_count = count
        self.badge.content.value = str(count) if count < 99 else "99+"
        self.badge.visible = count > 0
        self.badge.update()

    def select(self):
        """Highlights the button as selected."""
        self.selected = True
        self.bgcolor = self.selected_bg
        # Access Icon inside the nested Row
        self.content.controls[0].controls[0].color = self.selected_icon 
        self.content.controls[0].controls[1].color = ft.Colors.BLACK
        self.update()

    def deselect(self):
        """Removes highlight from the button."""
        self.selected = False
        self.bgcolor = ft.Colors.TRANSPARENT
        self.content.controls[0].controls[0].color = ft.Colors.GREY_400
        self.content.controls[0].controls[1].color = ft.Colors.GREY_400
        self.update()
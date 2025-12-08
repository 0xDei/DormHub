import flet as ft
from pages.sections.section import Section
from utils.element_factory import create_info_card

class AccessKeySection(Section):
    def __init__(self, admin_page):
        super().__init__()
        self.admin_page = admin_page
        
        # Retrieve the key stored in the admin_page instance
        access_key = self.admin_page.admin_access_key 

        header = ft.Row([
            ft.Column([
                ft.Text("Access Key", color="#E78B28", size=16, weight="bold"),
                ft.Text("Share this unique 6-digit key with your residents for registration.", size=12, weight="w500")
            ], spacing=1, expand=True)
        ])

        # Key Display Card
        key_display = ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text("Your Unique Landlord Access Key", size=14, color=ft.Colors.GREY_600),
                    ft.Row([
                        ft.Icon(ft.Icons.KEY, size=24, color="#FF6900"),
                        # Display the actual access key
                        ft.Text(access_key, size=20, weight="bold", expand=True), # Increased size for visibility
                        # Button to copy the key to the clipboard
                        ft.IconButton(ft.Icons.CONTENT_COPY, tooltip="Copy Key", on_click=lambda e: self.copy_key_to_clipboard(access_key))
                    ], spacing=10, alignment=ft.MainAxisAlignment.START)
                ], spacing=10),
                padding=20
            ),
            elevation=2
        )

        self.content = ft.Container(
            ft.Column([header, key_display], spacing=20, expand=True),
            padding=20, expand=True
        )

    def copy_key_to_clipboard(self, key):
        # Uses Flet's clipboard functionality
        self.admin_page.page.set_clipboard(key)
        # Show a confirmation snackbar
        self.admin_page.page.snack_bar = ft.SnackBar(ft.Text("Access Key copied to clipboard!"), duration=1000)
        self.admin_page.page.snack_bar.open = True
        self.admin_page.page.update()
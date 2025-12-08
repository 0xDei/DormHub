import flet as ft
import json
from pages.sections.section import Section
from utils.element_factory import create_banner

class Settings(Section):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller # AdminPage or ResidentPage instance
        
        # Check if the user is a Resident (has an ID and database entry)
        self.is_resident = hasattr(self.controller, 'id') and self.controller.id is not None
        
        self.username = self.controller.username if self.is_resident else "Administrator"
        self.email = self.controller.email if self.is_resident else "admin@dormhub.com"

        header = ft.Row([
            ft.Column([
                ft.Text("Settings", color="#E78B28", size=16, weight="bold"),
                ft.Text("Application preferences and info", size=12, weight="w500")
            ], spacing=1, expand=True)
        ])

        # Notification state
        notify_val = True
        if self.is_resident and self.controller.data:
            notify_val = self.controller.data.get("notifications_enabled", True)

        self.notify_switch = ft.Switch(
            value=notify_val, 
            active_color="#FF6900",
            on_change=self.toggle_notifications,
            disabled=not self.is_resident
        )

        # Store reference to profile tile to update it dynamically
        self.profile_tile = ft.ListTile(
            leading=ft.Icon(ft.Icons.PERSON_OUTLINE, color=ft.Colors.GREY_700),
            title=ft.Text("Account Profile"),
            subtitle=ft.Text(f"Logged in as {self.username}"),
            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color="grey"),
            on_click=self.show_profile_dialog,
            disabled=not self.is_resident
        )

        # Settings Options List
        settings_list = ft.Column([
            self.profile_tile,
            ft.Divider(height=1, thickness=1, color="#eee"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.GREY_700),
                title=ft.Text("Security"),
                subtitle=ft.Text("Change password"),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color="grey"),
                on_click=self.show_security_dialog,
                disabled=not self.is_resident
            ),
            ft.Divider(height=1, thickness=1, color="#eee"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=ft.Colors.GREY_700),
                title=ft.Text("Notifications"),
                subtitle=ft.Text("Manage alert preferences"),
                trailing=self.notify_switch
            ),
            ft.Divider(height=1, thickness=1, color="#eee"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.GREY_700),
                title=ft.Text("About DormHub"),
                subtitle=ft.Text("Version 1.0.0"),
                on_click=self.show_about_dialog
            )
        ], spacing=0)

        self.content = ft.Container(
            ft.Column([
                header,
                ft.Container(
                    settings_list,
                    bgcolor="white",
                    border_radius=10,
                    padding=5,
                    border=ft.border.all(1, "#eee")
                )
            ], spacing=20, expand=True),
            padding=20,
            expand=True
        )

    # --- Actions ---

    async def toggle_notifications(self, e):
        """Save notification preference."""
        if self.is_resident:
            self.controller.data["notifications_enabled"] = self.notify_switch.value
            try:
                await self.controller.page.data.update_user(
                    self.controller.id,
                    self.controller.username,
                    self.controller.email,
                    self.controller.password,
                    self.controller.data
                )
                create_banner(self.controller.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color="green"), "Preferences saved!", ft.Colors.GREEN)
            except Exception as ex:
                print(f"Error saving preferences: {ex}")

    async def show_profile_dialog(self, e):
        if not self.is_resident: return

        user_tf = ft.TextField(label="Username", value=self.controller.username)
        email_tf = ft.TextField(label="Email", value=self.controller.email)

        async def save_profile(e):
            if not user_tf.value or not email_tf.value:
                user_tf.error_text = "Required" if not user_tf.value else None
                email_tf.error_text = "Required" if not email_tf.value else None
                user_tf.update()
                email_tf.update()
                return

            try:
                await self.controller.page.data.update_user(
                    self.controller.id,
                    user_tf.value,
                    email_tf.value,
                    self.controller.password,
                    self.controller.data
                )
                
                # 1. Update Controller State
                self.controller.username = user_tf.value
                self.controller.email = email_tf.value
                
                # 2. Update Settings UI immediately
                self.profile_tile.subtitle.value = f"Logged in as {self.controller.username}"
                self.profile_tile.update()

                # 3. Update Navbar immediately
                if hasattr(self.controller, 'navbar'):
                    self.controller.navbar.update_user_display()
                
                self.controller.page.close(dlg)
                create_banner(self.controller.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color="green"), "Profile updated successfully!", ft.Colors.GREEN)
                
            except Exception as ex:
                print(ex)

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Profile"),
            content=ft.Column([user_tf, email_tf], tight=True, width=300),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.controller.page.close(dlg)),
                ft.FilledButton("Save", bgcolor="#FF6900", on_click=save_profile)
            ]
        )
        self.controller.page.open(dlg)

    async def show_security_dialog(self, e):
        if not self.is_resident: return

        old_pass = ft.TextField(label="Current Password", password=True, can_reveal_password=True)
        new_pass = ft.TextField(label="New Password", password=True, can_reveal_password=True)
        confirm_pass = ft.TextField(label="Confirm New Password", password=True, can_reveal_password=True)

        async def change_password(e):
            if old_pass.value != self.controller.password:
                old_pass.error_text = "Incorrect password"
                old_pass.update()
                return
            
            if len(new_pass.value) < 6:
                new_pass.error_text = "Must be at least 6 chars"
                new_pass.update()
                return

            if new_pass.value != confirm_pass.value:
                confirm_pass.error_text = "Passwords do not match"
                confirm_pass.update()
                return

            try:
                await self.controller.page.data.update_user(
                    self.controller.id,
                    self.controller.username,
                    self.controller.email,
                    new_pass.value,
                    self.controller.data
                )
                
                self.controller.password = new_pass.value
                self.controller.page.close(dlg)
                create_banner(self.controller.page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK, color="green"), "Password changed successfully!", ft.Colors.GREEN)
            except Exception as ex:
                print(ex)

        dlg = ft.AlertDialog(
            title=ft.Text("Change Password"),
            content=ft.Column([old_pass, new_pass, confirm_pass], tight=True, width=300),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.controller.page.close(dlg)),
                ft.FilledButton("Update", bgcolor="#FF6900", on_click=change_password)
            ]
        )
        self.controller.page.open(dlg)

    async def show_about_dialog(self, e):
        dlg = ft.AlertDialog(
            title=ft.Text("About DormHub"),
            content=ft.Container(
                ft.Column([
                    ft.Image(src="../assets/icon64.png", width=64, height=64),
                    ft.Text("DormHub v1.0.0", weight="bold", size=16),
                    ft.Text("A cozy dormitory management system designed to make life easier for landlords and residents.", text_align="center"),
                    ft.Text("© 2025 DormHub Inc.", color="grey", size=12)
                ], horizontal_alignment="center", spacing=10, tight=True),
                width=300, padding=10
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.controller.page.close(dlg))
            ]
        )
        self.controller.page.open(dlg)
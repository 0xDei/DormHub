import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section

class AdminAnnouncements(Section):
    def __init__(self, admin_page):
        super().__init__()
        self.admin_page = admin_page
        self.admin_id = admin_page.page.data.get_active_user() # Get current Admin ID
        self.reply_parent_id = None # State for tracking reply target
        
        header = ft.Row([
            ft.Column([
                ft.Text("Announcements", color="#E78B28", size=16, weight="bold"),
                ft.Text("Post updates for residents", size=12, weight="w500")
            ], spacing=1, expand=True),
            ft.FilledButton("New Post", icon=ft.Icons.ADD, bgcolor="#FF6900", on_click=self.show_add_dialog)
        ])

        self.posts_list = ft.ListView(spacing=15, expand=True)

        self.content = ft.Container(
            ft.Column([header, self.posts_list], spacing=20, expand=True),
            padding=20, expand=True
        )

        self.admin_page.page.run_task(self.load_data)

    async def load_data(self):
        self.posts_list.controls.clear()
        # MODIFIED: Filter posts to only those created by this admin
        self.admin_id = self.admin_page.page.data.get_active_user()
        posts = await self.admin_page.page.data.get_announcements(admin_user_id=self.admin_id)
        
        if not posts:
            self.posts_list.controls.append(ft.Container(ft.Text("No announcements yet.", color="grey"), alignment=ft.alignment.center, padding=50))
        else:
            for p in posts:
                # p: id(0), admin_user_id(1), title(2), content(3), date(4), likes(5)
                pid = p[0]
                
                # FIX: Safely parse likes field (p[5]). Handle non-string/corrupt data (TypeError fix).
                likes_raw = p[5]
                likes = []
                if isinstance(likes_raw, str):
                    try:
                        likes = json.loads(likes_raw)
                    except json.JSONDecodeError:
                        likes = []
                
                likes_count = len(likes)
                
                # FIX: Safely convert timestamp (p[4]). If invalid, defaults to 0 (Unix epoch start).
                date_raw = p[4]
                try:
                    dt = datetime.fromtimestamp(int(date_raw)).strftime("%b %d, %Y")
                except (ValueError, TypeError):
                    dt = "N/A"
                
                # Use updated indices: title(2), content(3), date(4)
                comments = await self.admin_page.page.data.get_comments(pid)
                comment_count = len(comments)
                
                card = ft.Container(
                    ft.Column([
                        ft.Row([
                            ft.Text(p[2], weight="bold", size=16, expand=True), # title 
                            # Updated: Calls show_delete_confirmation instead of delete_post directly
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE, 
                                icon_color="red", 
                                on_click=lambda e, pid=pid: self.admin_page.page.run_task(self.show_delete_confirmation, pid)
                            )
                        ]),
                        ft.Text(p[3], size=13, color="#444444"), # content
                        ft.Divider(),
                        ft.Row([
                            ft.Text(dt, size=11, color="grey"),
                            ft.Row([
                                ft.Icon(ft.Icons.FAVORITE, size=14, color="red"),
                                ft.Text(f"{likes_count}", size=11),
                                ft.Container(width=10),
                                ft.Icon(ft.Icons.CHAT_BUBBLE, size=14, color="blue"),
                                ft.Text(f"{comment_count}", size=11),
                                ft.TextButton("View Comments", style=ft.ButtonStyle(color="blue"), on_click=lambda e, i=pid: self.admin_page.page.run_task(self.show_comments, i))
                            ], spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        ], alignment="spaceBetween")
                    ]),
                    padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#eee")
                )
                self.posts_list.controls.append(card)
        self.admin_page.page.update()

    async def show_add_dialog(self, e):
        title = ft.TextField(label="Title")
        content = ft.TextField(label="Content", multiline=True, min_lines=3)
        
        async def post(e):
            if not title.value or not content.value: return
            # MODIFIED: Pass admin_id when creating announcement
            await self.admin_page.page.data.create_announcement(title.value, content.value, self.admin_id)
            self.admin_page.page.close(dlg)
            await self.load_data()

        dlg = ft.AlertDialog(
            title=ft.Text("New Announcement"),
            content=ft.Container(ft.Column([title, content], tight=True), width=400),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(dlg)),
                ft.FilledButton("Post", bgcolor="#FF6900", on_click=post)
            ]
        )
        self.admin_page.page.open(dlg)

    async def show_delete_confirmation(self, pid):
        """Shows a confirmation dialog before deleting an announcement."""
        
        async def confirm_delete(e):
            # Perform deletion
            await self.admin_page.page.data.delete_announcement(pid)
            self.admin_page.page.close(dlg)
            await self.load_data()

        dlg = ft.AlertDialog(
            title=ft.Text("Delete Announcement"),
            content=ft.Text("Are you sure you want to delete this post? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.admin_page.page.close(dlg)),
                ft.FilledButton("Delete", bgcolor="red", on_click=confirm_delete)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.admin_page.page.open(dlg)

    async def show_comments(self, pid):
        self.reply_parent_id = None # Reset
        comments_data = await self.admin_page.page.data.get_comments(pid)
        
        # Sort into parents and replies
        parents = [c for c in comments_data if c[6] is None] # parent_id is index 6
        replies = [c for c in comments_data if c[6] is not None]

        comment_list = ft.ListView(expand=True, spacing=10)

        # Helper defined before loop to avoid UnboundLocalError
        async def post_comment(e):
            if not new_comment_tf.value: return
            # Admin User ID = 0, Username = "Landlord"
            await self.admin_page.page.data.add_comment(pid, 0, "Landlord", new_comment_tf.value, self.reply_parent_id)
            self.admin_page.page.close(dlg)
            await self.load_data() 
            await self.show_comments(pid)

        new_comment_tf = ft.TextField(
            hint_text="Write as Landlord...", 
            text_size=12, border_radius=20, content_padding=10, expand=True,
            on_submit=lambda e: self.admin_page.page.run_task(post_comment, e)
        )
        
        if not comments_data:
            comment_list.controls.append(ft.Text("No comments yet.", color="grey", italic=True))
        else:
            for p in parents:
                p_dt = datetime.fromtimestamp(int(p[5])).strftime("%b %d %H:%M")
                p_id = p[0]
                
                comment_list.controls.append(self.create_comment_bubble(p[3], p[4], p_dt, p_id, new_comment_tf))

                # Render Replies for this parent
                p_replies = [r for r in replies if r[6] == p_id]
                for r in p_replies:
                    r_dt = datetime.fromtimestamp(int(r[5])).strftime("%b %d %H:%M")
                    comment_list.controls.append(
                        ft.Container(
                            self.create_comment_bubble(r[3], r[4], r_dt, p_id, new_comment_tf),
                            padding=ft.padding.only(left=20)
                        )
                    )

        dlg = ft.AlertDialog(
            title=ft.Text("Comments"),
            content=ft.Container(
                ft.Column([
                    comment_list,
                    ft.Row([new_comment_tf, ft.IconButton(ft.Icons.SEND, icon_color="#FF6900", on_click=lambda e: self.admin_page.page.run_task(post_comment, e))])
                ]),
                width=350, height=400
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.admin_page.page.close(dlg))]
        )
        self.admin_page.page.open(dlg)

    def create_comment_bubble(self, username, content, date_str, comment_id, tf_ref):
        def reply_click(e):
            self.reply_parent_id = comment_id
            tf_ref.prefix_text = f"Replying to {username}: "
            tf_ref.focus()
            tf_ref.update()

        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=12, color="blue" if username == "Landlord" else "black"),
                        ft.Text(username, weight="bold", size=12, color="blue" if username == "Landlord" else "black")
                    ], spacing=5),
                    ft.Text(date_str, size=10, color="grey")
                ], alignment="spaceBetween"),
                ft.Text(content, size=12),
                ft.Container(
                    ft.Text("Reply", size=10, color="blue", weight="bold"),
                    on_click=reply_click,
                    padding=ft.padding.only(top=2)
                )
            ], spacing=2),
            bgcolor="#F9F9F9", padding=10, border_radius=8
        )
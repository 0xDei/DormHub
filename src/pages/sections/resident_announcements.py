import flet as ft
from datetime import datetime
import json

from pages.sections.section import Section

class ResidentAnnouncements(Section):
    def __init__(self, resident_page):
        super().__init__()
        self.resident_page = resident_page
        self.user_id = resident_page.id
        self.reply_parent_id = None
        
        header = ft.Row([
            ft.Column([
                ft.Text("Community Board", color="#E78B28", size=16, weight="bold"),
                ft.Text("Latest news and updates", size=12, weight="w500")
            ], spacing=1)
        ])

        self.posts_list = ft.ListView(spacing=15, expand=True)

        self.content = ft.Container(
            ft.Column([header, self.posts_list], spacing=20, expand=True),
            padding=20, expand=True
        )

        self.resident_page.page.run_task(self.load_data)

    async def load_data(self):
        self.posts_list.controls.clear()
        posts = await self.resident_page.page.data.get_announcements()
        
        if not posts:
            self.posts_list.controls.append(ft.Container(ft.Text("No announcements yet.", color="grey"), alignment=ft.alignment.center, padding=50))
        else:
            for p in posts:
                # p: id, title, content, date, likes
                pid = p[0]
                likes = json.loads(p[4])
                is_liked = self.user_id in likes
                dt = datetime.fromtimestamp(int(p[3])).strftime("%b %d, %Y")
                
                comments = await self.resident_page.page.data.get_comments(pid)
                comment_count = len(comments)

                card = ft.Container(
                    ft.Column([
                        ft.Text(p[1], weight="bold", size=16),
                        ft.Text(p[2], size=13, color="#444444"),
                        ft.Container(height=5),
                        ft.Row([
                            ft.Text(dt, size=11, color="grey"),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.FAVORITE if is_liked else ft.Icons.FAVORITE_BORDER,
                                    icon_color="red" if is_liked else "grey",
                                    icon_size=20,
                                    on_click=lambda e, i=pid: self.resident_page.page.run_task(self.toggle_like, i)
                                ),
                                ft.Text(str(len(likes)), size=12),
                                ft.Container(width=10),
                                ft.IconButton(ft.Icons.CHAT_BUBBLE_OUTLINE, icon_size=20, icon_color="blue", on_click=lambda e, i=pid: self.resident_page.page.run_task(self.show_comments, i)),
                                ft.Text(str(comment_count), size=12),
                            ], spacing=0)
                        ], alignment="spaceBetween", vertical_alignment="center")
                    ]),
                    padding=15, bgcolor="white", border_radius=10, border=ft.border.all(1, "#eee")
                )
                self.posts_list.controls.append(card)
        self.resident_page.page.update()

    async def toggle_like(self, pid):
        await self.resident_page.page.data.toggle_like(pid, self.user_id)
        await self.load_data()

    async def show_comments(self, pid):
        self.reply_parent_id = None
        comments_data = await self.resident_page.page.data.get_comments(pid)
        
        parents = [c for c in comments_data if c[6] is None]
        replies = [c for c in comments_data if c[6] is not None]

        comment_list = ft.ListView(expand=True, spacing=10)
        
        new_comment_tf = ft.TextField(
            hint_text="Write a comment...", text_size=12, border_radius=20, content_padding=10, expand=True,
            on_submit=lambda e: self.resident_page.page.run_task(post_comment, e)
        )

        if not comments_data:
            comment_list.controls.append(ft.Text("No comments yet.", color="grey", italic=True))
        else:
            for p in parents:
                p_dt = datetime.fromtimestamp(int(p[5])).strftime("%b %d %H:%M")
                p_id = p[0]
                comment_list.controls.append(self.create_comment_bubble(p[3], p[4], p_dt, p_id, new_comment_tf))
                
                p_replies = [r for r in replies if r[6] == p_id]
                for r in p_replies:
                    r_dt = datetime.fromtimestamp(int(r[5])).strftime("%b %d %H:%M")
                    comment_list.controls.append(
                        ft.Container(
                            self.create_comment_bubble(r[3], r[4], r_dt, p_id, new_comment_tf),
                            padding=ft.padding.only(left=30)
                        )
                    )

        async def post_comment(e):
            if not new_comment_tf.value: return
            await self.resident_page.page.data.add_comment(pid, self.user_id, self.resident_page.username, new_comment_tf.value, self.reply_parent_id)
            self.resident_page.page.close(dlg)
            await self.load_data()
            await self.show_comments(pid)

        dlg = ft.AlertDialog(
            title=ft.Text("Comments"),
            content=ft.Container(
                ft.Column([
                    comment_list,
                    ft.Row([new_comment_tf, ft.IconButton(ft.Icons.SEND, icon_color="#FF6900", on_click=post_comment)])
                ]),
                width=350, height=400
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.resident_page.page.close(dlg))]
        )
        self.resident_page.page.open(dlg)

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
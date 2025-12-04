import flet as ft
import json

from pages.components.navbar import NavBar
from pages.components.navbar_button import NavBarButton

class ResidentPage:
    def __init__(self, page: ft.Page, user_id):
        self.page = page
        self.id = user_id
        self.username = None
        self.email = None
        self.password = None
        self.user_data = None

        # json.dumps(string) to encode

    async def load_data(self):
        res = await self.page.data.get_user_by_id(self.id)
        self.username = res[0][1]        
        self.email = res[0][2]        
        self.password = res[0][3]
        self.user_data = json.loads(res[0][4]) if res[0][4] != 'none' else {}

    async def show(self):
        self.page.views.append(
            ft.View(
                "/page-resident",
                [
                    NavBar(
                        isAdmin=False, 
                        user_data=[self.username, self.user_data], 
                        buttons=[
                            NavBarButton(ft.Icons.BED, "My Room", lambda e: print("clicked my room")),
                            NavBarButton(ft.Icons.CREDIT_CARD_ROUNDED, "Payments", lambda e: print("clicked payments")),
                            NavBarButton(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, "Requests", lambda e: print("clicked requests"))
                            #create_navbar_button(ft.Icons.BED, "Community", lambda e: print("clicked"))
                        ]
                    )
                ],
                bgcolor="#FFFBEB",
                padding=5
            )
        )
        self.page.update()
    

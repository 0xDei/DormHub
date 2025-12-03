import flet as ft
import json

from element_factory import *

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
                    ft.Text("Resident Page: Coming Soon...")
                ]
            )
        )

        self.page.update()
    

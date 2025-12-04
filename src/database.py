import aiomysql
import os
import aiofiles

import flet as ft
from utils.element_factory import *

class Database:
    def __init__(self):
        self.connected = False
        self.active_user = None

        base_path = os.getenv("FLET_APP_STORAGE_DATA")
        if base_path is None: base_path = os.getcwd()

        self.token_path = os.path.join(base_path, "token.txt")

        # connection holder
        self.pool = None

    def set_active_user(self, user_id):
        self.active_user = user_id


    def get_active_user(self):
        return self.active_user


    async def connect(self, page):
        if self.connected: return

        create_banner(page, ft.Colors.AMBER_100, ft.Image(src="assets/db-connect.png", color=ft.Colors.AMBER_900), "Attempting to connect to database...", ft.Colors.BLUE)
        try:
            self.pool = await aiomysql.create_pool(host="localhost", user="root", password="djpim!", db="dormhub_app", autocommit=True)
            create_banner(page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN), "You are now connected!", ft.Colors.GREEN_500)
            self.connected = True
        except Exception as e:
            create_banner(page, ft.Colors.RED_100, ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, color=ft.Colors.RED), f"Could not connect to database! Please check your internet connection.", ft.Colors.RED)


    async def create_user(self, username, email, password):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO users (username, email, password, data) VALUES (%s, %s, %s, %s)",
                    (username, email, password, "none")
                )


    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users")
                return await cur.fetchall()

    async def get_user_by_id(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM users WHERE id = %s",
                    (user_id,)
                )
                return await cur.fetchall()


    async def get_user_by_name(self, name, exact=True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if exact:
                    await cur.execute(
                        "SELECT * FROM users WHERE username = %s",
                        (name,)
                    )
                else: 
                    await cur.execute(
                        "SELECT * FROM users WHERE LOWER(username) LIKE %s",
                        ("%" + name.lower() + "%",)
                    )
                return await cur.fetchall()


    async def get_user_by_email(self, email):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (email,)
                )
                return await cur.fetchall()

    async def update_user(self, user_id, name, email, password, data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET username=%s, email=%s, password=%s, data=%s WHERE id=%s",
                    (name, email, password, data, user_id)
                )


    async def delete_user(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM users WHERE id=%s", (user_id,))

    # i don't know if I have enough time to implement a feature that will use this to store acount token and make them auto log in
    async def get_token(self):
        try:
            async with aiofiles.open(self.token_path, "r") as f:
                token = await f.read()
                return token.strip()
        except (FileNotFoundError, ValueError):
            return None


    async def set_token(self, token):
        async with aiofiles.open(self.token_path, "w") as f:
            await f.write(str(token))


    async def close(self):
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
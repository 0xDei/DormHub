import aiomysql
import os
import aiofiles
import json
from datetime import datetime
import random 
import string 

import flet as ft
from utils.element_factory import *

class Database:
    def __init__(self):
        self.connected = False
        self.active_user = None

        base_path = os.getenv("FLET_APP_STORAGE_DATA")
        if base_path is None: base_path = os.getcwd()

        self.token_path = os.path.join(base_path, "token.txt")
        self.pool = None

    def set_active_user(self, user_id):
        self.active_user = user_id

    def get_active_user(self):
        return self.active_user

    # NEW: Function to generate a unique 6-digit alphanumeric key
    def generate_access_key(self, length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    async def connect(self, page):
        if self.connected: return

        create_banner(page, ft.Colors.AMBER_100, ft.Image(src="assets/db-connect.png", color=ft.Colors.AMBER_900), "Attempting to connect to database...", ft.Colors.BLUE)
        try:
            self.pool = await aiomysql.create_pool(host="localhost", user="root", password="", db="DORMHUB__DATABASE", autocommit=True)
            create_banner(page, ft.Colors.GREEN_100, ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN), "You are now connected!", ft.Colors.GREEN_500)
            self.connected = True
            await self.create_tables()

        except Exception as e:
            create_banner(page, ft.Colors.RED_100, ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, color=ft.Colors.RED), f"Could not connect to database! Please check your internet connection.", ft.Colors.RED)

    async def create_tables(self):
        await self.custom_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT,
                username VARCHAR(24),
                email TEXT,
                password TEXT,
                data TEXT,
                PRIMARY KEY(id)
            )
        """)
        await self.custom_query("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT,
                admin_user_id INT DEFAULT 0, -- NEW COLUMN
                amenities TEXT,
                residents TEXT,
                bed_count INT DEFAULT 0,
                monthly_rent INT,
                current_status TEXT,
                thumbnail TEXT,
                PRIMARY KEY(id)
            )
        """)
        await self.custom_query("""
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT,
                room_id INT,
                issue TEXT,
                current_status TEXT,
                urgency TEXT,
                user_id INT,
                date_created TEXT,
                date_updated TEXT,
                PRIMARY KEY(id)
            )
        """)
        await self.custom_query("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INT AUTO_INCREMENT,
                admin_user_id INT DEFAULT 0,  -- ADDED COLUMN
                title TEXT,
                content TEXT,
                date_created TEXT,
                likes TEXT,
                PRIMARY KEY(id)
            )
        """)
        
        # Create comments table if it doesn't exist
        await self.custom_query("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT,
                announcement_id INT,
                user_id INT,
                username TEXT,
                content TEXT,
                date_created TEXT,
                parent_id INT DEFAULT NULL,
                PRIMARY KEY(id)
            )
        """)

        # --- MIGRATION FIX for announcements table ---
        try:
            # Check if admin_user_id exists
            await self.custom_query("SELECT admin_user_id FROM announcements LIMIT 1")
        except:
            print("Migrating Database: Adding 'admin_user_id' column to announcements table...")
            try:
                await self.custom_query("ALTER TABLE announcements ADD COLUMN admin_user_id INT DEFAULT 0")
                print("Migration successful.")
            except Exception as e:
                print(f"Migration failed: {e}")
        
        # --- MIGRATION FIX for rooms table ---
        try:
            await self.custom_query("SELECT admin_user_id FROM rooms LIMIT 1")
        except:
            print("Migrating Database: Adding 'admin_user_id' column to rooms table...")
            try:
                await self.custom_query("ALTER TABLE rooms ADD COLUMN admin_user_id INT DEFAULT 0")
                print("Migration successful.")
            except Exception as e:
                print(f"Migration failed: {e}")

        # --- MIGRATION FIX for comments table ---
        # Check if parent_id exists in comments (for existing databases)
        try:
            await self.custom_query("SELECT parent_id FROM comments LIMIT 1")
        except:
            print("Migrating Database: Adding 'parent_id' column to comments table...")
            try:
                await self.custom_query("ALTER TABLE comments ADD COLUMN parent_id INT DEFAULT NULL")
                print("Migration successful.")
            except Exception as e:
                print(f"Migration failed: {e}")

    async def custom_query(self, query, params=[]):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    # --- User Methods ---
    # MODIFIED: Added 'role' and optional 'linked_admin_id' for residents
    async def create_user(self, username, email, password, phone_number="N/A", role="resident", linked_admin_id=None): 
        async with self.pool.acquire() as conn:
            access_key = ""
            if role == "admin":
                access_key = self.generate_access_key()

            # Store the linked_admin_id ONLY for residents
            if role == "resident" and linked_admin_id is not None:
                admin_link = linked_admin_id
            else:
                admin_link = "N/A"
                
            data = {
                "role": role, 
                "access_key": access_key, 
                "linked_admin_id": admin_link, # NEW: Links resident to their admin
                "room_id": "N/A", "move_in_date": "N/A", "due_date": "N/A",
                "payment_history": [], "unpaid_dues": [], "phone_number": phone_number
            }
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO users (username, email, password, data) VALUES (%s, %s, %s, %s)",
                    (username, email, password, json.dumps(data))
                )
                
    # NEW METHOD: Retrieve Admin ID if key is valid
    async def get_admin_id_by_access_key(self, key):
        admin_users = await self.custom_query("SELECT id, data FROM users")
        
        for user in admin_users:
            user_id = user[0]
            try:
                user_data = json.loads(user[1])
                if user_data.get("role") == "admin" and user_data.get("access_key") == key:
                    return user_id
            except:
                continue
        return None

    async def get_all_users(self):
        return await self.custom_query("SELECT * FROM users")

    async def get_user_by_id(self, user_id):
        return await self.custom_query("SELECT * FROM users WHERE id = %s", (user_id,))

    async def get_user_by_name(self, name, exact=True):
        if exact: return await self.custom_query("SELECT * FROM users WHERE username = %s", (name,))
        else: return await self.custom_query("SELECT * FROM users WHERE LOWER(username) LIKE %s", ("%" + name.lower() + "%",))

    async def get_user_by_email(self, email):
        return await self.custom_query("SELECT * FROM users WHERE email = %s", (email,))

    async def get_user_by_email_and_role(self, email, role):
        res = await self.custom_query("SELECT * FROM users WHERE email = %s", (email,))
        if res:
            try:
                user_data = json.loads(res[0][4])
                if user_data.get("role") == role:
                    return res
            except:
                pass
        return []

    async def update_user(self, user_id, name, email, password, data):
        await self.custom_query(
            "UPDATE users SET username=%s, email=%s, password=%s, data=%s WHERE id=%s",
            (name, email, password, json.dumps(data), user_id)
        )

    async def delete_user(self, user_id):
        await self.custom_query("DELETE FROM users WHERE id=%s", (user_id,))

    # --- Room Methods ---
    # MODIFIED: Added admin_user_id parameter
    async def create_room(self, bed_count, monthly_rent, current_status, thumbnail, admin_user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO rooms (admin_user_id, amenities, residents, bed_count, monthly_rent, current_status, thumbnail) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (admin_user_id, json.dumps([]), json.dumps([]), bed_count, monthly_rent, current_status, thumbnail)
                )

    # MODIFIED: Added admin_user_id filter
    async def get_all_rooms(self, admin_user_id=None):
        if admin_user_id is None:
            # Fallback to global query (should generally be filtered by admin_user_id in practice)
            return await self.custom_query("SELECT * FROM rooms")
        else:
            return await self.custom_query("SELECT * FROM rooms WHERE admin_user_id = %s", (admin_user_id,))

    async def get_room_by_id(self, room_id):
        return await self.custom_query("SELECT * FROM rooms WHERE id = %s", (room_id,))

    # --- Request Methods ---
    async def create_request(self, room_id, title, desc, urgency, user_id):
        async with self.pool.acquire() as conn:
            issue = {"title": title, "desc": desc}
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO requests (room_id, issue, current_status, urgency, user_id, date_created, date_updated) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (room_id, json.dumps(issue), "pending", urgency, user_id, int(datetime.now().timestamp()), int(datetime.now().timestamp()))
                )

    async def update_request_status(self, request_id, status):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE requests SET current_status=%s, date_updated=%s WHERE id=%s",
                    (status, int(datetime.now().timestamp()), request_id)
                )

    async def get_all_requests(self):
        return await self.custom_query("SELECT * FROM requests")

    async def get_request_by_id(self, request_id):
        return await self.custom_query("SELECT * FROM requests WHERE id = %s", (request_id,))

    async def get_request_by_room_id(self, room_id):
        return await self.custom_query("SELECT * FROM requests WHERE room_id = %s", (room_id,))

    # --- Announcement Methods ---
    # MODIFIED: Added admin_user_id parameter
    async def create_announcement(self, title, content, admin_user_id):
        await self.custom_query(
            "INSERT INTO announcements (admin_user_id, title, content, date_created, likes) VALUES (%s, %s, %s, %s, %s)",
            (admin_user_id, title, content, str(int(datetime.now().timestamp())), json.dumps([]))
        )

    # MODIFIED: Added admin_user_id filter
    async def get_announcements(self, admin_user_id=None):
        if admin_user_id is None:
            # Fallback to global query for generic use 
            return await self.custom_query("SELECT * FROM announcements ORDER BY id DESC")
        else:
            # Filter posts to show only those matching the provided admin ID
            return await self.custom_query(
                "SELECT * FROM announcements WHERE admin_user_id = %s ORDER BY id DESC",
                (admin_user_id,)
            )

    async def delete_announcement(self, ann_id):
        await self.custom_query("DELETE FROM announcements WHERE id=%s", (ann_id,))
        await self.custom_query("DELETE FROM comments WHERE announcement_id=%s", (ann_id,))

    async def toggle_like(self, ann_id, user_id):
        res = await self.custom_query("SELECT likes FROM announcements WHERE id=%s", (ann_id,))
        if not res: return
        try: likes = json.loads(res[0][0])
        except: likes = []
        if user_id in likes: likes.remove(user_id)
        else: likes.append(user_id)
        await self.custom_query("UPDATE announcements SET likes=%s WHERE id=%s", (json.dumps(likes), ann_id))

    async def add_comment(self, ann_id, user_id, username, content, parent_id=None):
        await self.custom_query(
            "INSERT INTO comments (announcement_id, user_id, username, content, date_created, parent_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (ann_id, user_id, username, content, str(int(datetime.now().timestamp())), parent_id)
        )

    async def get_comments(self, ann_id):
        return await self.custom_query("SELECT * FROM comments WHERE announcement_id=%s ORDER BY id ASC", (ann_id,))

    async def close(self):
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
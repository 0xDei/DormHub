import flet as ft
import json
from datetime import datetime

from pages.sections.my_room import MyRoom
from pages.sections.payment import Payment
from pages.sections.requests import Requests
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
        self.view = None
        self.data = None
        self.navbar = None

    async def update_data(self):
        """Fetch and update all resident data from database"""
        try:
            print(f"Loading data for user ID: {self.id}")
            
            # Get user basic info
            res = await self.page.data.get_user_by_id(self.id)
            
            if not res or len(res) == 0:
                print(f"Error: No user found with id {self.id}")
                return
            
            self.username = res[0][1]        
            self.email = res[0][2]        
            self.password = res[0][3]
            
            # Parse user data safely
            try:
                self.data = json.loads(res[0][4])
            except:
                print("Failed to parse user data, using defaults")
                self.data = {
                    "room_id": "N/A",
                    "move_in_date": "N/A",
                    "due_date": "N/A",
                    "payment_history": [],
                    "unpaid_dues": [],
                    "phone_number": "N/A"
                }

            print(f"User data loaded: {self.data}")

            # Initialize default values if missing
            if "room_id" not in self.data:
                self.data["room_id"] = "N/A"
            if "move_in_date" not in self.data:
                self.data["move_in_date"] = "N/A"
            if "due_date" not in self.data:
                self.data["due_date"] = "N/A"
            if "payment_history" not in self.data:
                self.data["payment_history"] = []
            if "unpaid_dues" not in self.data:
                self.data["unpaid_dues"] = []
            if "phone_number" not in self.data:
                self.data["phone_number"] = "N/A"

            # If user has a room, fetch room-related data
            if self.data["room_id"] != "N/A":
                print(f"User has room: {self.data['room_id']}")
                
                # Fetch requests for this room and user
                requests_data = []
                try:
                    all_requests = await self.page.data.custom_query(
                        "SELECT * FROM requests WHERE room_id = %s AND user_id = %s", 
                        (self.data["room_id"], self.id)
                    )
                    
                    for request_info in all_requests:
                        requests_data.append({
                            "id": request_info[0],
                            "issue": json.loads(request_info[2]),
                            "status": request_info[3], 
                            "urgency": request_info[4], 
                            "date_created": request_info[6],
                            "date_updated": request_info[7]
                        })
                    print(f"Loaded {len(requests_data)} requests")
                except Exception as e:
                    print(f"Error loading requests: {e}")

                self.data["requests_data"] = requests_data

                # Fetch room details including thumbnail
                try:
                    # Added 'thumbnail' to the query
                    room_res = await self.page.data.custom_query(
                        "SELECT residents, monthly_rent, bed_count, current_status, thumbnail FROM rooms WHERE id = %s", 
                        (self.data["room_id"],)
                    )

                    if room_res and len(room_res) > 0:
                        self.data["monthly_rent"] = room_res[0][1]
                        self.data["bed_count"] = room_res[0][2]
                        self.data["room_status"] = room_res[0][3]
                        self.data["thumbnail"] = room_res[0][4]  # Store thumbnail

                        # DYNAMICALLY FIND ROOMMATES
                        # Instead of using the static list in rooms table, we search all users
                        roommates = []
                        roommate_data = []
                        
                        try:
                            # Get all users to check who is in this room
                            all_users = await self.page.data.get_all_users()
                            
                            for user in all_users:
                                user_id = user[0]
                                if user_id == self.id: continue # Skip self

                                try:
                                    u_data = json.loads(user[4])
                                    # Check if this user is in the same room
                                    if str(u_data.get("room_id")) == str(self.data["room_id"]):
                                        roommates.append(user[1]) # username
                                        roommate_data.append(u_data)
                                except:
                                    continue

                        except Exception as e:
                            print(f"Error loading roommates: {e}")

                        self.data["roommates"] = roommates
                        self.data["roommate_data"] = roommate_data
                        print(f"Loaded {len(roommates)} roommates: {roommates}")
                    else:
                        # Room not found defaults
                        print("Room not found in database")
                        self.data["monthly_rent"] = 0
                        self.data["bed_count"] = 0
                        self.data["roommates"] = []
                        self.data["roommate_data"] = []
                        self.data["room_status"] = "N/A"
                        self.data["thumbnail"] = "placeholder.jpg"
                except Exception as e:
                    print(f"Error loading room data: {e}")
                    self.data["monthly_rent"] = 0
                    self.data["bed_count"] = 0
                    self.data["roommates"] = []
                    self.data["roommate_data"] = []
                    self.data["room_status"] = "N/A"
                    self.data["thumbnail"] = "placeholder.jpg"
            else:
                # No room assigned, set empty data
                print("User has no room assigned")
                self.data["requests_data"] = []
                self.data["monthly_rent"] = 0
                self.data["bed_count"] = 0
                self.data["roommates"] = []
                self.data["roommate_data"] = []
                self.data["room_status"] = "N/A"
                self.data["thumbnail"] = "placeholder.jpg"

            print("Data update complete!")

        except Exception as e:
            print(f"Error updating resident data: {e}")
            import traceback
            traceback.print_exc()


    async def show(self):
        """Create and return the resident page view"""
        print("Creating resident page view...")
        
        self.navbar = NavBar(
            isAdmin=False, 
            current_page=self,
            buttons=[
                NavBarButton(
                    ft.Icons.BED, 
                    "My Room", 
                    lambda e: self.page.run_task(self.show_section, MyRoom(self)), 
                    True
                ),
                NavBarButton(
                    ft.Icons.CREDIT_CARD_ROUNDED, 
                    "Payments", 
                    lambda e: self.page.run_task(self.show_section, Payment(self))
                ),
                NavBarButton(
                    ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, 
                    "Requests", 
                    lambda e: self.page.run_task(self.show_section, Requests(self))
                )
            ]
        )
        
        self.view = ft.View(
            "/active-resident",
            [
                ft.Row(
                    [self.navbar], 
                    spacing=0, 
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH, # Stretch sidebar to bottom
                    expand=True
                )
            ],
            bgcolor="#FFFBEB",
            padding=ft.padding.only(top=-4)
        )

        print("Resident page view created!")
        return self.view

    
    async def show_section(self, section):
        """Switch to a different section in the resident dashboard"""
        try:
            print(f"Showing section: {type(section).__name__}")
            
            # Update the content area with new section
            if len(self.view.controls[0].controls) > 1: 
                self.view.controls[0].controls[1] = section
            else: 
                self.view.controls[0].controls.append(section)
            
            # Refresh data before showing section
            await self.update_data()
            self.view.update()
            print("Section displayed successfully!")
        except Exception as e:
            print(f"Error showing section: {e}")
            import traceback
            traceback.print_exc()


    async def refresh_section(self):
        """Refresh the current section with updated data"""
        try:
            await self.update_data()
            if self.view and len(self.view.controls[0].controls) > 1:
                self.view.controls[0].controls[1].update()
        except Exception as e:
            print(f"Error refreshing section: {e}")


    def get_user_data(self):
        """Get current user data"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "data": self.data
        }


    async def update_user_info(self, new_data):
        """Update user information in database"""
        try:
            await self.page.data.update_user(
                self.id, 
                self.username, 
                self.email, 
                self.password, 
                new_data
            )
            await self.update_data()
            return True
        except Exception as e:
            print(f"Error updating user info: {e}")
            return False
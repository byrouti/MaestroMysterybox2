import json
import os
from typing import Dict, List

class ClickTracker:
    def __init__(self):
        self.db_file = "click_data.json"
        self.max_clicks = 10
        self._load_data()

    def _load_data(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "clicked_users": [],
                    "total_clicks": 0
                }
                self._save_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {
                "clicked_users": [],
                "total_clicks": 0
            }

    def _save_data(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def can_user_click(self, user_id: str) -> bool:
        self._load_data()  # Reload data to ensure we have latest state
        # Check if maximum clicks reached
        if self.data["total_clicks"] >= self.max_clicks:
            return False
        
        # Check if user already clicked
        if user_id in self.data["clicked_users"]:
            return False
        
        return True

    def record_click(self, user_id: str) -> bool:
        self._load_data()  # Reload data to ensure we have latest state
        if not self.can_user_click(user_id):
            return False
        
        self.data["clicked_users"].append(user_id)
        self.data["total_clicks"] += 1
        self._save_data()
        return True

    def get_remaining_clicks(self) -> int:
        self._load_data()  # Reload data to ensure we have latest state
        return self.max_clicks - self.data["total_clicks"]

    def reset_clicks(self):
        self.data = {
            "clicked_users": [],
            "total_clicks": 0
        }
        self._save_data()

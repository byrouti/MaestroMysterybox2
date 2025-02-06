import unittest
from click_tracker import ClickTracker
import os
import json

class TestClickTracker(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_click_data.json"
        self.tracker = ClickTracker()
        self.tracker.db_file = self.test_db  # Use test database file
        
    def tearDown(self):
        # Clean up test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_initial_state(self):
        """Test initial state of click tracker"""
        self.assertEqual(self.tracker.get_remaining_clicks(), 10)
        self.assertTrue(self.tracker.can_user_click("user1"))
    
    def test_single_user_click(self):
        """Test single user clicking"""
        self.assertTrue(self.tracker.record_click("user1"))
        self.assertFalse(self.tracker.can_user_click("user1"))  # Can't click twice
        self.assertEqual(self.tracker.get_remaining_clicks(), 9)
    
    def test_multiple_users(self):
        """Test multiple users clicking"""
        # Record clicks for 9 users
        for i in range(9):
            self.assertTrue(self.tracker.record_click(f"user{i}"))
        
        self.assertEqual(self.tracker.get_remaining_clicks(), 1)
        
        # 10th user should succeed
        self.assertTrue(self.tracker.record_click("user9"))
        
        # 11th user should fail
        self.assertFalse(self.tracker.can_user_click("user10"))
        self.assertEqual(self.tracker.get_remaining_clicks(), 0)
    
    def test_reset_clicks(self):
        """Test resetting clicks"""
        # Record some clicks
        self.tracker.record_click("user1")
        self.tracker.record_click("user2")
        
        # Reset
        self.tracker.reset_clicks()
        
        # Check if reset worked
        self.assertEqual(self.tracker.get_remaining_clicks(), 10)
        self.assertTrue(self.tracker.can_user_click("user1"))
        self.assertTrue(self.tracker.can_user_click("user2"))
    
    def test_persistence(self):
        """Test if data persists between tracker instances"""
        # Record a click
        self.tracker.record_click("user1")
        
        # Create new tracker instance
        new_tracker = ClickTracker()
        new_tracker.db_file = self.test_db
        
        # Check if click data persisted
        self.assertFalse(new_tracker.can_user_click("user1"))
        self.assertEqual(new_tracker.get_remaining_clicks(), 9)

if __name__ == '__main__':
    unittest.main()

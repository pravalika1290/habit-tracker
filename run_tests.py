import os
import unittest
import datetime
from db import get_db_connection, create_tables
from models import Habit
from analytics import calculate_streak, get_longest_streak_for_habit

TEST_DB = "test_habits.db"

class TestHabitTracker(unittest.TestCase):

    def setUp(self):
        """Runs before EVERY single test to set up a clean database."""
        conn = get_db_connection(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS completions")
        cursor.execute("DROP TABLE IF EXISTS habits")
        conn.commit()
        conn.close()
        
        # Create fresh tables for testing
        create_tables_for_test()

    def tearDown(self):
        """Runs after EVERY test to clean up the test database file."""
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                pass

    def test_habit_creation(self):
        conn = get_db_connection(TEST_DB)
        habit = Habit(name="Test Habit", periodicity="daily")
        habit.save(conn)
        
        self.assertIsNotNone(habit.id)
        self.assertEqual(habit.name, "Test Habit")
        self.assertEqual(habit.periodicity, "daily")
        conn.close()

    def test_single_check_off(self):
        conn = get_db_connection(TEST_DB)
        habit = Habit(name="Test Habit", periodicity="daily")
        habit.save(conn)
        
        success = habit.check_off(conn)
        self.assertTrue(success)
        self.assertEqual(len(habit.get_completions(conn)), 1)
        conn.close()

    def test_double_check_off_prevention(self):
        conn = get_db_connection(TEST_DB)
        habit = Habit(name="Test Habit", periodicity="daily")
        habit.save(conn)
        
        # First check-off should succeed
        self.assertTrue(habit.check_off(conn))
        # Second check-off on the same day should fail
        self.assertFalse(habit.check_off(conn))
        self.assertEqual(len(habit.get_completions(conn)), 1)
        conn.close()

    def test_streak_calculation(self):
        # Test our math logic directly using mock dates
        dates = [
            "2026-10-01T12:00:00",
            "2026-10-02T12:00:00",
            "2026-10-03T12:00:00",
            "2026-10-05T12:00:00", # Gap of 2 days (broken streak)
            "2026-10-06T12:00:00"
        ]
        
        # The longest consecutive streak is 3 days (Oct 1 to Oct 3)
        streak = calculate_streak(dates, "daily")
        self.assertEqual(streak, 3)

def create_tables_for_test():
    """Helper function to create tables specifically inside the test DB."""
    conn = get_db_connection(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        periodicity TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    unittest.main()

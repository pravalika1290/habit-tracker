import datetime

class Habit:
    def __init__(self, name: str, periodicity: str, created_at: str = None, id: int = None):
        """
        Initializes a Habit object.
        :param name: The name of the habit (e.g., "Drink Water")
        :param periodicity: "daily" or "weekly"
        :param created_at: ISO timestamp of creation (defaults to current time)
        :param id: Database ID (automatically assigned when fetched from DB)
        """
        self.id = id
        self.name = name
        self.periodicity = periodicity  # Must be "daily" or "weekly"
        self.created_at = created_at or datetime.datetime.now().isoformat()

    def save(self, db_conn):
        """Saves a new habit definition into the database."""
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO habits (name, periodicity, created_at) VALUES (?, ?, ?)",
            (self.name, self.periodicity, self.created_at)
        )
        db_conn.commit()
        # Retrieve the auto-incremented ID assigned by SQLite
        self.id = cursor.lastrowid
        print(f"Habit '{self.name}' saved to database with ID: {self.id}")

    def check_off(self, db_conn, check_in_date: str = None):
        """
        Records a completion timestamp for this habit.
        Prevents duplicate check-offs on the same calendar day for daily habits.
        """
        if self.id is None:
            raise ValueError("This habit must be saved to the database first!")

        date_to_record = check_in_date or datetime.datetime.now().isoformat()
        
        # Keep dates clean for comparison (extract just the YYYY-MM-DD part)
        check_date_only = date_to_record[:10]

        cursor = db_conn.cursor()
        
        # For daily habits, check if we already checked off today
        if self.periodicity == "daily":
            cursor.execute(
                "SELECT check_in_date FROM completions WHERE habit_id = ?",
                (self.id,)
            )
            completions = cursor.fetchall()
            # If any previous completion matches the same YYYY-MM-DD, prevent a double check-off
            for comp in completions:
                if comp['check_in_date'][:10] == check_date_only:
                    print(f"⚠️ Habit '{self.name}' was already checked off today!")
                    return False

        # If clean, insert the completion
        cursor.execute(
            "INSERT INTO completions (habit_id, check_in_date) VALUES (?, ?)",
            (self.id, date_to_record)
        )
        db_conn.commit()
        print(f"✅ Habit '{self.name}' successfully checked off at {date_to_record}!")
        return True

    def get_completions(self, db_conn) -> list:
        """Retrieves all check-off timestamps for this habit from the database."""
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT check_in_date FROM completions WHERE habit_id = ? ORDER BY check_in_date ASC",
            (self.id,)
        )
        rows = cursor.fetchall()
        return [row['check_in_date'] for row in rows]

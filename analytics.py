import datetime

# Helper function to convert ISO string to date object
def to_date(date_str: str) -> datetime.date:
    return datetime.datetime.fromisoformat(date_str).date()

# --- Core Analytics Functions ---

def get_all_habits(db_conn) -> list:
    """Returns a raw list of all tracked habit records in the database."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM habits")
    return cursor.fetchall()


def filter_by_periodicity(db_conn, periodicity: str) -> list:
    """Functional filtering: Returns only habits matching the specified periodicity."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE periodicity = ?", (periodicity,))
    return cursor.fetchall()


def calculate_streak(completion_dates: list, periodicity: str) -> int:
    """
    Core functional streak calculator.
    Takes a raw list of completion date strings, sorts them, cleans duplicates,
    and calculates the longest consecutive streak of completions.
    """
    if not completion_dates:
        return 0

    # 1. Map to unique sorted date objects (Pure functional transformation)
    dates = sorted(list(set(map(to_date, completion_dates))))
    
    longest_streak = 0
    current_streak = 1
    
    # Allowed gap threshold depending on habit frequency
    max_allowed_gap = 1 if periodicity == "daily" else 7

    for i in range(len(dates) - 1):
        gap = (dates[i + 1] - dates[i]).days
        
        if gap <= max_allowed_gap:
            current_streak += 1
        else:
            # Streak broken, save the maximum reached and reset
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1
            
    return max(longest_streak, current_streak)


def get_longest_streak_for_habit(db_conn, habit_id: int, periodicity: str) -> int:
    """Calculates the longest streak achieved for a specific habit ID."""
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT check_in_date FROM completions WHERE habit_id = ? ORDER BY check_in_date ASC",
        (habit_id,)
    )
    rows = cursor.fetchall()
    completions = [row['check_in_date'] for row in rows]
    return calculate_streak(completions, periodicity)


def get_longest_streak_overall(db_conn) -> dict:
    """
    Finds the single habit with the longest streak across the entire database.
    Returns a dictionary with details or None if no habits exist.
    """
    habits = get_all_habits(db_conn)
    if not habits:
        return None

    longest_streak = 0
    best_habit = None

    for h in habits:
        streak = get_longest_streak_for_habit(db_conn, h['id'], h['periodicity'])
        if streak > longest_streak:
            longest_streak = streak
            best_habit = h['name']

    return {"habit": best_habit, "streak": longest_streak}

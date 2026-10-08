import datetime
from db import get_db_connection, create_tables
from models import Habit
from analytics import calculate_streak, get_longest_streak_for_habit

# 1. Set up clean database tables
create_tables()
conn = get_db_connection()

# 2. Create a daily habit "Read Book"
habit = Habit(name="Read Book", periodicity="daily")
habit.save(conn)

# 3. Simulate a 5-day streak of check-offs by creating past dates
today = datetime.datetime.now()
past_dates = [
    (today - datetime.timedelta(days=i)).isoformat()
    for i in range(5)
]

# Save completions in the database
cursor = conn.cursor()
for date_str in past_dates:
    cursor.execute(
        "INSERT INTO completions (habit_id, check_in_date) VALUES (?, ?)",
        (habit.id, date_str)
    )
conn.commit()

# 4. Use the functional analytics module to calculate the streak
streak = get_longest_streak_for_habit(conn, habit.id, habit.periodicity)

print("\n--- Analytics Test ---")
print(f"Recorded completion dates: {[d[:10] for d in past_dates]}")
print(f"Calculated consecutive streak: {streak} days!")

conn.close()

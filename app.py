import sys
from db import get_db_connection, create_tables
from models import Habit
from analytics import (
    get_all_habits,
    filter_by_periodicity,
    get_longest_streak_for_habit,
    get_longest_streak_overall
)

def show_menu():
    print("\n==============================")
    print("      HABIT TRACKER MENU      ")
    print("==============================")
    print("[1] Create a New Habit")
    print("[2] Check-off a Habit")
    print("[3] View All Tracked Habits")
    print("[4] View Habits by Frequency (Daily/Weekly)")
    print("[5] View Longest Streak for a Habit")
    print("[6] View Longest Streak Overall")
    print("[7] Exit App")
    print("==============================")

def run_app():
    # Make sure database tables are set up
    create_tables()
    conn = get_db_connection()

    while True:
        show_menu()
        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            name = input("Enter habit name (e.g., 'Drink Water'): ").strip()
            if not name:
                print("❌ Habit name cannot be empty.")
                continue
            
            periodicity = input("Enter frequency ('daily' or 'weekly'): ").strip().lower()
            if periodicity not in ["daily", "weekly"]:
                print("❌ Invalid frequency. Please type 'daily' or 'weekly'.")
                continue

            # Create and save the new habit
            habit = Habit(name=name, periodicity=periodicity)
            habit.save(conn)
            print(f"🎉 Habit '{name}' created successfully!")

        elif choice == "2":
            habits = get_all_habits(conn)
            if not habits:
                print("ℹ️ No habits tracked yet. Create one first!")
                continue

            print("\nSelect a habit to check off:")
            for h in habits:
                print(f"[{h['id']}] {h['name']} ({h['periodicity']})")

            try:
                habit_id = int(input("Enter habit ID: "))
                selected = next((h for h in habits if h['id'] == habit_id), None)
                
                if selected:
                    # Instantiate standard Habit object to call object methods
                    habit_obj = Habit(
                        id=selected['id'],
                        name=selected['name'],
                        periodicity=selected['periodicity'],
                        created_at=selected['created_at']
                    )
                    habit_obj.check_off(conn)
                else:
                    print("❌ Invalid habit ID.")
            except ValueError:
                print("❌ Please enter a valid numerical ID.")

        elif choice == "3":
            habits = get_all_habits(conn)
            if not habits:
                print("ℹ️ No habits tracked yet.")
            else:
                print("\n--- Tracked Habits ---")
                for h in habits:
                    print(f"• ID {h['id']}: {h['name']} [{h['periodicity']}] (Created: {h['created_at'][:10]})")

        elif choice == "4":
            freq = input("Enter frequency to filter by ('daily' or 'weekly'): ").strip().lower()
            if freq not in ["daily", "weekly"]:
                print("❌ Invalid frequency. Use 'daily' or 'weekly'.")
                continue
            
            habits = filter_by_periodicity(conn, freq)
            if not habits:
                print(f"ℹ️ No {freq} habits found.")
            else:
                print(f"\n--- {freq.capitalize()} Habits ---")
                for h in habits:
                    print(f"• {h['name']}")

        elif choice == "5":
            habits = get_all_habits(conn)
            if not habits:
                print("ℹ️ No habits tracked yet.")
                continue

            print("\nSelect a habit to view streak statistics:")
            for h in habits:
                print(f"[{h['id']}] {h['name']}")

            try:
                habit_id = int(input("Enter habit ID: "))
                selected = next((h for h in habits if h['id'] == habit_id), None)
                if selected:
                    streak = get_longest_streak_for_habit(conn, selected['id'], selected['periodicity'])
                    print(f"\n🔥 Longest streak for '{selected['name']}': {streak} periods!")
                else:
                    print("❌ Invalid habit ID.")
            except ValueError:
                print("❌ Please enter a valid numerical ID.")

        elif choice == "6":
            result = get_longest_streak_overall(conn)
            if not result or not result["habit"]:
                print("ℹ️ No active streaks found.")
            else:
                print(f"\n🏆 Champion Streak overall: '{result['habit']}' with a streak of {result['streak']} periods!")

        elif choice == "7":
            print("\nThank you for using BSH Habit Tracker! Goodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 7.")

    conn.close()

if __name__ == "__main__":
    run_app()

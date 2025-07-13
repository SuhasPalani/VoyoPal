from datetime import datetime, time, timedelta

# General utility functions can go here
def format_currency(amount: float) -> str:
    """Formats a float as a currency string."""
    return f"${amount:,.2f}"

def calculate_duration_minutes(start_time_str: str, end_time_str: str) -> int:
    """
    Calculates duration in minutes between two time strings (e.g., "10:30 AM", "2:00 PM").
    Assumes times are on the same day.
    """
    try:
        # Parse times. Assume arbitrary date for timedelta calculation
        start_time_obj = datetime.strptime(start_time_str, "%I:%M %p").time()
        end_time_obj = datetime.strptime(end_time_str, "%I:%M %p").time()

        dummy_date = datetime(2000, 1, 1).date()
        start_dt = datetime.combine(dummy_date, start_time_obj)
        end_dt = datetime.combine(dummy_date, end_time_obj)

        if end_dt < start_dt:
            # Handle cases where end time is on the next day (e.g., 10 PM to 2 AM)
            end_dt += timedelta(days=1)
        
        duration = end_dt - start_dt
        return int(duration.total_seconds() / 60)
    except ValueError as e:
        print(f"Error parsing time strings: {e}. Start: '{start_time_str}', End: '{end_time_str}'")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred in calculate_duration_minutes: {e}")
        return 0
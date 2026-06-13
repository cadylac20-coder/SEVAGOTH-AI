"""
SEVAGOTH Reminders Module
Handles reminder creation, management, and task scheduling
"""

import re
import datetime
from threading import Lock
from config import REMINDER_TIME_FORMAT, REMINDER_TIMESTAMP_FORMAT

# Global reminders list and lock for thread safety
reminders = []
reminder_lock = Lock()


def set_reminder(query: str, sevagoth_speak_func):
    """
    Set a reminder based on voice command
    Supports both relative (in X minutes) and absolute (at X PM) times
    
    Args:
        query: Voice command string
        sevagoth_speak_func: Function to call for voice feedback
    """
    query = query.lower().replace(".", "")
    
    # Try to match relative time pattern (in X minutes/hours)
    relative_time = re.search(r'(in|after) (\d+)\s?(minute|minutes|hour|hours)', query)
    
    # Try to match absolute time pattern (at X AM/PM)
    absolute_time = re.search(r'at (\d{1,2}(:\d{2})?\s?(am|pm))', query)
    
    # Extract the task description
    task_pattern = re.search(r'remind me to (.+?) (?:at|in|after)', query)
    
    if relative_time and task_pattern:
        # Handle relative time reminder
        amount = int(relative_time.group(2))
        unit = relative_time.group(3)
        task = task_pattern.group(1).strip()
        
        now = datetime.datetime.now()
        delta = datetime.timedelta(hours=amount) if 'hour' in unit else datetime.timedelta(minutes=amount)
        reminder_time = (now + delta).strftime(REMINDER_TIME_FORMAT)
        
        with reminder_lock:
            reminders.append({"time": reminder_time, "task": task})
        
        sevagoth_speak_func(f"Reminder set for {task} in {amount} {unit}")
        print(f"Reminder set: {task} at {reminder_time}")
    
    elif absolute_time and task_pattern:
        # Handle absolute time reminder
        raw_time = absolute_time.group(1).strip()
        task = task_pattern.group(1).strip()
        
        try:
            # Add :00 if no minutes specified
            if ':' not in raw_time:
                raw_time = raw_time.replace('am', ':00 am').replace('pm', ':00 pm')
            
            reminder_time = datetime.datetime.strptime(raw_time, "%I:%M %p").strftime(REMINDER_TIME_FORMAT)
        except ValueError as e:
            sevagoth_speak_func("Sorry, I couldn't understand the time format.")
            print(f"Parsing error: {e}")
            return
        
        with reminder_lock:
            reminders.append({"time": reminder_time, "task": task})
        
        sevagoth_speak_func(f"Reminder set for {task} at {reminder_time}")
        print(f"Reminder set: {task} at {reminder_time}")
    
    else:
        sevagoth_speak_func("Please say something like 'Remind me to feed the dog at 6 PM'.")


def list_reminders(sevagoth_speak_func):
    """
    Display all set reminders
    
    Args:
        sevagoth_speak_func: Function to call for voice feedback
    """
    with reminder_lock:
        if not reminders:
            sevagoth_speak_func("You have no reminders set, sir.")
            print("No reminders set.")
        else:
            sevagoth_speak_func(f"You have {len(reminders)} reminders:")
            for reminder in reminders:
                sevagoth_speak_func(f"{reminder['task']} at {reminder['time']}")
                print(f"{reminder['task']} at {reminder['time']}")


def get_all_reminders() -> list:
    """
    Get all reminders as a list
    
    Returns:
        List of reminder dictionaries
    """
    with reminder_lock:
        return reminders.copy()


def clear_reminders():
    """Clear all reminders"""
    global reminders
    with reminder_lock:
        reminders = []
    print("[REMINDERS] All reminders cleared.")


def add_reminder(task: str, time_str: str):
    """
    Add a reminder programmatically
    
    Args:
        task: Task description
        time_str: Time in HH:MM format
    """
    with reminder_lock:
        reminders.append({"time": time_str, "task": task})
    print(f"Reminder added: {task} at {time_str}")
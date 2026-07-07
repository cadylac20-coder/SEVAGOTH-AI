"""
SEVAGOTH Admin Module
Handles admin-specific commands and user management
"""

import re
from modules.auth import Admin


def handle_admin_commands(query: str, user_obj, current_username: str, sevagoth_speak_func) -> bool:
    """
    Handle admin-specific voice commands
    
    Args:
        query: Voice command string
        user_obj: Current user object (Employee or Admin)
        current_username: Username of current user
        sevagoth_speak_func: Function to call for voice feedback
        
    Returns:
        True if command was handled, False otherwise
    """
    
    # Check if user has admin privileges
    if not isinstance(user_obj, Admin):
        # Block non-admin users from running admin commands
        if any(k in query for k in ["show all users", "show history of", "add user", "delete user", "all histories"]):
            sevagoth_speak_func("Access denied. You do not have admin privileges.")
            return True
        return False

    # ── ADMIN COMMANDS ────────────────────────────────────────────────────────────

    if "show all users" in query:
        users = user_obj.list_all_users()
        sevagoth_speak_func(f"Registered users: {', '.join(users)}")
        return True

    if "show history of" in query:
        match = re.search(r'show history of (.+)', query)
        if match:
            target = match.group(1).strip()
            history = user_obj.get_user_history(target)
            if not history:
                sevagoth_speak_func(f"{target} has no history.")
            else:
                sevagoth_speak_func(f"{target} has {len(history)} logged commands.")
                for entry in history:
                    if isinstance(entry, dict):
                        print(f"  [{entry['timestamp']}] {entry['command']}")
                    else:
                        print(f"  {entry}")
        return True

    if "show all histories" in query:
        user_obj.print_all_histories()
        sevagoth_speak_func("All user histories printed to console.")
        return True

    if "add user" in query:
        sevagoth_speak_func("Enter new username:")
        new_user = input("New username: ").strip()
        
        import getpass
        new_pass = getpass.getpass("New password: ").strip()
        
        role_input = input("Role (employee/admin): ").strip().lower()
        role = role_input if role_input in ("employee", "admin") else "employee"
        
        user_obj.add_user(new_user, new_pass, role)
        sevagoth_speak_func(f"User {new_user} has been added.")
        return True

    if "delete user" in query:
        match = re.search(r'delete user (.+)', query)
        if match:
            target_user = match.group(1).strip()
            user_obj.delete_user(target_user)
            sevagoth_speak_func(f"User {target_user} deleted.")
        return True

    if "clear history of" in query:
        match = re.search(r'clear history of (.+)', query)
        if match:
            target_user = match.group(1).strip()
            user_obj.clear_user_history(target_user)
            sevagoth_speak_func(f"History cleared for {target_user}.")
        return True

    return False
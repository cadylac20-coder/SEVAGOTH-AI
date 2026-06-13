"""
SEVAGOTH Authentication Module
Handles user login, registration, and role management
"""

import hashlib
import json
import os
import sys
import getpass
import datetime
from config import USER_DB_FILE, MAX_LOGIN_ATTEMPTS, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, REMINDER_TIMESTAMP_FORMAT


def _hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_user_db() -> dict:
    """Load user database from JSON file"""
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    
    # Create default admin account
    default = {
        DEFAULT_ADMIN_USERNAME: {
            "password": _hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": "admin",
            "command_history": []
        }
    }
    _save_user_db(default)
    return default


def _save_user_db(db: dict):
    """Save user database to JSON file"""
    with open(USER_DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


class Employee:
    """Regular employee user class"""
    def __init__(self, username: str):
        self.username = username

    def log_command(self, command: str):
        """Log a command executed by this user"""
        db = _load_user_db()
        entry = {
            "command": command,
            "timestamp": datetime.datetime.now().strftime(REMINDER_TIMESTAMP_FORMAT)
        }
        db[self.username]["command_history"].append(entry)
        _save_user_db(db)

    def get_history(self) -> list:
        """Get command history for this user"""
        return _load_user_db()[self.username].get("command_history", [])

    def clear_history(self):
        """Clear command history for this user"""
        db = _load_user_db()
        db[self.username]["command_history"] = []
        _save_user_db(db)


class Admin(Employee):
    """Admin user class with elevated privileges"""
    
    def list_all_users(self) -> list:
        """List all registered users"""
        return list(_load_user_db().keys())

    def get_user_history(self, username: str) -> list:
        """Get command history for a specific user"""
        db = _load_user_db()
        if username not in db:
            return [f"User '{username}' does not exist."]
        return db[username].get("command_history", [])

    def add_user(self, username: str, password: str, role: str = "employee"):
        """Add a new user to the system"""
        db = _load_user_db()
        if username in db:
            print(f"[ADMIN] User '{username}' already exists.")
            return
        db[username] = {
            "password": _hash_password(password),
            "role": role,
            "command_history": []
        }
        _save_user_db(db)
        print(f"[ADMIN] User '{username}' added with role '{role}'.")

    def delete_user(self, username: str):
        """Delete a user from the system"""
        db = _load_user_db()
        if username == DEFAULT_ADMIN_USERNAME:
            print("[ADMIN] Cannot delete the root admin account.")
            return
        if username not in db:
            print(f"[ADMIN] User '{username}' not found.")
            return
        del db[username]
        _save_user_db(db)
        print(f"[ADMIN] User '{username}' deleted.")

    def clear_user_history(self, username: str):
        """Clear command history for a specific user"""
        db = _load_user_db()
        if username not in db:
            print(f"[ADMIN] User '{username}' not found.")
            return
        db[username]["command_history"] = []
        _save_user_db(db)
        print(f"[ADMIN] History cleared for '{username}'.")

    def print_all_histories(self):
        """Print command histories for all users"""
        for uname, udata in _load_user_db().items():
            print(f"\n── {uname} ({udata['role']}) ──")
            history = udata.get("command_history", [])
            if not history:
                print("  No commands logged.")
            for entry in history:
                if isinstance(entry, dict):
                    print(f"  [{entry['timestamp']}] {entry['command']}")
                else:
                    print(f"  {entry}")


def login() -> tuple:
    """
    Login function - handles user authentication
    Returns: (username, user_object) where user_object is Admin or Employee instance
    """
    db = _load_user_db()
    print("\n" + "=" * 50)
    print("       SEVAGOTH — SECURE LOGIN")
    print("=" * 50)
    
    attempts = 0
    while attempts < MAX_LOGIN_ATTEMPTS:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        # Check credentials
        if username in db and db[username]["password"] == _hash_password(password):
            role = db[username]["role"]
            print(f"\n[SEVAGOTH] Access granted. Welcome, {username}.")
            
            # Return appropriate user object based on role
            return (username, Admin(username)) if role == "admin" else (username, Employee(username))
        
        attempts += 1
        remaining = MAX_LOGIN_ATTEMPTS - attempts
        print(f"[SEVAGOTH] Invalid credentials. {remaining} attempt(s) remaining.")
    
    print("[SEVAGOTH] Access denied. Shutting down.")
    sys.exit(1)
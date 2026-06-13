import os
import getpass
from datetime import datetime

DIARY_FILE = "diary.txt"
PASSWORD = "Oswaal Dilution Law And Henry's Constant"  # Replace with your own secure password

def write_entry():
    print("Enter your diary entry (type 'exit' to finish):")
    lines = []
    while True:
        line = input()
        if line.lower() == "exit":
            break
        lines.append(line)
    
    if lines:
        with open(DIARY_FILE, "a", encoding="utf-8") as file:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            file.write(f"\n{timestamp}\n" + "\n".join(lines) + "\n")
        print("Entry saved.")

def view_entries():
    entered = getpass.getpass("Enter diary password: ")
    if entered != PASSWORD:
        print("Incorrect password. Access denied.")
        return

    if not os.path.exists(DIARY_FILE):
        print("No diary entries found.")
        return

    with open(DIARY_FILE, "r", encoding="utf-8") as file:
        print("\n==== Your Diary ====\n")
        print(file.read())
        print("====================\n")

def open_diary():
    print("1. View Diary\n2. Write in Diary\n3. Cancel")
    choice = input("Select option: ")

    if choice == "1":
        view_entries()
    elif choice == "2":
        entered = getpass.getpass("Enter diary password to write: ")
        if entered != PASSWORD:
            print("Incorrect password.")
            return
        write_entry()
    elif choice == "3":
        print("Diary closed.")
    else:
        print("Invalid option.")

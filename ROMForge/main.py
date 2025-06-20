import os
import sys
from pathlib import Path

# --- ROMForge Main Application ---

# Define all required folders
FOLDERS = [
    'Consoles',
    'Covers',
    'Reports',
    'Backups'
]

PROJECT_ROOT = Path(__file__).parent.resolve()

# Welcome message
print("""
====================================
 Welcome to ROMForge - ROM Manager!
====================================
""")

# Check if all folders exist
for folder in FOLDERS:
    folder_path = PROJECT_ROOT / folder
    if not folder_path.exists():
        print(f"Missing folder: {folder_path}. Please run setup.py first.")
        sys.exit(1)

# Error log path
ERROR_LOG = PROJECT_ROOT / 'Reports' / 'errors.txt'

def log_error(msg):
    with open(ERROR_LOG, 'a') as f:
        f.write(msg + '\n')

# Main menu
while True:
    print("\nMain Menu:")
    print("1. Validate Games")
    print("2. Organize Collection")
    print("3. Download Artwork")
    print("4. Generate Reports")
    print("0. Exit")
    choice = input("Select an option: ").strip()
    if choice == '1':
        print("[Placeholder] Validate Games - This feature will check your ROM files.")
    elif choice == '2':
        print("[Placeholder] Organize Collection - This feature will sort and backup your ROMs.")
    elif choice == '3':
        print("[Placeholder] Download Artwork - This feature will fetch game covers.")
    elif choice == '4':
        print("[Placeholder] Generate Reports - This feature will create collection and missing game reports.")
    elif choice == '0':
        print("Goodbye!")
        break
    else:
        print("Invalid option. Please enter a number from 0 to 4.")

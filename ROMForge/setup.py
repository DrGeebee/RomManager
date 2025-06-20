import os
import sys
import subprocess
from pathlib import Path

# --- Setup script for ROMForge ---

# Define all required folders
FOLDERS = [
    'Consoles',
    'Covers',
    'Reports',
    'Backups'
]

# Define requirements
REQUIREMENTS = [
    'requests',
    'pandas',
    'python-dateutil'
]

# Get project root
PROJECT_ROOT = Path(__file__).parent.resolve()

# 1. Create folders if they don't exist
for folder in FOLDERS:
    folder_path = PROJECT_ROOT / folder
    if not folder_path.exists():
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Created folder: {folder_path}")
        except Exception as e:
            print(f"Error creating folder {folder_path}: {e}")

# 2. Install required packages
print("\nChecking and installing required Python packages...")
try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(PROJECT_ROOT / 'requirements.txt')])
except Exception as e:
    print(f"Error installing packages: {e}")
    sys.exit(1)

# 3. Check for permissions (write access to all folders)
print("\nChecking folder permissions...")
for folder in FOLDERS:
    folder_path = PROJECT_ROOT / folder
    try:
        test_file = folder_path / 'test_perm.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        print(f"No write permission in {folder_path}: {e}")
        sys.exit(1)

# 4. Create a desktop shortcut (Windows only)
if os.name == 'nt':
    try:
        import winshell
        from win32com.client import Dispatch
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut = os.path.join(desktop, 'ROMForge.lnk')
        target = str(PROJECT_ROOT / 'main.py')
        wDir = str(PROJECT_ROOT)
        icon = target
        shell = Dispatch('WScript.Shell')
        shortcut_obj = shell.CreateShortCut(shortcut)
        shortcut_obj.Targetpath = sys.executable
        shortcut_obj.Arguments = f'"{target}"'
        shortcut_obj.WorkingDirectory = wDir
        shortcut_obj.IconLocation = icon
        shortcut_obj.save()
        print(f"Desktop shortcut created: {shortcut}")
    except Exception as e:
        print(f"Could not create desktop shortcut: {e}\nYou may need to install 'pywin32' and 'winshell' packages.")

print("\nSetup complete! Your ROM Manager is ready. Type: python main.py to start.")

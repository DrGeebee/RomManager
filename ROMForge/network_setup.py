import os
import json
import shutil
from pathlib import Path

def validate_json(data):
    try:
        json.dumps(data)
        return True
    except Exception as e:
        print(f"JSON validation error: {e}")
        return False

def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = str(file_path) + ".bak"
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")

def write_json(file_path, data):
    backup_file(file_path)
    if validate_json(data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Wrote: {file_path}")
    else:
        print(f"Invalid JSON, not writing: {file_path}")

# 1. Store network ROM path in config.json
config_path = Path('ROMForge/config.json')
config = {
    "master_rom_path": "//UNRAID/Games/ROMs/",
    "tags_version": "1.0"
}
write_json(config_path, config)

# 2. Example console metadata (SNES)
example_metadata = {
    "type": "console",
    "manufacturer": "Nintendo",
    "generation": 4,
    "years": "1990-2003",
    "media_type": "cartridge",
    "architecture": "16-bit",
    "popularity": "high",
    "online_support": False,
    "multiplayer": "local",
    "region_encoding": True,
    "special_tags": ["rumble_pak", "super_fx"],
    # Universal tags
    "AV_outputs": ["composite", "HDMI"],
    "multiplayer_type": "local"
}

# 3. For each console folder, create console_metadata.json
consoles_root = Path('ROMForge/Consoles/Home Consoles/Nintendo/SNES')
os.makedirs(consoles_root, exist_ok=True)
console_metadata_path = consoles_root / 'console_metadata.json'
write_json(console_metadata_path, example_metadata)

# 4. Create rom_locations.json with network paths only
rom_locations = {
    "roms": [
        "//UNRAID/Games/ROMs/SNES/Super Mario World.sfc",
        "//UNRAID/Games/ROMs/SNES/The Legend of Zelda.sfc"
    ]
}
write_json(consoles_root / 'rom_locations.json', rom_locations)

# 5. Create tag_database.json in root
all_tags = [
    "16-bit", "cartridge", "nintendo", "console", "high", "local", "composite", "HDMI", "rumble_pak", "super_fx"
]
tag_database = {
    "all_tags": all_tags,
    "tag_categories": {
        "generation": [1,2,3,4,5,6,7,8,9],
        "media_type": ["cartridge", "cd", "disk", "card", "digital"],
        "region": ["NTSC-U", "PAL", "NTSC-J", "Region-free"]
    }
}
write_json('ROMForge/tag_database.json', tag_database)

print("network_setup.py complete. All metadata and config files created and validated.")

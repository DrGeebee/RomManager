import json
from pathlib import Path
import re

def sanitize(name):
    # Remove special characters for cross-platform compatibility
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

# Hardcoded console data (expand as needed)
CONSOLES = [
    # Sega Home Consoles
    {"manufacturer": "Sega", "type": "Home Console", "name": "SG-1000", "generation": 3, "release_year": "1983", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "Master System", "generation": 3, "release_year": "1985", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "Genesis", "generation": 4, "release_year": "1988", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "Sega CD", "generation": 4, "release_year": "1991", "media_type": "cd", "architecture": "16-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "32X", "generation": 4, "release_year": "1994", "media_type": "cartridge", "architecture": "32-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "Saturn", "generation": 5, "release_year": "1994", "media_type": "cd", "architecture": "32-bit"},
    {"manufacturer": "Sega", "type": "Home Console", "name": "Dreamcast", "generation": 6, "release_year": "1998", "media_type": "gd-rom", "architecture": "128-bit"},
    # Sega Handhelds
    {"manufacturer": "Sega", "type": "Handheld", "name": "Game Gear", "generation": 4, "release_year": "1990", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Sega", "type": "Handheld", "name": "Nomad", "generation": 4, "release_year": "1995", "media_type": "cartridge", "architecture": "16-bit"},
    # NEC Home Consoles
    {"manufacturer": "NEC", "type": "Home Console", "name": "PC Engine (TurboGrafx-16)", "generation": 4, "release_year": "1987", "media_type": "huCard", "architecture": "8-bit"},
    {"manufacturer": "NEC", "type": "Home Console", "name": "SuperGrafx", "generation": 4, "release_year": "1989", "media_type": "huCard", "architecture": "8-bit"},
    {"manufacturer": "NEC", "type": "Home Console", "name": "PC-FX", "generation": 5, "release_year": "1994", "media_type": "cd", "architecture": "32-bit"},
    # NEC Handhelds
    {"manufacturer": "NEC", "type": "Handheld", "name": "TurboExpress", "generation": 4, "release_year": "1990", "media_type": "huCard", "architecture": "8-bit"},
    # Nintendo Home Consoles
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "NES", "generation": 3, "release_year": "1983", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "Super Nintendo Entertainment System (SNES)", "generation": 4, "release_year": "1990", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "Nintendo 64", "generation": 5, "release_year": "1996", "media_type": "cartridge", "architecture": "64-bit"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "GameCube", "generation": 6, "release_year": "2001", "media_type": "miniDVD", "architecture": "128-bit"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "Wii", "generation": 7, "release_year": "2006", "media_type": "dvd", "architecture": "PowerPC"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "Wii U", "generation": 8, "release_year": "2012", "media_type": "wii u optical disc", "architecture": "PowerPC"},
    {"manufacturer": "Nintendo", "type": "Home Console", "name": "Switch", "generation": 9, "release_year": "2017", "media_type": "game card", "architecture": "ARM"},
    # Nintendo Handhelds
    {"manufacturer": "Nintendo", "type": "Handheld", "name": "Game Boy", "generation": 4, "release_year": "1989", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Nintendo", "type": "Handheld", "name": "Game Boy Color", "generation": 5, "release_year": "1998", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Nintendo", "type": "Handheld", "name": "Game Boy Advance", "generation": 6, "release_year": "2001", "media_type": "cartridge", "architecture": "32-bit"},
    {"manufacturer": "Nintendo", "type": "Handheld", "name": "Nintendo DS", "generation": 7, "release_year": "2004", "media_type": "game card", "architecture": "ARM"},
    {"manufacturer": "Nintendo", "type": "Handheld", "name": "Nintendo 3DS", "generation": 8, "release_year": "2011", "media_type": "game card", "architecture": "ARM"},
    # Sony Home Consoles
    {"manufacturer": "Sony", "type": "Home Console", "name": "PlayStation", "generation": 5, "release_year": "1994", "media_type": "cd", "architecture": "32-bit"},
    {"manufacturer": "Sony", "type": "Home Console", "name": "PlayStation 2", "generation": 6, "release_year": "2000", "media_type": "dvd", "architecture": "128-bit"},
    {"manufacturer": "Sony", "type": "Home Console", "name": "PlayStation 3", "generation": 7, "release_year": "2006", "media_type": "blu-ray", "architecture": "Cell"},
    {"manufacturer": "Sony", "type": "Home Console", "name": "PlayStation 4", "generation": 8, "release_year": "2013", "media_type": "blu-ray", "architecture": "x86-64"},
    {"manufacturer": "Sony", "type": "Home Console", "name": "PlayStation 5", "generation": 9, "release_year": "2020", "media_type": "ultra hd blu-ray", "architecture": "x86-64"},
    # Microsoft Home Consoles
    {"manufacturer": "Microsoft", "type": "Home Console", "name": "Xbox", "generation": 6, "release_year": "2001", "media_type": "dvd", "architecture": "x86"},
    {"manufacturer": "Microsoft", "type": "Home Console", "name": "Xbox 360", "generation": 7, "release_year": "2005", "media_type": "dvd", "architecture": "PowerPC"},
    {"manufacturer": "Microsoft", "type": "Home Console", "name": "Xbox One", "generation": 8, "release_year": "2013", "media_type": "blu-ray", "architecture": "x86-64"},
    {"manufacturer": "Microsoft", "type": "Home Console", "name": "Xbox Series X", "generation": 9, "release_year": "2020", "media_type": "ultra hd blu-ray", "architecture": "x86-64"},
    # SNK
    {"manufacturer": "SNK", "type": "Home Console", "name": "Neo Geo AES", "generation": 4, "release_year": "1990", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "SNK", "type": "Home Console", "name": "Neo Geo CD", "generation": 4, "release_year": "1994", "media_type": "cd", "architecture": "16-bit"},
    {"manufacturer": "SNK", "type": "Handheld", "name": "Neo Geo Pocket", "generation": 5, "release_year": "1998", "media_type": "cartridge", "architecture": "16-bit"},
    # Atari
    {"manufacturer": "Atari", "type": "Home Console", "name": "2600", "generation": 2, "release_year": "1977", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Atari", "type": "Home Console", "name": "5200", "generation": 2, "release_year": "1982", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Atari", "type": "Home Console", "name": "7800", "generation": 3, "release_year": "1986", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Atari", "type": "Home Console", "name": "Lynx", "generation": 4, "release_year": "1989", "media_type": "cartridge", "architecture": "8-bit"},
    {"manufacturer": "Atari", "type": "Home Console", "name": "Jaguar", "generation": 5, "release_year": "1993", "media_type": "cartridge", "architecture": "64-bit"},
    # Commodore
    {"manufacturer": "Commodore", "type": "Computer", "name": "C64", "generation": 2, "release_year": "1982", "media_type": "tape/disk", "architecture": "8-bit"},
    {"manufacturer": "Commodore", "type": "Computer", "name": "Amiga", "generation": 3, "release_year": "1985", "media_type": "disk", "architecture": "16-bit"},
    # Arcade
    {"manufacturer": "SNK", "type": "Arcade", "name": "Neo Geo MVS", "generation": 4, "release_year": "1990", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "Capcom", "type": "Arcade", "name": "CPS-1", "generation": 4, "release_year": "1988", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "Capcom", "type": "Arcade", "name": "CPS-2", "generation": 5, "release_year": "1993", "media_type": "cartridge", "architecture": "16-bit"},
    {"manufacturer": "Sega", "type": "Arcade", "name": "Naomi", "generation": 6, "release_year": "1998", "media_type": "gd-rom", "architecture": "128-bit"},
]

# Category mapping for folder structure
CATEGORY_MAP = {
    "Home Console": "Home Consoles",
    "Handheld": "Handhelds",
    "Computer": "Computers",
    "Arcade": "Arcade"
}

root = Path(__file__).parent / "Consoles"
created = 0
manufacturers = set()

for c in CONSOLES:
    category = CATEGORY_MAP.get(c["type"], c["type"])
    manufacturer = sanitize(c["manufacturer"])
    console_name = sanitize(c["name"])
    # Folder path: Consoles/<Category>/<Manufacturer>/<Console Name>/
    if c["type"] == "Handheld":
        folder = root / category / manufacturer / console_name
    elif c["type"] == "Computer":
        folder = root / category / manufacturer / console_name
    elif c["type"] == "Arcade":
        folder = root / category / manufacturer / console_name
    else:
        folder = root / category / manufacturer / console_name
    if folder.exists():
        continue
    # Create folders
    (folder / "roms").mkdir(parents=True, exist_ok=True)
    # Metadata
    tags = [
        manufacturer.lower(),
        c["type"].replace(" ", "_").lower(),
        f"gen-{c['generation']}",
        c["media_type"].lower(),
        c["architecture"].lower()
    ]
    meta = {
        "manufacturer": c["manufacturer"],
        "type": c["type"],
        "generation": c["generation"],
        "release_year": c["release_year"],
        "media_type": c["media_type"],
        "tags": tags
    }
    with open(folder / "console_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    created += 1
    manufacturers.add(c["manufacturer"])

print(f"\n✅ Created {created} folders across {len(manufacturers)} manufacturers")

import os
import requests
import xmltodict
import binascii
import shutil
from pathlib import Path
from urllib.parse import quote
import re

def download_dat_file(dat_path):
    print("Downloading No-Intro SNES DAT file...")
    response = requests.get("https://datomatic.no-intro.org/datfiles/15")
    if response.status_code == 200:
        with open(dat_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded DAT file to {dat_path}")
    else:
        print("Failed to download DAT file.")
        exit(1)

def parse_dat_file(dat_path):
    print("Parsing DAT file...")
    with open(dat_path, "rb") as f:
        dat = xmltodict.parse(f.read())
    rom_info = {}
    for game in dat['datafile']['game']:
        rom = game['rom']
        genre = game.get('category', 'Unknown')
        title = game['@name'] if '@name' in game else rom['@name']
        region = game.get('region', 'Unknown')
        if isinstance(rom, list):
            for r in rom:
                rom_info[r['@crc'].lower()] = {
                    'name': r['@name'],
                    'title': title,
                    'genre': genre,
                    'region': region,
                    'ext': os.path.splitext(r['@name'])[1]
                }
        else:
            rom_info[rom['@crc'].lower()] = {
                'name': rom['@name'],
                'title': title,
                'genre': genre,
                'region': region,
                'ext': os.path.splitext(rom['@name'])[1]
            }
    return rom_info

def compute_crc32(file_path):
    buf_size = 65536
    crc = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            crc = binascii.crc32(data, crc)
    return format(crc & 0xFFFFFFFF, '08x')

def download_cover(game_title, covers_dir):
    search_url = f"https://www.bing.com/images/search?q={quote(game_title + ' SNES cover')}&form=HDRSC2"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            match = re.search(r'imgurl:&quot;(https://[^&]+)', resp.text)
            if match:
                img_url = match.group(1)
                img_ext = os.path.splitext(img_url)[1].split('?')[0]
                cover_path = os.path.join(covers_dir, f"{game_title}{img_ext}")
                img_resp = requests.get(img_url, stream=True, timeout=10)
                if img_resp.status_code == 200:
                    with open(cover_path, 'wb') as f:
                        shutil.copyfileobj(img_resp.raw, f)
                    print(f"Downloaded cover for {game_title}")
                    return cover_path
    except Exception as e:
        print(f"Failed to download cover for {game_title}: {e}")
    return None

def menu():
    print("\nSNES ROM Manager")
    print("1. Check ROM health")
    print("2. Auto-sort ROMs by genre and letter")
    print("3. Download covers for good ROMs")
    print("4. Show missing games report")
    print("5. Run all (recommended)")
    print("0. Exit")
    return input("Select an option: ").strip()

def get_rom_dir():
    rom_dir = input("Enter the path to your SNES ROM directory (e.g. C:/Games/SNES): ").strip('"')
    if not os.path.isdir(rom_dir):
        print("Invalid directory.")
        return None
    return rom_dir

def main():
    DAT_FILENAME = "Super_Nintendo_Entertainment_System_No-Intro.dat"
    dat_path = Path(DAT_FILENAME)
    if not dat_path.exists():
        download_dat_file(dat_path)
    rom_info = parse_dat_file(dat_path)
    rom_dir = None
    good = []
    bad = []
    covers_dir = None
    while True:
        choice = menu()
        if choice == '0':
            break
        if not rom_dir:
            rom_dir = get_rom_dir()
            if not rom_dir:
                continue
            covers_dir = os.path.join(rom_dir, 'Covers')
            os.makedirs(covers_dir, exist_ok=True)
        if choice in {'1', '5'}:
            print("\nChecking ROMs...")
            good.clear()
            bad.clear()
            for root, _, files in os.walk(rom_dir):
                for file in files:
                    if file.lower().endswith(('.sfc', '.smc')):
                        file_path = os.path.join(root, file)
                        crc = compute_crc32(file_path)
                        if crc in rom_info:
                            good.append((file, file_path, rom_info[crc]))
                        else:
                            bad.append(file)
            print("\nGood ROMs:")
            for file, _, info in good:
                print(f"  {file} (matches: {info['title']})")
            print("\nBad ROMs:")
            for file in bad:
                print(f"  {file}")
            print(f"\nSummary: {len(good)} good, {len(bad)} bad.")
            if choice == '1':
                continue
        if choice in {'2', '5'}:
            print("\nSorting and renaming good ROMs...")
            for file, file_path, info in good:
                genre = info['genre'] or 'Unknown'
                first_letter = info['title'][0].upper() if info['title'] else 'U'
                region = info['region'] or 'Unknown'
                ext = info['ext']
                safe_title = ''.join(c for c in info['title'] if c not in '\/:*?"<>|').strip()
                new_name = f"{safe_title} ({region}){ext}"
                target_dir = os.path.join(rom_dir, genre, first_letter)
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, new_name)
                if os.path.abspath(file_path) != os.path.abspath(target_path):
                    try:
                        os.rename(file_path, target_path)
                        print(f"Moved: {file} -> {target_path}")
                    except Exception as e:
                        print(f"Failed to move {file}: {e}")
            if choice == '2':
                continue
        if choice in {'3', '5'}:
            print("\nDownloading covers for good ROMs...")
            for file, _, info in good:
                safe_title = ''.join(c for c in info['title'] if c not in '\/:*?"<>|').strip()
                cover_filename = f"{safe_title}.jpg"
                cover_path = os.path.join(covers_dir, cover_filename)
                if not os.path.exists(cover_path):
                    download_cover(safe_title, covers_dir)
            if choice == '3':
                continue
        if choice in {'4', '5'}:
            print("\nMissing SNES Games (compared to full Nintendo list):")
            all_titles = set(info['title'] for info in rom_info.values())
            found_titles = set(info['title'] for _, _, info in good)
            missing_titles = sorted(all_titles - found_titles)
            for title in missing_titles:
                print(f"  {title}")
            print(f"\nTotal missing: {len(missing_titles)}")
            if choice == '4':
                continue
        if choice not in {'1','2','3','4','5','0'}:
            print("Invalid option.")

if __name__ == "__main__":
    main()

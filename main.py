import os
import requests
import xmltodict
import binascii
from pathlib import Path

NOINTRO_DAT_URL = "https://datomatic.no-intro.org/datfiles/15"
DAT_FILENAME = "Super_Nintendo_Entertainment_System_No-Intro.dat"


def download_dat_file(dat_path):
    print("Downloading No-Intro SNES DAT file...")
    response = requests.get(NOINTRO_DAT_URL)
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
    rom_hashes = {}
    for game in dat['datafile']['game']:
        rom = game['rom']
        if isinstance(rom, list):
            for r in rom:
                rom_hashes[r['@crc'].lower()] = r['@name']
        else:
            rom_hashes[rom['@crc'].lower()] = rom['@name']
    return rom_hashes


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


def main():
    dat_path = Path(DAT_FILENAME)
    if not dat_path.exists():
        download_dat_file(dat_path)
    rom_hashes = parse_dat_file(dat_path)

    rom_dir = input("Enter the path to your SNES ROM directory: ").strip('"')
    if not os.path.isdir(rom_dir):
        print("Invalid directory.")
        return

    print("\nChecking ROMs...")
    good = []
    bad = []
    for root, _, files in os.walk(rom_dir):
        for file in files:
            if file.lower().endswith(('.sfc', '.smc')):
                file_path = os.path.join(root, file)
                crc = compute_crc32(file_path)
                if crc in rom_hashes:
                    good.append((file, rom_hashes[crc]))
                else:
                    bad.append(file)

    print("\nGood ROMs:")
    for file, name in good:
        print(f"  {file} (matches: {name})")
    print("\nBad ROMs:")
    for file in bad:
        print(f"  {file}")
    print(f"\nSummary: {len(good)} good, {len(bad)} bad.")

if __name__ == "__main__":
    main()

import os
import requests
from bs4 import BeautifulSoup

WIKI_URL = 'https://en.wikipedia.org/wiki/Home_video_game_console#List_of_home_video_game_consoles'
ROOT = 'ROMForge/Consoles'

def clean_name(name):
    return ''.join(c for c in name if c not in '\\/:*?"<>|').strip()

def main():
    print('Fetching Wikipedia page...')
    resp = requests.get(WIKI_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    created = 0
    # Find all tables under the 'List of home video game consoles' section
    tables = soup.find_all('table', {'class': 'wikitable'})
    for table in tables:
        # Get table headers
        headers = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue
            # Extract fields
            name = cols[0].get_text(strip=True)
            manufacturer = cols[1].get_text(strip=True)
            generation = ''
            release_year = ''
            wiki_url = ''
            for i, h in enumerate(headers):
                if 'generation' in h.lower():
                    generation = cols[i].get_text(strip=True) if i < len(cols) else ''
                if 'release' in h.lower():
                    release_year = cols[i].get_text(strip=True) if i < len(cols) else ''
            link = cols[0].find('a')
            if link and link.has_attr('href'):
                wiki_url = 'https://en.wikipedia.org' + link['href']
            # Skip if missing data
            if not (name and manufacturer and generation and release_year and wiki_url):
                continue
            # Make folders
            folder = os.path.join(ROOT, 'Home Console', clean_name(manufacturer), clean_name(name))
            os.makedirs(os.path.join(folder, 'roms'), exist_ok=True)
            # Write console_info.txt
            info_path = os.path.join(folder, 'console_info.txt')
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"Manufacturer: {manufacturer}\n")
                f.write(f"Type: Home Console\n")
                f.write(f"Generation: {generation}\n")
                f.write(f"Release Year: {release_year}\n")
                f.write(f"Wikipedia URL: {wiki_url}\n")
            created += 1
            print(f"Created: {info_path}")
    print(f"\nCreated {created} console folders")

if __name__ == '__main__':
    main()

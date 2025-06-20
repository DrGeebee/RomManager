import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json
from time import sleep

def get_console_tables(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Find all tables with class 'wikitable'
    tables = soup.find_all('table', {'class': 'wikitable'})
    return tables

def parse_console_table(table, category):
    consoles = []
    headers = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]
    for row in table.find_all('tr')[1:]:
        cols = row.find_all(['td', 'th'])
        if len(cols) < 2:
            continue
        data = {h: (cols[i].get_text(strip=True) if i < len(cols) else '') for i, h in enumerate(headers)}
        # Extract fields
        name = data.get('Name') or data.get('Console') or data.get('System') or ''
        manufacturer = data.get('Manufacturer') or data.get('Maker') or ''
        gen = data.get('Generation') or data.get('Gen.') or ''
        year = data.get('Release date') or data.get('Released') or data.get('Release') or ''
        media = data.get('Media') or data.get('Media type') or ''
        # Clean up year
        year_match = re.search(r'(\d{4})', year)
        year = year_match.group(1) if year_match else ''
        # Clean up generation
        gen_match = re.search(r'(\d+)[a-z]{2}', gen.lower())
        generation = f"{gen_match.group(1)}-bit" if gen_match else gen
        # Find Wikipedia link
        link = cols[0].find('a')
        wiki_url = f"https://en.wikipedia.org{link['href']}" if link and link.has_attr('href') else ''
        consoles.append({
            'name': name,
            'manufacturer': manufacturer,
            'category': category,
            'generation': generation,
            'release_year': year,
            'media_type': media,
            'wikipedia_url': wiki_url
        })
    return consoles

def get_game_list(wiki_url):
    # Try to find a 'List of ... games' link on the console's Wikipedia page
    try:
        resp = requests.get(wiki_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Look for links like 'List of ... games'
        for a in soup.find_all('a', href=True):
            if a.text.lower().startswith('list of') and 'game' in a.text.lower():
                games_url = a['href']
                if not games_url.startswith('http'):
                    games_url = 'https://en.wikipedia.org' + games_url
                return scrape_games_from_list(games_url)
    except Exception as e:
        print(f"Could not get games for {wiki_url}: {e}")
    return []

def scrape_games_from_list(games_url):
    print(f"  Scraping games from: {games_url}")
    try:
        resp = requests.get(games_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        games = []
        # Try to find wikitable(s) with game lists
        tables = soup.find_all('table', {'class': 'wikitable'})
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]
            for row in table.find_all('tr')[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2:
                    continue
                data = {h: (cols[i].get_text(strip=True) if i < len(cols) else '') for i, h in enumerate(headers)}
                title = data.get('Title') or data.get('Game') or data.get('Name') or ''
                if not title:
                    continue
                games.append({
                    'title': title,
                    'developer': data.get('Developer', ''),
                    'publisher': data.get('Publisher', ''),
                    'release_date': data.get('Release date', '') or data.get('Release', ''),
                    'genre': data.get('Genre', ''),
                    'region': data.get('Region', ''),
                })
        return games
    except Exception as e:
        print(f"    Failed to scrape games: {e}")
    return []

def main():
    url = 'https://en.wikipedia.org/wiki/List_of_video_game_consoles'
    print('Fetching Wikipedia page...')
    tables = get_console_tables(url)
    all_consoles = []
    # Table order: Home, Handheld, PC, Arcade (approximate)
    categories = ['Home', 'Handheld', 'PC', 'Arcade']
    for i, table in enumerate(tables):
        cat = categories[i] if i < len(categories) else 'Other'
        consoles = parse_console_table(table, cat)
        all_consoles.extend(consoles)
    # Save to CSV and JSON
    df = pd.DataFrame(all_consoles)
    out_dir = Path('ROMForge/Consoles')
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / 'console_list.csv', index=False)
    df.to_json(out_dir / 'console_list.json', orient='records', indent=2)
    # Organize folders and scrape games
    for c in all_consoles:
        folder = out_dir / c['category'] / c['manufacturer'] / c['name']
        folder.mkdir(parents=True, exist_ok=True)
        meta = {
            'manufacturer': c['manufacturer'],
            'category': c['category'],
            'generation': c['generation'],
            'release_year': c['release_year'],
            'media_type': c['media_type'],
            'wikipedia_url': c['wikipedia_url']
        }
        with open(folder / 'console_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
        (folder / 'roms').mkdir(exist_ok=True)
        # Scrape games and save as games.json
        games = []
        if c.get('wikipedia_url'):
            games = get_game_list(c['wikipedia_url'])
            sleep(1)  # Be polite to Wikipedia
        if games:
            with open(folder / 'games.json', 'w', encoding='utf-8') as f:
                json.dump(games, f, indent=2)
            print(f"  Saved {len(games)} games for {c['name']}")
    print('Scraping and folder organization complete!')

if __name__ == '__main__':
    main()

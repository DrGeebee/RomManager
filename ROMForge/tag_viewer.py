import os
import json
import csv
from pathlib import Path

def load_metadata(console_dir):
    meta_path = Path(console_dir) / 'console_metadata.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def filter_consoles_by_tag(root, tag_key, tag_value):
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        if 'console_metadata.json' in filenames:
            meta = load_metadata(dirpath)
            if meta and meta.get(tag_key) == tag_value:
                results.append((dirpath, meta))
    return results

def search_by_manufacturer(root, manufacturer):
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        if 'console_metadata.json' in filenames:
            meta = load_metadata(dirpath)
            if meta and meta.get('manufacturer', '').lower() == manufacturer.lower():
                results.append((dirpath, meta))
    return results

def output_results(results, out_format='csv', out_file=None):
    if out_format == 'csv':
        keys = set()
        for _, meta in results:
            keys.update(meta.keys())
        keys = list(keys)
        if out_file:
            with open(out_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['path'] + keys)
                writer.writeheader()
                for path, meta in results:
                    row = {'path': path}
                    row.update(meta)
                    writer.writerow(row)
            print(f"CSV output written to {out_file}")
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=['path'] + keys)
            writer.writeheader()
            for path, meta in results:
                row = {'path': path}
                row.update(meta)
                writer.writerow(row)
    elif out_format == 'json':
        data = [{"path": path, **meta} for path, meta in results]
        if out_file:
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"JSON output written to {out_file}")
        else:
            print(json.dumps(data, indent=2))

def main():
    root = 'ROMForge/Consoles/'
    print("Tag Viewer Utility")
    print("1. Show all 16-bit handhelds")
    print("2. Search by manufacturer")
    print("3. Search by generation")
    print("4. Output to CSV")
    print("5. Output to JSON")
    choice = input("Select an option: ").strip()
    if choice == '1':
        results = filter_consoles_by_tag(root, 'architecture', '16-bit')
        results = [r for r in results if r[1].get('type') == 'handheld']
        output_results(results)
    elif choice == '2':
        mfg = input("Enter manufacturer: ")
        results = search_by_manufacturer(root, mfg)
        output_results(results)
    elif choice == '3':
        gen = int(input("Enter generation (1-9): "))
        results = filter_consoles_by_tag(root, 'generation', gen)
        output_results(results)
    elif choice == '4':
        tag = input("Tag key: ")
        val = input("Tag value: ")
        results = filter_consoles_by_tag(root, tag, val)
        output_results(results, out_format='csv', out_file='ROMForge/Reports/tag_view.csv')
    elif choice == '5':
        tag = input("Tag key: ")
        val = input("Tag value: ")
        results = filter_consoles_by_tag(root, tag, val)
        output_results(results, out_format='json', out_file='ROMForge/Reports/tag_view.json')
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Apply translations from JSON files to property HTML pages.
Reads translations_batch_*.json files, merges them, and updates HTML files.
"""
import json
import os
import re
import glob


DIRS = {
    'fr': 'biens',
    'en': 'en/properties-list',
    'nl': 'nl/vastgoed',
}


def find_html_file(slug, lang):
    """Find the HTML file for a given slug and language."""
    directory = DIRS[lang]
    # Try exact slug match first
    path = os.path.join(directory, f"{slug}.html")
    if os.path.exists(path):
        return path
    # Try with language suffix
    suffix = f"-{lang}" if lang != 'fr' else ''
    path = os.path.join(directory, f"{slug}{suffix}.html")
    if os.path.exists(path):
        return path
    return None


def apply_to_html(filepath, translation):
    """Apply a translation dict to an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # 1. Update <title>
    if translation.get('meta_title'):
        html = re.sub(
            r'<title>.*?</title>',
            f'<title>{translation["meta_title"]}</title>',
            html, count=1
        )

    # 2. Add or update <meta name="description">
    if translation.get('meta_description'):
        desc = translation['meta_description'].replace('"', '&quot;')
        if re.search(r'<meta\s+name="description"', html):
            html = re.sub(
                r'<meta\s+name="description"\s+content="[^"]*"[^>]*/?>',
                f'<meta name="description" content="{desc}">',
                html, count=1
            )
        else:
            # Insert after <meta name="viewport"...>
            html = re.sub(
                r'(<meta\s+name="viewport"[^>]*>)',
                f'\\1\n    <meta name="description" content="{desc}">',
                html, count=1
            )

    # 3. Update property description
    if translation.get('description_html'):
        html = re.sub(
            r'(<div class="property-description">).*?(</div>\s*\n?\s*<h2)',
            lambda m: m.group(1) + '\n' + translation['description_html'] + '\n                ' + m.group(2),
            html, count=1, flags=re.DOTALL
        )

    # 4. Update amenities
    if translation.get('amenities') and isinstance(translation['amenities'], list):
        amenities_items = ''.join(
            f'<li><i class="fas fa-check"></i> {item}</li>' for item in translation['amenities']
        )
        html = re.sub(
            r'(<ul class="amenities-list">).*?(</ul>)',
            f'\\1{amenities_items}\\2',
            html, count=1, flags=re.DOTALL
        )

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def main():
    # Load all batch files
    batch_files = sorted(glob.glob('translations_batch_*.json'))
    if not batch_files:
        print("No translations_batch_*.json files found!")
        return

    all_translations = {}
    for bf in batch_files:
        with open(bf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_translations.update(data)
        print(f"Loaded {len(data)} properties from {bf}")

    print(f"\nTotal: {len(all_translations)} properties to process")

    # Apply translations
    updated = 0
    skipped = 0
    missing = 0

    for slug, langs in all_translations.items():
        for lang, translation in langs.items():
            filepath = find_html_file(slug, lang)
            if not filepath:
                missing += 1
                continue
            if apply_to_html(filepath, translation):
                updated += 1
            else:
                skipped += 1

    print(f"\nDone: {updated} files updated, {skipped} unchanged, {missing} missing files")


if __name__ == '__main__':
    main()

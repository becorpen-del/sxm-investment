#!/usr/bin/env python3
"""
Rebuild data.json by parsing the existing HTML property pages in biens/, en/properties-list/, nl/vastgoed/.
This recreates the data.json that generate_all.py expects.
"""
import json
import os
import re
from html.parser import HTMLParser


DIRS = {
    'fr': 'biens',
    'en': 'en/properties-list',
    'nl': 'nl/vastgoed',
}

# Maps FR detail table headers to field names
FR_HEADERS = {
    'Localisation': 'location',
    'Type': 'type',
    'Année': 'year_built',
    'Vue': 'view',
    'Climatisation': 'cooling',
    'Piscine': 'pool',
}
EN_HEADERS = {
    'Location': 'location',
    'Type': 'type',
    'Year': 'year_built',
    'View': 'view',
    'Cooling': 'cooling',
    'Pool': 'pool',
}
NL_HEADERS = {
    'Locatie': 'location',
    'Type': 'type',
    'Bouwjaar': 'year_built',
    'Uitzicht': 'view',
    'Airco': 'cooling',
    'Zwembad': 'pool',
}
HEADER_MAPS = {'fr': FR_HEADERS, 'en': EN_HEADERS, 'nl': NL_HEADERS}

# 72 biens Andréou à garder (Section A)
ALLOWED_SLUGS = {
    '1-bedroom-condo-at-la-terrasse-maho-beach',
    '1-bedroom-condo-with-large-terrace-at-blue-marine-maho',
    '1-bedroom-ocean-view-condo-for-sale-in-point-blanche-las-colinas',
    '2-bedroom-at-cupecoy-beach-club-with-garden-views',
    '2-bedroom-with-dual-rental-potential',
    '4-bedroom-aqua-villa-with-boat-slip',
    'apartment-building-le-diamand-blanc',
    'aqualina-beach-club-luxury-condo',
    'aquamarina-2-bedroom-condo-point-pirouette',
    'aquamarina-4-bedroom-penthouse',
    'aquamarina-villa',
    'beachfront-2-bedroom-condo-at-the-cliff',
    'beachfront-multi-unit-residence',
    'brand-new-villa-lagoon',
    'commercial-retail-space-belair-plaza-type-b',
    'concord-2-bedroom-condo',
    'concord-penthouse',
    'condo-for-sale-in-maho-village-la-terrasse-royal-islander-club',
    'cozy-1-bedroom-condo-for-sale-in-maho-village-sint-maarten-la-terrasse',
    'cupecoy-beach-club-turnkey-investment-condo',
    'cupecoy-beachfront-3-bedroom-condo',
    'diamond-hill-multi-family-property',
    'dual-studio-condo-investment-in-pelican',
    'elegant-3-bedroom-ocean-view-condo-i-porto-cupecoy',
    'elegant-ocean-view-condo-at-fourteen-mullet-bay',
    'elevated-island-living-fourteen-mullet-bay',
    'exceptional-4-bedroom-penthouse',
    'house-with-2-apartments',
    'infinity-villas-by-elie-saab-frontline-villas',
    'infinity-villas-by-elie-saab-highline-villas',
    'investment-opportunity-at-the-hills-residence-1-bedroom-condo',
    'la-maddalena-new-development-in-cupecoy',
    'le-papillon-penthouse',
    'luxury-beachfront-condo-for-sale-in-cupecoy',
    'luxury-marina-view-condo-for-sale-porto-cupecoy',
    'marina-2-bedroom-condo-porto-cupecoy',
    'new-cay-hill-condos-mountblu-estate',
    'new-waterfront-aqua-villa-cupecoy',
    'ocean-view-condo-at-rainbow-beach-club-cupecoy',
    'ocean-view-condo-for-sale-at-sapphire-beach-club-cupecoy',
    'ocean-view-condo-for-sale-princess-heights',
    'oceanfront-2-bedroom-condo-at-rainbow-beach-club',
    'office-space-for-sale-in-cay-hill-belair-plaza-unit-12',
    'panoramic-view-at-solea-residence-little-bay',
    'pre-construction-condo-in-cay-hill-belair-plaza',
    'pre-construction-condo-in-cay-hill-belair-plaza-unit-f',
    'pre-construction-ocean-view-studio-in-pelican-key-concord-residence',
    'prime-beachfront-investment-at-rainbow-beach-club',
    'pristine-2-bedroom-condo-with-boat-slip-aquamarina',
    'red-pond-villa',
    'renovated-3-bedroom-duplex-in-cupecoy',
    'sapphire-beach-club-penthouse',
    'sapphire-penthouse',
    'spacious-5-bedroom-duplex-guana-bay',
    'tennis-building-condo-at-rainbow-beach-club-cupecoy',
    'the-hills-residence-1-bedroom-condo-for-sale',
    'top-floor-beachfront-condo-cupecoy-beach-club',
    'top-floor-condo-porto-cupecoy',
    'turnkey-condo-at-the-hills-residence-simpson-bay',
    'villa-always',
    'villa-avanti-a-private-resort-estate',
    'villa-coralia',
    'villa-lotus',
    'villa-oceane',
    'villa-shiaou',
    'villa-sophia',
    'villa-with-3-apartments-and-boat-slip',
    'vivid-residences-sint-maarten-ocean-view-condos-for-sale',
    'waterfront-condo-for-sale-with-marina-views-boat-slip',
    'white-sand-beachfront-2-bedroom-condo',
    'windgate-luxury-condo',
}


def parse_property_html(filepath, lang):
    """Parse a single property HTML file and extract all metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    slug = os.path.splitext(os.path.basename(filepath))[0]
    prop = {'slug': slug, 'language': lang}

    # Title from <h1>
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    prop['title'] = m.group(1).strip() if m else slug

    # Price from .property-hero-price
    m = re.search(r'class="property-hero-price"[^>]*>(.*?)</span>', html, re.DOTALL)
    prop['price'] = m.group(1).strip() if m else ''

    # Location from .property-hero-location
    m = re.search(r'class="property-hero-location"[^>]*>.*?</i>\s*(.*?)</span>', html, re.DOTALL)
    prop['location'] = m.group(1).strip() if m else ''

    # Feature items: bedrooms, bathrooms, surface, type
    features = re.findall(
        r'<div class="feature-item">.*?<strong>(.*?)</strong>.*?</div>\s*</div>',
        html, re.DOTALL
    )
    if len(features) >= 1:
        prop['rooms'] = features[0].strip()
    if len(features) >= 2:
        prop['baths'] = features[1].strip()
    if len(features) >= 3:
        prop['sqft'] = features[2].strip()
    if len(features) >= 4:
        prop['type'] = features[3].strip()

    # Description
    m = re.search(r'<div class="property-description">(.*?)</div>', html, re.DOTALL)
    if m:
        prop['content'] = m.group(1).strip()
    else:
        prop['content'] = ''

    # Gallery images from lightbox slides (most reliable source)
    gallery_imgs = re.findall(r'<div class="lightbox-slide"><img src="([^"]+)"', html)
    if gallery_imgs:
        # Normalize paths: remove ../ prefix to get images/properties/... format
        normalized = []
        for img in gallery_imgs:
            cleaned = img
            while cleaned.startswith('../'):
                cleaned = cleaned[3:]
            normalized.append(cleaned)
        prop['gallery_images'] = ','.join(normalized)
    else:
        prop['gallery_images'] = ''

    # Details table (year_built, view, cooling, pool)
    header_map = HEADER_MAPS.get(lang, FR_HEADERS)
    rows = re.findall(r'<tr>\s*<th>(.*?)</th>\s*<td>(.*?)</td>\s*</tr>', html, re.DOTALL)
    for th, td in rows:
        th_clean = th.strip()
        td_clean = td.strip()
        field = header_map.get(th_clean)
        if field and field not in ('location', 'type'):
            # location and type already extracted above, only fill supplementary fields
            prop[field] = td_clean

    # Amenities (if present)
    m = re.search(r'<ul class="amenities-list">(.*?)</ul>', html, re.DOTALL)
    if m:
        items = re.findall(r'<li>.*?</i>\s*(.*?)</li>', m.group(1), re.DOTALL)
        prop['amenities'] = '\n'.join(i.strip() for i in items)
    else:
        prop['amenities'] = ''

    # Categories (reconstruct from location)
    categories = []
    if prop.get('location'):
        loc_slug = re.sub(r'[^a-z0-9]+', '-', prop['location'].lower()).strip('-')
        categories.append({'domain': 'project-location', 'nicename': loc_slug})
    if prop.get('type'):
        type_slug = re.sub(r'[^a-z0-9]+', '-', prop['type'].lower()).strip('-')
        categories.append({'domain': 'project-type', 'nicename': type_slug})
    prop['categories'] = categories

    return prop


def main():
    # Parse all FR properties (reference)
    fr_dir = DIRS['fr']
    fr_files = sorted([
        f for f in os.listdir(fr_dir)
        if f.endswith('.html') and os.path.splitext(f)[0] in ALLOWED_SLUGS
    ])
    print(f"Found {len(fr_files)} allowed FR property files in {fr_dir}/ (out of {len([f for f in os.listdir(fr_dir) if f.endswith('.html')])} total)")

    all_properties = []
    properties_by_slug = {}

    for filename in fr_files:
        slug = os.path.splitext(filename)[0]
        props_for_slug = {}

        # Parse each language version
        for lang, directory in DIRS.items():
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                prop = parse_property_html(filepath, lang)
                all_properties.append(prop)
                props_for_slug[lang] = prop
            else:
                print(f"  WARNING: Missing {lang} version for {slug}")

        properties_by_slug[slug] = props_for_slug

    # Build output
    data = {
        'properties': all_properties,
        'properties_by_slug': properties_by_slug,
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Stats
    lang_counts = {}
    for p in all_properties:
        lang_counts[p['language']] = lang_counts.get(p['language'], 0) + 1

    print(f"\nGenerated data.json with {len(all_properties)} total entries:")
    for lang in ('fr', 'en', 'nl'):
        print(f"  {lang.upper()}: {lang_counts.get(lang, 0)} properties")
    print(f"  Unique slugs: {len(properties_by_slug)}")


if __name__ == '__main__':
    main()

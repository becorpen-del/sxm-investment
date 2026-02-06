#!/usr/bin/env python3
"""
Script to parse WordPress XML export and extract properties data
"""
import xml.etree.ElementTree as ET
import json
import re
import html
from collections import defaultdict

# Namespaces used in WordPress export
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

def clean_html(text):
    """Remove HTML tags and clean text"""
    if not text:
        return ""
    # Remove CDATA markers
    text = re.sub(r'<!\[CDATA\[|\]\]>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    return text.strip()

def extract_text(element, tag, namespaces=None):
    """Extract text from an XML element"""
    if namespaces:
        el = element.find(tag, namespaces)
    else:
        el = element.find(tag)
    if el is not None and el.text:
        return clean_html(el.text)
    return ""

def parse_wordpress_xml(xml_path):
    """Parse WordPress XML and extract all content"""
    print(f"Parsing {xml_path}...")

    # Parse with iterparse for large files
    properties = []
    pages = []
    attachments = []

    current_item = None
    current_meta = {}
    current_categories = []

    for event, elem in ET.iterparse(xml_path, events=('start', 'end')):
        if event == 'start' and elem.tag == 'item':
            current_item = {
                'title': '',
                'content': '',
                'excerpt': '',
                'post_id': '',
                'post_name': '',
                'post_type': '',
                'status': '',
                'meta': {},
                'categories': [],
                'language': 'en'  # default
            }
            current_meta = {}
            current_categories = []

        elif event == 'end':
            if elem.tag == 'title' and current_item is not None:
                current_item['title'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == '{http://purl.org/rss/1.0/modules/content/}encoded' and current_item is not None:
                current_item['content'] = elem.text if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}post_id' and current_item is not None:
                current_item['post_id'] = elem.text if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}post_name' and current_item is not None:
                current_item['post_name'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}post_type' and current_item is not None:
                current_item['post_type'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}status' and current_item is not None:
                current_item['status'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}attachment_url' and current_item is not None:
                current_item['attachment_url'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == 'category' and current_item is not None:
                domain = elem.get('domain', '')
                nicename = elem.get('nicename', '')
                value = clean_html(elem.text) if elem.text else ''
                current_categories.append({
                    'domain': domain,
                    'nicename': nicename,
                    'value': value
                })
                # Detect language
                if domain == 'language':
                    if nicename == 'fr':
                        current_item['language'] = 'fr'
                    elif nicename == 'nl':
                        current_item['language'] = 'nl'
                    elif nicename == 'en':
                        current_item['language'] = 'en'

            elif elem.tag == '{http://wordpress.org/export/1.2/}meta_key' and current_item is not None:
                current_meta['key'] = clean_html(elem.text) if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}meta_value' and current_item is not None:
                current_meta['value'] = elem.text if elem.text else ''

            elif elem.tag == '{http://wordpress.org/export/1.2/}postmeta' and current_item is not None:
                if current_meta.get('key') and not current_meta['key'].startswith('_'):
                    current_item['meta'][current_meta['key']] = current_meta.get('value', '')
                current_meta = {}

            elif elem.tag == 'item' and current_item is not None:
                current_item['categories'] = current_categories

                # Categorize by post type
                if current_item['post_type'] == 'project' and current_item['status'] == 'publish':
                    properties.append(current_item)
                elif current_item['post_type'] == 'page':
                    pages.append(current_item)
                elif current_item['post_type'] == 'attachment':
                    attachments.append(current_item)

                current_item = None
                elem.clear()

    return properties, pages, attachments

def organize_properties_by_language(properties):
    """Group properties by their translation groups"""
    # Group by post_name (slug)
    by_slug = defaultdict(dict)

    for prop in properties:
        slug = prop['post_name']
        lang = prop['language']
        by_slug[slug][lang] = prop

    return dict(by_slug)

def extract_property_data(prop):
    """Extract structured data from a property"""
    meta = prop.get('meta', {})
    categories = prop.get('categories', [])

    # Extract location from categories
    location = ''
    property_type = ''
    price_range_cat = ''

    for cat in categories:
        if cat['domain'] == 'project-location':
            location = cat['value']
        elif cat['domain'] == 'project-type':
            property_type = cat['value']
        elif cat['domain'] == 'project-status':
            price_range_cat = cat['value']

    return {
        'id': prop['post_id'],
        'slug': prop['post_name'],
        'title': prop['title'],
        'language': prop['language'],
        'content': prop['content'],
        'location': meta.get('project_location', location),
        'price': meta.get('price_range', ''),
        'rooms': meta.get('rooms', ''),
        'baths': meta.get('baths', ''),
        'sqft': meta.get('sqft', ''),
        'floor': meta.get('floor', ''),
        'type': property_type,
        'status': meta.get('project_status', ''),
        'neighborhood': meta.get('more_information_neighborhood', ''),
        'address': meta.get('more_information_full_address', ''),
        'amenities': meta.get('more_information_ameneties', ''),
        'property_type': meta.get('property_features_property_type', ''),
        'year_built': meta.get('property_features_year_built', ''),
        'cooling': meta.get('property_features_cooling_type', ''),
        'flooring': meta.get('property_features_flooring', ''),
        'garage': meta.get('property_features_garage', ''),
        'parking': meta.get('property_features_parking_space', ''),
        'pool': meta.get('property_features_pool', ''),
        'view': meta.get('property_features_view', ''),
        'agent': meta.get('agent', ''),
        'email': meta.get('email', ''),
        'phone': meta.get('phone', ''),
        'gallery_images': meta.get('gallery_images', ''),
        'categories': categories
    }

def main():
    xml_path = '/Users/benjaminlegal/Downloads/sxmdreaminvestments.WordPress.2026-01-20.xml'

    # Parse XML
    properties, pages, attachments = parse_wordpress_xml(xml_path)

    print(f"\nFound:")
    print(f"  - {len(properties)} published properties")
    print(f"  - {len(pages)} pages")
    print(f"  - {len(attachments)} attachments")

    # Count by language
    lang_count = defaultdict(int)
    for prop in properties:
        lang_count[prop['language']] += 1
    print(f"\nProperties by language:")
    for lang, count in lang_count.items():
        print(f"  - {lang}: {count}")

    # Extract structured data
    structured_properties = [extract_property_data(p) for p in properties]

    # Group by slug
    properties_by_slug = organize_properties_by_language(properties)
    print(f"\nUnique properties (by slug): {len(properties_by_slug)}")

    # Extract image URLs
    image_urls = []
    for att in attachments:
        if att.get('attachment_url'):
            url = att['attachment_url']
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                image_urls.append({
                    'title': att['title'],
                    'url': url,
                    'post_id': att['post_id']
                })

    print(f"Image URLs found: {len(image_urls)}")

    # Save to JSON
    output = {
        'properties': structured_properties,
        'properties_by_slug': {slug: {lang: extract_property_data(p) for lang, p in langs.items()}
                               for slug, langs in properties_by_slug.items()},
        'pages': [{'title': p['title'], 'slug': p['post_name'], 'status': p['status']} for p in pages],
        'images': image_urls[:500]  # Limit for now
    }

    with open('/Users/benjaminlegal/Documents/SXM-Invest/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nData saved to data.json")

    # Print some sample properties
    print("\n--- Sample Properties ---")
    seen_slugs = set()
    for prop in structured_properties[:20]:
        if prop['slug'] not in seen_slugs and prop['language'] == 'fr':
            print(f"  - {prop['title']} | {prop['price']} | {prop['location']} | {prop['type']}")
            seen_slugs.add(prop['slug'])

if __name__ == '__main__':
    main()

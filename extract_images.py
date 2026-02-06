#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json
import re

# Parse XML
print("Parsing WordPress XML...")
tree = ET.parse('/Users/benjaminlegal/Downloads/sxmdreaminvestments.WordPress.2026-01-20.xml')
root = tree.getroot()

# Namespaces
ns = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
}

# Build attachment map: post_id -> URL
attachments = {}
for item in root.findall('.//item'):
    post_type = item.find('wp:post_type', ns)
    if post_type is not None and post_type.text == 'attachment':
        post_id = item.find('wp:post_id', ns)
        guid = item.find('guid')
        if post_id is not None and guid is not None:
            attachments[post_id.text] = guid.text

print(f"Found {len(attachments)} attachments")

# Build property -> thumbnail map
property_images = {}
for item in root.findall('.//item'):
    post_type = item.find('wp:post_type', ns)
    if post_type is not None and post_type.text == 'project':
        post_id = item.find('wp:post_id', ns)
        title = item.find('title')
        
        if post_id is None:
            continue
            
        pid = post_id.text
        ptitle = title.text if title is not None else ''
        
        # Find thumbnail ID in postmeta
        for meta in item.findall('wp:postmeta', ns):
            key = meta.find('wp:meta_key', ns)
            val = meta.find('wp:meta_value', ns)
            if key is not None and val is not None:
                if key.text == '_thumbnail_id' and val.text:
                    thumb_id = val.text
                    if thumb_id in attachments:
                        property_images[pid] = attachments[thumb_id]
                        break
                # Also check for gallery images
                if key.text == 'fave_property_images' and val.text:
                    # This might be serialized PHP array
                    img_ids = re.findall(r'"(\d+)"', val.text)
                    if img_ids and img_ids[0] in attachments:
                        property_images[pid] = attachments[img_ids[0]]

print(f"Found {len(property_images)} properties with images")

# Load and update data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for prop in data['properties']:
    pid = prop.get('id')
    if pid and pid in property_images:
        prop['featured_image'] = property_images[pid]
        updated += 1

print(f"Updated {updated} properties with images")

# Save
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved updated data.json")

# Show some examples
print("\nExamples:")
for prop in data['properties'][:5]:
    print(f"  {prop.get('title')}: {prop.get('featured_image', 'NO IMAGE')[:60]}...")

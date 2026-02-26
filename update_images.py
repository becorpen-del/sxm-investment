#!/usr/bin/env python3
"""
Script de mise à jour des images du site SXM-Invest.
- Cherche les meilleures images (edited, sans logo) dans les downloads
- Redimensionne à 1920px max de large
- Compresse en JPEG qualité 85
- Met à jour data.json
"""

import os
import json
import shutil
from PIL import Image
import re

SITE_DIR = '/Users/benjaminlegal/Documents/SXM-Invest/images/properties'
DL_BASE = '/Users/benjaminlegal/Downloads/LISTINGS FOR SALE/LISTINGS FOR SALE'
DATA_JSON = '/Users/benjaminlegal/Documents/SXM-Invest/data.json'

MAX_WIDTH = 1920
MAX_HEIGHT = 1280
JPEG_QUALITY = 85
MAX_IMAGES = 30

# Complete mapping: site_slug -> download_path (relative to DL_BASE)
MAPPING = {
    '2-bedroom-with-dual-rental-potential': None,  # Already has 30 good images
    '3-bedroom-aqua-villa-new': 'CUPECOY/AQUA VILLAS',
    '3-bedroom-at-blue-marine-residences-2': 'MAHO/Blue Marine B17 3-bedroom',
    '3-bedroom-blue-marine-penthouse': None,  # No clear match after C18 reassignment
    '4-bedroom-aqua-villa-with-boat-slip': 'CUPECOY/AQUA VILLAS',
    'apartment-building-le-diamand-blanc-2': 'OYSTER POND - DAWN BEACH/Oyster Pond Building Diamand Blanc',
    'aquamarina-villa-2': 'CUPECOY/Aquamarina Villa #4 $1,495,000',
    'beachfront-coco-beach-condo': 'SIMPSON BAY/Coco Beach Simpson 2-bedroom',
    'beachfront-condo-at-sapphire-resort': 'CUPECOY/Sapphire 2 bed condo Cupecoy',
    'beachfront-cupecoy-condo': 'CUPECOY/Beachfront-cupecoy-condo',
    'brand-new-villa-lagoon-2': 'POINT PIROUETTE/Villa Lagoon 5',
    'concord-2-bedroom-condo': 'NEW DEVELOPMENTS/Concord Residence, Pelican ',
    'concord-penthouse': 'NEW DEVELOPMENTS/Concord Residence, Pelican ',
    'condo-in-maho-beach': 'MAHO/La Terrace #5591',
    'cupecoy-beachfront-3-bedroom-condo': 'CUPECOY/Cupecoy Beach Club 220- 3-bedroom',
    'exceptional-4-bedroom-penthouse': 'MAHO/Blue Marine C18 4-bedroom',
    'great-bay-villas': 'PHILIPSBURG/Great Bay Villa',
    'guana-bay-penthouse': 'GUANA BAY/Guana Bay Penthouse',
    'la-lagune-top-floor': 'NETTLE BAY/La Lagune 425 3-bedroom ',
    'large-condo-with-yard': 'CUPECOY/CBC 202 - 2-bedroom',
    'large-studio-with-separated-bedroom': 'CUPECOY/Studio 1 bedroom Sapphire Cupecoy',
    'large-terrace-blue-marine-condo': 'MAHO/C5 Blue Marine',
    'le-papillon-penthouse': 'SIMPSON BAY/Le Papillon Penthouse',
    'maho-beach-1-bedroom': 'SOLD/Maho-beach-1-bedroom',
    'modern-beachfront-condo-2': 'SOLD/Simpson bay beach 2-bed-2',
    'multi-unit-residential-building-direct-beach-access': 'SIMPSON BAY/Building Simpson Bay Road 36 ',
    'multifamily-home-rental-income-cole-bay': None,  # Not found in downloads
    'oceanfront-living-3-bedroom-in-cupecoy': 'CUPECOY/CBC 212 950k',
    'palm-beach-1-bedroom-condo': 'SIMPSON BAY/Palm beach 1-bed',
    'pelican-cove-villa': 'PELICAN KEY/Pelican Villa 5 bedrooms - Thomas',
    'penthouse-aquamarina-4-chambres': 'SIMPSON BAY/Aquamarina Penthouse Edited with logo',
    'penthouse-condo-in-maho': 'MAHO/La Terrace 1178',
    'porto-cupecoy-penthouse': 'CUPECOY/Porto Cupecoy Penthouse Leo',
    'rainbow-beach-club-oceanview-condo': 'CUPECOY/RBC 307',
    'red-pond-villa': 'Red Pond 4 bedrooms villa ',
    'sapphire-beach-club-penthouse-2': 'JUST LISTED/SAPPHIRE BEACH CLUB FRIDA',
    'sapphire-penthouse': 'CUPECOY/Sapphire Penthouse 2 Thérèse',
    'solea-residence-2': 'BELAIR - LITTLE BAY/Little Bay SOLEA 2 bed',
    'st-john-villa': 'SOLD/St John House 4bed',
    'stand-alone-house-in-saunders': 'SAUNDERS/Saunders 4.5 bed house',
    'stand-alone-house-with-3-apartments': 'POINT PIROUETTE/Villa Point Pirouette 6 bedrooms- 3 apartments',
    'stunning-beachfront-3-bedroom-condo': 'CUPECOY/CBC 214 1.1M',
    'the-hills-residence-1-bedroom-condo': 'SIMPSON BAY/The Hills 1 BR Edited wit logo',
    'top-floor-porto-cupecoy-condo': 'CUPECOY/Top-floor-porto-cupecoy-condo',
    'vielven-dawn-suite': 'NEW DEVELOPMENTS/Vie L_Ven - Indigo Bay',
    'vielven-pinel-suite': 'NEW DEVELOPMENTS/Vie L_Ven - Indigo Bay',
    'vielven-rouge-suite': 'NEW DEVELOPMENTS/Vie L_Ven - Indigo Bay',
    'villa-de-luxe-a-vendre-tamarind-hill-moderne-piscine-vue-mer': 'OYSTER POND - DAWN BEACH/Villa Do - Tamarind Hill',
    'villa-frangipani-2': 'PELICAN KEY/Villa Frangipani Pelican',
    'villa-lotus': 'GRAND CASE/LOTUS Grand Case',
    'villa-oceane': 'PELICAN KEY/Villa Oceane',
    'villa-shiaou': 'CUPECOY/Villa SHIAOU 6 bedrooms ',
    'villa-sophia-2': 'ALMOND GROVE/Villa Sophia Almond Grove',
    'villa-twin-palms': 'SOLD/Villa Twin Palms',
    'villa-vijoux': 'OYSTER POND - DAWN BEACH/Villa Vijoux 8-bedroom',
    'villa-with-3-apartments-and-boat-slip-2': 'SIMPSON BAY/3-bed SBYC condo with boat slip',
    'windgate-luxury-condo': 'POINT BLANCHE/Windgate 3,5-bedroom',
    'yacht-club-1-bedroom-with-boat-slip': 'SIMPSON BAY/Simpson Bay Yacht Club - Studio-1-bedroom',
}

# Keywords to identify best image sources (priority order)
PREFER_KEYWORDS = ['edited no logo', 'without logo', 'no logo', 'sans logo']
GOOD_KEYWORDS = ['edited', 'compressed']
AVOID_KEYWORDS = ['logo', 'with logo', 'logo compressed', 'compressed logo']

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tiff'}


def is_image_file(filename):
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS


def score_folder(folder_name):
    """Score a subfolder name. Higher = better (prefer edited without logo)."""
    name_lower = folder_name.lower()

    # Best: edited without logo
    for kw in PREFER_KEYWORDS:
        if kw in name_lower:
            return 100

    # Avoid: folders with "logo" in name (has watermark)
    for kw in AVOID_KEYWORDS:
        if kw in name_lower and 'no logo' not in name_lower and 'without logo' not in name_lower:
            return -50

    # Good: edited versions
    for kw in GOOD_KEYWORDS:
        if kw in name_lower:
            return 50

    # Neutral: raw/original
    return 0


def find_best_images(dl_path):
    """Find the best images in a download folder, preferring edited/no-logo versions."""
    if not os.path.isdir(dl_path):
        return []

    # Collect all subfolders with their scores
    candidates = []

    # Check subfolders recursively (max 3 levels)
    for root, dirs, files in os.walk(dl_path):
        depth = root.replace(dl_path, '').count(os.sep)
        if depth > 3:
            continue

        # Get image files in this directory
        images = [os.path.join(root, f) for f in sorted(files) if is_image_file(f)]
        if images:
            # Score based on path
            rel_path = os.path.relpath(root, dl_path)
            score = score_folder(rel_path)
            candidates.append((score, rel_path, images))

    if not candidates:
        return []

    # Sort by score (highest first), then by number of images (more is better)
    candidates.sort(key=lambda x: (x[0], len(x[2])), reverse=True)

    best_score = candidates[0][0]

    # If best is "no logo" or "edited", use those
    if best_score >= 50:
        # Use images from the best-scored folder(s)
        best_images = []
        for score, path, images in candidates:
            if score >= 50:
                best_images.extend(images)
        return best_images[:MAX_IMAGES]

    # Otherwise, collect from root level first, then subfolders, avoiding "logo" ones
    best_images = []
    for score, path, images in candidates:
        if score >= 0:  # Skip logo folders
            best_images.extend(images)

    if not best_images:
        # Fallback: use whatever we have
        for score, path, images in candidates:
            best_images.extend(images)

    return best_images[:MAX_IMAGES]


def process_image(src_path, dst_path):
    """Resize and compress an image for web use."""
    try:
        img = Image.open(src_path)

        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'P', 'LA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Auto-orient based on EXIF
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)

        # Resize if larger than max dimensions
        w, h = img.size
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            ratio = min(MAX_WIDTH / w, MAX_HEIGHT / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # Save as optimized JPEG
        img.save(dst_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        return True
    except Exception as e:
        print(f"  ERREUR processing {src_path}: {e}")
        return False


def main():
    # Load data.json
    with open(DATA_JSON, 'r') as f:
        data = json.load(f)

    # Get unique FR slugs
    fr_slugs = set()
    for p in data['properties']:
        if p.get('language') == 'fr':
            fr_slugs.add(p['slug'])

    stats = {'updated': 0, 'skipped': 0, 'errors': 0, 'total_images': 0}

    for slug in sorted(fr_slugs):
        dl_rel_path = MAPPING.get(slug)

        if dl_rel_path is None:
            print(f"SKIP {slug} (pas de dossier download)")
            stats['skipped'] += 1
            continue

        dl_full_path = os.path.join(DL_BASE, dl_rel_path)

        if not os.path.isdir(dl_full_path):
            print(f"SKIP {slug} (dossier introuvable: {dl_rel_path})")
            stats['skipped'] += 1
            continue

        # Find best images
        source_images = find_best_images(dl_full_path)

        if not source_images:
            print(f"SKIP {slug} (aucune image trouvée dans {dl_rel_path})")
            stats['skipped'] += 1
            continue

        # Filter out very small images (< 10KB probably thumbnails)
        source_images = [img for img in source_images if os.path.getsize(img) > 10000]

        if not source_images:
            print(f"SKIP {slug} (images trop petites dans {dl_rel_path})")
            stats['skipped'] += 1
            continue

        # Sort images by filename for consistent ordering
        source_images.sort(key=lambda x: os.path.basename(x).lower())

        # Limit to MAX_IMAGES
        source_images = source_images[:MAX_IMAGES]

        # Prepare destination directory
        dst_dir = os.path.join(SITE_DIR, slug)

        # Backup existing images (just clear them)
        if os.path.isdir(dst_dir):
            for f in os.listdir(dst_dir):
                os.remove(os.path.join(dst_dir, f))
        else:
            os.makedirs(dst_dir, exist_ok=True)

        # Process and copy images
        processed = 0
        gallery_paths = []

        for i, src_img in enumerate(source_images, 1):
            dst_file = os.path.join(dst_dir, f"{i:02d}.jpg")

            if process_image(src_img, dst_file):
                processed += 1
                rel_path = f"images/properties/{slug}/{i:02d}.jpg"
                gallery_paths.append(rel_path)

        if processed > 0:
            # Update data.json entries for all languages
            gallery_str = ','.join(gallery_paths)
            for p in data['properties']:
                if p['slug'] == slug:
                    p['gallery_images'] = gallery_str

            print(f"OK    {slug}: {processed} images ({os.path.basename(dl_rel_path)})")
            stats['updated'] += 1
            stats['total_images'] += processed
        else:
            print(f"ERROR {slug}: aucune image traitée")
            stats['errors'] += 1

    # Save updated data.json
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"RÉSUMÉ:")
    print(f"  Mis à jour:    {stats['updated']} biens")
    print(f"  Images totales: {stats['total_images']}")
    print(f"  Ignorés:       {stats['skipped']} biens")
    print(f"  Erreurs:       {stats['errors']} biens")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

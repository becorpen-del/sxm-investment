#!/usr/bin/env python3
"""
Script v2 - Mise à jour des images avec filtrage STRICT des logos/watermarks.
Priorité: "no logo" > "edited" (sans logo dans nom) > "raw/pics" > root
JAMAIS de dossier contenant "logo" dans le nom (sauf "no logo"/"without logo").
"""

import os
import json
from PIL import Image, ImageOps

SITE_DIR = '/Users/benjaminlegal/Documents/SXM-Invest/images/properties'
DL_BASE = '/Users/benjaminlegal/Downloads/LISTINGS FOR SALE/LISTINGS FOR SALE'
DATA_JSON = '/Users/benjaminlegal/Documents/SXM-Invest/data.json'

MAX_WIDTH = 1920
MAX_HEIGHT = 1280
JPEG_QUALITY = 85
MAX_IMAGES = 30

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tiff'}

# Explicit best-folder overrides for tricky properties
# These are manually verified clean folders
FOLDER_OVERRIDES = {
    # slug: list of relative subfolder paths to use (in order of priority)
    'palm-beach-1-bedroom-condo': ['Edited No logo '],
    'red-pond-villa': ['WITHOUT LOGO'],
    'villa-sophia-2': ['Villa Sophia New/No logo'],
    'cupecoy-beachfront-3-bedroom-condo': ['SM Cupecoy beach club #220 condo', 'Pictures CBC #220'],
    'exceptional-4-bedroom-penthouse': ['New Pics C18'],
    '3-bedroom-at-blue-marine-residences-2': ['B17 Edited'],
    'aquamarina-villa-2': ['Edited Aquamarina Villa'],
    'beachfront-condo-at-sapphire-resort': ['Enhance'],
    'brand-new-villa-lagoon-2': ['Edited'],
    'concord-2-bedroom-condo': ['Compressed Pics CONCORD', 'Renders'],
    'concord-penthouse': ['Compressed Pics CONCORD', 'Renders'],
    'large-condo-with-yard': ['Newly edited CBC 202 2BR 825K'],
    'le-papillon-penthouse': ['.'],  # root has 40 images (the Logo subfolder is separate)
    'modern-beachfront-condo-2': ['Edited'],
    'multi-unit-residential-building-direct-beach-access': ['iloveimg-compressed'],
    'oceanfront-living-3-bedroom-in-cupecoy': ['.'],  # root has 22 images
    'pelican-cove-villa': ['Staged'],
    'penthouse-aquamarina-4-chambres': ['.'],  # root - "Edited with logo" is the folder name itself
    'penthouse-condo-in-maho': ['Edited'],
    'porto-cupecoy-penthouse': ['Edited Pics', 'Edited Pics/Twilight'],
    'solea-residence-2': ['Edited', 'Edited/Twilight'],
    'stand-alone-house-with-3-apartments': ['Edited'],
    'stunning-beachfront-3-bedroom-condo': ['Pics'],
    'villa-oceane': ['New edited Villa oceane'],
    'villa-with-3-apartments-and-boat-slip-2': ['SBYC'],
    'windgate-luxury-condo': ['Windgate Pics Enhance ', 'Windgate Pics Enhance /Day to dusk'],
    'yacht-club-1-bedroom-with-boat-slip': ['.'],  # root has 14 images
    'la-lagune-top-floor': ['Edited'],
    'sapphire-penthouse': ['Edited', 'Edited/Twilight'],
    'condo-in-maho-beach': ['.'],  # root has 16 images
    'large-terrace-blue-marine-condo': ['.'],  # root has 12 images
    'guana-bay-penthouse': ['.'],  # root
    'great-bay-villas': ['.'],  # root
    'st-john-villa': ['.'],  # root
    'maho-beach-1-bedroom': ['.'],  # root
    'beachfront-cupecoy-condo': ['.'],  # root
    'top-floor-porto-cupecoy-condo': ['.'],  # root
    'rainbow-beach-club-oceanview-condo': ['Edited and compressed'],
    'large-studio-with-separated-bedroom': ['.'],  # root
    'villa-lotus': ['Pics large', '.'],
    'villa-shiaou': ['.'],  # root
    'beachfront-coco-beach-condo': ['.'],  # check root
    'villa-twin-palms': ['.'],  # root
    'villa-vijoux': ['Pictures Villa Vijoux', '.'],
    'villa-frangipani-2': ['Pictures Villa Frangipani', '.'],
    'apartment-building-le-diamand-blanc-2': ['Jpeg', 'Drone pics HDR'],
    'sapphire-beach-club-penthouse-2': ['.'],
    'the-hills-residence-1-bedroom-condo': ['.'],
    'villa-de-luxe-a-vendre-tamarind-hill-moderne-piscine-vue-mer': ['.'],
    '3-bedroom-aqua-villa-new': ['Aqua Villas Edited'],
    '4-bedroom-aqua-villa-with-boat-slip': ['Aqua Villas Edited'],
    'stand-alone-house-in-saunders': ['.'],  # root - Saunders 4.5 bed house
    'vielven-dawn-suite': ['Suite Renderings/Executive Suites', 'Exterior Renderings', 'Amenities'],
    'vielven-pinel-suite': ['Suite Renderings/Junior Suites', 'Exterior Renderings', 'Amenities'],
    'vielven-rouge-suite': ['Suite Renderings/Executive Suites', 'Exterior Renderings', 'Amenities'],
}

MAPPING = {
    '2-bedroom-with-dual-rental-potential': None,
    '3-bedroom-aqua-villa-new': 'CUPECOY/AQUA VILLAS',
    '3-bedroom-at-blue-marine-residences-2': 'MAHO/Blue Marine B17 3-bedroom',
    '3-bedroom-blue-marine-penthouse': None,
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
    'multifamily-home-rental-income-cole-bay': None,
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


def is_image_file(filename):
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS


def has_logo_in_path(path):
    """Check if path contains logo-related keywords (bad)."""
    p = path.lower()
    if 'no logo' in p or 'without logo' in p or 'sans logo' in p:
        return False  # These are CLEAN
    return 'logo' in p


def find_images_in_folder(folder_path):
    """Get all image files in a single folder (non-recursive)."""
    if not os.path.isdir(folder_path):
        return []
    images = []
    for f in sorted(os.listdir(folder_path)):
        if is_image_file(f):
            full = os.path.join(folder_path, f)
            # Skip tiny files (thumbnails)
            if os.path.getsize(full) > 15000:
                images.append(full)
    return images


def find_best_images(slug, dl_path):
    """Find the best images using explicit overrides."""
    if slug in FOLDER_OVERRIDES:
        overrides = FOLDER_OVERRIDES[slug]
        images = []
        for sub in overrides:
            if sub == '.':
                folder = dl_path
            else:
                folder = os.path.join(dl_path, sub)
            imgs = find_images_in_folder(folder)
            images.extend(imgs)
            if len(images) >= MAX_IMAGES:
                break
        return images[:MAX_IMAGES]

    # Fallback: auto-detect (avoid anything with "logo" in path)
    images = []
    for root, dirs, files in os.walk(dl_path):
        rel = os.path.relpath(root, dl_path)
        if has_logo_in_path(rel):
            continue
        depth = root.replace(dl_path, '').count(os.sep)
        if depth > 2:
            continue
        for f in sorted(files):
            if is_image_file(f) and os.path.getsize(os.path.join(root, f)) > 15000:
                images.append(os.path.join(root, f))
    return images[:MAX_IMAGES]


def process_image(src_path, dst_path):
    """Resize and compress an image for web use."""
    try:
        img = Image.open(src_path)

        if img.mode in ('RGBA', 'P', 'LA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if 'A' in img.mode:
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        img = ImageOps.exif_transpose(img)

        w, h = img.size
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            ratio = min(MAX_WIDTH / w, MAX_HEIGHT / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        img.save(dst_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        return True
    except Exception as e:
        print(f"  ERREUR: {e} ({src_path})")
        return False


def main():
    with open(DATA_JSON, 'r') as f:
        data = json.load(f)

    fr_slugs = set()
    for p in data['properties']:
        if p.get('language') == 'fr':
            fr_slugs.add(p['slug'])

    stats = {'updated': 0, 'skipped': 0, 'errors': 0, 'total_images': 0}

    for slug in sorted(fr_slugs):
        dl_rel_path = MAPPING.get(slug)

        if dl_rel_path is None:
            print(f"SKIP  {slug} (pas de source)")
            stats['skipped'] += 1
            continue

        dl_full_path = os.path.join(DL_BASE, dl_rel_path)
        if not os.path.isdir(dl_full_path):
            print(f"SKIP  {slug} (dossier introuvable)")
            stats['skipped'] += 1
            continue

        source_images = find_best_images(slug, dl_full_path)

        if not source_images:
            print(f"SKIP  {slug} (aucune image propre)")
            stats['skipped'] += 1
            continue

        # Prepare destination
        dst_dir = os.path.join(SITE_DIR, slug)
        if os.path.isdir(dst_dir):
            for f in os.listdir(dst_dir):
                fp = os.path.join(dst_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
        else:
            os.makedirs(dst_dir, exist_ok=True)

        processed = 0
        gallery_paths = []

        for i, src_img in enumerate(source_images, 1):
            dst_file = os.path.join(dst_dir, f"{i:02d}.jpg")
            if process_image(src_img, dst_file):
                processed += 1
                gallery_paths.append(f"images/properties/{slug}/{i:02d}.jpg")

        if processed > 0:
            gallery_str = ','.join(gallery_paths)
            for p in data['properties']:
                if p['slug'] == slug:
                    p['gallery_images'] = gallery_str

            # Show which source folder was used
            if slug in FOLDER_OVERRIDES:
                src_info = ' + '.join(FOLDER_OVERRIDES[slug])
            else:
                src_info = 'auto'
            print(f"OK    {slug}: {processed} imgs ← [{src_info}]")
            stats['updated'] += 1
            stats['total_images'] += processed
        else:
            print(f"ERROR {slug}")
            stats['errors'] += 1

    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"RÉSUMÉ v2 (filtrage strict):")
    print(f"  Mis à jour:     {stats['updated']} biens")
    print(f"  Images totales: {stats['total_images']}")
    print(f"  Ignorés:        {stats['skipped']} biens")
    print(f"  Erreurs:        {stats['errors']} biens")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

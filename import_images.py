#!/usr/bin/env python3
"""
Import images from Drive folders into the project.
Maps Drive photo folders to data.json property slugs,
selects the best images, copies/resizes them, and updates data.json.
"""

import json
import os
import shutil
from pathlib import Path
from PIL import Image

# Source folder with Drive photos
DRIVE_ROOT = os.path.expanduser("~/Desktop/SXM-Investments")

# Output folder for processed images
OUTPUT_ROOT = "images/properties"

# Max width for web images
MAX_WIDTH = 1920
MAX_IMAGES = 30  # Max images per property

# Mapping: Drive folder path (relative to DRIVE_ROOT) → base slug in data.json
# The base slug is used to find all language variants (slug, slug-2, slug-en, slug-nl, etc.)
FOLDER_TO_SLUG = {
    "ALMOND GROVE/Villa Sophia Almond Grove": "villa-sophia",
    "BELAIR - LITTLE BAY/Little Bay SOLEA 2 bed": "solea-residence",
    "GRAND CASE/LOTUS Grand Case": "villa-lotus",
    "GUANA BAY/Guana Bay Penthouse": "guana-bay-penthouse",
    "INDIGO BAY/Ellie Saab Villas": "vielven-dawn-suite",
    "NETTLE BAY/La Lagune 425 3-bedroom ": "la-lagune-top-floor",
    "OYSTER POND - DAWN BEACH/Oyster Pond Building Diamand Blanc": "apartment-building-le-diamand-blanc",
    "OYSTER POND - DAWN BEACH/Villa Do - Tamarind Hill": "villa-do",
    "OYSTER POND - DAWN BEACH/Villa Vijoux 8-bedroom": "villa-vijoux",
    "PELICAN KEY/Villa Frangipani Pelican": "villa-frangipani",
    "PELICAN KEY/Villa Oceane": "villa-oceane",
    "PELICAN KEY/Cae Jae Haven 2BR": "2-bedroom-with-dual-rental-potential",
    "PHILIPSBURG/Great Bay Villa": "great-bay-villas",
}

# Subfolders to prioritize (best quality first)
PRIORITY_FOLDERS = ["Edited with Logo", "Edited", "logo", "LOGO", "New edited", "New", "HDR", "Pics", "Pictures", "Jpeg"]

# Subfolders to ignore
IGNORE_FOLDERS = {"Floorplans", "Social Media", "compressjpeg", "compresspng", "FrontLine Villas Floorplan", "Highline Villas Floorplan"}

# Image extensions
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}


def find_all_slugs(data, base_slug):
    """Find all slug variants for a property across languages.
    Properties share images via the same base slug pattern:
    e.g. villa-sophia, villa-sophia-2, villa-sophia-en, villa-sophia-nl
    Also handles special cases like villa-do with different slug patterns.
    """
    # Special mappings for properties with very different slugs per language
    SPECIAL_SLUG_GROUPS = {
        "villa-do": [
            "villa-do",
            "en-tamarind-hill-luxury-villa-for-sale-modern-pool-home-ocean-view",
            "villa-de-luxe-a-vendre-tamarind-hill-moderne-piscine-vue-mer",
        ],
        "villa-frangipani": [
            "villa-frangipani-2",
            "villa-frangipani-en-9",
            "villa-frangipani-nl-9",
        ],
    }

    if base_slug in SPECIAL_SLUG_GROUPS:
        return SPECIAL_SLUG_GROUPS[base_slug]

    # Find all slugs that start with the base slug
    all_slugs = set()
    for prop in data["properties"]:
        slug = prop.get("slug", "")
        if slug == base_slug or slug.startswith(base_slug + "-"):
            all_slugs.add(slug)
    return list(all_slugs)


def collect_images(folder_path):
    """Collect image files from a property folder, prioritizing edited versions."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"  WARNING: Folder not found: {folder}")
        return []

    # Collect from priority subfolders first
    images_by_priority = []

    # Check priority subfolders
    for prio_name in PRIORITY_FOLDERS:
        for sub in folder.rglob("*"):
            if sub.is_dir() and prio_name.lower() in sub.name.lower():
                # Skip ignored folders
                if any(ign.lower() in sub.name.lower() for ign in IGNORE_FOLDERS):
                    continue
                imgs = []
                for f in sub.iterdir():
                    if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
                        imgs.append(f)
                if imgs:
                    # Sort by file size descending (larger = better quality)
                    imgs.sort(key=lambda x: x.stat().st_size, reverse=True)
                    images_by_priority.extend(imgs)

    # Also collect images from the root folder
    root_images = []
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            root_images.append(f)
    root_images.sort(key=lambda x: x.stat().st_size, reverse=True)

    # Also collect from any subfolder not already covered and not ignored
    other_images = []
    for sub in folder.iterdir():
        if sub.is_dir():
            if any(ign.lower() in sub.name.lower() for ign in IGNORE_FOLDERS):
                continue
            # Check if already in priority list
            already_covered = any(
                prio.lower() in sub.name.lower() for prio in PRIORITY_FOLDERS
            )
            if not already_covered:
                for f in sub.rglob("*"):
                    if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
                        other_images.append(f)
    other_images.sort(key=lambda x: x.stat().st_size, reverse=True)

    # Combine: priority first, then root, then other
    all_images = images_by_priority + root_images + other_images

    # Deduplicate by filename (keep first occurrence = higher priority)
    seen_names = set()
    unique_images = []
    for img in all_images:
        name = img.name.lower()
        if name not in seen_names:
            seen_names.add(name)
            unique_images.append(img)

    return unique_images[:MAX_IMAGES]


def process_image(src_path, dst_path):
    """Copy and resize image to max width."""
    try:
        with Image.open(src_path) as img:
            # Convert RGBA to RGB for JPEG output
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize if wider than MAX_WIDTH
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                new_size = (MAX_WIDTH, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Save as JPEG with good quality
            img.save(dst_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"  ERROR processing {src_path}: {e}")
        return False


def main():
    # Load data.json
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # Build a lookup: slug → property indices
    slug_to_indices = {}
    for i, prop in enumerate(data["properties"]):
        slug = prop.get("slug", "")
        if slug:
            slug_to_indices.setdefault(slug, []).append(i)

    total_imported = 0

    for drive_folder, base_slug in FOLDER_TO_SLUG.items():
        src_folder = os.path.join(DRIVE_ROOT, drive_folder)
        print(f"\n--- {drive_folder} → {base_slug} ---")

        # Collect images
        images = collect_images(src_folder)
        if not images:
            print(f"  No images found, skipping.")
            continue

        print(f"  Found {len(images)} images")

        # Create output directory
        out_dir = os.path.join(OUTPUT_ROOT, base_slug)
        os.makedirs(out_dir, exist_ok=True)

        # Process and copy images
        gallery_paths = []
        for idx, img_path in enumerate(images, 1):
            dst_name = f"{idx:02d}.jpg"
            dst_path = os.path.join(out_dir, dst_name)
            if process_image(img_path, dst_path):
                # Store path relative to site root
                rel_path = f"images/properties/{base_slug}/{dst_name}"
                gallery_paths.append(rel_path)
                print(f"  {dst_name} ← {img_path.name}")

        if not gallery_paths:
            print(f"  No images processed successfully.")
            continue

        total_imported += len(gallery_paths)

        # Find all slug variants for this property
        all_slugs = find_all_slugs(data, base_slug)
        print(f"  Updating slugs: {all_slugs}")

        # Update data.json for all matching properties
        gallery_str = ",".join(gallery_paths)
        featured = gallery_paths[0]

        for slug in all_slugs:
            if slug in slug_to_indices:
                for i in slug_to_indices[slug]:
                    data["properties"][i]["gallery_images"] = gallery_str
                    data["properties"][i]["featured_image"] = featured

    # Save updated data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n=== Done! Imported {total_imported} images for {len(FOLDER_TO_SLUG)} properties ===")


if __name__ == "__main__":
    main()

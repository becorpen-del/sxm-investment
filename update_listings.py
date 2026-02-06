#!/usr/bin/env python3
import json
import re
from html import escape

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def get_image(prop):
    """Get best image for property. Prefers local gallery images, then featured_image, then fallback."""
    if prop.get('gallery_images'):
        imgs = prop['gallery_images'].split(',')
        if imgs and imgs[0].strip(): return imgs[0].strip()
    if prop.get('featured_image'):
        return prop['featured_image']
    pt = (prop.get('type', '') or prop.get('property_type', '')).lower()
    if 'villa' in pt: return 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    if 'penthouse' in pt: return 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    if 'condo' in pt: return 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    return 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'

def get_price_num(price):
    nums = re.findall(r'[\d,]+', price.replace(',', ''))
    return int(nums[0].replace(',', '')) if nums else 0

def get_location_slug(prop):
    for cat in prop.get('categories', []):
        if cat.get('domain') == 'project-location':
            return cat.get('nicename', '').lower()
    loc = prop.get('location', '').lower()
    if 'maho' in loc: return 'maho'
    if 'cupecoy' in loc: return 'cupecoy'
    if 'simpson' in loc: return 'simpson-bay'
    if 'pelican' in loc: return 'pelican-key'
    if 'pirouette' in loc: return 'point-pirouette'
    if 'cole' in loc: return 'cole-bay'
    if 'orient' in loc: return 'orient-bay'
    if 'dawn' in loc: return 'dawn-beach'
    if 'oyster' in loc: return 'oyster-pond'
    if 'philipsburg' in loc: return 'philipsburg'
    return 'other'

def get_type_slug(prop):
    pt = (prop.get('type', '') or prop.get('property_type', '')).lower()
    if 'villa' in pt: return 'villa'
    if 'penthouse' in pt: return 'penthouse'
    if 'condo' in pt: return 'condo'
    if 'appart' in pt: return 'appartement'
    return 'other'

def generate_listing_page(lang, props):
    TRANS = {
        'fr': {
            'title': 'Nos Propriétés', 'subtitle': 'Notre Portfolio', 'desc': 'Découvrez notre sélection exclusive de biens immobiliers de luxe à Saint-Martin',
            'all_types': 'Tous les types', 'villas': 'Villas', 'penthouses': 'Penthouses', 'condos': 'Condos', 'apartments': 'Appartements',
            'all_locations': 'Toutes les localisations', 'all_budgets': 'Tous les budgets', 'type': 'Type', 'location': 'Localisation', 'budget': 'Budget',
            'count_text': 'propriétés disponibles', 'beds': 'ch.', 'baths': 'sdb.',
            'nav_home': 'index.html', 'nav_props': 'proprietes.html', 'nav_loc': 'saint-martin.html', 'nav_contact': 'contact.html',
            'home': 'Accueil', 'properties': 'Propriétés', 'saint_martin': 'Saint-Martin', 'contact': 'Contact', 'contact_us': 'Nous contacter',
            'footer_text': 'Votre partenaire de confiance pour l\'investissement immobilier à Saint-Martin depuis plus de 15 ans.',
            'all_rights': 'Tous droits réservés.', 'location_name': 'Saint-Martin',
            'prop_dir': 'biens'
        },
        'en': {
            'title': 'Our Properties', 'subtitle': 'Our Portfolio', 'desc': 'Discover our exclusive selection of luxury real estate in St. Martin',
            'all_types': 'All types', 'villas': 'Villas', 'penthouses': 'Penthouses', 'condos': 'Condos', 'apartments': 'Apartments',
            'all_locations': 'All locations', 'all_budgets': 'All budgets', 'type': 'Type', 'location': 'Location', 'budget': 'Budget',
            'count_text': 'properties available', 'beds': 'bd', 'baths': 'ba',
            'nav_home': 'index.html', 'nav_props': 'properties.html', 'nav_loc': 'st-martin.html', 'nav_contact': 'contact.html',
            'home': 'Home', 'properties': 'Properties', 'saint_martin': 'St. Martin', 'contact': 'Contact', 'contact_us': 'Contact Us',
            'footer_text': 'Your trusted partner for real estate investment in St. Martin for over 15 years.',
            'all_rights': 'All rights reserved.', 'location_name': 'St. Martin',
            'prop_dir': 'properties-list'
        },
        'nl': {
            'title': 'Ons Vastgoed', 'subtitle': 'Ons Portfolio', 'desc': 'Ontdek onze exclusieve selectie van luxe vastgoed in Sint Maarten',
            'all_types': 'Alle types', 'villas': "Villa's", 'penthouses': 'Penthouses', 'condos': "Condo's", 'apartments': 'Appartementen',
            'all_locations': 'Alle locaties', 'all_budgets': 'Alle budgetten', 'type': 'Type', 'location': 'Locatie', 'budget': 'Budget',
            'count_text': 'woningen beschikbaar', 'beds': 'slpk', 'baths': 'badk',
            'nav_home': 'index.html', 'nav_props': 'eigenschappen.html', 'nav_loc': 'sint-maarten.html', 'nav_contact': 'contact.html',
            'home': 'Home', 'properties': 'Vastgoed', 'saint_martin': 'Sint Maarten', 'contact': 'Contact', 'contact_us': 'Neem Contact Op',
            'footer_text': 'Uw vertrouwde partner voor vastgoedinvesteringen in Sint Maarten sinds meer dan 15 jaar.',
            'all_rights': 'Alle rechten voorbehouden.', 'location_name': 'Sint Maarten',
            'prop_dir': 'vastgoed'
        }
    }
    t = TRANS[lang]
    
    # Build properties JS array
    props_js = []
    for p in props:
        slug = p.get('slug', slugify(p.get('title', '')))
        if lang == 'fr':
            link = f"biens/{slug}.html"
        else:
            link = f"{t['prop_dir']}/{slug}.html"
        # Adjust local image paths relative to listing page location
        listing_image = get_image(p)
        if listing_image.startswith('images/'):
            listing_image = listing_image if lang == 'fr' else '../' + listing_image
        props_js.append({
            'title': p.get('title', ''),
            'price': p.get('price', ''),
            'priceNum': get_price_num(p.get('price', '')),
            'type': get_type_slug(p),
            'location': p.get('location', ''),
            'locationSlug': get_location_slug(p),
            'beds': p.get('rooms', '-'),
            'baths': p.get('baths', '-'),
            'sqft': p.get('sqft', '-'),
            'image': listing_image,
            'link': link
        })
    
    props_json = json.dumps(props_js, ensure_ascii=False)
    
    if lang == 'fr':
        base_path = ''
        img_path = 'images/logos/'
        css_path = 'css/style.css'
        js_path = 'js/main.js'
    else:
        base_path = '../'
        img_path = '../images/logos/'
        css_path = '../css/style.css'
        js_path = '../js/main.js'

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']} | SXM Dream Investments</title>
    <meta name="description" content="{t['desc']}">
    <link rel="icon" type="image/png" href="{img_path}favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{css_path}">
    <style>
        .page-hero {{ height: 50vh; min-height: 400px; background: linear-gradient(rgba(26, 42, 58, 0.7), rgba(26, 42, 58, 0.7)), url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=2071&q=80') center/cover; display: flex; align-items: center; justify-content: center; text-align: center; color: white; }}
        .page-hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .page-hero p {{ font-size: 1.2rem; opacity: 0.9; max-width: 600px; }}
        .properties-section {{ padding: 4rem 5%; }}
        .filters-bar {{ background: var(--off-white); padding: 2rem 5%; display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; align-items: center; }}
        .filter-group {{ display: flex; align-items: center; gap: 0.5rem; }}
        .filter-group label {{ font-weight: 500; color: var(--navy); }}
        .filter-select {{ padding: 0.75rem 1.5rem; border: 1px solid var(--gray-light); border-radius: 6px; font-family: 'Montserrat', sans-serif; min-width: 200px; background: white; }}
        .properties-count {{ text-align: center; padding: 1rem; color: var(--gray); font-size: 0.95rem; }}
        .properties-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; max-width: 1400px; margin: 0 auto; }}
        .property-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s; text-decoration: none; color: inherit; display: block; }}
        .property-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.15); }}
        .property-image {{ height: 220px; background-size: cover; background-position: center; position: relative; }}
        .property-badge {{ position: absolute; top: 1rem; left: 1rem; background: var(--gold); color: var(--navy); padding: 0.4rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }}
        .property-price {{ position: absolute; bottom: 1rem; right: 1rem; background: var(--navy); color: white; padding: 0.5rem 1rem; border-radius: 4px; font-weight: 600; }}
        .property-content {{ padding: 1.5rem; }}
        .property-content h3 {{ font-family: 'Playfair Display', serif; font-size: 1.2rem; color: var(--navy); margin-bottom: 0.5rem; }}
        .property-location {{ color: var(--gray); font-size: 0.9rem; margin-bottom: 1rem; }}
        .property-location i {{ color: var(--gold); margin-right: 0.3rem; }}
        .property-features {{ display: flex; gap: 1rem; }}
        .property-feature {{ display: flex; align-items: center; gap: 0.3rem; color: var(--gray); font-size: 0.85rem; }}
        .property-feature i {{ color: var(--gold); }}
        @media (max-width: 1024px) {{ .properties-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 768px) {{ .properties-grid {{ grid-template-columns: 1fr; }} .filters-bar {{ flex-direction: column; }} }}
    </style>
</head>
<body>
    <nav class="navbar" id="navbar">
        <a href="{base_path}{t['nav_home']}" class="logo">
            <img src="{img_path}logo-white.png" alt="SXM Dream Investments" class="logo-white">
            <img src="{img_path}logo-black.png" alt="SXM Dream Investments" class="logo-black" style="display:none;">
        </a>
        <ul class="nav-links">
            <li><a href="{base_path}{t['nav_home']}">{t['home']}</a></li>
            <li><a href="{t['nav_props']}">{t['properties']}</a></li>
            <li><a href="{t['nav_loc']}">{t['saint_martin']}</a></li>
            <li><a href="{t['nav_contact']}">{t['contact']}</a></li>
            <li><a href="{t['nav_contact']}" class="nav-cta">{t['contact_us']}</a></li>
            <li class="lang-switcher">
                <a href="{base_path}proprietes.html" {'class="active"' if lang=='fr' else ''}>FR</a>
                <a href="{base_path}en/properties.html" {'class="active"' if lang=='en' else ''}>EN</a>
                <a href="{base_path}nl/eigenschappen.html" {'class="active"' if lang=='nl' else ''}>NL</a>
            </li>
        </ul>
        <button class="mobile-menu-btn"><i class="fas fa-bars"></i></button>
    </nav>

    <section class="page-hero">
        <div>
            <span class="hero-badge">{t['subtitle']}</span>
            <h1>{t['title']}</h1>
            <p>{t['desc']}</p>
        </div>
    </section>

    <div class="filters-bar">
        <div class="filter-group">
            <label>{t['type']} :</label>
            <select class="filter-select" id="typeFilter" onchange="filterProperties()">
                <option value="all">{t['all_types']}</option>
                <option value="villa">{t['villas']}</option>
                <option value="penthouse">{t['penthouses']}</option>
                <option value="condo">{t['condos']}</option>
                <option value="appartement">{t['apartments']}</option>
            </select>
        </div>
        <div class="filter-group">
            <label>{t['location']} :</label>
            <select class="filter-select" id="locationFilter" onchange="filterProperties()">
                <option value="all">{t['all_locations']}</option>
                <option value="maho">Maho</option>
                <option value="cupecoy">Cupecoy</option>
                <option value="simpson-bay">Simpson Bay</option>
                <option value="pelican-key">Pelican Key</option>
                <option value="point-pirouette">Point Pirouette</option>
                <option value="cole-bay">Cole Bay</option>
                <option value="orient-bay">Orient Bay</option>
                <option value="dawn-beach">Dawn Beach</option>
                <option value="oyster-pond">Oyster Pond</option>
                <option value="philipsburg">Philipsburg</option>
            </select>
        </div>
        <div class="filter-group">
            <label>{t['budget']} :</label>
            <select class="filter-select" id="priceFilter" onchange="filterProperties()">
                <option value="all">{t['all_budgets']}</option>
                <option value="0-500000">0 - $500,000</option>
                <option value="500000-1000000">$500,000 - $1,000,000</option>
                <option value="1000000-2000000">$1,000,000 - $2,000,000</option>
                <option value="2000000+">+ $2,000,000</option>
            </select>
        </div>
    </div>

    <p class="properties-count"><span id="count">{len(props)}</span> {t['count_text']}</p>

    <section class="properties-section">
        <div class="properties-grid" id="propertiesGrid"></div>
    </section>

    <footer>
        <div class="footer-grid">
            <div class="footer-col">
                <img src="{img_path}logo-white.png" alt="SXM Dream Investments" style="max-width: 180px; margin-bottom: 1rem;">
                <p>{t['footer_text']}</p>
            </div>
            <div class="footer-col">
                <h4>Navigation</h4>
                <ul>
                    <li><a href="{base_path}{t['nav_home']}">{t['home']}</a></li>
                    <li><a href="{t['nav_props']}">{t['properties']}</a></li>
                    <li><a href="{t['nav_loc']}">{t['saint_martin']}</a></li>
                    <li><a href="{t['nav_contact']}">{t['contact']}</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Contact</h4>
                <p><i class="fas fa-map-marker-alt"></i> Simpson Bay, {t['location_name']}</p>
                <p><i class="fas fa-phone"></i> +1 721 XXX XXXX</p>
                <p><i class="fas fa-envelope"></i> info@sxmdreaminvestments.com</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 SXM Dream Investments. {t['all_rights']}</p>
        </div>
    </footer>

    <script src="{js_path}"></script>
    <script>
        const properties = {props_json};
        const BEDS = "{t['beds']}";
        const BATHS = "{t['baths']}";
        
        function renderProperties(props) {{
            const grid = document.getElementById('propertiesGrid');
            grid.innerHTML = props.map(p => `
                <a href="${{p.link}}" class="property-card">
                    <div class="property-image" style="background-image: url('${{p.image}}');">
                        <span class="property-badge">${{p.type.charAt(0).toUpperCase() + p.type.slice(1)}}</span>
                        <span class="property-price">${{p.price}}</span>
                    </div>
                    <div class="property-content">
                        <h3>${{p.title}}</h3>
                        <p class="property-location"><i class="fas fa-map-marker-alt"></i> ${{p.location}}</p>
                        <div class="property-features">
                            <span class="property-feature"><i class="fas fa-bed"></i> ${{p.beds}} ${{BEDS}}</span>
                            <span class="property-feature"><i class="fas fa-bath"></i> ${{p.baths}} ${{BATHS}}</span>
                            <span class="property-feature"><i class="fas fa-expand"></i> ${{p.sqft}}</span>
                        </div>
                    </div>
                </a>
            `).join('');
            document.getElementById('count').textContent = props.length;
        }}
        
        function filterProperties() {{
            const type = document.getElementById('typeFilter').value;
            const location = document.getElementById('locationFilter').value;
            const price = document.getElementById('priceFilter').value;
            
            let filtered = properties;
            if (type !== 'all') filtered = filtered.filter(p => p.type === type);
            if (location !== 'all') filtered = filtered.filter(p => p.locationSlug === location);
            if (price !== 'all') {{
                const [min, max] = price.split('-').map(v => v === '+' ? Infinity : parseInt(v.replace('+', '')));
                if (max) filtered = filtered.filter(p => p.priceNum >= min && p.priceNum <= max);
                else filtered = filtered.filter(p => p.priceNum >= min);
            }}
            renderProperties(filtered);
        }}
        
        // Apply filter from URL hash (e.g. #location=maho)
        const hash = window.location.hash.substring(1);
        if (hash) {{
            const params = new URLSearchParams(hash);
            const loc = params.get('location');
            if (loc) {{ document.getElementById('locationFilter').value = loc; }}
            const type = params.get('type');
            if (type) {{ document.getElementById('typeFilter').value = type; }}
            filterProperties();
        }} else {{
            renderProperties(properties);
        }}
    </script>
</body>
</html>'''

def main():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    props_by_lang = {'fr': [], 'en': [], 'nl': []}
    for p in data.get('properties', []):
        lang = p.get('language', 'en')
        if lang in props_by_lang:
            props_by_lang[lang].append(p)
    
    # Generate FR
    with open('proprietes.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing_page('fr', props_by_lang['fr']))
    print(f"Updated proprietes.html with {len(props_by_lang['fr'])} properties")
    
    # Generate EN
    with open('en/properties.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing_page('en', props_by_lang['en']))
    print(f"Updated en/properties.html with {len(props_by_lang['en'])} properties")
    
    # Generate NL
    with open('nl/eigenschappen.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing_page('nl', props_by_lang['nl']))
    print(f"Updated nl/eigenschappen.html with {len(props_by_lang['nl'])} properties")

if __name__ == '__main__':
    main()

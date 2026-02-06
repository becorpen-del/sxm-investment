#!/usr/bin/env python3
import json
import os
import re
from html import escape

OUTPUT_DIRS = {'fr': 'biens', 'en': 'en/properties-list', 'nl': 'nl/vastgoed'}

TRANSLATIONS = {
    'fr': {
        'back_to_list': 'Retour aux propriétés', 'bedrooms': 'Chambres', 'bathrooms': 'Salles de bain',
        'surface': 'Surface', 'year_built': 'Année de construction', 'property_type': 'Type de bien',
        'location': 'Localisation', 'price': 'Prix', 'description': 'Description',
        'features': 'Caractéristiques', 'amenities': 'Équipements', 'contact_agent': "Contacter l'agent",
        'view': 'Vue', 'cooling': 'Climatisation', 'flooring': 'Sol', 'parking': 'Parking', 'pool': 'Piscine',
        'home': 'Accueil', 'properties': 'Propriétés', 'saint_martin': 'Saint-Martin', 'contact': 'Contact',
        'contact_us': 'Nous contacter', 'sqft': 'sqft', 'interested': 'Intéressé par ce bien ?',
        'contact_text': 'Notre équipe est à votre disposition pour organiser une visite.',
        'nav_properties': 'proprietes.html', 'nav_location': 'saint-martin.html', 'nav_contact': 'contact.html',
        'footer_text': 'Votre partenaire de confiance pour investir à Saint-Martin.',
        'all_rights': 'Tous droits réservés.', 'location_name': 'Saint-Martin'
    },
    'en': {
        'back_to_list': 'Back to properties', 'bedrooms': 'Bedrooms', 'bathrooms': 'Bathrooms',
        'surface': 'Surface', 'year_built': 'Year built', 'property_type': 'Property type',
        'location': 'Location', 'price': 'Price', 'description': 'Description',
        'features': 'Features', 'amenities': 'Amenities', 'contact_agent': 'Contact agent',
        'view': 'View', 'cooling': 'Cooling', 'flooring': 'Flooring', 'parking': 'Parking', 'pool': 'Pool',
        'home': 'Home', 'properties': 'Properties', 'saint_martin': 'St. Martin', 'contact': 'Contact',
        'contact_us': 'Contact Us', 'sqft': 'sqft', 'interested': 'Interested in this property?',
        'contact_text': 'Our team is available to arrange a viewing or answer your questions.',
        'nav_properties': 'properties.html', 'nav_location': 'st-martin.html', 'nav_contact': 'contact.html',
        'footer_text': 'Your trusted partner for real estate investment in St. Martin.',
        'all_rights': 'All rights reserved.', 'location_name': 'St. Martin'
    },
    'nl': {
        'back_to_list': 'Terug naar vastgoed', 'bedrooms': 'Slaapkamers', 'bathrooms': 'Badkamers',
        'surface': 'Oppervlakte', 'year_built': 'Bouwjaar', 'property_type': 'Type woning',
        'location': 'Locatie', 'price': 'Prijs', 'description': 'Beschrijving',
        'features': 'Kenmerken', 'amenities': 'Voorzieningen', 'contact_agent': 'Contact agent',
        'view': 'Uitzicht', 'cooling': 'Airconditioning', 'flooring': 'Vloer', 'parking': 'Parkeren', 'pool': 'Zwembad',
        'home': 'Home', 'properties': 'Vastgoed', 'saint_martin': 'Sint Maarten', 'contact': 'Contact',
        'contact_us': 'Neem Contact Op', 'sqft': 'sqft', 'interested': 'Geïnteresseerd in deze woning?',
        'contact_text': 'Ons team staat klaar om een bezichtiging te regelen.',
        'nav_properties': 'eigenschappen.html', 'nav_location': 'sint-maarten.html', 'nav_contact': 'contact.html',
        'footer_text': 'Uw vertrouwde partner voor vastgoedinvesteringen in Sint Maarten.',
        'all_rights': 'Alle rechten voorbehouden.', 'location_name': 'Sint Maarten'
    }
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def clean_html(text):
    if not text: return ''
    text = re.sub(r'class="[^"]*"', '', text)
    text = re.sub(r'data-testid="[^"]*"', '', text)
    text = re.sub(r'id="comp-[^"]*"', '', text)
    text = re.sub(r'dir="ltr"', '', text)
    text = re.sub(r'role=""', '', text)
    text = re.sub(r'\s+>', '>', text)
    return text

def get_property_image(prop):
    if prop.get('gallery_images'):
        images = prop['gallery_images'].split(',')
        if images and images[0].strip(): return images[0].strip()
    pt = (prop.get('type', '') or prop.get('property_type', '')).lower()
    if 'villa' in pt: return 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
    if 'penthouse' in pt: return 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
    if 'condo' in pt: return 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
    return 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'

def generate_page(prop, lang):
    t = TRANSLATIONS[lang]
    title = prop.get('title', 'Property')
    price = prop.get('price', 'Contact us')
    location = prop.get('location', prop.get('neighborhood', ''))
    rooms = prop.get('rooms', '-')
    baths = prop.get('baths', '-')
    sqft = prop.get('sqft', '-')
    year = prop.get('year_built', '-')
    ptype = prop.get('type', '') or prop.get('property_type', '')
    content = clean_html(prop.get('content', ''))
    amenities = prop.get('amenities', '')
    view = prop.get('view', '-')
    cooling = prop.get('cooling', '-')
    flooring = prop.get('flooring', '-')
    parking = prop.get('parking', '-')
    pool = prop.get('pool', '-')
    agent = prop.get('agent', 'Sacha Mimouni')
    email = prop.get('email', 'sxm.dream.investments@gmail.com')
    phone = prop.get('phone', '+1 (721) 523 7855')
    image = get_property_image(prop)
    slug = prop.get('slug', slugify(title))
    
    amenities_html = ''
    if amenities:
        items = amenities.replace('<br>', '\n').split('\n')
        amenities_html = ''.join([f'<li><i class="fas fa-check"></i> {i.strip("- ").strip()}</li>' for i in items if i.strip()])
    
    if lang == 'fr':
        nav_home, nav_props, nav_loc, nav_contact = '../index.html', '../proprietes.html', '../saint-martin.html', '../contact.html'
        logo_path, css_path, js_path = '../images/logos/', '../css/style.css', '../js/main.js'
    else:
        nav_home = '../index.html'
        nav_props = '../' + t['nav_properties']
        nav_loc = '../' + t['nav_location']
        nav_contact = '../' + t['nav_contact']
        logo_path, css_path, js_path = '../../images/logos/', '../../css/style.css', '../../js/main.js'
    
    phone_clean = phone.replace(' ', '').replace('(', '').replace(')', '').replace('+', '').replace('-', '')
    
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} | SXM Dream Investments</title>
    <link rel="icon" type="image/png" href="{logo_path}favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{css_path}">
    <style>
        .property-hero {{ height:60vh; min-height:500px; background:linear-gradient(rgba(26,42,58,0.3),rgba(26,42,58,0.5)),url('{image}') center/cover; display:flex; align-items:flex-end; padding:3rem 5%; }}
        .property-hero-content {{ max-width:1200px; width:100%; margin:0 auto; color:white; }}
        .property-hero h1 {{ font-family:'Playfair Display',serif; font-size:3rem; margin-bottom:1rem; text-shadow:2px 2px 4px rgba(0,0,0,0.3); }}
        .property-hero-meta {{ display:flex; gap:2rem; flex-wrap:wrap; align-items:center; }}
        .property-hero-price {{ font-size:2rem; font-weight:700; color:var(--gold); }}
        .property-hero-location {{ display:flex; align-items:center; gap:0.5rem; font-size:1.1rem; }}
        .back-link {{ display:inline-flex; align-items:center; gap:0.5rem; color:white; text-decoration:none; margin-bottom:1rem; opacity:0.9; }}
        .back-link:hover {{ opacity:1; }}
        .property-content {{ padding:4rem 5%; max-width:1200px; margin:0 auto; }}
        .property-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:3rem; }}
        .property-main h2 {{ font-family:'Playfair Display',serif; font-size:1.8rem; color:var(--navy); margin-bottom:1.5rem; }}
        .property-description {{ line-height:1.8; color:var(--gray); }}
        .property-description p {{ margin-bottom:1rem; }}
        .property-description strong {{ color:var(--navy); }}
        .property-features {{ display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin:2rem 0; padding:2rem; background:var(--off-white); border-radius:12px; }}
        .feature-item {{ display:flex; align-items:center; gap:1rem; }}
        .feature-item i {{ width:40px; height:40px; background:white; border-radius:50%; display:flex; align-items:center; justify-content:center; color:var(--gold); }}
        .feature-item-text span {{ display:block; font-size:0.85rem; color:var(--gray); }}
        .feature-item-text strong {{ color:var(--navy); font-size:1.1rem; }}
        .amenities-list {{ list-style:none; padding:0; display:grid; grid-template-columns:repeat(2,1fr); gap:0.75rem; }}
        .amenities-list li {{ display:flex; align-items:center; gap:0.75rem; color:var(--gray); }}
        .amenities-list i {{ color:var(--gold); }}
        .property-sidebar {{ position:sticky; top:100px; }}
        .contact-card {{ background:white; border-radius:12px; padding:2rem; box-shadow:0 10px 40px rgba(0,0,0,0.1); }}
        .contact-card h3 {{ font-family:'Playfair Display',serif; font-size:1.5rem; color:var(--navy); margin-bottom:1rem; }}
        .contact-card p {{ color:var(--gray); margin-bottom:1.5rem; line-height:1.6; }}
        .agent-info {{ display:flex; align-items:center; gap:1rem; padding:1rem; background:var(--off-white); border-radius:8px; margin-bottom:1.5rem; }}
        .agent-avatar {{ width:60px; height:60px; background:var(--gold); border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-size:1.5rem; }}
        .agent-details h4 {{ color:var(--navy); margin-bottom:0.25rem; }}
        .agent-details span {{ font-size:0.9rem; color:var(--gray); }}
        .contact-btn {{ display:block; width:100%; padding:1rem; border:none; border-radius:6px; font-family:'Montserrat',sans-serif; font-size:1rem; font-weight:600; text-align:center; text-decoration:none; margin-bottom:0.75rem; transition:all 0.3s; }}
        .contact-btn-primary {{ background:var(--gold); color:var(--navy); }}
        .contact-btn-primary:hover {{ background:#b8983f; }}
        .contact-btn-secondary {{ background:var(--navy); color:white; }}
        .contact-btn-secondary:hover {{ background:#152232; }}
        .contact-btn i {{ margin-right:0.5rem; }}
        .details-table {{ width:100%; margin-top:2rem; border-collapse:collapse; }}
        .details-table th,.details-table td {{ padding:0.75rem; text-align:left; border-bottom:1px solid var(--gray-light); }}
        .details-table th {{ color:var(--gray); font-weight:500; width:40%; }}
        .details-table td {{ color:var(--navy); font-weight:500; }}
        @media(max-width:1024px) {{ .property-grid {{ grid-template-columns:1fr; }} .property-sidebar {{ position:static; }} }}
        @media(max-width:768px) {{ .property-hero h1 {{ font-size:2rem; }} .property-features,.amenities-list {{ grid-template-columns:1fr; }} }}
    </style>
</head>
<body>
    <nav class="navbar scrolled" id="navbar">
        <a href="{nav_home}" class="logo">
            <img src="{logo_path}logo-white.png" alt="SXM Dream Investments" class="logo-white" style="display:none;">
            <img src="{logo_path}logo-black.png" alt="SXM Dream Investments" class="logo-black">
        </a>
        <ul class="nav-links">
            <li><a href="{nav_home}">{t['home']}</a></li>
            <li><a href="{nav_props}">{t['properties']}</a></li>
            <li><a href="{nav_loc}">{t['saint_martin']}</a></li>
            <li><a href="{nav_contact}">{t['contact']}</a></li>
            <li><a href="{nav_contact}" class="nav-cta">{t['contact_us']}</a></li>
        </ul>
        <button class="mobile-menu-btn"><i class="fas fa-bars"></i></button>
    </nav>
    <section class="property-hero">
        <div class="property-hero-content">
            <a href="{nav_props}" class="back-link"><i class="fas fa-arrow-left"></i> {t['back_to_list']}</a>
            <h1>{escape(title)}</h1>
            <div class="property-hero-meta">
                <span class="property-hero-price">{price}</span>
                <span class="property-hero-location"><i class="fas fa-map-marker-alt"></i> {escape(location)}</span>
            </div>
        </div>
    </section>
    <section class="property-content">
        <div class="property-grid">
            <div class="property-main">
                <div class="property-features">
                    <div class="feature-item"><i class="fas fa-bed"></i><div class="feature-item-text"><span>{t['bedrooms']}</span><strong>{rooms}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-bath"></i><div class="feature-item-text"><span>{t['bathrooms']}</span><strong>{baths}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-expand"></i><div class="feature-item-text"><span>{t['surface']}</span><strong>{sqft} {t['sqft']}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-home"></i><div class="feature-item-text"><span>{t['property_type']}</span><strong>{escape(ptype) if ptype else '-'}</strong></div></div>
                </div>
                <h2>{t['description']}</h2>
                <div class="property-description">{content if content else '<p>' + escape(title) + '</p>'}</div>
                {'<h2>' + t['amenities'] + '</h2><ul class="amenities-list">' + amenities_html + '</ul>' if amenities_html else ''}
                <h2>{t['features']}</h2>
                <table class="details-table">
                    <tr><th>{t['location']}</th><td>{escape(location)}</td></tr>
                    <tr><th>{t['property_type']}</th><td>{escape(ptype) if ptype else '-'}</td></tr>
                    <tr><th>{t['year_built']}</th><td>{year}</td></tr>
                    <tr><th>{t['view']}</th><td>{escape(view)}</td></tr>
                    <tr><th>{t['cooling']}</th><td>{escape(cooling)}</td></tr>
                    <tr><th>{t['flooring']}</th><td>{escape(flooring)}</td></tr>
                    <tr><th>{t['parking']}</th><td>{escape(parking)}</td></tr>
                    <tr><th>{t['pool']}</th><td>{escape(pool)}</td></tr>
                </table>
            </div>
            <div class="property-sidebar">
                <div class="contact-card">
                    <h3>{t['interested']}</h3>
                    <p>{t['contact_text']}</p>
                    <div class="agent-info">
                        <div class="agent-avatar"><i class="fas fa-user"></i></div>
                        <div class="agent-details"><h4>{escape(agent)}</h4><span>SXM Dream Investments</span></div>
                    </div>
                    <a href="mailto:{email}" class="contact-btn contact-btn-primary"><i class="fas fa-envelope"></i> {t['contact_agent']}</a>
                    <a href="tel:+{phone_clean}" class="contact-btn contact-btn-secondary"><i class="fas fa-phone"></i> {phone}</a>
                    <a href="https://wa.me/{phone_clean}" class="contact-btn contact-btn-secondary" target="_blank"><i class="fab fa-whatsapp"></i> WhatsApp</a>
                </div>
            </div>
        </div>
    </section>
    <footer>
        <div class="footer-grid">
            <div class="footer-col">
                <img src="{logo_path}logo-white.png" alt="SXM Dream Investments" style="max-width:180px;margin-bottom:1rem;">
                <p>{t['footer_text']}</p>
            </div>
            <div class="footer-col">
                <h4>Contact</h4>
                <p><i class="fas fa-map-marker-alt"></i> Simpson Bay, {t['location_name']}</p>
                <p><i class="fas fa-phone"></i> {phone}</p>
                <p><i class="fas fa-envelope"></i> {email}</p>
            </div>
        </div>
        <div class="footer-bottom"><p>&copy; 2025 SXM Dream Investments. {t['all_rights']}</p></div>
    </footer>
    <script src="{js_path}"></script>
</body>
</html>'''

def main():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    properties = data.get('properties', [])
    print(f"Loaded {len(properties)} properties")
    
    for d in OUTPUT_DIRS.values():
        os.makedirs(d, exist_ok=True)
    
    props_by_lang = {'fr': [], 'en': [], 'nl': []}
    for p in properties:
        lang = p.get('language', 'en')
        if lang in props_by_lang:
            props_by_lang[lang].append(p)
    
    total = 0
    for lang, props in props_by_lang.items():
        print(f"Generating {len(props)} {lang.upper()} pages...")
        for p in props:
            slug = p.get('slug', slugify(p.get('title', 'property')))
            path = os.path.join(OUTPUT_DIRS[lang], f"{slug}.html")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(generate_page(p, lang))
            total += 1
        print(f"  Created in {OUTPUT_DIRS[lang]}/")
    
    print(f"\nTotal: {total} pages generated!")

if __name__ == '__main__':
    main()

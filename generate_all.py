#!/usr/bin/env python3
import json
import os
import re
from html import escape

OUTPUT_DIRS = {'fr': 'biens', 'en': 'en/properties-list', 'nl': 'nl/vastgoed'}

TRANS = {
    'fr': {
        'back_to_list': 'Retour aux propriétés', 'bedrooms': 'Chambres', 'bathrooms': 'Salles de bain',
        'surface': 'Surface', 'year_built': 'Année', 'property_type': 'Type',
        'location': 'Localisation', 'description': 'Description', 'features': 'Caractéristiques',
        'amenities': 'Équipements', 'contact_agent': "Contacter", 'view': 'Vue',
        'cooling': 'Climatisation', 'flooring': 'Sol', 'parking': 'Parking', 'pool': 'Piscine',
        'home': 'Accueil', 'properties': 'Propriétés', 'saint_martin': 'Saint-Martin', 'contact': 'Contact',
        'contact_us': 'Nous contacter', 'sqft': 'sqft', 'interested': 'Intéressé par ce bien ?',
        'contact_text': 'Notre équipe est à votre disposition.',
        'nav_props': 'proprietes.html', 'nav_loc': 'saint-martin.html', 'nav_contact': 'contact.html',
        'footer_text': 'Votre partenaire de confiance à Saint-Martin.',
        'all_rights': 'Tous droits réservés.', 'location_name': 'Saint-Martin'
    },
    'en': {
        'back_to_list': 'Back to properties', 'bedrooms': 'Bedrooms', 'bathrooms': 'Bathrooms',
        'surface': 'Surface', 'year_built': 'Year', 'property_type': 'Type',
        'location': 'Location', 'description': 'Description', 'features': 'Features',
        'amenities': 'Amenities', 'contact_agent': 'Contact', 'view': 'View',
        'cooling': 'Cooling', 'flooring': 'Flooring', 'parking': 'Parking', 'pool': 'Pool',
        'home': 'Home', 'properties': 'Properties', 'saint_martin': 'St. Martin', 'contact': 'Contact',
        'contact_us': 'Contact Us', 'sqft': 'sqft', 'interested': 'Interested?',
        'contact_text': 'Our team is available to help.',
        'nav_props': 'properties.html', 'nav_loc': 'st-martin.html', 'nav_contact': 'contact.html',
        'footer_text': 'Your trusted partner in St. Martin.',
        'all_rights': 'All rights reserved.', 'location_name': 'St. Martin'
    },
    'nl': {
        'back_to_list': 'Terug naar vastgoed', 'bedrooms': 'Slaapkamers', 'bathrooms': 'Badkamers',
        'surface': 'Oppervlakte', 'year_built': 'Bouwjaar', 'property_type': 'Type',
        'location': 'Locatie', 'description': 'Beschrijving', 'features': 'Kenmerken',
        'amenities': 'Voorzieningen', 'contact_agent': 'Contact', 'view': 'Uitzicht',
        'cooling': 'Airco', 'flooring': 'Vloer', 'parking': 'Parkeren', 'pool': 'Zwembad',
        'home': 'Home', 'properties': 'Vastgoed', 'saint_martin': 'Sint Maarten', 'contact': 'Contact',
        'contact_us': 'Neem Contact Op', 'sqft': 'sqft', 'interested': 'Geïnteresseerd?',
        'contact_text': 'Ons team staat klaar om u te helpen.',
        'nav_props': 'eigenschappen.html', 'nav_loc': 'sint-maarten.html', 'nav_contact': 'contact.html',
        'footer_text': 'Uw partner in Sint Maarten.',
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
    text = re.sub(r'id="[^"]*"', '', text)
    text = re.sub(r'data-[^=]*="[^"]*"', '', text)
    text = re.sub(r'dir="[^"]*"', '', text)
    text = re.sub(r'role="[^"]*"', '', text)
    text = re.sub(r'\s+>', '>', text)
    return text

def get_image(prop, lang='fr'):
    """Get the best image for a property. Prefers local gallery images."""
    gallery = prop.get('gallery_images', '')
    if gallery:
        imgs = [i.strip() for i in gallery.split(',') if i.strip()]
        if imgs:
            # Adjust path based on language (property pages are one level deep)
            return imgs[0]
    if prop.get('featured_image'):
        return prop['featured_image']
    pt = (prop.get('type', '') or prop.get('property_type', '')).lower()
    if 'villa' in pt: return 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'
    if 'penthouse' in pt: return 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800'
    if 'condo' in pt: return 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800'
    return 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800'

def get_gallery_images(prop):
    """Get list of all gallery images for a property."""
    gallery = prop.get('gallery_images', '')
    if gallery:
        return [i.strip() for i in gallery.split(',') if i.strip()]
    return []

def generate_page(prop, lang):
    t = TRANS[lang]
    title = prop.get('title', 'Property')
    price = prop.get('price', 'Contact')
    location = prop.get('location', '')
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
    image = get_image(prop, lang)
    gallery = get_gallery_images(prop)

    amenities_html = ''
    if amenities:
        items = amenities.replace('<br>', '\n').split('\n')
        amenities_html = ''.join([f'<li><i class="fas fa-check"></i> {i.strip("- ").strip()}</li>' for i in items if i.strip()])
    
    if lang == 'fr':
        nav_home, nav_props, nav_loc, nav_contact = '../index.html', '../proprietes.html', '../saint-martin.html', '../contact.html'
        logo_path, css_path, js_path = '../images/logos/', '../css/style.css', '../js/main.js'
    else:
        nav_home = '../index.html'
        nav_props = '../' + t['nav_props']
        nav_loc = '../' + t['nav_loc']
        nav_contact = '../' + t['nav_contact']
        logo_path, css_path, js_path = '../../images/logos/', '../../css/style.css', '../../js/main.js'
    
    phone_clean = phone.replace(' ', '').replace('(', '').replace(')', '').replace('+', '').replace('-', '')
    
    # Build gallery HTML
    img_prefix = '../' if lang == 'fr' else '../../'
    hero_image = img_prefix + gallery[0] if gallery else image

    gallery_thumbs = ''
    gallery_items = ''
    if gallery:
        for idx, gimg in enumerate(gallery):
            full_path = img_prefix + gimg
            active = ' active' if idx == 0 else ''
            gallery_thumbs += f'<div class="gallery-thumb{active}" onclick="openLightbox({idx})" style="background-image:url(\'{full_path}\')"></div>\n'
            gallery_items += f'<div class="lightbox-slide"><img src="{full_path}" alt="{escape(title)} - Photo {idx+1}"></div>\n'

    gallery_section = ''
    if gallery and len(gallery) > 1:
        gallery_section = f'''
                <h2>Photos</h2>
                <div class="gallery-grid">
                    {gallery_thumbs}
                </div>'''

    lightbox_html = ''
    if gallery:
        lightbox_html = f'''
    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <button class="lightbox-close" onclick="closeLightbox(event)">&times;</button>
        <button class="lightbox-prev" onclick="prevSlide(event)">&#10094;</button>
        <button class="lightbox-next" onclick="nextSlide(event)">&#10095;</button>
        <div class="lightbox-container">
            {gallery_items}
        </div>
        <div class="lightbox-counter"><span id="lightboxCounter">1</span> / {len(gallery)}</div>
    </div>'''

    lightbox_js = '''
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.lightbox-slide');
        const totalSlides = slides.length;
        function openLightbox(idx) {
            currentSlide = idx;
            showSlide();
            document.getElementById('lightbox').classList.add('open');
            document.body.style.overflow = 'hidden';
        }
        function closeLightbox(e) {
            if (e.target.classList.contains('lightbox') || e.target.classList.contains('lightbox-close')) {
                document.getElementById('lightbox').classList.remove('open');
                document.body.style.overflow = '';
            }
        }
        function showSlide() {
            slides.forEach((s, i) => s.style.display = i === currentSlide ? 'flex' : 'none');
            document.getElementById('lightboxCounter').textContent = currentSlide + 1;
        }
        function nextSlide(e) { e.stopPropagation(); currentSlide = (currentSlide + 1) % totalSlides; showSlide(); }
        function prevSlide(e) { e.stopPropagation(); currentSlide = (currentSlide - 1 + totalSlides) % totalSlides; showSlide(); }
        document.addEventListener('keydown', function(e) {
            const lb = document.getElementById('lightbox');
            if (!lb || !lb.classList.contains('open')) return;
            if (e.key === 'Escape') { lb.classList.remove('open'); document.body.style.overflow = ''; }
            if (e.key === 'ArrowRight') { currentSlide = (currentSlide + 1) % totalSlides; showSlide(); }
            if (e.key === 'ArrowLeft') { currentSlide = (currentSlide - 1 + totalSlides) % totalSlides; showSlide(); }
        });
        if (slides.length > 0) showSlide();
    </script>''' if gallery else ''

    # Hero slider buttons if gallery exists
    hero_nav = ''
    if gallery and len(gallery) > 1:
        hero_nav = f'''
            <div class="hero-slider-nav">
                <button class="hero-slider-btn" onclick="openLightbox(0)"><i class="fas fa-images"></i> {len(gallery)} photos</button>
            </div>'''

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
        .property-hero {{ height:60vh; min-height:500px; background:linear-gradient(rgba(26,42,58,0.3),rgba(26,42,58,0.5)),url('{hero_image}') center/cover; display:flex; align-items:flex-end; padding:3rem 5%; position:relative; }}
        .property-hero-content {{ max-width:1200px; width:100%; margin:0 auto; color:white; }}
        .property-hero h1 {{ font-family:'Playfair Display',serif; font-size:3rem; margin-bottom:1rem; text-shadow:2px 2px 4px rgba(0,0,0,0.3); }}
        .property-hero-meta {{ display:flex; gap:2rem; flex-wrap:wrap; align-items:center; }}
        .property-hero-price {{ font-size:2rem; font-weight:700; color:var(--gold); }}
        .property-hero-location {{ display:flex; align-items:center; gap:0.5rem; font-size:1.1rem; }}
        .back-link {{ display:inline-flex; align-items:center; gap:0.5rem; color:white; text-decoration:none; margin-bottom:1rem; opacity:0.9; }}
        .hero-slider-nav {{ position:absolute; bottom:2rem; right:5%; }}
        .hero-slider-btn {{ background:rgba(255,255,255,0.9); color:var(--navy); border:none; padding:0.7rem 1.2rem; border-radius:6px; cursor:pointer; font-family:'Montserrat',sans-serif; font-weight:600; font-size:0.9rem; display:flex; align-items:center; gap:0.5rem; transition:background 0.3s; }}
        .hero-slider-btn:hover {{ background:white; }}
        .property-content {{ padding:4rem 5%; max-width:1200px; margin:0 auto; }}
        .property-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:3rem; }}
        .property-main h2 {{ font-family:'Playfair Display',serif; font-size:1.8rem; color:var(--navy); margin-bottom:1.5rem; }}
        .property-description {{ line-height:1.8; color:var(--gray); }}
        .property-description p {{ margin-bottom:1rem; }}
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
        .contact-card p {{ color:var(--gray); margin-bottom:1.5rem; }}
        .agent-info {{ display:flex; align-items:center; gap:1rem; padding:1rem; background:var(--off-white); border-radius:8px; margin-bottom:1.5rem; }}
        .agent-avatar {{ width:60px; height:60px; background:var(--gold); border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-size:1.5rem; }}
        .agent-details h4 {{ color:var(--navy); }}
        .agent-details span {{ font-size:0.9rem; color:var(--gray); }}
        .contact-btn {{ display:block; width:100%; padding:1rem; border:none; border-radius:6px; font-family:'Montserrat',sans-serif; font-size:1rem; font-weight:600; text-align:center; text-decoration:none; margin-bottom:0.75rem; }}
        .contact-btn-primary {{ background:var(--gold); color:var(--navy); }}
        .contact-btn-secondary {{ background:var(--navy); color:white; }}
        .details-table {{ width:100%; margin-top:2rem; border-collapse:collapse; }}
        .details-table th,.details-table td {{ padding:0.75rem; text-align:left; border-bottom:1px solid var(--gray-light); }}
        .details-table th {{ color:var(--gray); width:40%; }}
        .details-table td {{ color:var(--navy); font-weight:500; }}
        /* Gallery grid */
        .gallery-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:2rem; }}
        .gallery-thumb {{ height:150px; background-size:cover; background-position:center; border-radius:8px; cursor:pointer; transition:transform 0.3s, opacity 0.3s; }}
        .gallery-thumb:hover {{ transform:scale(1.03); opacity:0.9; }}
        /* Lightbox */
        .lightbox {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:10000; align-items:center; justify-content:center; }}
        .lightbox.open {{ display:flex; }}
        .lightbox-container {{ width:100%; height:100%; display:flex; align-items:center; justify-content:center; }}
        .lightbox-slide {{ display:none; align-items:center; justify-content:center; width:100%; height:100%; padding:60px; box-sizing:border-box; }}
        .lightbox-slide img {{ max-width:100%; max-height:100%; object-fit:contain; border-radius:4px; }}
        .lightbox-close {{ position:absolute; top:20px; right:30px; color:white; font-size:2.5rem; background:none; border:none; cursor:pointer; z-index:10001; line-height:1; }}
        .lightbox-prev,.lightbox-next {{ position:absolute; top:50%; transform:translateY(-50%); color:white; font-size:2rem; background:rgba(255,255,255,0.15); border:none; cursor:pointer; z-index:10001; padding:1rem 1.2rem; border-radius:50%; transition:background 0.3s; }}
        .lightbox-prev:hover,.lightbox-next:hover {{ background:rgba(255,255,255,0.3); }}
        .lightbox-prev {{ left:20px; }}
        .lightbox-next {{ right:20px; }}
        .lightbox-counter {{ position:absolute; bottom:20px; left:50%; transform:translateX(-50%); color:white; font-size:1rem; font-family:'Montserrat',sans-serif; }}
        @media(max-width:1024px) {{ .property-grid {{ grid-template-columns:1fr; }} .gallery-grid {{ grid-template-columns:repeat(3,1fr); }} }}
        @media(max-width:768px) {{ .property-hero h1 {{ font-size:2rem; }} .property-features,.amenities-list {{ grid-template-columns:1fr; }} .gallery-grid {{ grid-template-columns:repeat(2,1fr); }} .gallery-thumb {{ height:120px; }} .lightbox-slide {{ padding:20px; }} }}
    </style>
</head>
<body>
    <nav class="navbar scrolled" id="navbar">
        <a href="{nav_home}" class="logo">
            <img src="{logo_path}logo-black.png" alt="SXM Dream Investments" class="logo-black">
        </a>
        <ul class="nav-links">
            <li><a href="{nav_home}">{t['home']}</a></li>
            <li><a href="{nav_props}">{t['properties']}</a></li>
            <li><a href="{nav_loc}">{t['saint_martin']}</a></li>
            <li><a href="{nav_contact}">{t['contact']}</a></li>
            <li><a href="{nav_contact}" class="nav-cta">{t['contact_us']}</a></li>
        </ul>
    </nav>
    <section class="property-hero">
        <div class="property-hero-content">
            <a href="{nav_props}" class="back-link"><i class="fas fa-arrow-left"></i> {t['back_to_list']}</a>
            <h1>{escape(title)}</h1>
            <div class="property-hero-meta">
                <span class="property-hero-price">{price}</span>
                <span class="property-hero-location"><i class="fas fa-map-marker-alt"></i> {escape(location)}</span>
            </div>
        </div>{hero_nav}
    </section>
    <section class="property-content">
        <div class="property-grid">
            <div class="property-main">
                <div class="property-features">
                    <div class="feature-item"><i class="fas fa-bed"></i><div class="feature-item-text"><span>{t['bedrooms']}</span><strong>{rooms}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-bath"></i><div class="feature-item-text"><span>{t['bathrooms']}</span><strong>{baths}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-expand"></i><div class="feature-item-text"><span>{t['surface']}</span><strong>{sqft}</strong></div></div>
                    <div class="feature-item"><i class="fas fa-home"></i><div class="feature-item-text"><span>{t['property_type']}</span><strong>{escape(ptype) if ptype else '-'}</strong></div></div>
                </div>{gallery_section}
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
    </section>{lightbox_html}
    <footer>
        <div class="footer-grid">
            <div class="footer-col"><img src="{logo_path}logo-white.png" alt="SXM" style="max-width:180px;margin-bottom:1rem;"><p>{t['footer_text']}</p></div>
            <div class="footer-col"><h4>Contact</h4><p><i class="fas fa-phone"></i> {phone}</p><p><i class="fas fa-envelope"></i> {email}</p></div>
        </div>
        <div class="footer-bottom"><p>&copy; 2025 SXM Dream Investments. {t['all_rights']}</p></div>
    </footer>
    <script src="{js_path}"></script>{lightbox_js}
</body>
</html>'''

def get_price_num(price):
    nums = re.findall(r'[\d,]+', price.replace(',', ''))
    return int(nums[0].replace(',', '')) if nums else 0

def get_location_slug(prop):
    for cat in prop.get('categories', []):
        if cat.get('domain') == 'project-location':
            return cat.get('nicename', '').lower()
    loc = prop.get('location', '').lower()
    for l in ['maho', 'cupecoy', 'simpson', 'pelican', 'pirouette', 'cole', 'orient', 'dawn', 'oyster', 'philipsburg']:
        if l in loc: return l if l != 'simpson' else 'simpson-bay'
    return 'other'

def get_type_slug(prop):
    pt = (prop.get('type', '') or prop.get('property_type', '')).lower()
    if 'villa' in pt: return 'villa'
    if 'penthouse' in pt: return 'penthouse'
    if 'condo' in pt: return 'condo'
    if 'appart' in pt: return 'appartement'
    return 'other'

def generate_listing(lang, props):
    T = {
        'fr': {'title': 'Nos Propriétés', 'subtitle': 'Notre Portfolio', 'desc': 'Découvrez notre sélection de biens de luxe',
               'all_types': 'Tous', 'all_loc': 'Toutes', 'all_budgets': 'Tous', 'type': 'Type', 'location': 'Lieu', 'budget': 'Budget',
               'count': 'propriétés', 'beds': 'ch.', 'baths': 'sdb.', 'home': 'Accueil', 'properties': 'Propriétés',
               'saint_martin': 'Saint-Martin', 'contact': 'Contact', 'contact_us': 'Nous contacter',
               'nav_props': 'proprietes.html', 'nav_loc': 'saint-martin.html', 'nav_contact': 'contact.html',
               'prop_dir': 'biens', 'location_name': 'Saint-Martin'},
        'en': {'title': 'Our Properties', 'subtitle': 'Our Portfolio', 'desc': 'Discover our exclusive luxury selection',
               'all_types': 'All', 'all_loc': 'All', 'all_budgets': 'All', 'type': 'Type', 'location': 'Location', 'budget': 'Budget',
               'count': 'properties', 'beds': 'bd', 'baths': 'ba', 'home': 'Home', 'properties': 'Properties',
               'saint_martin': 'St. Martin', 'contact': 'Contact', 'contact_us': 'Contact Us',
               'nav_props': 'properties.html', 'nav_loc': 'st-martin.html', 'nav_contact': 'contact.html',
               'prop_dir': 'properties-list', 'location_name': 'St. Martin'},
        'nl': {'title': 'Ons Vastgoed', 'subtitle': 'Ons Portfolio', 'desc': 'Ontdek onze exclusieve luxe selectie',
               'all_types': 'Alle', 'all_loc': 'Alle', 'all_budgets': 'Alle', 'type': 'Type', 'location': 'Locatie', 'budget': 'Budget',
               'count': 'woningen', 'beds': 'slpk', 'baths': 'badk', 'home': 'Home', 'properties': 'Vastgoed',
               'saint_martin': 'Sint Maarten', 'contact': 'Contact', 'contact_us': 'Neem Contact Op',
               'nav_props': 'eigenschappen.html', 'nav_loc': 'sint-maarten.html', 'nav_contact': 'contact.html',
               'prop_dir': 'vastgoed', 'location_name': 'Sint Maarten'}
    }
    t = T[lang]
    
    props_js = []
    for p in props:
        slug = p.get('slug', slugify(p.get('title', '')))
        link = f"biens/{slug}.html" if lang == 'fr' else f"{t['prop_dir']}/{slug}.html"
        # For listings, local images need path relative to listing page location
        listing_image = get_image(p, lang)
        if listing_image.startswith('images/'):
            # Listing pages: fr is at root, en/nl are one level deep
            listing_image = listing_image if lang == 'fr' else '../' + listing_image
        props_js.append({
            'title': p.get('title', ''), 'price': p.get('price', ''), 'priceNum': get_price_num(p.get('price', '')),
            'type': get_type_slug(p), 'location': p.get('location', ''), 'locationSlug': get_location_slug(p),
            'beds': p.get('rooms', '-'), 'baths': p.get('baths', '-'), 'sqft': p.get('sqft', '-'),
            'image': listing_image, 'link': link
        })
    
    base = '' if lang == 'fr' else '../'
    img = 'images/logos/' if lang == 'fr' else '../images/logos/'
    css = 'css/style.css' if lang == 'fr' else '../css/style.css'
    js = 'js/main.js' if lang == 'fr' else '../js/main.js'

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']} | SXM Dream Investments</title>
    <link rel="icon" type="image/png" href="{img}favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{css}">
    <style>
        .page-hero {{ height:50vh; min-height:400px; background:linear-gradient(rgba(26,42,58,0.7),rgba(26,42,58,0.7)),url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=2000') center/cover; display:flex; align-items:center; justify-content:center; text-align:center; color:white; }}
        .page-hero h1 {{ font-size:3rem; margin-bottom:1rem; }}
        .properties-section {{ padding:4rem 5%; }}
        .filters-bar {{ background:var(--off-white); padding:2rem 5%; display:flex; flex-wrap:wrap; gap:1rem; justify-content:center; }}
        .filter-group {{ display:flex; align-items:center; gap:0.5rem; }}
        .filter-group label {{ font-weight:500; color:var(--navy); }}
        .filter-select {{ padding:0.75rem 1.5rem; border:1px solid var(--gray-light); border-radius:6px; font-family:'Montserrat',sans-serif; min-width:200px; }}
        .properties-count {{ text-align:center; padding:1rem; color:var(--gray); }}
        .properties-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:2rem; max-width:1400px; margin:0 auto; }}
        .property-card {{ background:white; border-radius:12px; overflow:hidden; box-shadow:0 5px 20px rgba(0,0,0,0.08); text-decoration:none; color:inherit; transition:transform 0.3s; }}
        .property-card:hover {{ transform:translateY(-5px); }}
        .property-image {{ height:220px; background-size:cover; background-position:center; position:relative; }}
        .property-badge {{ position:absolute; top:1rem; left:1rem; background:var(--gold); color:var(--navy); padding:0.4rem 0.8rem; border-radius:4px; font-size:0.8rem; font-weight:600; text-transform:capitalize; }}
        .property-price {{ position:absolute; bottom:1rem; right:1rem; background:var(--navy); color:white; padding:0.5rem 1rem; border-radius:4px; font-weight:600; }}
        .property-content {{ padding:1.5rem; }}
        .property-content h3 {{ font-family:'Playfair Display',serif; font-size:1.2rem; color:var(--navy); margin-bottom:0.5rem; }}
        .property-location {{ color:var(--gray); font-size:0.9rem; margin-bottom:1rem; }}
        .property-location i {{ color:var(--gold); margin-right:0.3rem; }}
        .property-features {{ display:flex; gap:1rem; }}
        .property-feature {{ display:flex; align-items:center; gap:0.3rem; color:var(--gray); font-size:0.85rem; }}
        .property-feature i {{ color:var(--gold); }}
        @media(max-width:1024px) {{ .properties-grid {{ grid-template-columns:repeat(2,1fr); }} }}
        @media(max-width:768px) {{ .properties-grid {{ grid-template-columns:1fr; }} .filters-bar {{ flex-direction:column; }} }}
    </style>
</head>
<body>
    <nav class="navbar" id="navbar">
        <a href="{base}index.html" class="logo"><img src="{img}logo-white.png" class="logo-white"><img src="{img}logo-black.png" class="logo-black" style="display:none;"></a>
        <ul class="nav-links">
            <li><a href="{base}index.html">{t['home']}</a></li>
            <li><a href="{t['nav_props']}">{t['properties']}</a></li>
            <li><a href="{t['nav_loc']}">{t['saint_martin']}</a></li>
            <li><a href="{t['nav_contact']}">{t['contact']}</a></li>
            <li><a href="{t['nav_contact']}" class="nav-cta">{t['contact_us']}</a></li>
            <li class="lang-switcher">
                <a href="{base}proprietes.html" {'class="active"' if lang=='fr' else ''}>FR</a>
                <a href="{base}en/properties.html" {'class="active"' if lang=='en' else ''}>EN</a>
                <a href="{base}nl/eigenschappen.html" {'class="active"' if lang=='nl' else ''}>NL</a>
            </li>
        </ul>
    </nav>
    <section class="page-hero"><div><span class="hero-badge">{t['subtitle']}</span><h1>{t['title']}</h1><p>{t['desc']}</p></div></section>
    <div class="filters-bar">
        <div class="filter-group"><label>{t['type']}:</label><select class="filter-select" id="typeFilter" onchange="filterProperties()">
            <option value="all">{t['all_types']}</option><option value="villa">Villa</option><option value="penthouse">Penthouse</option><option value="condo">Condo</option><option value="appartement">Appartement</option>
        </select></div>
        <div class="filter-group"><label>{t['location']}:</label><select class="filter-select" id="locationFilter" onchange="filterProperties()">
            <option value="all">{t['all_loc']}</option><option value="maho">Maho</option><option value="cupecoy">Cupecoy</option><option value="simpson-bay">Simpson Bay</option><option value="pelican-key">Pelican Key</option><option value="point-pirouette">Point Pirouette</option><option value="cole-bay">Cole Bay</option>
        </select></div>
        <div class="filter-group"><label>{t['budget']}:</label><select class="filter-select" id="priceFilter" onchange="filterProperties()">
            <option value="all">{t['all_budgets']}</option><option value="0-500000">0-$500K</option><option value="500000-1000000">$500K-$1M</option><option value="1000000-2000000">$1M-$2M</option><option value="2000000+">$2M+</option>
        </select></div>
    </div>
    <p class="properties-count"><span id="count">{len(props)}</span> {t['count']}</p>
    <section class="properties-section"><div class="properties-grid" id="propertiesGrid"></div></section>
    <footer><div class="footer-grid"><div class="footer-col"><img src="{img}logo-white.png" style="max-width:180px;"></div></div><div class="footer-bottom"><p>&copy; 2025 SXM Dream Investments</p></div></footer>
    <script src="{js}"></script>
    <script>
        const properties = {json.dumps(props_js, ensure_ascii=False)};
        const BEDS="{t['beds']}",BATHS="{t['baths']}";
        function renderProperties(props) {{
            document.getElementById('propertiesGrid').innerHTML = props.map(p => `<a href="${{p.link}}" class="property-card"><div class="property-image" style="background-image:url('${{p.image}}')"><span class="property-badge">${{p.type}}</span><span class="property-price">${{p.price}}</span></div><div class="property-content"><h3>${{p.title}}</h3><p class="property-location"><i class="fas fa-map-marker-alt"></i> ${{p.location}}</p><div class="property-features"><span class="property-feature"><i class="fas fa-bed"></i> ${{p.beds}} ${{BEDS}}</span><span class="property-feature"><i class="fas fa-bath"></i> ${{p.baths}} ${{BATHS}}</span></div></div></a>`).join('');
            document.getElementById('count').textContent = props.length;
        }}
        function filterProperties() {{
            let f=properties;
            const type=document.getElementById('typeFilter').value;
            const loc=document.getElementById('locationFilter').value;
            const price=document.getElementById('priceFilter').value;
            if(type!='all')f=f.filter(p=>p.type===type);
            if(loc!='all')f=f.filter(p=>p.locationSlug===loc);
            if(price!='all'){{const[min,max]=price.split('-').map(v=>v==='+'?Infinity:parseInt(v.replace('+','')));if(max)f=f.filter(p=>p.priceNum>=min&&p.priceNum<=max);else f=f.filter(p=>p.priceNum>=min);}}
            renderProperties(f);
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
    
    for d in OUTPUT_DIRS.values():
        os.makedirs(d, exist_ok=True)
    
    total = 0
    for lang, props in props_by_lang.items():
        print(f"Generating {len(props)} {lang.upper()} property pages...")
        for p in props:
            slug = p.get('slug', slugify(p.get('title', 'property')))
            path = os.path.join(OUTPUT_DIRS[lang], f"{slug}.html")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(generate_page(p, lang))
            total += 1
    print(f"Generated {total} property pages")
    
    # Generate listings
    with open('proprietes.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing('fr', props_by_lang['fr']))
    with open('en/properties.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing('en', props_by_lang['en']))
    with open('nl/eigenschappen.html', 'w', encoding='utf-8') as f:
        f.write(generate_listing('nl', props_by_lang['nl']))
    print("Updated listing pages")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Convert all property pages from old hero layout to new Andréu-style layout."""
import os, re, glob
from html import unescape

BIENS_DIR = '/Users/benjaminlegal/Documents/SXM-Invest/biens'
SKIP = ['aquamarina-2-bedroom-condo-point-pirouette.html']

def extract(html, pattern, default=''):
    m = re.search(pattern, html, re.DOTALL)
    return m.group(1).strip() if m else default

def convert_page(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Check it's the old format
    if 'property-hero' not in html:
        return False

    # Title
    title = extract(html, r'<h1>(.*?)</h1>')
    if not title:
        return False

    # Price
    price = extract(html, r'property-hero-price["\']?>(.*?)</span')
    if not price:
        price = 'Prix sur demande'

    # Location
    location = extract(html, r'property-hero-location["\']?>.*?</i>\s*(.*?)</span', 'Saint-Martin')

    # Features (beds, baths, sqft, type)
    beds = baths = sqft = typ = ''
    feature_block = extract(html, r'<div class="property-features">(.*?)</div>\s*<h2', '')
    if feature_block:
        items = re.findall(r'<span>(.*?)</span>\s*<strong>(.*?)</strong>', feature_block)
        for label, value in items:
            ll = label.lower().strip()
            if 'chambre' in ll or 'bedroom' in ll or 'slaap' in ll:
                beds = value
            elif 'salle' in ll or 'bath' in ll or 'badk' in ll:
                baths = value
            elif 'surface' in ll or 'sqft' in ll or 'opp' in ll:
                sqft = value
            elif 'type' in ll:
                typ = value

    # Description - extract just the content between property-description div tags
    desc = ''
    m = re.search(r'<div class="property-description">(.*?)</div>\s*\n', html, re.DOTALL)
    if m:
        desc = m.group(1).strip()
    else:
        m = re.search(r'<div class="property-description">(.*?)</div>', html, re.DOTALL)
        if m:
            desc = m.group(1).strip()

    # Details table rows
    details_rows = re.findall(r'<tr><th>(.*?)</th><td>(.*?)</td></tr>', html)
    # Filter out empty values and avoid duplicating beds/baths/sqft/type/location
    skip_labels = {'localisation', 'type', 'chambres', 'salles de bain', 'surface', 'location', 'bedrooms', 'bathrooms'}
    filtered_details = [(k, v) for k, v in details_rows if v.strip() and k.lower().strip() not in skip_labels]

    # Amenities list
    amenities = []
    amenities_block = extract(html, r'<ul class="amenities-list">(.*?)</ul>', '')
    if amenities_block:
        amenities = re.findall(r'</i>\s*(.*?)</li>', amenities_block)
        amenities = [a.strip() for a in amenities if a.strip()]

    # Image folder and count
    img_folder = ''
    m = re.search(r"properties_clean/([^/]+)/", html)
    if m:
        img_folder = m.group(1)

    # Count lightbox slides
    num_photos = len(re.findall(r'class="lightbox-slide"', html))
    if num_photos == 0:
        m = re.search(r'(\d+)\s*photos?', html)
        if m:
            num_photos = int(m.group(1))

    if not img_folder or num_photos == 0:
        print(f"  SKIP (no images): {os.path.basename(filepath)}")
        return False

    # Build badges HTML
    badges = ''
    if beds:
        badges += f'<span class="listing-badge">{beds} Chambres</span>\n                    '
    if baths:
        badges += f'<span class="listing-badge">{baths} Sdb.</span>\n                    '
    if sqft:
        badges += f'<span class="listing-badge">{sqft} SQFT</span>'

    # Build info items (avoid duplicates)
    info_items = f'<div class="listing-info-item"><span class="label">Prix</span><span class="value">{price}</span></div>\n'
    if beds:
        info_items += f'                    <div class="listing-info-item"><span class="label">Chambres</span><span class="value">{beds}</span></div>\n'
    if baths:
        info_items += f'                    <div class="listing-info-item"><span class="label">Salles de bain</span><span class="value">{baths}</span></div>\n'
    if sqft:
        info_items += f'                    <div class="listing-info-item"><span class="label">Surface</span><span class="value">{sqft} SQFT</span></div>\n'
    if typ:
        info_items += f'                    <div class="listing-info-item"><span class="label">Type</span><span class="value">{typ}</span></div>\n'
    info_items += f'                    <div class="listing-info-item"><span class="label">Localisation</span><span class="value">{location}</span></div>\n'
    for k, v in filtered_details:
        info_items += f'                    <div class="listing-info-item"><span class="label">{k}</span><span class="value">{v}</span></div>\n'
    info_items += '                    <div class="listing-info-item"><span class="label">Statut</span><span class="value">Actif</span></div>'

    # Build features pills
    features_section = ''
    if amenities:
        pills = '\n                    '.join(f'<span class="feature-pill">{a}</span>' for a in amenities)
        features_section = f'''
                <h2 class="listing-section-title">Caractéristiques</h2>
                <div class="listing-features">
                    {pills}
                </div>'''

    # Build lightbox slides
    lightbox_slides = '\n'.join(
        f'            <div class="lightbox-slide"><img src="../images/properties_clean/{img_folder}/{str(i).zfill(2)}.jpg" alt="Photo {i}"></div>'
        for i in range(1, num_photos + 1)
    )

    title_escaped = title.replace('"', '&quot;')

    new_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{unescape(title)} | SXM Dream Investments</title>
    <link rel="icon" type="image/png" href="../images/logos/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .listing-page {{ max-width:1200px; margin:0 auto; padding:2rem 5%; padding-top:100px; }}
        .breadcrumb {{ padding:1rem 0; font-size:0.85rem; }}
        .breadcrumb a {{ color:var(--navy); text-decoration:none; }}
        .breadcrumb a:hover {{ text-decoration:underline; }}
        .breadcrumb i {{ color:#c0392b; margin-right:0.3rem; }}
        .listing-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.5rem; gap:2rem; flex-wrap:wrap; }}
        .listing-header-left h1 {{ font-family:'Playfair Display',serif; font-size:2rem; color:var(--navy); margin-bottom:0.75rem; font-weight:600; }}
        .listing-badges {{ display:flex; gap:0.6rem; flex-wrap:wrap; }}
        .listing-badge {{ background:var(--navy); color:white; padding:0.35rem 0.9rem; border-radius:4px; font-size:0.8rem; font-weight:500; }}
        .listing-header-right {{ text-align:right; }}
        .listing-header-right .asking {{ font-size:0.85rem; color:var(--gray); margin-bottom:0.25rem; }}
        .listing-header-right .price {{ font-size:2rem; font-weight:700; color:var(--navy); }}
        .listing-hero {{ position:relative; width:100%; margin-bottom:2.5rem; border-radius:12px; overflow:hidden; }}
        .listing-hero img {{ width:100%; height:500px; object-fit:cover; display:block; cursor:pointer; }}
        .hero-nav {{ position:absolute; top:50%; transform:translateY(-50%); background:rgba(255,255,255,0.85); border:none; cursor:pointer; padding:0.8rem 1rem; border-radius:50%; font-size:1.2rem; color:var(--navy); transition:background 0.3s; }}
        .hero-nav:hover {{ background:white; }}
        .hero-nav-prev {{ left:1rem; }}
        .hero-nav-next {{ right:1rem; }}
        .hero-counter {{ position:absolute; bottom:1rem; right:1rem; background:rgba(0,0,0,0.6); color:white; padding:0.4rem 0.8rem; border-radius:4px; font-size:0.8rem; }}
        .listing-grid {{ display:grid; grid-template-columns:1fr 380px; gap:3rem; }}
        .listing-section-title {{ font-family:'Playfair Display',serif; font-style:italic; font-size:1.5rem; color:var(--navy); margin:2.5rem 0 1rem; padding-bottom:0.5rem; border-bottom:1px solid var(--gray-light, #e0e0e0); }}
        .listing-section-title:first-child {{ margin-top:0; }}
        .listing-description {{ line-height:1.8; color:#444; font-size:0.95rem; }}
        .listing-description p {{ margin-bottom:1rem; }}
        .listing-description h3 {{ font-family:'Playfair Display',serif; font-style:italic; font-size:1.1rem; color:var(--navy); margin:1.5rem 0 0.5rem; }}
        .listing-info-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; }}
        .listing-info-item {{ display:flex; justify-content:space-between; padding:0.75rem 1rem; border-bottom:1px solid #eee; }}
        .listing-info-item .label {{ color:var(--gray); font-size:0.9rem; }}
        .listing-info-item .value {{ color:var(--navy); font-weight:600; font-size:0.9rem; }}
        .listing-features {{ display:flex; flex-wrap:wrap; gap:0.6rem; }}
        .feature-pill {{ border:1.5px solid var(--navy); color:var(--navy); padding:0.4rem 1rem; border-radius:20px; font-size:0.8rem; font-weight:500; }}
        .listing-sidebar {{ position:sticky; top:100px; align-self:start; }}
        .showing-card {{ background:white; border-radius:12px; padding:2rem; box-shadow:0 5px 30px rgba(0,0,0,0.08); border:1px solid #eee; }}
        .showing-card h3 {{ font-family:'Playfair Display',serif; font-style:italic; font-size:1.3rem; color:var(--navy); margin-bottom:0.5rem; }}
        .showing-card .subtitle {{ color:var(--gray); font-size:0.85rem; margin-bottom:1.5rem; }}
        .form-row {{ display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem; }}
        .form-field {{ display:flex; flex-direction:column; }}
        .form-field label {{ font-size:0.75rem; color:var(--gray); margin-bottom:0.3rem; font-weight:500; }}
        .form-field input, .form-field textarea {{ padding:0.7rem; border:1px solid #ddd; border-radius:6px; font-family:'Montserrat',sans-serif; font-size:0.85rem; width:100%; box-sizing:border-box; }}
        .form-field textarea {{ resize:vertical; min-height:80px; }}
        .form-field-full {{ margin-bottom:0.75rem; }}
        .form-field-full label {{ font-size:0.75rem; color:var(--gray); margin-bottom:0.3rem; font-weight:500; display:block; }}
        .form-field-full input, .form-field-full textarea {{ width:100%; padding:0.7rem; border:1px solid #ddd; border-radius:6px; font-family:'Montserrat',sans-serif; font-size:0.85rem; box-sizing:border-box; }}
        .showing-btn {{ width:100%; padding:1rem; background:var(--navy); color:white; border:none; border-radius:6px; font-family:'Montserrat',sans-serif; font-size:0.95rem; font-weight:600; cursor:pointer; margin-top:0.5rem; transition:opacity 0.3s; }}
        .showing-btn:hover {{ opacity:0.9; }}
        .agent-card {{ display:flex; align-items:center; gap:1rem; padding:1.2rem; margin-top:1.5rem; border-top:1px solid #eee; }}
        .agent-photo {{ width:55px; height:55px; min-width:55px; min-height:55px; border-radius:50%; background:var(--navy); display:flex; align-items:center; justify-content:center; color:white; font-size:1.3rem; flex-shrink:0; }}
        .agent-card-info h4 {{ color:var(--navy); font-size:0.95rem; margin-bottom:0.2rem; }}
        .agent-card-info a {{ color:var(--gray); font-size:0.8rem; text-decoration:none; display:block; }}
        .agent-card-info a:hover {{ color:var(--navy); }}
        @media(max-width:1024px) {{ .listing-grid {{ grid-template-columns:1fr; }} .listing-info-grid {{ grid-template-columns:1fr 1fr; }} }}
        @media(max-width:768px) {{ .listing-header {{ flex-direction:column; }} .listing-header-right {{ text-align:left; }} .listing-hero img {{ height:300px; }} .listing-info-grid {{ grid-template-columns:1fr; }} .form-row {{ grid-template-columns:1fr; }} }}
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
    </style>
</head>
<body>
    <nav class="navbar scrolled" id="navbar">
        <a href="../index.html" class="logo">
            <img src="../images/logos/logo-black.png" alt="SXM Dream Investments" class="logo-black">
        </a>
        <ul class="nav-links">
            <li><a href="../index.html">Accueil</a></li>
            <li><a href="../proprietes.html">Propriétés</a></li>
            <li><a href="../saint-martin.html">Saint-Martin</a></li>
            <li><a href="../vendre.html">Vendre</a></li>
            <li><a href="../contact.html" class="nav-cta">Nous contacter</a></li>
        </ul>
    </nav>

    <div class="listing-page">
        <div class="breadcrumb">
            <a href="../proprietes.html"><i class="fas fa-home"></i> À vendre</a>
        </div>

        <div class="listing-header">
            <div class="listing-header-left">
                <h1>{title}</h1>
                <div class="listing-badges">
                    {badges}
                </div>
            </div>
            <div class="listing-header-right">
                <div class="asking">Prix demandé</div>
                <div class="price">{price}</div>
            </div>
        </div>

        <div class="listing-hero">
            <img id="heroImg" src="../images/properties_clean/{img_folder}/01.jpg" alt="{title_escaped}">
            <button class="hero-nav hero-nav-prev" onclick="heroNav(-1)">&#10094;</button>
            <button class="hero-nav hero-nav-next" onclick="heroNav(1)">&#10095;</button>
            <div class="hero-counter"><span id="heroCounter">1</span> / {num_photos}</div>
        </div>

        <div class="listing-grid">
            <div class="listing-main">
                <h2 class="listing-section-title">Description</h2>
                <div class="listing-description">{desc}</div>

                <h2 class="listing-section-title">Informations</h2>
                <div class="listing-info-grid">
                    {info_items}
                </div>
{features_section}
            </div>

            <div class="listing-sidebar">
                <div class="showing-card">
                    <h3>Demander une visite</h3>
                    <p class="subtitle">Contactez directement l'agent responsable</p>
                    <div class="form-row">
                        <div class="form-field">
                            <label>Prénom</label>
                            <input type="text" placeholder="Votre prénom">
                        </div>
                        <div class="form-field">
                            <label>Nom</label>
                            <input type="text" placeholder="Votre nom">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-field">
                            <label>Téléphone</label>
                            <input type="tel" placeholder="+1 (xxx) xxx-xxxx">
                        </div>
                        <div class="form-field">
                            <label>Email</label>
                            <input type="email" placeholder="votre@email.com">
                        </div>
                    </div>
                    <div class="form-field-full">
                        <label>Message</label>
                        <textarea placeholder="Je souhaite en savoir plus sur ce bien..."></textarea>
                    </div>
                    <button class="showing-btn">Demander une visite</button>
                    <div class="agent-card">
                        <div class="agent-photo"><i class="fas fa-user"></i></div>
                        <div class="agent-card-info">
                            <h4>Sacha Mimouni</h4>
                            <a href="mailto:sxm.dream.investments@gmail.com">sxm.dream.investments@gmail.com</a>
                            <a href="tel:+17215237855">+1 (721) 523 7855</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <button class="lightbox-close" onclick="closeLightbox(event)">&times;</button>
        <button class="lightbox-prev" onclick="prevSlide(event)">&#10094;</button>
        <button class="lightbox-next" onclick="nextSlide(event)">&#10095;</button>
        <div class="lightbox-container">
{lightbox_slides}
        </div>
        <div class="lightbox-counter"><span id="lightboxCounter">1</span> / {num_photos}</div>
    </div>

    <footer>
        <div class="footer-grid">
            <div class="footer-brand">
                <a href="../index.html" class="logo"><img src="../images/logos/logo-white.png" alt="SXM Dream Investments"></a>
                <p>Votre partenaire de confiance pour l'immobilier de luxe à Saint-Martin.</p>
            </div>
            <div class="footer-column">
                <h4 class="footer-title">Navigation</h4>
                <ul class="footer-links">
                    <li><a href="../index.html">Accueil</a></li>
                    <li><a href="../proprietes.html">Nos propriétés</a></li>
                    <li><a href="../saint-martin.html">Saint-Martin</a></li>
                    <li><a href="../vendre.html">Vendre votre bien</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h4 class="footer-title">Contact</h4>
                <ul class="footer-links">
                    <li><a href="tel:+17215237855"><i class="fas fa-phone"></i> +1 (721) 523 7855</a></li>
                    <li><a href="mailto:sxm.dream.investments@gmail.com"><i class="fas fa-envelope"></i> sxm.dream.investments@gmail.com</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h4 class="footer-title">Langues</h4>
                <ul class="footer-links">
                    <li><a href="../index.html">Français</a></li>
                    <li><a href="../en/index.html">English</a></li>
                    <li><a href="../nl/index.html">Nederlands</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 SXM Dream Investments. Tous droits réservés.</p>
        </div>
    </footer>
    <script src="../js/main.js"></script>
    <script>
    var nb = document.getElementById('navbar');
    nb.classList.add('scrolled');
    window.addEventListener('scroll', function() {{ nb.classList.add('scrolled'); }});
    (function() {{
        var heroImages = [];
        for (var i = 1; i <= {num_photos}; i++) {{
            heroImages.push('../images/properties_clean/{img_folder}/' + String(i).padStart(2,'0') + '.jpg');
        }}
        var heroIdx = 0;
        window.heroNav = function(dir) {{
            heroIdx = (heroIdx + dir + heroImages.length) % heroImages.length;
            document.getElementById('heroImg').src = heroImages[heroIdx];
            document.getElementById('heroCounter').textContent = heroIdx + 1;
        }};
        document.getElementById('heroImg').addEventListener('click', function() {{ openLightbox(heroIdx); }});
        var lbCurrentSlide = 0;
        var lbSlides = document.querySelectorAll('.lightbox-slide');
        var lbTotal = lbSlides.length;
        function lbShow() {{
            lbSlides.forEach(function(s, i) {{ s.style.display = i === lbCurrentSlide ? 'flex' : 'none'; }});
            document.getElementById('lightboxCounter').textContent = lbCurrentSlide + 1;
        }}
        window.openLightbox = function(idx) {{
            lbCurrentSlide = idx;
            lbShow();
            document.getElementById('lightbox').classList.add('open');
            document.body.style.overflow = 'hidden';
        }};
        window.closeLightbox = function(e) {{
            if (e.target.classList.contains('lightbox') || e.target.classList.contains('lightbox-close')) {{
                document.getElementById('lightbox').classList.remove('open');
                document.body.style.overflow = '';
            }}
        }};
        window.nextSlide = function(e) {{ e.stopPropagation(); lbCurrentSlide = (lbCurrentSlide + 1) % lbTotal; lbShow(); }};
        window.prevSlide = function(e) {{ e.stopPropagation(); lbCurrentSlide = (lbCurrentSlide - 1 + lbTotal) % lbTotal; lbShow(); }};
        document.addEventListener('keydown', function(e) {{
            var lb = document.getElementById('lightbox');
            if (!lb || !lb.classList.contains('open')) return;
            if (e.key === 'Escape') {{ lb.classList.remove('open'); document.body.style.overflow = ''; }}
            if (e.key === 'ArrowRight') {{ lbCurrentSlide = (lbCurrentSlide + 1) % lbTotal; lbShow(); }}
            if (e.key === 'ArrowLeft') {{ lbCurrentSlide = (lbCurrentSlide - 1 + lbTotal) % lbTotal; lbShow(); }}
        }});
        var lbTouchStartX = 0;
        var lbContainer = document.getElementById('lightbox');
        if (lbContainer) {{
            lbContainer.addEventListener('touchstart', function(e) {{ lbTouchStartX = e.touches[0].clientX; }}, {{ passive: true }});
            lbContainer.addEventListener('touchend', function(e) {{
                var dx = e.changedTouches[0].clientX - lbTouchStartX;
                if (Math.abs(dx) > 50) {{
                    if (dx < 0) {{ lbCurrentSlide = (lbCurrentSlide + 1) % lbTotal; }}
                    else {{ lbCurrentSlide = (lbCurrentSlide - 1 + lbTotal) % lbTotal; }}
                    lbShow();
                }}
            }}, {{ passive: true }});
        }}
        if (lbSlides.length > 0) lbShow();
    }})();
    </script>
    <a href="https://wa.me/17215237855" target="_blank" rel="noopener noreferrer" class="whatsapp-float" aria-label="WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
</body>
</html>'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    return True

# Run
files = sorted(glob.glob(os.path.join(BIENS_DIR, '*.html')))
converted = skipped = 0
errors = []
for fp in files:
    fname = os.path.basename(fp)
    if fname in SKIP:
        print(f"  SKIP (already done): {fname}")
        skipped += 1
        continue
    try:
        if convert_page(fp):
            converted += 1
            print(f"  OK: {fname}")
        else:
            skipped += 1
            print(f"  SKIP: {fname}")
    except Exception as e:
        errors.append((fname, str(e)))
        print(f"  ERROR: {fname} - {e}")

print(f"\nDone: {converted} converted, {skipped} skipped, {len(errors)} errors")
for name, err in errors:
    print(f"  - {name}: {err}")

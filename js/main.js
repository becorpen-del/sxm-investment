// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Fade in animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Mobile menu toggle
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });
}

// Property filters
function filterProperties(type) {
    const cards = document.querySelectorAll('.property-card');
    const buttons = document.querySelectorAll('.filter-btn');

    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    cards.forEach(card => {
        if (type === 'all' || card.dataset.type === type) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Location filter
function filterByLocation() {
    const select = document.getElementById('locationFilter');
    const location = select.value;
    const cards = document.querySelectorAll('.property-card');

    cards.forEach(card => {
        if (location === 'all' || card.dataset.location === location) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Price filter
function filterByPrice() {
    const select = document.getElementById('priceFilter');
    const range = select.value;
    const cards = document.querySelectorAll('.property-card');

    cards.forEach(card => {
        const price = parseInt(card.dataset.price);
        let show = true;

        switch(range) {
            case '0-500000':
                show = price < 500000;
                break;
            case '500000-1000000':
                show = price >= 500000 && price < 1000000;
                break;
            case '1000000-2000000':
                show = price >= 1000000 && price < 2000000;
                break;
            case '2000000+':
                show = price >= 2000000;
                break;
            default:
                show = true;
        }

        card.style.display = show ? 'block' : 'none';
    });
}

// Location carousel auto-rotation
const carouselSlides = document.querySelectorAll('.carousel-slide');
const carouselDots = document.querySelectorAll('.carousel-dot');
let currentSlide = 0;

function showSlide(index) {
    carouselSlides.forEach(s => s.classList.remove('active'));
    carouselDots.forEach(d => d.classList.remove('active'));
    carouselSlides[index].classList.add('active');
    carouselDots[index].classList.add('active');
    currentSlide = index;
}

if (carouselSlides.length > 0) {
    setInterval(() => {
        showSlide((currentSlide + 1) % carouselSlides.length);
    }, 3000);

    carouselDots.forEach(dot => {
        dot.addEventListener('click', () => {
            showSlide(parseInt(dot.dataset.index));
        });
    });
}

// Form submission
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Here you would normally send the form data
        alert('Merci pour votre message! Nous vous contacterons bientôt.');
        this.reset();
    });
}

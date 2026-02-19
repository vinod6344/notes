// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
mobileMenuBtn.addEventListener('click', () => {
    const isExpanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
    mobileMenuBtn.setAttribute('aria-expanded', !isExpanded);
    mobileMenu.classList.toggle('hidden');
});

// Smooth Scrolling
function scrollToSection(id) {
    event.preventDefault();
    document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

// Form Submission
document.getElementById('contact-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('/contact', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(result.message);
        e.target.reset();
    } catch (error) {
        alert('An error occurred. Please try again later.');
    }
});

// Active Navigation
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('nav a');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            navLinks.forEach(link => {
                link.classList.remove('active-nav');
                if (link.getAttribute('href').endsWith(`#${entry.target.id}`) || (link.getAttribute('href') === '#home' && entry.target.id === 'home')) {
                    link.classList.add('active-nav');
                }
            });
        }
    });
}, { threshold: 0.5 });
sections.forEach(section => observer.observe(section));
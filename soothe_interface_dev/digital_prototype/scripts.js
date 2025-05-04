
document.addEventListener('DOMContentLoaded', function () {
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add active class to current page in navigation
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation.includes(linkPath) ||
            (currentLocation === '/' && linkPath === 'index.html')) {
            link.classList.add('active');
        }
    });

    // Mobile navigation toggle (can be expanded later if needed)
    // This is a placeholder for future mobile menu implementation

    // Future animations and interactive elements can be added here
});
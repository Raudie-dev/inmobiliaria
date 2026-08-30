// Scroll Progress Bar
document.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    const progressEl = document.getElementById('scroll-progress');
    if(progressEl) progressEl.style.width = scrolled + '%';
});

// GSAP Animations
document.addEventListener("DOMContentLoaded", (event) => {
    // Register ScrollTrigger
    gsap.registerPlugin(ScrollTrigger);

    // Hero Parallax
    gsap.to(".hero-bg", {
        yPercent: 30,
        ease: "none",
        scrollTrigger: {
            trigger: ".hero-section",
            start: "top top",
            end: "bottom top",
            scrub: true
        }
    });

    // Fade Up for cards
    gsap.utils.toArray('.gsap-fade-up').forEach(element => {
        gsap.from(element, {
            y: 50,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out",
            scrollTrigger: {
                trigger: element,
                start: "top 85%", // Triggers when top of element hits 85% of viewport
                toggleActions: "play none none reverse"
            }
        });
    });

    // Stagger for lists or grids
    gsap.utils.toArray('.gsap-stagger-container').forEach(container => {
        gsap.from(container.children, {
            y: 40,
            opacity: 0,
            duration: 0.6,
            stagger: 0.15,
            ease: "power2.out",
            scrollTrigger: {
                trigger: container,
                start: "top 80%",
            }
        });
    });
});
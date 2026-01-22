// Custom Cursor
const cursor = document.querySelector('.cursor');
const follower = document.querySelector('.cursor-follower');
const links = document.querySelectorAll('a, button, .menu-toggle');

document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';

    // Smooth follow effect
    setTimeout(() => {
        follower.style.left = e.clientX + 'px';
        follower.style.top = e.clientY + 'px';
    }, 50);
});

links.forEach(link => {
    link.addEventListener('mouseenter', () => {
        follower.classList.add('cursor-hover');
    });
    link.addEventListener('mouseleave', () => {
        follower.classList.remove('cursor-hover');
    });
});

// Mobile Menu
const menuToggle = document.getElementById('mobile-menu');
const navMenu = document.querySelector('.nav-menu');

menuToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');

    // Hamburger animation
    const bars = document.querySelectorAll('.bar');
    if (navMenu.classList.contains('active')) {
        bars[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
        bars[1].style.opacity = '0';
        bars[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
    } else {
        bars[0].style.transform = 'rotate(0)';
        bars[1].style.opacity = '1';
        bars[2].style.transform = 'rotate(0)';
    }
});

// Close menu when link is clicked
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    navMenu.classList.remove('active');
    const bars = document.querySelectorAll('.bar');
    bars[0].style.transform = 'rotate(0)';
    bars[1].style.opacity = '1';
    bars[2].style.transform = 'rotate(0)';
}));

// Neural Network Canvas Animation
const canvas = document.getElementById('neural-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let particles = [];

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}

window.addEventListener('resize', resize);
resize();

class Particle {
    constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 1; // Velocity X
        this.vy = (Math.random() - 0.5) * 1; // Velocity Y
        this.size = Math.random() * 2 + 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Bounce off edges
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
        ctx.fillStyle = 'rgba(0, 229, 255, 0.4)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    particles = [];
    const particleCount = Math.min(Math.floor(width / 10), 100); // Responsive count
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function animate() {
    ctx.clearRect(0, 0, width, height);

    particles.forEach((p, index) => {
        p.update();
        p.draw();

        // Draw connections
        for (let j = index + 1; j < particles.length; j++) {
            const p2 = particles[j];
            const dx = p.x - p2.x;
            const dy = p.y - p2.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 150) {
                ctx.strokeStyle = `rgba(0, 229, 255, ${1 - distance / 150})`;
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        }
    });

    requestAnimationFrame(animate);
}

initParticles();
animate();

// Glitch Effect for Name
const glitchText = document.querySelector('.glitch-effect');
const originalText = glitchText.getAttribute('data-text');
const chars = '!<>-_\\/[]{}—=+*^?#________';

function startGlitch() {
    let iterations = 0;
    const interval = setInterval(() => {
        glitchText.innerText = glitchText.innerText.split('')
            .map((letter, index) => {
                if (index < iterations) {
                    return originalText[index];
                }
                return chars[Math.floor(Math.random() * chars.length)];
            })
            .join('');

        if (iterations >= originalText.length) {
            clearInterval(interval);
        }

        iterations += 1 / 3;
    }, 30);
}

// Trigger glitch on load and hover
startGlitch();
glitchText.addEventListener('mouseover', startGlitch);

// Scroll Reveal
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            entry.target.style.opacity = 1;
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.section-title, .about-content, .skills-wrapper, .project-card, .contact-wrapper').forEach(el => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

document.addEventListener('DOMContentLoaded', function() {
    createAnimatedBackground();
    initInteractiveBackground();
    initSectionSwitching();
});

function createAnimatedBackground() {
    const bgContainer = document.createElement('div');
    bgContainer.className = 'animated-bg';
    document.body.appendChild(bgContainer);

    // Increase number of floating shapes for more activity
    for (let i = 0; i < 12; i++) {
        createFloatingShape(bgContainer);
    }
    
    // Add continuous generation of new shapes
    setInterval(() => {
        if (document.querySelectorAll('.floating-shape').length < 15) {
            createFloatingShape(bgContainer);
        }
    }, 3000);
}

function createFloatingShape(container) {
    const shape = document.createElement('div');
    shape.className = 'floating-shape';
    
    // Random size between 30px and 80px
    const size = Math.random() * 50 + 30;
    shape.style.width = size + 'px';
    shape.style.height = size + 'px';
    
    // Random position
    shape.style.left = Math.random() * 100 + '%';
    shape.style.top = Math.random() * 100 + '%';
    
    // Random animation duration and delay
    const duration = Math.random() * 4 + 6; // 6-10 seconds
    const delay = Math.random() * 2;
    
    shape.style.animationDuration = duration + 's';
    shape.style.animationDelay = delay + 's';
    
    // Random opacity
    shape.style.opacity = Math.random() * 0.2 + 0.1;
    
    container.appendChild(shape);
    
    // Recreate shape after animation
    setTimeout(() => {
        if (shape.parentNode) {
            shape.parentNode.removeChild(shape);
            createFloatingShape(container);
        }
    }, (duration + delay) * 1000);
}

function initInteractiveBackground() {
    const interactiveShapes = [];
    let lastMouseMove = 0;
    
    // Create mouse follow effect with floating shapes
    document.addEventListener('mousemove', function(e) {
        const now = Date.now();
        
        // Reduced interval to 750ms (0.25 seconds faster than 1 second)
        if (now - lastMouseMove > 750) {
            createInteractiveShape(e.clientX, e.clientY);
            lastMouseMove = now;
        }
        
        // Clean up old shapes
        cleanupShapes();
        
        // Existing floating shapes effect
        const shapes = document.querySelectorAll('.floating-shape');
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        shapes.forEach((shape, index) => {
            const speed = (index + 1) * 0.3;
            const x = (mouseX - 0.5) * speed * 10;
            const y = (mouseY - 0.5) * speed * 10;
            
            shape.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
    
    // Add random shapes generation in background
    setInterval(() => {
        if (interactiveShapes.length < 25) {
            const randomX = Math.random() * window.innerWidth;
            const randomY = Math.random() * window.innerHeight;
            createInteractiveShape(randomX, randomY);
        }
    }, 2000);
    
    function createInteractiveShape(x, y) {
        const shape = document.createElement('div');
        shape.className = 'interactive-floating-shape';
        
        // Same size range as floating shapes: 30px and 80px
        const size = Math.random() * 50 + 30;
        shape.style.width = size + 'px';
        shape.style.height = size + 'px';
        
        // Start from cursor position
        shape.style.left = (x - size/2) + 'px';
        shape.style.top = (y - size/2) + 'px';
        
        // Random direction and distance for floating
        const angle = Math.random() * 2 * Math.PI;
        const distance = Math.random() * 200 + 100;
        const endX = x + Math.cos(angle) * distance;
        const endY = y + Math.sin(angle) * distance;
        
        document.body.appendChild(shape);
        interactiveShapes.push({
            element: shape,
            createdAt: Date.now()
        });
        
        // Animate shape to float away
        setTimeout(() => {
            shape.style.left = (endX - size/2) + 'px';
            shape.style.top = (endY - size/2) + 'px';
            shape.style.opacity = '0';
            shape.style.transform = 'scale(0.5) rotate(180deg)';
        }, 50);
    }
    
    function cleanupShapes() {
        const now = Date.now();
        for (let i = interactiveShapes.length - 1; i >= 0; i--) {
            const shape = interactiveShapes[i];
            if (now - shape.createdAt > 3000) { // Remove shapes older than 3 seconds
                if (shape.element.parentNode) {
                    shape.element.parentNode.removeChild(shape.element);
                }
                interactiveShapes.splice(i, 1);
            }
        }
        
        // Limit number of shapes for performance
        if (interactiveShapes.length > 20) {
            const oldestShape = interactiveShapes.shift();
            if (oldestShape.element.parentNode) {
                oldestShape.element.parentNode.removeChild(oldestShape.element);
            }
        }
    }
}

function initSectionSwitching() {
    const welcomeContainer = document.querySelector('.welcome-container');
    const mainContent = document.querySelector('.main-content');
    const footerBtns = document.querySelectorAll('.footer-btn');
    
    footerBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1); // Remove #
            showSection(target);
        });
    });
    
    function showSection(sectionName) {
        if (sectionName === 'welcome') {
            // Hide any existing content sections immediately
            const existingSections = document.querySelectorAll('.content-section');
            existingSections.forEach(section => {
                section.style.display = 'none';
                section.remove();
            });
            
            // Show main content
            mainContent.style.display = 'flex';
            mainContent.classList.remove('slide-out');
            return;
        }
        
        // Hide main content
        mainContent.classList.add('slide-out');
        
        setTimeout(() => {
            mainContent.style.display = 'none';
            createSectionContent(sectionName);
        }, 300);
    }
    
    function createSectionContent(sectionName) {
        // Remove existing content sections
        const existingSections = document.querySelectorAll('.content-section');
        existingSections.forEach(section => section.remove());
        
        const section = document.createElement('div');
        section.className = 'content-section';
        
        if (sectionName === 'about') {
            section.innerHTML = `
                <div class="about-content">
                    <div class="about-columns">
                        <div class="about-main">
                            <h2>About Aptura</h2>
                            <p>Social media has evolved into a battle for followers and restricted uncreative posts to match search algorithms.</p>
                            <p>Aptura is a platform for photographers or anyone who wants to share their photography work, without the focus on followers, likes, or algorithms that force you to fight for your photos to be seen by others at the expense of posting what truly represents your proudest work.</p>
                            <p>Aptura is all about displaying your photos and getting inspired by other photographer's work too!</p>
                        </div>
                        <div class="about-features">
                            <h2>Latest Features</h2>
                            <p>• Save posts to view later in your personal collection</p>
                            <p>• Find other photographers to stay updated with their work</p>
                            <p>• Get notifications when someone saves your photos or notices you</p>
                            <p>• Upload and organize your photography portfolio with custom albums</p>
                            <p>• Customize your photography profile</p>
                            <p>• Explore the latest posts from the community</p>
                        </div>
                    </div>
                </div>
            `;
        } else if (sectionName === 'contact') {
            section.innerHTML = `
                <div class="contact-content">
                    <h2>Get in Touch</h2>
                    <p>Suggest new features and changes or just reach out to learn more from the links below!</p>
                    <div class="contact-buttons">
                        <a href="mailto:bradleywong99@gmail.com" class="contact-btn">📧 Email Us</a>
                        <a href="https://github.com/bwong99" class="contact-btn" target="_blank">💻 GitHub</a>
                    </div>
                </div>
            `;
        }
        
        // Insert section in place of main-content
        welcomeContainer.insertBefore(section, welcomeContainer.querySelector('.welcome-footer'));
        
        // Trigger animation
        setTimeout(() => {
            section.classList.add('active');
        }, 50);
    }
}
    function hideSection(section) {
        section.classList.add('slide-out');
        
        setTimeout(() => {
            section.remove();
            // Show main content
            mainContent.style.display = 'flex';
            mainContent.classList.remove('slide-out');
        }, 600);
    }

    function hideSection(section) {
        section.classList.add('slide-out');
        
        setTimeout(() => {
            section.remove();
            // Show main content
            mainContent.style.display = 'flex';
            mainContent.classList.remove('slide-out');
        }, 600);
    }


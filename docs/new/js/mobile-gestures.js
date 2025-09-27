/**
 * Mobile Gesture Navigation for AuntieRuth.com
 * Implements swipe navigation, long-press menus, and touch-friendly interactions
 */

class MobileGestureHandler {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.longPressTimer = null;
        this.longPressDelay = 500; // ms
        this.swipeThreshold = 100; // px
        this.isLongPress = false;

        this.init();
    }

    init() {
        if (!this.isTouchDevice()) return;

        this.setupSwipeNavigation();
        this.setupLongPressMenus();
        this.setupTouchFeedback();
        this.setupPinchZoom();

        console.log('Mobile gesture navigation initialized');
    }

    isTouchDevice() {
        return 'ontouchstart' in window ||
               navigator.maxTouchPoints > 0 ||
               window.innerWidth <= 768;
    }

    /**
     * Setup swipe navigation between family members
     */
    setupSwipeNavigation() {
        // Only enable on person pages (XF*.htm)
        if (!window.location.pathname.includes('XF')) return;

        const swipeArea = document.querySelector('.main-content, main');
        if (!swipeArea) return;

        swipeArea.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].clientX;
            this.touchStartY = e.changedTouches[0].clientY;
        }, { passive: true });

        swipeArea.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].clientX;
            this.touchEndY = e.changedTouches[0].clientY;

            this.handleSwipeGesture();
        }, { passive: true });
    }

    handleSwipeGesture() {
        const swipeDistanceX = this.touchEndX - this.touchStartX;
        const swipeDistanceY = this.touchEndY - this.touchStartY;

        // Ensure horizontal swipe (not vertical scroll)
        if (Math.abs(swipeDistanceY) > Math.abs(swipeDistanceX)) return;
        if (Math.abs(swipeDistanceX) < this.swipeThreshold) return;

        if (swipeDistanceX > 0) {
            // Right swipe - go to previous person
            this.navigateToPreviousPerson();
        } else {
            // Left swipe - go to next person
            this.navigateToNextPerson();
        }
    }

    navigateToPreviousPerson() {
        const familyNav = document.querySelector('.family-navigation');
        if (!familyNav) return;

        // Look for parent or spouse links
        const parentLink = familyNav.querySelector('a[href*="XF"]:first-child');
        if (parentLink) {
            this.showSwipeFeedback('Previous: ' + parentLink.textContent);
            setTimeout(() => window.location.href = parentLink.href, 300);
        }
    }

    navigateToNextPerson() {
        const familyNav = document.querySelector('.family-navigation');
        if (!familyNav) return;

        // Look for child or spouse links
        const childLink = familyNav.querySelector('a[href*="XF"]:last-child');
        if (childLink) {
            this.showSwipeFeedback('Next: ' + childLink.textContent);
            setTimeout(() => window.location.href = childLink.href, 300);
        }
    }

    /**
     * Setup long-press context menus for quick actions
     */
    setupLongPressMenus() {
        document.addEventListener('touchstart', (e) => {
            // Check if target is a person link
            const personLink = e.target.closest('a[href*="XF"]');
            if (!personLink) return;

            this.isLongPress = false;
            this.longPressTimer = setTimeout(() => {
                this.isLongPress = true;
                this.showContextMenu(personLink, e.touches[0]);

                // Haptic feedback if available
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            }, this.longPressDelay);
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (this.longPressTimer) {
                clearTimeout(this.longPressTimer);
            }
        }, { passive: true });

        document.addEventListener('touchmove', () => {
            if (this.longPressTimer) {
                clearTimeout(this.longPressTimer);
            }
        }, { passive: true });
    }

    showContextMenu(personLink, touch) {
        const existingMenu = document.querySelector('.mobile-context-menu');
        if (existingMenu) existingMenu.remove();

        const menu = document.createElement('div');
        menu.className = 'mobile-context-menu';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="open">
                Open ${this.getPersonName(personLink)}
            </div>
            <div class="context-menu-item" data-action="photos">
                View Photos
            </div>
            <div class="context-menu-item" data-action="family">
                Family Tree
            </div>
        `;

        // Position menu
        menu.style.left = touch.clientX + 'px';
        menu.style.top = touch.clientY + 'px';

        document.body.appendChild(menu);

        // Auto-hide after 3 seconds
        setTimeout(() => menu.remove(), 3000);

        // Handle menu actions
        menu.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action === 'open') {
                window.location.href = personLink.href;
            } else if (action === 'photos') {
                const photoUrl = personLink.href.replace('XF', 'THF');
                window.location.href = photoUrl;
            }
            menu.remove();
        });
    }

    /**
     * Setup visual touch feedback
     */
    setupTouchFeedback() {
        document.addEventListener('touchstart', (e) => {
            const target = e.target.closest('a, button, [role="button"]');
            if (!target) return;

            target.classList.add('touch-active');

            // Remove feedback after touch ends
            const removeFeedback = () => {
                target.classList.remove('touch-active');
                target.removeEventListener('touchend', removeFeedback);
                target.removeEventListener('touchcancel', removeFeedback);
            };

            target.addEventListener('touchend', removeFeedback, { passive: true });
            target.addEventListener('touchcancel', removeFeedback, { passive: true });
        }, { passive: true });
    }

    /**
     * Setup pinch-to-zoom for images
     */
    setupPinchZoom() {
        const images = document.querySelectorAll('#right img, #singleImage img');

        images.forEach(img => {
            let scale = 1;
            let isPinching = false;
            let initialDistance = 0;

            img.addEventListener('touchstart', (e) => {
                if (e.touches.length === 2) {
                    isPinching = true;
                    initialDistance = this.getDistance(e.touches[0], e.touches[1]);
                }
            }, { passive: true });

            img.addEventListener('touchmove', (e) => {
                if (isPinching && e.touches.length === 2) {
                    e.preventDefault();
                    const currentDistance = this.getDistance(e.touches[0], e.touches[1]);
                    const scaleChange = currentDistance / initialDistance;
                    scale = Math.min(Math.max(scaleChange, 0.5), 3);

                    img.style.transform = `scale(${scale})`;
                    img.style.transition = 'none';
                }
            });

            img.addEventListener('touchend', () => {
                isPinching = false;
                img.style.transition = 'transform 0.3s ease';

                // Reset if scale is too small
                if (scale < 0.8) {
                    scale = 1;
                    img.style.transform = 'scale(1)';
                }
            });
        });
    }

    // Utility methods
    getDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    getPersonName(link) {
        return link.textContent.replace(/\[.*?\]/g, '').trim() || 'Person';
    }

    showSwipeFeedback(message) {
        const feedback = document.createElement('div');
        feedback.className = 'swipe-feedback';
        feedback.textContent = message;

        document.body.appendChild(feedback);

        setTimeout(() => {
            feedback.classList.add('fade-out');
            setTimeout(() => feedback.remove(), 300);
        }, 1500);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth <= 768 || 'ontouchstart' in window) {
        new MobileGestureHandler();
    }
});

window.MobileGestureHandler = MobileGestureHandler;
/* HomifyHub - Centralized JavaScript Functions */

/**
 * =====================================================
 * HOMIFYHUB NAMESPACE
 * =====================================================
 */
window.HomifyHub = window.HomifyHub || {};

/**
 * =====================================================
 * UTILITY FUNCTIONS
 * =====================================================
 */

// Toggle password visibility
HomifyHub.togglePassword = function(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
};

// Toggle mobile menu
HomifyHub.toggleMobileMenu = function() {
    const mobileMenu = document.getElementById('mobile-menu');
    const hamburger = document.querySelector('.hamburger-menu i');
    
    if (mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.remove('hidden');
        hamburger.className = 'fas fa-times text-xl';
    } else {
        mobileMenu.classList.add('hidden');
        hamburger.className = 'fas fa-bars text-xl';
    }
};

// Toast Notification System
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fixed top-4 right-4 z-50 transform translate-x-full transition-all duration-300`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="flex items-center p-4 rounded-xl shadow-lg backdrop-blur-sm">
            <i class="${icons[type]} mr-3 text-lg"></i>
            <span class="flex-1 font-medium">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-3 hover:bg-white/20 rounded-full p-1 transition-colors">
                <i class="fas fa-times text-sm"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.remove('translate-x-full'), 100);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    return toast;
}

// Convenience methods for different toast types
function showSuccess(message, duration = 3000) {
    return showToast(message, 'success', duration);
}

function showError(message, duration = 5000) {
    return showToast(message, 'error', duration);
}

function showWarning(message, duration = 4000) {
    return showToast(message, 'warning', duration);
}

function showInfo(message, duration = 3000) {
    return showToast(message, 'info', duration);
}

// Legacy support
const showNotification = showToast;

/**
 * =====================================================
 * CART AND WISHLIST FUNCTIONS
 * =====================================================
 */

// Add to cart with AJAX
function addToCart(productSlug, quantity = 1) {
    // Show loading toast
    const loadingToast = showInfo('Adding to cart...', 0);
    
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
    
    fetch(`/carts/add/${productSlug}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingToast.remove();
        if (data.success) {
            showSuccess(data.message || 'Added to cart successfully!');
            updateCartBadge();
        } else {
            showError(data.message || 'Failed to add to cart');
        }
    })
    .catch(error => {
        loadingToast.remove();
        console.error('Error:', error);
        showError('Something went wrong. Please try again.');
    });
}

// Add to wishlist (only for authenticated users)
function addToWishlist(productSlug) {
    // Check if user is authenticated
    if (!document.body.dataset.userAuthenticated) {
        showWarning('Please login to add items to wishlist');
        return;
    }
    
    const loadingToast = showInfo('Adding to wishlist...', 0);
    
    fetch(`/carts/wishlist/add/${productSlug}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingToast.remove();
        if (data.success) {
            showSuccess(data.message || 'Added to wishlist!');
            updateWishlistBadge();
        } else {
            showError(data.message || 'Failed to add to wishlist');
        }
    })
    .catch(error => {
        loadingToast.remove();
        console.error('Error:', error);
        showError('Something went wrong. Please try again.');
    });
}

// Remove from cart
function removeFromCart(itemId) {
    const loadingToast = showInfo('Removing from cart...', 0);
    
    fetch(`/carts/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingToast.remove();
        if (data.success) {
            showSuccess(data.message || 'Removed from cart');
            location.reload(); // Refresh to update cart
        } else {
            showError(data.message || 'Failed to remove from cart');
        }
    })
    .catch(error => {
        loadingToast.remove();
        console.error('Error:', error);
        showError('Something went wrong. Please try again.');
    });
}

// Update cart badge count
function updateCartBadge() {
    fetch('/carts/count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartBadges = document.querySelectorAll('.cart-count');
        cartBadges.forEach(badge => {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    })
    .catch(error => console.error('Error updating cart badge:', error));
}

// Update wishlist badge count (only for authenticated users)
function updateWishlistBadge() {
    if (!document.body.dataset.userAuthenticated) return;
    
    fetch('/carts/wishlist/count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        const wishlistBadges = document.querySelectorAll('.wishlist-count');
        wishlistBadges.forEach(badge => {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    })
    .catch(error => console.error('Error updating wishlist badge:', error));
}

// Show badges only if they have items
function showBadgesIfNotEmpty() {
    updateCartBadge();
    if (document.body.dataset.userAuthenticated) {
        updateWishlistBadge();
    }
}

// Toggle password visibility
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        button.setAttribute('aria-label', 'Hide password');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        button.setAttribute('aria-label', 'Show password');
    }
}

// Quantity controls
function changeQuantity(input, delta) {
    const currentValue = parseInt(input.value) || 1;
    const newValue = Math.max(1, currentValue + delta);
    const maxValue = parseInt(input.getAttribute('max')) || 999;
    
    input.value = Math.min(newValue, maxValue);
    input.dispatchEvent(new Event('change'));
}

// Setup quantity controls
function setupQuantityControls() {
    document.querySelectorAll('.quantity-input').forEach(input => {
        const container = input.parentElement;
        
        // Create minus button
        const minusBtn = document.createElement('button');
        minusBtn.type = 'button';
        minusBtn.className = 'btn btn-secondary btn-sm px-2 py-1 rounded-l-xl border-r-0';
        minusBtn.innerHTML = '<i class="fas fa-minus"></i>';
        minusBtn.onclick = () => changeQuantity(input, -1);
        
        // Create plus button
        const plusBtn = document.createElement('button');
        plusBtn.type = 'button';
        plusBtn.className = 'btn btn-secondary btn-sm px-2 py-1 rounded-r-xl border-l-0';
        plusBtn.innerHTML = '<i class="fas fa-plus"></i>';
        plusBtn.onclick = () => changeQuantity(input, 1);
        
        // Style the input
        input.className = 'input-field text-center border-l-0 border-r-0 rounded-none w-16';
        
        // Wrap in flex container
        const wrapper = document.createElement('div');
        wrapper.className = 'flex items-center';
        
        container.insertBefore(wrapper, input);
        wrapper.appendChild(minusBtn);
        wrapper.appendChild(input);
        wrapper.appendChild(plusBtn);
    });
}

/**
 * =====================================================
 * CART & WISHLIST MANAGEMENT
 * =====================================================
 */

// Update cart badge visibility and count
function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-count');
    badges.forEach(badge => {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// Update wishlist badge visibility and count
function updateWishlistBadge(count) {
    const badges = document.querySelectorAll('.wishlist-count');
    badges.forEach(badge => {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// Initialize badge visibility on page load
function initializeBadges() {
    // Get cart count from data attribute or DOM
    const cartCountElement = document.querySelector('.cart-count');
    const wishlistCountElement = document.querySelector('.wishlist-count');
    
    if (cartCountElement) {
        const cartCount = parseInt(cartCountElement.textContent) || 0;
        updateCartBadge(cartCount);
    }
    
    if (wishlistCountElement) {
        const wishlistCount = parseInt(wishlistCountElement.textContent) || 0;
        updateWishlistBadge(wishlistCount);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', initializeBadges);

/**
 * =====================================================
 * QUANTITY CONTROLS
 * =====================================================
 */

// Initialize quantity controls
function initializeQuantityControls() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(container => {
        const minusBtn = container.querySelector('.quantity-minus');
        const plusBtn = container.querySelector('.quantity-plus');
        const input = container.querySelector('.quantity-value');
        
        if (minusBtn && plusBtn && input) {
            const min = parseInt(input.getAttribute('min')) || 1;
            const max = parseInt(input.getAttribute('max')) || 99;
            
            minusBtn.addEventListener('click', () => {
                let currentValue = parseInt(input.value) || min;
                if (currentValue > min) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            plusBtn.addEventListener('click', () => {
                let currentValue = parseInt(input.value) || min;
                if (currentValue < max) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            // Ensure input value is within bounds
            input.addEventListener('blur', () => {
                let value = parseInt(input.value) || min;
                if (value < min) value = min;
                if (value > max) value = max;
                input.value = value;
            });
        }
    });
}

// Add to page load initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeBadges();
    initializeQuantityControls();
    initializeLazyLoading();
});

/**
 * =====================================================
 * NOTIFICATION SYSTEM
 * =====================================================
 */

// Show toast notification
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 max-w-sm w-full transition-all duration-300 transform translate-x-full`;
    
    const typeClasses = {
        success: 'bg-green-500 text-white border-green-600',
        error: 'bg-red-500 text-white border-red-600',
        warning: 'bg-yellow-500 text-white border-yellow-600',
        info: 'bg-blue-500 text-white border-blue-600'
    };
    
    const typeIcons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="flex items-center p-4 rounded-xl shadow-xl border-l-4 backdrop-blur-sm ${typeClasses[type] || typeClasses.info}">
            <i class="${typeIcons[type] || typeIcons.info} mr-3 text-lg"></i>
            <span class="flex-1 font-medium">${message}</span>
            <button onclick="hideToast(this.parentElement.parentElement)" class="ml-3 text-white hover:text-gray-200 transition-colors duration-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Slide in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto hide
    if (duration > 0) {
        setTimeout(() => {
            hideToast(toast);
        }, duration);
    }
    
    return toast;
}

// Hide toast notification
function hideToast(toast) {
    if (toast) {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// Convenience methods for different types
function showSuccess(message, duration = 3000) {
    return showToast(message, 'success', duration);
}

function showError(message, duration = 4000) {
    return showToast(message, 'error', duration);
}

function showWarning(message, duration = 3500) {
    return showToast(message, 'warning', duration);
}

function showInfo(message, duration = 3000) {
    return showToast(message, 'info', duration);
}

/**
 * =====================================================
 * LAZY LOADING FUNCTIONALITY
 * =====================================================
 */

// Initialize lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('.lazy-image');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src;
                    
                    if (src) {
                        img.src = src;
                        img.classList.add('loaded');
                        img.classList.remove('lazy-image');
                        observer.unobserve(img);
                    }
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                img.classList.add('loaded');
                img.classList.remove('lazy-image');
            }
        });
    }
}

/**
 * =====================================================
 * PRODUCT INTERACTIONS
 * =====================================================
 */

// Handle add to cart action
function addToCart(productId, quantity = 1, variantId = null) {
    const data = {
        product_id: productId,
        quantity: quantity,
        variant_id: variantId
    };
    
    fetch('/carts/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(data.message || 'Added to cart successfully!');
            updateCartBadge(data.cart_count || 0);
        } else {
            showError(data.message || 'Failed to add to cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('An error occurred while adding to cart');
    });
}

// Handle add to wishlist action
function addToWishlist(productId) {
    fetch('/carts/wishlist/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(data.message || 'Added to wishlist!');
            updateWishlistBadge(data.wishlist_count || 0);
        } else {
            showError(data.message || 'Failed to add to wishlist');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('An error occurred while adding to wishlist');
    });
}

// Get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.content || '';
}

// Add to cart with animation
function addToCart(productSlug, quantity = 1) {
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Adding...';
    button.disabled = true;
    
    fetch(`/cart/add/${productSlug}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Product added to cart!', 'success');
            updateCartCount(data.cart_count);
            animateCartIcon();
        } else {
            showNotification(data.message || 'Failed to add to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Something went wrong', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Remove from cart
function removeFromCart(productSlug) {
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }
    
    fetch(`/cart/remove/${productSlug}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item removed from cart', 'success');
            updateCartCount(data.cart_count);
            
            // Remove item from DOM with animation
            const itemElement = document.querySelector(`[data-product-slug="${productSlug}"]`);
            if (itemElement) {
                itemElement.style.transition = 'all 0.3s ease';
                itemElement.style.transform = 'translateX(-100%)';
                itemElement.style.opacity = '0';
                setTimeout(() => {
                    itemElement.remove();
                    updateCartTotal();
                }, 300);
            }
        } else {
            showNotification(data.message || 'Failed to remove item', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Something went wrong', 'error');
    });
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartBadge = document.querySelector('.cart-count');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// Animate cart icon
function animateCartIcon() {
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.classList.add('animate-bounce');
        setTimeout(() => {
            cartIcon.classList.remove('animate-bounce');
        }, 1000);
    }
}

/**
 * =====================================================
 * WISHLIST FUNCTIONS
 * =====================================================
 */

// Toggle wishlist
function toggleWishlist(productSlug) {
    const button = event.target.closest('button');
    const icon = button.querySelector('i');
    const isInWishlist = icon.classList.contains('fas');
    
    fetch(`/wishlist/${isInWishlist ? 'remove' : 'add'}/${productSlug}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (isInWishlist) {
                icon.classList.remove('fas');
                icon.classList.add('far');
                button.classList.remove('text-red-500');
                button.classList.add('text-gray-400');
                showNotification('Removed from wishlist', 'info');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
                button.classList.remove('text-gray-400');
                button.classList.add('text-red-500');
                showNotification('Added to wishlist', 'success');
            }
            updateWishlistCount(data.wishlist_count);
        } else {
            showNotification(data.message || 'Failed to update wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Something went wrong', 'error');
    });
}

// Update wishlist count
function updateWishlistCount(count) {
    const wishlistBadge = document.querySelector('.wishlist-count');
    if (wishlistBadge) {
        wishlistBadge.textContent = count;
        wishlistBadge.style.display = count > 0 ? 'flex' : 'none';
    }
}

/**
 * =====================================================
 * MODAL FUNCTIONS
 * =====================================================
 */

// Show modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        
        // Animate in
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.classList.add('animate-scale-in');
        }
    }
}

// Hide modal
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.9)';
            modalContent.style.opacity = '0';
        }
        
        setTimeout(() => {
            modal.classList.remove('flex');
            modal.classList.add('hidden');
            document.body.style.overflow = '';
            
            if (modalContent) {
                modalContent.style.transform = '';
                modalContent.style.opacity = '';
            }
        }, 200);
    }
}

// Setup modal event listeners
function setupModals() {
    // Close modal when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal(modal.id);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const visibleModal = document.querySelector('.modal.flex');
            if (visibleModal) {
                hideModal(visibleModal.id);
            }
        }
    });
}

/**
 * =====================================================
 * IMAGE FUNCTIONS
 * =====================================================
 */

// Lazy load images
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Product image gallery
function setupImageGallery() {
    const thumbnails = document.querySelectorAll('.image-thumbnail');
    const mainImage = document.querySelector('.main-product-image');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            const newSrc = thumb.dataset.fullImage || thumb.src;
            if (mainImage) {
                mainImage.style.opacity = '0';
                setTimeout(() => {
                    mainImage.src = newSrc;
                    mainImage.style.opacity = '1';
                }, 150);
            }
            
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('ring-2', 'ring-blue-500'));
            thumb.classList.add('ring-2', 'ring-blue-500');
        });
    });
}

/**
 * =====================================================
 * FORM FUNCTIONS
 * =====================================================
 */

// Form validation
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('input-field-error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i>${message}`;
    
    field.parentElement.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('input-field-error');
    const existingError = field.parentElement.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * =====================================================
 * NAVIGATION FUNCTIONS
 * =====================================================
 */

// Mobile menu toggle
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const hamburger = document.querySelector('.hamburger-menu');
    
    if (mobileMenu && hamburger) {
        const isOpen = !mobileMenu.classList.contains('hidden');
        
        if (isOpen) {
            mobileMenu.classList.add('hidden');
            hamburger.innerHTML = '<i class="fas fa-bars"></i>';
        } else {
            mobileMenu.classList.remove('hidden');
            hamburger.innerHTML = '<i class="fas fa-times"></i>';
        }
    }
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * =====================================================
 * UTILITY FUNCTIONS
 * =====================================================
 */

// Get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update cart total
function updateCartTotal() {
    const cartItems = document.querySelectorAll('.cart-item');
    let total = 0;
    
    cartItems.forEach(item => {
        const price = parseFloat(item.dataset.price || 0);
        const quantity = parseInt(item.querySelector('.quantity-input')?.value || 0);
        total += price * quantity;
    });
    
    const totalElement = document.querySelector('.cart-total');
    if (totalElement) {
        totalElement.textContent = formatCurrency(total);
    }
}

/**
 * =====================================================
 * INITIALIZATION
 * =====================================================
 */

// Initialize all functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupLazyLoading();
    setupImageGallery();
    setupQuantityControls();
    setupModals();
    
    // Setup form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
    
    // Setup smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
        });
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.transition = 'all 0.3s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
    
    console.log('HomifyHub JavaScript initialized successfully!');
});

// Export functions for use in other scripts
window.HomifyHub = {
    showNotification,
    hideNotification,
    togglePassword,
    addToCart,
    removeFromCart,
    toggleWishlist,
    showModal,
    hideModal,
    toggleMobileMenu,
    scrollToSection,
    formatCurrency,
    validateForm,
    
    // Toast functions (aliases for consistency)
    showToast: showNotification,
    showSuccess: function(message, duration = 5000) {
        showNotification(message, 'success', duration);
    },
    showError: function(message, duration = 5000) {
        showNotification(message, 'error', duration);
    },
    showWarning: function(message, duration = 5000) {
        showNotification(message, 'warning', duration);
    },
    showInfo: function(message, duration = 5000) {
        showNotification(message, 'info', duration);
    },

    // Cart/Wishlist functions with authentication detection
    addToCart: function(productSlug) {
        const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
        
        if (!isAuthenticated) {
            this.showError('Please login to add items to cart');
            return;
        }

        const loadingToast = this.showInfo('Adding to cart...', 0);
        
        fetch(`/carts/add/${productSlug}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        })
        .then(response => response.json())
        .then(data => {
            loadingToast.remove();
            if (data.success) {
                this.showSuccess(data.message || 'Added to cart!');
                this.updateCartBadge();
            } else {
                this.showError(data.message || 'Failed to add to cart');
            }
        })
        .catch(error => {
            loadingToast.remove();
            console.error('Error:', error);
            this.showError('Something went wrong. Please try again.');
        });
    },

    addToWishlist: function(productSlug) {
        const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
        
        if (!isAuthenticated) {
            this.showError('Please login to add items to wishlist');
            return;
        }

        const loadingToast = this.showInfo('Adding to wishlist...', 0);
        
        fetch(`/carts/wishlist/add/${productSlug}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        })
        .then(response => response.json())
        .then(data => {
            loadingToast.remove();
            if (data.success) {
                this.showSuccess(data.message || 'Added to wishlist!');
                this.updateWishlistBadge();
            } else {
                this.showError(data.message || 'Failed to add to wishlist');
            }
        })
        .catch(error => {
            loadingToast.remove();
            console.error('Error:', error);
            this.showError('Something went wrong. Please try again.');
        });
    },

    // Update cart badge count
    updateCartBadge: function(count) {
        const badge = document.querySelector('.cart-badge, .cart-count');
        if (badge) {
            badge.textContent = count || '0';
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    },

    // Update wishlist badge count
    updateWishlistBadge: function(count) {
        const badge = document.querySelector('.wishlist-badge, .wishlist-count');
        if (badge) {
            badge.textContent = count || '0';
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    },

    // Initialize lazy loading for images
    initializeLazyLoading: function() {
        const lazyImages = document.querySelectorAll('img[loading="lazy"], .lazy-load');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.remove('lazy-load');
                        observer.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            lazyImages.forEach(img => {
                img.classList.remove('lazy-load');
            });
        }
    }
};

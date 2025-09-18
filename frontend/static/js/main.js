/**
 * AI Productivity Platform - Main JavaScript
 * Organized structure with modular components
 */

// Application Configuration
const AppConfig = {
    API_BASE_URL: '/api',
    NOTIFICATION_REFRESH_INTERVAL: 30000,
    AUTO_SAVE_INTERVAL: 30000,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

// Application State Management
const AppState = {
    notifications: [],
    currentUser: null,
    aiQuota: null,
    lastNotificationCheck: null
};

// Core Utilities
const Utils = {
    // Get CSRF token from cookies
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Format date for display
    formatDate(dateString, options = {}) {
        const date = new Date(dateString);
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
    },

    // Debounce function
    debounce(func, wait) {
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
};

// API Service
const ApiService = {
    async request(url, options = {}, retries = AppConfig.MAX_RETRIES) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Utils.getCookie('csrftoken')
            }
        };

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, finalOptions);

            if (response.status === 429) {
                UI.showToast('Rate limit exceeded. Please wait a moment.', 'warning');
                throw new Error('Rate limited');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (retries > 0 && !error.message.includes('Rate limited')) {
                await new Promise(resolve => setTimeout(resolve, AppConfig.RETRY_DELAY));
                return this.request(url, options, retries - 1);
            }
            throw error;
        }
    }
};

// UI Components
const UI = {
    showToast(message, type = 'info', duration = 5000) {
        // Remove existing toasts
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast show bg-${type} text-white`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-header bg-${type} text-white border-0">
                <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                <strong class="me-auto">AI Productivity Platform</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto-hide after duration
        setTimeout(() => {
            if (toast && toast.parentNode) {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (toast && toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            }
        }, duration);
    },

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'danger': 'times-circle'
        };
        return icons[type] || 'info-circle';
    },

    showLoading(message = 'Loading...') {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner"></div>
                    <p class="mt-3">${message}</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    },

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
};

// Notification Management
const NotificationManager = {
    async loadNotifications() {
        try {
            const data = await ApiService.request('/api/core/notifications/');
            AppState.notifications = data;
            this.updateNotificationUI();
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    },

    updateNotificationUI() {
        const notificationList = document.getElementById('notification-list');
        const notificationCount = document.getElementById('notification-count');

        if (!notificationList || !notificationCount) {
            return;
        }

        const unreadCount = AppState.notifications.filter(n => !n.is_read).length;

        // Update count badge
        if (unreadCount > 0) {
            notificationCount.textContent = unreadCount > 99 ? '99+' : unreadCount;
            notificationCount.style.display = 'block';
        } else {
            notificationCount.style.display = 'none';
        }

        // Update notification list
        if (AppState.notifications.length === 0) {
            notificationList.innerHTML = '<li><span class="dropdown-item-text text-muted">No notifications</span></li>';
            return;
        }

        notificationList.innerHTML = AppState.notifications.slice(0, 5).map(notification => `
            <li>
                <div class="dropdown-item notification-item ${!notification.is_read ? 'notification-unread' : ''} type-${notification.notification_type}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 fw-bold">${notification.title}</h6>
                            <p class="mb-1 small">${notification.message}</p>
                            <small class="text-muted">${Utils.formatDate(notification.created_at)}</small>
                        </div>
                        <div class="d-flex flex-column gap-1">
                            ${!notification.is_read ? `
                                <button class="btn btn-sm btn-outline-primary" onclick="NotificationManager.markAsRead(${notification.id})" title="Mark as read">
                                    <i class="fas fa-check"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-sm btn-outline-secondary" onclick="NotificationManager.dismiss(${notification.id})" title="Dismiss">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </li>
        `).join('');
    },

    async markAsRead(notificationId) {
        try {
            await ApiService.request(`/api/core/notifications/${notificationId}/read/`, {
                method: 'POST'
            });

            // Update local state
            const notification = AppState.notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.is_read = true;
            }

            this.updateNotificationUI();
        } catch (error) {
            console.error('Error marking notification as read:', error);
            UI.showToast('Failed to mark notification as read', 'error');
        }
    },

    async dismiss(notificationId) {
        try {
            await ApiService.request(`/api/core/notifications/${notificationId}/dismiss/`, {
                method: 'POST'
            });

            // Remove from local state
            AppState.notifications = AppState.notifications.filter(n => n.id !== notificationId);
            this.updateNotificationUI();
        } catch (error) {
            console.error('Error dismissing notification:', error);
            UI.showToast('Failed to dismiss notification', 'error');
        }
    }
};

// Global Event Handlers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize notifications if user is authenticated
    if (document.body.dataset.userAuthenticated === 'true') {
        NotificationManager.loadNotifications();
        // Refresh notifications every 30 seconds
        setInterval(() => NotificationManager.loadNotifications(), AppConfig.NOTIFICATION_REFRESH_INTERVAL);
    }

    // Setup keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Implementation for quick search
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    console.log('AI Productivity Platform initialized');
});

// Export for global use
window.AppConfig = AppConfig;
window.AppState = AppState;
window.Utils = Utils;
window.ApiService = ApiService;
window.UI = UI;
window.NotificationManager = NotificationManager;
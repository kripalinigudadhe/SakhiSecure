// Women Safety Analytics - Main JavaScript

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('nav')) {
            navMenu?.classList.remove('active');
        }
    });
    
    // Emergency Button Alert
    const emergencyBtn = document.querySelector('.emergency-btn');
    if (emergencyBtn) {
        emergencyBtn.addEventListener('click', function() {
            if (confirm('Are you in immediate danger? This will alert emergency services.')) {
                alert('Emergency services have been notified! Help is on the way.');
                // In real application, this would trigger actual emergency protocols
            }
        });
    }
    
    // Form Validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = '#e0e0e0';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                showAlert('Please fill in all required fields', 'danger');
            }
        });
    });
    
    // Initialize dashboard if on dashboard page
    if (window.location.pathname.includes('dashboard')) {
        initializeDashboard();
    }
    
    // Initialize analytics if on analytics page
    if (window.location.pathname.includes('analytics')) {
        initializeAnalytics();
    }
});

// Alert System
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Dashboard Initialization
function initializeDashboard() {
    // Simulate real-time updates
    updateDashboardStats();
    setInterval(updateDashboardStats, 30000); // Update every 30 seconds
    
    // Initialize map (placeholder)
    initializeMap();
}

function updateDashboardStats() {
    const stats = [
        { id: 'active-alerts', value: Math.floor(Math.random() * 10) + 5 },
        { id: 'safe-zones', value: Math.floor(Math.random() * 50) + 100 },
        { id: 'reports-today', value: Math.floor(Math.random() * 20) + 10 },
        { id: 'response-time', value: Math.floor(Math.random() * 3) + 2 }
    ];
    
    stats.forEach(stat => {
        const element = document.getElementById(stat.id);
        if (element) {
            element.textContent = stat.value + (stat.id === 'response-time' ? ' min' : '');
        }
    });
}

function initializeMap() {
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div style="text-align: center;">
                <h3 style="color: var(--primary-pink); margin-bottom: 1rem;">Live Safety Map</h3>
                <p>Interactive map with real-time safety alerts would be displayed here</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">
                    🟢 Safe Zones &nbsp;&nbsp; 🟡 Caution Areas &nbsp;&nbsp; 🔴 Alert Zones
                </p>
            </div>
        `;
    }
}

// Analytics Initialization
function initializeAnalytics() {
    // Create sample charts (in real app, would use Chart.js or similar)
    createSampleCharts();
}

function createSampleCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        container.innerHTML = `
            <div style="height: 200px; background: linear-gradient(45deg, var(--soft-pink), var(--light-pink)); 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                <p>Interactive Chart Would Display Here</p>
            </div>
        `;
    });
}

// Incident Reporting
function submitIncident(formData) {
    // Show loading
    const submitBtn = document.querySelector('form button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        submitBtn.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            
            // Redirect to thank you page
            window.location.href = '/thank-you.html';
        }, 2000);
    }
}

// Geolocation Helper
function getCurrentLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const location = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                callback(location);
            },
            error => {
                console.error('Error getting location:', error);
                showAlert('Unable to get your location. Please enable location services.', 'warning');
            }
        );
    } else {
        showAlert('Geolocation is not supported by this browser.', 'danger');
    }
}

// Search Functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const targetSelector = e.target.dataset.search;
            const items = document.querySelectorAll(targetSelector);
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

// Initialize search when page loads
document.addEventListener('DOMContentLoaded', initializeSearch);

// Utility function to format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Theme toggle (if needed)
function toggleTheme() {
    // Could implement dark/light theme toggle here
    console.log('Theme toggle functionality can be added here');
}
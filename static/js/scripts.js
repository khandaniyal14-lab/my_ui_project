// Main JavaScript file for My UI Project

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('My UI Project loaded successfully!');
    
    // Initialize page-specific functionality
    initializePage();
});

// Initialize functionality based on current page
function initializePage() {
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
        case 'login.html':
            initializeLoginPage();
            break;
        case 'dashboard.html':
            initializeDashboard();
            break;
        case 'index.html':
        case '':
            initializeHomePage();
            break;
        default:
            console.log('Page initialized:', currentPage);
    }
}

// Home page functionality
function initializeHomePage() {
    console.log('Home page initialized');
    
    // Add smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Login page functionality
function initializeLoginPage() {
    console.log('Login page initialized');
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Add input validation
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidationError);
    });
}

// Handle login form submission
function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember') ? document.getElementById('remember').checked : false;
    
    // Basic validation
    if (!email || !password) {
        showMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    if (!isValidEmail(email)) {
        showMessage('Please enter a valid email address.', 'error');
        return;
    }
    
    // Simulate login process
    showMessage('Logging in...', 'info');
    
    // Simulate API call delay
    setTimeout(() => {
        // For demo purposes, accept any email/password combination
        if (email && password) {
            showMessage('Login successful! Redirecting...', 'success');
            
            // Store user session (for demo)
            if (remember) {
                localStorage.setItem('userEmail', email);
            } else {
                sessionStorage.setItem('userEmail', email);
            }
            
            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showMessage('Invalid credentials. Please try again.', 'error');
        }
    }, 1000);
}

// Dashboard functionality
function initializeDashboard() {
    console.log('Dashboard initialized');
    
    // Check if user is logged in
    const userEmail = localStorage.getItem('userEmail') || sessionStorage.getItem('userEmail');
    if (!userEmail) {
        // Redirect to login if not authenticated
        window.location.href = 'login.html';
        return;
    }
    
    // Update user name display
    const userNameElement = document.querySelector('.user-name');
    if (userNameElement) {
        userNameElement.textContent = `Welcome, ${userEmail}!`;
    }
    
    // Initialize logout functionality
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Initialize sidebar navigation
    initializeSidebarNavigation();
    
    // Initialize action buttons
    initializeActionButtons();
    
    // Load dashboard data (simulated)
    loadDashboardData();
}

// Handle logout
function handleLogout() {
    // Clear user session
    localStorage.removeItem('userEmail');
    sessionStorage.removeItem('userEmail');
    
    // Redirect to login page
    window.location.href = 'login.html';
}

// Initialize sidebar navigation
function initializeSidebarNavigation() {
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            sidebarLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Update dashboard content based on selection
            const section = this.textContent.toLowerCase();
            updateDashboardContent(section);
        });
    });
}

// Initialize action buttons
function initializeActionButtons() {
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent;
            showMessage(`${action} functionality would be implemented here.`, 'info');
        });
    });
}

// Update dashboard content (placeholder)
function updateDashboardContent(section) {
    const contentArea = document.querySelector('.dashboard-header-section h2');
    if (contentArea) {
        contentArea.textContent = section.charAt(0).toUpperCase() + section.slice(1);
    }
    
    console.log(`Loading ${section} content...`);
}

// Load dashboard data (simulated)
function loadDashboardData() {
    // Simulate loading data with random values
    const statNumbers = document.querySelectorAll('.stat-number');
    
    setTimeout(() => {
        statNumbers.forEach(stat => {
            const currentValue = stat.textContent;
            // Add some animation or update logic here
            stat.style.opacity = '0.7';
            setTimeout(() => {
                stat.style.opacity = '1';
            }, 200);
        });
    }, 500);
}

// Utility functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    
    // Remove existing error styling
    input.classList.remove('error');
    
    if (input.hasAttribute('required') && !value) {
        showInputError(input, 'This field is required');
        return false;
    }
    
    if (input.type === 'email' && value && !isValidEmail(value)) {
        showInputError(input, 'Please enter a valid email address');
        return false;
    }
    
    return true;
}

function showInputError(input, message) {
    input.classList.add('error');
    
    // Remove existing error message
    const existingError = input.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentNode.appendChild(errorDiv);
}

function clearValidationError(e) {
    const input = e.target;
    input.classList.remove('error');
    
    const errorMessage = input.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessage = document.querySelector('.message-popup');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-popup ${type}`;
    messageDiv.textContent = message;
    
    // Style the message
    Object.assign(messageDiv.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '4px',
        color: 'white',
        fontWeight: 'bold',
        zIndex: '1000',
        opacity: '0',
        transition: 'opacity 0.3s ease'
    });
    
    // Set background color based on type
    switch(type) {
        case 'success':
            messageDiv.style.backgroundColor = '#28a745';
            break;
        case 'error':
            messageDiv.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            messageDiv.style.backgroundColor = '#ffc107';
            messageDiv.style.color = '#333';
            break;
        default:
            messageDiv.style.backgroundColor = '#17a2b8';
    }
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Fade in
    setTimeout(() => {
        messageDiv.style.opacity = '1';
    }, 100);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
}

// Add CSS for error styling
const style = document.createElement('style');
style.textContent = `
    .form-group input.error {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
    }
`;
document.head.appendChild(style);

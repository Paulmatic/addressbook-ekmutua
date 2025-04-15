/**
 * Address Book Main JavaScript
 * Handles common UI interactions and initializations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });

    // Form validation helper
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Auto-format phone numbers
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    });

    // Confirm before delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this contact?')) {
                e.preventDefault();
            }
        });
    });

    // Status filter chips
    const statusFilters = document.querySelectorAll('.status-filter');
    statusFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            statusFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Toggle advanced search
    const searchToggle = document.getElementById('advanced-search-toggle');
    if (searchToggle) {
        searchToggle.addEventListener('click', function() {
            const advancedSearch = document.getElementById('advanced-search');
            advancedSearch.classList.toggle('d-none');
            this.textContent = advancedSearch.classList.contains('d-none') ? 
                'Show Advanced Search' : 'Hide Advanced Search';
        });
    }

    // Auto-focus search input on search page
    if (window.location.pathname.includes('search')) {
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) searchInput.focus();
    }

    // Initialize clipboard for copy actions
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-clipboard-text') || 
                              this.previousElementSibling.value;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Table row click handler (for larger click areas)
    const tableRows = document.querySelectorAll('tr[data-href]');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                window.location.href = this.dataset.href;
            }
        });
    });
});

// Helper function for AJAX requests
function makeRequest(method, url, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            successCallback(JSON.parse(xhr.responseText));
        } else {
            errorCallback(xhr.statusText);
        }
    };
    
    xhr.onerror = function() {
        errorCallback('Network error');
    };
    
    xhr.send(JSON.stringify(data));
}

// CSRF token helper for AJAX
function getCookie(name) {
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
}

// Debounce function for search inputs
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Initialize any modals with dynamic content
function initDynamicModal(modalId, contentUrl) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const url = button.getAttribute('data-content-url') || contentUrl;
            
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    modal.querySelector('.modal-body').innerHTML = html;
                })
                .catch(err => {
                    console.error('Failed to load modal content:', err);
                });
        });
    }
}
// DOM elements
const form = document.getElementById('simulationForm');
const submitBtn = document.getElementById('simulateBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');

// Set default dates
function setDefaultDates() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 1); // 1 year ago
    
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
}

// Set default values
function setDefaults() {
    setDefaultDates();
    document.getElementById('symbol').value = 'TCS.NS';
    document.getElementById('ma1').value = '10';
    document.getElementById('ma2').value = '50';
}

// Validate form inputs
function validateForm(formData) {
    const errors = [];
    
    // Check symbol
    if (!formData.symbol.trim()) {
        errors.push('Stock symbol is required');
    }
    
    // Check dates
    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);
    const today = new Date();
    
    if (startDate >= endDate) {
        errors.push('Start date must be before end date');
    }
    
    if (endDate > today) {
        errors.push('End date cannot be in the future');
    }
    
    // Check if date range is too short
    const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
    if (daysDiff < 30) {
        errors.push('Date range should be at least 30 days');
    }
    
    // Check moving averages
    const ma1 = parseInt(formData.ma1_window);
    const ma2 = parseInt(formData.ma2_window);
    
    if (ma1 <= 0 || ma2 <= 0) {
        errors.push('Moving average windows must be positive numbers');
    }
    
    if (ma1 >= ma2) {
        errors.push('Short MA window must be smaller than Long MA window');
    }
    
    if (ma2 > daysDiff) {
        errors.push('Long MA window is too large for the selected date range');
    }
    
    return errors;
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorAlert.classList.remove('hidden');
    setTimeout(() => {
        errorAlert.classList.add('hidden');
    }, 8000);
}

// Show loading state
function showLoading() {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Running...';
    loadingIndicator.classList.remove('hidden');
    errorAlert.classList.add('hidden');
}

// Hide loading state
function hideLoading() {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-play mr-2"></i>Run Simulation';
    loadingIndicator.classList.add('hidden');
}

// Make API request
async function runSimulation(formData) {
    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('API request failed:', error);
        throw new Error(`Failed to connect to the server: ${error.message}`);
    }
}

// Handle form submission
async function handleSubmit(event) {
    event.preventDefault();
    
    // Get form data
    const formData = {
        symbol: document.getElementById('symbol').value.trim().toUpperCase(),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        ma1_window: parseInt(document.getElementById('ma1').value),
        ma2_window: parseInt(document.getElementById('ma2').value)
    };
    
    // Validate form
    const validationErrors = validateForm(formData);
    if (validationErrors.length > 0) {
        showError(validationErrors.join('. '));
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Run simulation
        const result = await runSimulation(formData);
        
        if (result.success) {
            // Store results and redirect
            sessionStorage.setItem('simulationResults', JSON.stringify(result));
            window.location.href = '/result';
        } else {
            throw new Error(result.error || 'Simulation failed');
        }
        
    } catch (error) {
        console.error('Simulation error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Add input event listeners for real-time validation
function addInputValidation() {
    const ma1Input = document.getElementById('ma1');
    const ma2Input = document.getElementById('ma2');
    
    function validateMAs() {
        const ma1 = parseInt(ma1Input.value);
        const ma2 = parseInt(ma2Input.value);
        
        if (ma1 && ma2 && ma1 >= ma2) {
            ma1Input.setCustomValidity('Short MA must be smaller than Long MA');
            ma2Input.setCustomValidity('Long MA must be larger than Short MA');
        } else {
            ma1Input.setCustomValidity('');
            ma2Input.setCustomValidity('');
        }
    }
    
    ma1Input.addEventListener('input', validateMAs);
    ma2Input.addEventListener('input', validateMAs);
    
    // Date validation
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    function validateDates() {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate && endDate && startDate >= endDate) {
            startDateInput.setCustomValidity('Start date must be before end date');
            endDateInput.setCustomValidity('End date must be after start date');
        } else {
            startDateInput.setCustomValidity('');
            endDateInput.setCustomValidity('');
        }
    }
    
    startDateInput.addEventListener('change', validateDates);
    endDateInput.addEventListener('change', validateDates);
}

// Popular stock symbols for quick selection
function addStockSuggestions() {
    const symbolInput = document.getElementById('symbol');
    const suggestions = [
        'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS',
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'
    ];
    
    // Create datalist for autocomplete
    const datalist = document.createElement('datalist');
    datalist.id = 'stockSuggestions';
    
    suggestions.forEach(symbol => {
        const option = document.createElement('option');
        option.value = symbol;
        datalist.appendChild(option);
    });
    
    symbolInput.setAttribute('list', 'stockSuggestions');
    symbolInput.parentNode.appendChild(datalist);
}

// Keyboard shortcuts
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Enter to submit form
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
        
        // Escape to hide error
        if (event.key === 'Escape') {
            errorAlert.classList.add('hidden');
        }
    });
}

// Initialize the application
function init() {
    // Set default values
    setDefaults();
    
    // Add event listeners
    form.addEventListener('submit', handleSubmit);
    
    // Add input validation
    addInputValidation();
    
    // Add stock suggestions
    addStockSuggestions();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    console.log('Trading Strategy Simulator initialized');
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
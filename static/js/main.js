// Main JavaScript for Face Recognition System

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components that need JavaScript functionality
    initializeComponents();
    
    // Set up event listeners
    setupEventListeners();
});

/**
 * Initialize UI components
 */
function initializeComponents() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Initialize camera if on a page with camera functionality
    initializeCamera();
}

/**
 * Set up event listeners for interactive elements
 */
function setupEventListeners() {
    // Handle confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });
    
    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize camera functionality if needed
 */
function initializeCamera() {
    const cameraElement = document.getElementById('camera');
    const captureButton = document.getElementById('capture-button');
    const retakeButton = document.getElementById('retake-button');
    const previewElement = document.getElementById('preview');
    const imageInput = document.getElementById('image-input');
    
    // If we're not on a page with camera functionality, exit early
    if (!cameraElement) return;
    
    let stream = null;
    let mediaRecorder = null;
    
    // Start camera when capture button is clicked
    if (captureButton) {
        captureButton.addEventListener('click', function() {
            if (stream) {
                // If stream exists, take a picture
                takePicture();
            } else {
                // Otherwise start the camera
                startCamera();
            }
        });
    }
    
    // Retake picture when retake button is clicked
    if (retakeButton) {
        retakeButton.addEventListener('click', function() {
            startCamera();
        });
    }
    
    /**
     * Start the camera stream
     */
    function startCamera() {
        // Hide preview and show camera
        if (previewElement) previewElement.style.display = 'none';
        if (cameraElement) cameraElement.style.display = 'block';
        
        // Update button text
        if (captureButton) captureButton.textContent = 'التقاط صورة';
        if (retakeButton) retakeButton.style.display = 'none';
        
        // Access the camera
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(mediaStream) {
                stream = mediaStream;
                cameraElement.srcObject = mediaStream;
                cameraElement.play();
            })
            .catch(function(err) {
                console.error('Error accessing camera: ', err);
                alert('حدث خطأ أثناء الوصول إلى الكاميرا. يرجى التحقق من إعدادات الكاميرا الخاصة بك.');
            });
    }
    
    /**
     * Take a picture from the camera stream
     */
    function takePicture() {
        if (!stream) return;
        
        // Create a canvas element to capture the image
        const canvas = document.createElement('canvas');
        canvas.width = cameraElement.videoWidth;
        canvas.height = cameraElement.videoHeight;
        
        // Draw the current video frame to the canvas
        const context = canvas.getContext('2d');
        context.drawImage(cameraElement, 0, 0, canvas.width, canvas.height);
        
        // Convert the canvas to a data URL and set as preview
        const imageDataUrl = canvas.toDataURL('image/png');
        if (previewElement) {
            previewElement.src = imageDataUrl;
            previewElement.style.display = 'block';
        }
        
        // Hide camera and show preview
        if (cameraElement) cameraElement.style.display = 'none';
        
        // Update buttons
        if (captureButton) captureButton.textContent = 'التقاط صورة جديدة';
        if (retakeButton) retakeButton.style.display = 'inline-block';
        
        // Set the image data in the hidden input field
        if (imageInput) imageInput.value = imageDataUrl;
        
        // Stop the camera stream
        stopCamera();
    }
    
    /**
     * Stop the camera stream
     */
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }
}

/**
 * Handle file input preview
 * @param {HTMLInputElement} input - The file input element
 * @param {string} previewId - The ID of the preview element
 */
function handleFileInputPreview(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Format a date string to a more readable format
 * @param {string} dateString - The date string to format
 * @returns {string} - The formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show a confirmation dialog before form submission
 * @param {Event} event - The form submission event
 * @param {string} message - The confirmation message
 * @returns {boolean} - Whether to proceed with form submission
 */
function confirmSubmit(event, message) {
    if (!confirm(message)) {
        event.preventDefault();
        return false;
    }
    return true;
}
// Global variables
let contacts = [];
let emailConfig = {
    sender_email: '',
    sender_password: '',
    subject_template: '',
    body_template: ''
};

// API endpoints
const API = {
    UPLOAD_CONTACTS: '/api/upload-contacts',
    PREVIEW_EMAIL: '/api/preview-email',
    SEND_EMAILS: '/api/send-emails'
};

// DOM Elements
const elements = {
    configForm: document.getElementById('configForm'),
    contactsForm: document.getElementById('contactsForm'),
    contactsFile: document.getElementById('contactsFile'),
    contactsPreview: document.getElementById('contactsPreview'),
    previewTable: document.getElementById('previewTable'),
    previewBtn: document.getElementById('previewBtn'),
    sendBtn: document.getElementById('sendBtn'),
    emailPreview: document.getElementById('emailPreview'),
    previewSubject: document.getElementById('previewSubject'),
    previewBody: document.getElementById('previewBody'),
    sendStatus: document.getElementById('sendStatus'),
    progressModal: new bootstrap.Modal(document.getElementById('progressModal')),
    progressBar: document.querySelector('.progress-bar'),
    progressText: document.getElementById('progressText'),
    selectedFileName: document.getElementById('selectedFileName'),
    selectedAttachmentName: document.getElementById('selectedAttachmentName')
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    elements.configForm.addEventListener('submit', handleConfigSubmit);
    elements.contactsFile.addEventListener('change', handleFileSelect);
    elements.previewBtn.addEventListener('click', handlePreview);
    elements.sendBtn.addEventListener('click', handleSendEmails);

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Update email configuration whenever inputs change
    document.getElementById('senderEmail').addEventListener('input', updateEmailConfig);
    document.getElementById('senderPassword').addEventListener('input', updateEmailConfig);
    document.getElementById('subjectTemplate').addEventListener('input', updateEmailConfig);
    document.getElementById('bodyTemplate').addEventListener('input', updateEmailConfig);
});

// Handle config form submission
async function handleConfigSubmit(event) {
    event.preventDefault();
}

// Handle contact file upload
async function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;

    // Update selected file name
    elements.selectedFileName.textContent = file.name;

    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    showLoading('Uploading and processing file...');

    try {
        const response = await fetch(API.UPLOAD_CONTACTS, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        contacts = await response.json();
        console.log('Contacts received:', contacts); // Debug log
        
        // Validate contacts data
        if (!Array.isArray(contacts) || contacts.length === 0) {
            throw new Error('No valid contacts found in the file');
        }

        displayContactsPreview(contacts);
        hideLoading();
        showSuccess(`Successfully loaded ${contacts.length} contacts`);
    } catch (error) {
        hideLoading();
        showError('Failed to upload contacts file: ' + error.message);
        console.error('Error:', error);
    }
}

// Handle attachment file select
function handleAttachmentSelect(input) {
    const file = input.files[0];
    if (file) {
        elements.selectedAttachmentName.textContent = file.name;
    }
}

// Display contacts preview
function displayContactsPreview(contacts) {
    const previewTable = elements.contactsPreview;
    previewTable.innerHTML = ''; // Clear existing content

    contacts.forEach(contact => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${contact.name || '-'}</td>
            <td>${contact.designation || '-'}</td>
            <td>${contact.linkedin || '-'}</td>
            <td>${contact.email || '-'}</td>
        `;
        previewTable.appendChild(row);
    });
}

// Update email configuration
function updateEmailConfig() {
    emailConfig = {
        sender_email: document.getElementById('senderEmail').value.trim(),
        sender_password: document.getElementById('senderPassword').value.trim(),
        subject_template: document.getElementById('subjectTemplate').value.trim(),
        body_template: document.getElementById('bodyTemplate').value.trim()
    };
    console.log('Email config updated:', { ...emailConfig, sender_password: '****' });
}

// Handle sending emails
async function handleSendEmails() {
    updateEmailConfig(); // Ensure we have the latest config

    if (!validateEmailConfig()) {
        return;
    }

    if (!contacts || contacts.length === 0) {
        showError('Please upload contacts file first');
        return;
    }

    const formData = new FormData();
    formData.append('config', JSON.stringify(emailConfig));
    formData.append('contacts', JSON.stringify(contacts));

    // Add attachment if present
    const attachment = document.getElementById('attachment').files[0];
    if (attachment) {
        formData.append('attachment', attachment);
    }

    // Show progress modal
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    progressModal.show();
    updateProgress(0, 'Preparing to send emails...');

    try {
        const response = await fetch('/api/send-emails', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to send emails');
        }

        updateProgress(100, `Sent ${result.success} out of ${result.total} emails successfully!`);
        
        setTimeout(() => {
            progressModal.hide();
            showSuccess(`Email campaign completed! Successfully sent: ${result.success}/${result.total} emails`);
            if (result.failed > 0) {
                showFailedEmails(result.failed_details);
            }
        }, 1000);
    } catch (error) {
        progressModal.hide();
        showError('Failed to send emails: ' + error.message);
        console.error('Error:', error);
    }
}

// Validate email configuration
function validateEmailConfig() {
    if (!emailConfig.sender_email) {
        showError('Please enter sender email');
        return false;
    }
    if (!emailConfig.sender_password) {
        showError('Please enter sender password');
        return false;
    }
    if (!emailConfig.subject_template) {
        showError('Please enter email subject template');
        return false;
    }
    if (!emailConfig.body_template) {
        showError('Please enter email body template');
        return false;
    }
    return true;
}

// Show failed emails in a modal
function showFailedEmails(failedDetails) {
    let failedMessage = 'Failed to send to:\n\n';
    failedDetails.forEach(detail => {
        failedMessage += `${detail.email}: ${detail.error}\n`;
    });
    
    Swal.fire({
        title: 'Some Emails Failed',
        text: failedMessage,
        icon: 'warning'
    });
}

// Update progress bar
function updateProgress(percent, message) {
    elements.progressBar.style.width = `${percent}%`;
    elements.progressText.textContent = message;
}

// Handle email preview
async function handlePreview() {
    if (!validateEmailConfig()) {
        return;
    }

    try {
        const formData = new FormData();
        formData.append('subject_template', emailConfig.subject_template);
        formData.append('body_template', emailConfig.body_template);
        formData.append('name', 'John Doe');
        formData.append('designation', 'Software Engineer');
        formData.append('linkedin', 'linkedin.com/johndoe');

        const response = await fetch(API.PREVIEW_EMAIL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Preview failed');
        }

        const preview = await response.json();
        
        // Show preview in modal
        elements.previewSubject.textContent = preview.subject;
        elements.previewBody.textContent = preview.body;
        
        const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
        previewModal.show();
    } catch (error) {
        showError('Failed to generate preview: ' + error.message);
        console.error('Error:', error);
    }
}

// Notification functions
function showSuccess(message) {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: message,
        timer: 3000,
        showConfirmButton: false
    });
}

function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message
    });
}

function showLoading(message) {
    Swal.fire({
        title: 'Processing',
        text: message,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

function hideLoading() {
    Swal.close();
}

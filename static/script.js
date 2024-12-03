// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const API = {
    UPLOAD_CONTACTS: `${API_BASE_URL}/upload_contacts`,
    SEND_EMAILS: `${API_BASE_URL}/send_emails`,
    PREVIEW_EMAIL: `${API_BASE_URL}/preview_email`
};

// DOM Elements
const elements = {
    configForm: document.getElementById('configForm'),
    contactsForm: document.getElementById('contactsForm'),
    contactsFile: document.getElementById('contactsFile'),
    previewSection: document.getElementById('previewSection'),
    previewTable: document.getElementById('previewTable'),
    previewBtn: document.getElementById('previewBtn'),
    sendBtn: document.getElementById('sendBtn'),
    emailPreview: document.getElementById('emailPreview'),
    previewContent: document.getElementById('previewContent'),
    progressModal: new bootstrap.Modal(document.getElementById('progressModal')),
    progressBar: document.querySelector('.progress-bar'),
    progressText: document.getElementById('progressText')
};

let contacts = [];

// Event Listeners
elements.contactsFile.addEventListener('change', handleFileUpload);
elements.previewBtn.addEventListener('click', handlePreview);
elements.sendBtn.addEventListener('click', handleSendEmails);

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(API.UPLOAD_CONTACTS, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        contacts = await response.json();
        displayContactsPreview(contacts);
        elements.previewSection.classList.remove('d-none');
    } catch (error) {
        showError('Failed to upload contacts file');
        console.error(error);
    }
}

function displayContactsPreview(contacts) {
    elements.previewTable.innerHTML = contacts.slice(0, 5).map(contact => `
        <tr>
            <td>${contact.Name}</td>
            <td>${contact.Designation}</td>
            <td>${contact.Email}</td>
            <td>${contact.LinkedIn_ID || '-'}</td>
        </tr>
    `).join('');
}

async function handlePreview() {
    const config = getConfig();
    if (!validateConfig(config)) return;

    try {
        const response = await fetch(API.PREVIEW_EMAIL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "John Doe",
                designation: "Software Engineer",
                subject_template: config.subject_template,
                body_template: config.body_template
            })
        });

        if (!response.ok) throw new Error('Preview failed');

        const preview = await response.json();
        displayPreview(preview);
    } catch (error) {
        showError('Failed to generate email preview');
        console.error(error);
    }
}

async function handleSendEmails() {
    const config = getConfig();
    if (!validateConfig(config) || !contacts.length) {
        showError('Please fill in all required fields and upload contacts');
        return;
    }

    const formData = new FormData();
    formData.append('config', JSON.stringify(config));
    formData.append('contacts', JSON.stringify(contacts));

    const attachment = document.getElementById('attachment').files[0];
    if (attachment) {
        formData.append('attachment', attachment);
    }

    elements.progressModal.show();
    updateProgress(0, 'Preparing to send emails...');

    try {
        const response = await fetch(API.SEND_EMAILS, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to send emails');

        const result = await response.json();
        updateProgress(100, 'All emails sent successfully!');
        
        setTimeout(() => {
            elements.progressModal.hide();
            showSuccess('Emails sent successfully!');
        }, 1000);
    } catch (error) {
        elements.progressModal.hide();
        showError('Failed to send emails');
        console.error(error);
    }
}

function getConfig() {
    return {
        sender_email: document.getElementById('senderEmail').value,
        sender_password: document.getElementById('senderPassword').value,
        subject_template: document.getElementById('subjectTemplate').value,
        body_template: document.getElementById('bodyTemplate').value
    };
}

function validateConfig(config) {
    return Object.values(config).every(value => value.trim() !== '');
}

function displayPreview(preview) {
    elements.emailPreview.classList.remove('d-none');
    elements.previewContent.innerHTML = `
        <strong>Subject:</strong><br>
        ${preview.subject}<br><br>
        <strong>Body:</strong><br>
        ${preview.body.replace(/\n/g, '<br>')}
    `;
}

function updateProgress(percent, text) {
    elements.progressBar.style.width = `${percent}%`;
    elements.progressText.textContent = text;
}

function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
        confirmButtonColor: '#0d6efd'
    });
}

function showSuccess(message) {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: message,
        confirmButtonColor: '#0d6efd'
    });
}

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os
from pathlib import Path
from io import BytesIO
import csv

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class EmailConfig(BaseModel):
    sender_email: str
    sender_password: str
    subject_template: str
    body_template: str

class Contact(BaseModel):
    Name: str
    Designation: str
    Email: str
    LinkedIn_ID: Optional[str] = None

@app.post("/api/upload-contacts")
async def upload_contacts(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        if file.filename.endswith('.json'):
            # Parse JSON file
            contacts_data = json.loads(content.decode())
            # Ensure it's a list
            if not isinstance(contacts_data, list):
                contacts_data = [contacts_data]
            
            # Standardize field names
            standardized_contacts = []
            for contact in contacts_data:
                standardized_contact = {}
                for key, value in contact.items():
                    # Convert keys to lowercase for comparison
                    key_lower = key.lower()
                    if 'name' in key_lower:
                        standardized_contact['name'] = value
                    elif 'email' in key_lower:
                        standardized_contact['email'] = value
                    elif 'designation' in key_lower:
                        standardized_contact['designation'] = value
                    elif 'linkedin' in key_lower:
                        standardized_contact['linkedin'] = value
                    else:
                        standardized_contact[key] = value
                standardized_contacts.append(standardized_contact)
            
            return standardized_contacts
            
        elif file.filename.endswith('.csv'):
            # Parse CSV file
            csv_content = content.decode().splitlines()
            csv_reader = csv.DictReader(csv_content)
            contacts_data = list(csv_reader)
            
            # Standardize field names
            standardized_contacts = []
            for contact in contacts_data:
                standardized_contact = {}
                for key, value in contact.items():
                    # Convert keys to lowercase for comparison
                    key_lower = key.lower()
                    if 'name' in key_lower:
                        standardized_contact['name'] = value
                    elif 'email' in key_lower:
                        standardized_contact['email'] = value
                    elif 'designation' in key_lower:
                        standardized_contact['designation'] = value
                    elif 'linkedin' in key_lower:
                        standardized_contact['linkedin'] = value
                    else:
                        standardized_contact[key] = value
                standardized_contacts.append(standardized_contact)
            
            return standardized_contacts
            
        elif file.filename.endswith(('.xlsx', '.xls')):
            # Parse Excel file
            df = pd.read_excel(BytesIO(content))
            contacts_data = df.to_dict('records')
            
            # Standardize field names
            standardized_contacts = []
            for contact in contacts_data:
                standardized_contact = {}
                for key, value in contact.items():
                    # Convert keys to lowercase for comparison
                    if isinstance(key, str):  # Handle non-string column names
                        key_lower = key.lower()
                        if 'name' in key_lower:
                            standardized_contact['name'] = value
                        elif 'email' in key_lower:
                            standardized_contact['email'] = value
                        elif 'designation' in key_lower:
                            standardized_contact['designation'] = value
                        elif 'linkedin' in key_lower:
                            standardized_contact['linkedin'] = value
                        else:
                            standardized_contact[key] = value
                standardized_contacts.append(standardized_contact)
            
            return standardized_contacts
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a JSON, CSV, or Excel file."
            )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview-email")
async def preview_email(
    subject_template: str = Form(...),
    body_template: str = Form(...),
    name: str = Form(...),
    designation: str = Form(...),
    linkedin: str = Form(...)
):
    try:
        # Create sample data
        sample_data = {
            'name': name,
            'designation': designation,
            'linkedin': linkedin
        }

        # Replace template variables
        subject = subject_template
        body = body_template

        for key, value in sample_data.items():
            placeholder = '{' + key + '}'
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)

        return {
            'subject': subject,
            'body': body
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-emails")
async def send_emails(
    config: str = Form(...),
    contacts: str = Form(...),
    attachment: UploadFile = None
):
    try:
        # Parse JSON data
        config_data = json.loads(config)
        contacts_data = json.loads(contacts)

        # Initialize counters
        total = len(contacts_data)
        success = 0
        failed = 0
        failed_details = []

        # Hostinger SMTP Settings
        smtp_server = "smtp.hostinger.com"
        smtp_port = 465
        
        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(config_data['sender_email'], config_data['sender_password'])

            # Process attachment if provided
            attachment_data = None
            if attachment:
                contents = await attachment.read()
                attachment_data = {
                    'filename': attachment.filename,
                    'content': contents
                }

            # Send emails
            for contact in contacts_data:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = config_data['sender_email']
                    msg['To'] = contact['email']
                    
                    # Get email templates
                    subject_template = config_data['subject_template']
                    body_template = config_data['body_template']
                    
                    # Replace template variables with contact data
                    subject = subject_template
                    body = body_template
                    
                    # Replace variables in both subject and body
                    replacements = {
                        '{name}': contact.get('name', ''),
                        '{email}': contact.get('email', ''),
                        '{designation}': contact.get('designation', ''),
                        '{linkedin}': contact.get('linkedin', '')
                    }
                    
                    for placeholder, value in replacements.items():
                        subject = subject.replace(placeholder, str(value))
                        body = body.replace(placeholder, str(value))
                    
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    # Add attachment if provided
                    if attachment_data:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment_data['content'])
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{attachment_data["filename"]}"'
                        )
                        msg.attach(part)

                    # Send email
                    server.send_message(msg)
                    success += 1

                except Exception as e:
                    failed += 1
                    failed_details.append({
                        'email': contact['email'],
                        'error': str(e)
                    })

            server.quit()

        except Exception as smtp_error:
            raise HTTPException(
                status_code=500,
                detail=f"SMTP Error: {str(smtp_error)}"
            )

        return {
            'success': success,
            'failed': failed,
            'total': total,
            'failed_details': failed_details
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

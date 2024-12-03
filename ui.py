import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from ttkthemes import ThemedTk

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Email Sender")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.file_path = None
        self.attachment_path = None
        self.preview_window = None
        
        self.setup_styles()
        self.create_ui()
        
    def setup_styles(self):
        # Configure styles
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Preview.TLabel", font=("Helvetica", 10))
        
    def create_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_container, text="Professional Email Sender", style="Title.TLabel")
        title.pack(pady=(0, 20))
        
        # Create left and right frames
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Left frame contents (File selection and credentials)
        self.create_file_section(left_frame)
        self.create_credentials_section(left_frame)
        
        # Right frame contents (Email content and preview)
        self.create_email_content_section(right_frame)
        
        # Bottom section
        self.create_bottom_section(main_container)
        
    def create_file_section(self, parent):
        file_frame = ttk.LabelFrame(parent, text="Data Source", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        self.file_label = ttk.Label(file_frame, text="No file selected", wraplength=300)
        self.file_label.pack(fill=tk.X, pady=(0, 5))
        
        select_file_btn = ttk.Button(file_frame, text="Select Contact File", command=self.select_file)
        select_file_btn.pack(fill=tk.X)
        
        # Attachment
        ttk.Separator(file_frame).pack(fill=tk.X, pady=10)
        
        self.attachment_label = ttk.Label(file_frame, text="No attachment selected", wraplength=300)
        self.attachment_label.pack(fill=tk.X, pady=(5, 5))
        
        attach_file_btn = ttk.Button(file_frame, text="Select Attachment", command=self.attach_file)
        attach_file_btn.pack(fill=tk.X)
        
    def create_credentials_section(self, parent):
        cred_frame = ttk.LabelFrame(parent, text="Email Credentials", padding="10")
        cred_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cred_frame, text="Sender Email:").pack(anchor=tk.W)
        self.email_entry = ttk.Entry(cred_frame, width=40)
        self.email_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cred_frame, text="Password:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(cred_frame, width=40, show="*")
        self.password_entry.pack(fill=tk.X)
        
    def create_email_content_section(self, parent):
        content_frame = ttk.LabelFrame(parent, text="Email Content", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Subject
        ttk.Label(content_frame, text="Subject Template:").pack(anchor=tk.W)
        self.subject_text = tk.Text(content_frame, height=2, width=50)
        self.subject_text.pack(fill=tk.X, pady=(0, 10))
        self.subject_text.insert("1.0", "Professional Connection Request - {name}")
        
        # Body
        ttk.Label(content_frame, text="Body Template:").pack(anchor=tk.W)
        self.body_text = tk.Text(content_frame, height=10, width=50)
        self.body_text.pack(fill=tk.BOTH, expand=True)
        default_body = """Dear {name},

I noticed your profile and your role as {designation} and would like to connect with you regarding potential collaboration opportunities.

[Your message content here]

Best regards,
[Your name]"""
        self.body_text.insert("1.0", default_body)
        
        # Preview button
        preview_btn = ttk.Button(content_frame, text="Preview Email", command=self.show_preview)
        preview_btn.pack(pady=10)
        
    def create_bottom_section(self, parent):
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Data preview
        preview_frame = ttk.LabelFrame(bottom_frame, text="Contact Data Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.data_table = ttk.Treeview(tree_frame, show="headings", height=5)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.data_table.yview)
        self.data_table.configure(yscrollcommand=scrollbar.set)
        
        self.data_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Send button
        self.send_button = ttk.Button(bottom_frame, text="Send Emails", command=self.send_emails, style="Accent.TButton")
        self.send_button.pack(pady=20)
        
    def select_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx;*.xls"),
            ),
        )
        if self.file_path:
            self.file_label.config(text=f"Selected File: {os.path.basename(self.file_path)}")
            try:
                self.show_file_content()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def attach_file(self):
        self.attachment_path = filedialog.askopenfilename(
            title="Select a File to Attach",
            filetypes=(("All Files", "*.*"),),
        )
        if self.attachment_path:
            self.attachment_label.config(text=f"Attachment: {os.path.basename(self.attachment_path)}")
            
    def show_file_content(self):
        try:
            data = self.load_data()
            self.show_data_table(data)
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying file content: {e}")
            
    def load_data(self):
        """Load email data from file."""
        if not self.file_path:
            raise ValueError("Please select a file first")
            
        if self.file_path.endswith(".json"):
            with open(self.file_path, 'r') as f:
                return pd.DataFrame(json.load(f))
        elif self.file_path.endswith(".csv"):
            return pd.read_csv(self.file_path)
        elif self.file_path.endswith((".xlsx", ".xls")):
            return pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format")
            
    def show_data_table(self, data):
        # Clear existing items
        for item in self.data_table.get_children():
            self.data_table.delete(item)
            
        # Configure columns
        self.data_table["columns"] = list(data.columns)
        for col in data.columns:
            self.data_table.heading(col, text=col)
            self.data_table.column(col, width=100)
            
        # Add data
        for idx, row in data.iterrows():
            self.data_table.insert("", "end", values=list(row))
            
    def show_preview(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a data file first")
            return
            
        try:
            data = self.load_data()
            if len(data) == 0:
                messagebox.showwarning("Warning", "No data available for preview")
                return
                
            # Create preview window
            if self.preview_window is None or not tk.Toplevel.winfo_exists(self.preview_window):
                self.preview_window = tk.Toplevel(self.root)
                self.preview_window.title("Email Preview")
                self.preview_window.geometry("600x400")
                
                preview_frame = ttk.Frame(self.preview_window, padding="20")
                preview_frame.pack(fill=tk.BOTH, expand=True)
                
                # Preview for first recipient
                row = data.iloc[0]
                subject = self.subject_text.get("1.0", tk.END).strip().format(
                    name=row["Name"],
                    designation=row["Desicnation"]
                )
                body = self.body_text.get("1.0", tk.END).strip().format(
                    name=row["Name"],
                    designation=row["Desicnation"]
                )
                
                ttk.Label(preview_frame, text="Preview for first recipient:", style="Header.TLabel").pack(anchor=tk.W)
                ttk.Label(preview_frame, text=f"To: {row['Email']}", style="Preview.TLabel").pack(anchor=tk.W, pady=(10, 5))
                ttk.Label(preview_frame, text=f"Subject: {subject}", style="Preview.TLabel").pack(anchor=tk.W, pady=5)
                ttk.Label(preview_frame, text="Body:", style="Preview.TLabel").pack(anchor=tk.W, pady=5)
                
                body_preview = tk.Text(preview_frame, wrap=tk.WORD, height=10)
                body_preview.pack(fill=tk.BOTH, expand=True)
                body_preview.insert("1.0", body)
                body_preview.config(state=tk.DISABLED)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {e}")
            
    def send_emails(self):
        try:
            sender_email = self.email_entry.get().strip()
            sender_password = self.password_entry.get().strip()
            
            if not all([sender_email, sender_password]):
                messagebox.showwarning("Warning", "Please enter email credentials")
                return
                
            data = self.load_data()
            total = len(data)
            success = 0
            
            for idx, row in data.iterrows():
                try:
                    subject = self.subject_text.get("1.0", tk.END).strip().format(
                        name=row["Name"],
                        designation=row["Desicnation"]
                    )
                    body = self.body_text.get("1.0", tk.END).strip().format(
                        name=row["Name"],
                        designation=row["Desicnation"]
                    )
                    
                    self.send_single_email(
                        sender_email,
                        sender_password,
                        row["Email"],
                        subject,
                        body
                    )
                    success += 1
                    
                except Exception as e:
                    print(f"Error sending to {row['Email']}: {e}")
                    
            messagebox.showinfo("Complete", f"Sent {success} out of {total} emails successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error sending emails: {e}")
            
    def send_single_email(self, sender_email, sender_password, recipient_email, subject, body):
        try:
            server = smtplib.SMTP("smtp.hostinger.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            if self.attachment_path:
                with open(self.attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(self.attachment_path)}",
                    )
                    message.attach(part)
                    
            server.sendmail(sender_email, recipient_email, message.as_string())
            server.quit()
            
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Using a modern theme
    app = EmailSenderApp(root)
    root.mainloop()

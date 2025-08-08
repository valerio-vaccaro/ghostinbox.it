from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
import imaplib
import email
from email.header import decode_header
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-for-development')

# Retrieve email and password from environment variables
EMAIL_ADDRESS = os.getenv('BASE_EMAIL')
PASSWORD = os.getenv('BASE_PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
DOMAIN = os.getenv('DOMAIN')
ONION_DOMAIN = os.getenv('ONION_DOMAIN')

# Example usage (e.g., connecting to an IMAP server)
# Replace this with your actual code
print(f"Email: {EMAIL_ADDRESS}")
print(f"Password: {PASSWORD}")

# Libero.it IMAP settings
IMAP_SERVER = 'imapmail.libero.it'

def extract_email_from_to_field(to_field):
    """
    Extract email address from the 'to' field which can be either:
    - Plain email: "user@example.com"
    - Formatted: '"Name Surname" <user@example.com>'

    Args:
        to_field (str): The 'to' field content

    Returns:
        str: The extracted email address or None if not found
    """
    if not to_field:
        return None

    # Pattern to match email addresses
    # This regex handles both plain emails and emails within angle brackets
    email_pattern = r'<([^>]+)>|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'

    match = re.search(email_pattern, to_field)
    if match:
        # Return the first non-None group (either from angle brackets or plain email)
        return match.group(1) if match.group(1) else match.group(2)

    return None

def get_emails():
    try:
        # Connect to Libero.it IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select('inbox')  # Select the inbox folder

        # Search for all emails in the inbox
        status, data = mail.search(None, 'ALL')
        email_ids = data[0].split()[-10:]  # Get the latest 10 emails

        emails = []
        for email_id in email_ids:
            # Fetch email by ID
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            # Get email subject
            subject, encoding = decode_header(msg['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='ignore')

            # Get sender
            from_ = msg.get('from')

            # Get email date
            date_ = msg.get('date')

            # Get email body (prefer plain text, fall back to HTML)
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
                    elif content_type == 'text/html' and not body:
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # Get receiver
            to_ = msg.get('to')

            # Store email info
            emails.append({
                'id': email_id.decode(),
                'from': from_,
                'to': to_,
                'subject': subject,
                'date': date_,
                'body': body
            })

        mail.logout()
        return emails[::-1]  # Reverse to show newest emails first

    except Exception as e:
        print(f"Error: {e}")
        return []

def get_email_by_id(email_id):
    try:
        # Connect to Libero.it IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select('inbox')  # Select the inbox folder

        # Fetch email by ID
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        # Get email subject
        subject, encoding = decode_header(msg['subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='ignore')

        # Get sender
        from_ = msg.get('from')

        # Get email date
        date_ = msg.get('date')

        # Get email body (prefer plain text, fall back to HTML)
        body = ''
        content_type = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
                elif content_type == 'text/html' and not body:
                    body = part.get_payload(decode=True).decode(errors='ignore')
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
            content_type = msg.get_content_type()

        # Get receiver
        to_ = msg.get('to')

        mail.logout()
        return {
            'id': email_id,
            'from': from_,
            'to': to_,
            'subject': subject,
            'date': date_,
            'body': body,
            'content_type': content_type
        }

    except Exception as e:
        print(f"Error fetching email {email_id}: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', domain=DOMAIN, onion_domain=ONION_DOMAIN)

@app.route('/email/<email_id>')
def view_email(email_id):
    hash = request.args.get('hash', '')
    if not hash:
        flash('Alias is required to view emails', 'error')
        return redirect(url_for('index'))
        
    email_data = get_email_by_id(email_id)
    if not email_data:
        flash('Email not found', 'error')
        return redirect(url_for('index'))
        
    # Extract the actual email address from the 'to' field
    extracted_email = extract_email_from_to_field(email_data['to'])

    # Check if the extracted email matches the hash
    if extracted_email != f'{hash}@ghostinbox.it':
        flash('Email not found, wrong hash', 'error')
        return redirect(url_for('index'))
    
    # Store the hash in session for subsequent requests
    session['hash'] = hash

    return render_template('email_view.html', email=email_data, hash=hash, domain=DOMAIN, onion_domain=ONION_DOMAIN)

@app.route('/search')
def search_alias():
    hash = request.args.get('hash', '').strip()

    if not hash or len(hash) != 64:
        return redirect(url_for('index'))
    
    try:
        emails = get_emails()
        # Filter emails where the extracted email matches the hash
        filtered_emails = []
        for email in emails:
            extracted_email = extract_email_from_to_field(email['to'])
            if extracted_email.lower() == f'{hash}@ghostinbox.it'.lower():
                filtered_emails.append(email)

        return render_template('search_results.html', 
                             emails=filtered_emails, 
                             alias=f'{hash}@ghostinbox.it',
                             hash=hash,
                             domain=DOMAIN,
                             onion_domain=ONION_DOMAIN)
    except Exception as e:
        flash(f'Error searching emails: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/stats')
def stats():
    return redirect('/static/stats.html')

@app.route('/about')
def about():
    return render_template('about.html', domain=DOMAIN, onion_domain=ONION_DOMAIN)

if __name__ == '__main__':
    app.run(debug=True)

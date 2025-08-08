from datetime import datetime
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from collections import Counter
import re

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_ADDRESS = os.getenv('BASE_EMAIL')
PASSWORD = os.getenv('BASE_PASSWORD')
IMAP_SERVER = 'imapmail.libero.it'

def extract_email_from_to_field(to_field):
    """Extract email address from the 'to' field"""
    if not to_field:
        return None
    email_pattern = r'<([^>]+)>|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, to_field)
    if match:
        return match.group(1) if match.group(1) else match.group(2)
    return None

def get_web_stats():
    """Get comprehensive email statistics for web display"""
    try:
        print(f"🔗 Connecting to IMAP server: {IMAP_SERVER}")
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select('inbox')

        # Search for all emails
        status, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        print(f"📧 Found {len(email_ids)} total emails in inbox")

        # Statistics tracking
        total_emails = 0
        unique_senders = set()
        unique_receivers = set()
        deleted_count = 0
        total_size = 0
        largest_email_size = 0
        recent_emails = 0
        older_emails = 0
        very_old_emails = 0
        
        # Counters for top senders/receivers
        sender_counter = Counter()
        receiver_counter = Counter()
        
        # Recent emails list for display
        recent_emails_list = []
        
        print(f"🔍 Starting email analysis...")
        ghostinbox_emails = 0

        for email_id in email_ids:
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            # Get email details
            from_ = msg.get('from', 'Unknown')
            to_ = msg.get('to', 'Unknown')
            
            # Extract email from 'to' field and check if it's ghostinbox.it
            extracted_email = extract_email_from_to_field(to_)
            if not extracted_email or not extracted_email.lower().endswith('@ghostinbox.it'):
                # Delete emails that don't end with @ghostinbox.it
                mail.store(email_id, '+FLAGS', '\\Deleted')
                print(f"🗑️  Deleting non-ghostinbox email: {extracted_email or 'unknown'}")
                continue  # Skip processing but mark for deletion
            
            ghostinbox_emails += 1
            total_emails += 1
            
            # Update counters
            unique_senders.add(from_)
            unique_receivers.add(extracted_email)
            sender_counter[from_] += 1
            receiver_counter[extracted_email] += 1
            
            # Get subject
            subject, encoding = decode_header(msg['subject'])[0] if msg['subject'] else ('No Subject', None)
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='ignore')

            # Calculate age in days
            date_str = msg.get('date')
            age_days = 'N/A'
            if date_str:
                try:
                    email_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    age_days = (datetime.now(email_date.tzinfo) - email_date).days
                except ValueError:
                    age_days = 'N/A'

            # Calculate size
            size = len(msg_data[0][1])
            total_size += size
            largest_email_size = max(largest_email_size, size)

            # Categorize by age
            if isinstance(age_days, int):
                if age_days <= 7:
                    recent_emails += 1
                elif age_days <= 30:
                    older_emails += 1
                else:
                    very_old_emails += 1

            # Check if email should be deleted
            status = 'Kept'
            if isinstance(age_days, int) and age_days > 30:
                mail.store(email_id, '+FLAGS', '\\Deleted')
                status = 'Deleted'
                deleted_count += 1

            # Add to recent emails list (last 10)
            if len(recent_emails_list) < 10:
                recent_emails_list.append({
                    'from_': from_,
                    'to_': extracted_email,  # Use extracted email instead of raw 'to' field
                    'subject': subject,
                    'age_days': age_days,
                    'size_kb': round(size / 1024, 1),
                    'status': status
                })

        # Permanently remove deleted emails
        mail.expunge()
        mail.logout()

        print(f"✅ Email analysis complete!")
        print(f"📊 Statistics Summary:")
        print(f"   • Total ghostinbox.it emails: {ghostinbox_emails}")
        print(f"   • Non-ghostinbox emails deleted: {len(email_ids) - ghostinbox_emails}")
        print(f"   • Unique senders: {len(unique_senders)}")
        print(f"   • Unique receivers: {len(unique_receivers)}")
        print(f"   • Deleted old emails: {deleted_count}")
        print(f"   • Total size: {round(total_size / (1024 * 1024), 1)} MB")
        print(f"   • Recent emails (0-7 days): {recent_emails}")
        print(f"   • Older emails (8-30 days): {older_emails}")
        print(f"   • Very old emails (30+ days): {very_old_emails}")

        # Prepare top senders and receivers
        top_senders = [{'email': email, 'count': count} for email, count in sender_counter.most_common(5)]
        top_receivers = [{'email': email, 'count': count} for email, count in receiver_counter.most_common(5)]

        # Calculate averages
        avg_size_kb = round(total_size / total_emails / 1024, 1) if total_emails > 0 else 0
        total_size_mb = round(total_size / (1024 * 1024), 1)
        largest_email_kb = round(largest_email_size / 1024, 1)

        return {
            'total_emails': total_emails,
            'unique_senders': len(unique_senders),
            'unique_receivers': len(unique_receivers),
            'deleted_count': deleted_count,
            'total_size_mb': total_size_mb,
            'avg_size_kb': avg_size_kb,
            'largest_email_kb': largest_email_kb,
            'recent_emails': recent_emails,
            'older_emails': older_emails,
            'very_old_emails': very_old_emails,
            'recent_emails_list': recent_emails_list,
            'top_senders': top_senders,
            'top_receivers': top_receivers,
            'imap_server': IMAP_SERVER,
            'email_account': EMAIL_ADDRESS,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        print(f"❌ Error getting web stats: {e}")
        print(f"🔍 Debug info:")
        print(f"   • IMAP Server: {IMAP_SERVER}")
        print(f"   • Email Address: {EMAIL_ADDRESS}")
        print(f"   • Password: {'*' * len(PASSWORD) if PASSWORD else 'Not set'}")
        return {
            'total_emails': 0,
            'unique_senders': 0,
            'unique_receivers': 0,
            'deleted_count': 0,
            'total_size_mb': 0,
            'avg_size_kb': 0,
            'largest_email_kb': 0,
            'recent_emails': 0,
            'older_emails': 0,
            'very_old_emails': 0,
            'recent_emails_list': [],
            'top_senders': [],
            'top_receivers': [],
            'imap_server': IMAP_SERVER,
            'email_account': EMAIL_ADDRESS,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }

def generate_static_stats_page():
    """Generate a static HTML stats page and save it to static folder"""
    print(f"🚀 Starting static stats page generation...")
    stats = get_web_stats()
    
    # Generate the HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stats - GhostInbox</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <style>
        body {{{{
            background-color: var(--bs-body-bg);
            color: var(--bs-body-color);
        }}}}
        .card {{{{
            background-color: var(--bs-card-bg);
            border-color: var(--bs-border-color);
        }}}}
        .table {{{{
            color: var(--bs-body-color);
        }}}}
        .table-striped > tbody > tr:nth-of-type(odd) > * {{{{
            background-color: var(--bs-table-striped-bg);
        }}}}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-envelope"></i> ghostinbox.it
            </a>
            <span class="navbar-text text-light ms-2">
                <i class="bi bi-shield-lock"></i> Static Stats Page
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">
                    <i class="bi bi-graph-up"></i> Email Statistics
                </h1>
                
                <!-- Summary Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card bg-primary text-white">
                            <div class="card-body text-center">
                                <i class="bi bi-envelope-fill fs-1"></i>
                                <h3 class="card-title">{stats['total_emails']}</h3>
                                <p class="card-text">Total Emails</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-success text-white">
                            <div class="card-body text-center">
                                <i class="bi bi-person-fill fs-1"></i>
                                <h3 class="card-title">{stats['unique_senders']}</h3>
                                <p class="card-text">Unique Senders</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-info text-white">
                            <div class="card-body text-center">
                                <i class="bi bi-people-fill fs-1"></i>
                                <h3 class="card-title">{stats['unique_receivers']}</h3>
                                <p class="card-text">Unique Receivers</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-warning text-dark">
                            <div class="card-body text-center">
                                <i class="bi bi-trash-fill fs-1"></i>
                                <h3 class="card-title">{stats['deleted_count']}</h3>
                                <p class="card-text">Deleted Emails</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Email Age Distribution -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="bi bi-calendar"></i> Email Age Distribution</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Recent (0-7 days)</span>
                                        <span class="badge bg-success">{stats['recent_emails']}</span>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" style="width: {(stats['recent_emails'] / stats['total_emails'] * 100) if stats['total_emails'] > 0 else 0}%"></div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Older (8-30 days)</span>
                                        <span class="badge bg-warning">{stats['older_emails']}</span>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-warning" style="width: {(stats['older_emails'] / stats['total_emails'] * 100) if stats['total_emails'] > 0 else 0}%"></div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Very Old (30+ days)</span>
                                        <span class="badge bg-danger">{stats['very_old_emails']}</span>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-danger" style="width: {(stats['very_old_emails'] / stats['total_emails'] * 100) if stats['total_emails'] > 0 else 0}%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="bi bi-hdd"></i> Storage Statistics</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Total Size</span>
                                        <span class="badge bg-primary">{stats['total_size_mb']} MB</span>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Average Email Size</span>
                                        <span class="badge bg-info">{stats['avg_size_kb']} KB</span>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between">
                                        <span>Largest Email</span>
                                        <span class="badge bg-warning">{stats['largest_email_kb']} KB</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Emails Table -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5><i class="bi bi-table"></i> Recent Emails</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>From</th>
                                        <th>To</th>
                                        <th>Subject</th>
                                        <th>Age (days)</th>
                                        <th>Size</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>'''
    
    # Add recent emails to the table
    for email in stats['recent_emails_list']:
        age_badge = ''
        if email['age_days'] == 'N/A':
            age_badge = '<span class="badge bg-secondary">N/A</span>'
        elif email['age_days'] <= 7:
            age_badge = f'<span class="badge bg-success">{email["age_days"]}</span>'
        elif email['age_days'] <= 30:
            age_badge = f'<span class="badge bg-warning">{email["age_days"]}</span>'
        else:
            age_badge = f'<span class="badge bg-danger">{email["age_days"]}</span>'
        
        status_badge = ''
        if email['status'] == 'Kept':
            status_badge = '<span class="badge bg-success">Kept</span>'
        elif email['status'] == 'Deleted':
            status_badge = '<span class="badge bg-danger">Deleted</span>'
        else:
            status_badge = f'<span class="badge bg-warning">{email["status"]}</span>'
        
        html_content += f'''
                                    <tr>
                                        <td><small class="text-muted">{email['from_'][:30]}{"..." if len(email['from_']) > 30 else ""}</small></td>
                                        <td><small class="text-muted">{email['to_'][:30]}{"..." if len(email['to_']) > 30 else ""}</small></td>
                                        <td><small>{email['subject'][:40]}{"..." if len(email['subject']) > 40 else ""}</small></td>
                                        <td>{age_badge}</td>
                                        <td><small>{email['size_kb']} KB</small></td>
                                        <td>{status_badge}</td>
                                    </tr>'''
    
    html_content += '''
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Top Senders and Receivers -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="bi bi-person-fill"></i> Top Senders</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Email</th>
                                                <th>Count</th>
                                            </tr>
                                        </thead>
                                        <tbody>'''
    
    for sender in stats['top_senders']:
        html_content += f'''
                                            <tr>
                                                <td><small class="text-muted">{sender['email'][:40]}{"..." if len(sender['email']) > 40 else ""}</small></td>
                                                <td><span class="badge bg-primary">{sender['count']}</span></td>
                                            </tr>'''
    
    html_content += '''
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="bi bi-people-fill"></i> Top Receivers</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Email</th>
                                                <th>Count</th>
                                            </tr>
                                        </thead>
                                        <tbody>'''
    
    for receiver in stats['top_receivers']:
        html_content += f'''
                                            <tr>
                                                <td><small class="text-muted">{receiver['email'][:40]}{"..." if len(receiver['email']) > 40 else ""}</small></td>
                                                <td><span class="badge bg-info">{receiver['count']}</span></td>
                                            </tr>'''
    
    html_content += '''
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Last Updated -->
                <div class="card">
                    <div class="card-body text-center">
                        <small class="text-muted">
                            <i class="bi bi-clock"></i> Last Updated: {last_updated}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Format the timestamps properly
    html_content = html_content.format(
        last_updated=stats['last_updated']
    )
    
    # Save to static folder
    static_file_path = os.path.join('static', 'stats.html')
    with open(static_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Static stats page generated: {static_file_path}")
    print(f"📄 File size: {len(html_content)} characters")
    return static_file_path

if __name__ == '__main__':
    print(f"🎯 GhostInbox Stats Generator")
    print(f"=" * 50)
    
    # Generate static stats page (this already calls get_web_stats())
    static_file = generate_static_stats_page()
    print(f"📁 Static stats page saved to: {static_file}")
    
    print(f"=" * 50)
    print(f"✅ Process completed successfully!")

from datetime import datetime
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_ADDRESS = os.getenv('BASE_EMAIL')
PASSWORD = os.getenv('BASE_PASSWORD')
IMAP_SERVER = 'imapmail.libero.it'

def get_email_stats():
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select('inbox')

        # Search for all emails
        status, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        # ANSI color codes
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        # Statistics tracking
        total_emails = 0
        unique_senders = set()
        unique_receivers = set()
        deleted_count = 0

        print(f"\n{BOLD}Email Statistics:{RESET}")
        print(f"{BLUE}{'-' * 135}{RESET}")
        print(f"{BOLD}{'From':<30} {'To':<30} {'Subject':<40} {'Age (days)':<12} {'Size (bytes)':<12} {'Status':<10}{RESET}")
        print(f"{BLUE}{'-' * 135}{RESET}")

        for email_id in email_ids:
            total_emails += 1
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            # Get email details
            from_ = msg.get('from', 'Unknown')
            to_ = msg.get('to', 'Unknown')
            
            # Update unique senders and receivers
            unique_senders.add(from_)
            unique_receivers.add(to_)
            
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
                    print(f"Error parsing date: {date_str}")

            # Calculate size
            size = len(msg_data[0][1])

            # Check if email should be deleted
            status = 'Kept'
            status_color = GREEN
            if isinstance(age_days, int):
                if age_days > 30:
                    mail.store(email_id, '+FLAGS', '\\Deleted')
                    status = 'Deleted'
                    status_color = RED
                    deleted_count += 1
                elif age_days > 20:
                    status_color = YELLOW

            # Print formatted output with colors
            print(f"{from_[:30]:<30} {to_[:30]:<30} {subject[:40]:<40} "
                  f"{str(age_days):<12} {size:<12} {status_color}{status:<10}{RESET}")

        # Print summary statistics
        print(f"\n{BOLD}Summary Statistics:{RESET}")
        print(f"{BLUE}{'-' * 30}{RESET}")
        print(f"{BOLD}Total Emails:{RESET} {total_emails}")
        print(f"{BOLD}Unique Senders:{RESET} {len(unique_senders)}")
        print(f"{BOLD}Unique Receivers:{RESET} {len(unique_receivers)}")
        print(f"{BOLD}Deleted Emails:{RESET} {deleted_count}")
        print(f"{BLUE}{'-' * 30}{RESET}")

        # Permanently remove deleted emails
        mail.expunge()
        mail.logout()

    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

if __name__ == '__main__':
    get_email_stats() 
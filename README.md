# GhostInbox.it 📧

> Use email without having an email

A Flask-based email viewing application that allows users to view emails sent to temporary aliases.

## 🚀 Features

- 🔒 View emails sent to temporary aliases in a easy way
- 🔍 Inspect any email sent to your alias
- 🔐 Your alias is generated with sha256 of your alias
- 📊 Email statistics and management

## 📋 Requirements

- Python 3.7+
- Flask
- python-dotenv
- imaplib (built-in)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ghostinbox.it.git
   cd ghostinbox.it
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file in the project root:
   ```bash
   FLASK_SECRET_KEY=your_secret_key
   BASE_EMAIL=your_email
   BASE_PASSWORD=your_password
   IMAP_SERVER=imapmail.myserver.it
   DOMAIN=your_domain
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

## 📧 Email Configuration

### Catch-All Setup
To forward all emails to your GhostInbox.it Base Email, you can use:
- [forwardemail.net](https://forwardemail.net) (Free service)
- Any other catch-all email service

## ⚠️ Security Notes

- 🔒 Never commit your `.env` file to version control
- 🔑 Use a strong, unique secret key in production
- 🔐 Keep your email credentials secure
- 🛡️ Regularly update dependencies for security patches

## 📊 Email Management

The application includes an email management script (`email_stats.py`) that provides:
- 📈 Email statistics
- 🗑️ Automatic cleanup of old/large emails
- 📊 Summary of unique senders and receivers

## 🔌 API Documentation

GhostInbox.it provides a REST API to programmatically access emails.

### Base URL
All API endpoints are available at: `http://your-domain/api/`

### Authentication
All API endpoints use hash-based authentication. The hash parameter must match the SHA256 hash used to generate your email alias (64 characters).

### Endpoints

#### 1. List Emails
Get a list of emails, optionally filtered by alias hash.

**Endpoint:** `GET /api/emails`

**Query Parameters:**
- `hash` (optional): Filter emails by alias hash (64 characters)
- `limit` (optional): Maximum number of emails to return (default: 10)

**Examples:**
```bash
# Get all emails (limited to 10)
curl "http://localhost:5000/api/emails"

# Get emails for a specific alias
curl "http://localhost:5000/api/emails?hash=abc123...xyz789"

# Get up to 20 emails
curl "http://localhost:5000/api/emails?limit=20"
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "emails": [
    {
      "id": "123",
      "from": "sender@example.com",
      "to": "hash@ghostinbox.it",
      "subject": "Test Email",
      "date": "Tue, 28 Oct 2025 10:00:00 +0000"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid hash format
- `500 Internal Server Error`: Server error

#### 2. Get Email Details
Get the full details of a specific email, including body content.

**Endpoint:** `GET /api/emails/<email_id>`

**Query Parameters:**
- `hash` (required): Alias hash to verify email ownership (64 characters)

**Example:**
```bash
curl "http://localhost:5000/api/emails/123?hash=abc123...xyz789"
```

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "123",
    "from": "sender@example.com",
    "to": "hash@ghostinbox.it",
    "subject": "Test Email",
    "date": "Tue, 28 Oct 2025 10:00:00 +0000",
    "body": "Email content...",
    "content_type": "text/plain"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid hash parameter
- `403 Forbidden`: Hash mismatch - email doesn't belong to this alias
- `404 Not Found`: Email not found
- `500 Internal Server Error`: Server error

### API Usage Tips

- 🔒 Always use HTTPS in production
- 🔑 Keep your hash secret - it's your authentication token
- 📝 The email list endpoint doesn't include body content for performance
- ⚡ Use the `limit` parameter to paginate results
- 🛡️ The hash verification ensures only the alias owner can view their emails

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
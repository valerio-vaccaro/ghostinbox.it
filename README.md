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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
# GhostInbox.it - Use email without having an email

A Flask-based email viewing application that allows users to view emails sent to temporary aliases.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ghostinbox.it.git
cd ghostinbox.it
``` 


2. Create and activate a virtual environment:  

```bash
python -m venv venv
source venv/bin/activate
```


3. Install required packages:

```bash
pip install -r requirements.txt
```


4. Create a `.env` file in the project root with the following variables:

```bash
FLASK_SECRET_KEY=your_secret_key
BASE_EMAIL=your_libero_email
BASE_PASSWORD=your_libero_password
```

5. Run the application:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

6. Configure a catch all email
You will need to configure a catch all email to forward all emails to your ghostinbox.it Base Email. 

You can use a service like forwardemail.net to do this. Ehi! It's works and it's free!

## Requirements

- Python 3.7+
- Flask
- python-dotenv
- imaplib (built-in)

## Features

- View emails sent to temporary aliases
- Search for emails by alias
- Secure email viewing with hash verification

## Security Notes

- Never commit your `.env` file to version control
- Use a strong, unique secret key in production
- Keep your email credentials secure
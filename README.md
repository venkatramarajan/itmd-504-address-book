# Address Book Web Application

A web-based address book application with Python Flask backend and Vue.js frontend.

## Features
- User authentication (login/register)
- Admin user management
- Address book management (CRUD operations)
- Secure password handling

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run serve
   ```

## Default Admin Credentials
- Username: admin
- Password: admin123

(Please change these credentials after first login)

## Environment Configuration

The application requires a `.env` file for configuration. If the deployment script doesn't create it automatically, you can create it manually:

1. Create a file named `.env` in the project root directory
2. Add the following content (replace the values with your actual configuration):

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://addressbook_user:your_secure_password@localhost/addressbook

# Application Security
SECRET_KEY=your-secret-key-change-this-in-production

# Optional: Application Settings
FLASK_ENV=development
FLASK_DEBUG=1
```

### Security Notes:
- Generate a secure SECRET_KEY using: `openssl rand -hex 32`
- Use strong passwords for the database
- In production, set FLASK_ENV=production and FLASK_DEBUG=0
- Keep the .env file secure and never commit it to version control

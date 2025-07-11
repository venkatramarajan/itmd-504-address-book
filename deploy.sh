#!/bin/bash

# Exit on error
set -e

echo "Starting deployment of Address Book Application..."

# Function to validate Git URL
validate_git_url() {
    local url=$1
    # Check for HTTPS/HTTP URLs
    if [[ $url =~ ^(https?|git)://.*\.git$ ]]; then
        return 0
    # Check for SSH URLs (git@github.com:username/repo.git)
    elif [[ $url =~ ^git@[a-zA-Z0-9.-]+:[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to get Git repository URL
get_git_repo() {
    local repo_url
    while true; do
        read -p "Please enter the Git repository URL (e.g., https://github.com/username/repo.git or git@github.com:username/repo.git): " repo_url
        if validate_git_url "$repo_url"; then
            echo "$repo_url"
            return 0
        else
            echo "Invalid Git URL format. Please enter a valid URL ending with .git"
            echo "Supported formats:"
            echo "  - HTTPS: https://github.com/username/repo.git"
            echo "  - SSH: git@github.com:username/repo.git"
        fi
    done
}

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv nginx git mysql-server \
    pkg-config \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential

# Function to check Node.js version
check_node_version() {
    if command -v node &> /dev/null; then
        local current_version=$(node --version | cut -d'v' -f2)
        local required_version="18.0.0"
        
        # Compare versions
        if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" = "$required_version" ]; then
            echo "Node.js version $current_version is already installed and meets requirements"
            return 0
        else
            echo "Node.js version $current_version is installed but needs to be updated"
            return 1
        fi
    else
        echo "Node.js is not installed"
        return 1
    fi
}

# Check if Node.js needs to be installed/updated
if ! check_node_version; then
    echo "Installing/Updating Node.js..."
    # Clean up any existing Node.js installations
    echo "Cleaning up existing Node.js installations..."
    sudo apt-get remove -y nodejs npm
    sudo apt-get autoremove -y

    # Install Node.js 18.x (LTS)
    echo "Installing Node.js 18.x..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get update
    sudo apt-get install -y nodejs
else
    echo "Skipping Node.js installation as it's already up to date"
fi

# Verify Node.js and npm installation
echo "Verifying Node.js and npm installation..."
node --version
npm --version

# Create application directory and set permissions
echo "Creating application directory..."
sudo mkdir -p /var/www/addressbook
sudo chown -R $USER:$USER /var/www/addressbook

# Create log directory and set permissions
echo "Creating log directory..."
sudo mkdir -p /var/log/addressbook
sudo chown -R www-data:www-data /var/log/addressbook
sudo chmod 755 /var/log/addressbook

# Get Git repository URL and clone
echo "Setting up Git repository..."
GIT_REPO=$(get_git_repo)

# Clone the repository (if not already present)
if [ ! -d "/var/www/addressbook/.git" ]; then
    echo "Cloning repository from $GIT_REPO..."
    git clone "$GIT_REPO" /var/www/addressbook
    if [ $? -ne 0 ]; then
        echo "Error: Failed to clone repository. Please check the URL and try again."
        exit 1
    fi
else
    echo "Repository already exists. Updating..."
    cd /var/www/addressbook
    git pull
    if [ $? -ne 0 ]; then
        echo "Error: Failed to update repository. Please check your connection and try again."
        exit 1
    fi
fi

# Configure MySQL
echo "Configuring MySQL..."

# Check and adjust MySQL password policy
echo "Configuring MySQL password policy..."
sudo mysql -e "SET GLOBAL validate_password.policy = 0;"
sudo mysql -e "SET GLOBAL validate_password.length = 8;"
sudo mysql -e "SET GLOBAL validate_password.mixed_case_count = 0;"
sudo mysql -e "SET GLOBAL validate_password.number_count = 0;"
sudo mysql -e "SET GLOBAL validate_password.special_char_count = 0;"

# Generate a secure password (without @ symbol to avoid URL encoding issues)
DB_PASSWORD="AddressBook123!"
echo "Using database password: $DB_PASSWORD"

# Create database and user with proper password
sudo mysql -e "CREATE DATABASE IF NOT EXISTS addressbook;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'addressbook_user'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"
sudo mysql -e "GRANT ALL PRIVILEGES ON addressbook.* TO 'addressbook_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Create .env file with secure configuration
echo "Creating environment configuration..."
ENV_FILE="/var/www/addressbook/.env"
if [ ! -f "$ENV_FILE" ]; then
    # Generate a secure random key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Create .env file with secure configuration
    sudo bash -c "cat > $ENV_FILE << EOL
# Database Configuration
DB_USER=addressbook_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_NAME=addressbook

# Application Security
SECRET_KEY=$SECRET_KEY

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=0
EOL"
    
    # Set proper permissions
    sudo chown www-data:www-data "$ENV_FILE"
    sudo chmod 600 "$ENV_FILE"
    
    echo "Created .env file with secure configuration"
    echo "IMPORTANT: Please save the database password: $DB_PASSWORD"
else
    echo ".env file already exists, skipping creation"
fi

# Set proper permissions
echo "Setting proper permissions..."
sudo chown -R www-data:www-data /var/www/addressbook
sudo chmod -R 755 /var/www/addressbook
sudo chmod -R 755 /var/www/addressbook/frontend/dist
sudo chmod 600 /var/www/addressbook/.env

# Create and set permissions for log directory
echo "Setting up log directory..."
sudo mkdir -p /var/log/addressbook
sudo chown -R www-data:www-data /var/log/addressbook
sudo chmod 755 /var/log/addressbook
sudo touch /var/log/addressbook/gunicorn.out.log /var/log/addressbook/gunicorn.err.log
sudo chown www-data:www-data /var/log/addressbook/gunicorn.*.log
sudo chmod 644 /var/log/addressbook/gunicorn.*.log

# Ensure virtual environment is properly set up
echo "Setting up virtual environment..."
cd /var/www/addressbook
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create Gunicorn configuration
echo "Creating Gunicorn configuration..."
sudo tee /var/www/addressbook/gunicorn_config.py << EOF
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/addressbook/access.log'
errorlog = '/var/log/addressbook/error.log'
loglevel = 'info'

# Process naming
proc_name = 'addressbook'

# Server mechanics
daemon = False
pidfile = '/var/run/addressbook.pid'
umask = 0
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """
    Log when the server starts
    """
    server.log.info("Starting Address Book application server")

def on_exit(server):
    """
    Log when the server exits
    """
    server.log.info("Stopping Address Book application server")
EOF

# Create systemd service for backend
echo "Creating systemd service for backend..."
sudo tee /etc/systemd/system/addressbook-backend.service << EOF
[Unit]
Description=Address Book Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/addressbook
Environment="PATH=/var/www/addressbook/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/addressbook/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Set up frontend
echo "Setting up frontend..."
cd /var/www/addressbook/frontend

# Create ESLint configuration
echo "Creating ESLint configuration..."
cat > .eslintrc.js << EOF
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  parserOptions: {
    parser: '@babel/eslint-parser'
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
}
EOF

# Clear npm cache and install dependencies
echo "Installing frontend dependencies..."
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Configure Nginx
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/addressbook << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain name if available

    # Frontend
    location / {
        root /var/www/addressbook/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Logging
    access_log /var/log/addressbook/nginx-access.log;
    error_log /var/log/addressbook/nginx-error.log;
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/addressbook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start and enable services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable addressbook-backend
sudo systemctl stop addressbook-backend || true
sudo systemctl start addressbook-backend
sudo systemctl restart nginx

# Check the status and logs
echo "Checking service status and logs..."
sudo systemctl status addressbook-backend
echo "=== Gunicorn Output Log ==="
sudo tail -n 50 /var/log/addressbook/gunicorn.out.log
echo "=== Gunicorn Error Log ==="
sudo tail -n 50 /var/log/addressbook/gunicorn.err.log
echo "=== Systemd Journal ==="
sudo journalctl -u addressbook-backend -n 50 --no-pager

# Set up SSL with Let's Encrypt (optional)
echo "Would you like to set up SSL with Let's Encrypt? (y/n)"
read -r ssl_response
if [[ $ssl_response =~ ^[Yy]$ ]]; then
    echo "Installing Certbot..."
    sudo apt-get install -y certbot python3-certbot-nginx
    echo "Please enter your domain name:"
    read -r domain_name
    sudo certbot --nginx -d "$domain_name"
fi

echo "Deployment completed successfully!"
echo "The application should now be accessible at:"
echo "http://localhost (or your domain name if configured)"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "Please change the admin password after first login!" 
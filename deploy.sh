#!/bin/bash

# Exit on error
set -e

echo "Starting deployment of Address Book Application..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm nginx

# Install Node.js 18.x (LTS)
echo "Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /var/www/addressbook
sudo chown -R $USER:$USER /var/www/addressbook

# Clone the repository (if not already present)
if [ ! -d "/var/www/addressbook/.git" ]; then
    echo "Cloning repository..."
    git clone https://github.com/yourusername/addressbook.git /var/www/addressbook
fi

# Set up Python backend
echo "Setting up Python backend..."
cd /var/www/addressbook
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service for backend
echo "Creating systemd service for backend..."
sudo tee /etc/systemd/system/addressbook-backend.service << EOF
[Unit]
Description=Address Book Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=/var/www/addressbook
Environment="PATH=/var/www/addressbook/venv/bin"
ExecStart=/var/www/addressbook/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Set up frontend
echo "Setting up frontend..."
cd /var/www/addressbook/frontend
npm install
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
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/addressbook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start and enable services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable addressbook-backend
sudo systemctl start addressbook-backend
sudo systemctl restart nginx

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
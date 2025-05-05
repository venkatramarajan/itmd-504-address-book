# Deployment Guide for Address Book Application

This guide provides instructions for deploying the Address Book application on Ubuntu LTS 24.04.

## Prerequisites

- Ubuntu LTS 24.04 server
- Sudo privileges
- Git installed
- Domain name (optional, for SSL)

## Deployment Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/addressbook.git
   cd addressbook
   ```

2. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

3. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

The script will:
- Update system packages
- Install required dependencies (Python, Node.js, Nginx)
- Set up the Python backend with systemd service
- Build and configure the Vue.js frontend
- Configure Nginx as a reverse proxy
- Optionally set up SSL with Let's Encrypt

## Manual Configuration

### Backend Configuration

The backend service runs as a systemd service. You can manage it using:
```bash
sudo systemctl status addressbook-backend  # Check status
sudo systemctl start addressbook-backend   # Start service
sudo systemctl stop addressbook-backend    # Stop service
sudo systemctl restart addressbook-backend # Restart service
```

### Nginx Configuration

The Nginx configuration is located at:
- `/etc/nginx/sites-available/addressbook`
- `/etc/nginx/sites-enabled/addressbook`

To modify the configuration:
1. Edit the configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/addressbook
   ```
2. Test the configuration:
   ```bash
   sudo nginx -t
   ```
3. Reload Nginx:
   ```bash
   sudo systemctl reload nginx
   ```

### SSL Configuration

If you didn't set up SSL during deployment, you can do it manually:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

### Backend Issues
1. Check the service status:
   ```bash
   sudo systemctl status addressbook-backend
   ```
2. View logs:
   ```bash
   sudo journalctl -u addressbook-backend
   ```

### Frontend Issues
1. Check Nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```
2. Verify frontend build:
   ```bash
   cd /var/www/addressbook/frontend
   npm run build
   ```

### Database Issues
The application uses SQLite by default. The database file is located at:
```
/var/www/addressbook/addressbook.db
```

## Security Considerations

1. Change the default admin credentials after first login
2. Update the Flask secret key in `app.py`
3. Configure firewall:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## Backup

To backup the application:
```bash
# Backup database
cp /var/www/addressbook/addressbook.db /backup/addressbook.db

# Backup configuration
cp /etc/nginx/sites-available/addressbook /backup/nginx-config
cp /etc/systemd/system/addressbook-backend.service /backup/backend-service
```

## Updating the Application

To update the application:
1. Pull the latest changes:
   ```bash
   cd /var/www/addressbook
   git pull
   ```
2. Update dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   cd frontend
   npm install
   npm run build
   ```
3. Restart services:
   ```bash
   sudo systemctl restart addressbook-backend
   sudo systemctl reload nginx
   ``` 
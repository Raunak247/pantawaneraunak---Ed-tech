# Deployment Guide

This guide explains how to deploy the Adaptive Learning Backend to production.

## Prerequisites

- Python 3.9+
- Git
- Server with SSH access (e.g., AWS EC2, Digital Ocean, etc.)
- Domain name (optional)

## Server Setup

1. **Update server packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and dependencies**:
   ```bash
   sudo apt install -y python3-pip python3-venv nginx
   ```

3. **Set up firewall** (if needed):
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

## Application Deployment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Raunak247/pantawaneraunak---Ed-tech.git
   cd pantawaneraunak---Ed-tech/Backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv backend
   source backend/bin/activate
   pip install -r requirements.txt
   ```

3. **Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

4. **Firebase setup**:
   ```bash
   mkdir -p firebase/credentials
   # Copy your firebase-credentials.json to firebase/credentials/
   ```

5. **Test the application**:
   ```bash
   cd backend
   python main.py
   # Confirm it works at http://localhost:5000
   ```

## Running as a Service

1. **Create a systemd service**:
   ```bash
   sudo nano /etc/systemd/system/adaptive-learning.service
   ```

2. **Add service configuration**:
   ```ini
   [Unit]
   Description=Adaptive Learning API
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/home/<your-username>/pantawaneraunak---Ed-tech/Backend/backend
   ExecStart=/home/<your-username>/pantawaneraunak---Ed-tech/Backend/backend/bin/python main.py
   Restart=always
   RestartSec=5
   Environment="PATH=/home/<your-username>/pantawaneraunak---Ed-tech/Backend/backend/bin"

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**:
   ```bash
   sudo systemctl enable adaptive-learning
   sudo systemctl start adaptive-learning
   sudo systemctl status adaptive-learning
   ```

## Setting Up Nginx (Optional)

1. **Create Nginx configuration**:
   ```bash
   sudo nano /etc/nginx/sites-available/adaptive-learning
   ```

2. **Add site configuration**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable the site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/adaptive-learning /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Set up SSL with Certbot** (optional):
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Updating the Deployment

To update the application with new changes:

```bash
cd pantawaneraunak---Ed-tech/Backend
git pull
source backend/bin/activate
pip install -r requirements.txt
sudo systemctl restart adaptive-learning
```

## Monitoring Logs

```bash
sudo journalctl -u adaptive-learning -f
```
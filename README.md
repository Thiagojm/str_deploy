# Deploy/Host a Streamlit App on a Linode Server using Nginx with SSL

This tutorial will guide you on how to deploy a Streamlit app on a Linode server using Nginx with SSL.

## Step 1: Set Up the Linode Server

Create a Linode server. In this case, we're using Ubuntu.

Access the server via the "Launch LISH Console".

## Step 2: Secure Your Server

### Create a New User

Replace `newuser` with your desired username. Type:

```bash
sudo adduser newuser
sudo passwd newuser
sudo usermod -aG sudo newuser
```

Close the console and re-login using your new user in the terminal:

```bash
ssh newuser@your_linode_ip
```

### Set Up the Firewall

Install UFW and allow SSH, HTTP, and TCP connections on port 443.

```bash
sudo apt-get install -y ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status
```

## Step 3: Install uv Package Manager

Install uv package manager using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add uv to your PATH by sourcing the shell configuration:

```bash
source ~/.cargo/env
```

Or restart your terminal session to ensure uv is available in your PATH.

**Alternative installation methods:**

If you prefer to install via pip:
```bash
pip install uv
```

Or using your system package manager:
```bash
# On Ubuntu/Debian
curl -LsSf https://astral.sh/uv/install.sh | sh

# On macOS with Homebrew
brew install uv

# On Windows with pip
pip install uv
```

## Step 4: Install Dependencies

Install Nginx and Git:

```bash
sudo apt-get -y install nginx git
```

## Step 5: Clone Your App Repository

Clone your app repository and navigate into the app folder:

```bash
git clone your_app
cd your_app
```

Install the required dependencies using uv sync (this will automatically create a virtual environment and install dependencies):

```bash
uv sync
```

Alternatively, if you prefer to use requirements.txt:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Step 6: Create Streamlit Configuration Files

Create .streamlit/secrets.toml and .streamlit/config.toml:

```bash
nano .streamlit/secrets.toml
```

Save your secrets inside this file.

Next, open the config.toml:

```bash
nano .streamlit/config.toml
```

Add the following configuration:

```toml
[server]
port = 8501
headless = true
[browser]
serverAddress = "localhost"
gatherUsageStats = false
serverPort = 8501
```

## Step 7: Create a System Service for Your Streamlit App

Replace your_service with your service name:

```bash
sudo nano /etc/systemd/system/your_service.service
```

Add the following configuration, replacing the paths and Python script name as needed:

**Note:** To find the correct path to `uv`, run `which uv` in your terminal. Common paths are:
- `/usr/local/bin/uv` (if installed via installer script)
- `/home/newuser/.local/bin/uv` (if installed via pip with --user)
- `/usr/bin/uv` (if installed via system package manager)

```ini
[Unit]
Description=Your App
After=network.target

[Service]
ExecStart=/home/newuser/.local/bin/uv run streamlit run /home/newuser/your_app/main.py
WorkingDirectory=/home/newuser/your_app
User=newuser
Group=newuser
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload the system daemon, enable and start your service, then check its status:

```bash
sudo systemctl daemon-reload
sudo systemctl enable your_service.service
sudo systemctl start your_service.service
sudo systemctl status your_service.service
```

## Step 8: Test Your Server

Allow connections on port 8501, then check the UFW status:

```bash
sudo ufw allow 8501
sudo ufw status
```

Visit your_linode_ip:8501 in your web browser. If everything is working fine, disable the port 8501:

```bash
sudo ufw delete allow 8501
sudo ufw status
```

## Step 9: Set Up Nginx

Create a temporary SSL certificate:

```bash
# Run these commands inside your_app folder
mkdir certs 
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem
```

Configure Nginx:

```bash
sudo nano /etc/nginx/sites-available/streamlit
```

Add the following configuration, replacing the paths, IP address, and port as needed:

```nginx
upstream ws-backend {
    server localhost:8501;
}

server {
    listen 80;
    server_name your_linode_ip;
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your_linode_ip;
    ssl_certificate /home/newuser/your_app/certs/cert.pem;
    ssl_certificate_key /home/newuser/your_app/certs/key.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;
    client_max_body_size 100M;

    location / {
        proxy_pass http://ws-backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Link the configuration file, check the configuration, and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled
sudo nginx -t
sudo service nginx reload
```

Visit your_linode_ip in your web browser. You should get a warning; accept the risk for now.

## Step 10: Add a Domain

Purchase a domain from a provider like Namecheap. Go to your dashboard on your provider's site, click "Manage", then add a new A Record with Host = @ and Value = your_linode_ip.

Back on the Linode terminal, modify the Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/streamlit
```

Change the server_name to your domain name, then reload Nginx:

```bash
sudo service nginx reload
```

## Step 11: Install SSL Certificates with Certbot

Follow the guide at https://certbot.eff.org/instructions to install SSL certificates.

```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
```

Follow the prompts to complete the installation.

Voilà! Your Streamlit app is now deployed on your Linode server.
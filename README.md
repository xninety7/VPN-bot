****VPN Operations Bot ****

An AI-powered Lark chatbot that automates V2Ray user provisioning and server management across multiple Alibaba Cloud ECS instances.

**Overview**

Managing V2Ray users manually required SSHing into servers, navigating interactive menus, and manually adding DNS records. This bot automates the entire pipeline through a simple Lark chat command.

**Before:**

1. Log into name.com → add DNS A record manually
2. Wait for DNS propagation
3. SSH into server → run 233boy script → navigate menus
4. Copy the VMess URL manually

**After:**

Just type "add user <name_of_the_user> on <location>

**Architecture**                            

                                            Lark Chat
                                                ↓
                                    bot.neweb.me (Caddy HTTPS) 
                                                ↓
                              Flask Webhook Server (port 8000)    
                                                ↓
                                         Command Parser
                                                ↓
                                        ┌─────────────────────────────┐
                                        │  name.com DNS API           │  → Creates subdomain A record
                                        │  DNS Propagation Polling    │  → Waits until resolved
                                        │  SSH via Paramiko           │  → Connects to V2Ray servers
                                        │  233boy v2ray script        │  → Provisions user config
                                        └─────────────────────────────┘
                                                ↓
                                      Lark Message Card (reply)
**Features**
              * Create V2Ray users (VMess-WS-TLS) on PH, HK, or both servers
              * Automatic DNS record creation via name.com API
              * DNS propagation polling before provisioning
              * Delete V2Ray users and DNS records
              * List active users per server
              * Restart services (v2ray, caddy) via SSH
              * Tail logs remotely
              * Lark interactive message cards
              * Webhook token verification
              * systemd service with auto-restart

Project Structure
                    vpn-bot/
                    
                      ├─ main.py           # Flask app, Lark webhook endpoint
                      ├─ claude_agent.py   # Command parser and router
                      ├─ tools.py          # Tool executor (create, delete, restart, logs)
                      ├─ ssh_client.py     # SSH helper using Paramiko
                      ├─ namecom.py        # name.com DNS API client
                      ├─ lark_client.py    # Lark messaging client (text + cards)
                      └─ .env              # Environment variables (not committed)

**Bot Commands**
Command	Description
* add user <name_of_the_user> on <location|all> 	Create a new V2Ray VMess-WS-TLS user
* delete user <name> on <ph|hk|both>	Delete a V2Ray user and DNS record
* list users on <ph|hk>	List all active V2Ray users
* restart v2ray on <ph|hk>	Restart V2Ray service
* restart caddy on <ph|hk>	Restart Caddy service
* logs v2ray on <ph|hk>	Get last 50 lines of V2Ray logs
* logs caddy on <ph|hk> <n>	Get last N lines of logs
* help	Show command reference


**Tech Stack**
* Python 3.8 — main language
* Flask — webhook server
* Paramiko — SSH automation
* Requests — HTTP client (name.com API, Lark API)
* Caddy — reverse proxy with automatic TLS
* Lark Open Platform — custom app with webhook events
* name.com API — programmatic DNS management
* 233boy V2Ray script — V2Ray server management
* systemd — process management
* Alibaba Cloud ECS — hosting (CentOS 7.9)

Setup
**Prerequisites**
CentOS 7.9 ECS instance with public IP
Python 3.8 (built from source on CentOS 7)
Caddy v2
SSH key access to V2Ray servers
name.com API credentials
Lark Developer account
1. Clone the repo: **git clone git@github.com:xninety7/VPN-bot.git**
   cd VPN-bot
2. Install dependencies
   pip3.8 install flask anthropic paramiko requests python-dotenv 

3. Configure environment
   cp .env.example .env
   vi .env

Fill in your values:
          env
          ANTHROPIC_AUTH_TOKEN=sk-ant-oat-...
          NAMECOM_USER=your_namecom_username
          NAMECOM_TOKEN=your_namecom_api_token
          LARK_APP_ID=cli_xxxxxxx
          LARK_APP_SECRET=xxxxxxx
          LARK_VERIFY_TOKEN=xxxxxxx
          PH_HOST=x.x.x.x
          PH_USER=root
          HK_HOST=x.x.x.x
          HK_USER=root
          SSH_KEY_PATH=/root/.ssh/v2ray_monitor
          4. Configure Caddy
          mkdir -p /etc/caddy
          cat > /etc/caddy/Caddyfile << 'EOF'
          bot.domain.me {
              reverse_proxy 127.0.0.1:8000
          }
          EOF
          
5. Set up systemd service

          cat > /etc/systemd/system/vpn-bot.service << 'EOF'
          [Unit]
          Description=VPN Ops Bot
          After=network.target
          
          [Service]
          User=root
          WorkingDirectory=/opt/vpn-bot
          ExecStart=/usr/local/bin/python3.8 /opt/vpn-bot/main.py
          Restart=always
          RestartSec=5
          
          [Install]
          WantedBy=multi-user.target
          EOF

systemctl daemon-reload
systemctl enable vpn-bot
systemctl start vpn-bot


6. Configure Lark App
              * Go to open.larksuite.com → Create App → Custom App
              * Credentials & Basic Info → copy App ID and App Secret to .env
              * Events & Callbacks → enable webhook → set URL to https://bot.neweb.me/webhook
              * Subscribe to event: im.message.receive_v1
              * Permissions & Scopes → add im:message, im:message.p2p_msg, im:message:send_as_bot
              * Version Management → release the app

**How V2Ray User Creation Works**
              1. Parse command → extract username and server
              2. Call name.com API → POST /v4/domains/neweb.me/records
                 → creates alice100.neweb.me A record → server IP
              3. Poll DNS every 15s → socket.gethostbyname()
                 → wait until resolves correctly (max 5 min)
              4. SSH into server via Paramiko
                 → echo "y" | v2ray add ws alice100.neweb.me
              5. Strip ANSI codes from output
                 → extract vmess:// URL
              6. Send Lark card with domain, protocol, status, URL

**Managing the Bot**

# View live logs
journalctl -u vpn-bot -f

# Restart
systemctl restart vpn-bot

# Stop
systemctl stop vpn-bot

# Check status
systemctl status vpn-bot


**Notes**
The 233boy V2Ray script is non-interactive via echo "y" | v2ray add ws <domain>
DNS must propagate before provisioning — the script validates DNS before proceeding
Lark auto-converts domains to hyperlinks — the parser strips markdown links before processing
The bot uses token verification to reject unauthorized webhook requests
CentOS 7 requires building OpenSSL 1.1.1w and Python 3.8 from source due to EOL package repos

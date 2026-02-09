#!/bin/bash
# Fixed installation script for Kali Linux

echo "[*] Installing APayloadMaster - Fixed Version"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}[*] Running as non-root user${NC}"
fi

# Update system
echo -e "${YELLOW}[*] Updating system packages...${NC}"
sudo apt update

# Install system dependencies
echo -e "${YELLOW}[*] Installing system tools...${NC}"
sudo apt install -y python3 python3-pip python3-venv git wget curl default-jdk apktool upx-ucl

# Install Metasploit if not present
if ! command -v msfvenom &> /dev/null; then
    echo -e "${YELLOW}[*] Installing Metasploit Framework...${NC}"
    sudo apt install -y metasploit-framework
fi

# Install ngrok
echo -e "${YELLOW}[*] Installing ngrok...${NC}"
if [ ! -f "/usr/local/bin/ngrok" ]; then
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    echo -e "${GREEN}[+] Ngrok installed${NC}"
else
    echo -e "${GREEN}[+] Ngrok already installed${NC}"
fi

# Create virtual environment
echo -e "${YELLOW}[*] Setting up Python virtual environment...${NC}"
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip3 install --upgrade pip

# Create working requirements file
cat > requirements_working.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
qrcode==7.4.2
pycryptodome==3.19.0
cryptography==41.0.7
pillow-simd==10.0.0
EOF

pip3 install -r requirements_working.txt

# Create directories
echo -e "${YELLOW}[*] Creating directory structure...${NC}"
mkdir -p output/payloads output/bound output/encrypted output/obfuscated
mkdir -p server/uploads downloads logs

# Create debug keystore for Android
echo -e "${YELLOW}[*] Creating Android debug keystore...${NC}"
if [ ! -f "debug.keystore" ]; then
    keytool -genkey -v -keystore debug.keystore \
        -alias androiddebugkey -keyalg RSA \
        -keysize 2048 -validity 10000 \
        -storepass android -keypass android \
        -dname "CN=Android Debug,O=Android,C=US" \
        -noprompt 2>/dev/null || true
fi

# Make scripts executable
chmod +x apayloadmaster.py

# Create symlink for easy access
sudo ln -sf "$(pwd)/apayloadmaster.py" /usr/local/bin/apayloadmaster 2>/dev/null || true

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║        INSTALLATION COMPLETE!                ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${YELLOW}[*] To start the tool:${NC}"
echo -e "    source venv/bin/activate"
echo -e "    python3 apayloadmaster.py"
echo ""
echo -e "${YELLOW}[*] Or use the shortcut:${NC}"
echo -e "    apayloadmaster"
echo ""
echo -e "${YELLOW}[*] Note: Configure ngrok with your auth token:${NC}"
echo -e "    ngrok config add-authtoken YOUR_TOKEN_HERE"

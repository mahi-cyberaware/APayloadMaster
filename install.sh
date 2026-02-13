#!/bin/bash
# Fixed installation script for Kali Linux / Termux (with adjustments)
# Now includes extra tunnel tools: ngrok, localxpose, cloudflared

echo "[*] Installing APayloadMaster - Enhanced Edition"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect platform
if [[ -n "$PREFIX" ]] && [[ "$PREFIX" == *"com.termux"* ]]; then
    TERMUX=true
    echo -e "${YELLOW}[*] Termux detected${NC}"
else
    TERMUX=false
fi

# Update system
echo -e "${YELLOW}[*] Updating system packages...${NC}"
if [ "$TERMUX" = true ]; then
    pkg update -y && pkg upgrade -y
else
    sudo apt update
fi

# Install system dependencies
echo -e "${YELLOW}[*] Installing system tools...${NC}"
if [ "$TERMUX" = true ]; then
    pkg install -y python python-pip python3 python3-pip git wget curl openjdk-17 apktool upx
    pkg install -y openssh  # for Serveo/Pinggy
else
    sudo apt install -y python3 python3-pip python3-venv git wget curl default-jdk apktool upx-ucl openssh-client
fi

# Install Metasploit if not present (Kali only)
if [ "$TERMUX" = false ] && ! command -v msfvenom &> /dev/null; then
    echo -e "${YELLOW}[*] Installing Metasploit Framework...${NC}"
    sudo apt install -y metasploit-framework
fi

# Install ngrok
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}[*] Installing ngrok...${NC}"
    if [ "$TERMUX" = true ]; then
        pkg install -y ngrok
    else
        wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
        tar -xzf ngrok-v3-stable-linux-amd64.tgz
        sudo mv ngrok /usr/local/bin/
        rm ngrok-v3-stable-linux-amd64.tgz
    fi
    echo -e "${GREEN}[+] Ngrok installed${NC}"
else
    echo -e "${GREEN}[+] Ngrok already installed${NC}"
fi

# Install LocalXpose
if ! command -v localxpose &> /dev/null && ! command -v loclx &> /dev/null; then
    echo -e "${YELLOW}[*] Installing LocalXpose...${NC}"
    if [ "$TERMUX" = true ]; then
        pkg install -y localxpose
    else
        wget -q https://localxpose.io/downloads/linux/amd64 -O loclx
        chmod +x loclx
        sudo mv loclx /usr/local/bin/loclx
    fi
    echo -e "${GREEN}[+] LocalXpose installed${NC}"
fi

# Install Cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}[*] Installing Cloudflare Tunnel (cloudflared)...${NC}"
    if [ "$TERMUX" = true ]; then
        pkg install -y cloudflared
    else
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
        chmod +x cloudflared
        sudo mv cloudflared /usr/local/bin/
    fi
    echo -e "${GREEN}[+] Cloudflared installed${NC}"
fi

# Create virtual environment (skip for Termux, use --system-site-packages if needed)
if [ "$TERMUX" = false ]; then
    echo -e "${YELLOW}[*] Setting up Python virtual environment...${NC}"
    python3 -m venv venv --system-site-packages
    source venv/bin/activate
fi

# Install Python dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip3 install --upgrade pip

cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
qrcode==7.4.2
pycryptodome==3.19.0
cryptography==41.0.7
pillow-simd==10.0.0
EOF

pip3 install -r requirements.txt

# Create directories
echo -e "${YELLOW}[*] Creating directory structure...${NC}"
mkdir -p output/payloads output/bound output/encrypted output/obfuscated
mkdir -p server/uploads downloads logs tools

# Create debug keystore for Android
if [ ! -f "debug.keystore" ]; then
    echo -e "${YELLOW}[*] Creating Android debug keystore...${NC}"
    if command -v keytool &> /dev/null; then
        keytool -genkey -v -keystore debug.keystore \
            -alias androiddebugkey -keyalg RSA \
            -keysize 2048 -validity 10000 \
            -storepass android -keypass android \
            -dname "CN=Android Debug,O=Android,C=US" \
            -noprompt 2>/dev/null || true
    else
        echo -e "${YELLOW}[!] keytool not found, skipping keystore creation${NC}"
    fi
fi

# Make script executable
chmod +x main.py

# Create symlink for easy access
if [ "$TERMUX" = false ]; then
    sudo ln -sf "$(pwd)/main.py" /usr/local/bin/apayloadmaster 2>/dev/null || true
    echo -e "${GREEN}[+] Symlink created: apayloadmaster${NC}"
else
    # Termux: create script in $PREFIX/bin
    mkdir -p $PREFIX/bin
    echo "#!/bin/bash" > $PREFIX/bin/apayloadmaster
    echo "cd $(pwd) && python3 main.py" >> $PREFIX/bin/apayloadmaster
    chmod +x $PREFIX/bin/apayloadmaster
    echo -e "${GREEN}[+] Termux script created: apayloadmaster${NC}"
fi

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║        INSTALLATION COMPLETE!                ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${YELLOW}[*] To start the tool:${NC}"
if [ "$TERMUX" = false ]; then
    echo -e "    source venv/bin/activate"
fi
echo -e "    python3 main.py"
echo ""
echo -e "${YELLOW}[*] Or use the shortcut:${NC}"
echo -e "    apayloadmaster"
echo ""
echo -e "${YELLOW}[*] Next steps:${NC}"
echo -e "    1. Get a free ngrok token from https://dashboard.ngrok.com"
echo -e "    2. Get a LocalXpose token from https://localxpose.io"
echo -e "    3. For Cloudflare Tunnel, get a token from Zero Trust dashboard"
echo -e "    4. Run the tool and enter your tokens when prompted"

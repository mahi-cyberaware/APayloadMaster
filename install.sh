#!/bin/bash
# APayloadMaster Installer (Updated with tunnel binaries and apktool upgrade)
# For Kali Linux

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[*] Installing APayloadMaster on Kali...${NC}"

# System packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git wget curl unzip \
    default-jdk upx-ucl sqlite3 libffi-dev libssl-dev python3-dev \
    build-essential openssh-client steghide android-sdk-build-tools \
    metasploit-framework

# -------------------- Tunnel Tools Installation --------------------
echo -e "${BLUE}[*] Installing tunneling tools...${NC}"

# NGROK
if ! command -v ngrok &> /dev/null; then
    echo "[*] Installing ngrok..."
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
else
    echo "[+] ngrok already installed"
fi

# LOCALXPOSE
if ! command -v loclx &> /dev/null; then
    echo "[*] Installing LocalXpose..."
    wget -q https://api.localxpose.io/api/v2/downloads/loclx-linux-amd64.zip
    unzip -q loclx-linux-amd64.zip
    sudo mv loclx /usr/local/bin/
    rm loclx-linux-amd64.zip
else
    echo "[+] LocalXpose already installed"
fi

# CLOUDFLARED
if ! command -v cloudflared &> /dev/null; then
    echo "[*] Installing Cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb > /dev/null 2>&1
    rm cloudflared-linux-amd64.deb
    # Fix any missing dependencies
    sudo apt install -f -y > /dev/null 2>&1
else
    echo "[+] Cloudflared already installed"
fi

# Serveo and Pinggy use SSH, which is already installed.

# -------------------- Upgrade apktool to latest version --------------------
echo -e "${BLUE}[*] Checking apktool version...${NC}"
current_apktool_version=$(apktool --version 2>/dev/null | head -n1 | sed 's/[^0-9.]//g')
required_version="2.9.2"

if [ -z "$current_apktool_version" ]; then
    echo "[!] apktool not found. Installing..."
    sudo apt install -y apktool
    current_apktool_version=$(apktool --version 2>/dev/null | head -n1 | sed 's/[^0-9.]//g')
fi

# Compare versions (simple string compare, but we need numeric)
# We'll use a function to compare version numbers.
version_ge() {
    # Returns 0 if $1 >= $2
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

if version_ge "$current_apktool_version" "$required_version"; then
    echo -e "${GREEN}[+] apktool version $current_apktool_version is sufficient.${NC}"
else
    echo -e "${YELLOW}[*] Upgrading apktool to latest version...${NC}"
    # Download latest apktool jar from official source
    LATEST_URL=$(curl -s https://api.github.com/repos/iBotPeaches/Apktool/releases/latest | grep "browser_download_url.*jar" | cut -d '"' -f 4)
    if [ -n "$LATEST_URL" ]; then
        wget -q "$LATEST_URL" -O apktool.jar
        sudo mv apktool.jar /usr/local/bin/apktool.jar
        # Create wrapper script
        sudo tee /usr/local/bin/apktool > /dev/null << 'EOF'
#!/bin/bash
java -jar /usr/local/bin/apktool.jar "$@"
EOF
        sudo chmod +x /usr/local/bin/apktool
        echo -e "${GREEN}[+] apktool upgraded to latest version.${NC}"
    else
        echo -e "${RED}[!] Failed to fetch latest apktool. Please upgrade manually.${NC}"
    fi
fi

# -------------------- Python environment --------------------
echo -e "${BLUE}[*] Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# -------------------- Android debug keystore --------------------
echo -e "${BLUE}[*] Creating Android debug keystore...${NC}"
if [ ! -f "debug.keystore" ]; then
    keytool -genkey -v -keystore debug.keystore -alias androiddebugkey \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass android -keypass android \
        -dname "CN=Android Debug,O=Android,C=US" 2>/dev/null || true
fi

# -------------------- Create directories --------------------
mkdir -p output/{payloads,bound,encrypted,obfuscated,evaded,persistent,distribution}
mkdir -p server/uploads downloads logs tools config assets/templates

# -------------------- Symlink for easy execution --------------------
sudo ln -sf "$(pwd)/main.py" /usr/local/bin/apayloadmaster 2>/dev/null || true

echo -e "${GREEN}[+] Installation complete! Run: source venv/bin/activate && python3 main.py${NC}"

#!/bin/bash
# APayloadMaster Installation Script
# For Kali Linux and Termux
# Includes all dependencies: Python packages, ngrok, localxpose, cloudflared, steghide, apktool, zipalign, apksigner

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                 APayloadMaster v3.1                      ║
║      Advanced Payload Generator with Pinggy.io Support   ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[+]${NC} $1"; }
print_error() { echo -e "${RED}[!]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# Detect platform
detect_platform() {
    if [ -d "/data/data/com.termux" ]; then
        echo "termux"
    elif [ -f "/etc/debian_version" ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

check_root() {
    if [ "$EUID" -eq 0 ]; then 
        print_warning "Running as root. Some operations may require sudo."
    fi
}

# Install dependencies for Debian/Kali
install_debian_deps() {
    print_status "Updating package list..."
    sudo apt update -y
    
    print_status "Installing system dependencies..."
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        wget \
        curl \
        default-jdk \
        apktool \
        upx-ucl \
        sqlite3 \
        libffi-dev \
        libssl-dev \
        python3-dev \
        build-essential \
        openssh-client \
        steghide \
        android-sdk-build-tools   # provides zipalign, apksigner
    
    # Check for Metasploit
    if ! command -v msfvenom &> /dev/null; then
        print_status "Installing Metasploit Framework..."
        sudo apt install -y metasploit-framework
    fi
}

# Install dependencies for Termux
install_termux_deps() {
    print_status "Updating Termux packages..."
    pkg update -y
    
    print_status "Installing Termux dependencies..."
    pkg install -y \
        python \
        python-pip \
        git \
        wget \
        curl \
        openjdk-17 \
        apktool \
        sqlite \
        libffi \
        openssl \
        binutils \
        openssh \
        steghide \
        android-tools   # provides zipalign (?), apksigner might be separate
    
    # Install Metasploit for Termux
    if ! command -v msfvenom &> /dev/null; then
        print_status "Installing Metasploit for Termux..."
        pkg install -y unstable-repo
        pkg install -y metasploit
    fi
}

# Download and install ngrok
install_ngrok() {
    if command -v ngrok &> /dev/null; then
        print_success "ngrok already installed"
        return
    fi
    print_status "Installing ngrok..."
    if [ "$PLATFORM" = "termux" ]; then
        pkg install -y ngrok
    else
        wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
        tar -xzf ngrok-v3-stable-linux-amd64.tgz
        sudo mv ngrok /usr/local/bin/
        rm ngrok-v3-stable-linux-amd64.tgz
    fi
    print_success "ngrok installed"
}

# Download and install LocalXpose
install_localxpose() {
    if command -v localxpose &> /dev/null || command -v loclx &> /dev/null; then
        print_success "LocalXpose already installed"
        return
    fi
    print_status "Installing LocalXpose..."
    if [ "$PLATFORM" = "termux" ]; then
        pkg install -y localxpose
    else
        wget -q https://localxpose.io/downloads/linux/amd64 -O loclx
        chmod +x loclx
        sudo mv loclx /usr/local/bin/loclx
    fi
    print_success "LocalXpose installed"
}

# Download and install Cloudflared
install_cloudflared() {
    if command -v cloudflared &> /dev/null; then
        print_success "cloudflared already installed"
        return
    fi
    print_status "Installing cloudflared..."
    if [ "$PLATFORM" = "termux" ]; then
        pkg install -y cloudflared
    else
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
        chmod +x cloudflared
        sudo mv cloudflared /usr/local/bin/
    fi
    print_success "cloudflared installed"
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    if [ -d "venv" ]; then
        rm -rf venv
    fi
    python3 -m venv venv
    source venv/bin/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    print_status "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Fallback
        pip install Flask==2.3.3 Flask-CORS==4.0.0 requests==2.31.0 qrcode==7.4.2 pycryptodome==3.19.0 cryptography==41.0.7 pillow==10.1.0 pinggy==0.1.5
    fi
    print_success "Python environment setup complete"
}

# Create necessary directories
setup_project_structure() {
    print_status "Creating project directories..."
    mkdir -p output/payloads output/bound output/encrypted output/obfuscated
    mkdir -p server/uploads downloads logs tools config
    print_success "Project structure created"
}

# Create Android debug keystore
setup_android_keystore() {
    print_status "Creating Android debug keystore..."
    if [ ! -f "debug.keystore" ]; then
        keytool -genkey -v \
            -keystore debug.keystore \
            -alias androiddebugkey \
            -keyalg RSA \
            -keysize 2048 \
            -validity 10000 \
            -storepass android \
            -keypass android \
            -dname "CN=Android Debug,O=Android,C=US" \
            -noprompt 2>/dev/null || print_warning "Could not create keystore. Android signing may not work."
    fi
}

# Create sample Pinggy credentials file
create_pinggy_config() {
    if [ ! -f "config/pinggy_creds.json" ]; then
        cat > config/pinggy_creds.json << 'EOF'
{
    "token": "your_token_here",
    "domain": "your_domain_here",
    "server": "pro.pinggy.io"
}
EOF
        print_warning "Edit config/pinggy_creds.json with your Pinggy Pro details"
    fi
}

# Create symlink for easy access
setup_symlink() {
    print_status "Setting up system symlink..."
    if [ "$PLATFORM" = "termux" ]; then
        mkdir -p $PREFIX/bin
        echo "#!/bin/bash" > $PREFIX/bin/apayloadmaster
        echo "cd $(pwd) && python3 main.py" >> $PREFIX/bin/apayloadmaster
        chmod +x $PREFIX/bin/apayloadmaster
        print_success "Termux script created: apayloadmaster"
    else
        sudo ln -sf "$(pwd)/main.py" /usr/local/bin/apayloadmaster 2>/dev/null || true
        sudo chmod +x /usr/local/bin/apayloadmaster 2>/dev/null || true
        print_success "Symlink created: apayloadmaster"
    fi
}

# Main installation
main() {
    check_root
    PLATFORM=$(detect_platform)
    print_status "Detected platform: $PLATFORM"
    
    case $PLATFORM in
        "debian")
            install_debian_deps
            ;;
        "termux")
            install_termux_deps
            ;;
        *)
            print_error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
    
    install_ngrok
    install_localxpose
    install_cloudflared
    setup_python_env
    setup_project_structure
    setup_android_keystore
    create_pinggy_config
    setup_symlink
    
    chmod +x main.py
    
    print_success "Installation completed successfully!"
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
    echo -e "║             APayloadMaster is ready!                        ║"
    echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}[*] To start:${NC}"
    echo "    source venv/bin/activate"
    echo "    python3 main.py"
    echo "    # or just: apayloadmaster"
    echo ""
    echo -e "${YELLOW}[*] Don't forget to edit config/pinggy_creds.json with your Pinggy Pro token!${NC}"
}

main

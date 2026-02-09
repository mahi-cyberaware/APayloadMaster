
# APayloadMaster 🔧

[![GitHub](https://img.shields.io/badge/GitHub-mahi.cyberaware-blue)](https://github.com/mahi.cyberaware)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Termux-orange)](https://www.kali.org)

Advanced Payload Generator with Localhost & Port Forwarding Support for Kali Linux and Termux.

> ⚠️ **WARNING**: For Educational & Authorized Penetration Testing Only!

## 📦 Features

### 🎯 Payload Creation
- **Multiple Platforms**: Android APK, Windows EXE, Linux ELF, Python scripts
- **Connection Methods**: 
  - Localhost (Direct connection)
  - Ngrok Port Forwarding
  - Cloudflare Tunnel
  - Serveo SSH Tunneling
- **Advanced Options**:
  - Auto-permissions for Android
  - Encryption (AES, XOR)
  - Code Obfuscation
  - AV Evasion techniques
  - Persistence mechanisms

### 📱 Binding & Distribution
- QR Code generation for downloads
- HTTP file server with QR codes
- Steganography (hide in images)
- Email/SMS distribution templates
- Social media sharing templates

### 🔧 Technical Features
- Database tracking (SQLite)
- Web interface (Flask)
- REST API
- Multi-threaded servers
- Logging system

## 🚀 Quick Start

### Installation (Kali Linux)
```bash
# Clone repository
git clone https://github.com/mahi.cyberaware/APayloadMaster.git
cd APayloadMaster

# Run installation script
chmod +x install.sh
sudo ./install.sh

# Activate virtual environment
source venv/bin/activate

# Run the tool
python3 main.py
# APayloadMaster

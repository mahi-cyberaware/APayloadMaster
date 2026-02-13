# APayloadMaster 🔧

[![GitHub](https://img.shields.io/badge/GitHub-mahi.cyberaware-blue)](https://github.com/mahi.cyberaware)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Termux-orange)](https://www.kali.org)
[![Version](https://img.shields.io/badge/Version-3.1-brightgreen)]()

**Advanced Payload Generator** with Localhost & Port Forwarding Support for **Kali Linux** and **Termux**.

> ⚠️ **WARNING**: For **Educational & Authorized Penetration Testing Only**!  
> Unauthorised use may be illegal. You are responsible for complying with all applicable laws.

---

## 📦 **Features**

### 🎯 **Payload Creation**
- **Multiple Platforms**  
  Android APK, Windows EXE/DLL, Linux ELF, Python, PowerShell, Bash
- **Connection Methods**  
  - Localhost (direct)  
  - **Ngrok** – TCP tunneling  
  - **LocalXpose** – instant TCP/HTTP tunnels  
  - **Pinggy** – SSH‑based public URLs  
  - **Cloudflare Tunnel** – via `cloudflared`  
  - **Serveo** – legacy SSH forwarding  
  - **Custom LHOST** – manual entry  
- **Advanced Options**  
  - Custom output filenames  
  - AES / XOR encryption  
  - Python code obfuscation  
  - UPX packing & junk‑byte insertion (AV evasion)  
  - Persistence mechanisms (registry, crontab, .bashrc)  
  - Auto‑permissions for Android (instructions provided)

### 🧩 **Binding & Distribution**
- **QR Code** generation for instant download  
- **HTTP file server** with directory listing  
- **Steganography** – hide payloads inside images (`steghide`)  
- **Windows Shortcut** (`.url`) creation  
- **Android launcher** template  
- **Email / SMS / Social‑Media** distribution templates  

### 🧰 **Tunnel Automation**
- **Auto‑download** of `ngrok`, `loclx`, `cloudflared` if missing  
- **Token prompts** for authenticated tunnels (ngrok, LocalXpose, Cloudflare)  
- **Background tunnel management** – no separate terminal needed  

### 🛠 **Listener**
- **Metasploit multi/handler** integration  
- **Correct payload selection** per target type (Android, Windows, Linux, etc.)  
- Automatic `.rc` file generation & background execution  

### 📱 **Termux Support**
- Full installation script for Termux (using `pkg`)  
- Works without root on Android devices  

---

## 🚀 **Quick Start**

### **1. Installation**

#### **Kali Linux**
```bash
git clone https://github.com/mahi-cyberaware/APayloadMaster.git
cd APayloadMaster
chmod +x install.sh
sudo ./install.sh          # installs dependencies, tools, Python venv
source venv/bin/activate
python3 main.py

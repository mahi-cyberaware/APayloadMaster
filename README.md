# APayloadMaster 🔧

[![GitHub](https://img.shields.io/badge/GitHub-mahi.cyberaware-blue)](https://github.com/mahi.cyberaware)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Termux-orange)](https://www.kali.org)
[![Version](https://img.shields.io/badge/Version-3.1-brightgreen)]()

**Advanced Payload Generator** with Localhost & Port Forwarding Support for **Kali Linux** and **Termux**.

> ⚠️ **WARNING**: For **Educational & Authorized Penetration Testing Only**!  
> Unauthorised use may be illegal. You are responsible for complying with all applicable laws.

---
Author: mahi.cyberaware

APayloadMaster is a professional security assessment tool that simplifies the creation, binding, and distribution of payloads for authorized penetration testing. It integrates multiple port‑forwarding services (Ngrok, Serveo, LocalXpose, Pinggy, Cloudflare) and provides a rich set of features for post‑exploitation.

## 🚀 Features

- **Payload Generation**  
  Android APK, Windows EXE/DLL, Linux ELF, Python, PowerShell, Bash scripts.

- **Multiple Tunnels**  
  - Localhost  
  - Ngrok (auto‑download + token)  
  - Serveo  
  - LocalXpose  
  - **Pinggy Pro** (supports persistent subdomains and TCP/HTTP/HTTPS)  
  - Cloudflare Tunnel  

- **Binding & Hiding**  
  - Bind payload with APK (requires apktool ≥2.9.2)  
  - Embed payload in PDF/DOCX  
  - Steganography (hide in images using steghide)  
  - Generate QR codes for download  
  - Create Windows shortcuts / Android launcher icons  

- **Distribution**  
  - Email, SMS, and social media templates  
  - Start an HTTP server for file sharing  
  - Decrypt encrypted APKs  

- **Listener**  
  - Automatically start Metasploit multi/handler with the correct payload  
  - For tunnels, binds to `0.0.0.0` (so the tunnel can forward connections)  

- **Professional Banner & Legal Notice**  
  Clear warnings about authorised use only.

## 📦 Installation

### On Kali Linux / Debian

```bash
git clone git@github.com:mahi-cyberaware/APayloadMaster.git
cd apayloadmaster
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
or
apayloadmaster

### On Termux Installation
```bash
pkg install git
git clone git@github.com:mahi-cyberaware/APayloadMaster.git
cd apayloadmaster
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
or
apayloadmaster

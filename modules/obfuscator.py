import os
import random
import string
import base64
import zlib
import ast
import re

class Obfuscator:
    def __init__(self):
        self.output_dir = "output/obfuscated"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def obfuscate_python(self, filepath, level="medium"):
        """Obfuscate Python code"""
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        obfuscated_code = code
        
        if level.lower() == "low":
            obfuscated_code = self._basic_obfuscation(code)
        elif level.lower() == "medium":
            obfuscated_code = self._medium_obfuscation(code)
        elif level.lower() == "high":
            obfuscated_code = self._advanced_obfuscation(code)
        
        output_path = f"{self.output_dir}/{os.path.basename(filepath).replace('.py', '_obf.py')}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)
        
        return output_path
    
    def _basic_obfuscation(self, code):
        """Basic obfuscation techniques"""
        # Rename variables
        var_mapping = {}
        
        # Find all variable names
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id not in var_mapping and len(node.id) > 2:
                    var_mapping[node.id] = self._generate_random_name()
        
        # Replace variable names
        for old_name, new_name in var_mapping.items():
            code = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, code)
        
        # Add junk code
        junk_code = """
# Junk code for obfuscation
def _junk_func_1():
    return None

class _JunkClass:
    def __init__(self):
        self.nothing = None
    
    def junk_method(self):
        pass
"""
        
        return junk_code + "\n" + code
    
    def _medium_obfuscation(self, code):
        """Medium level obfuscation"""
        # Base64 encode strings
        string_pattern = r'(".*?"|\'.*?\')'
        
        def encode_match(match):
            string = match.group(1)[1:-1]  # Remove quotes
            encoded = base64.b64encode(string.encode()).decode()
            return f'base64.b64decode("{encoded}").decode()'
        
        code = re.sub(string_pattern, encode_match, code)
        
        # Add more junk functions
        code = self._add_junk_functions(code)
        
        # Encode entire code in base64
        encoded = base64.b64encode(code.encode()).decode()
        wrapped_code = f"""
import base64, codecs
exec(base64.b64decode("{encoded}"))
"""
        
        return wrapped_code
    
    def _advanced_obfuscation(self, code):
        """Advanced obfuscation with multiple layers"""
        # Layer 1: Compress
        compressed = zlib.compress(code.encode())
        
        # Layer 2: Base64 encode
        encoded = base64.b64encode(compressed).decode()
        
        # Layer 3: Split into parts
        parts = [encoded[i:i+50] for i in range(0, len(encoded), 50)]
        
        # Create decoder
        decoder = f"""
import base64, zlib

parts = {parts}
encoded = ''.join(parts)
compressed = base64.b64decode(encoded)
code = zlib.decompress(compressed).decode()

exec(code)
"""
        
        # Add anti-debugging
        anti_debug = """
import sys
import os

def anti_debug():
    # Check for debuggers
    debuggers = ['pydevd', 'pdb', 'debugpy']
    for module in sys.modules:
        for debugger in debuggers:
            if debugger in module.lower():
                os._exit(0)
    
    # Check for VM/sandbox
    vm_indicators = ['vmware', 'virtualbox', 'qemu', 'xen']
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            for vm in vm_indicators:
                if vm in cpuinfo:
                    os._exit(0)
    except:
        pass

anti_debug()
"""
        
        return anti_debug + decoder
    
    def _generate_random_name(self):
        """Generate random variable/function name"""
        length = random.randint(8, 15)
        chars = string.ascii_letters + '_'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _add_junk_functions(self, code):
        """Add junk functions to confuse analysis"""
        junk_functions = []
        
        for i in range(5):
            func_name = self._generate_random_name()
            junk_func = f"""
def {func_name}():
    {" + ".join([str(random.randint(1, 100)) for _ in range(5)])}
    return None
"""
            junk_functions.append(junk_func)
        
        return '\n'.join(junk_functions) + '\n' + code

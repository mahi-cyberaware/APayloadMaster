import os
import base64
import hashlib
from Crypto.Cipher import AES, DES, ARC4
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
import zlib

class EncryptionManager:
    def __init__(self):
        self.output_dir = "output/encrypted"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def encrypt_file(self, filepath, method="AES", key=None):
        """Encrypt file with specified method"""
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        encrypted_data = None
        output_ext = ".enc"
        
        if method == "1" or method.lower() == "aes":
            encrypted_data = self.aes_encrypt(data, key)
            output_ext = ".aes"
        
        elif method == "2" or method.lower() == "xor":
            encrypted_data = self.xor_encrypt(data, key)
            output_ext = ".xor"
        
        elif method == "3" or method.lower() == "rc4":
            encrypted_data = self.rc4_encrypt(data, key)
            output_ext = ".rc4"
        
        elif method == "4":
            encrypted_data = self.custom_encrypt(data, key)
            output_ext = ".custom"
        
        elif method == "5":
            # Steganography + Encryption
            encrypted_data = self.stego_encrypt(data, key)
            output_ext = ".png"  # Output as image
        
        if encrypted_data:
            output_path = f"{self.output_dir}/{os.path.basename(filepath)}{output_ext}"
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            return output_path
        
        return None
    
    def aes_encrypt(self, data, key=None):
        """AES-256 encryption"""
        if key is None:
            key = Random.new().read(32)  # 256-bit key
        
        # Derive key using SHA256
        if len(key) != 32:
            key = hashlib.sha256(key.encode() if isinstance(key, str) else key).digest()
        
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Store IV + encrypted data
        encrypted = iv + cipher.encrypt(pad(data, AES.block_size))
        
        # Store key for decryption (in real use, secure key exchange needed)
        key_file = f"{self.output_dir}/key.aes"
        with open(key_file, 'wb') as f:
            f.write(key)
        
        return encrypted
    
    def xor_encrypt(self, data, key=None):
        """XOR encryption"""
        if key is None:
            key = os.urandom(32)
        
        if isinstance(key, str):
            key = key.encode()
        
        # Repeat key to match data length
        key = (key * (len(data) // len(key) + 1))[:len(data)]
        
        # XOR encryption
        encrypted = bytes(a ^ b for a, b in zip(data, key))
        
        return encrypted
    
    def rc4_encrypt(self, data, key=None):
        """RC4 encryption"""
        if key is None:
            key = Random.new().read(16)
        
        if isinstance(key, str):
            key = key.encode()
        
        cipher = ARC4.new(key)
        encrypted = cipher.encrypt(data)
        
        return encrypted
    
    def custom_encrypt(self, data, key=None):
        """Custom multi-layer encryption"""
        if key is None:
            key = "APayloadMaster2024"
        
        # Layer 1: XOR with key
        key_bytes = key.encode() if isinstance(key, str) else key
        key_bytes = (key_bytes * (len(data) // len(key_bytes) + 1))[:len(data)]
        layer1 = bytes(a ^ b for a, b in zip(data, key_bytes))
        
        # Layer 2: Base64 encode
        layer2 = base64.b64encode(layer1)
        
        # Layer 3: Reverse
        layer3 = layer2[::-1]
        
        # Layer 4: Compress
        layer4 = zlib.compress(layer3)
        
        return layer4
    
    def stego_encrypt(self, data, key=None):
        """Combine encryption with steganography"""
        # First encrypt
        encrypted = self.aes_encrypt(data, key)
        
        # Convert to base64 for embedding in image
        encoded = base64.b64encode(encrypted).decode()
        
        # Create simple image with data (in real use, use proper steganography)
        from PIL import Image, ImageDraw
        import hashlib
        
        # Create image with encoded data as pixel values
        img_size = int(len(encoded) ** 0.5) + 1
        img = Image.new('RGB', (img_size, img_size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Embed data in image (simple example)
        for i, char in enumerate(encoded[:img_size*img_size]):
            x = i % img_size
            y = i // img_size
            color_value = ord(char) % 256
            img.putpixel((x, y), (color_value, color_value, color_value))
        
        output_path = f"{self.output_dir}/stego_encrypted.png"
        img.save(output_path)
        
        # Return image path instead of raw data
        return open(output_path, 'rb').read()

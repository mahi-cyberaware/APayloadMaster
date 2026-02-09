import os

class Config:
    # Database
    DB_PATH = "payloads.db"
    
    # Directories
    OUTPUT_DIR = "output"
    PAYLOADS_DIR = os.path.join(OUTPUT_DIR, "payloads")
    BOUND_DIR = os.path.join(OUTPUT_DIR, "bound")
    ENCRYPTED_DIR = os.path.join(OUTPUT_DIR, "encrypted")
    OBFUSCATED_DIR = os.path.join(OUTPUT_DIR, "obfuscated")
    EVADED_DIR = os.path.join(OUTPUT_DIR, "evaded")
    PERSISTENT_DIR = os.path.join(OUTPUT_DIR, "persistent")
    
    # Server
    SERVER_PORT = 8000
    API_PORT = 5000
    WEB_PORT = 5001
    
    # Encryption
    ENCRYPTION_KEY = "CHANGE_THIS_TO_SECURE_KEY"
    
    # Ngrok
    NGROK_AUTH_TOKEN = ""  # Add your ngrok token here
    
    # CloudFlare
    CLOUDFLARE_TOKEN = ""
    
    # Email (for distribution)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USER = ""
    EMAIL_PASS = ""
    
    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        directories = [
            cls.OUTPUT_DIR,
            cls.PAYLOADS_DIR,
            cls.BOUND_DIR,
            cls.ENCRYPTED_DIR,
            cls.OBFUSCATED_DIR,
            cls.EVADED_DIR,
            cls.PERSISTENT_DIR,
            "server/uploads",
            "downloads",
            "logs",
            "assets/templates"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

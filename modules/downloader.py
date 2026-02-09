import os
import http.server
import socketserver
import threading
import requests
import mimetypes
import qrcode
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import uuid

class DownloadHandler:
    def __init__(self, db):
        self.db = db
        self.servers = {}
    
    def save_locally(self, filepath, save_dir="./downloads"):
        """Save file locally"""
        os.makedirs(save_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        dest_path = os.path.join(save_dir, filename)
        
        try:
            import shutil
            shutil.copy2(filepath, dest_path)
            print(f"{Colors().GREEN}[+] File saved to: {dest_path}{Colors().ENDC}")
            
            # Log to database
            self.db.add_download(0, {
                'download_url': f"file://{dest_path}",
                'ip_address': '127.0.0.1',
                'user_agent': 'Local Save'
            })
            
            return dest_path
        except Exception as e:
            print(f"{Colors().RED}[!] Error saving file: {e}{Colors().ENDC}")
            return None
    
    def upload_to_server(self, filepath, server_url, api_key=None):
        """Upload file to remote server"""
        try:
            filename = os.path.basename(filepath)
            
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f)}
                headers = {}
                
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'
                
                response = requests.post(
                    f"{server_url}/upload",
                    files=files,
                    headers=headers,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                download_url = result.get('download_url')
                
                print(f"{Colors().GREEN}[+] File uploaded successfully{Colors().ENDC}")
                print(f"{Colors().CYAN}[*] Download URL: {download_url}{Colors().ENDC}")
                
                # Generate QR code for URL
                self.generate_qr_code(download_url)
                
                return download_url
            else:
                print(f"{Colors().RED}[!] Upload failed: {response.text}{Colors().ENDC}")
                return None
                
        except Exception as e:
            print(f"{Colors().RED}[!] Upload error: {e}{Colors().ENDC}")
            return None
    
    def start_local_server(self, filepath, port=8080):
        """Start local HTTP server for file sharing"""
        filename = os.path.basename(filepath)
        
        class FileHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == f'/{filename}' or self.path == '/download':
                    self.send_response(200)
                    
                    # Get file type
                    mime_type, _ = mimetypes.guess_type(filename)
                    if mime_type:
                        self.send_header('Content-type', mime_type)
                    
                    self.send_header('Content-Disposition', 
                                   f'attachment; filename="{filename}"')
                    self.end_headers()
                    
                    with open(filepath, 'rb') as f:
                        self.wfile.write(f.read())
                
                elif self.path == '/qr':
                    # Generate QR code for download
                    download_url = f"http://{self.headers.get('Host')}/{filename}"
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(download_url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill='black', back_color='white')
                    
                    # Convert to bytes
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(img_bytes.read())
                
                else:
                    # Serve HTML page with download link and QR
                    download_url = f"http://{self.headers.get('Host')}/{filename}"
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Download {filename}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; }}
                            .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                            .download-btn {{
                                display: inline-block;
                                padding: 15px 30px;
                                background: #007bff;
                                color: white;
                                text-decoration: none;
                                border-radius: 5px;
                                font-size: 18px;
                                margin: 20px 0;
                            }}
                            .qr-code {{ margin: 20px 0; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Download {filename}</h1>
                            <p>File size: {os.path.getsize(filepath) // 1024} KB</p>
                            
                            <a href="/{filename}" class="download-btn">Download Now</a>
                            
                            <div class="qr-code">
                                <h3>Scan to download:</h3>
                                <img src="/qr" alt="QR Code">
                            </div>
                            
                            <p>Or copy this link: <code>{download_url}</code></p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
            
            def log_message(self, format, *args):
                # Log downloads to database
                client_ip = self.client_address[0]
                user_agent = self.headers.get('User-Agent', 'Unknown')
                
                if self.path == f'/{filename}' or self.path == '/download':
                    self.db.add_download(0, {
                        'download_url': f"http://{self.headers.get('Host')}{self.path}",
                        'ip_address': client_ip,
                        'user_agent': user_agent
                    })
                    print(f"{Colors().CYAN}[*] Download: {client_ip} - {user_agent}{Colors().ENDC}")
        
        print(f"{Colors().GREEN}[*] Starting server on port {port}{Colors().ENDC}")
        print(f"{Colors().CYAN}[*] Download URL: http://localhost:{port}/{filename}{Colors().ENDC}")
        print(f"{Colors().CYAN}[*] QR Code URL: http://localhost:{port}/qr{Colors().ENDC}")
        
        os.chdir(os.path.dirname(filepath) or '.')
        
        with socketserver.TCPServer(("", int(port)), FileHandler) as httpd:
            self.servers[port] = httpd
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\n{Colors().YELLOW}[*] Server stopped{Colors().ENDC}")
    
    def start_web_server(self, port=8000):
        """Start full-featured web server"""
        os.chdir("server")
        
        class WebHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/download/'):
                    file_id = self.path.split('/')[-1]
                    file_path = f"uploads/{file_id}"
                    
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        
                        self.send_response(200)
                        
                        mime_type, _ = mimetypes.guess_type(filename)
                        if mime_type:
                            self.send_header('Content-type', mime_type)
                        
                        self.send_header('Content-Disposition', 
                                       f'attachment; filename="{filename}"')
                        self.end_headers()
                        
                        with open(file_path, 'rb') as f:
                            self.wfile.write(f.read())
                        
                        # Log download
                        client_ip = self.client_address[0]
                        self.db.add_download(0, {
                            'download_url': self.path,
                            'ip_address': client_ip,
                            'user_agent': self.headers.get('User-Agent', 'Unknown')
                        })
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'File not found')
                
                elif self.path == '/upload':
                    # Serve upload form
                    html = '''
                    <html>
                    <body>
                        <h1>Upload File</h1>
                        <form action="/upload" method="post" enctype="multipart/form-data">
                            <input type="file" name="file" required>
                            <input type="submit" value="Upload">
                        </form>
                    </body>
                    </html>
                    '''
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                
                else:
                    super().do_GET()
            
            def do_POST(self):
                if self.path == '/upload':
                    content_type = self.headers['Content-Type']
                    if not content_type.startswith('multipart/form-data'):
                        self.send_response(400)
                        self.end_headers()
                        return
                    
                    try:
                        import cgi
                        form = cgi.FieldStorage(
                            fp=self.rfile,
                            headers=self.headers,
                            environ={'REQUEST_METHOD': 'POST'}
                        )
                        
                        file_item = form['file']
                        if file_item.filename:
                            # Generate unique filename
                            file_id = str(uuid.uuid4())[:8]
                            filename = file_item.filename
                            file_path = f"uploads/{file_id}"
                            
                            with open(file_path, 'wb') as f:
                                f.write(file_item.file.read())
                            
                            download_url = f"/download/{file_id}"
                            
                            html = f'''
                            <html>
                            <body>
                                <h1>Upload Successful!</h1>
                                <p>Filename: {filename}</p>
                                <p>Download URL: <a href="{download_url}">{download_url}</a></p>
                                <p>Direct link: http://{self.headers.get('Host')}{download_url}</p>
                            </body>
                            </html>
                            '''
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(html.encode())
                        else:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write(b'No file uploaded')
                    except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(str(e).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
        
        print(f"{Colors().GREEN}[*] Starting web server on port {port}{Colors().ENDC}")
        print(f"{Colors().CYAN}[*] URL: http://localhost:{port}{Colors().ENDC}")
        print(f"{Colors().CYAN}[*] Upload: http://localhost:{port}/upload{Colors().ENDC}")
        
        with socketserver.TCPServer(("", int(port)), WebHandler) as httpd:
            self.servers[port] = httpd
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\n{Colors().YELLOW}[*] Server stopped{Colors().ENDC}")
    
    def generate_qr_code(self, url):
        """Generate QR code for download URL"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            qr_path = "download_qr.png"
            img.save(qr_path)
            
            print(f"{Colors().GREEN}[+] QR code saved: {qr_path}{Colors().ENDC}")
            return qr_path
        except Exception as e:
            print(f"{Colors().RED}[!] QR generation error: {e}{Colors().ENDC}")
            return None
    
    def email_distribution(self, filepath, email_list, subject):
        """Distribute file via email"""
        try:
            # Read file and encode
            with open(filepath, 'rb') as f:
                file_data = f.read()
                encoded = base64.b64encode(file_data).decode()
            
            # Create email
            msg = MIMEMultipart()
            msg['Subject'] = subject or "Important Document"
            msg['From'] = "sender@example.com"
            msg['To'] = email_list
            
            # Add body
            body = f"""
            Download the attached file.
            
            Or use this direct link: http://your-server.com/download
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment
            filename = os.path.basename(filepath)
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 
                                f'attachment; filename="{filename}"')
            msg.attach(attachment)
            
            # Send email (configure SMTP settings)
            print(f"{Colors().YELLOW}[*] Email configuration needed{Colors().ENDC}")
            print(f"{Colors().CYAN}[*] Would send to: {email_list}{Colors().ENDC}")
            
            return True
            
        except Exception as e:
            print(f"{Colors().RED}[!] Email error: {e}{Colors().ENDC}")
            return False

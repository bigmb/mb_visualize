from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    # Change to the directory containing visualization.html
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create server
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print('Server running at http://0.0.0.0:8000/')
    httpd.serve_forever()

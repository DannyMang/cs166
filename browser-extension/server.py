from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Change to the browser-extension directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create server
server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Server started at http://localhost:8000")
print("Visit http://localhost:8000/test.html to test the extension")
server.serve_forever() 
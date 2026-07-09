#!/usr/bin/env python3
import os, http.server, socketserver

os.chdir("/Users/cam/Documents/saved stuff/SSA/FFA")
PORT = 4567
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()

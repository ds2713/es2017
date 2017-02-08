#!/usr/bin/python
import http.server
import time

PORT_NUMBER = 8080

# This class will handles any incoming request from the browser
class myHandler(http.server.BaseHTTPRequestHandler):

	# Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type","text/html")
		self.end_headers()
		# Prepare and send the HTML message
		time_data = ','.join(map(str, time.localtime()))
		response = "START" + time_data + "END"
		self.wfile.write(bytes(response, "utf-8"))
		return

try:
	# Create a web server and define the handler to manage the
	# Incoming request
	server = http.server.HTTPServer(('', PORT_NUMBER), myHandler)
	print("Webserver started on port " + str(PORT_NUMBER) + ". ")

	# Wait forever for incoming HTTP requests
	server.serve_forever()

except KeyboardInterrupt:
	print("^C received, shutting down the web server.")
	server.socket.close()

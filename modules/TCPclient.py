import socket
import sys

target_host = "127.0.0.1"
target_port = 9000

client_socket = socket.socekt(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((target_host, target_port))

except:
    print "[!!] unable to connect to target host"
    sys.exit(0)

print "[*] Connected to target %s:%d" % (target_host, target_port)

client_socket.send(sys.argv[2])

response = client_socket.recv(4096)

print(response)
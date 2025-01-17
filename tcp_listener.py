import socket

TCP_IP = '0.0.0.0' # Listen on all interfaces
TCP_PORT = 5005 # Port to listen on
BUFFER_SIZE = 1024 # Buffer size for incoming data

#Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind the socket to the port
s.bind((TCP_IP, TCP_PORT))

#Listen for incoming connections
s.listen(1)
print("Server listening on {TCP_IP}: {TCP_PORT}")

#Accept connection from client
conn, addr = s.accept()
print("Connection from: {addr}")

#Receive data in the specified buffer size
while True:
    data = conn.recv(BUFFER_SIZE)
    if not data: #If no data, break the loop (connection closed)
        break
    print("Received data: {data.decode('utf-8')}") #Decode to string
    conn.send(data) # Echo back the data

#Close the connection
conn.close   
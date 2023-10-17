import os
import socket

import protocol

# make sure that the folder is empty
dir_path = os.path.join(os.getcwd(), "files")
if os.path.exists(dir_path):
    if os.path.isdir(dir_path):
        files = os.listdir(dir_path)
        for file in files:
            os.remove(os.path.join(dir_path, file))
        os.rmdir(dir_path)
    elif os.path.isfile(dir_path):
        os.remove(dir_path)
os.mkdir(dir_path)
files = os.listdir(dir_path)


# make sure 2 files doesn't have the same name
def name_check(name):
    global files
    if name not in files:
        return name
    number = 1
    name1 = name.split(".")[0] + f"({number})"
    while name1 in files:
        number += 1
        name1 = name.split(".")[0] + f"({number})"

    return name1 + "." + name.split(".")[1]


IP, PORT = "0.0.0.0", 1112  # IP and PORT

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()
print("Server is up and running")

(client_socket, client_address) = server_socket.accept()
msg = protocol.create_msg(2, [])
client_socket.send(msg)
print("Client connected")


while True:
    msg_data = protocol.get_msg(client_socket)
    if msg_data[1] == "quit":
        msg = protocol.create_msg(0, "quit")
        client_socket.send(msg)
        break
    if msg_data[0] == "0":
        path = os.path.join(dir_path, msg_data[1])
        with open(path, 'rb') as file:
            data = file.read()
        msg = protocol.create_msg(1, data, path)
        client_socket.send(msg)
    elif msg_data[0] == "1":
        file_name = name_check(msg_data[1])
        with open(os.path.join(dir_path, file_name), 'wb') as file:
            file.write(msg_data[2])
        files = os.listdir(dir_path)
        msg = protocol.create_msg(2, files)
        client_socket.send(msg)

client_socket.close()
server_socket.close()

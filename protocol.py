import os

LENGTH_FIELD_SIZE = 4


# first letter is command, 0 for message and 1 for data
def get_msg(my_socket, length_field_size=LENGTH_FIELD_SIZE):
    """
    Extract data from message, return the data or message
    """
    cmd = my_socket.recv(1).decode('utf-8')
    if cmd == "0":
        print("these is message")
        length = my_socket.recv(LENGTH_FIELD_SIZE).decode('utf-8')
        msg = my_socket.recv(int(length)).decode('utf-8')
        return [cmd, msg]
    if cmd == "1":
        print("these is data")
        length_file_name = my_socket.recv(length_field_size).decode('utf-8')
        file_name = my_socket.recv(int(length_file_name)).decode('utf-8')
        length = my_socket.recv(length_field_size).decode('utf-8')
        length1 = my_socket.recv(int(length)).decode('utf-8')
        data = my_socket.recv(int(length1))
        return [cmd, file_name, data]
    if cmd == "2":
        print("these is file list")
        length = my_socket.recv(LENGTH_FIELD_SIZE).decode('utf-8')
        msg = my_socket.recv(int(length)).decode('utf-8')
        msg = msg.split(",")
        return [cmd, msg]
    return [-1, -1]


# command 0 for message (like request download), 1 for data, 2 for create file list message
def create_msg(command, data, file_path=""):
    if command == 0:  # request data
        length = str(len(data.encode('utf-8'))).zfill(LENGTH_FIELD_SIZE)
        return (str(command) + length + data).encode('utf-8')
    if command == 1:  # data
        length1 = str(len(data)).zfill(LENGTH_FIELD_SIZE)
        length = str(len(length1)).zfill(LENGTH_FIELD_SIZE)
        file_name = os.path.basename(file_path)
        length_file_name = str(len(file_name.encode('utf-8'))).zfill(LENGTH_FIELD_SIZE)
        return (str(command) + length_file_name + file_name + length + length1).encode('utf-8') + data
    if command == 2:  # file list
        data = ",".join(data)
        length = str(len(data.encode('utf-8'))).zfill(LENGTH_FIELD_SIZE)
        return (str(command) + length + data).encode('utf-8')

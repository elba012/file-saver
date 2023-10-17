import os
import socket
import string
import threading
import time

import protocol
import tkinter as tk
from tkinter import filedialog, messagebox

# connect client
IP, PORT = "127.0.0.1", 1112

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((IP, PORT))

file_path = ''
download_var = True


def open_file_dialog(path=""):
    global file_path
    filetypes = [("All Files", "*.txt *.png *.jpg *.jpeg *.gif *.bmp *.mp4 *.avi *.mkv *.mp3 *.wav")]
    file_path = filedialog.askopenfilename(filetypes=filetypes, initialdir=path)
    file_label.config(text=f"selected file {os.path.basename(file_path)}")


def submit_action():
    global file_path
    if file_path:
        with open(file_path, 'rb') as file:
            data = file.read()
        msg = protocol.create_msg(1, data, file_path)
        my_socket.send(msg)
        messagebox.showinfo("message", f"file saved")
    else:
        messagebox.showinfo("message", "you need to select file")


# Create the main window
window = tk.Tk()
width, height = 600, 450
window.geometry(f"{width}x{height}")
window.title("file saver")

# define colors
widget_color = "#EEEEEE"  # background for frames
text_color = "#222831"  # text color

# Create a label and place it above the top_frame
file_label = tk.Label(window, text="You need to select a file", background="light blue", font=("Helvetica", 12))
file_label.pack(side=tk.TOP, pady=10)

# Create a frame for the top half with a light blue background
top_frame = tk.Frame(window, bg="light blue", height=200)
top_frame.pack(fill=tk.BOTH, expand=True)

# Create a frame for the bottom half with a white background
bottom_frame = tk.Frame(window, bg="white", height=200)
bottom_frame.pack(fill=tk.BOTH, expand=True)

button_frame = tk.Frame(bottom_frame)
button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

# create list for files
members_listbox = tk.Listbox(bottom_frame, background=widget_color, foreground=text_color, font=("Helvetica", 12))
members_listbox.pack(fill=tk.BOTH, expand=True)


def download():
    global download_var
    download_var = True
    selected_file = members_listbox.get(members_listbox.curselection())
    if selected_file:
        msg = protocol.create_msg(0, selected_file)
        my_socket.send(msg)
    else:
        messagebox.showinfo("message", "you need to select file to download")


def open_file():
    global download_var
    download_var = False
    selected_file = members_listbox.get(members_listbox.curselection())
    if selected_file:
        msg = protocol.create_msg(0, selected_file)
        my_socket.send(msg)
    else:
        messagebox.showinfo("message", "you need to select file to open")


# update files in the list box
def update_files(files):
    global members_listbox
    members_listbox.destroy()
    members_listbox = tk.Listbox(bottom_frame, background=widget_color, foreground=text_color, font=("Helvetica", 12))
    members_listbox.pack(fill=tk.BOTH, expand=True)
    for file in files:
        members_listbox.insert(tk.END, file)


def receive():
    global download_var
    while True:
        try:
            data = protocol.get_msg(my_socket)
            if data[0] == "1":  # the server sent data
                if download_var:  # download file
                    save_path = filedialog.askdirectory()
                    path = os.path.join(save_path, data[1])
                    with open(path, "wb") as file:
                        file.write(data[2])
                    messagebox.showinfo("message", f"file downloaded in {path}")
                else:  # open file
                    file = open(data[1], "wb")
                    file.write(data[2])
                    path = os.path.join(os.getcwd(), data[1])
                    os.startfile(path)
            elif data[0] == "2":  # the server sent file list
                update_files(data[1])
        except ConnectionError:
            window.destroy()
            break


# get all connected drivers
def get_drive_status():
    devices = []
    for label in string.ascii_uppercase:
        path = label + ":\\"
        if os.path.exists(path):
            devices.append(path)
    return devices


# Detects drives changes meaning detect usb connection
def detect_device():
    while True:
        original = set(get_drive_status())
        time.sleep(3)
        updated = set(get_drive_status())

        added_devices = updated - original
        removed_devices = original - updated

        if added_devices:
            print(f'There were {len(added_devices)} drive(s) added:')
            for drive in added_devices:  # drive added
                open_file_dialog(drive)
                print(f'The drive added: {drive}')

        if removed_devices:
            print(f'There were {len(removed_devices)} drive(s) removed:')
            for drive in removed_devices:  # drive disconnected
                print(f'The drive removed: {drive}')


def quit_window():
    msg = protocol.create_msg(0, "quit")
    my_socket.send(msg)
    my_socket.close()
    window.destroy()
    exit()


# Starting Threads For Listening
receive_thread = threading.Thread(target=receive)
receive_thread.start()

usb_thread = threading.Thread(target=detect_device)
usb_thread.start()

# Create the "Upload" button and "Submit" button in the top frame using grid
upload_button = tk.Button(top_frame, text="Upload File", command=open_file_dialog, width=50, height=2)
submit_button = tk.Button(top_frame, text="Submit", command=submit_action, width=50, height=2)
quit_button = tk.Button(button_frame, text="Quit", command=quit_window, width=10, height=1)
download_button = tk.Button(button_frame, text="Download", command=download, width=10, height=1)
open_button = tk.Button(button_frame, text="open", command=open_file, width=10, height=1)

# Place buttons in the middle of the top frame
upload_button.pack(pady=30)
submit_button.pack()
download_button.pack(side=tk.TOP, padx=10, pady=10)
open_button.pack(side=tk.TOP, padx=10, pady=10)
quit_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Start the main event loop
window.mainloop()

my_socket.close()

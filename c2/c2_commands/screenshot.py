import os
from datetime import datetime
from PIL import Image
import io

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
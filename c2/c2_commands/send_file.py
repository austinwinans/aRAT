import os

def send_file(client_socket, file_path):
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        return

    with open(file_path, 'rb') as f:
        file_data = f.read()

    try:
        size = len(file_data)
        client_socket.sendall(str(size).encode('utf-8'))
        client_socket.sendall(file_data)
        print(f"File '{file_path}' sent successfully.")
    except Exception as e:
        print(f"Failed to send file - {e}")
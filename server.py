import socket
import threading


clients=[]

def client(conn,addr):

    clients.append(conn)
    print('New client : ' ,addr )

    while True:
        data=conn.recv(1024)
        data=data.decode()

        online_users=str(len(clients))

        for client in clients:
            if client != conn:
                client.sendall(f"CHAT:{data}\n".encode())

        for client in clients:
            client.sendall(f"ONLINE:{online_users}\n".encode())
                

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 60000))
    server.listen()

    while True:
        conn, addr= server.accept()
        t=threading.Thread(target=client ,args=(conn,addr))
        t.start()
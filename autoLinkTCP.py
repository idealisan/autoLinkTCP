import socket
import threading
import sys

def get_local_ips():
    """获取本机的所有IP地址"""
    ips = socket.gethostbyname_ex(socket.gethostname())[2]
    return ips

def forward_data(source_sock, target_sock):
    """从源socket转发数据到目标socket"""
    try:
        while True:
            data = source_sock.recv(4096)
            if not data:
                # 关闭连接时也关闭对方的socket
                target_sock.shutdown(socket.SHUT_WR)
                break
            target_sock.sendall(data)
    except Exception as e:
        print(f"Error forwarding data: {e}")
    finally:
        source_sock.close()
        target_sock.close()

def handle_connection(client_socket, target_ip, target_port):
    """处理新的连接，将数据双向转发到目标地址和端口"""
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((target_ip, target_port))
        # 为客户端到目标的数据流创建一个线程
        threading.Thread(target=forward_data, args=(client_socket, target_socket), daemon=True).start()
        # 为目标到客户端的数据流创建一个线程
        threading.Thread(target=forward_data, args=(target_socket, client_socket), daemon=True).start()
    except Exception as e:
        print(f"Failed to handle connection: {e}")
        client_socket.close()

def start_tcp_server(listen_ip, listen_port, target_ip, target_port):
    """在指定的IP和端口上启动TCP服务器，并双向转发数据到目标地址和端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((listen_ip, listen_port))
        server_socket.listen(5)
        print(f"Listening on {listen_ip}:{listen_port}, forwarding to {target_ip}:{target_port}\n")
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Received connection from {addr}")
            threading.Thread(target=handle_connection, args=(client_socket, target_ip, target_port), daemon=True).start()

def main():
    ips = get_local_ips()
    for idx, ip in enumerate(ips):
        print(f"{idx + 1}: {ip}")
    listen_idx = int(input("Choose the listen IP address number: ")) - 1
    
    if listen_idx < 0 or listen_idx >= len(ips):
        print("Invalid IP address selection.")
        sys.exit(1)
    
    target_ip = input("Enter the target IP address: ")
    listen_port = int(input("Enter the listen port: "))
    target_port = int(input("Enter the target port: "))
    
    start_tcp_server(ips[listen_idx], listen_port, target_ip, target_port)

if __name__ == "__main__":
    main()

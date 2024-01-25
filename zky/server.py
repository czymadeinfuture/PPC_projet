import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def handle_player(conn, addr):
    print(f"玩家 {addr} 加入游戏")
    try:
        while True:
            # 接收玩家动作
            data = conn.recv(1024)
            if not data:
                break

            # 这里加入处理游戏逻辑的代码
            # ...

            # 响应玩家
            conn.sendall(b"动作已接收")
    finally:
        print(f"玩家 {addr} 离开游戏")
        conn.close()

def game_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"游戏服务器启动，在 {HOST}:{PORT} 上监听")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_player, args=(conn, addr)).start()

if __name__ == "__main__":
    game_server()

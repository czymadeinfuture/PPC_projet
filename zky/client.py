import socket

HOST = '127.0.0.1'
PORT = 65432

def player_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("已连接到游戏服务器")

        while True:
            # 发送动作到服务器
            action = input("输入你的动作: ")
            s.sendall(action.encode())

            # 接收服务器响应
            response = s.recv(1024)
            print(f"服务器响应: {response.decode()}")

if __name__ == "__main__":
    player_client()

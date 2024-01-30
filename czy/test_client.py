'''import socket

def player_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 65432))
        print("Connected to the game server.")

        try:
            while True:
                server_message = client_socket.recv(1024).decode()
                print(server_message)

                if server_message.startswith("Your hand:"):
                    action = input("Enter your action (play/discard/hint): ")
                    client_socket.sendall(action.encode())
                elif server_message == "We don't make a game":
                    print("Game cannot be started. Closing the client.")
                    break
                elif server_message.startswith("Your Player ID is") or server_message.startswith("Invalid response"):
                    response = input("Reply to server (yes/no): ")
                    client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()
            

if __name__ == "__main__":
    player_client()'''

import socket
import threading
from sysv_ipc import MessageQueue

def listen_for_hints(mq_key):
    """监听消息队列以接收其他玩家的提示信息"""
    mq = MessageQueue(mq_key)
    while True:
        message, _ = mq.receive()
        print(f"Received hint: {message.decode()}")

def send_hint(target_mq_key, hint):
    """发送提示信息给指定玩家"""
    mq = MessageQueue(target_mq_key)
    mq.send(hint.encode())

def handle_user_input(client_socket, mq_key):
    """处理用户输入的动作，并将其发送到服务器或通过消息队列发送提示"""
    while True:
        action = input("Enter your action (play, discard, hint, quit): ")
        if action == "quit":
            print("Quitting the game...")
            break
        elif action.startswith("hint"):
            # 提示动作格式：hint target_player_id hint_info
            _, target_player_id, hint_info = action.split(maxsplit=2)
            target_mq_key = 1000 + int(target_player_id)
            send_hint(target_mq_key, hint_info)
        else:
            client_socket.sendall(action.encode())

def player_client():
    is_your_turn_event = threading.Event()
    """客户端主函数"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 65432))
        print("Connected to the game server.")

        try:
            while True:
                server_message = client_socket.recv(1024).decode()
                print(server_message)

                if server_message.startswith("mq_key:"):
                    # 接收消息队列键值
                    mq_key = int(server_message.split(":")[1])
                    threading.Thread(target=listen_for_hints, args=(mq_key,)).start()
                elif server_message == "We don't make a game":
                    print("Game cannot be started. Closing the client.")
                    break
                elif server_message.startswith("Your Player ID is") or server_message.startswith("Invalid response"):
                    response = input("Reply to server (yes/no): ")
                    client_socket.sendall(response.encode())
                elif server_message.startswith("Your hand:") or server_message.startswith("It's now Player"):
                    is_your_turn_event.set() 
                    # 当接收到手牌信息或轮到玩家动作时，允许玩家输入动作
                    threading.Thread(target=handle_user_input, args=(client_socket, mq_key)).start()
                elif server_message.startswith("Game over"):
                    print("Game over. Closing the client.")
                    break
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    player_client()

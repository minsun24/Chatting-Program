import socket
import threading
# --------------------- 채팅 사용 방법 --------------------------
# !create room 번호 : 채팅방 생성
# !enter 번호 : 채팅방에 입장 / 채팅방 초대 수락
# !invite id : id를 채팅방으로 초대
# !online : 현재 활동 중인 id 정보, 채팅방 현황 나타내기
# !bye : 채팅방에서 나가기
# !quit : 프로그램을 종료하기
# ----------------------------------------------------------------

# --------------------- 클라이언트 세팅 --------------------------
host = 'localhost'
port = 55555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((host, port))
except ConnectionRefusedError:
    print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    exit()

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            if message:
                print(message)
            else:
                print("서버와의 연결이 끊어졌습니다.")
                client.close()
                break
        except Exception as e:
            print("연결에 오류가 발생했습니다:", e)
            client.close()
            break

def send_messages():
    while True:
        message = input()
        if message == "!quit":
            client.send(message.encode())
            client.close()
            break
        else:
            print(f"me: {message}")
            client.send(message.encode())

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()

receive_thread.join()  # 수신 스레드가 종료될 때까지 대기
send_thread.join()  # 송신 스레드가 종료될 때까지 대기

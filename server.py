import threading
import socket

# ------------------ 서버 세팅 --------------------
host = 'localhost'
port = 55555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = {}  # 접속한 클라이언트 목록 (ID: 소켓)
rooms = {}  # 생성된 채팅방 목록 (룸 번호: 클라이언트 ID 리스트)

def handle_client(client, addr):
    # 클라이언트가 접속하면 ID를 요청 
    client.send("ID를 입력하세요: ".encode())
    client_id = client.recv(1024).decode().strip()
    
    # ID가 이미 사용 중인 경우 다른 ID 요청
    while client_id in clients:
        client.send("이미 사용 중인 ID입니다. 다른 ID를 입력하세요: ".encode())
        client_id = client.recv(1024).decode().strip()
    
    # 클라이언트 등록 및 모든 클라이언트에게 새로운 클라이언트 등장 알림
    clients[client_id] = client
    notify_all_clients(f">> {client_id}님이 홈에 입장했습니다 <<\n")
    
    # 환영 메시지 및 현재 활동 중인 멤버와 채팅방 현황 전송
    welcome_message = f">> 환영합니다 {client_id}님 <<\n"
    welcome_message += f">> 활동 중인 멤버: {list(clients.keys())} <<\n"
    room_status = ">> 채팅방 현황: " + ", ".join([f"[{i} ({', '.join(rooms[i])})]" for i in rooms]) + " <<\n"
    welcome_message += room_status
    welcome_message += ">> 채팅방을 생성하시려면 '!create room 번호'를 입력해주세요. <<\n"
    welcome_message += ">> 채팅방에 들어가려면 '!enter 번호'를 입력해주세요. <<\n"
    client.send(welcome_message.encode())

    # 클라이언트로부터 명령을 받아 처리
    while True:
        try:
            message = client.recv(1024).decode().strip()
            if message.startswith("!create room "): # 채팅방 생성
                room_number = int(message.split()[2])
                if room_number not in rooms:
                    rooms[room_number] = []
                    enter_room(client_id, room_number)
                    notify_room(client_id, room_number, f">> 채팅방 {room_number}번이 생성되었습니다. {client_id} 님이 입장하였습니다. <<\n")
                else:
                    client.send("이미 존재하는 채팅방 번호입니다.".encode())
            elif message.startswith("!enter "):  # 채팅방 입장
                room_number = int(message.split()[1])
                if room_number in rooms:
                    if client_id in rooms[room_number]:
                        client.send(">> 이미 참여 중인 채팅방입니다. <<\n".encode())
                    else:
                        enter_room(client_id, room_number)
                        notify_room(client_id, room_number, f">> {client_id} 님이 채팅방에 입장하였습니다. <<\n")
                else:
                    client.send(">> 아직 생성되지 않은 채팅방입니다. !create room 번호 로 채팅방을 생성해주세요.<<\n".encode())
            elif message == "!bye": # 채팅방 나가고 홈으로 돌아가기
                exit_room(client_id)
                client.send(">> 홈으로 돌아왔습니다 <<\n".encode())
            elif message == "!online":  # 현재 온라인 사용자 및 채팅방 현황 보기
                online_users = f">> 활동 중인 멤버: {list(clients.keys())} <<\n"
                room_status = ">> 채팅방 현황: " + ", ".join([f"[{i} ({', '.join(rooms[i])})]" for i in rooms]) + " <<\n"
                online = online_users + room_status
                client.send(online.encode())
            elif message == "!quit":  # 프로그램 종료
                if exit_room(client_id):
                    client.send(">> 홈으로 돌아왔습니다 <<\n".encode())
                client.close()
                break
            elif message.startswith("!invite "):  # 다른 클라이언트 초대
                invited_id = message.split()[1]
                invite_client(client_id, invited_id)
            else: # 채팅 메시지 전송
                room_number = find_client_room(client_id)
                if room_number is not None:
                    broadcast_message(client_id, room_number, message)
        except ConnectionResetError:
            break
    # 클라이언트 연결 종료 시 처리        
    client.close()
    if client_id in clients:
        del clients[client_id]
    exit_room(client_id)
    notify_all_clients(f">> {client_id}님이 나갔습니다 <<\n")

# 클라이언트를 채팅방에 입장시키는 함수
def enter_room(client_id, room_number):
    exit_room(client_id)
    rooms[room_number].append(client_id)
    # notify_room(client_id, room_number, f">> {client_id} 님이 입장하였습니다. <<\n")

# 채팅방의 모든 클라이언트에게 메시지를 전송하는 함수
def notify_room(client_id, room_number, message):
    for cid in rooms[room_number]:
        if clients[cid]:
            clients[cid].send(message.encode())

# 모든 클라이언트에게 메시지를 전송하는 함수
def notify_all_clients(message):
    for client_id, client in clients.items():
        client.send(message.encode())

# 클라이언트를 채팅방에서 나가게 하고, 채팅방이 비어 있으면 채팅방을 삭제하는 함수
def exit_room(client_id):
    for room_number, room in rooms.items():
        if client_id in room:
            room.remove(client_id)
            notify_room(client_id, room_number, f">> {client_id}님이 방을 나갔습니다. <<\n")
            if not room:
                del rooms[room_number]  # 채팅방에 클라이언트가 없으면 채팅방 삭제
                notify_all_clients(f">> 채팅방 {room_number}번이 종료되었습니다. <<\n")
            break
          
# 클라이언트가 속한 채팅방을 찾는 함수
def find_client_room(client_id):
    for room_id, room in rooms.items():
        if client_id in room:
            return room_id
    return None

# 채팅방 함수
def broadcast_message(client_id, room_number, message):
    for cid in rooms[room_number]:
        if clients[cid] and cid != client_id:
            clients[cid].send(f"{client_id}: {message}\n".encode())
            
# 클라이언트를 초대하는 함수 
def invite_client(client_id, invited_id):
    room_number = find_client_room(client_id)
    if room_number is not None and invited_id in clients:
        invite_message = f">> {client_id}님이 채팅방 {room_number}번으로 초대했습니다. 수락하시려면 '!enter {room_number}'을 입력하세요. <<\n"
        clients[invited_id].send(invite_message.encode())
    else:
        clients[client_id].send("초대할 수 없는 사용자이거나, 사용자가 현재 채팅방에 없습니다.".encode())

# 서버 시작 함수 
def start_server():
    print("서버가 시작되었습니다.")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

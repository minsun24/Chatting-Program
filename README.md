# Chatting-Program

python 다중 채팅 프로그램

## 사용 방법

- !create room 번호 : 채팅방 생성
- !enter 번호 : 채팅방에 입장 / 채팅방 초대 수락
- !invite id : id를 채팅방으로 초대
- !online : 현재 활동 중인 id 정보, 채팅방 현황 나타내기
- !bye : 채팅방에서 나가기
- !quit : 프로그램을 종료하기

---

## 작동 흐름

통신을 위해 두개의 파일을 준비

- server.py
- client.py

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/eb9f72c4-f7d4-4510-ab8a-da2ab11b71fb/025c2f4b-30b2-45e1-86f9-fbfcb7cbcd23/Untitled.png)

---

## python - Thread 라이브러리

<라이브러리 사용 예제>

- normal일반 thread

```
import threading # 쓰레드 라이브러리

thread_1 = threading.Thread(target="쓰레드 동작 함수", args=(필요한 인자들))

thread_1.start()
```

- demon데몬 thread

```
# 데몬 쓰레드 생성
thread_2 = threading.Thread(target="function", args=(인자들))
thread_2.demon = True
thread_2.start()

```

---
## 시연 예시 영상
https://youtu.be/one_-pS8Dh0?si=v9Rftw9DSf9UGrZX 


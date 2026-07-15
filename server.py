import socket
import random

# 設定連線資訊
HOST = '10.228.255.39' 
PORT = 12345           

# 建立一個 Socket 物件，AF_INET 是用 IPv4，SOCK_STREAM 是用 TCP 協議
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 把上面的 IP 和 Port 綁定到這個 Socket 上
server_socket.bind((HOST, PORT))

server_socket.listen(2)
print(f"Server 已啟動，正在等待連線...")

while True:
    # 程式會卡在這裡，直到有 cliet 連進來為止
    client_socket, address = server_socket.accept()
    print(f"連線成功！來自：{address}")

    try:
        # 1. 接收學號並發送歡迎詞
        # 從 Client那邊收資料，限制 1024 bytes，並把二進位轉成 utf-8 字串
        student_id = client_socket.recv(1024).decode('utf-8')
        welcome_msg = f" Welcome Game {student_id}"
        
        # 把歡迎訊息傳回去給 Client
        client_socket.send(welcome_msg.encode('utf-8'))
        print(f"已與 {student_id} 開始遊戲")

        # 2. 開始猜拳迴圈
        win_count = 0 # 用來記錄client贏了幾次
        options = ["rock", "paper", "scissors"] # 伺服器可以出的選項

        # 只要client 還沒贏到 3 次，就一直玩下去
        while win_count < 3:
            # 接收 Client出什麼拳，轉成小寫比較好判斷
            data = client_socket.recv(1024).decode('utf-8').lower()
            if not data: break # 如果Client 突然斷線了，就跳出這輪遊戲

            client_choice = data
            server_choice = random.choice(options) #Server 隨機選一個出

            # 判斷勝負邏輯
            if client_choice == server_choice:
                result = "draw" # 平手
            elif (client_choice == "rock" and server_choice == "scissors") or \
                 (client_choice == "paper" and server_choice == "rock") or \
                 (client_choice == "scissors" and server_choice == "paper"):
                result = "win"  # Client 贏
                win_count += 1  # 贏的次數加 1
            else:
                result = "lose" # Client輸

            # 組合結果訊息，回傳給 Client讓他知道目前的戰況
            response = f"Server出的是: {server_choice}, 你這局: {result}, 目前你已贏了 {win_count} 次"
            client_socket.send(response.encode('utf-8'))
            print(f"[{student_id}] 出拳: {client_choice} | Server: {server_choice} | 結果: {result}")

        print(f"遊戲結束，{student_id} 贏了三次。")

    except Exception as e:
        # 如果中間發生什麼意外（eg網路斷掉），會跑來這裡
        print(f"處理過程發生錯誤: {e}")
    finally:
        # 無論遊戲正常結束還是出錯，最後都要把這個Client的連線關掉
        client_socket.close()
        print("連線已關閉，等待下一個玩家...")
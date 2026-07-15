import socket

# 要連過去的目標server資訊
SERVER_IP = '10.228.255.39' 
SERVER_PORT = 12345

# 建立 Client 的 Socket 物件
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"正在連線至 Server {SERVER_IP}:{SERVER_PORT}...")
    # 嘗試撥號給 Server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("連線成功！")

    # 1. 輸入學號
    my_id = input("請輸入學號 : ")
    # 把學號傳給 Server
    client_socket.send(my_id.encode('utf-8'))

    # 2. 接收歡迎訊息
    # 等 Server回傳 Welcome 訊息
    welcome = client_socket.recv(1024).decode('utf-8')
    print(f"Server 回應: {welcome}")

    # 3. 遊戲迴圈
    print("\n--- 猜拳遊戲開始 ---")
    print("請輸入 rock / paper / scissors")

    while True:
        # 讓使用者輸入出拳，strip() 去掉空白，lower() 變小寫
        choice = input("你的出拳: ").strip().lower()
        
        # 防呆：如果亂打字就不傳給server，要求重打
        if choice not in ["rock", "paper", "scissors"]:
            print("無效的輸入，請重新輸入！")
            continue

        # 把出的拳傳給 Server
        client_socket.send(choice.encode('utf-8'))

        # 接收server回傳的結果 (包含server出什麼、這局輸贏、目前贏幾次)
        result_msg = client_socket.recv(1024).decode('utf-8')
        print(result_msg)

        # 判斷Server 傳回來的字串裡有沒有贏了3次
        if "贏了 3 次" in result_msg:
            print("\n恭喜！你已經達成 3 次勝利，遊戲結束。")
            break # 贏滿三次，跳出遊戲迴圈

except Exception as e:
    # 連線失敗或中途出問題會顯示在這裡
    print(f"\n連線中斷或錯誤：{e}")
finally:
    # 結束後把連線關閉，釋放資源
    client_socket.close()
    input("\n按任意鍵結束...")
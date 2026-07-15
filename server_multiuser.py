import socket
import threading

# --- 設定參數 ---
HOST = '10.228.255.39'  
PORT = 12345
MAX_ROUNDS = 3

def judge_round(moves):
    """
    判定猜拳結果
    moves: {'Server': 'rock', 'Client1': 'paper', ...}
    回傳該回合獲勝者的名稱清單
    """
    unique_moves = set(moves.values())
    
    # 規則：全部出一樣，或是三種拳都有出現，則該局平手 (皆 0 分)
    if len(unique_moves) == 1 or len(unique_moves) == 3:
        return []

    # 只有兩種拳出現時，判斷哪種贏
    m1, m2 = list(unique_moves)
    win_map = {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}
    
    winning_move = m1 if win_map[m1] == m2 else m2
    
    # 回傳出獲勝拳的人
    winners = [name for name, move in moves.items() if move == winning_move]
    return winners

def handle_client(conn, addr, client_info, client_id):
    """處理 Client 的名稱輸入"""
    try:
        # 接收學號
        name = conn.recv(1024).decode('utf-8')
        client_info[client_id] = {'conn': conn, 'name': name, 'score': 0}
        
        # 發送歡迎訊息
        welcome_msg = f"Welcome Game {name}"
        conn.sendall(welcome_msg.encode('utf-8'))
        print(f"[系統] 已連接玩家: {name} (來自 {addr})")
    except Exception as e:
        print(f"處理 Client {client_id} 時發生錯誤: {e}")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)
    
    print(f"Server 已啟動，監聽 IP: {HOST}, Port: {PORT}")
    print("等待兩名玩家連線...")

    clients = {} # 儲存 client 連線資訊
    
    # 接受兩個 Client 連線
    for i in range(1, 3):
        conn, addr = server_socket.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr, clients, i))
        t.start()
        t.join() # 確保依序取得名稱

    server_name = "Server"
    server_score = 0

    print("\n--- 遊戲開始 (共三回合) ---")

    for r in range(1, MAX_ROUNDS + 1):
        print(f"\n[第 {r} 回合]")
        
        # 1. 取得 Server 玩家自己的輸入
        server_move = ""
        while server_move not in ['rock', 'paper', 'scissors']:
            server_move = input("你的出拳 (rock/paper/scissors): ").lower()

        # 2. 通知所有 Client 開始出拳並接收資料
        current_moves = {'Server': server_move}
        
        for cid in clients:
            clients[cid]['conn'].sendall(f"ROUND_START".encode('utf-8'))
            move = clients[cid]['conn'].recv(1024).decode('utf-8')
            current_moves[clients[cid]['name']] = move

        # 3. 判定勝負
        winners = judge_round(current_moves)
        
        # 4. 更新分數並準備結果訊息
        result_msg = f"\n--- 第 {r} 回合結果 ---\n"
        for name, move in current_moves.items():
            result_msg += f"{name} 出: {move}\n"
        
        if not winners:
            result_msg += "本局結果: 平手 (Draw)\n"
        else:
            result_msg += f"本局獲勝: {', '.join(winners)}\n"
            if "Server" in winners:
                server_score += 1
            for cid in clients:
                if clients[cid]['name'] in winners:
                    clients[cid]['score'] += 1

        print(result_msg)
        
        # 5. 將結果發送給所有 Client
        for cid in clients:
            clients[cid]['conn'].sendall(result_msg.encode('utf-8'))

    # --- 遊戲結束，顯示最終計分板 ---
    final_board = "\n" + "="*25 + "\n"
    final_board += f"{'Name':<15} | {'Score':<5}\n"
    final_board += "-"*25 + "\n"
    final_board += f"{server_name:<15} | {server_score:<5}\n"
    for cid in clients:
        final_board += f"{clients[cid]['name']:<15} | {clients[cid]['score']:<5}\n"
    final_board += "="*25 + "\n"

    print(final_board)
    
    # 發送最終計分板給所有 Client 並關閉連線
    for cid in clients:
        try:
            clients[cid]['conn'].sendall(f"FINAL_SCORE{final_board}".encode('utf-8'))
            clients[cid]['conn'].close()
        except:
            pass

    server_socket.close()
    print("遊戲結束，Server 已關閉。")

if __name__ == "__main__":
    main()
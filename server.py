import socket
import threading
from database import init_db, save_message
from database import get_recent_messages

init_db()

clients={}

def broadcast(message, exclude_conn=None):
    for client_conn in clients:
        if client_conn != exclude_conn:
            try:
                client_conn.sendall(message.encode("utf-8"))
            except:
                pass

def handle_client(conn, addr):
    username = ""
    try:
        # دریافت نام کاربری از کلاینت
        data = conn.recv(1024).decode("utf-8").strip()
        if data.startswith("USERNAME:"):
            username = data.split(":", 1)[1]
        else:
            username = f"User_{addr[1]}"

        clients[conn] = username

                # دریافت ۲۰ پیام آخر
        recent_msgs = get_recent_messages(20)
        
        for row in recent_msgs:
            # اطمینان از اینکه تعداد ستون‌های دریافتی با ساختار دیتابیس برابر است
            # بر اساس تابع get_recent_messages شما: 0=user, 1=msg, 2=time
            db_user = row[0]
            db_msg = row[1]
            db_time = row[2]
            
            # ساخت پیام با فرمت استاندارد کلاینت
            # اضافه کردن \n در انتها برای اینکه در سمت کلاینت باعث شکستن خط نشود (بستگی به نحوه دریافت کلاینت دارد)
            formatted_message = f"CHAT:{db_user}:{db_msg} ({db_time})"
            
            try:
                conn.sendall(formatted_message.encode("utf-8"))
                # یک وقفه بسیار بسیار کم برای جلوگیری از پر شدن بافر کلاینت در یک لحظه
                import time
                time.sleep(0.01)
            except Exception as e:
                print(f"Error sending history: {e}")
                break
        # پیام ورود و به‌روزرسانی تعداد آنلاین‌ها
        broadcast(f"CHAT:🟢 {username} به چت پیوست.\n", exclude_conn=conn)
        online_count = str(len(clients))
        broadcast(f"ONLINE:{online_count}\n")

        while True:
            data = conn.recv(1024)
            if not data: break
            msg = data.decode("utf-8").strip()
            save_message(username, msg)
            # ارسال پیام چت با نام فرستنده
            broadcast(f"CHAT:{username}: {msg}\n", exclude_conn=conn)

    except (ConnectionResetError, OSError):
        pass
    finally:
        # مدیریت خروج
        if conn in clients:
            username = clients.pop(conn)
            broadcast(f"CHAT:🔴 {username} از چت خارج شد.\n")
            online_count = str(len(clients))
            broadcast(f"ONLINE:{online_count}\n")
            conn.close()
                

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 60000))
    server.listen()

    while True:
        conn, addr= server.accept()
        t=threading.Thread(target=handle_client ,args=(conn,addr))
        t.start()
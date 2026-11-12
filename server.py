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

# در تابع handle_client و بخش‌های خروج/ورود، این تابع کمکی را برای broadcast کردن لیست استفاده می‌کنیم:
def broadcast_online_status():
    names = ",".join(clients.values())
    count = str(len(clients))
    broadcast(f"ONLINE:{count}:{names}\n")


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

        # دریافت ۲۰ پیام آخر از دیتابیس
        recent_msgs = get_recent_messages(20)
        
        for row in recent_msgs:
            db_user = row[0]
            db_msg = row[1]
            full_timestamp = str(row[2])  # به عنوان مثال "2026-11-10 14:35:20"
            
            # استخراج فقط ساعت و دقیقه (مثلاً 14:35) برای نمایش تمیز در کلاینت
            try:
                # اگر فرمت تاریخ و ساعت است، ساعت و دقیقه را برمی‌دارد
                display_time = full_timestamp.split(" ")[1][:5]
            except Exception:
                display_time = full_timestamp[-5:]

            # حتماً باید در انتها n\ قرار داده شود تا کلاینت متوجه پایان پیام شود
            formatted_message = f"CHAT:{db_user}:{db_msg} ({display_time})\n"
            
            try:
                conn.sendall(formatted_message.encode("utf-8"))
            except Exception as e:
                print(f"Error sending history: {e}")
                break

        # پیام ورود و به‌روزرسانی تعداد آنلاین‌ها
        broadcast(f"CHAT:🟢 {username} به چت پیوست.\n", exclude_conn=conn)
        online_count = str(len(clients))
        broadcast_online_status()


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
            broadcast_online_status()
            conn.close()
                

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 60000))
    server.listen()

    while True:
        conn, addr= server.accept()
        t=threading.Thread(target=handle_client ,args=(conn,addr))
        t.start()
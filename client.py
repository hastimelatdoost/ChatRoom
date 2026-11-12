import threading
import customtkinter as ctk
import socket
import time

# بستن امن برنامه و سوکت‌ها
def close_app():
    global closing, connected
    closing = True
    connected = False

    try:
        client.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    try:
        client.close()
    except OSError:
        pass

    window.destroy()

# تنظیمات ظاهری CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BACKGROUND = "#10121A"
HEADER = "#191C27"
CHAT_BACKGROUND = "#11141D"
PURPLE = "#8065F5"
PURPLE_HOVER = "#6C50E0"
MY_MESSAGE = "#7056D9"
OTHER_MESSAGE = "#242936"
TEXT = "#F5F6FA"
GREEN = "#63D99A"
RED = "#FF7272"
TIME_COLOR = "#A0A0A0" # رنگی برای متن زمان

# متغیرهای ارتباطی و دریافت نام کاربری
connected = False
client = None
connection_lock = threading.Lock()
closing = False


# نمایش تعداد کاربران آنلاین
def update_online_count(count):
    status.configure(text=f"● {count} کاربر آنلاین", text_color=GREEN)

# لیست کاربران آنلاین (متغیر سراسری)
online_users_list = []

# تابعی که با کلیک روی تعداد آنلاین‌ها اجرا می‌شود و پنجره لیست را باز می‌کند
def show_online_users_popup(event=None):
    popup = ctk.CTkToplevel(window)
    popup.title("کاربران آنلاین")
    popup.geometry("250\u00d7300")
    popup.resizable(False, False)
    popup.attributes("-topmost", True) # همیشه رو بماند

    title_lbl = ctk.CTkLabel(popup, text="👥 افراد حاضر در چت", font=("Tahoma", 14, "bold"))
    title_lbl.pack(pady=10)

    # کادر اسکرول‌شونده یا لیست‌باکس برای اسامی
    scroll_frame = ctk.CTkScrollableFrame(popup, width=220, height=200)
    scroll_frame.pack(padx=10, pady=5, fill="both", expand=True)

    if not online_users_list:
        lbl = ctk.CTkLabel(scroll_frame, text="کسی آنلاین نیست", font=("Tahoma", 12))
        lbl.pack(pady=5)
    else:
        for user in online_users_list:
            user_lbl = ctk.CTkLabel(scroll_frame, text=f"• {user}", font=("Tahoma", 12), anchor="w")
            user_lbl.pack(fill="x", padx=5, pady=2)



def get_modern_username():
    temp_root = ctk.CTk()
    temp_root.withdraw()

    dialog = ctk.CTkToplevel(temp_root)
    dialog.title("Login")
    dialog.geometry("350x220")
    dialog.configure(fg_color=BACKGROUND)
    dialog.resizable(False, False)
    dialog.grab_set()
    
    user_name_var = []

    label = ctk.CTkLabel(dialog, text="Welcome!", font=("Segoe UI", 20, "bold"), text_color=PURPLE)
    label.pack(pady=(30, 10))

    sub_label = ctk.CTkLabel(dialog, text="Please enter your username", font=("Segoe UI", 12), text_color=TIME_COLOR)
    sub_label.pack(pady=(0, 10))

    entry = ctk.CTkEntry(dialog, width=220, height=35, fg_color=HEADER, border_color=PURPLE, placeholder_text="Username...")
    entry.pack(pady=10)
    entry.focus()

    def on_submit():
        val = entry.get().strip()
        if val:
            user_name_var.append(val)
            dialog.destroy()

    submit_btn = ctk.CTkButton(dialog, text="Start Chatting", command=on_submit, 
                               fg_color=PURPLE, hover_color=PURPLE_HOVER, width=120)
    submit_btn.pack(pady=20)

    dialog.bind("<Return>", lambda e: on_submit())
    dialog.wait_window()
    temp_root.destroy()
    
    return user_name_var[0] if user_name_var else "Guest"

username = get_modern_username()

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(("127.0.0.1", 60000))
    connected = True
    client.sendall(f"USERNAME:{username}\n".encode("utf-8"))
    client.settimeout(None)
    print(f"Connected as {username}!")
except Exception as e:
    print(f"Connection error: {e}")
    connected = False
    if client:
        client.close()
# ساخت پنجره اصلی 
window = ctk.CTk()
window.title("ChatRoom")
window.geometry("850x650")
window.minsize(600, 500)
window.configure(fg_color=BACKGROUND)

# سربرگ و منوی بالایی
header = ctk.CTkFrame(window, fg_color=HEADER, corner_radius=0, height=75)
header.pack(fill="x")
header.pack_propagate(False)

title = ctk.CTkLabel(header, text="ChatRoom", font=("Arial", 23, "bold"), text_color=TEXT)
title.pack(side="left", padx=25)

right_container = ctk.CTkFrame(header, fg_color="transparent")
right_container.pack(side="right", padx=20)

status = ctk.CTkLabel(
    right_container,
    text="● در حال اتصال..." if connected else "● اتصال برقرار نشد",
    font=("Arial", 13),
    text_color=GREEN if connected else RED
)
status.pack(side="left", padx=15)
status.bind("<Button-1>", show_online_users_popup)
status.configure(cursor="hand2")



exit_btn = ctk.CTkButton(
    right_container,
    text="خروج",
    width=80,
    height=35,
    corner_radius=10,
    fg_color="#E963F5",
    hover_color="#E055E0",
    font=("Arial", 13, "bold"),
    command=close_app
)
exit_btn.pack(side="left", padx=5)

# فضای اسکرول پیام‌ها
chat_area = ctk.CTkScrollableFrame(window, fg_color=CHAT_BACKGROUND, corner_radius=0)
chat_area.pack(fill="both", expand=True, padx=12, pady=12)


# نمایش حباب پیام در چت (اصلاح شده برای نمایش زمان)
def show_message(message, mine=False, timestamp=""):
    message_row = ctk.CTkFrame(chat_area, fg_color="transparent")
    message_row.pack(fill="x", padx=8, pady=4)

    bubble_color = MY_MESSAGE if mine else OTHER_MESSAGE
    bubble = ctk.CTkFrame(message_row, fg_color=bubble_color, corner_radius=16)
    bubble.pack(side="right" if mine else "left", padx=5)

    # متن اصلی پیام
    label = ctk.CTkLabel(
        bubble,
        text=message,
        font=("Arial", 14),
        text_color=TEXT,
        wraplength=450,
        justify="left"
    )
    # اگر زمان وجود دارد فاصله پایینی کمتری می‌گذاریم تا ساعت نزدیک متن باشد
    label.pack(padx=16, pady=(10, 2 if timestamp else 10), anchor="w")

    # نمایش ساعت دقیق زیر متن پیام
    if timestamp:
        time_label = ctk.CTkLabel(
            bubble,
            text=timestamp,
            font=("Arial", 10),
            text_color=TIME_COLOR
        )
        # انتقال pady و padx به متد pack و تنظیم تراز افقی (anchor)
        time_label.pack(anchor="e", padx=12, pady=(0, 6))

    # اسکرول خودکار به آخرین پیام
    try:
        chat_area._parent_canvas.yview_moveto(1.0)
    except Exception:
        pass

# به‌روزرسانی متن وضعیت اتصال
def update_status(is_connected):
    if is_connected:
        status.configure(text="● متصل به سرور", text_color=GREEN)
    else:
        status.configure(text="● اتصال قطع شد", text_color=RED)


# ارسال پیام به سرور
def send_message(event=None):
    message = message_entry.get().strip()
    if not message:
        return

    if not connected:
        show_message("اتصال به سرور برقرار نیست.", False)
        return

    try:
        data = f"{message}\n".encode("utf-8")
        with connection_lock:
            client.sendall(data)
        
        # محاسبه زمان دقیق فعلی (ساعت:دقیقه)
        # اگر ثانیه را هم می‌خواهید: time.strftime("%H:%M:%S")
        current_time = time.strftime("%H:%M")
        
        show_message(message, True, current_time)
        message_entry.delete(0, "end")
    except OSError:
        show_message("ارسال پیام ناموفق بود.", False)
        window.after(0, update_status, False)


# نوار پایین صفحه برای نوشتن پیام
bottom = ctk.CTkFrame(window, fg_color=HEADER, corner_radius=0, height=85)
bottom.pack(fill="x")
bottom.pack_propagate(False)

message_entry = ctk.CTkEntry(
    bottom,
    height=46,
    corner_radius=14,
    placeholder_text="پیامت را بنویس...",
    font=("Arial", 14),
    fg_color="#242936",
    border_color="#343B4B",
    text_color=TEXT
)
message_entry.pack(side="left", fill="x", expand=True, padx=(18, 10), pady=18)

send_button = ctk.CTkButton(
    bottom,
    text="ارسال  ➤",
    width=105,
    height=46,
    corner_radius=14,
    fg_color=PURPLE,
    hover_color=PURPLE_HOVER,
    font=("Arial", 14, "bold"),
    command=send_message
)
send_button.pack(side="right", padx=(0, 18), pady=18)

# دریافت پیام‌ها از سرور به صورت همگام (Thread) با بافر اختصاصی خط‌به‌خط
def receive_message():
    global connected,  online_users_list
    buffer = ""

    while connected and not closing:
        try:
            data = client.recv(4096)
            if not data:
                break

            # اضافه کردن داده‌های دریافتی جدید به بافر
            buffer += data.decode("utf-8")

            # پردازش هر پیامی که با \n به پایان رسیده است
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                # ۱. پردازش تعداد آنلاین‌ها
                                # ۱. پردازش تعداد و لیست آنلاین‌ها (فرمت جدید: ONLINE:count:name1,name2,...)
                if line.startswith("ONLINE:"):
                    parts = line.split(":", 2)
                    count = parts[1]
                    if len(parts) > 2 and parts[2]:
                        online_users_list = parts[2].split(",")
                    else:
                        online_users_list = []
                    window.after(0, update_online_count, count)


                # ۲. پردازش پیام‌های چت و تاریخچه (CHAT:sender:message (HH:MM))
                elif line.startswith("CHAT:"):
                    try:
                        content = line[5:]  # حذف عبارت CHAT:
                        user, full_msg = content.split(":", 1)

                        # استخراج زمان از انتهای متن پیام (اگر پرانتز زمان وجود داشته باشد)
                        if full_msg.endswith(")") and "(" in full_msg:
                            last_open_paren = full_msg.rfind("(")
                            msg_text = full_msg[:last_open_paren].strip()
                            timestamp_str = full_msg[last_open_paren + 1:-1].strip()
                        else:
                            msg_text = full_msg.strip()
                            timestamp_str = ""

                        # اگر پیام از خود ما بود (مثلاً از قبل در دیتابیس بوده یا اکو شده)
                        is_mine = (user == username)
                        display_text = msg_text if is_mine else f"{user}: {msg_text}"

                        window.after(0, show_message, display_text, is_mine, timestamp_str)

                    except Exception as err:
                        # در صورت بروز هرگونه خطای فرمت‌بندی در خط
                        window.after(0, show_message, line, False, "")

                # ۳. پیام‌های سیستمی یا اطلاع‌رسانی معمولی
                else:
                    window.after(0, show_message, line, False, "")

        except OSError:
            break
        except Exception as e:
            print(f"Error processing message: {e}")
            break

    if not closing:
        connected = False
        window.after(0, update_status, False)

# رویدادها و اجرای نهایی برنامه
message_entry.bind("<Return>", send_message)
window.protocol("WM_DELETE_WINDOW", close_app)

if connected:
    update_status(True)
    thread = threading.Thread(target=receive_message, daemon=True)
    thread.start()
else:
    message_entry.configure(state="disabled")
    send_button.configure(state="disabled")

window.mainloop()
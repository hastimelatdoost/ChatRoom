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
    message_row.pack(fill="x", padx=8, pady=5)

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
    label.pack(padx=16, pady=(10, 2))

    # نمایش زمان در زیر متن پیام (در صورت وجود)
    if timestamp:
        time_label = ctk.CTkLabel(
            bubble,
            text=timestamp,
            font=("Arial", 10), # سایز کوچکتر
            text_color=TIME_COLOR,
            padx=12,
            pady=(0, 5)
        )
        time_label.pack()

# به‌روزرسانی متن وضعیت اتصال
def update_status(is_connected):
    if is_connected:
        status.configure(text="● متصل به سرور", text_color=GREEN)
    else:
        status.configure(text="● اتصال قطع شد", text_color=RED)

# نمایش تعداد کاربران آنلاین
def update_online_count(count):
    status.configure(text=f"● {count} کاربر آنلاین", text_color=GREEN)

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
        
        # اضافه کردن زمان فعلی برای پیام خود کلاینت
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

# دریافت پیام‌ها از سرور به صورت همگام (Thread)
def receive_message():
    global connected
    while connected and not closing:
        try:
            data = client.recv(4096)
            if not data:
                break

            message = data.decode("utf-8").strip()

            if message.startswith("ONLINE:"):
                count = message.split(":")[1]
                window.after(0, update_online_count, count)
            elif message.startswith("CHAT:"):
                # تحلیل پیام چت: USER:MESSAGE (TIME) یا USER:MESSAGE
                # فرض بر این است که سرور فرمت "CHAT:user:msg (time)" یا "CHAT:user:msg" را می‌فرستد
                try:
                    # جدا کردن قسمت اول (CHAT) و بقیه
                    content = message.split(":", 1)[1]
                    # جدا کردن نام کاربری از متن پیام
                    user_part, msg_content = content.split(":", 1)
                    
                    # استخراج زمان اگر در قالب (HH:MM) باشد
                    timestamp_str = ""
                    if "(" in msg_content and ")" in msg_content:
                        # جدا کردن متن اصلی از زمان
                        msg_content = msg_content.split("(")[0].strip()
                        timestamp_str = msg_content.split("(")[-1].replace(")", "") # روش ساده‌تر
                        # اصلاح دقیق‌تر برای استخراج زمان بین پرانتزها
                        start_idx = msg_content.find("(")
                        end_idx = msg_content.find(")")
                        # اما چون msg_content را split کردیم، باید از متن اصلی زمان را برداریم
                        # بیایید از روش امن‌تری برای جدا کردن استفاده کنیم:
                        
                        # بازسازی مجدد برای دقت بالا:
                        parts = content.split(":", 1)
                        user = parts[0]
                        full_msg = parts[1]
                        if "(" in full_msg:
                            msg_text = full_msg.split("(")[0].strip()
                            time_text = full_msg.split("(")[1].replace(")", "")
                            show_message(f"{user}: {msg_text}", False, time_text)
                        else:
                            show_message(f"{user}: {full_msg}", False)
                    else:
                        show_message(f"{user}: {msg_content}", False)
                except Exception:
                    # اگر فرمت پیام چت در دیتابیس یا سرور با split مشکل داشت
                    show_message(message, False)
            else:
                # برای پیام‌های معمولی که شامل فرمت چت نیستند
                show_message(message, False)

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
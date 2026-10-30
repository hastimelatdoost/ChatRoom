
import socket
import threading
import customtkinter as ctk
from tkinter import simpledialog

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

# متغیرهای ارتباطی و دریافت نام کاربری
connected = False
client = None
connection_lock = threading.Lock()
closing = False

root_temp = ctk.CTk()
root_temp.withdraw()
username = simpledialog.askstring("نام کاربری", "لطفاً نام خود را وارد کنید:", parent=root_temp)
root_temp.destroy()

if not username or not username.strip():
    username = "Guest"
else:
    username = username.strip()

# تلاش برای اتصال به سرور
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(("127.0.0.1", 60000))
    connected = True
    client.sendall(f"USERNAME:{username}\n".encode("utf-8"))
    client.settimeout(None)
    print("Connected to server successfully!")
except Exception as e:
    print(f"Connection error: {e}")
    connected = False
    if client:
        client.close()

# ایجاد پنجره اصلی
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

# نمایش حباب پیام در چت
def show_message(message, mine=False):
    message_row = ctk.CTkFrame(chat_area, fg_color="transparent")
    message_row.pack(fill="x", padx=8, pady=5)

    bubble_color = MY_MESSAGE if mine else OTHER_MESSAGE
    bubble = ctk.CTkFrame(message_row, fg_color=bubble_color, corner_radius=16)
    bubble.pack(side="right" if mine else "left", padx=5)

    label = ctk.CTkLabel(
        bubble,
        text=message,
        font=("Arial", 14),
        text_color=TEXT,
        wraplength=450,
        justify="left"
    )
    label.pack(padx=16, pady=10)

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
        show_message(message, True)
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
    border_color="#343A4B",
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
                text = message.split(":", 1)[1]
                window.after(0, show_message, text, False)
            else:
                window.after(0, show_message, message, False)

        except OSError:
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
from Server import *
from fileinput import filename
import os, mimetypes, re, shutil
from email.mime import image
import tkinter as tk
from tkinter import ANCHOR, W, Label, PhotoImage, Canvas, Scrollbar, filedialog
from turtle import bgcolor, color, update, width
from datetime import datetime
import shutil
import time
ONLINE = "CONNECTED"
OFFLINE = "DISCONNECTED"
TIME = 1

class Item:
    def __init__(self, hostname,last_ping_time = time.time(),status = OFFLINE):
        self.hostname = hostname
        self.last_ping_time = last_ping_time
        self.last_ping_time = self.format_last_ping_time()
        self.status = status
        
    def format_last_ping_time(self):
        # Chuyển last_fetch_time từ dạng timestamp sang datetime và định dạng lại
        dt = datetime.fromtimestamp(self.last_ping_time)
        formatted_time = dt.strftime("%I:%M:%S %p")
        return formatted_time

def create_item_frame(item : Item):
    item_frame = tk.Frame(list_frame)
    item_frame.pack(fill="x")
    
    info_frame = tk.Frame(item_frame)
    info_frame.pack(side="left", fill="x", expand=True)
    
    info_frame.columnconfigure(0, weight=1)
    info_frame.columnconfigure(1, weight=1)
    info_frame.columnconfigure(2, weight=1)
    
    name_label = tk.Label(info_frame, text=item.hostname, width=20)
    name_label.grid(row=0, column=0)
    
    status_label = tk.Label(info_frame, text=item.status, width = 20)
    status_label.grid(row=0, column=2)
    if(item.status == "ONLINE"):
        status_label.config(fg = "#00FF00")
    else:
        status_label.config(fg="#FF0000")
    
    last_ping_time_label = tk.Label(info_frame, text=item.last_ping_time, width = 20)
    last_ping_time_label.grid(row=0, column=1)
    
    ping_button = tk.Button(item_frame, text = "Ping",command=lambda: ping(item,last_ping_time_label,status_label), bg="#98F5FF", activebackground="#FFCCCC")
    ping_button.pack(side = "right")
    
    ping_button = tk.Button(item_frame, text = "Discover",command=lambda: discover(item.hostname), bg="#7FFF00", activebackground="#FFCCCC")
    ping_button.pack(side = "right")

    return (last_ping_time_label,status_label)

def discover_popup(hostname):
    popup = tk.Toplevel(root)
    popup.title("List of files in "+hostname)
    popup.geometry("300x300")
    client_tracking = directory_path+"/"+ hostname + ".txt"
    print(client_tracking)
    if os.path.exists(client_tracking):
        file_listbox = tk.Listbox(popup, selectmode=tk.SINGLE)
        with open(client_tracking,"r") as f:
            tracked_file = f.read().split(" ")
        for file in tracked_file:
            file_listbox.insert(tk.END,file)
        file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #tạo scroll bar
        scrollbar = Scrollbar(popup, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        #thêm scroll bar
        file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=file_listbox.yview)
    else:
        error_label = tk.Label(popup, text=hostname+" doesn't exsit")
        error_label.pack()


def ping(item : Item, last_ping_time_label, status_label):
    color = "#00FF00"
    if(server.ping(item.hostname)):
        item.status = ONLINE
    else:
        item.status = OFFLINE
        color = "#FF0000"
    item.last_ping_time = time.time()
    item.last_ping_time = item.format_last_ping_time()
    status_label.config(text = item.status,fg = color )
    last_ping_time_label.config(text = item.last_ping_time)

def discover(hostname):
    # try:
    #     f = open(hostname + ".txt","r+")
    #     files = f.read()
    #     f.truncate(0)
    #     f.close()
    # except:
    #     print(hostname + " doesn't exist")
    #     return 0
    if(server.discover(hostname)):
        discover_popup(hostname)
    # else :
    #     f = open(hostname + ".txt","w")
    #     f.write(files)
        
def ping_all():
    for item_tuple in items:
        item, (time_label, status_label) = item_tuple
        ping(item,time_label,status_label)
        
       
items = []
def update_item():
    if os.path.exists(directory_path):
        files = os.listdir(directory_path)

        for file in files:
            if file.endswith(".txt"):
                hostname = file.split('.')[0]
                status = OFFLINE
                if(server.ping(hostname)):
                    status = ONLINE
                item = Item(hostname = hostname,status=status)
                items.append((item,create_item_frame(item))) # bao gồm (item,(time,status))
                            
def on_enter(event):
    # Lấy nội dung đã nhập từ trường nhập liệu
    cli_input = file_name_entry.get().strip()  # Loại bỏ khoảng trắng thừa
    discover_line = r'^discover\s+.+$'
    ping_line = r'^ping\s+.+$'

    if re.match(discover_line, cli_input):  # discover
        parts = cli_input.split()
        command = parts[0]
        hostname = parts[1]
        print(f"Command: {command}, Hostname: {hostname}")
        # todo
        discover(hostname)
            
    elif re.match(ping_line, cli_input):  # ping
        parts = cli_input.split()
        command = parts[0]
        hostname = parts[1]
        print(f"Command: {command}, Hostname: {hostname}")
        # todo
        for item_tuple in items:
            item, (time_label, status_label) = item_tuple
            if item.hostname == hostname:
                ping(item,time_label,status_label)
    else:
        print("Nhap sai")

    # Xóa nội dung trường nhập liệu
    file_name_entry.delete(0, 'end')


def show_cli_popup():
    popup = tk.Toplevel(root)
    popup.geometry("600x30+150+150")
    popup.title("CLI")

    # Tạo một hộp để nhập tên file
    entry_frame = tk.Frame(popup)
    entry_frame.pack()

    file_name_label = tk.Label(entry_frame, text="CLI:")
    file_name_label.pack(side="left")

    global file_name_entry
    file_name_entry = tk.Entry(entry_frame, width=600)
    file_name_entry.pack(side="left")

    # Gắn sự kiện Enter với hàm on_enter
    file_name_entry.bind('<Return>', on_enter)

    # Chạy cửa sổ popup
    popup.mainloop() 

# Tạo cửa sổ giao diện
root = tk.Tk()
root.title("Danh sách các Client")
root.geometry("600x400+100+100")
root.resizable(width=False, height=False)

# Tạo khung cho vùng phía trên
header_frame = tk.Frame(root, borderwidth=2, relief="solid")
header_frame.pack(fill="x")

header_name_label = tk.Label(header_frame, text="Name", bg="lightgray")
header_name_label.grid(row=0, column=0, padx=50, sticky="w")

header_time_label = tk.Label(header_frame, text="Last Ping Time", bg="lightgray")
header_time_label.grid(row=0, column=1, padx=40, sticky="e")

header_time_label = tk.Label(header_frame, text="Status", bg="lightgray")
header_time_label.grid(row=0, column=2, padx=45, sticky="e")

# Tạo thanh trượt
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")

# Tạo một vùng hiển thị danh sách
canvas = Canvas(root, yscrollcommand=scrollbar.set)
canvas.pack(side="top", fill="both", expand=True)

# Tạo một khung cho danh sách
list_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=list_frame, anchor="nw")

# Đường dẫn đến thư mục bạn muốn kiểm tra trong kho
directory_path = os.getcwd()
print(directory_path)

# Thiết lập danh sách
update_item()

# Thiết lập canvas để làm việc với thanh trượt
list_frame.update_idletasks()
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind('<Configure>', on_configure)

scrollbar.config(command=canvas.yview)

# Tạo khung cho nút
button_frame = tk.Frame(root, borderwidth=2, relief="solid", pady=10)
button_frame.pack(side="bottom", fill="x", anchor="s")  # Thay đổi khoảng cách ngang

# Tạo các nút
button_ping_all = tk.Button(button_frame, text="Ping all", command= ping_all, bg="#00FF66", activebackground="#CCFF99")
button_cli = tk.Button(button_frame, text="Open CLI", comman = show_cli_popup, bg="#00FF66", activebackground="#CCFF99")

button_ping_all.pack(side = "left",padx=30)
button_cli.pack(side = "right" ,padx = 30)

#chạy ứng dụng
def on_closing():
    # if os.path.exists(directory_path):
    #     files = os.listdir(directory_path)
    #     for file in files:
    #         if file.endswith(".txt"):
    #             f = open(file,"r+")
    #             f.truncate(0)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
from fileinput import filename
import os, mimetypes, re, shutil
from email.mime import image
import tkinter as tk
from tkinter import ANCHOR, W, Label, PhotoImage, Canvas, Scrollbar, filedialog
from turtle import bgcolor, color, update, width
from datetime import datetime
import shutil
from Client import *
class Item:
    def __init__(self, file_type, name, last_fetch_time):
        self.file_type = file_type
        self.name = name
        self.last_fetch_time = last_fetch_time
        self.last_fetch_time = self.format_last_fetch_time()
        self.icon = self.get_icon_with_type()

    def set_property(self, file_type, name, last_fetch_time):
        self.file_type = file_type
        self.name = name
        self.last_fetch_time = last_fetch_time
        self.last_fetch_time = self.format_last_fetch_time()
        self.icon = self.get_icon_with_type()

    def get_icon_with_type(self):
        if self.file_type=="image/jpeg":
            return "Images/apple.png"
        else:
            return "Images/blueberry.png"
    
    def format_last_fetch_time(self):
        # Chuyển last_fetch_time từ dạng timestamp sang datetime và định dạng lại
        dt = datetime.fromtimestamp(self.last_fetch_time)
        formatted_time = dt.strftime("%I:%M:%S %p")
        return formatted_time


def create_item_frame(item):
    item_frame = tk.Frame(list_frame)
    item_frame.pack(fill="x")

    icon = PhotoImage(file = item.icon)
    icon_label = tk.Label(item_frame, image=icon)
    icon_label.image = icon
    icon_label.pack(side="left")
    icon_label.config(width=50, height=50)

    info_frame = tk.Frame(item_frame)
    info_frame.pack(side="left", fill="x", expand=True)

    info_frame.columnconfigure(0, weight=1)
    info_frame.columnconfigure(1, weight=1)
    info_frame.columnconfigure(2, weight=1)
    info_frame.columnconfigure(3, weight=1)
    info_frame.columnconfigure(4, weight=1)

    name_label = tk.Label(info_frame, text=item.name, width=20)
    name_label.grid(row=0, column=0)

    last_fetch_time_label = tk.Label(info_frame, text=item.last_fetch_time, width = 20)
    last_fetch_time_label.grid(row=0, column=4, padx=50)

    delete_button = tk.Button(item_frame, text="Delete", command=lambda: delete_item(item_frame, item), bg="#FF6666", activebackground="#FFCCCC")
    delete_button.pack(side="right")

def delete_item(item_frame, item):
    item_frame.destroy()
    #todo : done
    os.remove(directory_path +"/"+item.name)
    items.remove(item)
    client.publish(fname = None, allFile=True)

def refresh_items():
    for widget in list_frame.winfo_children():
        widget.destroy()

    for item in items:
        create_item_frame(item)

    on_configure(None)

def publish_file_btn():
    def rename_file(tempdir):
        def on_accept():
            new_name = file_name_entry.get()
            if new_name:
                try:
                    file_name = os.path.basename(tempdir)
                    destination_path = os.path.join(os.getcwd(), "Repository", new_name)
                    shutil.move(tempdir, destination_path)
                    print(f"File moved and renamed from {tempdir} to {destination_path}")
                    file_name = os.path.basename(destination_path)
                    add_item(file_name)
                    #update_item()
                    popup.destroy()
                    client.publish(new_name)
                except Exception as e:
                    print(f"Error: {e}")

        popup = tk.Toplevel(root)
        popup.title("Rename file")

        entry_frame = tk.Frame(popup)
        entry_frame.pack()

        file_name_label = tk.Label(entry_frame, text="Enter file new name:")
        file_name_label.pack(side="left")

        file_name_entry = tk.Entry(entry_frame)
        file_name_entry.pack(side="left")

        accept_button = tk.Button(popup, text="Accept", command=on_accept, bg="#00FF66", activebackground="#CCFF99")
        accept_button.pack()

    tempdir = search_for_file_path()
    if tempdir:
        rename_file(tempdir)

def publish_file(lname, fname):
    try:
        destination_path = os.getcwd()+"/Repository"
        shutil.move(os.path.normpath(lname), destination_path)
        new_path = os.path.join(destination_path, fname)
        os.rename(os.path.join(destination_path, os.path.basename(lname)), new_path)
        print(f"File moved from {lname} to {destination_path} and rename to {fname}")
        file_name = os.path.basename(new_path)
        add_item(file_name)
        client.publish(fname)
        #update_item()
    except Exception as e:
        print(f"Error: {e}")

    # thông báo lên server
def request_file_popup():
    # Tạo cửa sổ popup
    request_popup = tk.Toplevel(root)
    request_popup.title("Request Fetch File")

    # Tạo một hộp để nhập tên file
    entry_frame = tk.Frame(request_popup)
    entry_frame.pack()

    file_name_label = tk.Label(entry_frame, text="Enter File Name:")
    file_name_label.pack(side="left")

    file_name_entry = tk.Entry(entry_frame)
    file_name_entry.pack(side="left")

    def request_fetch():
        file_name = file_name_entry.get()
        if file_name:
            # Xử lý tên file và yêu cầu file ở đây
            #todo
            #
            #
            #
            show_accept_popup(client.hostname,file_name)
            #client.fetch(file_name)   
            
            print(f"Requesting file: {file_name}")
            # Đóng cửa sổ popup sau khi xử lý xong
            request_popup.destroy()

    request_button = tk.Button(request_popup, text="Request", command=request_fetch, bg="#00FF66", activebackground="#CCFF99")
    request_button.pack()

def show_accept_popup(client_request_name, request_file_name):
    popup = tk.Toplevel(root)
    popup.title("Accept request")

    # Tạo một nhãn trong cửa sổ popup
    label = tk.Label(popup, text="Accept fetch request with file '" + request_file_name + "' from '" + client_request_name +"'")
    label.pack(padx=10, pady=10)

    # Hàm xử lý khi nút "Accept" được nhấn
    def accept_action():
        popup.destroy()
        if(client.fetch(request_file_name)):
            client.publish(request_file_name)
            add_item(request_file_name)
        else :
            print("fetch fail !")
        #todo

    # Hàm xử lý khi nút "Cancel" được nhấn
    def cancel_action():
        popup.destroy()
        #todo

    # Tạo nút "Accept" và gắn với hàm xử lý
    accept_button = tk.Button(popup, text="Accept", command=accept_action, bg="#00FF66", activebackground="#CCFF99")
    accept_button.pack(side="left", padx=10, pady=10)

    # Tạo nút "Cancel" và gắn với hàm xử lý
    cancel_button = tk.Button(popup, text="Cancel", command=cancel_action, bg="#FF6666", activebackground="#FFCCCC")
    cancel_button.pack(side="right", padx=10, pady=10)

    # Chạy cửa sổ popup
    popup.mainloop()

def on_enter(event):
    # Lấy nội dung đã nhập từ trường nhập liệu
    cli_input = file_name_entry.get().strip()  # Loại bỏ khoảng trắng thừa
    publish_line = r'^publish\s+.+\s+.+$'
    fetch_line = r'^fetch\s+.+$'

    if re.match(publish_line, cli_input):  # publish
        parts = cli_input.split()
        command = parts[0]
        lname = parts[1]
        fname = parts[2]
        print(f"Command: {command}, Local Name: {lname}, File Name: {fname}")
        publish_file(lname, fname)
    elif re.match(fetch_line, cli_input):  # fetch
        parts = cli_input.split()
        command = parts[0]
        fname = parts[1]
        print(f"Command: {command}, Fetch Name: {fname}")
        # todo : done
        show_accept_popup(client.hostname,fname)
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

def search_for_file_path ():
    currdir = os.getcwd()
    tempdir = filedialog.askopenfilename(parent=root, initialdir=currdir, title='Select file to publish')
    if len(tempdir) > 0:
        print ("You chose: %s" % tempdir)
    return tempdir
#------------------------------------------------------------------------------------------- MAIN


# Tạo cửa sổ giao diện
root = tk.Tk()
root.title("Danh sách các mục của "+ client.hostname)
root.geometry("600x400+100+100")
root.resizable(width=False, height=False)

# Tạo khung cho vùng phía trên
header_frame = tk.Frame(root, borderwidth=2, relief="solid")
header_frame.pack(fill="x")

header_icon_label = tk.Label(header_frame, text="Icon", bg="lightgray")
header_icon_label.grid(row=0, column=0, padx=10, sticky="w")

header_name_label = tk.Label(header_frame, text="Name", bg="lightgray")
header_name_label.grid(row=0, column=1, padx=60, sticky="w")

header_time_label = tk.Label(header_frame, text="Last Fetch Time", bg="lightgray")
header_time_label.grid(row=0, column=2, padx=80, sticky="e")

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
directory_path = os.getcwd()+"/Repository"
print(directory_path)

items = []
def update_item():
    if os.path.exists(directory_path):
        files = os.listdir(directory_path)

        for file in files:
            file_path = os.path.join(directory_path, file)  # Đường dẫn đầy đủ đến tệp
            file_type, encoding = mimetypes.guess_type(file)
            item = Item(file_type, file, os.path.getmtime(file_path))  # Lấy thời gian sửa đổi từ đường dẫn đầy đủ
            item.get_icon_with_type()  # Gọi phương thức này để thiết lập biểu tượng dựa trên loại tệp
            items.append(item)


    # Thêm các mục vào danh sách
    for item in items:
        create_item_frame(item)
def add_item(file):
    file_path = os.path.join(directory_path, file)  # Đường dẫn đầy đủ đến tệp
    file_type, encoding = mimetypes.guess_type(file)
    item = Item(file_type, file, os.path.getmtime(file_path))  # Lấy thời gian sửa đổi từ đường dẫn đầy đủ
    item.get_icon_with_type()  # Gọi phương thức này để thiết lập biểu tượng dựa trên loại tệp
    items.append(item)
    create_item_frame(item)
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

# Tạo nút button
button_publish = tk.Button(button_frame, text="Publish file", command= publish_file_btn, bg="#00FF66", activebackground="#CCFF99")
button_request = tk.Button(button_frame, text="Request fetch file", comman = request_file_popup, bg="#00FF66", activebackground="#CCFF99")
button_cli = tk.Button(button_frame, text="Open CLI", comman = show_cli_popup, bg="#00FF66", activebackground="#CCFF99")
button_publish.pack(side="left", padx=60)  # Thay đổi khoảng cách ngang
button_request.pack(side="left", padx=50)  # Thay đổi khoảng cách ngang
button_cli.pack(side="left", padx=50)  # Thay đổi khoảng cách ngang

# Chạy ứng dụng

def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

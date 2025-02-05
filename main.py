import tkinter as tk
from tkinter import messagebox
import subprocess  # Sử dụng để gọi các file crawl

# Hàm xử lý khi bấm nút Instagram
def open_instagram_window():
    open_keyword_window("Instagram")

# Hàm xử lý khi bấm nút Pinterest
def open_pinterest_window():
    open_keyword_window("Pinterest")

def open_tiktok_window():
    open_keyword_window("Tiktok")

# Hàm mở cửa sổ nhập keyword
def open_keyword_window(platform):
    # Xóa nội dung cửa sổ chính
    for widget in root.winfo_children():
        widget.destroy()

    # Hiển thị giao diện nhập keyword
    tk.Label(root, text=f"Nhập keyword để crawl dữ liệu từ {platform}:", font=("Arial", 14)).pack(pady=20)
    keyword_entry = tk.Entry(root, width=30, font=("Arial", 14))
    keyword_entry.pack(pady=10)

    def crawl_data():
        keyword = keyword_entry.get()
        if keyword:
            messagebox.showinfo("Thông báo", f"Bắt đầu crawl dữ liệu từ {platform} với keyword: {keyword}")
            if platform == "Pinterest":
                subprocess.run(["python", "crawl/crawl_pinterest.py", keyword])
            elif platform == "Instagram":
                subprocess.run(["python", "crawl/crawl_instagram.py", keyword])
            elif platform == "Tiktok":
                subprocess.run(["python", "crawl/crawl_tiktok.py", keyword])
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập keyword!")

    tk.Button(root, text="Crawl Data", font=("Arial", 14), command=crawl_data).pack(pady=10)
    tk.Button(root, text="Quay lại", font=("Arial", 14), command=show_main_window).pack(pady=10)

# Giao diện trang chủ
def show_main_window():
    # Xóa nội dung hiện tại
    for widget in root.winfo_children():
        widget.destroy()

    # Hiển thị giao diện chính
    tk.Label(root, text="Trang chủ", font=("Arial", 20)).pack(pady=20)
    tk.Button(root, text="Instagram", font=("Arial", 14), width=15, command=open_instagram_window).pack(pady=10)
    tk.Button(root, text="Pinterest", font=("Arial", 14), width=15, command=open_pinterest_window).pack(pady=10)
    tk.Button(root, text="Tiktok", font=("Arial", 14), width=15, command=open_tiktok_window).pack(pady=10)

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Data Crawler")
root.geometry("400x300")

# Hiển thị giao diện chính ban đầu
show_main_window()

# Chạy ứng dụng
root.mainloop()

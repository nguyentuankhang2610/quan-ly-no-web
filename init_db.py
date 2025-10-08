# File: init_db.py
import sqlite3

# Tên file cơ sở dữ liệu
DATABASE_FILE = 'debt.db'

# Kết nối tới CSDL (nếu chưa có file, nó sẽ được tạo ra)
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

# Xóa bảng cũ nếu nó tồn tại để đảm bảo bắt đầu sạch
cursor.execute("DROP TABLE IF EXISTS transactions")

# Tạo bảng 'transactions' với các cột cần thiết
# id: Một số định danh duy nhất cho mỗi giao dịch, tự động tăng
# name: Tên người giao dịch, là dạng TEXT và không được rỗng (NOT NULL)
# amount: Số tiền, là dạng REAL (số thực) và không được rỗng
# description: Nội dung, là dạng TEXT
# timestamp: Thời gian giao dịch, không được rỗng
cursor.execute("""
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    timestamp TIMESTAMP NOT NULL
);
""")

# Lưu lại thay đổi (commit) và đóng kết nối
connection.commit()
connection.close()

print(f"Cơ sở dữ liệu '{DATABASE_FILE}' đã được khởi tạo thành công.")
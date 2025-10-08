# File: app.py (phiên bản SQLite)
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# --- Cấu hình CSDL ---
# Render sẽ cung cấp một đường dẫn cố định qua biến môi trường.
# Nếu không có, ta dùng file cục bộ 'debt.db' để test trên máy.
DATABASE_PATH = os.path.join(os.environ.get('RENDER_DISK_PATH', '.'), 'debt.db')


def get_db_connection():
    """Tạo kết nối tới CSDL. Trả về các dòng dữ liệu dạng dictionary."""
    conn = sqlite3.connect(DATABASE_PATH)
    # Dòng này rất quan trọng: nó giúp chúng ta truy cập các cột bằng tên
    # ví dụ: row['name'] thay vì row[1]
    conn.row_factory = sqlite3.Row
    return conn


# --- Các Route (Đường dẫn) của Trang Web ---

@app.route('/')
def index():
    """Route chính, hiển thị trang chủ với form và các bảng báo cáo."""
    conn = get_db_connection()
    # Lấy tất cả giao dịch từ CSDL
    transactions_rows = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()

    # Chuyển đổi các dòng CSDL thành list of dictionaries (cấu trúc cũ)
    transactions = [dict(row) for row in transactions_rows]

    # --- Logic tính toán không thay đổi ---
    debts_by_person = {}
    total_overall_debt = 0
    for trans in transactions:
        name = trans['name']
        debts_by_person[name] = debts_by_person.get(name, 0) + trans['amount']
        total_overall_debt += trans['amount']

    sorted_debts = dict(sorted(debts_by_person.items()))
    display_transactions = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)

    # Chuyển đổi timestamp từ string (nếu cần) sang datetime object cho template
    for trans in display_transactions:
        if isinstance(trans['timestamp'], str):
            trans['timestamp'] = datetime.strptime(trans['timestamp'], '%Y-%m-%d %H:%M:%S.%f')

    return render_template(
        'index.html',
        transactions=display_transactions,
        summary=sorted_debts,
        total_debt=total_overall_debt
    )


@app.route('/add', methods=['POST'])
def add_transaction():
    """Xử lý dữ liệu từ form và thêm vào CSDL."""
    name = request.form.get('name')
    amount_str = request.form.get('amount')
    description = request.form.get('description')
    trans_type = request.form.get('type')

    if not all([name, amount_str, description, trans_type]):
        return redirect(url_for('index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            return redirect(url_for('index'))

        if trans_type == 'pay':
            amount *= -1

        conn = get_db_connection()
        # Dùng '?' để tránh lỗi bảo mật SQL Injection
        conn.execute(
            'INSERT INTO transactions (name, amount, description, timestamp) VALUES (?, ?, ?, ?)',
            (name.strip(), amount, description.strip(), datetime.now())
        )
        conn.commit()
        conn.close()

    except ValueError:
        pass

    return redirect(url_for('index'))


if __name__ == '__main__':
    # Kiểm tra xem CSDL đã tồn tại chưa, nếu chưa thì báo người dùng chạy init_db.py
    if not os.path.exists(DATABASE_PATH):
        print("-" * 50)
        print(f"LỖI: Không tìm thấy file CSDL '{DATABASE_PATH}'.")
        print("Vui lòng chạy lệnh: python init_db.py")
        print("-" * 50)
    else:
        app.run(debug=True)
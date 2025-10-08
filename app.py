import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Tên file để lưu trữ dữ liệu
FILENAME = "debt_log.txt"


# --- TÁI SỬ DỤNG CÁC HÀM XỬ LÝ DỮ LIỆU TỪ PHIÊN BẢN TRƯỚC ---
def load_transactions(filename):
    transactions = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    try:
                        name = row[0]
                        amount = float(row[1])
                        timestamp = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
                        description = row[3]
                        transactions.append(
                            {'name': name, 'amount': amount, 'timestamp': timestamp, 'description': description})
                    except (ValueError, IndexError):
                        pass  # Bỏ qua dòng lỗi một cách im lặng
    except FileNotFoundError:
        pass
    return transactions


def save_transactions(filename, transactions):
    transactions.sort(key=lambda x: x['timestamp'])
    with open(filename, mode='w', newline='', encoding='utf-t_8') as file:
        writer = csv.writer(file)
        for trans in transactions:
            ts_string = trans['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([trans['name'], trans['amount'], ts_string, trans['description']])


# --- CÁC ROUTE (ĐƯỜNG DẪN) CỦA TRANG WEB ---

@app.route('/')
def index():
    """
    Route chính, hiển thị trang chủ với form và các bảng báo cáo.
    """
    # Tải tất cả giao dịch
    transactions = load_transactions(FILENAME)

    # Tính toán tổng nợ theo người
    debts_by_person = {}
    total_overall_debt = 0
    for trans in transactions:
        name = trans['name']
        debts_by_person[name] = debts_by_person.get(name, 0) + trans['amount']
        total_overall_debt += trans['amount']

    # Sắp xếp tên người theo A-Z
    sorted_debts = dict(sorted(debts_by_person.items()))

    # Sắp xếp lịch sử giao dịch theo thời gian mới nhất lên đầu để hiển thị
    display_transactions = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)

    # "Render" (dựng) file HTML và truyền dữ liệu vào cho nó
    return render_template(
        'index.html',
        transactions=display_transactions,
        summary=sorted_debts,
        total_debt=total_overall_debt
    )


@app.route('/add', methods=['POST'])
def add_transaction():
    """
    Route này xử lý dữ liệu khi người dùng gửi form.
    Nó không hiển thị trang nào cả, chỉ xử lý và chuyển hướng về trang chủ.
    """
    # Lấy dữ liệu từ form người dùng gửi lên
    name = request.form.get('name')
    amount_str = request.form.get('amount')
    description = request.form.get('description')
    trans_type = request.form.get('type')  # 'debt' hoặc 'pay'

    # Kiểm tra dữ liệu đầu vào
    if not all([name, amount_str, description, trans_type]):
        # Nếu thiếu thông tin, không làm gì cả và quay lại trang chủ
        return redirect(url_for('index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            # Số tiền phải dương
            return redirect(url_for('index'))

        # Nếu là "Trả Nợ", biến số tiền thành số âm
        if trans_type == 'pay':
            amount *= -1

        transactions = load_transactions(FILENAME)
        transactions.append({
            'name': name.strip(),
            'amount': amount,
            'description': description.strip(),
            'timestamp': datetime.now()
        })
        save_transactions(FILENAME, transactions)

    except ValueError:
        # Nếu số tiền không phải là số hợp lệ, bỏ qua
        pass

    # Chuyển hướng người dùng về lại trang chủ để thấy kết quả mới
    return redirect(url_for('index'))


# Dòng này để chạy ứng dụng khi thực thi file python
if __name__ == '__main__':
    app.run(debug=True)
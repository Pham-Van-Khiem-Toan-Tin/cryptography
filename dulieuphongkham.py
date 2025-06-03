import pandas as pd
import mysql.connector

# ====== Cấu hình kết nối MySQL ======
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
cursor = conn.cursor()

# ====== Đọc file Excel ======
file_path = "C:/Users/KhiemJP/Desktop/dulieucsdl/dulieucacphong.xlsx"  # ← đổi thành đường dẫn file thật
df = pd.read_excel(file_path)

insert_sql = """
INSERT INTO room (room_id, room_name, room_type, status, note, department_id)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    room_name = VALUES(room_name),
    room_type = VALUES(room_type),
    status = VALUES(status),
    note = VALUES(note),
    department_id = VALUES(department_id);
"""

for _, row in df.iterrows():
    cursor.execute(insert_sql, (
        row['room_id'],
        row['room_name'],
        row['room_type'],
        row.get('status', 'đang sử dụng'),
        row.get('note', None),
        row['department_id']
    ))

conn.commit()
print("✅ Đã đổ dữ liệu vào bảng `room` thành công!")

cursor.close()
conn.close()
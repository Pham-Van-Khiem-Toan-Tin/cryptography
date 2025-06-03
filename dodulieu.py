import pandas as pd
import mysql.connector

# Đọc file CSV
df = pd.read_excel("C:/Users/KhiemJP/Desktop/dulieucsdl/dulieucackhoa.xlsx")

# Thêm cột isActive dựa vào giá kê khai

# Kết nối MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
cursor = conn.cursor()

# Insert từng dòng
for _, row in df.iterrows():
    sql = """
    INSERT INTO department (
        id, name, description, position
    ) VALUES (%s, %s, %s, %s)
    """
    values = (
        row["ma_khoa"],
        row["ten_khoa"],
        row["mo_ta"],
        row["vi_tri"],
    )
    cursor.execute(sql, values)

# Lưu thay đổi và đóng
conn.commit()
cursor.close()
conn.close()

print("✅ Đã đổ dữ liệu vào MySQL thành công với isActive đúng logic.")

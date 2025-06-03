import pandas as pd
import mysql.connector

# Đọc file CSV
df = pd.read_csv("C:/Users/KhiemJP/Desktop/Code/codematma/thuoc_drugbank_full.csv", encoding="utf-8-sig")

# Thêm cột isActive dựa vào giá kê khai
df["isActive"] = df["Giá kê khai"].apply(lambda x: False if pd.isna(x) or str(x).strip() == "" else True)

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
    INSERT INTO medicines (
        id, name, registration_no, ingredient, concentration, form,
        packaging, classification, manufacturer, origin_country,
        standard, shelf_life, listed_price, is_active
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        ingredient = VALUES(ingredient),
        concentration = VALUES(concentration),
        form = VALUES(form),
        packaging = VALUES(packaging),
        classification = VALUES(classification),
        manufacturer = VALUES(manufacturer),
        origin_country = VALUES(origin_country),
        standard = VALUES(standard),
        shelf_life = VALUES(shelf_life),
        listed_price = VALUES(listed_price),
        is_active = VALUES(is_active)
    """
    values = (
        row["Số ĐK"],                 # id
        row["Tên thuốc"],            # name
        row["Số ĐK"],                # registration_no
        row["Hoạt chất"],
        row["Hàm lượng"],
        row["Dạng bào chế"],
        row["Đóng gói"],
        row["Phân loại"],
        row["Công ty SX"],
        row["Nước SX"],
        row["Tiêu chuẩn"],
        row["Tuổi thọ"],
        int(row["Giá kê khai"]) if not pd.isna(row["Giá kê khai"]) and str(row["Giá kê khai"]).strip() != "" else None,
        row["isActive"]
    )
    cursor.execute(sql, values)

# Lưu thay đổi và đóng
conn.commit()
cursor.close()
conn.close()

print("✅ Đã đổ dữ liệu vào MySQL thành công với isActive đúng logic.")

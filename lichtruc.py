import mysql.connector
from datetime import datetime, timedelta

# Kết nối với MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
departments_to_schedule = [
    'KHOA_012', 'KHOA_013', 'KHOA_023', 'KHOA_004',
    'KHOA_003', 'KHOA_010', 'KHOA_008', 'KHOA_028', 'KHOA_014'
]
# Ca trực (Ngày, Đêm)
shift_times = ['Ngày', 'Đêm']
cursor = db.cursor()

# Tạo danh sách ngày từ 2010 đến hiện tại
start_date = datetime(2010, 1, 1)
end_date = datetime.today()

# Danh sách các ca trực (sáng, chiều, tối)

# Hàm sinh dữ liệu lịch trực
def generate_shift_schedule(start_date, end_date):
    current_date = start_date
    shift_data = []

    # Duyệt qua từng ngày
    while current_date <= end_date:
        # Sinh các ca trực cho ngày đó
        for shift_time in shift_times:
            for dept_id in departments_to_schedule:
                shift_data.append((current_date.date(), shift_time, dept_id))
        current_date += timedelta(days=1)

    return shift_data

# Sinh dữ liệu lịch trực từ năm 2010 đến nay
shift_schedule_data = generate_shift_schedule(start_date, end_date)
index = 1
# Đổ dữ liệu vào bảng ShiftSchedule với id theo định dạng LT_DDMMYYYY và trường created_at (chỉ ngày)
for shift in shift_schedule_data:
    shift_date, shift_time, dept_id = shift
    shift_id = f"LT_{index:09}" 

    cursor.execute("INSERT INTO shiftschedule (id, shift_date, shift_time, department_id) VALUES (%s, %s, %s, %s)", 
                   (shift_id, shift_date, shift_time, dept_id))
    index +=1
# Commit các thay đổi và đóng kết nối
db.commit()
cursor.close()
db.close()

print("Dữ liệu đã được chèn vào bảng ShiftSchedule với định dạng ID LT_DDMMYYYY và trường created_at (ngày).")

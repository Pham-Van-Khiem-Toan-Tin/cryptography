import mysql.connector
import random
from datetime import datetime, timedelta

# Kết nối đến MySQL
conn = mysql.connector.connect(
    host="localhost",  # Địa chỉ máy chủ MySQL
    user="root",       # Tên người dùng MySQL
    password="271201",  # Mật khẩu MySQL
    database="healthcare"   # Tên cơ sở dữ liệu
)
departments_to_schedule = [
    'KHOA_012', 'KHOA_013', 'KHOA_023', 'KHOA_004',
    'KHOA_003', 'KHOA_010', 'KHOA_008', 'KHOA_028', 'KHOA_014'
]
# Lấy dữ liệu lịch khám từ MySQL
cursor = conn.cursor()
query = '''
        SELECT DISTINCT 
            doctor_id, 
            DATE_FORMAT(appointment_date, '%Y-%m-%d') AS day_appointment
        FROM appointments
        WHERE status != 'Huỷ'
        ORDER BY doctor_id, day_appointment
        '''
cursor.execute(query)
appointment_dates = {}
for doctor_id, day in cursor.fetchall():
    if doctor_id not in appointment_dates:
        appointment_dates[doctor_id] = []
    appointment_dates[doctor_id].append(day)
    
query = '''
        SELECT id, department_id
        FROM doctors
        WHERE department_id IN (%s)
        ''' % ','.join(['%s'] * len(departments_to_schedule))
cursor.execute(query, departments_to_schedule)
doctors_by_dept = {}
for dept_id in departments_to_schedule:
    doctors_by_dept[dept_id] = []
for doctor_id, dept_id in cursor.fetchall():
    if dept_id in doctors_by_dept:
        doctors_by_dept[dept_id].append(doctor_id)
cursor.execute("SELECT * FROM shiftschedule")
shiftSchedules = cursor.fetchall()

def generate_shift_schedule():
    """Sinh lịch trực và đổ vào bảng lichtruc_bacsi"""
    assigned_doctors_by_date = {}
    for schedule in shiftSchedules:
        # Lấy danh sách bác sĩ của khoa
        dept_id = schedule[3]
        current_date = schedule[1]
        shift_id = schedule[0]
        shift_type = schedule[2]
        available_doctors = doctors_by_dept.get(dept_id, [])
        # Lọc bác sĩ không có lịch khám vào current_date
        date_str = current_date.strftime('%Y-%m-%d')
        valid_doctors = [
            doc for doc in available_doctors
            if doc not in appointment_dates or date_str not in appointment_dates[doc]
        ]
        if date_str not in assigned_doctors_by_date:
            assigned_doctors_by_date[date_str] = {'Ngày': [], 'Đêm': []}

        # Loại bỏ bác sĩ đã trực ca khác trong cùng ngày
        other_shift_type = 'Đêm' if shift_type == 'Ngày' else 'Ngày'
        valid_doctors = [
            doc for doc in valid_doctors
            if doc not in assigned_doctors_by_date[date_str][other_shift_type]
        ]
        if valid_doctors:
            # Chọn ngẫu nhiên một bác sĩ
            selected_doctor = random.choice(valid_doctors)
            assigned_doctors_by_date[date_str][shift_type].append(selected_doctor)
            cursor.execute('''
            INSERT INTO shift_doctor (shift_id, doctor_id)
            VALUES (%s, %s)
            ''', (shift_id, selected_doctor))
        else:
            print(f"Không tìm thấy bác sĩ khả dụng cho khoa {dept_id} vào ngày {date_str}")
    conn.commit()
generate_shift_schedule()
cursor.close()
conn.close()

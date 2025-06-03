import random
from datetime import datetime, timedelta
import mysql.connector

# Kết nối CSDL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
cursor = db.cursor(dictionary=True)

# Lấy danh sách bệnh nhân
cursor.execute("SELECT patient_id, date_of_birth FROM patient")
patients = cursor.fetchall()

# Lấy danh sách bác sĩ
cursor.execute("SELECT id FROM doctors")
doctors = cursor.fetchall()

# Hàm tạo thời gian khám trong ngày
def generate_time(base_date):
    hour = random.randint(7, 16)
    minute = random.choice([0, 30])
    return base_date.replace(hour=hour, minute=minute, second=0)

# Lưu lịch tránh trùng
used_slots = set()

# Số lượng lịch cần tạo
total_appointments = 2000000
batch_size = 1000
appointments = []
id_counter = 1  # Đếm từ 1 để tạo LK_000001, LK_000002,...
for _ in range(total_appointments):
    retry = 0
    while True:
        appointment_id = f"LK_{id_counter:08d}"
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        # Mốc thời gian hợp lệ
        dob_datetime = datetime.combine(patient['date_of_birth'], datetime.min.time())
        min_date = max(datetime(2010, 1, 1), dob_datetime)
        max_date = datetime.now()

        if min_date >= max_date:
            retry += 1
            if retry > 10:
                break  # Tránh kẹt vòng lặp
            continue

        random_day = random.randint(0, (max_date - min_date).days)
        appt_date = min_date + timedelta(days=random_day)
        appt_time = generate_time(appt_date)

        # Check trùng lịch
        key1 = (patient['patient_id'], appt_time)
        key2 = (doctor['id'], appt_time)

        if key1 not in used_slots and key2 not in used_slots:
            used_slots.add(key1)
            used_slots.add(key2)
            break

    # Trạng thái
    status = random.choice(['Đang chờ', 'Đã khám', 'Hủy'])

    # Thêm vào danh sách batch insert
    appointments.append((
        appointment_id,
        patient['patient_id'],
        doctor['id'],
        appt_time.strftime('%Y-%m-%d %H:%M:%S'),
        status
    ))
    id_counter += 1
    # Batch insert mỗi 1000 bản ghi
    if len(appointments) == batch_size:
        cursor.executemany("""
            INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, appointments)
        db.commit()
        print(f"Đã insert {len(appointments)} lịch...")
        appointments.clear()

# Insert phần còn lại
if appointments:
    cursor.executemany("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status)
        VALUES (%s, %s, %s, %s)
    """, appointments)
    db.commit()
    print(f"Đã insert {len(appointments)} lịch cuối cùng.")

print("✅ Tạo thành công 500.000 lịch khám từ 2010 đến nay!")

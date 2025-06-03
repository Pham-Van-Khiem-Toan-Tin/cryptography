import mysql.connector
from faker import Faker
from datetime import datetime
from unidecode import unidecode
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum
from collections import defaultdict
import re
import random
from random import choice, randint
import numpy as np
# Kết nối đến MySQL
db = mysql.connector.connect(
    host="localhost",  # Địa chỉ host của MySQL (thường là localhost)
    user="root",       # Tên người dùng của MySQL
    password="271201",  # Mật khẩu MySQL
    database="healthcare"  # Tên cơ sở dữ liệu của bạn
)

cursor = db.cursor()

# Sử dụng Faker để tạo dữ liệu giả
fake = Faker("vi_VN")

# Lấy dữ liệu từ bảng BacSi (bác sĩ), Bộ phận và Khoa
cursor.execute("SELECT id FROM doctors;")
bac_si_list = cursor.fetchall()

cursor.execute("SELECT id FROM departments WHERE id NOT LIKE 'KHOA_%';")
departments = cursor.fetchall()  # Phòng ban không phải khoa (Bảo vệ, Lễ tân, Hành chính, v.v.)

cursor.execute("SELECT id FROM departments WHERE id LIKE 'KHOA_%';")
khoa_list = cursor.fetchall()  # Các khoa (Khoa Nội tổng hợp, Khoa Ngoại tổng hợp, v.v.)
province_to_districts = {}
for district in DistrictEnum:
    province_to_districts.setdefault(district.value.province_code, []).append(district.value)

district_to_wards = {}
for ward in WardEnum:
    district_to_wards.setdefault(ward.value.district_code, []).append(ward.value)
# Hàm kiểm tra tên hợp lệ
def is_valid_name(name):
    invalid_keywords = ['Quý ông', 'Quý bà', 'Quý cô','Bác', 'Cô', 'Bà', 'Anh', 'Chị', 'Ông', 'Mr.', 'Mrs.']
    return not any(keyword in name for keyword in invalid_keywords)
def generate_address_parts():
    province = random.choice(list(ProvinceEnum)).value
    districts = province_to_districts.get(province.code)
    if not districts:
        return "Không rõ", "Không rõ", province.name, "Số ???"
    district = random.choice(districts)
    wards = district_to_wards.get(district.code)
    if not wards:
        return "Không rõ", district.name, province.name, "Số ???"
    ward = random.choice(wards)
    return ward.name, district.name, province.name, f"Số {random.randint(1, 400)}"
used_emails = set()
# cursor.execute("SELECT ssn FROM doctors")
# existing_ssns = set(row[0] for row in cursor.fetchall())
# def generate_unique_ssn(existing_ssns):
#     new_ssn = fake.unique.ssn()
#     while new_ssn in existing_ssns:
#         new_ssn = fake.unique.ssn()
#     existing_ssns.add(new_ssn)  # Đánh dấu đã dùng
#     return new_ssn
def generate_email(name):
    base = unidecode(name).lower()
    base = re.sub(r'[^a-z0-9]', '', base)
    email = f"{base}@hospital.vn"
    suffix = 1
    while email in used_emails:
        email = f"{base}{suffix}@hospital.vn"
        suffix += 1
    used_emails.add(email)
    return email
# Tạo dữ liệu cho bảng staff (cho các nhân viên không phải bác sĩ)
def generate_staff_id(index):
    return f"ST_{str(index).zfill(4)}"
def generate_staff_data(num_staff):
    # Giới hạn số lượng nhân viên theo yêu cầu
    index = 1
    guard_count = 10  # Số lượng bảo vệ
    nurse_count_per_khoa = randint(40, 50)  # Y tá và Hộ lý mỗi khoa từ 40 đến 50 người
    receptionist_count_per_khoa = randint(2, 3)  # Lễ tân mỗi khoa từ 2 đến 3 người
    
    # Bảo vệ, với trạng thái đang làm việc hoặc tạm nghỉ (10 người)
    for _ in range(guard_count):
        staff_id = generate_staff_id(index)
        full_name = fake.name()
        while not is_valid_name(full_name):  # Kiểm tra nếu tên không hợp lệ, tạo lại
            full_name = fake.name()
        
        gender = choice(['Nam', 'Nữ'])
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
        position_title = 'Bảo vệ'
        phone_number = fake.phone_number()
        email = generate_email(full_name)
        # citizen_id = generate_unique_ssn(existing_ssns)
        ward_name, district_name, province_name, house_number = generate_address_parts()
        department_id = choice(departments)[0]  # Gán vào phòng ban bảo vệ
        status = choice(['đang làm', 'tạm nghỉ'])
        note = fake.text(max_nb_chars=100)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = created_at  # Mới tạo lần đầu

        cursor.execute("""
                INSERT INTO staff (staff_id, full_name, gender, date_of_birth, position_title, 
                                   phone_number, email, house_number, ward, district, 
                                   province, department_id, status, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (staff_id, full_name, gender, date_of_birth, position_title, phone_number, email,
                  house_number, ward_name, district_name, province_name, department_id, status, note, created_at, updated_at))
        db.commit()
        index += 1

    # Tạo nhân viên y tá và hộ lý cho các khoa (40-50 người cho mỗi khoa)
    for khoa in khoa_list:
        for _ in range(nurse_count_per_khoa):
            staff_id = generate_staff_id(index)
            full_name = fake.name()
            while not is_valid_name(full_name):  # Kiểm tra nếu tên không hợp lệ, tạo lại
                full_name = fake.name()

            gender = choice(['Nam', 'Nữ'])
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
            position_title = choice(['Y tá', 'Hộ lý'])
            phone_number = generate_email(full_name)
            email = fake.email()
            # citizen_id = generate_unique_ssn(existing_ssns)
            ward_name, district_name, province_name, house_number = generate_address_parts()
            department_id = khoa[0]  # Gán vào khoa cụ thể
            status = choice(['đang làm', 'tạm nghỉ'])
            note = fake.text(max_nb_chars=100)
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = created_at  # Mới tạo lần đầu

            cursor.execute("""
                INSERT INTO staff (staff_id, full_name, gender, date_of_birth, position_title, 
                                   phone_number, email, house_number, ward, district, 
                                   province, department_id, status, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (staff_id, full_name, gender, date_of_birth, position_title, phone_number, email,
                  house_number, ward_name, district_name, province_name, department_id, status, note, created_at, updated_at))
            db.commit()
            index += 1

    # Tạo lễ tân cho các khoa (2-3 người cho mỗi khoa)
    for khoa in khoa_list:
        for _ in range(receptionist_count_per_khoa):
            staff_id = generate_staff_id(index)
            full_name = fake.name()
            while not is_valid_name(full_name):  # Kiểm tra nếu tên không hợp lệ, tạo lại
                full_name = fake.name()

            gender = choice(['Nam', 'Nữ'])
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
            position_title = 'Lễ tân'
            phone_number = fake.phone_number()
            email = generate_email(full_name)
            # citizen_id = generate_unique_ssn(existing_ssns)
            ward_name, district_name, province_name, house_number = generate_address_parts()
            department_id = khoa[0]  # Gán vào khoa cụ thể
            status = choice(['đang làm', 'tạm nghỉ'])
            note = fake.text(max_nb_chars=100)
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = created_at  # Mới tạo lần đầu

            cursor.execute("""
                INSERT INTO staff (staff_id, full_name, gender, date_of_birth, position_title, 
                                   phone_number, email, house_number, ward, district, 
                                   province, department_id, status, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (staff_id, full_name, gender, date_of_birth, position_title, phone_number, email,
                  house_number, ward_name, district_name, province_name, department_id, status, note, created_at, updated_at))
            db.commit()
            index += 1

    print("Dữ liệu nhân viên đã được tạo thành công!")

# Tạo 10 nhân viên mẫu
generate_staff_data(1000)

cursor.close()
db.close()

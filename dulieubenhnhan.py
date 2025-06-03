import random
import mysql.connector
from faker import Faker
from unidecode import unidecode
from collections import defaultdict
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum
import re
import numpy as np
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
genders = ["Nam", "Nữ"]
fake = Faker("vi_VN")
cursor = conn.cursor()
province_to_districts = {}
for district in DistrictEnum:
    province_to_districts.setdefault(district.value.province_code, []).append(district.value)

district_to_wards = {}
for ward in WardEnum:
    district_to_wards.setdefault(ward.value.district_code, []).append(ward.value)
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
def generate_email(name):
    base = unidecode(name).lower()
    base = re.sub(r'[^a-z0-9]', '', base)
    email = f"{base}@gmail.com"
    suffix = 1
    while email in used_emails:
        email = f"{base}{suffix}@hospital.vn"
        suffix += 1
    used_emails.add(email)
    return email
def is_valid_name(name):
    invalid_keywords = ['Quý ông', 'Quý bà', 'Quý cô','Bác', 'Cô', 'Bà', 'Anh', 'Chị', 'Ông', 'Mr.', 'Mrs.']
    return not any(keyword in name for keyword in invalid_keywords)
def generate_patient(n):
    records = []
    for i in range(n):
        ward_name, district_name, province_name, house_number = generate_address_parts()
        name = fake.name()
        while not is_valid_name(name):  # Kiểm tra nếu tên không hợp lệ, tạo lại
            name = fake.name()
        records.append((
            f"BN_{i+1:04d}",
            name,
            random.choice(genders),
            fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            fake.unique.numerify(text="0###########"),
            fake.unique.bothify(text="##??#######"),
            fake.phone_number(),
            generate_email(name),
            house_number,
            ward_name,
            district_name,
            province_name,
            fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S'),
        ))
    return records
patients = generate_patient(10000)
sql = """
INSERT INTO patient (
    patient_id, full_name, gender, date_of_birth,
    citizen_id, health_insurance, phone_number, email,
    house_number, ward, district, province,
    created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(sql, patients)
conn.commit()

print("✅ Đã thêm dữ liệu bằng mysql-connector-python")

cursor.close()
conn.close()
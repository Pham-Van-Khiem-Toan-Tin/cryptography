import random
import mysql.connector
from faker import Faker
from unidecode import unidecode
from collections import defaultdict
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum
import re
import numpy as np

# Cấu hình
fake = Faker("vi_VN")
department_ids = [f"KHOA_{i:03}" for i in range(1, 34)]
specialties = [
    "Nội tổng quát", "Ngoại thần kinh", "Tim mạch", "Chấn thương chỉnh hình", "Hô hấp",
    "Tiêu hóa", "Da liễu", "Sản phụ khoa", "Mắt", "Tai mũi họng", "Nhi", "Thận - Tiết niệu",
    "Ung bướu", "Thần kinh", "Nội tiết", "Gây mê hồi sức", "Y học cổ truyền"
]
degrees = ["BS", "ThS.BS", "TS.BS", "PGS.TS.BS", "GS.TS.BS"]
genders = ["Nam", "Nữ"]
department_specialties_map = {
    "KHOA_001": ["Nội tổng quát"],
    "KHOA_002": ["Ngoại thần kinh"],
    "KHOA_003": ["Tim mạch"],
    "KHOA_004": ["Chấn thương chỉnh hình"],
    "KHOA_005": ["Hô hấp"],
    "KHOA_006": ["Tiêu hóa"],
    "KHOA_007": ["Da liễu"],
    "KHOA_008": ["Sản phụ khoa"],
    "KHOA_009": ["Mắt"],
    "KHOA_010": ["Tai mũi họng"],
    "KHOA_011": ["Nhi"],
    "KHOA_012": ["Thận - Tiết niệu"],
    "KHOA_013": ["Ung bướu"],
    "KHOA_014": ["Thần kinh"],
    "KHOA_015": ["Nội tiết"],
    "KHOA_016": ["Gây mê hồi sức"],
    "KHOA_017": ["Y học cổ truyền"],
    # Từ KHOA_018 trở đi, bạn có thể phân phối lại nếu cần (gán chung hoặc chọn random từ danh sách specialties)
}
def is_valid_name(name):
    invalid_keywords = ['Quý ông', 'Quý bà', 'Quý cô','Bác', 'Cô', 'Bà', 'Anh', 'Chị', 'Ông', 'Mr.', 'Mrs.']
    return not any(keyword in name for keyword in invalid_keywords)
# Đảm bảo mỗi khoa >=2 bác sĩ, tổng là 300
base = [10] * len(department_ids)
remaining = 1000 - sum(base)
adds = np.random.multinomial(remaining, [1/len(department_ids)]*len(department_ids))
final_counts = [base[i] + adds[i] for i in range(len(department_ids))]
dept_doctor_count = dict(zip(department_ids, final_counts))

# Địa chỉ hành chính
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

# Email xử lý
used_emails = set()
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

# Sinh dữ liệu
doctors = []
index = 1
for dept_id, count in dept_doctor_count.items():
    dept_doctors = []
    for _ in range(count):
        name = fake.name()
        while not is_valid_name(name):  # Kiểm tra nếu tên không hợp lệ, tạo lại
            name = fake.name()
        exp = random.randint(1, 35)
        ward_name, district_name, province_name, house_number = generate_address_parts()
        doctor = {
            "id": f"BS_{index:04}",
            "full_name": name,
            "gender": random.choice(genders),
            "specialty": random.choice(department_specialties_map.get(dept_id, specialties)),
            "degree": random.choice(degrees),
            "phone": fake.phone_number(),
            "email": generate_email(name),
            "department_id": dept_id,
            "years_of_experience": exp,
            "house_number": house_number,
            "ward": ward_name,
            "district": district_name,
            "province": province_name
        }
        dept_doctors.append(doctor)
        index += 1

    # Phân vai
    dept_doctors.sort(key=lambda d: d["years_of_experience"], reverse=True)
    for i, doc in enumerate(dept_doctors):
        if i == 0:
            doc["position"] = "Trưởng khoa"
        elif i == 1:
            doc["position"] = "Phó khoa"
        else:
            doc["position"] = "Bác sĩ"
        doctors.append(tuple(doc.values()))

# Kết nối MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="271201",
    database="healthcare"
)
cursor = conn.cursor()

# Tạo bảng nếu cần
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id VARCHAR(10) PRIMARY KEY,
    full_name VARCHAR(100),
    gender VARCHAR(10),
    specialty VARCHAR(100),
    degree VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    department_id VARCHAR(10),
    years_of_experience INT,
    house_number VARCHAR(50),
    ward VARCHAR(100),
    district VARCHAR(100),
    province VARCHAR(100),
    position VARCHAR(50)
)
""")

# Insert
sql = """
INSERT INTO doctors (
    id, full_name, gender, specialty, degree, phone, email,
    department_id, years_of_experience, house_number, ward, district, province, position
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(sql, doctors)
conn.commit()
cursor.close()
conn.close()

print(f"✅ Đã sinh {len(doctors)} bác sĩ (mỗi khoa ít nhất 10 người) và ghi vào MySQL.")

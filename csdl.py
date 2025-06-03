import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector
from mysql.connector import Error

# Khởi tạo Faker
fake = Faker()

# Danh sách triệu chứng dị ứng
allergy_symptoms = [
    ('Rash', 'Mild'),
    ('Itching', 'Mild'),
    ('Swelling', 'Moderate'),
    ('Difficulty Breathing', 'Severe'),
    ('Anaphylaxis', 'Severe')
]

# Danh sách mã y tế mở rộng
medical_codes = [
    # Diagnosis
    ('185345009', 'Asthma', 'Diagnosis'),
    ('314000', 'Hypertension', 'Diagnosis'),
    ('E11.9', 'Type 2 Diabetes Mellitus', 'Diagnosis'),
    ('J18.9', 'Pneumonia', 'Diagnosis'),
    ('I21.9', 'Acute Myocardial Infarction', 'Diagnosis'),
    ('M54.9', 'Back Pain', 'Diagnosis'),
    ('F32.9', 'Depression', 'Diagnosis'),
    ('K29.7', 'Gastritis', 'Diagnosis'),
    # LabTest
    ('8310-5', 'Blood Glucose', 'LabTest'),
    ('2345-7', 'Hemoglobin A1c', 'LabTest'),
    ('6690-2', 'Complete Blood Count', 'LabTest'),
    ('2951-2', 'Sodium Level', 'LabTest'),
    ('2160-0', 'Creatinine', 'LabTest'),
    ('1751-7', 'Cholesterol Total', 'LabTest'),
    ('4548-4', 'Liver Function Test', 'LabTest'),
    # Medication
    ('197361', 'Albuterol', 'Medication'),
    ('198405', 'Insulin', 'Medication'),
    ('314076', 'Paracetamol', 'Medication'),
    ('315286', 'Atorvastatin', 'Medication'),
    ('198211', 'Metformin', 'Medication'),
    ('310798', 'Amoxicillin', 'Medication'),
    ('198240', 'Omeprazole', 'Medication'),
    # Procedure
    ('314076', 'Appendectomy', 'Procedure'), # Note: This code is repeated for Paracetamol. Might want to check.
    ('387713003', 'Colonoscopy', 'Procedure'),
    ('71010', 'Chest X-ray', 'Procedure'),
    ('74160', 'CT Scan Abdomen', 'Procedure'),
    ('33586001', 'Coronary Artery Bypass Graft', 'Procedure'),
    ('392021009', 'Knee Arthroscopy', 'Procedure'),
    # Allergy
    ('90688005', 'Penicillin Allergy', 'Allergy'),
    ('419263009', 'Peanut Allergy', 'Allergy'),
    ('232347008', 'Dust Mite Allergy', 'Allergy'),
    ('418689008', 'Shellfish Allergy', 'Allergy'),
    ('91936005', 'Latex Allergy', 'Allergy'),
    ('300913006', 'Egg Allergy', 'Allergy'),
    ('425525006', 'Soy Allergy', 'Allergy'),
    ('91930004', 'Pollen Allergy', 'Allergy'),
    # Immunization
    ('90734009', 'Influenza Vaccine', 'Immunization'),
    ('127785005', 'Hepatitis B Vaccine', 'Immunization'),
    ('396427003', 'HPV Vaccine', 'Immunization'),
    ('333621006', 'Tetanus Vaccine', 'Immunization'),
    ('396429000', 'Pneumococcal Vaccine', 'Immunization')
]
# Danh sách các loại địa chỉ
address_types = ['Home', 'Work', 'Temporary', 'Mailing']
# Kết nối MySQL
conn = None # Khởi tạo conn để đảm bảo nó luôn được định nghĩa
cursor = None
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Thay bằng tên người dùng MySQL
        password="271201",  # Thay bằng mật khẩu MySQL
        database="healthcare_db"
    )
    cursor = conn.cursor()

    # --- Bắt đầu phần tạo dữ liệu tĩnh và tra cứu ---
    # Bắt đầu giao dịch cho dữ liệu tĩnh
    conn.start_transaction()

    # Tạo dữ liệu Department
    departments = []
    for dept in ['Cardiology', 'Pediatrics', 'Surgery', 'General Medicine']:
        dept_id = str(uuid.uuid4())
        departments.append((dept_id, dept)) # Lưu cả ID và tên để tiện tra cứu
        cursor.execute("""
            INSERT INTO Department (department_id, department_name, description)
            VALUES (%s, %s, %s)
        """, (dept_id, dept, f'Department of {dept}'))

    # Tạo dữ liệu Hospital
    hospitals = []
    for _ in range(10):
        hospital_id = str(uuid.uuid4())
        hospitals.append(hospital_id)
        cursor.execute("""
            INSERT INTO Hospital (hospital_id, hospital_name, address, phone)
            VALUES (%s, %s, %s, %s)
        """, (
            hospital_id,
            fake.company() + ' Hospital',
            fake.address().replace('\n', ', '),
            fake.phone_number()
        ))

    # Tạo dữ liệu Doctor và liên kết
    doctors = [] # Sẽ lưu doctor_id
    doctor_batch = []
    doctor_hospital_batch = []
    doctor_department_batch = []

    # Lưu trữ thông tin bệnh viện/khoa mà mỗi bác sĩ làm việc để tra cứu nhanh
    doctor_hospital_map = {} # {doctor_id: [hospital_id1, hospital_id2]}
    doctor_department_map = {} # {doctor_id: [department_id1, department_id2]}

    department_ids = [d[0] for d in departments] # Chỉ lấy IDs của department
    for _ in range(200):
        doctor_id = str(uuid.uuid4())
        doctors.append(doctor_id)
        doctor_batch.append((
            doctor_id,
            fake.first_name(),
            fake.last_name(),
            random.choice(['Cardiology', 'Pediatrics', 'Surgery', 'General Practice']),
            fake.phone_number(),
            fake.email()
        ))
        
        # Thêm vào map để tra cứu
        doctor_hospital_map[doctor_id] = []
        assigned_hospitals = random.sample(hospitals, random.randint(1, 3))
        for hospital_id in assigned_hospitals:
            doctor_hospital_batch.append((
                doctor_id,
                hospital_id,
                fake.date_this_year(),
                None
            ))
            doctor_hospital_map[doctor_id].append(hospital_id)
        
        doctor_department_map[doctor_id] = []
        assigned_departments = random.sample(department_ids, random.randint(1, 2))
        for department_id in assigned_departments:
            doctor_department_batch.append((
                doctor_id,
                department_id,
                fake.date_this_year(),
                None
            ))
            doctor_department_map[doctor_id].append(department_id)

    cursor.executemany("""
        INSERT INTO Doctor (doctor_id, first_name, last_name, specialty, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, doctor_batch)

    cursor.executemany("""
        INSERT INTO Doctor_Hospital (doctor_id, hospital_id, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """, doctor_hospital_batch)

    cursor.executemany("""
        INSERT INTO Doctor_Department (doctor_id, department_id, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """, doctor_department_batch)

    # Tạo dữ liệu LabTest
    # Lấy ra các mã LabTest để dùng sau này
    lab_test_codes = [c for c in medical_codes if c[2] == 'LabTest']
    lab_tests_info = [] # (test_id, test_code, test_name)
    for code, name, _ in lab_test_codes:
        test_id = str(uuid.uuid4())
        lab_tests_info.append((test_id, code, name)) # Lưu ID, code, name để tra cứu
        cursor.execute("""
            INSERT INTO LabTest (test_id, test_code, test_name, description)
            VALUES (%s, %s, %s, %s)
        """, (test_id, code, name, f'Test for {name}'))

    # Cam kết giao dịch cho dữ liệu tĩnh
    conn.commit()
    print("Static data (Departments, Hospitals, Doctors, LabTests) committed.")

    # --- Bắt đầu phần tạo dữ liệu động (số lượng lớn) ---
    total_patients = 100000
    batch_size = 10000
    
    # Lọc các mã theo loại để dùng nhanh hơn
    diagnosis_codes = [c for c in medical_codes if c[2] == 'Diagnosis']
    medication_codes = [c for c in medical_codes if c[2] == 'Medication']
    procedure_codes = [c for c in medical_codes if c[2] == 'Procedure']
    allergy_codes = [c for c in medical_codes if c[2] == 'Allergy']
    immunization_codes = [c for c in medical_codes if c[2] == 'Immunization']
    
    # Chỉ lấy IDs của lab_tests_info cho random.choice
    lab_test_ids = [lt[0] for lt in lab_tests_info] 

    for batch_start in range(0, total_patients, batch_size):
        print(f"Processing batch {batch_start // batch_size + 1}/{total_patients // batch_size} for patient data...")
        try:
            conn.start_transaction()

            # Tạo dữ liệu Patient, Address, Insurance
            patient_batch = []
            address_batch = []
            insurance_batch = []
            
            # Danh sách patient_id của batch hiện tại để sử dụng cho Encounter
            current_batch_patient_ids = [] 

            for _ in range(batch_size):
                patient_id = str(uuid.uuid4())
                current_batch_patient_ids.append(patient_id) # Thêm vào danh sách tạm thời
                patient_batch.append((
                    patient_id,
                    fake.first_name(),
                    fake.last_name(),
                    fake.date_of_birth(minimum_age=0, maximum_age=90),
                    random.choice(['Male', 'Female', 'Other']),
                    fake.phone_number(),
                    fake.email()
                ))
                # --- PHẦN THAY ĐỔI ĐỂ TẠO NHIỀU ĐỊA CHỈ CHO MỖI BỆNH NHÂN ---
                address_id = str(uuid.uuid4())
                address_batch.append((
                    address_id,
                    patient_id,
                    fake.street_address(),
                    fake.city(),
                    fake.state(),
                    fake.postcode(),
                    fake.country(),
                    'Home' # Loại địa chỉ mặc định
                ))
                # Tạo thêm từ 0 đến 2 địa chỉ khác (tổng cộng 1 đến 3 địa chỉ)
                num_additional_addresses = random.randint(0, 2)
                # Loại địa chỉ còn lại để chọn ngẫu nhiên, tránh trùng lặp nếu chỉ có 1 địa chỉ
                available_address_types = [at for at in address_types if at != 'Home'] 
                
                # Đảm bảo không chọn lại cùng loại địa chỉ trong cùng một bệnh nhân
                chosen_address_types = ['Home'] # Loại địa chỉ đã được sử dụng
                
                for _ in range(num_additional_addresses):
                    if not available_address_types: # Nếu không còn loại địa chỉ nào khác để chọn
                        break # Thoát vòng lặp
                    
                    selected_type = random.choice(available_address_types)
                    chosen_address_types.append(selected_type)
                    available_address_types.remove(selected_type) # Loại bỏ để tránh lặp lại

                    address_id = str(uuid.uuid4())
                    address_batch.append((
                        address_id,
                        patient_id,
                        fake.street_address(),
                        fake.city(),
                        fake.state(),
                        fake.postcode(),
                        fake.country(),
                        selected_type # Loại địa chỉ được chọn ngẫu nhiên
                    ))
                # --- KẾT THÚC PHẦN THAY ĐỔI ---
                num_insurances = random.randint(0, 3) 
                for _ in range(num_insurances):
                    insurance_id = str(uuid.uuid4())
                    insurance_batch.append((
                        insurance_id,
                        patient_id,
                        fake.company(),
                        fake.bothify(text='POL-#####'),
                        fake.date_this_year(),
                        fake.date_this_year() + timedelta(days=random.randint(365, 1825)) # Thời hạn 1-5 năm
                    ))

            cursor.executemany("""
                INSERT INTO Patient (patient_id, first_name, last_name, birth_date, gender, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, patient_batch)

            cursor.executemany("""
                INSERT INTO Address (address_id, patient_id, street, city, state, postal_code, country, address_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, address_batch)

            if insurance_batch:
                cursor.executemany("""
                    INSERT INTO Insurance (insurance_id, patient_id, provider_name, policy_number, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, insurance_batch)

            # Tạo dữ liệu Encounter và các bảng liên quan
            encounter_batch = []
            diagnosis_batch = []
            medication_batch = []
            medication_detail_batch = []
            lab_result_batch = []
            procedure_batch = []
            allergy_batch = []
            allergy_symptom_batch = []
            immunization_batch = []

            for patient_id in current_batch_patient_ids: # Lặp qua bệnh nhân của batch hiện tại
                num_encounters = random.randint(1, 5)
                for _ in range(num_encounters):
                    encounter_id = str(uuid.uuid4())
                    encounter_date = fake.date_time_this_year()
                    
                    # Chọn bác sĩ ngẫu nhiên và tìm bệnh viện/khoa mà bác sĩ đó làm việc từ map
                    doctor_id = random.choice(doctors)
                    
                    # Đảm bảo bác sĩ có bệnh viện và khoa được gán
                    hospital_id = random.choice(doctor_hospital_map.get(doctor_id, hospitals))
                    department_id = random.choice(doctor_department_map.get(doctor_id, department_ids))
                    
                    encounter_batch.append((
                        encounter_id,
                        patient_id,
                        doctor_id,
                        hospital_id,
                        department_id,
                        encounter_date,
                        random.choice(['Checkup', 'Follow-up', 'Emergency', 'Consultation', 'Routine Visit'])
                    ))

                    # Diagnosis
                    diagnosis_id = str(uuid.uuid4())
                    diag_code, diag_name, _ = random.choice(diagnosis_codes)
                    diagnosis_batch.append((
                        diagnosis_id,
                        patient_id,
                        encounter_id,
                        diag_code,
                        diag_name,
                        encounter_date
                    ))

                    # Medication (có thể có nhiều loại thuốc cho 1 encounter)
                    if random.random() < 0.7: # Tỷ lệ có thuốc
                        num_meds = random.randint(1, 3)
                        for _ in range(num_meds):
                            medication_id = str(uuid.uuid4())
                            medication_code, medication_name, _ = random.choice(medication_codes)
                            med_start_date = encounter_date
                            med_end_date = med_start_date + timedelta(days=random.randint(7, 90))

                            medication_batch.append((
                                medication_id,
                                patient_id,
                                encounter_id,
                                doctor_id,
                                medication_code,
                                medication_name,
                                med_start_date,
                                med_end_date
                            ))
                            detail_id = str(uuid.uuid4())
                            medication_detail_batch.append((
                                detail_id,
                                medication_id,
                                random.choice(['Take 1 tablet daily', 'Take 2 pills twice a day', 'Apply topically as needed']),
                                random.choice([1, 2, 3]), # Sửa từ random.randint(1,2,3)
                                random.randint(7, 90),
                                random.choice(['days', 'weeks', 'months'])
                            ))

                    # LabResult (có thể có nhiều xét nghiệm cho 1 encounter)
                    if random.random() < 0.6: # Tỷ lệ có xét nghiệm
                        num_labs = random.randint(1, 2)
                        for _ in range(num_labs):
                            result_id = str(uuid.uuid4())
                            selected_lab_test_id = random.choice(lab_test_ids) # Chọn ID của LabTest đã tạo
                            lab_result_batch.append((
                                result_id,
                                patient_id,
                                encounter_id,
                                selected_lab_test_id,
                                round(random.uniform(70, 200), 2), # Giá trị ngẫu nhiên
                                random.choice(['mg/dL', 'mmol/L', 'mU/L', 'cells/uL', 'g/dL']),
                                encounter_date
                            ))

                    # Procedure
                    if random.random() < 0.2: # Tỷ lệ có thủ tục
                        procedure_id = str(uuid.uuid4())
                        proc_code, proc_name, _ = random.choice(procedure_codes)
                        procedure_batch.append((
                            procedure_id,
                            patient_id,
                            encounter_id,
                            proc_code,
                            proc_name,
                            encounter_date
                        ))

                    # Allergy (Mỗi encounter có thể ghi nhận hoặc không ghi nhận dị ứng)
                    if random.random() < 0.1: # Tỷ lệ có dị ứng mới được ghi nhận
                        allergy_id = str(uuid.uuid4())
                        all_code, all_name, _ = random.choice(allergy_codes)
                        allergy_batch.append((
                            allergy_id,
                            patient_id,
                            all_code,
                            all_name,
                            encounter_date # Ngày phát hiện/ghi nhận dị ứng
                        ))
                        # Tạo 1-3 triệu chứng cho dị ứng này
                        num_symptoms = random.randint(1, 3)
                        selected_symptoms = random.sample(allergy_symptoms, num_symptoms)
                        for symptom_desc, severity in selected_symptoms:
                            symptom_id = str(uuid.uuid4())
                            allergy_symptom_batch.append((
                                symptom_id,
                                allergy_id,
                                symptom_desc, # Đã sửa lỗi 'symptom_desc ingred'
                                severity
                            ))

                    # Immunization
                    if random.random() < 0.05: # Tỷ lệ có tiêm chủng trong encounter này
                        immunization_id = str(uuid.uuid4())
                        imm_code, imm_name, _ = random.choice(immunization_codes) # Sửa immun_medical_codes
                        immunization_batch.append((
                            immunization_id,
                            patient_id,
                            encounter_id,
                            imm_code,
                            imm_name,
                            encounter_date # Ngày tiêm chủng
                        ))

            # Thực thi chèn dữ liệu theo lô
            cursor.executemany("""
                INSERT INTO Encounter (encounter_id, patient_id, doctor_id, hospital_id, department_id, encounter_date, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, encounter_batch)

            cursor.executemany("""
                INSERT INTO Diagnosis (diagnosis_id, patient_id, encounter_id, diagnosis_code, diagnosis_description, diagnosis_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, diagnosis_batch)

            # Sửa lỗi cú pháp SQL và thêm dấu ngoặc đóng cho VALUES
            cursor.executemany("""
                INSERT INTO Medication (medication_id, patient_id, encounter_id, doctor_id, medication_code, medication_name, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, medication_batch)

            # Sửa lỗi cú pháp SQL
            cursor.executemany("""
                INSERT INTO MedicationDetail (detail_id, medication_id, dosage_instruction, frequency_per_day, duration, duration_unit)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, medication_detail_batch)

            cursor.executemany("""
                INSERT INTO LabResult (result_id, patient_id, encounter_id, test_id, result_value, result_unit, result_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, lab_result_batch)

            cursor.executemany("""
                INSERT INTO MedicalProcedure (procedure_id, patient_id, encounter_id, procedure_code, procedure_name, procedure_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, procedure_batch)

            cursor.executemany("""
                INSERT INTO Allergy (allergy_id, patient_id, allergy_code, allergy_name, onset_date)
                VALUES (%s, %s, %s, %s, %s)
            """, allergy_batch)

            # Sửa lỗi cú pháp SQL và tên cột
            cursor.executemany("""
                INSERT INTO Allergy_Symptom (symptom_id, allergy_id, symptom_description, severity)
                VALUES (%s, %s, %s, %s)
            """, allergy_symptom_batch)

            # Sửa lỗi cú pháp SQL
            cursor.executemany("""
                INSERT INTO Immunization (immunization_id, patient_id, encounter_id, vaccine_code, vaccine_name, administration_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, immunization_batch)

            conn.commit()
            print(f"Batch {batch_start // batch_size + 1} completed.")

        except Error as e:
            print(f"Error in batch {batch_start // batch_size + 1}: {e}")
            if conn: # Đảm bảo conn đã được khởi tạo
                conn.rollback()
            raise # Ném lại ngoại lệ để dừng chương trình nếu có lỗi nghiêm trọng

except Error as e:
    print(f"Connection Error: {e}")

finally:
    if conn and conn.is_connected(): # Kiểm tra xem conn có tồn tại và đang kết nối không
        cursor.close()
        conn.close()
        print("Closed MySQL connection.")
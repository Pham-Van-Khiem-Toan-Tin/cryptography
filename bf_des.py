import random
import time
from tabulate import tabulate # Để in bảng đẹp hơn

# --- Các hàm tiện ích cho thao tác bit và chuyển đổi ---
# Di chuyển lên đầu để đảm bảo chúng được định nghĩa trước khi được gọi

def string_to_bytes(s):
    """Chuyển chuỗi thành danh sách các giá trị byte (decimal)."""
    return list(s.encode('utf-8'))

def bytes_to_bits(byte_list):
    """Chuyển danh sách byte thành danh sách bit."""
    bits = []
    for byte in byte_list:
        bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)]) # MSB first
    return bits

def bits_to_bytes(bit_list):
    """Chuyển danh sách bit thành danh sách byte."""
    bytes_list = []
    for i in range(0, len(bit_list), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bit_list[i + j]
        bytes_list.append(byte)
    return bytes_list

def permute(block, permutation_table):
    """Áp dụng một bảng hoán vị lên một khối bit."""
    return [block[p - 1] for p in permutation_table]

def xor_bits(bits1, bits2):
    """Thực hiện phép XOR bitwise giữa hai danh sách bit."""
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

def left_shift_bits(bits, num_shifts):
    """Dịch trái vòng một danh sách bit."""
    return bits[num_shifts:] + bits[:num_shifts]

def bytes_to_hex_str(byte_list):
    """Chuyển danh sách byte thành chuỗi hex."""
    return [format(b, '02x') for b in byte_list]


# --- Các bảng và hằng số DES ---

# Initial Permutation (IP) - Hoán vị ban đầu
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Final Permutation (FP) - Hoán vị cuối cùng (nghịch đảo của IP)
FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Permuted Choice 1 (PC-1) - Chọn và hoán vị khóa ban đầu
PC_1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# Permuted Choice 2 (PC-2) - Chọn và hoán vị để tạo khóa con
PC_2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Left Shift Schedule - Số lượng dịch trái cho mỗi vòng
SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Expansion Permutation (E-box) - Mở rộng 32 bit thành 48 bit
E_BOX = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# P-box - Hoán vị sau S-box
P_BOX = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

# S-boxes (S1 đến S8)
S_BOXES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 2, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
    ],
]


# --- Key Schedule của DES ---

def des_key_schedule(key_bytes):
    """
    Tạo 16 khóa con (subkey) 48 bit từ khóa 64 bit (56 bit hiệu dụng).
    Args:
        key_bytes (list of int): Khóa 8 byte.
    Returns:
        list of list of int: Danh sách 16 khóa con, mỗi khóa là 48 bit.
    """
    if len(key_bytes) != 8:
        raise ValueError("DES key must be 8 bytes (64 bits).")
    
    key_bits = bytes_to_bits(key_bytes)
    
    # PC-1: Chọn 56 bit từ 64 bit và hoán vị
    permuted_key = permute(key_bits, PC_1)
    
    # Chia thành C0 và D0 (28 bit mỗi phần)
    C = permuted_key[:28]
    D = permuted_key[28:]
    
    subkeys = []
    for i in range(16): # 16 vòng
        # Dịch trái C và D
        C = left_shift_bits(C, SHIFT_SCHEDULE[i])
        D = left_shift_bits(D, SHIFT_SCHEDULE[i])
        
        # Kết hợp C và D
        combined_CD = C + D
        
        # PC-2: Chọn 48 bit để tạo khóa con
        subkey = permute(combined_CD, PC_2)
        subkeys.append(subkey)
        
    return subkeys

# --- Hàm Feistel (F-function) của DES ---

def des_feistel_function(right_half_bits, subkey_bits):
    """
    Thực hiện hàm Feistel của DES.
    Args:
        right_half_bits (list of int): Nửa phải của khối (32 bit).
        subkey_bits (list of int): Khóa con (48 bit).
    Returns:
        list of int: Kết quả 32 bit của hàm Feistel.
    """
    # 1. Mở rộng R (32 bit) thành 48 bit bằng E-box
    expanded_R = permute(right_half_bits, E_BOX)
    
    # 2. XOR với khóa con (48 bit)
    xor_result = xor_bits(expanded_R, subkey_bits)
    
    # 3. Chia 48 bit thành 8 khối 6 bit và áp dụng S-boxes
    sbox_output_bits = []
    for i in range(8): # 8 S-boxes
        six_bits = xor_result[i*6 : (i+1)*6]
        
        # Lấy hàng (row) từ bit đầu tiên và bit cuối cùng
        row = (six_bits[0] << 1) | six_bits[5]
        
        # Lấy cột (column) từ 4 bit giữa
        col = (six_bits[1] << 3) | (six_bits[2] << 2) | (six_bits[3] << 1) | six_bits[4]
        
        # Tra cứu S-box và chuyển kết quả 4 bit thành danh sách bit
        sbox_value = S_BOXES[i][row][col]
        sbox_output_bits.extend([(sbox_value >> j) & 1 for j in range(3, -1, -1)]) # 4 bits, MSB first
        
    # 4. Áp dụng P-box lên kết quả 32 bit từ S-boxes
    pbox_result = permute(sbox_output_bits, P_BOX)
    
    return pbox_result

# --- Hàm mã hóa DES một khối ---

def des_encrypt_block(plaintext_block_bytes, key_bytes):
    """
    Mã hóa một khối plaintext 8 byte (64 bit) bằng DES.
    Args:
        plaintext_block_bytes (list of int): Danh sách 8 byte của khối plaintext.
        key_bytes (list of int): Khóa 8 byte (64 bit, 56 bit hiệu dụng).
    Returns:
        list of int: Danh sách 8 byte của khối ciphertext.
    """
    if len(plaintext_block_bytes) != 8:
        raise ValueError("Plaintext block must be 8 bytes (64 bits).")
    if len(key_bytes) != 8:
        raise ValueError("Key must be 8 bytes (64 bits).")

    # 1. Tạo các khóa con
    subkeys = des_key_schedule(key_bytes)
    
    # 2. Chuyển plaintext thành danh sách bit
    plaintext_bits = bytes_to_bits(plaintext_block_bytes)
    
    # 3. Hoán vị ban đầu (IP)
    initial_permutation = permute(plaintext_bits, IP)
    
    # 4. Chia thành L0 và R0 (32 bit mỗi phần)
    L = initial_permutation[:32]
    R = initial_permutation[32:]
    
    # 5. 16 vòng Feistel
    for i in range(16):
        L_next = R
        # R_next = L XOR F(R, K_i)
        feistel_output = des_feistel_function(R, subkeys[i])
        R_next = xor_bits(L, feistel_output)
        
        L = L_next
        R = R_next
    
    # 6. Hoán đổi L và R sau 16 vòng (pre-output swap)
    combined = R + L # R16L16
    
    # 7. Hoán vị cuối cùng (FP)
    ciphertext_bits = permute(combined, FP)
    
    # 8. Chuyển kết quả bit thành byte
    ciphertext_bytes = bits_to_bytes(ciphertext_bits)
    
    return ciphertext_bytes

# --- Hàm mô phỏng tấn công Brute Force trên DES ---

def simulate_des_brute_force_attack(plaintext_str, actual_key_str, max_attempts=1000000):
    """
    Mô phỏng tấn công Brute Force trên DES (khóa 56 bit hiệu dụng).
    (Chỉ mang tính minh họa khái niệm, không thực tế cho toàn bộ không gian khóa)
    
    Args:
        plaintext_str (str): Văn bản gốc (8 ký tự).
        actual_key_str (str): Khóa bí mật thực tế (8 ký tự).
        max_attempts (int): Số lần thử tối đa cho mô phỏng.
    """
    print("\n--- Bắt đầu mô phỏng tấn công Brute Force trên DES ---")
    print(f"Plaintext: '{plaintext_str}'")
    print(f"Khóa bí mật: '{actual_key_str}'")

    if len(plaintext_str) != 8 or len(actual_key_str) != 8:
        print("Lỗi: Plaintext và Key phải có độ dài 8 byte (64 bit).")
        print("Lưu ý: DES sử dụng khóa 64 bit, nhưng chỉ 56 bit là hiệu dụng.")
        return

    plaintext_bytes = string_to_bytes(plaintext_str)
    actual_key_bytes = string_to_bytes(actual_key_str)

    # 1. Mã hóa plaintext với khóa bí mật để có ciphertext mục tiêu
    print("\nĐang mã hóa plaintext với khóa bí mật để tạo ciphertext mục tiêu...")
    target_ciphertext_block = des_encrypt_block(plaintext_bytes, actual_key_bytes)
    print(f"Ciphertext mục tiêu (hex): {bytes_to_hex_str(target_ciphertext_block)}")

    start_time = time.time()
    found_key = None
    attempts = 0

    print(f"\nBắt đầu thử các khóa ngẫu nhiên (tối đa {max_attempts} lần)...")
    for i in range(max_attempts):
        attempts += 1
        
        # 2. Tạo một khóa thử ngẫu nhiên (8 byte)
        # Để minh họa, chúng ta sẽ tạo khóa ngẫu nhiên.
        # Trong thực tế, brute force sẽ thử tất cả các kết hợp tuần tự.
        # Lưu ý: DES chỉ sử dụng 56 bit của khóa, các bit chẵn lẻ (bit 8, 16, 24, ...) bị bỏ qua.
        # Tuy nhiên, trong brute force, chúng ta vẫn thường tạo khóa 64 bit và để thuật toán DES xử lý.
        trial_key_bytes = [random.randint(0, 255) for _ in range(8)]
        
        # Để tìm thấy khóa nhanh chóng trong mô phỏng nhỏ,
        # bạn có thể "gian lận" bằng cách tiêm khóa đúng vào một lúc nào đó.
        # Ví dụ: if attempts == 500000: trial_key_bytes = actual_key_bytes
        
        # 3. Mã hóa plaintext với khóa thử
        trial_ciphertext_block = des_encrypt_block(plaintext_bytes, trial_key_bytes)
        
        # 4. So sánh ciphertext thử với ciphertext mục tiêu
        if trial_ciphertext_block == target_ciphertext_block:
            found_key = bytes_to_hex_str(trial_key_bytes)
            break
        
        if (i + 1) % (max_attempts // 10 if max_attempts >= 10 else 1) == 0:
            print(f"  Đã thử {i + 1} khóa...")

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Kết thúc mô phỏng Brute Force ---")
    if found_key:
        print(f"!!! THÀNH CÔNG !!! Đã tìm thấy khóa sau {attempts} lần thử.")
        print(f"Khóa tìm thấy (hex): {found_key}")
        print(f"Khóa bí mật (hex): {bytes_to_hex_str(actual_key_bytes)}")
    else:
        print(f"Không tìm thấy khóa sau {max_attempts} lần thử.")
        print("Lưu ý: Với DES (56 bit), số lượng khóa vẫn rất lớn để brute force hoàn toàn trong mô phỏng.")
    print(f"Thời gian mô phỏng: {duration:.4f} giây.")

# --- Hàm chính để chạy mô phỏng ---
if __name__ == "__main__":
    plaintext_des = "8bytes!!" # Phải là 8 ký tự (64 bit)
    key_des = "des_key!"   # Phải là 8 ký tự (64 bit, 56 bit hiệu dụng)
    
    # Chạy mô phỏng Brute Force với số lần thử nhỏ để minh họa
    # Để thực sự tìm thấy khóa, max_attempts cần rất lớn.
    # Ví dụ: Để tìm thấy khóa trong mô phỏng, bạn có thể giảm max_attempts
    # và "gian lận" bằng cách gán trial_key_bytes = actual_key_bytes tại một lần thử cụ thể.
    simulate_des_brute_force_attack(plaintext_des, key_des, max_attempts=1000000)

import random
import time
from tabulate import tabulate # Để in bảng đẹp hơn

# Bảng S-box cho SubBytes (tra cứu thay thế byte)
SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

# Hằng số Rcon cho mở rộng khóa
RCON = [
    [0x01, 0x00, 0x00, 0x00], [0x02, 0x00, 0x00, 0x00], [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00], [0x10, 0x00, 0x00, 0x00], [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00], [0x80, 0x00, 0x00, 0x00], [0x1B, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]
]

MIX_COLUMNS_MATRIX = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

# --- Các hàm AES cơ bản cần thiết cho mã hóa một khối ---

def string_to_bytes(s):
    """Chuyển chuỗi thành danh sách các giá trị byte (decimal)."""
    return list(s.encode('utf-8'))

def bytes_to_hex_str(byte_list):
    """Chuyển danh sách byte thành chuỗi hex."""
    return [format(b, '02x') for b in byte_list]

def rot_word(word):
    """Xoay trái 1 byte trong từ 4 byte."""
    return [word[1], word[2], word[3], word[0]]

def sub_word(word):
    """Áp dụng S-box cho từng byte trong từ."""
    return [SBOX[byte] for byte in word]

def xor_words(word1, word2):
    """XOR hai từ (4 byte)."""
    return [a ^ b for a, b in zip(word1, word2)]

def key_expansion(key_str):
    """
    Mở rộng khóa 16 byte (AES-128) thành 11 khóa vòng (176 byte).
    Lưu ý: Hàm này được cố định cho AES-128.
    """
    key_bytes = string_to_bytes(key_str)
    w = [[] for _ in range(44)] # 44 words for AES-128 (11 round keys * 4 words/key)
    
    # Khởi tạo 4 từ đầu tiên từ khóa gốc
    for i in range(4):
        w[i] = key_bytes[4*i:4*i+4]
    
    # Tạo 40 từ tiếp theo
    for i in range(4, 44):
        temp = list(w[i-1]) # Tạo một bản sao để tránh sửa đổi w[i-1] trực tiếp
        
        if i % 4 == 0:
            temp = rot_word(temp)
            temp = sub_word(temp)
            temp = xor_words(temp, RCON[i//4 - 1])
        
        w[i] = xor_words(w[i-4], temp)
    
    # Tạo các khóa vòng từ các từ
    round_keys = []
    for i in range(0, 44, 4):
        round_key = w[i] + w[i+1] + w[i+2] + w[i+3]
        round_keys.append(round_key)
    
    return round_keys

def sub_bytes(state):
    """Thay thế byte bằng S-box."""
    return [[SBOX[state[i][j]] for j in range(4)] for i in range(4)]

def shift_rows(state):
    """Dịch trái các hàng."""
    result = [
        [state[0][0], state[0][1], state[0][2], state[0][3]],
        [state[1][1], state[1][2], state[1][3], state[1][0]],
        [state[2][2], state[2][3], state[2][0], state[2][1]],
        [state[3][3], state[3][0], state[3][1], state[3][2]]
    ]
    return result

def gf_mult(a, b):
    """Nhân trong GF(2^8) với đa thức bất khả quy x^8 + x^4 + x^3 + x + 1 (0x11B)."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit = a & 0x80 
        a <<= 1
        if hi_bit:
            a ^= 0x1B
        a &= 0xFF
        b >>= 1
    return p

def mix_columns(state_rowwise):
    """Thực hiện phép biến đổi MixColumns trên toàn bộ ma trận trạng thái AES."""
    new_state_rowwise = [[0] * 4 for _ in range(4)]
    for c in range(4):
        for r in range(4):
            new_state_rowwise[r][c] = (
                gf_mult(MIX_COLUMNS_MATRIX[r][0], state_rowwise[0][c]) ^
                gf_mult(MIX_COLUMNS_MATRIX[r][1], state_rowwise[1][c]) ^
                gf_mult(MIX_COLUMNS_MATRIX[r][2], state_rowwise[2][c]) ^
                gf_mult(MIX_COLUMNS_MATRIX[r][3], state_rowwise[3][c])
            )
    return new_state_rowwise

def add_round_key(state, round_key_bytes):
    """XOR ma trận trạng thái với khóa vòng."""
    # Chuyển round_key_bytes thành ma trận 4x4 theo cột để khớp với cấu trúc state
    round_key_matrix = [[round_key_bytes[j * 4 + i] for j in range(4)] for i in range(4)]
    result = [[state[i][j] ^ round_key_matrix[i][j] for j in range(4)] for i in range(4)]
    return result

def aes_encrypt_block(plaintext_block_bytes, round_keys):
    """
    Mã hóa một khối plaintext 16 byte bằng AES-128.
    Args:
        plaintext_block_bytes (list of int): Danh sách 16 byte của khối plaintext.
        round_keys (list of list of int): Danh sách các khóa vòng đã mở rộng.
    Returns:
        list of int: Danh sách 16 byte của khối ciphertext.
    """
    if len(plaintext_block_bytes) != 16:
        raise ValueError("Plaintext block must be 16 bytes.")

    # Chuyển khối thành ma trận trạng thái 4x4 (column-major)
    state = [[plaintext_block_bytes[j * 4 + i] for j in range(4)] for i in range(4)]
    
    # Vòng 0: Chỉ AddRoundKey
    state = add_round_key(state, round_keys[0])
    
    # 9 vòng chính
    for round_num in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[round_num])
    
    # Vòng cuối (10): Không có MixColumns
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[10])
    
    # Chuyển ma trận trạng thái thành khối ciphertext (column-major)
    # Lưu ý: Cần đảm bảo thứ tự byte đầu ra đúng với tiêu chuẩn AES (column-major)
    cipher_block = [state[j][i] for i in range(4) for j in range(4)] 
    
    return cipher_block

# --- Hàm mô phỏng tấn công Brute Force ---
def simulate_brute_force_attack(plaintext_str, actual_key_str, max_attempts=100000):
    """
    Mô phỏng tấn công Brute Force trên AES-128.
    (Chỉ mang tính minh họa khái niệm, không thực tế cho AES-128)
    
    Args:
        plaintext_str (str): Văn bản gốc (16 ký tự).
        actual_key_str (str): Khóa bí mật thực tế (16 ký tự).
        max_attempts (int): Số lần thử tối đa cho mô phỏng.
    """
    print("\n--- Bắt đầu mô phỏng tấn công Brute Force trên AES-128 ---")
    print(f"Plaintext: '{plaintext_str}'")
    print(f"Khóa bí mật: '{actual_key_str}'")

    if len(plaintext_str) != 16 or len(actual_key_str) != 16:
        print("Lỗi: Plaintext và Key phải có độ dài 16 byte (16 ký tự).")
        return

    plaintext_bytes = string_to_bytes(plaintext_str)
    actual_key_bytes = string_to_bytes(actual_key_str)


    print("\nĐang mã hóa plaintext với khóa bí mật để tạo ciphertext mục tiêu...")
    actual_round_keys = key_expansion(actual_key_str)
    target_ciphertext_block = aes_encrypt_block(plaintext_bytes, actual_round_keys)
    print(f"Ciphertext mục tiêu (hex): {bytes_to_hex_str(target_ciphertext_block)}")

    start_time = time.time()
    found_key = None
    attempts = 0

    print(f"\nBắt đầu thử các khóa ngẫu nhiên (tối đa {max_attempts} lần)...")
    for i in range(max_attempts):
        attempts += 1
        

        trial_key_bytes = [random.randint(0, 255) for _ in range(16)]
        

        
        trial_key_str = "".join(chr(b % 256) for b in trial_key_bytes) 
        
        # 3. Mở rộng khóa thử
        trial_round_keys = key_expansion(trial_key_str)
        
        # 4. Mã hóa plaintext với khóa thử
        trial_ciphertext_block = aes_encrypt_block(plaintext_bytes, trial_round_keys)
        
        # 5. So sánh ciphertext thử với ciphertext mục tiêu
        if trial_ciphertext_block == target_ciphertext_block:
            found_key = trial_key_str
            break
        
        if (i + 1) % (max_attempts // 10 if max_attempts >= 10 else 1) == 0:
            print(f"  Đã thử {i + 1} khóa...")

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Kết thúc mô phỏng Brute Force ---")
    if found_key:
        print(f"!!! THÀNH CÔNG !!! Đã tìm thấy khóa sau {attempts} lần thử.")
        print(f"Khóa tìm thấy: '{found_key}' (Hex: {bytes_to_hex_str(string_to_bytes(found_key))})")
        print(f"Khóa bí mật: '{actual_key_str}' (Hex: {bytes_to_hex_str(string_to_bytes(actual_key_str))})")
    else:
        print(f"Không tìm thấy khóa sau {max_attempts} lần thử.")
        print("Lưu ý: Với AES-128, số lượng khóa là quá lớn để brute force trong thực tế.")
    print(f"Thời gian mô phỏng: {duration:.4f} giây.")

# --- Hàm chính để chạy mô phỏng ---
if __name__ == "__main__":
    plaintext_brute_force = "AES Brute Force!"
    key_brute_force = "SecretKeyForTest"
    
    simulate_brute_force_attack(plaintext_brute_force, key_brute_force, max_attempts=100000)



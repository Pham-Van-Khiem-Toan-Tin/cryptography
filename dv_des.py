import random
import time
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

# --- Các hàm tiện ích cho thao tác bit và chuyển đổi ---

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
            if (i + j) < len(bit_list):
                byte = (byte << 1) | bit_list[i + j]
            else:
                byte = (byte << 1) | 0
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

def hex_to_bytes(hex_str_list):
    """Chuyển danh sách chuỗi hex thành danh sách byte (decimal)."""
    return [int(h, 16) for h in hex_str_list]

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

def des_feistel_function_detailed(right_half_bits, subkey_bits):
    """
    Thực hiện hàm Feistel của DES và trả về các kết quả trung gian.
    Args:
        right_half_bits (list of int): Nửa phải của khối (32 bit).
        subkey_bits (list of int): Khóa con (48 bit).
    Returns:
        tuple: (pbox_result, expanded_R, xor_result, sbox_output_values)
    """
    # 1. Mở rộng R (32 bit) thành 48 bit bằng E-box
    expanded_R = permute(right_half_bits, E_BOX)
    
    # 2. XOR với khóa con (48 bit)
    xor_result = xor_bits(expanded_R, subkey_bits)
    
    # 3. Chia 48 bit thành 8 khối 6 bit và áp dụng S-boxes
    sbox_output_bits = []
    sbox_output_values = [] # Lưu trữ giá trị số nguyên (0-15) của đầu ra S-box
    for i in range(8): # 8 S-boxes
        six_bits = xor_result[i*6 : (i+1)*6]
        
        # Lấy hàng (row) từ bit đầu tiên và bit cuối cùng
        row = (six_bits[0] << 1) | six_bits[5]
        
        # Lấy cột (column) từ 4 bit giữa
        col = (six_bits[1] << 3) | (six_bits[2] << 2) | (six_bits[3] << 1) | six_bits[4]
        
        # Tra cứu S-box và chuyển kết quả 4 bit thành danh sách bit
        sbox_value = S_BOXES[i][row][col]
        sbox_output = [(sbox_value >> j) & 1 for j in range(3, -1, -1)] # 4 bits, MSB first
        sbox_output_bits.extend(sbox_output)
        sbox_output_values.append(sbox_value) # Store the integer value of the S-box output
        
    # 4. Áp dụng P-box lên kết quả 32 bit từ S-boxes
    pbox_result = permute(sbox_output_bits, P_BOX)
    
    return pbox_result, expanded_R, xor_result, sbox_output_values

def des_feistel_function(right_half_bits, subkey_bits):
    """
    Thực hiện hàm Feistel của DES (phiên bản đơn giản chỉ trả về kết quả cuối cùng).
    """
    pbox_result, _, _, _ = des_feistel_function_detailed(right_half_bits, subkey_bits)
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

    subkeys = des_key_schedule(key_bytes)
    plaintext_bits = bytes_to_bits(plaintext_block_bytes)
    initial_permutation = permute(plaintext_bits, IP)
    
    L = initial_permutation[:32]
    R = initial_permutation[32:]
    
    # 16 vòng Feistel
    for i in range(16):
        L_next = R[:] # Copy R
        feistel_output = des_feistel_function(R, subkeys[i])
        R_next = xor_bits(L, feistel_output)
        
        L = L_next
        R = R_next
    
    combined = R + L # Hoán đổi L và R sau 16 vòng (pre-output swap)
    ciphertext_bits = permute(combined, FP)
    ciphertext_bytes = bits_to_bytes(ciphertext_bits)
    
    return ciphertext_bytes

# --- Hàm băm Davies-Meyer với DES ---

def pkcs5_pad(data_bytes, block_size):
    """
    Áp dụng đệm PKCS#5 cho danh sách byte.
    Args:
        data_bytes (list of int): Dữ liệu cần đệm.
        block_size (int): Kích thước khối (byte).
    Returns:
        list of int: Dữ liệu đã được đệm.
    """
    padding_len = block_size - (len(data_bytes) % block_size)
    if padding_len == 0: # Nếu đã là bội số của block_size, thêm một khối đệm đầy đủ
        padding_len = block_size
    
    padded_data = list(data_bytes) # Tạo bản sao
    padded_data.extend([padding_len] * padding_len)
    return padded_data

def des_davies_meyer_hash(message_str, iv_str):
    """
    Thực hiện hàm băm Davies-Meyer sử dụng DES.
    H(i) = E_K(M_i) XOR M_i
    Trong đó:
        E là hàm mã hóa DES.
        K là khối trước đó (H_{i-1}).
        M_i là khối tin nhắn hiện tại.
    Do DES có kích thước khóa 56 bit và kích thước khối 64 bit,
    chúng ta cần điều chỉnh để M_i là khóa và H_{i-1} là plaintext.
    
    Args:
        message_str (str): Tin nhắn đầu vào.
        iv_str (str): Giá trị khởi tạo (IV) 8 byte (64 bit).
    Returns:
        list of int: Giá trị băm cuối cùng (8 byte).
    """
    if len(iv_str) != 8:
        raise ValueError("IV phải có độ dài 8 byte (64 bit).")
    
    message_bytes = string_to_bytes(message_str)
    iv_bytes = string_to_bytes(iv_str)
    
    # Đệm tin nhắn để có độ dài là bội số của 8 byte (kích thước khối DES)
    padded_message_bytes = pkcs5_pad(message_bytes, 8)
    
    current_hash_value = iv_bytes
    
    # print(f"\n--- Bắt đầu hàm băm Davies-Meyer với DES ---")
    # print(f"Tin nhắn gốc: '{message_str}' (Hex: {bytes_to_hex_str(message_bytes)})")
    # print(f"Tin nhắn sau đệm: (Hex: {bytes_to_hex_str(padded_message_bytes)})")
    # print(f"IV ban đầu: (Hex: {bytes_to_hex_str(iv_bytes)})")

    # Chia tin nhắn thành các khối 8 byte
    blocks = [padded_message_bytes[i:i+8] for i in range(0, len(padded_message_bytes), 8)]
    
    for i, block in enumerate(blocks):
        # print(f"\n--- Xử lý khối {i+1}/{len(blocks)} ---")
        # print(f"Khối tin nhắn M_{i+1} (Hex): {bytes_to_hex_str(block)}")
        # print(f"Giá trị băm trước đó H_{i} (Hex): {bytes_to_hex_str(current_hash_value)}")
        
        # H_new = E_{current_hash_value}(block) XOR block
        encrypted_output_dm = des_encrypt_block(block, current_hash_value)
        
        # XOR với khối tin nhắn hiện tại (block)
        next_hash_value = [e ^ b for e, b in zip(encrypted_output_dm, block)]
        
        # print(f"Giá trị băm mới H_{i+1} (Hex): {bytes_to_hex_str(next_hash_value)}")
        current_hash_value = next_hash_value
        
    # print(f"\n--- Kết thúc hàm băm Davies-Meyer với DES ---")
    # print(f"Giá trị băm cuối cùng (Hex): {bytes_to_hex_str(current_hash_value)}")
    return current_hash_value

# --- Hàm mô phỏng hiệu ứng tuyết lở (Avalanche Effect) cho Davies-Meyer ---

def hamming_distance(bits1, bits2):
    """Tính khoảng cách Hamming giữa hai danh sách bit."""
    return sum(b1 ^ b2 for b1, b2 in zip(bits1, bits2))

def simulate_davies_meyer_avalanche_effect(num_tests=1000, message_length=16, iv_str="init_iv!"):
    """
    Mô phỏng hiệu ứng tuyết lở cho hàm băm Davies-Meyer.
    Tạo các cặp tin nhắn khác nhau 1 bit và tính khoảng cách Hamming của giá trị băm.
    
    Args:
        num_tests (int): Số lượng cặp tin nhắn để kiểm tra.
        message_length (int): Độ dài của tin nhắn ngẫu nhiên (byte).
        iv_str (str): IV cho hàm băm (8 byte).
    """
    print("\n--- Bắt đầu mô phỏng hiệu ứng tuyết lở cho Davies-Meyer DES ---")
    print(f"Số lượng kiểm tra: {num_tests}")
    print(f"Độ dài tin nhắn cơ sở: {message_length} byte")
    print(f"IV: '{iv_str}'")

    if len(iv_str) != 8:
        print("Lỗi: IV phải có độ dài 8 byte (64 bit).")
        return

    all_hamming_distances = []
    output_hash_size_bits = 64 # DES output is 64 bits

    for i in range(num_tests):
        # 1. Tạo tin nhắn cơ sở ngẫu nhiên
        base_message_bytes = [random.randint(0, 255) for _ in range(message_length)]
        base_message_str = "".join(chr(b) for b in base_message_bytes)

        # 2. Tạo tin nhắn đã thay đổi 1 bit
        # Chọn một vị trí bit ngẫu nhiên để lật
        bit_pos_to_flip = random.randint(0, message_length * 8 - 1)
        
        modified_message_bytes = list(base_message_bytes) # Tạo bản sao
        
        byte_idx = bit_pos_to_flip // 8
        bit_in_byte_idx = bit_pos_to_flip % 8
        
        # Lật bit tại vị trí đã chọn
        modified_message_bytes[byte_idx] ^= (1 << (7 - bit_in_byte_idx)) # Lật bit (MSB first)
        modified_message_str = "".join(chr(b) for b in modified_message_bytes)

        # 3. Tính giá trị băm cho cả hai tin nhắn
        hash1_bytes = des_davies_meyer_hash(base_message_str, iv_str)
        hash2_bytes = des_davies_meyer_hash(modified_message_str, iv_str)

        # 4. Tính khoảng cách Hamming giữa hai giá trị băm
        hash1_bits = bytes_to_bits(hash1_bytes)
        hash2_bits = bytes_to_bits(hash2_bytes)
        
        dist = hamming_distance(hash1_bits, hash2_bits)
        all_hamming_distances.append(dist)
        
        if (i + 1) % (num_tests // 10 if num_tests >= 10 else 1) == 0:
            print(f"  Đã kiểm tra {i + 1} cặp...")

    # --- Trực quan hóa kết quả ---
    plt.figure(figsize=(10, 6))
    plt.hist(all_hamming_distances, bins=range(output_hash_size_bits + 1), edgecolor='black', alpha=0.7)
    plt.title('Phân phối khoảng cách Hamming (Hiệu ứng tuyết lở)')
    plt.xlabel(f'Khoảng cách Hamming (số bit khác biệt trên {output_hash_size_bits} bit)')
    plt.ylabel('Số lượng cặp tin nhắn')
    plt.xticks(range(0, output_hash_size_bits + 1, 4)) # Nhãn x-axis mỗi 4 bit
    plt.axvline(x=output_hash_size_bits / 2, color='red', linestyle='--', label=f'Trung bình lý thuyết ({output_hash_size_bits / 2:.0f} bit)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    print(f"\n--- Kết thúc mô phỏng hiệu ứng tuyết lở ---")
    print(f"Khoảng cách Hamming trung bình: {np.mean(all_hamming_distances):.2f} bit")
    print(f"Độ lệch chuẩn khoảng cách Hamming: {np.std(all_hamming_distances):.2f}")

# --- Hàm chính để chạy mô phỏng ---
if __name__ == "__main__":
    # Ví dụ sử dụng hàm băm Davies-Meyer với DES
    test_message = "Hello World!"
    initial_vector = "init_iv!" # IV 8 byte (64 bit)
    
    # Băm tin nhắn
    final_hash = des_davies_meyer_hash(test_message, initial_vector)
    print(f"\nTin nhắn: '{test_message}'")
    print(f"IV: '{initial_vector}'")
    print(f"Hash cuối cùng: {bytes_to_hex_str(final_hash)}")

    # Thử với tin nhắn khác
    test_message_2 = "Hello World?"
    final_hash_2 = des_davies_meyer_hash(test_message_2, initial_vector)
    print(f"\nTin nhắn: '{test_message_2}'")
    print(f"IV: '{initial_vector}'")
    print(f"Hash cuối cùng: {bytes_to_hex_str(final_hash_2)}")

    # Thử với tin nhắn dài hơn
    test_message_long = "This is a longer message that needs multiple blocks to be processed by the Davies-Meyer hash function using DES."
    final_hash_long = des_davies_meyer_hash(test_message_long, initial_vector)
    print(f"\nTin nhắn: '{test_message_long}'")
    print(f"IV: '{initial_vector}'") # Đã sửa từ initial_iv thành initial_vector
    print(f"Hash cuối cùng: {bytes_to_hex_str(final_hash_long)}")

    # --- Chạy mô phỏng hiệu ứng tuyết lở ---
    # Số lượng kiểm tra càng lớn, kết quả càng chính xác.
    # 10000 tests sẽ cho biểu đồ phân phối đẹp hơn.
    simulate_davies_meyer_avalanche_effect(num_tests=10000, message_length=16, iv_str="init_iv!")

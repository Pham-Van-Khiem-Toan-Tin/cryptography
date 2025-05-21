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
            # Thêm kiểm tra an toàn để tránh IndexError nếu bit_list không phải là bội số của 8
            if (i + j) < len(bit_list):
                byte = (byte << 1) | bit_list[i + j]
            else:
                # Đệm bằng 0 nếu không đủ 8 bit
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

# --- Hàm mô phỏng tấn công Phá mã tuyến tính (Linear Cryptanalysis - LC) trên DES ---

def calculate_sbox_bias(sbox_index, input_mask_bits, output_mask_bits):
    """
    Tính toán độ lệch (bias) của một xấp xỉ tuyến tính cho một S-box cụ thể.
    Bias = (Số lần xấp xỉ đúng / Tổng số đầu vào) - 0.5
    
    Args:
        sbox_index (int): Chỉ số của S-box (0-7).
        input_mask_bits (list of int): Mask 6 bit cho đầu vào S-box (1 nếu bit được chọn, 0 nếu không).
        output_mask_bits (list of int): Mask 4 bit cho đầu ra S-box (1 nếu bit được chọn, 0 nếu không).
    
    Returns:
        float: Độ lệch của xấp xỉ tuyến tính.
    """
    sbox = S_BOXES[sbox_index]
    num_inputs = 64 # 2^6 = 64 khả năng đầu vào 6 bit
    
    count_correct = 0
    
    for i in range(num_inputs):
        # Chuyển số nguyên i thành danh sách 6 bit
        input_bits = [(i >> j) & 1 for j in range(5, -1, -1)] # MSB first
        
        # Áp dụng input_mask
        input_xor_sum = 0
        for k in range(6):
            input_xor_sum ^= (input_bits[k] & input_mask_bits[k])
            
        # Lấy đầu ra S-box
        row = (input_bits[0] << 1) | input_bits[5]
        col = (input_bits[1] << 3) | (input_bits[2] << 2) | (input_bits[3] << 1) | input_bits[4]
        sbox_output_value = sbox[row][col]
        
        # Chuyển đầu ra S-box thành danh sách 4 bit
        output_bits = [(sbox_output_value >> j) & 1 for j in range(3, -1, -1)] # MSB first
        
        # Áp dụng output_mask
        output_xor_sum = 0
        for k in range(4):
            output_xor_sum ^= (output_bits[k] & output_mask_bits[k])
            
        # Kiểm tra xấp xỉ tuyến tính: Input_XOR_Sum XOR Output_XOR_Sum == 0
        if (input_xor_sum ^ output_xor_sum) == 0:
            count_correct += 1
            
    bias = (count_correct / num_inputs) - 0.5
    return bias

def simulate_des_linear_cryptanalysis(key_str, num_plaintext_pairs=100000):
    """
    Mô phỏng khái niệm tấn công Phá mã tuyến tính trên DES.
    Tính toán độ lệch cho một xấp xỉ S-box và minh họa việc quan sát độ lệch này
    trên một số lượng lớn dữ liệu.
    
    Args:
        key_str (str): Khóa bí mật (8 ký tự).
        num_plaintext_pairs (int): Số lượng cặp plaintext để quan sát.
    """
    print("\n--- Bắt đầu mô phỏng tấn công Phá mã tuyến tính (Linear Cryptanalysis) trên DES ---")
    print(f"Khóa bí mật: '{key_str}'")

    if len(key_str) != 8:
        print("Lỗi: Key phải có độ dài 8 byte (64 bit).")
        return

    key_bytes = string_to_bytes(key_str)

    # --- Bước 1: Tính toán độ lệch lý thuyết cho một xấp xỉ S-box ---
    # Chọn một xấp xỉ tuyến tính nổi tiếng cho S1 của DES (từ các nghiên cứu)
    # X_2 XOR X_3 XOR X_4 XOR Y_1 = 0
    # Input bits: 0-5 (bit 0 và 5 là row, bit 1-4 là col)
    # Output bits: 0-3
    
    # X_2 là input bit thứ 1 (index 1)
    # X_3 là input bit thứ 2 (index 2)
    # X_4 là input bit thứ 3 (index 3)
    input_mask_s1 = [0, 1, 1, 1, 0, 0] # Bit 1, 2, 3 (tương ứng với input bit 2, 3, 4)
    # Y_1 là output bit thứ 0 (index 0)
    output_mask_s1 = [1, 0, 0, 0] # Bit 0 (tương ứng với output bit 1)
    
    s1_bias = calculate_sbox_bias(0, input_mask_s1, output_mask_s1)
    print(f"\nĐộ lệch lý thuyết cho S1 (input_mask={input_mask_s1}, output_mask={output_mask_s1}): {s1_bias:.4f}")

    # --- Bước 2: Mô phỏng quan sát độ lệch trên dữ liệu thực tế ---
    # Chúng ta sẽ sử dụng một xấp xỉ tuyến tính đơn giản cho toàn bộ DES (ví dụ 1 vòng)
    # để minh họa việc quan sát độ lệch.
    # Một xấp xỉ thực tế sẽ liên quan đến nhiều S-box và nhiều vòng.
    
    # Giả sử chúng ta có một xấp xỉ tuyến tính cho 1 vòng DES:
    # P_i XOR P_j XOR ... XOR C_k XOR C_l XOR ... = 0
    # Để đơn giản, chúng ta sẽ chọn một xấp xỉ liên quan đến 1 S-box của vòng cuối cùng
    # (hoặc một S-box bất kỳ trong vòng giữa).

    # Để minh họa, chúng ta sẽ theo dõi một xấp xỉ đơn giản:
    # Bit 0 của Plaintext (sau IP) XOR Bit 0 của Ciphertext (trước FP)
    # Đây không phải là một đặc tính tuyến tính thực tế cho LC, chỉ là ví dụ để vẽ biểu đồ.
    
    observed_biases = []
    num_data_points = []
    
    print(f"\nBắt đầu thu thập dữ liệu và quan sát độ lệch (tối đa {num_plaintext_pairs} cặp)...")
    
    true_count = 0
    for i in range(1, num_plaintext_pairs + 1):
        # Tạo plaintext ngẫu nhiên (8 bytes)
        plaintext_bytes = [random.randint(0, 255) for _ in range(8)]
        
        # Mã hóa plaintext
        ciphertext_bytes = des_encrypt_block(plaintext_bytes, key_bytes)

        # Chuyển plaintext và ciphertext sang bit sau IP và trước FP
        # Đây là một xấp xỉ tuyến tính rất đơn giản (chỉ để minh họa)
        # Thực tế, LC sẽ sử dụng các bit đầu vào/đầu ra của S-box sau E-box và P-box
        
        # Lấy bit 0 của plaintext sau IP (P_0)
        p_bits_ip = permute(bytes_to_bits(plaintext_bytes), IP)
        p_bit_0 = p_bits_ip[0] # Bit đầu tiên của khối sau IP (bit 58 của plaintext gốc)

        # Lấy bit 0 của ciphertext trước FP (C'_0)
        # Để làm điều này, chúng ta cần chạy DES và lấy giá trị trước FP.
        # Hàm des_encrypt_block hiện tại không trả về intermediate_states.
        # Sẽ cần một phiên bản của des_encrypt_block để trả về L16, R16.
        # Để đơn giản hóa mô phỏng, chúng ta sẽ lấy bit 0 của ciphertext cuối cùng sau FP.
        # Đây là một sự đơn giản hóa lớn và không đại diện cho LC thực tế.
        c_bits_fp = bytes_to_bits(ciphertext_bytes)
        c_bit_0 = c_bits_fp[0] # Bit đầu tiên của ciphertext cuối cùng

        # Xấp xỉ tuyến tính ví dụ: P_bit_0 XOR C_bit_0 == 0
        if (p_bit_0 ^ c_bit_0) == 0:
            true_count += 1
            
        if i % (num_plaintext_pairs // 10 if num_plaintext_pairs >= 10 else 1) == 0 or i == num_plaintext_pairs:
            observed_bias = (true_count / i) - 0.5
            observed_biases.append(observed_bias)
            num_data_points.append(i)
            print(f"  Đã thu thập {i} cặp. Độ lệch quan sát: {observed_bias:.4f}")

    # --- Trực quan hóa độ lệch quan sát ---
    plt.figure(figsize=(12, 6))
    plt.plot(num_data_points, observed_biases, marker='o', linestyle='-', color='blue')
    plt.axhline(y=s1_bias, color='r', linestyle='--', label=f'Độ lệch lý thuyết S1 ({s1_bias:.4f})')
    plt.axhline(y=0, color='gray', linestyle=':', label='Độ lệch 0 (ngẫu nhiên)')
    plt.title('Độ lệch quan sát qua số lượng cặp Plaintext/Ciphertext')
    plt.xlabel('Số lượng cặp Plaintext/Ciphertext')
    plt.ylabel('Độ lệch quan sát')
    plt.xscale('log') # Sử dụng thang log cho trục x để hiển thị tốt hơn
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("\n--- Kết thúc mô phỏng Phá mã tuyến tính ---")

# --- Hàm chính để chạy mô phỏng ---
if __name__ == "__main__":
    key_lc = "linear!!" # Khóa 8 ký tự
    
    # Chạy mô phỏng Phá mã tuyến tính
    # Số lượng cặp plaintext càng lớn, độ lệch quan sát càng gần độ lệch lý thuyết.
    simulate_des_linear_cryptanalysis(key_lc, num_plaintext_pairs=500000)

import random
import time
from tabulate import tabulate # Để in bảng đẹp hơn
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
    # Đảm bảo bit_list có độ dài là bội số của 8.
    # Nếu không, phần còn lại sẽ được bỏ qua hoặc bạn có thể thêm đệm nếu cần cho mục đích khác.
    # Trong trường hợp này, lỗi xảy ra khi bit_list không đủ 8 bit.
    # Logic này chỉ nên được gọi với các danh sách bit có độ dài là bội số của 8.
    for i in range(0, len(bit_list), 8):
        byte = 0
        # Đảm bảo không truy cập ngoài phạm vi nếu bit_list không phải là bội số của 8
        # Mặc dù trong trường hợp này, lỗi được giải quyết bằng cách không gọi nó với 4 bit.
        for j in range(8):
            if (i + j) < len(bit_list): # Thêm kiểm tra an toàn, mặc dù không phải nguyên nhân chính của lỗi này
                byte = (byte << 1) | bit_list[i + j]
            else:
                # Nếu không đủ 8 bit, có thể đệm bằng 0 hoặc xử lý theo cách khác
                # Trong ngữ cảnh này, điều này không nên xảy ra nếu hàm được gọi đúng cách
                pass 
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

def des_encrypt_block(plaintext_block_bytes, key_bytes, return_intermediate_diffs=False):
    """
    Mã hóa một khối plaintext 8 byte (64 bit) bằng DES.
    Args:
        plaintext_block_bytes (list of int): Danh sách 8 byte của khối plaintext.
        key_bytes (list of int): Khóa 8 byte (64 bit, 56 bit hiệu dụng).
        return_intermediate_diffs (bool): Nếu True, trả về danh sách các trạng thái L/R
                                          sau mỗi vòng để phân tích khác biệt.
    Returns:
        list of int: Danh sách 8 byte của khối ciphertext.
        list of tuples: (L_bits, R_bits) sau mỗi vòng nếu return_intermediate_diffs=True.
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
    
    intermediate_states = []
    if return_intermediate_diffs:
        intermediate_states.append((L[:], R[:])) # Store initial L0, R0

    for i in range(16): # 16 vòng Feistel
        L_next = R[:] # Copy R
        
        feistel_output = des_feistel_function(R, subkeys[i])
        R_next = xor_bits(L, feistel_output)
        
        L = L_next
        R = R_next

        if return_intermediate_diffs:
            intermediate_states.append((L[:], R[:])) # Store L_i, R_i after each round
    
    combined = R + L # Hoán đổi L và R sau 16 vòng (pre-output swap)
    ciphertext_bits = permute(combined, FP)
    ciphertext_bytes = bits_to_bytes(ciphertext_bits)
    
    if return_intermediate_diffs:
        return ciphertext_bytes, intermediate_states
    return ciphertext_bytes

# --- Hàm mô phỏng tấn công Phá mã vi sai (Differential Cryptanalysis - DC) trên DES ---

def simulate_des_differential_cryptanalysis(base_plaintext_str, key_str, input_diff_bytes_hex, num_rounds_to_simulate=16):
    """
    Mô phỏng sự lan truyền khác biệt trong DES cho tấn công Phá mã vi sai.
    Trực quan hóa Hamming weight của sự khác biệt sau mỗi vòng.
    
    Args:
        base_plaintext_str (str): Văn bản gốc cơ sở (8 ký tự).
        key_str (str): Khóa (8 ký tự).
        input_diff_bytes_hex (list of str): Sự khác biệt đầu vào (8 byte hex string).
        num_rounds_to_simulate (int): Số vòng DES để mô phỏng (tối đa 16).
    """
    print("\n--- Bắt đầu mô phỏng tấn công Phá mã vi sai (Differential Cryptanalysis) trên DES ---")
    print(f"Văn bản gốc cơ sở: '{base_plaintext_str}'")
    print(f"Khóa: '{key_str}'")
    print(f"Sự khác biệt đầu vào (hex): {input_diff_bytes_hex}")

    if len(base_plaintext_str) != 8 or len(key_str) != 8 or len(input_diff_bytes_hex) != 8:
        print("Lỗi: Plaintext, Key và Input Difference phải có độ dài 8 byte.")
        return

    base_plaintext_bytes = string_to_bytes(base_plaintext_str)
    key_bytes = string_to_bytes(key_str)
    input_diff_bytes = hex_to_bytes(input_diff_bytes_hex)

    # Tạo plaintext thứ hai: P2 = P1 XOR input_difference
    plaintext2_bytes = [p1 ^ diff for p1, diff in zip(base_plaintext_bytes, input_diff_bytes)]

    # Lấy các khóa con
    subkeys = des_key_schedule(key_bytes)

    # Chuyển plaintext thành danh sách bit và hoán vị ban đầu
    p1_bits_initial_perm = permute(bytes_to_bits(base_plaintext_bytes), IP)
    p2_bits_initial_perm = permute(bytes_to_bits(plaintext2_bytes), IP)

    # Chia thành L và R cho cả hai plaintext
    L1 = p1_bits_initial_perm[:32]
    R1 = p1_bits_initial_perm[32:]
    L2 = p2_bits_initial_perm[:32]
    R2 = p2_bits_initial_perm[32:]

    # Lưu trữ Hamming weight của sự khác biệt ở R-half sau mỗi vòng
    diff_hamming_weights = []
    round_labels = []

    # Tính Hamming weight ban đầu của sự khác biệt đầu vào (sau IP)
    initial_diff_LR = xor_bits(p1_bits_initial_perm, p2_bits_initial_perm)
    diff_hamming_weights.append(sum(initial_diff_LR))
    round_labels.append("Initial Diff (IP)")

    print(f"\nSự khác biệt đầu vào (sau IP): {sum(initial_diff_LR)} bit")

    # 16 vòng Feistel
    for i in range(num_rounds_to_simulate):
        # Thực hiện một vòng cho plaintext 1
        L1_next = R1[:]
        feistel_output1 = des_feistel_function(R1, subkeys[i])
        R1_next = xor_bits(L1, feistel_output1)
        
        # Thực hiện một vòng cho plaintext 2
        L2_next = R2[:]
        feistel_output2 = des_feistel_function(R2, subkeys[i])
        R2_next = xor_bits(L2, feistel_output2)

        # Cập nhật L và R
        L1, R1 = L1_next, R1_next
        L2, R2 = L2_next, R2_next

        # Tính sự khác biệt của nửa phải (R) sau vòng này
        diff_R = xor_bits(R1, R2)
        diff_hamming_weights.append(sum(diff_R))
        round_labels.append(f"Round {i+1} Output Diff (R)")
        print(f"Sự khác biệt sau Vòng {i+1} (nửa phải): {sum(diff_R)} bit")

    # --- Trực quan hóa ---
    plt.figure(figsize=(12, 6))
    plt.plot(round_labels, diff_hamming_weights, marker='o', linestyle='-', color='red')
    plt.title('Sự lan truyền khác biệt (Hamming Weight) qua các vòng DES')
    plt.xlabel('Vòng mã hóa')
    plt.ylabel('Hamming Weight của sự khác biệt')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    print("\n--- Kết thúc mô phỏng Phá mã vi sai ---")


# --- Hàm chính để chạy mô phỏng ---
if __name__ == "__main__":
    # --- Mô phỏng Phá mã vi sai (Differential Cryptanalysis) ---
    # Một ví dụ về cặp khác biệt đầu vào có xác suất cao trong DES
    # Ví dụ: input_diff = 0x4008000000000000 (tức là chỉ bit thứ 24 khác biệt)
    # Trong DES, sự khác biệt thường được biểu diễn dưới dạng các bit.
    # Để đơn giản, chúng ta sẽ chọn một sự khác biệt đơn giản.
    # Ví dụ: chỉ bit đầu tiên của byte đầu tiên khác biệt (0x8000000000000000)
    # Tức là plaintext2 = plaintext1 XOR 0x80
    
    # Input difference (8 bytes)
    # Ví dụ: chỉ byte đầu tiên khác biệt 0x01
    input_diff_example_bytes_hex = ['01', '00', '00', '00', '00', '00', '00', '00'] 
    
    plaintext_des_dc = "DC_test!" # Plaintext cơ sở (8 ký tự)
    key_des_dc = "dc_key!!"   # Khóa (8 ký tự)

    simulate_des_differential_cryptanalysis(plaintext_des_dc, key_des_dc, input_diff_example_bytes_hex, num_rounds_to_simulate=16)

    # Để thấy các đặc điểm khác biệt "tốt" hơn, bạn cần chọn các khác biệt đầu vào
    # đã được nghiên cứu trong Differential Cryptanalysis của DES.
    # Ví dụ: một cặp khác biệt đầu vào nổi tiếng là 0x4008000000000000 (bit 24 khác biệt)
    # input_diff_complex_hex = ['40', '08', '00', '00', '00', '00', '00', '00']
    # simulate_des_differential_cryptanalysis(plaintext_des_dc, key_des_dc, input_diff_complex_hex, num_rounds_to_simulate=16)

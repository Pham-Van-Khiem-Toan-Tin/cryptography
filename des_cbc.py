PC1 = [
    57, 49, 41, 33, 25, 17, 9, 1,
    58, 50, 42, 34, 26, 18, 10, 2,
    59, 51, 43, 35, 27, 19, 11, 3,
    60, 52, 44, 36, 63, 55, 47, 39,
    31, 23, 15, 7, 62, 54, 46, 38,
    30, 22, 14, 6, 61, 53, 45, 37,
    29, 21, 13, 5, 28, 20, 12, 4
]
def hex_to_binary(hex_string):
    try:
        # Chuyển chuỗi hex thành số nguyên
        decimal_value = int(hex_string, 16)
        # Chuyển số nguyên thành chuỗi nhị phân và loại bỏ tiền tố "0b"
        binary_string = bin(decimal_value)[2:]
        return binary_string
    except ValueError:
    # Xử lý trường hợp đầu vào không phải là chuỗi hex hợp lệ
        return None
def key_to_binary(s):
    if len(s) != 8:
        raise ValueError("Chuỗi phải có đúng 8 ký tự để tạo khóa 64 bit!")
    return ''.join(format(ord(c), '08b') for c in s)
def pc1_permutation(binary_key):
    key_56bit = ""
    for index in PC1:
        key_56bit += binary_key[index - 1]
    return key_56bit
def split_key_56bit(key_56bit):
    left_half = key_56bit[:28]
    right_half = key_56bit[28:]
    return left_half, right_half
shift_schedule = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
# Dịch trái chuỗi bits với số lượng bit được chỉ định
def left_shift(bits, num_shifts):
    return bits[num_shifts:] + bits[:num_shifts]
# Hàm tạo khóa con từ khóa 56 bit
def generate_subkeys(key_56bit):
    C, D = split_key_56bit(key_56bit)
    print("Nửa C (28 bit):", C)
    print("Nửa D (28 bit):", D)
    C_list = [C]
    D_list = [D]
    for i in range(16):
        num_shifts = shift_schedule[i]
        C = left_shift(C, num_shifts)
        D = left_shift(D, num_shifts)
        C_list.append(C)
        D_list.append(D)
    return C_list, D_list
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]
def pc2_permutation(C, D):
    combined_key = C + D
    if len(combined_key) != 56:
        raise ValueError("Khóa kết hợp phải có đúng 56 bit!")
    sub_key_48bit = ""
    for index in PC2:
        sub_key_48bit += combined_key[index - 1]
    return sub_key_48bit
def string_to_binary(s):
    return ''.join(format(ord(c), '08b') for c in s)
def pkcs5_padding(plaintext):
    """Áp dụng đệm PKCS#5 cho plaintext"""
    block_size = 8  # 8 byte = 64 bit
    padding_needed = block_size - (len(plaintext) % block_size)
    padding_char = chr(padding_needed)
    padded_text = plaintext + padding_char * padding_needed
    return padded_text

def plaintext_to_blocks(plaintext):
    """Chuyển plaintext thành các khối 64 bit với đệm PKCS#5"""
    # Áp dụng đệm PKCS#5
    padded_text = pkcs5_padding(plaintext)
    
    # Chuyển thành nhị phân
    binary_text = string_to_binary(padded_text)
    
    # Chia thành các khối 64 bit
    blocks = []
    for i in range(0, len(binary_text), 64):
        block = binary_text[i:i+64]
        blocks.append(block)
    
    return blocks
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
def ip_permutation(block):
    if len(block) != 64:
        raise ValueError("Khối phải có đúng 64 bit!")
    ip_block = ""
    for index in IP:
        ip_block += block[index - 1]  # Chuyển từ 1-based sang 0-based
    return ip_block
def split_ip_block(ip_block):
    left_half = ip_block[:32]
    right_half = ip_block[32:]
    return left_half, right_half
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]
def expansion(Ri):
    if len(Ri) != 32:
        raise ValueError("R phải có đúng 32 bit!")
    expanded = ""
    for index in E:
        expanded += Ri[index - 1]
    return expanded
S_BOXES = [
        # S1
        [
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
        ],
        # S2
        [
            [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
        ],
        # S3
        [
            [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
        ],
        # S4
        [
            [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
        ],
        # S5
        [
            [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
        ],
        # S6
        [
            [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
        ],
        # S7
        [
            [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
        ],
        # S8
        [
            [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
        ]
    ]
def sbox_substitution(input_48bit):
    if len(input_48bit) != 48:
        raise ValueError("Đầu vào S-box phải có đúng 48 bit!")
    output_32bit = ""
    for i in range(8):
        group = input_48bit[i*6:(i+1)*6]
        row = int(group[0] + group[5], 2)  # Bit đầu và cuối xác định hàng
        col = int(group[1:5], 2)  # 4 bit giữa xác định cột
        value = S_BOXES[i][row][col]
        output_32bit += format(value, '04b')  # Chuyển thành 4 bit
    return output_32bit
P = [
        16, 7, 20, 21, 29, 12, 28, 17,
        1, 15, 23, 26, 5, 18, 31, 10,
        2, 8, 24, 14, 32, 27, 3, 9,
        19, 13, 30, 6, 22, 11, 4, 25
    ]
def p_permutation(sbox_output):
    if len(sbox_output) != 32:
        raise ValueError("Đầu ra S-box phải có đúng 32 bit!")
    p_output = ""
    for index in P:
        p_output += sbox_output[index - 1]
    return p_output
def f_function(R, K):
    expanded_R = expansion(R)
    xored = xor(expanded_R, K)
    sbox_output = sbox_substitution(xored)
    return p_permutation(sbox_output)
def xor(bits1, bits2):
    if len(bits1) != len(bits2):
        raise ValueError("Hai chuỗi bit phải có độ dài bằng nhau!")
    return ''.join('0' if b1 == b2 else '1' for b1, b2 in zip(bits1, bits2))

def des_rounds(L0, R0, subkeys):
    L = L0
    R = R0
    for i in range(16):
        L_next = R
        f_output = f_function(R, subkeys[i % len(subkeys)])
        R_next = xor(L, f_output)
        L = L_next
        R = R_next
        print(f"Vòng {i+1}: L{i+1} = {L}, R{i+1} = {R}")
    return L, R
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
def FP_permutation(L16, R16):
    combined = R16 + L16  # Ghép R16 + L16
    if len(combined) != 64:
        raise ValueError("Khối R16 + L16 phải có đúng 64 bit!")
    ciphertext = ""
    for index in FP:
        ciphertext += combined[index - 1]
    return ciphertext
def main():
    # Bản rõ DES
    plaintext = "Hello DES!"
    iv = string_to_binary("12345678")
    # khoá DES
    key = "DESEXAMP"
    print("Khóa gốc:", key)
    print("Quá trình sinh khóa con:")
    binary_key = key_to_binary(key)
    print("Khóa nhị phân:", binary_key)
    if len(binary_key) != 64:
        raise ValueError("Khóa phải có đúng 64 bit!")
    key_56bit = pc1_permutation(binary_key)
    print("Khóa 56 bit sau khi chuyển đổi:", key_56bit)
    C_list, D_list = generate_subkeys(key_56bit)
    print("\nKết quả dịch trái qua 16 vòng:")
    subkeys = []
    for i in range(1, 17):
        print(f"Vòng {i}:")
        print(f"  C{i}: {C_list[i]}")
        print(f"  D{i}: {D_list[i]}")
        sub_key_48bit = pc2_permutation(C_list[i], D_list[i])
        subkeys.append(sub_key_48bit)
        print(f"Vòng {i}: Khóa con K{i}: {sub_key_48bit}")
    print("Kết thúc sinh khoá con")
    print("Chuỗi gốc:", plaintext)
    blocks = plaintext_to_blocks(plaintext)
    print("Các khối 64 bit:")
    print("Plaintext sau đệm (văn bản):", pkcs5_padding(plaintext))
    print("Các khối 64 bit:")
    for i, block in enumerate(blocks, 1):
        print(f"Khối {i}: {block} ({len(block)} bit)")
    ip_blocks = []
    ciphertexts = []
    prev_ciphertext = iv  # Bắt đầu với IV
    for i, block in enumerate(blocks, 1):
        block = xor(block, prev_ciphertext)
        ip_block = ip_permutation(block)
        ip_blocks.append(ip_block)
        L0, R0 = split_ip_block(ip_block)
        print(f"Khối {i} (sau IP): {ip_block} ({len(ip_block)} bit)")
        print(f"  L0 (32 bit): {L0}")
        print(f"  R0 (32 bit): {R0}")
        print(f"\n16 vòng mã hóa cho khối {i}:")
        L_16, R_16 = des_rounds(L0, R0, subkeys)
        print(f"Kết quả cuối (L16, R16): {L_16}, {R_16}")
        ciphertext = FP_permutation(L_16, R_16)
        ciphertexts.append(ciphertext)
        print(f"Ciphertext khối {i}: {ciphertext} (hex: {hex(int(ciphertext, 2))[2:].zfill(16)})")
        prev_ciphertext = ciphertext 
    # Chuỗi ciphertext cuối cùng
    final_ciphertext = ''.join(ciphertexts)
    final_ciphertext_hex = hex(int(final_ciphertext, 2))[2:].zfill(len(final_ciphertext) // 4)
    print("\nChuỗi ciphertext cuối cùng:")
    print(f"Nhị phân: {final_ciphertext}")
    print(f"Hex: {final_ciphertext_hex}")
main()
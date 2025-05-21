from tabulate import tabulate
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

def string_to_hex(s):
    try:
        byte_data = s.encode('utf-8')
    except UnicodeEncodeError:
        raise ValueError("Chuỗi đầu vào không thể chuyển thành byte (kiểm tra ký tự không hợp lệ)")
    
    # Trả về danh sách các giá trị byte
    return list(byte_data)

def hex_to_string(hex_list):
    """Chuyển danh sách byte thành chuỗi hex."""
    return ''.join(format(b, '02x') for b in hex_list)

def rot_word(word):
    """Xoay trái 1 byte trong từ 4 byte."""
    return [word[1], word[2], word[3], word[0]]

def sub_word(word):
    """Áp dụng S-box cho từng byte trong từ."""
    return [SBOX[byte] for byte in word]

def xor_words(word1, word2):
    """XOR hai từ (4 byte)."""
    return [a ^ b for a, b in zip(word1, word2)]
def print_hex(byte_list):
    """In danh sách byte dưới dạng hex."""
    return [format(b, '02x') for b in byte_list]
def key_expansion(key):
    """Mở rộng khóa 16 byte thành 11 khóa vòng (176 byte)."""
    print("\n=== Bắt đầu mở rộng khóa ===")
    key_bytes = string_to_hex(key)
    print("Khóa gốc (bytes) ASCII:", key_bytes)
    print("Khoá gốc hex: ",print_hex(key_bytes))
    w = [[] for _ in range(44)]
    
    # Bước 1: Khởi tạo 4 từ đầu tiên từ khóa gốc
    print("\nKhởi tạo 4 từ đầu tiên từ khóa gốc:")
    for i in range(4):
        w[i] = key_bytes[4*i:4*i+4]
        print(f"w[{i}] = {w[i]}")
    
    # Bước 2: Tạo 40 từ tiếp theo
    print("\nTạo 40 từ tiếp theo:")
    for i in range(4, 44):
        temp = w[i-1]
        print(f"\nTính w[{i}]")
        print(f"temp (w[{i-1}]) = {temp}")
        if i % 4 == 0:
            print(f"i = {i} chia hết cho 4, áp dụng RotWord, SubWord và XOR với Rcon")
            temp = rot_word(temp)
            print(f"Sau RotWord ASCII: {temp}")
            print(f"Sau RotWord hex: {print_hex(temp)}")
            temp = sub_word(temp)
            print(f"Sau SubWord ASCII: {temp}")
            print(f"Sau SubWord hex: {print_hex(temp)}")
            temp = xor_words(temp, RCON[i//4 - 1])
            print(f"Sau XOR với Rcon[{i//4 - 1}]: {temp}")
        w[i] = xor_words(w[i-4], temp)
        print(f"w[{i}] = w[{i-4}] XOR temp = {w[i-4]} XOR {temp} = {w[i]}")
    
    # Bước 3: Tạo các khóa vòng từ các từ
    print("\nTạo các khóa vòng:")
    round_keys = []
    for i in range(0, 44, 4):
        round_key = w[i] + w[i+1] + w[i+2] + w[i+3]
        print(f"Khóa vòng {i//4}: {round_key}")
        round_keys.append(round_key)
    
    return round_keys

def pkcs5_padding(plaintext):
    """Áp dụng đệm PKCS#5 cho plaintext."""
    print("\n=== Áp dụng đệm PKCS#5 ===")
    block_size = 16
    padding_needed = block_size - (len(plaintext) % block_size)
    padding_char = chr(padding_needed)
    padded_text = plaintext + padding_char * padding_needed
    print(f"Plaintext gốc: {plaintext}")
    print(f"Độ dài plaintext: {len(plaintext)}")
    print(f"Cần đệm: {padding_needed} byte")
    print(f"Plaintext sau đệm: {padded_text}")
    return padded_text



def sub_bytes(state):
    """Thay thế byte bằng S-box."""
    print("\nÁp dụng SubBytes:")
    result = [[SBOX[state[i][j]] for j in range(4)] for i in range(4)]
    print(f"Trạng thái sau SubBytes: {result}")
    return result

def shift_rows(state):
    """Dịch trái các hàng."""
    print("\nÁp dụng ShiftRows:")
    result = [
        [state[0][0], state[0][1], state[0][2], state[0][3]],
        [state[1][1], state[1][2], state[1][3], state[1][0]],
        [state[2][2], state[2][3], state[2][0], state[2][1]],
        [state[3][3], state[3][0], state[3][1], state[3][2]]
    ]
    print(f"Trạng thái sau ShiftRows: {result}")
    return result

MIX_COLUMNS_MATRIX = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

def gf_mult(a, b):
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
    print("\n--- Bắt đầu bước MixColumns ---")
    new_state_rowwise = [[0] * 4 for _ in range(4)]
    for c in range(4):
        for r in range(4):
            new_state_rowwise[r][c] = (
                gf_mult(MIX_COLUMNS_MATRIX[r][0], state_rowwise[0][c]) ^ # Hàng r, cột 0 của MIX_COLUMNS_MATRIX nhân với phần tử hàng 0, cột c của state_rowwise
                gf_mult(MIX_COLUMNS_MATRIX[r][1], state_rowwise[1][c]) ^ # Hàng r, cột 1 của MIX_COLUMNS_MATRIX nhân với phần tử hàng 1, cột c của state_rowwise
                gf_mult(MIX_COLUMNS_MATRIX[r][2], state_rowwise[2][c]) ^ # Hàng r, cột 2 của MIX_COLUMNS_MATRIX nhân với phần tử hàng 2, cột c của state_rowwise
                gf_mult(MIX_COLUMNS_MATRIX[r][3], state_rowwise[3][c])   # Hàng r, cột 3 của MIX_COLUMNS_MATRIX nhân với phần tử hàng 3, cột c của state_rowwise
            )

    print(f"\nTrạng thái sau MixColumns (decimal): {new_state_rowwise}")
    print("--- Kết thúc bước MixColumns ---")
    return new_state_rowwise

def add_round_key(state, round_key):
    """XOR ma trận trạng thái với khóa vòng."""
    print("\nÁp dụng AddRoundKey:")
    round_key_T = [[round_key[j * 4 + i] for j in range(4)] for i in range(4)]
    print(f"Khóa vòng: {round_key_T}")
    result = [[state[i][j] ^ round_key_T[i][j] for j in range(4)] for i in range(4)]
    print(f"Trạng thái sau AddRoundKey (Decimal): {result}")
    return result
def state_to_ciphertext(state):
    # Khởi tạo danh sách 16 byte cho ciphertext
    ciphertext = [0] * 16
    
    # Trích xuất các byte theo cấu trúc hàng
    for i in range(4):  # Duyệt qua các hàng
        for j in range(4):  # Duyệt qua các cột
            # Vị trí trong danh sách tuyến tính: i * 4 + j
            ciphertext[i * 4 + j] = state[i][j]
    
    return ciphertext
def decimal_to_hex(ciphertext):
    return [f"{x:02x}" for x in ciphertext]
def aes_ecb_encrypt(plaintext, key):
    print("\n=== Bắt đầu mã hóa AES-128 ECB ===")
    
    # Bước 1: Mở rộng khóa
    print("\nBước 1: Mở rộng khóa")
    round_keys = key_expansion(key)
    print(f"Số khóa vòng: {len(round_keys)}")
    
    # Bước 2: Áp dụng đệm PKCS#5
    plaintext_padded = pkcs5_padding(plaintext)
    plaintext_bytes = string_to_hex(plaintext_padded)
    print(f"Plaintext bytes sau đệm (hex): {print_hex(plaintext_bytes)}")
    
    # Bước 3: Chia thành các khối 16 byte
    blocks = [plaintext_bytes[i:i+16] for i in range(0, len(plaintext_bytes), 16)]
    print(f"Các khối plaintext (hex): {[print_hex(block) for block in blocks]}")
    
    ciphertext = []
    
    # Bước 4: Mã hóa từng khối
    for block_index, block in enumerate(blocks):
        print(f"\n=== Mã hóa khối {block_index} ===")
        print(f"Khối plaintext (hex): {print_hex(block)}")
        
        # Chuyển khối thành ma trận trạng thái 4x4
        state = [[block[j * 4 + i] for j in range(4)] for i in range(4)]
        print(f"Ma trận trạng thái ban đầu (hex): {[print_hex(row) for row in state]}")
        
        # Vòng 0: Chỉ AddRoundKey
        print("\nVòng 0:")
        state = add_round_key(state, round_keys[0])
        print(f"Sau AddRoundKey (hex): {[print_hex(row) for row in state]}")
        
        # 9 vòng chính
        for round_num in range(1, 10):
            print(f"\nVòng {round_num}:")
            state = sub_bytes(state)
            print(f"Sau SubBytes (hex): {[print_hex(row) for row in state]}")
            state = shift_rows(state)
            print(f"Sau ShiftRows (hex): {[print_hex(row) for row in state]}")
            state = mix_columns(state)
            print(f"Sau MixColumns (hex): {[print_hex(row) for row in state]}")
            state = add_round_key(state, round_keys[round_num])
            print(f"Sau AddRoundKey (hex): {[print_hex(row) for row in state]}")
        
        # Vòng cuối: Không có MixColumns
        print("\nVòng cuối (10):")
        state = sub_bytes(state)
        print(f"Sau SubBytes (hex): {[print_hex(row) for row in state]}")
        state = shift_rows(state)
        print(f"Sau ShiftRows (hex): {[print_hex(row) for row in state]}")
        state = add_round_key(state, round_keys[10])
        print(f"Sau AddRoundKey (hex): {[print_hex(row) for row in state]}")
        
        # Chuyển ma trận trạng thái thành khối ciphertext
        cipher_block = [state[i][j] for j in range(4) for i in range(4)]
        cipher_block_hex = print_hex(cipher_block)
        print(cipher_block)
        print(f"Khối ciphertext (hex): {cipher_block_hex}")
        
        # Lưu ciphertext của khối này
        ciphertext.extend(cipher_block)
    
    return ciphertext

def main():
    """Hàm chính để chạy ví dụ mã hóa AES-128 CBC."""
    plaintext = "Two One Nine Two"
    key = "Thats my Kung Fu"
    # iv = "1234567890abcdef"  # IV phải dài 16 byte
    
    print("Plaintext:", plaintext)
    print("Key:", key)
    # print("IV:", iv)
    # aes_cbc_encrypt(plaintext, key, iv)
    # Mã hóa
    ciphertext_bytes = aes_ecb_encrypt(plaintext, key)
    ciphertext_hex = hex_to_string(ciphertext_bytes)
    
    print("\n=== Kết quả ===")
    print("Ciphertext (hex):", ciphertext_hex)

if __name__ == "__main__":
    main()
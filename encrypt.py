# Bảng hoán vị ban đầu (IP)
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

# Hàm chuyển đổi từ hexadecimal sang binary
def hex_to_bin(hex_string):
    return bin(int(hex_string, 16))[2:].zfill(64)

# Hàm chuyển đổi từ chuỗi ký tự sang binary
def string_to_bin(data):
    return ''.join([bin(ord(c))[2:].zfill(8) for c in data])

# Hàm áp dụng padding PKCS#5
def pkcs5_padding(data, block_size=8):
    padding_length = block_size - (len(data) % block_size)
    return data + chr(padding_length) * padding_length

# Hàm hoán vị theo IP
def permute_IP(bits):
    return ''.join([bits[i-1] for i in IP])

# Hàm chia thành hai phần (L0 và R0)
def split_LR(bits):
    return bits[:32], bits[32:]

# Hàm sinh khóa con (subkey) từ khóa đầu vào
def generate_subkeys(key):
    # Chuyển khóa từ hexadecimal sang binary
    key_bin = hex_to_bin(key)
    
    # Bảng hoán vị ban đầu PC-1
    PC1 = [
        57, 49, 41, 33, 25, 17, 9, 1,
        58, 50, 42, 34, 26, 18, 10, 2,
        59, 51, 43, 35, 27, 19, 11, 3,
        60, 52, 44, 36, 63, 55, 47, 39,
        31, 23, 15, 7, 62, 54, 46, 38,
        30, 22, 14, 6, 61, 53, 45, 37,
        29, 21, 13, 5, 28, 20, 12, 4
    ]
    
    # Bảng hoán vị con PC-2
    PC2 = [
        14, 17, 11, 24, 1, 5, 3, 28,
        15, 6, 21, 10, 23, 19, 12, 4,
        26, 8, 16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55, 30, 40,
        51, 45, 33, 48, 44, 49, 39, 56,
        34, 53, 46, 42, 50, 36, 29, 32
    ]
    
    # Hoán vị PC-1
    key = ''.join([key_bin[i-1] for i in PC1])
    
    # Chia khóa thành C0 và D0 (28 bit mỗi phần)
    C = key[:28]
    D = key[28:]
    
    subkeys = []
    
    # Dịch vòng và tạo khóa con
    shift_values = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    for i in range(16):
        # Dịch vòng C và D
        shift = shift_values[i]
        C = C[shift:] + C[:shift]
        D = D[shift:] + D[:shift]
        
        # Kết hợp C và D sau khi dịch
        combined = C + D
        
        # Hoán vị PC-2 để tạo khóa con
        subkey = ''.join([combined[i-1] for i in PC2])
        subkeys.append(subkey)
    
    return subkeys

# Mã hóa chuỗi "abcde" với khóa "d4e0b81e27bf6b9d3c9e4a2f5b6c7d8e"
def encrypt_data(data, key):
    # Áp dụng PKCS#5 padding
    data = pkcs5_padding(data)
    
    # Chuyển chuỗi "abcde" thành nhị phân
    data_bin = string_to_bin(data)
    print("data_bin: ", data_bin)
    # Hoán vị ban đầu
    num_blocks = len(data_bin) // 64  # Số lượng khối 64 bit
    
    for i in range(num_blocks):
        # Lấy khối 64 bit hiện tại
        block = data_bin[i * 64: (i + 1) * 64]
        
        # Hoán vị ban đầu (IP)
        block_ip = permute_IP(block)
        
        # Chia khối thành L0 và R0
        L0, R0 = split_LR(block_ip)
        
        # In kết quả sau khi hoán vị
        print(f"Khối {i + 1}: {block}")
        print("Khối sau hoán vị IP:", block_ip)
        print("L0:", L0)
        print("R0:", R0)
    subkeys = generate_subkeys(key)
    print("Khóa con:", subkeys)


def main():
    # Khóa bí mật
    key = 'd4e0b81e27bf6b9d3c9e4a2f5b6c7d8e'

    # Thực hiện mã hóa
    encrypt_data("d4e0b81e27bf6b9d3c9e4a2f5b6c7d8e", key)

main()
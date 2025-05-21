import matplotlib.pyplot as plt
import numpy as np
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

MIX_COLUMNS_MATRIX = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

# --- Các hàm AES cơ bản (tái sử dụng từ các cuộc trò chuyện trước) ---

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
    """Mở rộng khóa 16 byte thành 11 khóa vòng (176 byte)."""
    key_bytes = string_to_bytes(key_str)
    w = [[] for _ in range(44)] # 44 words for AES-128 (11 round keys * 4 words/key)
    
    # Initialize first 4 words from the original key
    for i in range(4):
        w[i] = key_bytes[4*i:4*i+4]
    
    # Generate subsequent 40 words
    for i in range(4, 44):
        temp = list(w[i-1]) # Create a copy to avoid modifying w[i-1] directly
        
        if i % 4 == 0:
            temp = rot_word(temp)
            temp = sub_word(temp)
            temp = xor_words(temp, RCON[i//4 - 1])
        
        w[i] = xor_words(w[i-4], temp)
    
    # Form round keys from words
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

# --- Các hàm hỗ trợ trực quan hóa ---

def state_to_flat_list(state):
    """Chuyển ma trận trạng thái 4x4 thành danh sách 16 byte phẳng."""
    flat_list = []
    for c in range(4): # Column-major order for AES internal state
        for r in range(4):
            flat_list.append(state[r][c])
    return flat_list

def calculate_difference_matrix(state1, state2):
    """Tính ma trận khác biệt (XOR) giữa hai trạng thái."""
    diff_matrix = [[state1[r][c] ^ state2[r][c] for c in range(4)] for r in range(4)]
    return diff_matrix

def count_diff_bytes(state1, state2):
    """Đếm số byte khác nhau giữa hai trạng thái."""
    count = 0
    for r in range(4):
        for c in range(4):
            if state1[r][c] != state2[r][c]:
                count += 1
    return count

def visualize_state_diffusion(state, title, ax, affected_bytes=None):
    """
    Vẽ ma trận trạng thái với các byte bị ảnh hưởng được tô màu.
    affected_bytes là một ma trận boolean 4x4.
    """
    ax.clear()
    ax.set_title(title, fontsize=10)
    
    # Tạo ma trận màu sắc: 0 cho không bị ảnh hưởng, 1 cho bị ảnh hưởng
    colors = np.zeros((4, 4))
    if affected_bytes is not None:
        for r in range(4):
            for c in range(4):
                if affected_bytes[r][c]:
                    colors[r][c] = 1 # Mark as affected

    cmap = plt.cm.get_cmap('Greys', 2) # 0: white, 1: grey/black for affected
    im = ax.imshow(colors, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Hiển thị giá trị hex của byte
    for r in range(4):
        for c in range(4):
            ax.text(c, r, f"{state[r][c]:02X}", ha='center', va='center', color='black', fontsize=9)
            if affected_bytes is not None and affected_bytes[r][c]:
                ax.text(c, r, f"{state[r][c]:02X}", ha='center', va='center', color='red', fontsize=9, fontweight='bold') # Highlight affected
    
    ax.set_xticks(np.arange(4))
    ax.set_yticks(np.arange(4))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False) # Remove grid lines
    ax.tick_params(axis='both', which='both', length=0) # Remove ticks

def aes_round_operations(state, round_key, round_num, is_last_round=False):
    """Thực hiện các phép toán của một vòng AES."""
    
    state_after_subbytes = sub_bytes(state)
    state_after_shiftrows = shift_rows(state_after_subbytes)
    
    if not is_last_round:
        state_after_mixcolumns = mix_columns(state_after_shiftrows)
    else:
        state_after_mixcolumns = state_after_shiftrows # No MixColumns in last round

    state_after_addroundkey = add_round_key(state_after_mixcolumns, round_key)
    
    return state_after_subbytes, state_after_shiftrows, state_after_mixcolumns, state_after_addroundkey

def simulate_fault_attack_visualization(plaintext_str, key_str, fault_round, fault_byte_index, fault_value):
    """
    Mô phỏng tấn công lỗi và trực quan hóa sự khuếch tán.
    
    Args:
        plaintext_str (str): Văn bản gốc (16 ký tự).
        key_str (str): Khóa (16 ký tự).
        fault_round (int): Vòng tiêm lỗi (0-9 cho vòng chính).
        fault_byte_index (int): Chỉ số byte để tiêm lỗi (0-15).
        fault_value (int): Giá trị lỗi để XOR vào byte (0-255).
    """
    if len(plaintext_str) != 16 or len(key_str) != 16:
        print("Lỗi: Plaintext và Key phải có độ dài 16 byte (16 ký tự).")
        return

    # Chuẩn bị dữ liệu
    plaintext_bytes = string_to_bytes(plaintext_str)
    round_keys = key_expansion(key_str)
    
    # Khởi tạo trạng thái ban đầu (giả định IV = 0 cho đơn giản)
    # Trong thực tế, đây là P XOR IV. Để mô phỏng DFA, ta giả định trạng thái trước vòng 0
    # hoặc trạng thái S^9 như trong tài liệu. Ở đây ta sẽ tiêm lỗi vào trạng thái đầu vào của một vòng.
    
    # Chuyển khối plaintext thành ma trận trạng thái 4x4 (column-major)
    initial_state_correct = [[plaintext_bytes[j * 4 + i] for j in range(4)] for i in range(4)]
    initial_state_faulty = [[plaintext_bytes[j * 4 + i] for j in range(4)] for i in range(4)]

    # --- Mô phỏng quá trình mã hóa (chỉ để theo dõi trạng thái) ---
    current_state_correct = [row[:] for row in initial_state_correct]
    current_state_faulty = [row[:] for row in initial_state_faulty]

    # Lưu trữ dữ liệu cho biểu đồ
    diff_byte_counts = []
    round_labels = []
    
    # Lưu trữ các ma trận trạng thái và ma trận khác biệt để trực quan hóa chi tiết
    detailed_states = [] # (round_num, operation, correct_state, faulty_state, diff_matrix, affected_mask)

    print(f"\n--- Mô phỏng tấn công lỗi vi sai (DFA) trên AES-128 ---")
    print(f"Tiêm lỗi: Vòng {fault_round}, Byte {fault_byte_index}, Giá trị lỗi: {fault_value:02X}")
    print(f"Plaintext: {plaintext_str} (Hex: {bytes_to_hex_str(plaintext_bytes)})")
    print(f"Key: {key_str} (Hex: {bytes_to_hex_str(string_to_bytes(key_str))})")

    num_rounds = 10 # For AES-128, 10 main rounds + 1 initial AddRoundKey

    # Vòng 0 (Initial AddRoundKey)
    state_after_addroundkey_correct = add_round_key(current_state_correct, round_keys[0])
    state_after_addroundkey_faulty = add_round_key(current_state_faulty, round_keys[0])
    
    diff_matrix_0 = calculate_difference_matrix(state_after_addroundkey_correct, state_after_addroundkey_faulty)
    diff_count_0 = count_diff_bytes(state_after_addroundkey_correct, state_after_addroundkey_faulty)
    diff_byte_counts.append(diff_count_0)
    round_labels.append(f"R0_ARK")
    detailed_states.append((0, "AddRoundKey", state_after_addroundkey_correct, state_after_addroundkey_faulty, diff_matrix_0, np.array(diff_matrix_0) != 0))

    current_state_correct = state_after_addroundkey_correct
    current_state_faulty = state_after_addroundkey_faulty

    # Các vòng chính (1 đến 9)
    for r_num in range(1, num_rounds + 1): # Vòng 1 đến 10
        is_last_round = (r_num == num_rounds) # Vòng 10 là vòng cuối cùng
        
        # --- Tiêm lỗi tại đầu vòng (trước SubBytes) ---
        if r_num == fault_round:
            row_idx = fault_byte_index % 4
            col_idx = fault_byte_index // 4
            print(f"\n--- TIÊM LỖI TẠI VÒNG {fault_round}, BYTE ({row_idx},{col_idx}) ---")
            current_state_faulty[row_idx][col_idx] ^= fault_value
            
            diff_matrix_fault_inject = calculate_difference_matrix(current_state_correct, current_state_faulty)
            diff_count_fault_inject = count_diff_bytes(current_state_correct, current_state_faulty)
            diff_byte_counts.append(diff_count_fault_inject)
            round_labels.append(f"R{r_num}_Fault")
            detailed_states.append((r_num, "Fault Injection", current_state_correct, current_state_faulty, diff_matrix_fault_inject, np.array(diff_matrix_fault_inject) != 0))

        # --- Thực hiện các bước của vòng ---
        # SubBytes
        state_sb_correct = sub_bytes(current_state_correct)
        state_sb_faulty = sub_bytes(current_state_faulty)
        diff_matrix_sb = calculate_difference_matrix(state_sb_correct, state_sb_faulty)
        diff_count_sb = count_diff_bytes(state_sb_correct, state_sb_faulty)
        diff_byte_counts.append(diff_count_sb)
        round_labels.append(f"R{r_num}_SB")
        detailed_states.append((r_num, "SubBytes", state_sb_correct, state_sb_faulty, diff_matrix_sb, np.array(diff_matrix_sb) != 0))
        
        # ShiftRows
        state_sr_correct = shift_rows(state_sb_correct)
        state_sr_faulty = shift_rows(state_sb_faulty)
        diff_matrix_sr = calculate_difference_matrix(state_sr_correct, state_sr_faulty)
        diff_count_sr = count_diff_bytes(state_sr_correct, state_sr_faulty)
        diff_byte_counts.append(diff_count_sr)
        round_labels.append(f"R{r_num}_SR")
        detailed_states.append((r_num, "ShiftRows", state_sr_correct, state_sr_faulty, diff_matrix_sr, np.array(diff_matrix_sr) != 0))

        # MixColumns (không có ở vòng cuối)
        if not is_last_round:
            state_mc_correct = mix_columns(state_sr_correct)
            state_mc_faulty = mix_columns(state_sr_faulty)
            diff_matrix_mc = calculate_difference_matrix(state_mc_correct, state_mc_faulty)
            diff_count_mc = count_diff_bytes(state_mc_correct, state_mc_faulty)
            diff_byte_counts.append(diff_count_mc)
            round_labels.append(f"R{r_num}_MC")
            detailed_states.append((r_num, "MixColumns", state_mc_correct, state_mc_faulty, diff_matrix_mc, np.array(diff_matrix_mc) != 0))
            current_state_correct = state_mc_correct
            current_state_faulty = state_mc_faulty
        else: # Vòng cuối không có MixColumns
            current_state_correct = state_sr_correct
            current_state_faulty = state_sr_faulty

        # AddRoundKey
        state_ark_correct = add_round_key(current_state_correct, round_keys[r_num])
        state_ark_faulty = add_round_key(current_state_faulty, round_keys[r_num])
        diff_matrix_ark = calculate_difference_matrix(state_ark_correct, state_ark_faulty)
        diff_count_ark = count_diff_bytes(state_ark_correct, state_ark_faulty)
        diff_byte_counts.append(diff_count_ark)
        round_labels.append(f"R{r_num}_ARK")
        detailed_states.append((r_num, "AddRoundKey", state_ark_correct, state_ark_faulty, diff_matrix_ark, np.array(diff_matrix_ark) != 0))
        
        current_state_correct = state_ark_correct
        current_state_faulty = state_ark_faulty

    # --- Trực quan hóa ---
    
    # Biểu đồ số byte khác biệt qua các bước
    plt.figure(figsize=(15, 6))
    plt.plot(round_labels, diff_byte_counts, marker='o', linestyle='-', color='blue')
    plt.title('Số byte khác biệt qua các bước của AES (DFA)')
    plt.xlabel('Vòng và Bước')
    plt.ylabel('Số byte khác biệt')
    plt.xticks(rotation=90, fontsize=8)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # Trực quan hóa chi tiết sự khuếch tán của lỗi trên ma trận trạng thái
    # Chọn một số điểm quan trọng để hiển thị
    display_points = [
        (0, "AddRoundKey"), # Initial ARK
        (fault_round, "Fault Injection"), # After fault injection
        (fault_round, "SubBytes"),
        (fault_round, "ShiftRows"),
        (fault_round, "MixColumns") if fault_round != num_rounds else (fault_round, "ShiftRows"), # Skip MC if last round
        (fault_round + 1, "SubBytes") if fault_round + 1 <= num_rounds else None, # Next round's SB
        (fault_round + 1, "MixColumns") if fault_round + 1 <= num_rounds and fault_round + 1 != num_rounds else None # Next round's MC (if applicable)
    ]
    
    # Lọc các điểm hiển thị hợp lệ
    display_points = [p for p in display_points if p is not None]
    
    # Lấy dữ liệu cho các điểm hiển thị
    display_data = []
    for r_num, op_name in display_points:
        for item in detailed_states:
            if item[0] == r_num and item[1] == op_name:
                display_data.append(item)
                break
    
    # Vẽ các ma trận
    num_plots = len(display_data)
    if num_plots > 0:
        fig, axes = plt.subplots(1, num_plots, figsize=(4 * num_plots, 4))
        if num_plots == 1: # Handle single subplot case
            axes = [axes]
        
        for i, (r_num, op_name, correct_state, faulty_state, diff_matrix, affected_mask) in enumerate(display_data):
            title = f"R{r_num} {op_name}\nDiff: {count_diff_bytes(correct_state, faulty_state)} bytes"
            visualize_state_diffusion(faulty_state, title, axes[i], affected_bytes=affected_mask)
        
        plt.tight_layout()
        plt.show()
    else:
        print("Không có điểm dữ liệu nào để trực quan hóa chi tiết.")

# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    # Ví dụ 1: Tiêm lỗi ở Vòng 1, Byte 0
    # Plaintext và Key phải có độ dài 16 ký tự
    plaintext_example = "This is a test!!"
    key_example = "MySecretAESKey!!"
    
    # Tiêm lỗi ở Vòng 1 (sau AddRoundKey đầu tiên), Byte 0 (s_0,0), XOR với 0x01
    simulate_fault_attack_visualization(plaintext_example, key_example, 
                                        fault_round=1, fault_byte_index=0, fault_value=0x01)
    
    # Ví dụ 2: Tiêm lỗi ở Vòng 8, Byte 5 (tương tự tài liệu)
    # Tài liệu nói "If a fault causes in one byte of the state matrix, then it is fed into round 8"
    # Tức là lỗi được tiêm vào đầu vòng 8 (trước SubBytes của vòng 8)
    print("\n--- Ví dụ theo tài liệu (Tiêm lỗi ở Vòng 8) ---")
    simulate_fault_attack_visualization(plaintext_example, key_example, 
                                        fault_round=8, fault_byte_index=5, fault_value=0xAA)

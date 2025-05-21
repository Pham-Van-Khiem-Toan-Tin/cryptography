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

def mix_column(column):
    """Thực hiện MixColumns trên 1 cột (4 byte)."""
    mix_matrix = [
        [2, 3, 1, 1],
        [1, 2, 3, 1],
        [1, 1, 2, 3],
        [3, 1, 1, 2]
    ]
    result = []
    for row in mix_matrix:
        val = 0
        for i in range(4):
            val ^= gf_mult(row[i], column[i])
        result.append(val)
    return result

# 🔍 Ví dụ: 1 cột cần MixColumns (giá trị mẫu từ FIPS-197)
state_after_shiftrows = [
    [1, 183, 117, 76],
    [195, 9, 159, 76],
    [143, 2, 64, 47],
    [159, 51, 33, 133]
]

# Lấy 1 cột cụ thể, ví dụ cột thứ 0 (index 0)
example_col = [state_after_shiftrows[r][0] for r in range(4)]  # = [1, 195, 143, 159]

# Gọi hàm mix_column
result = mix_column(example_col)

# In kết quả
print("Kết quả sau MixColumns (hex):", [hex(b) for b in result])
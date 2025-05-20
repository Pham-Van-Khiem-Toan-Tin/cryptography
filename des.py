def hex_to_binary(hex_string):
  """
  Chuyển đổi một chuỗi số thập lục phân (hex) thành chuỗi số nhị phân (binary).

  Args:
    hex_string: Chuỗi số thập lục phân cần chuyển đổi.

  Returns:
    Chuỗi số nhị phân tương ứng.
    Trả về None nếu đầu vào không phải là chuỗi hex hợp lệ.
  """
  try:
    # Chuyển chuỗi hex thành số nguyên
    decimal_value = int(hex_string, 16)
    # Chuyển số nguyên thành chuỗi nhị phân và loại bỏ tiền tố "0b"
    binary_string = bin(decimal_value)[2:]
    return binary_string
  except ValueError:
    # Xử lý trường hợp đầu vào không phải là chuỗi hex hợp lệ
    return None

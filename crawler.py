import requests
import csv
import time

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

base_url = "https://drugbank.vn/services/drugbank/api/public/thuoc?page={}&size=12&sort=rate,desc&sort=tenThuoc,asc"
price_url_template = "https://drugbank.vn/services/drugbank/api/public/gia-ke-khai?sdk={}&size=10000"

results = []
page = 0
max_pages = 100

while page < max_pages:
    url = base_url.format(page)
    print(f"📦 Đang lấy dữ liệu từ trang {page}...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Lỗi kết nối (mã {response.status_code}) tại trang {page}")
        break

    try:
        items = response.json()
    except Exception as e:
        print(f"❌ Không parse được JSON tại trang {page}: {e}")
        break

    if not items:
        print("✅ Hết dữ liệu.")
        break

    for item in items:
        sdk = item.get("soDangKy", "").strip()
        gia_ke_khai = ""

        # Gọi API phụ để lấy giá kê khai
        if sdk:
            price_url = price_url_template.format(sdk)
            try:
                price_response = requests.get(price_url, headers=headers)
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    if price_data:
                        # Ưu tiên lấy giá từ dòng đầu tiên
                        gia_ke_khai = price_data[0].get("giaBan", "")
                        don_vi_tinh = price_data[0].get("dvt", "")
            except Exception as e:
                print(f"⚠️ Lỗi lấy giá kê khai cho SDK {sdk}: {e}")

        results.append([
            (item.get("tenThuoc") or "").strip(),
            sdk,
            (item.get("hoatChat") or "").strip(),
            (item.get("nongDo") or "").strip(),
            (item.get("baoChe") or "").strip(),
            (item.get("dongGoi") or "").strip(),
            (item.get("phanLoai") or "").strip(),
            (item.get("congTySx") or "").strip(),
            (item.get("nuocSx") or "").strip(),
            (item.get("tieuChuan") or "").strip(),
            (item.get("tuoiTho") or "").strip(),
            gia_ke_khai,
            don_vi_tinh
        ])

        time.sleep(0.1)  # tránh spam quá nhanh gây block IP

    page += 1
    time.sleep(0.3)

# Ghi dữ liệu ra file CSV
with open("C:/Users/KhiemJP/Desktop/Code/codematma/thuoc_drugbank_full.csv", "w", newline='', encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Tên thuốc", "Số ĐK", "Hoạt chất", "Hàm lượng", "Dạng bào chế",
        "Đóng gói", "Phân loại", "Công ty SX", "Nước SX", "Tiêu chuẩn",
        "Tuổi thọ", "Giá kê khai", "Đơn vị tính"
    ])
    writer.writerows(results)

print(f"✅ Đã lưu {len(results)} thuốc vào 'thuoc_drugbank_full.csv'")

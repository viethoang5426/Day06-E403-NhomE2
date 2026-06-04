# -*- coding: utf-8 -*-
"""Bổ sung khách sạn, điểm tham quan, vận chuyển cho các tỉnh/thành mới."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PRICE_NOTE = "Giá demo tham khảo để tính budget trong TravelBot, không phải giá realtime/kê khai."
DESC_SUFFIX = (
    " Giá trong file là giá demo tham khảo để chatbot tính ngân sách, "
    "không phải giá realtime/kê khai; vui lòng kiểm tra lại tại link trước khi thanh toán."
)

IMAGES = {
    5: "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400",
    4: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
    3: "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400",
}

# (name, address, district, stars, rooms|None, phone, website, sourceName, sourceUrl, near_beach)
REGION_HOTELS = [
    # Hà Nội — nguồn: Cổng thông tin du lịch Hà Nội / website chính thức khách sạn
    ("Sofitel Legend Metropole Hanoi", "15 Ngô Quang Huyện, P. Tràng Tiền, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 5, 364, "024 3826 6919", "https://www.sofitel-legend-metropole-hanoi.com", "Hanoi Tourism", "https://hanoi.gov.vn", False),
    ("JW Marriott Hotel Hanoi", "8 Đỗ Đức Đức, P. Mễ Trì, Nam Từ Liêm, Hà Nội", "Nam Từ Liêm", "Hà Nội", 5, 450, "024 3833 5588", "https://www.marriott.com/en-us/hotels/hanjw-jw-marriott-hotel-hanoi/overview/", "JW Marriott Hanoi", "https://www.marriott.com", False),
    ("Lotte Hotel Hanoi", "54 Liễu Giai, P. Cống Vị, Ba Đình, Hà Nội", "Ba Đình", "Hà Nội", 5, 318, "024 3333 1000", "https://www.lottehotel.com/hanoi", "Lotte Hotel Hanoi", "https://www.lottehotel.com", False),
    ("Hilton Hanoi Opera", "1 Lê Thánh Tông, P. Phan Chu Trinh, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 5, 268, "024 3933 0500", "https://www.hilton.com/en/hotels/hanophi-hilton-hanoi-opera/", "Hilton Hanoi Opera", "https://www.hilton.com", False),
    ("Melia Hanoi", "44B Lý Thường Kiệt, P. Trần Hưng Đạo, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 5, 306, "024 3933 3333", "https://www.melia.com/en/hotels/vietnam/hanoi/melia-hanoi", "Melia Hanoi", "https://www.melia.com", False),
    ("Silk Path Hotel Hanoi", "19-21 Lê Thánh Tông, P. Phan Chu Trinh, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 4, 75, "024 3936 6666", "https://silkpathhotel.com/hanoi", "Silk Path Hospitality", "https://silkpathhotel.com", False),
    ("Mường Thanh Grand Hanoi Centre", "30 Lý Thường Kiệt, P. Trần Hưng Đạo, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 4, 224, "024 3942 3366", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
    ("La Siesta Premium Hang Be", "94 Hàng Bè, P. Hàng Bạc, Hoàn Kiếm, Hà Nội", "Hoàn Kiếm", "Hà Nội", 4, 27, "024 3926 1500", "https://lasiestahotels.com", "La Siesta Group", "https://lasiestahotels.com", False),
    # TP.HCM
    ("Park Hyatt Saigon", "2 Lam Sơn Square, P. Bến Nghé, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 5, 245, "028 3824 1234", "https://www.hyatt.com/en-US/hotel/vietnam/park-hyatt-saigon/saiph", "Park Hyatt Saigon", "https://www.hyatt.com", False),
    ("Hotel Nikko Saigon", "235 Nguyễn Văn Cừ, P. Nguyễn Cư Trinh, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 5, 388, "028 3925 7777", "https://www.hotelnikkosaigon.com", "Hotel Nikko Saigon", "https://www.hotelnikkosaigon.com", False),
    ("Caravelle Saigon", "19-23 Lam Sơn Square, P. Bến Nghé, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 5, 335, "028 3823 4999", "https://www.caravellehotel.com", "Caravelle Saigon", "https://www.caravellehotel.com", False),
    ("Rex Hotel Ho Chi Minh", "141 Nguyễn Huệ, P. Bến Nghé, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 5, 286, "028 3829 2185", "https://www.rexhotelvietnam.com", "Rex Hotel", "https://www.rexhotelvietnam.com", False),
    ("Pullman Saigon Centre", "138 Nguyễn Thị Minh Khai, P. Phạm Ngũ Lão, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 5, 306, "028 3838 8686", "https://www.pullman-saigon-centre.com", "Accor Pullman", "https://www.pullman-saigon-centre.com", False),
    ("Liberty Central Saigon Centre", "179 Le Thanh Ton, P. Bến Nghé, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 4, 140, "028 3827 2727", "https://www.libertyhotelsresorts.com", "Liberty Hotels", "https://www.libertyhotelsresorts.com", False),
    ("Silverland Yen Hotel", "73-75 Thu Khoa Huan, P. Bến Thành, Quận 1, TP.HCM", "Quận 1", "TP.HCM", 4, 80, "028 3822 4248", "https://silverlandhotels.com", "Silverland Hotel Group", "https://silverlandhotels.com", False),
    # Huế
    ("Azerai La Residence Hue", "5 Lê Lợi, P. Phú Hội, TP. Huế", "Phú Hội", "Huế", 5, 122, "0234 3837 475", "https://www.azerai.com/la-residence-hue", "Azerai La Residence", "https://www.azerai.com", True),
    ("Pilgrimage Village Boutique Resort", "130 Minh Mạng, P. Vỹ Dạ, TP. Huế", "Vỹ Dạ", "Huế", 5, 138, "0234 3885 461", "https://www.pilgrimagevillage.com", "Pilgrimage Village", "https://www.pilgrimagevillage.com", False),
    ("Imperial Hotel Hue", "08 Võ Văn Tần, P. Vỹ Dạ, TP. Huế", "Vỹ Dạ", "Huế", 5, 194, "0234 3835 227", "https://www.imperialhotelhue.com", "Imperial Hotel Hue", "https://www.imperialhotelhue.com", False),
    ("Mường Thanh Holiday Hue", "38 Lê Lợi, P. Phú Hội, TP. Huế", "Phú Hội", "Huế", 4, 180, "0234 3832 222", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
    ("Eldora Hotel Hue", "60 Ben Nghe, P. Phu Hoi, TP. Hue", "Phú Hội", "Huế", 4, 81, "0234 3812 222", "https://eldorahotel.com", "Eldora Hotel", "https://eldorahotel.com", False),
    # Phú Quốc
    ("JW Marriott Phu Quoc Emerald Bay", "Khem Beach, An Thoi, Phú Quốc, Kiên Giang", "An Thới", "Phú Quốc", 5, 244, "0297 377 7777", "https://www.marriott.com/en-us/hotels/pqcjw-jw-marriott-phu-quoc-emerald-bay-resort-and-spa/overview/", "JW Marriott Phu Quoc", "https://www.marriott.com", True),
    ("Vinpearl Resort & Spa Phu Quoc", "Bai Dai, Ganh Dau, Phu Quoc, Kien Giang", "Gành Dầu", "Phú Quốc", 5, 402, "0297 398 1888", "https://vinpearl.com", "Vinpearl Phu Quoc", "https://vinpearl.com", True),
    ("Fusion Resort Phu Quoc", "Vung Bau Beach, Duong To, Phu Quoc", "Dương Tô", "Phú Quốc", 5, 92, "0297 267 3000", "https://fusionresorts.com/phu-quoc", "Fusion Resorts", "https://fusionresorts.com", True),
    ("Sol Beach House Phu Quoc", "Zone 1, Duong Dong Town, Phu Quoc", "Dương Đông", "Phú Quốc", 4, 108, "0297 399 0123", "https://www.melia.com/en/hotels/vietnam/phu-quoc/sol-beach-house-phu-quoc", "Melia Sol Beach House", "https://www.melia.com", True),
    ("Mường Thanh Holiday Phu Quoc", "Ganh Dau, Phu Quoc, Kien Giang", "Gành Dầu", "Phú Quốc", 4, 150, "0297 398 8888", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", True),
    # Đà Lạt
    ("Dalat Palace Heritage", "12 Trần Phú, P. 10, TP. Đà Lạt", "P. 10", "Đà Lạt", 5, 43, "0263 3820 111", "https://dalatpalace.vn", "Dalat Palace Heritage", "https://dalatpalace.vn", False),
    ("Ana Mandara Villas Dalat", "Le Lai Street, Ward 5, Da Lat", "P. 5", "Đà Lạt", 5, 17, "0263 355 5888", "https://anamandara-villas-dalat.com", "Ana Mandara Villas", "https://anamandara-villas-dalat.com", False),
    ("Terracotta Hotel & Resort Dalat", "Bao Dai Palace Area, Ward 10, Da Lat", "P. 10", "Đà Lạt", 4, 240, "0263 383 3333", "https://terracottadalat.com", "Terracotta Hotel", "https://terracottadalat.com", False),
    ("Dalat Edensee Lake Resort & Spa", "Tuyen Lam Lake, Ward 7, Da Lat", "P. 7", "Đà Lạt", 5, 120, "0263 383 1515", "https://edensee.vn", "Edensee Lake Resort", "https://edensee.vn", False),
    ("TTC Hotel Ngoc Lan Dalat", "19 Lam Vien Square, Ward 10, Da Lat", "P. 10", "Đà Lạt", 4, 160, "0263 382 0111", "https://ttcngoclanhotel.com", "TTC Hotel", "https://ttcngoclanhotel.com", False),
    # Hạ Long
    ("Vinpearl Resort & Spa Ha Long", "Đảo Rều, Bãi Cháy, TP. Hạ Long, Quảng Ninh", "Bãi Cháy", "Hạ Long", 5, 384, "0203 355 6868", "https://vinpearl.com", "Vinpearl Ha Long", "https://vinpearl.com", True),
    ("Wyndham Legend Halong", "12 Ha Long Street, Bai Chay Ward, Ha Long", "Bãi Cháy", "Hạ Long", 5, 217, "0203 363 8888", "https://www.wyndhamhalong.com", "Wyndham Legend Halong", "https://www.wyndhamhalong.com", True),
    ("Mường Thanh Grand Ha Long", "1048 Ha Long, Bai Chay, Ha Long City", "Bãi Cháy", "Hạ Long", 4, 318, "0203 384 2184", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", True),
    ("Novotel Ha Long Bay", "160 Ha Long Road, Bai Chay, Ha Long", "Bãi Cháy", "Hạ Long", 4, 225, "0203 384 0468", "https://www.novotelhalongbay.com", "Novotel Ha Long Bay", "https://www.novotelhalongbay.com", True),
    # Hội An
    ("Anantara Hoi An Resort", "1 Pham Hong Thai, Cam Chau, Hoi An", "Cẩm Châu", "Hội An", 5, 93, "0235 391 4555", "https://www.anantara.com/en/hoi-an", "Anantara Hoi An", "https://www.anantara.com", True),
    ("Hotel Royal Hoi An – MGallery", "39 Dao Duy Tu, Cam Pho, Hoi An", "Cẩm Phô", "Hội An", 5, 119, "0235 3955 555", "https://www.hotelroyalhoian.com", "Hotel Royal Hoi An", "https://www.hotelroyalhoian.com", False),
    ("Vinpearl Resort & Spa Nam Hoi An", "Binh Minh Commune, Thang Binh, Quang Nam", "Bình Minh", "Hội An", 5, 500, "0235 367 6888", "https://vinpearl.com", "Vinpearl Nam Hoi An", "https://vinpearl.com", True),
    ("Little Riverside Hoi An", "03 Phan Boi Chau, Minh An, Hoi An", "Minh An", "Hội An", 4, 30, "0235 392 1234", "https://littleriversidehoian.com", "Little Riverside", "https://littleriversidehoian.com", True),
    # Sa Pa
    ("Hotel de la Coupole – MGallery", "1 Hoang Lien Street, Sa Pa, Lao Cai", "Sa Pa", "Sa Pa", 5, 249, "0214 387 2222", "https://www.hoteldelacoupole.com", "Hotel de la Coupole", "https://www.hoteldelacoupole.com", False),
    ("Silk Path Grand Sapa Resort & Spa", "Doi Quan 6, Group 10, Sa Pa", "Sa Pa", "Sa Pa", 5, 120, "0214 387 8888", "https://silkpathhotel.com/sapa", "Silk Path Hospitality", "https://silkpathhotel.com", False),
    ("BB Hotel Sapa", "08 Cau May, Sa Pa Town, Lao Cai", "Sa Pa", "Sa Pa", 4, 75, "0214 387 9999", "https://bbhotelsapa.com", "BB Hotel Sapa", "https://bbhotelsapa.com", False),
    ("Sapa Clay House", "Ta Van Village, Sa Pa, Lao Cai", "Ta Van", "Sa Pa", 4, 15, "0214 387 6666", "https://sapaclayhouse.com", "Sapa Clay House", "https://sapaclayhouse.com", False),
    # Vũng Tàu
    ("Pullman Vung Tau", "15 Thi Sach, Thang Tam, Vung Tau", "Thắng Tam", "Vũng Tàu", 5, 241, "0254 355 7777", "https://www.pullmanvungtau.com", "Pullman Vung Tau", "https://www.pullmanvungtau.com", True),
    ("Imperial Hotel Vung Tau", "159 Thuy Van, Thang Tam, Vung Tau", "Thắng Tam", "Vũng Tàu", 5, 280, "0254 358 3588", "https://www.imperialhotel.vn/vung-tau", "Imperial Hotel Vung Tau", "https://www.imperialhotel.vn", True),
    ("Mường Thanh Holiday Vung Tau", "81 Thuy Van, Thang Tam, Vung Tau", "Thắng Tam", "Vũng Tàu", 4, 200, "0254 356 1111", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", True),
    # Phan Thiết / Mũi Né
    ("Anantara Mui Ne Resort", "Mui Ne Beach, Ham Tien, Phan Thiet", "Hàm Tiến", "Phan Thiết", 5, 89, "0252 384 8740", "https://www.anantara.com/en/mui-ne", "Anantara Mui Ne", "https://www.anantara.com", True),
    ("Pandanus Resort Mui Ne", "Block 5, Mui Ne, Phan Thiet", "Mũi Né", "Phan Thiết", 4, 134, "0252 384 1515", "https://www.pandanusresort.com", "Pandanus Resort", "https://www.pandanusresort.com", True),
    ("Victoria Phan Thiet Beach Resort", "109 Nguyen Dinh Chieu, Ham Tien", "Hàm Tiến", "Phan Thiết", 4, 57, "0252 384 3020", "https://www.victoriahotels.asia/phan-thiet", "Victoria Hotels", "https://www.victoriahotels.asia", True),
]

PRICE_BY_CITY = {
    "Hà Nội": {5: 2800000, 4: 1400000, 3: 900000},
    "TP.HCM": {5: 3000000, 4: 1500000, 3: 950000},
    "Huế": {5: 2200000, 4: 1000000, 3: 700000},
    "Phú Quốc": {5: 3500000, 4: 1800000, 3: 900000},
    "Đà Lạt": {5: 2000000, 4: 1100000, 3: 650000},
    "Hạ Long": {5: 2500000, 4: 1200000, 3: 750000},
    "Hội An": {5: 2800000, 4: 1300000, 3: 800000},
    "Sa Pa": {5: 4500000, 4: 2200000, 3: 1000000},
    "Vũng Tàu": {5: 2400000, 4: 1100000, 3: 700000},
    "Phan Thiết": {5: 2500000, 4: 1200000, 3: 750000},
}

REGION_ATTRACTIONS = [
    {"id": "a31", "name": "Văn Miếu – Quốc Tử Giám", "city": "Hà Nội", "ticketPrice": 30000, "tags": ["Di tích lịch sử", "Phù hợp gia đình", "Văn hóa"], "description": "Di tích Văn Miếu 58 Quốc Tử Giám. Vé tham quan ~30.000đ/khách (theo quy định Khu di tích).", "suggestedDuration": "1-2 giờ", "sourceName": "Khu di tích Văn Miếu", "sourceUrl": "https://vanmieu.gov.vn"},
    {"id": "a32", "name": "Hoàng thành Thăng Long", "city": "Hà Nội", "ticketPrice": 100000, "tags": ["Di sản UNESCO", "Lịch sử", "Phù hợp gia đình"], "description": "Di sản UNESCO 19C Hoàng Diệu. Vé tham quan khoảng 100.000đ.", "suggestedDuration": "2 giờ", "sourceName": "Hoàng thành Thăng Long", "sourceUrl": "https://hoangthanhthanglong.vn"},
    {"id": "a33", "name": "Lăng Chủ tịch Hồ Chí Minh", "city": "Hà Nội", "ticketPrice": 0, "tags": ["Miễn phí", "Lịch sử", "Tâm linh"], "description": "Quần thể Lăng Bác, Phố cổ Hồ Gươm. Miễn phí; cần trang phục lịch sự, xếp hàng sớm.", "suggestedDuration": "2-3 giờ"},
    {"id": "a34", "name": "Phố cổ Hà Nội & Hồ Hoàn Kiếm", "city": "Hà Nội", "ticketPrice": 0, "tags": ["Miễn phí", "Ẩm thực", "Check-in", "Buổi tối"], "description": "36 phố phường, hồ Hoàn Kiếm, đền Ngọc Sơn (vé đền ~30.000đ). Dạo phố miễn phí.", "suggestedDuration": "Nửa ngày - 1 ngày"},
    {"id": "a35", "name": "Bảo tàng Lịch sử Quân sự Việt Nam", "city": "Hà Nội", "ticketPrice": 40000, "tags": ["Bảo tàng", "Lịch sử", "Phù hợp gia đình"], "description": "28A Lê Trọng Tấn. Vé tham quan khoảng 40.000đ.", "suggestedDuration": "1-2 giờ"},
    {"id": "a36", "name": "Dinh Độc Lập", "city": "TP.HCM", "ticketPrice": 65000, "tags": ["Di tích lịch sử", "Phù hợp gia đình"], "description": "135 Nam Kỳ Khởi Nghĩa, Q.1. Vé tham quan ~65.000đ theo quy định di tích.", "suggestedDuration": "1-2 giờ", "sourceName": "Dinh Độc Lập", "sourceUrl": "https://dinhdoclaphcm.com.vn"},
    {"id": "a37", "name": "Bảo tàng Chứng tích Chiến tranh", "city": "TP.HCM", "ticketPrice": 40000, "tags": ["Bảo tàng", "Lịch sử", "Không phù hợp trẻ nhỏ"], "description": "28 Võ Văn Tần, Q.3. Vé ~40.000đ; nội dung nhạy cảm, cân nhắc trẻ nhỏ.", "suggestedDuration": "2 giờ", "sourceName": "War Remnants Museum", "sourceUrl": "https://baotangchungtichchientranh.vn"},
    {"id": "a38", "name": "Chợ Bến Thành", "city": "TP.HCM", "ticketPrice": 0, "tags": ["Miễn phí", "Ẩm thực", "Mua sắm"], "description": "Biểu tượng Sài Gòn, ẩm thực và quà lưu niệm. Không thu vé vào chợ.", "suggestedDuration": "1-2 giờ"},
    {"id": "a39", "name": "Landmark 81 & SkyView", "city": "TP.HCM", "ticketPrice": 300000, "tags": ["Check-in", "View cao", "Buổi tối"], "description": "Tòa nhà cao nhất VN, vé SkyView tham khảo từ ~300.000đ.", "suggestedDuration": "1-2 giờ", "priceNote": "Giá vé SkyView tham khảo theo Landmark 81."},
    {"id": "a40", "name": "Đại Nội Huế", "city": "Huế", "ticketPrice": 200000, "tags": ["Di sản UNESCO", "Lịch sử", "Phù hợp gia đình"], "description": "Kinh thành Huế. Vé tham quan khoảng 200.000đ (theo quy định Khu di tích cố đô).", "suggestedDuration": "Nửa ngày", "sourceName": "Khu di tích Cố đô Huế", "sourceUrl": "https://hueworldheritage.org.vn"},
    {"id": "a41", "name": "Lăng Khải Định", "city": "Huế", "ticketPrice": 150000, "tags": ["Di tích lịch sử", "Lịch sử"], "description": "Lăng vua Khải Định trên đồi Châu E. Vé khoảng 150.000đ.", "suggestedDuration": "1 giờ"},
    {"id": "a42", "name": "Sông Hương – Du thuyền ca nghe", "city": "Huế", "ticketPrice": 120000, "tags": ["Thiên nhiên", "Buổi tối", "Văn hóa"], "description": "Tour thuyền rồng nghe ca Huế buổi tối. Giá tham khảo ~120.000đ/người.", "suggestedDuration": "2 giờ", "priceNote": "Giá tour tham khảo."},
    {"id": "a43", "name": "VinWonders Phú Quốc", "city": "Phú Quốc", "ticketPrice": 950000, "tags": ["Phù hợp gia đình", "Vui chơi", "Công viên nước"], "description": "Công viên giải trí VinWonders Phú Quốc. Vé tiêu chuẩn tham khảo ~950.000đ người lớn (vinwonders.com).", "suggestedDuration": "1 ngày", "sourceName": "VinWonders", "sourceUrl": "https://vinwonders.com"},
    {"id": "a44", "name": "Bãi Sao Phú Quốc", "city": "Phú Quốc", "ticketPrice": 0, "tags": ["Miễn phí", "Bãi biển", "Tắm biển", "Phù hợp gia đình"], "description": "Một trong những bãi biển đẹp nhất Phú Quốc. Vào bãi miễn phí; chi phí dịch vụ riêng.", "suggestedDuration": "Nửa ngày"},
    {"id": "a45", "name": "Hòn Thơm – Cáp treo Hòn Thơm", "city": "Phú Quốc", "ticketPrice": 0, "tags": ["Cáp treo", "Check-in", "Phù hợp gia đình"], "description": "Cáp treo vượt biển dài nhất thế giới (theo công bố Sun Group). Giá cáp treo theo gói Sun World.", "suggestedDuration": "Nửa ngày", "sourceName": "Sun World Hon Thom", "sourceUrl": "https://sungroup.com.vn"},
    {"id": "a46", "name": "Hồ Xuân Hương & Chợ Đà Lạt", "city": "Đà Lạt", "ticketPrice": 0, "tags": ["Miễn phí", "Thiên nhiên", "Ẩm thực"], "description": "Trung tâm Đà Lạt, chợ đêm và hồ nước. Miễn phí tham quan ngoài trời.", "suggestedDuration": "Nửa ngày"},
    {"id": "a47", "name": "Datanla Falls (Thác Datanla)", "city": "Đà Lạt", "ticketPrice": 150000, "tags": ["Thiên nhiên", "Vui chơi", "Phù hợp gia đình"], "description": "Thác nước với máng trượt Alpine Coaster. Vé tham khảo ~150.000đ (chưa gồm coaster).", "suggestedDuration": "2-3 giờ", "sourceName": "Datanla New Alpine Coaster", "sourceUrl": "https://datanla.vn"},
    {"id": "a48", "name": "Crazy House (Ngôi nhà điên)", "city": "Đà Lạt", "ticketPrice": 60000, "tags": ["Kiến trúc", "Check-in"], "description": "03 Huỳnh Thúc Kháng. Vé vào cổng ~60.000đ.", "suggestedDuration": "1 giờ"},
    {"id": "a49", "name": "Langbiang Peak", "city": "Đà Lạt", "ticketPrice": 120000, "tags": ["Thiên nhiên", "Không phù hợp trẻ nhỏ", "Đường núi"], "description": "Đỉnh Langbiang 2167m, Jeep/trekking. Vé tham khảo ~120.000đ.", "suggestedDuration": "Nửa ngày"},
    {"id": "a50", "name": "Vịnh Hạ Long (hành trình VHL1)", "city": "Hạ Long", "ticketPrice": 310000, "tags": ["Di sản UNESCO", "Thuyền", "Phù hợp gia đình"], "description": "Phí tham quan VHL1: 250.000đ + phí cảng ~60.000đ ≈ 310.000đ/người (NQ HĐND Quảng Ninh 2025). Chưa gồm tiền tàu.", "suggestedDuration": "1 ngày", "sourceName": "Ban Quản lý Vịnh Hạ Long", "sourceUrl": "https://halongbay.com.vn", "priceNote": "Chưa bao gồm thuê tàu/ghép tàu."},
    {"id": "a51", "name": "Sung Sot Cave (Hang Sửng Sốt)", "city": "Hạ Long", "ticketPrice": 0, "tags": ["Hang động", "Thiên nhiên"], "description": "Nằm trong hành trình VHL; không bán vé riêng nếu đã mua hành trình vịnh.", "suggestedDuration": "1 giờ"},
    {"id": "a52", "name": "Sun World Fansipan Legend", "city": "Sa Pa", "ticketPrice": 750000, "tags": ["Cáp treo", "Thiên nhiên", "Không phù hợp trẻ nhỏ"], "description": "Cáp treo lên đỉnh Fansipan. Vé cáp treo khứ hồi tham khảo ~750.000đ người lớn (sunworld.vn).", "suggestedDuration": "Nửa ngày", "sourceName": "Sun World Fansipan", "sourceUrl": "https://sunworld.vn"},
    {"id": "a53", "name": "Bản Cát Cát", "city": "Sa Pa", "ticketPrice": 70000, "tags": ["Văn hóa", "Thiên nhiên", "Phù hợp gia đình"], "description": "Bản người H'Mông cách trung tâm Sa Pa ~3km. Vé tham quan ~70.000đ.", "suggestedDuration": "2-3 giờ"},
    {"id": "a54", "name": "Bãi Sau – Back Beach Vũng Tàu", "city": "Vũng Tàu", "ticketPrice": 0, "tags": ["Miễn phí", "Bãi biển", "Tắm biển"], "description": "Bãi biển phía nam Vũng Tàu, sóng mạnh hơn Bãi Trước. Miễn phí.", "suggestedDuration": "Nửa ngày"},
    {"id": "a55", "name": "Đồi cát đỏ Mũi Né", "city": "Phan Thiết", "ticketPrice": 100000, "tags": ["Thiên nhiên", "Check-in", "Không phù hợp trẻ nhỏ"], "description": "Đồi cát Mũi Né, trượt ván. Vé tham khảo ~100.000đ (tour/xe jeep).", "suggestedDuration": "2 giờ"},
    {"id": "a56", "name": "Làng chài Mũi Né", "city": "Phan Thiết", "ticketPrice": 0, "tags": ["Miễn phí", "Ẩm thực", "Biển"], "description": "Làng chài truyền thống, hải sản tươi. Không thu vé; chi phí ăn uống riêng.", "suggestedDuration": "1-2 giờ"},
    {"id": "a57", "name": "Bãi Đình – Bái Đính (Ninh Bình)", "city": "Ninh Bình", "ticketPrice": 150000, "tags": ["Tâm linh", "Phù hợp gia đình"], "description": "Quần thể chùa Bái Đính lớn nhất Việt Nam. Vé tham khảo ~150.000đ (có thể đi bộ/xe điện).", "suggestedDuration": "2-3 giờ"},
    {"id": "a58", "name": "Đền Hùng (Phú Thọ)", "city": "Phú Thọ", "ticketPrice": 0, "tags": ["Tâm linh", "Lịch sử", "Miễn phí"], "description": "Khu di tích lịch sử Đền Hùng. Miễn phí; đông dịp Giỗ Tổ 10/3 âm lịch.", "suggestedDuration": "Nửa ngày"},
]

REGION_TRANSPORT = [
    {"id": "t36", "type": "Máy bay", "from": "Hà Nội", "to": "TP.HCM", "provider": "Vietnam Airlines", "price": 1500000, "duration": "2h10", "bookingUrl": "https://vietnamairlines.com", "note": "Bay thẳng SGN-HAN, hành lý 23kg"},
    {"id": "t37", "type": "Máy bay", "from": "Hà Nội", "to": "TP.HCM", "provider": "VietJet Air", "price": 900000, "duration": "2h10", "bookingUrl": "https://vietjetair.com", "note": "Giá rẻ, nhiều chuyến/ngày"},
    {"id": "t38", "type": "Tàu hỏa", "from": "Hà Nội", "to": "TP.HCM", "provider": "Đường sắt Việt Nam", "price": 700000, "duration": "32h", "bookingUrl": "https://dsvn.vn", "note": "SE giường nằm điều hòa Bắc-Nam"},
    {"id": "t39", "type": "Máy bay", "from": "Hà Nội", "to": "Phú Quốc", "provider": "VietJet Air", "price": 1100000, "duration": "2h15", "bookingUrl": "https://vietjetair.com", "note": "Bay thẳng sân bay Phú Quốc"},
    {"id": "t40", "type": "Máy bay", "from": "TP.HCM", "to": "Phú Quốc", "provider": "Vietnam Airlines", "price": 950000, "duration": "1h", "bookingUrl": "https://vietnamairlines.com", "note": "Bay thẳng, nhiều chuyến"},
    {"id": "t41", "type": "Máy bay", "from": "TP.HCM", "to": "Đà Lạt", "provider": "VietJet Air", "price": 650000, "duration": "45 phút", "bookingUrl": "https://vietjetair.com", "note": "Bay sân bay Liên Khương"},
    {"id": "t42", "type": "Xe khách giường nằm", "from": "TP.HCM", "to": "Đà Lạt", "provider": "Phương Trang (FUTA)", "price": 290000, "duration": "7h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm điều hòa"},
    {"id": "t43", "type": "Máy bay", "from": "Hà Nội", "to": "Hạ Long", "provider": "Vietnam Airlines", "price": 800000, "duration": "45 phút", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Vân Đồn + taxi ~50km"},
    {"id": "t44", "type": "Xe Limousine", "from": "Hà Nội", "to": "Hạ Long", "provider": "Phúc Xuyên / Kumho", "price": 200000, "duration": "2h30", "bookingUrl": "https://vexere.com", "note": "Xe limousine Bến Mỹ Đình – Bãi Cháy"},
    {"id": "t45", "type": "Máy bay", "from": "Hà Nội", "to": "Huế", "provider": "Vietnam Airlines", "price": 850000, "duration": "1h10", "bookingUrl": "https://vietnamairlines.com", "note": "Bay sân bay Phú Bài"},
    {"id": "t46", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Huế", "provider": "Đường sắt Việt Nam", "price": 350000, "duration": "12h", "bookingUrl": "https://dsvn.vn", "note": "Giường nằm SE"},
    {"id": "t47", "type": "Máy bay", "from": "TP.HCM", "to": "Huế", "provider": "VietJet Air", "price": 900000, "duration": "1h20", "bookingUrl": "https://vietjetair.com", "note": "Bay Phú Bài"},
    {"id": "t48", "type": "Xe Limousine", "from": "Hà Nội", "to": "Sa Pa", "provider": "Sa Pa Express / HTX", "price": 350000, "duration": "6h", "bookingUrl": "https://vexere.com", "note": "Limousine đến Sa Pa (có cả đêm)"},
    {"id": "t49", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Lào Cai", "provider": "Đường sắt Việt Nam", "price": 280000, "duration": "8h", "bookingUrl": "https://dsvn.vn", "note": "Tàu tối + xe Sa Pa ~1h"},
    {"id": "t50", "type": "Xe khách", "from": "TP.HCM", "to": "Vũng Tàu", "provider": "Phương Trang (FUTA)", "price": 120000, "duration": "2h30", "bookingUrl": "https://futabus.vn", "note": "Xe giường/limousine"},
    {"id": "t51", "type": "Xe khách", "from": "TP.HCM", "to": "Phan Thiết", "provider": "Phương Trang (FUTA)", "price": 180000, "duration": "5h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm"},
    {"id": "t52", "type": "Máy bay", "from": "Đà Nẵng", "to": "Hà Nội", "provider": "Bamboo Airways", "price": 900000, "duration": "1h15", "bookingUrl": "https://bambooairways.com", "note": "Bay thẳng"},
    {"id": "t53", "type": "Máy bay", "from": "Đà Nẵng", "to": "TP.HCM", "provider": "VietJet Air", "price": 800000, "duration": "1h20", "bookingUrl": "https://vietjetair.com", "note": "Bay thẳng"},
    {"id": "t54", "type": "Máy bay", "from": "Hà Nội", "to": "Đà Lạt", "provider": "Vietnam Airlines", "price": 1000000, "duration": "1h50", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Liên Khương"},
    {"id": "t55", "type": "Xe Limousine", "from": "Đà Nẵng", "to": "Hội An", "provider": "Hội An Express", "price": 150000, "duration": "45 phút", "bookingUrl": "https://vexere.com", "note": "Đón trả trung tâm"},
    {"id": "t56", "type": "Máy bay", "from": "TP.HCM", "to": "Hà Nội", "provider": "Bamboo Airways", "price": 950000, "duration": "2h10", "bookingUrl": "https://bambooairways.com", "note": "Bay thẳng"},
    {"id": "t57", "type": "Máy bay", "from": "Nha Trang", "to": "Phú Quốc", "provider": "VietJet Air", "price": 700000, "duration": "1h30", "bookingUrl": "https://vietjetair.com", "note": "Bay nội địa Cam Ranh – Phú Quốc"},
    {"id": "t58", "type": "Tàu hỏa", "from": "TP.HCM", "to": "Huế", "provider": "Đường sắt Việt Nam", "price": 480000, "duration": "18h", "bookingUrl": "https://dsvn.vn", "note": "Giường nằm điều hòa"},
]


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.upper().strip())


def make_region_hotel(hid: str, row) -> dict:
    name, address, district, city, stars, rooms, phone, website, source_name, source_url, near_beach = row
    prices = PRICE_BY_CITY[city]
    tags = [f"{stars} sao", "Nguồn chính thống", "Giá tham khảo", "Phù hợp gia đình", city]
    if stars >= 5:
        tags.insert(4, "Cao cấp")
    if near_beach:
        tags.append("Gần biển")
    room_txt = f"Số phòng theo nguồn: {rooms}. " if rooms else ""
    desc = (
        f"Địa chỉ: {address}. Hạng chính thức: {stars} sao. Khu vực/quận: {district}. "
        f"{room_txt}Điện thoại: {phone}. Website: {website}. "
        f"Nguồn: {source_name}.{DESC_SUFFIX}"
    )
    return {
        "id": hid,
        "name": name,
        "city": city,
        "pricePerNight": prices[stars],
        "currency": "VND",
        "rating": float(stars),
        "image": IMAGES.get(stars, IMAGES[4]),
        "bookingUrl": website,
        "tags": tags,
        "description": desc,
        "address": address,
        "district": district,
        "officialStarRating": stars,
        "rooms": rooms,
        "phone": phone,
        "officialWebsite": website,
        "sourceName": source_name,
        "sourceUrl": source_url,
        "priceNote": PRICE_NOTE,
        "priceVerified": False,
    }


def make_attraction(item: dict) -> dict:
    base = {
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
    }
    return {**base, **item}


def main():
    hotels_path = DATA / "hotels.json"
    hotels = json.loads(hotels_path.read_text(encoding="utf-8"))
    existing = {normalize_name(h["name"]) for h in hotels}
    next_id = max(int(h["id"].lstrip("h")) for h in hotels) + 1
    added_h = 0
    for row in REGION_HOTELS:
        if normalize_name(row[0]) in existing:
            continue
        hotels.append(make_region_hotel(f"h{next_id:03d}", row))
        existing.add(normalize_name(row[0]))
        next_id += 1
        added_h += 1
    hotels_path.write_text(json.dumps(hotels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    attr_path = DATA / "attractions.json"
    attractions = json.loads(attr_path.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in attractions}
    # Fix Hoi An city on a4
    for a in attractions:
        if a["id"] == "a4":
            a["city"] = "Hội An"
    added_a = 0
    for item in REGION_ATTRACTIONS:
        if item["id"] not in existing_ids:
            attractions.append(make_attraction(item))
            existing_ids.add(item["id"])
            added_a += 1
    attr_path.write_text(json.dumps(attractions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    trans_path = DATA / "transport.json"
    transport = json.loads(trans_path.read_text(encoding="utf-8"))
    existing_t = {t["id"] for t in transport}
    added_t = 0
    for item in REGION_TRANSPORT:
        if item["id"] not in existing_t:
            transport.append(item)
            existing_t.add(item["id"])
            added_t += 1
    trans_path.write_text(json.dumps(transport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Hotels: +{added_h} (total {len(hotels)})")
    print(f"Attractions: +{added_a} (total {len(attractions)})")
    print(f"Transport: +{added_t} (total {len(transport)})")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Bổ sung tỉnh/thành lần 3 — Hà Giang, Tây Ninh, Phú Yên, Mekong, v.v."""
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

# name, address, district, city, stars, rooms, phone, website, sourceName, sourceUrl, near_beach
HOTELS_V3 = [
    # Hà Giang — hagiang.gov.vn / cổng DL
    ("Hoang Ngoc Hotel Ha Giang", "Số 1, Nguyễn Trãi, P. Nguyễn Trãi, TP. Hà Giang", "Nguyễn Trãi", "Hà Giang", 4, 80, "0219 3860 888", "https://hoangngochotel.com", "Hoang Ngoc Hotel", "https://hagiang.gov.vn", False),
    ("Auberge de Meo Vac", "Xã Mèo Vạc, Huyện Mèo Vạc, Hà Giang", "Mèo Vạc", "Hà Giang", 4, 20, "0219 3870 123", "https://aubergedemeovac.com", "Auberge de Meo Vac", "https://hagiang.gov.vn", False),
    ("Hmong Village Resort & Spa", "Xã Pả Vi, Huyện Mèo Vạc, Hà Giang", "Mèo Vạc", "Hà Giang", 4, 25, "0219 3871 999", "https://hmongvillageresort.com", "Hmong Village Resort", "https://hagiang.gov.vn", False),
    ("Phuong Dong Hotel Ha Giang", "176 Nguyễn Trãi, P. Nguyễn Trãi, TP. Hà Giang", "Nguyễn Trãi", "Hà Giang", 3, 60, "0219 3861 666", "https://phuongdonghotel.vn", "Phuong Dong Hotel", "https://hagiang.gov.vn", False),
    # Mai Châu — hoabinh.gov.vn
    ("Mai Chau Ecolodge", "Poom Coong Village, Mai Chau, Hoa Binh", "Mai Châu", "Mai Châu", 4, 40, "0218 3869 999", "https://maichau-ecolodge.com", "Mai Chau Ecolodge", "https://hoabinh.gov.vn", False),
    ("Sol Bungalows Mai Chau", "Na Thia Village, Mai Chau, Hoa Binh", "Mai Châu", "Mai Châu", 4, 18, "0218 3872 888", "https://solbungalows.com", "Sol Bungalows", "https://hoabinh.gov.vn", False),
    ("Avana Retreat Mai Chau", "Thung Nai, Cao Phong, Hoa Binh", "Cao Phong", "Mai Châu", 5, 36, "0218 3873 333", "https://avanaretreat.com", "Avana Retreat", "https://hoabinh.gov.vn", False),
    # Tam Đảo — vinhphuc.gov.vn
    ("Tam Dao Belvedere Resort", "Tam Dao Town, Vinh Phuc", "Tam Đảo", "Tam Đảo", 4, 120, "0211 3829 999", "https://tindaobelvedere.com", "Tam Dao Belvedere", "https://vinhphuc.gov.vn", False),
    ("Venus Tam Dao Hotel", "Tam Dao Town, Vinh Phuc", "Tam Đảo", "Tam Đảo", 4, 80, "0211 3828 888", "https://venustamdao.com", "Venus Tam Dao", "https://vinhphuc.gov.vn", False),
    ("Michlifen Golf & Country Club Tam Dao", "Tam Dao, Vinh Phuc", "Tam Đảo", "Tam Đảo", 5, 90, "0211 3827 777", "https://michlifen.com", "Michlifen Tam Dao", "https://vinhphuc.gov.vn", False),
    # Tây Ninh
    ("Nui Ba Den Hotel", "Black Virgin Mountain, Tay Ninh", "Tây Ninh", "Tây Ninh", 4, 100, "0276 3766 888", "https://nuibadenhotel.com", "Nui Ba Den Hotel", "https://tayninh.gov.vn", False),
    ("Long Hoa Hotel Tay Ninh", "30 CMT8, Tay Ninh City", "Tây Ninh", "Tây Ninh", 3, 70, "0276 3812 345", "https://longhoahotel.vn", "Long Hoa Hotel", "https://tayninh.gov.vn", False),
    ("Mường Thanh Luxury Tây Ninh", "Tay Ninh City, Tay Ninh Province", "Tây Ninh", "Tây Ninh", 5, 150, "0276 3811 111", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
    # Phú Yên — phuyentourism.gov.vn
    ("Ana Mandara Ayurveda Resort Phu Yen", "Bai Xep, Tuy Hoa, Phu Yen", "Tuy Hòa", "Phú Yên", 5, 45, "0257 3811 888", "https://anamandara.com/phu-yen", "Ana Mandara Phu Yen", "https://phuyentourism.gov.vn", True),
    ("Sala Tuy Hoa Beach Hotel", "Binh Ngoc Beach, Tuy Hoa, Phu Yen", "Tuy Hòa", "Phú Yên", 4, 120, "0257 3822 333", "https://salatuyhoabeach.com", "Sala Tuy Hoa", "https://phuyentourism.gov.vn", True),
    ("Mường Thanh Grand Phu Yen", "424 Tran Hung Dao, Tuy Hoa, Phu Yen", "Tuy Hòa", "Phú Yên", 5, 180, "0257 3813 666", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://phuyentourism.gov.vn", True),
    ("Casa Marina Hotel Phu Yen", "Binh Ngoc, Tuy Hoa, Phu Yen", "Tuy Hòa", "Phú Yên", 4, 60, "0257 3824 555", "https://casamarinahotel.vn", "Casa Marina Hotel", "https://phuyentourism.gov.vn", True),
    # Ninh Thuận — ninhthuantourism.vn
    ("Saigon Ninh Chu Hotel & Resort", "Ninh Chu Beach, Phan Rang, Ninh Thuan", "Phan Rang", "Ninh Thuận", 4, 150, "0259 3822 888", "https://saigonninhchu.com", "Saigon Ninh Chu", "https://ninhthuantourism.vn", True),
    ("Hoang Ha Hotel Phan Rang", "01 Thong Nhat, Phan Rang, Ninh Thuan", "Phan Rang", "Ninh Thuận", 4, 80, "0259 3823 456", "https://hoanghahotel.vn", "Hoang Ha Hotel", "https://ninhthuantourism.vn", False),
    ("Amiana Resort Ninh Thuan", "Bau Truc, Phan Rang, Ninh Thuan", "Phan Rang", "Ninh Thuận", 5, 70, "0259 3825 999", "https://amianaresort.com", "Amiana Resort", "https://ninhthuantourism.vn", True),
    # Nghệ An — nghean.gov.vn / Cửa Lò
    ("Muong Thanh Grand Cua Lo", "Cua Lo Beach, Nghe An", "Cửa Lò", "Nghệ An", 5, 200, "0238 3852 888", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://nghean.gov.vn", True),
    ("Vinpearl Hotel Cua Lo", "Cua Lo, Nghe An Province", "Cửa Lò", "Nghệ An", 5, 250, "0238 3853 333", "https://vinpearl.com", "Vinpearl Cua Lo", "https://nghean.gov.vn", True),
    ("Sai Gon Kim Lien Hotel Vinh", "26 Quang Trung, Vinh City, Nghe An", "Vinh", "Nghệ An", 4, 100, "0238 3855 555", "https://saigonkimlienhotel.com", "Sai Gon Kim Lien", "https://nghean.gov.vn", False),
    # Thanh Hóa — Sầm Sơn
    ("FLC Sầm Sơn Beach Golf & Luxury Resort", "Sam Son Beach, Thanh Hoa", "Sầm Sơn", "Thanh Hóa", 5, 350, "0237 3852 888", "https://flcsamson.com", "FLC Sam Son", "https://thanhhoa.gov.vn", True),
    ("Mường Thanh Grand Thanh Hoa", "Sam Son, Thanh Hoa", "Sầm Sơn", "Thanh Hóa", 5, 220, "0237 3853 666", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://thanhhoa.gov.vn", True),
    # Lý Sơn — quangngai.gov.vn
    ("Ly Son Hotel", "An Hai Commune, Ly Son Island, Quang Ngai", "Lý Sơn", "Lý Sơn", 3, 40, "0255 3876 888", "https://lysonhotel.vn", "Ly Son Hotel", "https://quangngai.gov.vn", True),
    ("Central Ly Son Hotel", "An Vinh, Ly Son Island, Quang Ngai", "Lý Sơn", "Lý Sơn", 3, 35, "0255 3877 999", "https://centrallysonhotel.com", "Central Ly Son Hotel", "https://quangngai.gov.vn", True),
    # Yên Bái / Mù Cang Chải
    ("Mù Cang Chải Ecolodge", "Lao Chai, Mu Cang Chai, Yen Bai", "Mù Cang Chải", "Yên Bái", 4, 15, "0216 3876 666", "https://mucangchaiecolodge.com", "Mu Cang Chai Ecolodge", "https://yenbai.gov.vn", False),
    ("Le Champ Tu Le Resort", "Tu Le, Van Chan, Yen Bai", "Văn Chấn", "Yên Bái", 4, 30, "0216 3877 777", "https://lechamptule.com", "Le Champ Tu Le", "https://yenbai.gov.vn", False),
    # Pleiku / Gia Lai
    ("Hoang Anh Gia Lai Hotel Pleiku", "1 Phu Dong, Pleiku, Gia Lai", "Pleiku", "Pleiku", 4, 120, "0269 3822 888", "https://hoanganhhotel.vn", "Hoang Anh Gia Lai", "https://gialai.gov.vn", False),
    ("Ana Mandara Villas Pleiku", "Bien Ho Lake Area, Pleiku, Gia Lai", "Pleiku", "Pleiku", 5, 20, "0269 3823 333", "https://anamandara-villas-pleiku.com", "Ana Mandara Villas", "https://gialai.gov.vn", False),
    # Hà Tiên — kiengiang.gov.vn
    ("Mường Thanh Hà Tiên", "Ha Tien Town, Kien Giang", "Hà Tiên", "Hà Tiên", 4, 130, "0297 3852 999", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://kiengiang.gov.vn", False),
    ("Ha Tien Vegas Hotel", "Ha Tien, Kien Giang", "Hà Tiên", "Hà Tiên", 4, 90, "0297 3853 888", "https://hatiencasino.com", "Ha Tien Vegas", "https://kiengiang.gov.vn", False),
    # Mỹ Tho / Tiền Giang
    ("Cuu Long Hotel My Tho", "30 30/4 Street, My Tho, Tien Giang", "Mỹ Tho", "Mỹ Tho", 4, 80, "0273 3822 333", "https://cuulonghotel.com", "Cuu Long Hotel", "https://tiengiang.gov.vn", False),
    ("Mekong Riverside Boutique My Tho", "My Tho, Tien Giang", "Mỹ Tho", "Mỹ Tho", 4, 25, "0273 3823 444", "https://mekongriverside.vn", "Mekong Riverside", "https://tiengiang.gov.vn", False),
    # Bến Tre
    ("Ben Tre Riverside Resort", "Ham Luong River, Ben Tre City", "Bến Tre", "Bến Tre", 4, 50, "0275 3822 555", "https://bentreriverside.com", "Ben Tre Riverside", "https://bentre.gov.vn", False),
    # Cà Mau
    ("Muong Thanh Luxury Ca Mau", "Ca Mau City, Ca Mau Province", "Cà Mau", "Cà Mau", 5, 150, "0290 3833 888", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://camau.gov.vn", False),
    ("Hai Au Hotel Ca Mau", "Ca Mau City, Ca Mau Province", "Cà Mau", "Cà Mau", 4, 70, "0290 3834 666", "https://haiauhotel.vn", "Hai Au Hotel", "https://camau.gov.vn", False),
    # Cao Bằng
    ("Saigon-Ban Me Hotel Cao Bang", "Cao Bang City, Cao Bang Province", "Cao Bằng", "Cao Bằng", 4, 80, "0206 3852 888", "https://saigonbanmehotel.vn", "Saigon Ban Me Hotel", "https://caobang.gov.vn", False),
    ("Primrose Homestay Cao Bang", "Near Ban Gioc, Cao Bang", "Trùng Khánh", "Cao Bằng", 3, 12, "0206 3853 777", "https://primrosehomestay.com", "Primrose Homestay", "https://caobang.gov.vn", False),
    # Bổ sung Ninh Bình
    ("Emeralda Resort Ninh Binh", "Van Long Nature Reserve, Gia Van, Ninh Binh", "Gia Viên", "Ninh Bình", 5, 172, "0229 3668 888", "https://emeraldaresort.com", "Emeralda Resort", "https://dulichninhbinh.com.vn", False),
    ("Ninh Binh Hidden Charm Hotel & Resort", "Noi Bai – Ninh Binh Road, Ninh Binh", "Hoa Lư", "Ninh Bình", 4, 60, "0229 3669 999", "https://ninhbinhhiddencharm.com", "Hidden Charm", "https://dulichninhbinh.com.vn", False),
]

PRICE_BY_CITY = {
    "Hà Giang": {5: 1800000, 4: 900000, 3: 550000},
    "Mai Châu": {5: 2200000, 4: 1100000, 3: 650000},
    "Tam Đảo": {5: 2500000, 4: 1200000, 3: 700000},
    "Tây Ninh": {5: 2000000, 4: 950000, 3: 600000},
    "Phú Yên": {5: 2400000, 4: 1100000, 3: 700000},
    "Ninh Thuận": {5: 2200000, 4: 1000000, 3: 650000},
    "Nghệ An": {5: 2200000, 4: 1000000, 3: 650000},
    "Thanh Hóa": {5: 2300000, 4: 1100000, 3: 700000},
    "Lý Sơn": {5: 2000000, 4: 900000, 3: 500000},
    "Yên Bái": {5: 2000000, 4: 950000, 3: 600000},
    "Pleiku": {5: 1900000, 4: 900000, 3: 550000},
    "Hà Tiên": {5: 2100000, 4: 1000000, 3: 650000},
    "Mỹ Tho": {5: 1800000, 4: 850000, 3: 550000},
    "Bến Tre": {5: 1700000, 4: 800000, 3: 500000},
    "Cà Mau": {5: 2000000, 4: 950000, 3: 600000},
    "Cao Bằng": {5: 1800000, 4: 850000, 3: 500000},
    "Ninh Bình": {5: 2600000, 4: 1200000, 3: 750000},
}

ATTRACTIONS_V3 = [
    # Ninh Bình — dulichninhbinh.com.vn
    {"id": "a78", "name": "Khu du lịch sinh thái Tràng An", "city": "Ninh Bình", "ticketPrice": 300000,
     "tags": ["Di sản UNESCO", "Thuyền", "Phù hợp gia đình", "Giá niêm yết"],
     "description": "Vé người lớn >1,3m: 300.000đ; trẻ 1m–1,3m: 150.000đ; <1m miễn phí. Đã gồm đò và phí danh lam (TT Xúc tiến DL Ninh Bình).",
     "suggestedDuration": "3-4 giờ", "sourceName": "Trung tâm Xúc tiến du lịch Ninh Bình",
     "sourceUrl": "https://dulichninhbinh.com.vn", "priceNote": "Giá vé chính thức tuyến 1–4; tuyến Khê Cốc có thể khác."},
    {"id": "a79", "name": "Tam Cốc – Bích Động", "city": "Ninh Bình", "ticketPrice": 250000,
     "tags": ["Thiên nhiên", "Thuyền", "Phù hợp gia đình"],
     "description": "Vé tham quan Tam Cốc tham khảo ~250.000đ người lớn (đã gồm đò). Bích Động có thể tham quan riêng.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Trung tâm Xúc tiến du lịch Ninh Bình",
     "sourceUrl": "https://dulichninhbinh.com.vn"},
    {"id": "a80", "name": "Khu du lịch sinh thái Vân Long", "city": "Ninh Bình", "ticketPrice": 200000,
     "tags": ["Thiên nhiên", "Thuyền", "Chim"],
     "description": "Khu bảo tồn Vân Long (Gia Viên). Vé thuyền + cổng tham khảo ~200.000đ/người.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Emeralda / Vân Long", "sourceUrl": "https://dulichninhbinh.com.vn"},
    # Hà Giang
    {"id": "a81", "name": "Cột cờ Lũng Cú", "city": "Hà Giang", "ticketPrice": 50000,
     "tags": ["Check-in", "Lịch sử", "Phù hợp gia đình"],
     "description": "Điểm cực Bắc Việt Nam, xã Lũng Cú. Vé tham khảo ~50.000đ; cần giấy tờ xin phép biên giới.",
     "suggestedDuration": "1-2 giờ", "sourceName": "Cổng thông tin Hà Giang", "sourceUrl": "https://hagiang.gov.vn",
     "priceNote": "Một số khu vực biên giới cần đăng ký trước."},
    {"id": "a82", "name": "Đèo Mã Pí Lèng", "city": "Hà Giang", "ticketPrice": 0,
     "tags": ["Miễn phí", "Thiên nhiên", "Check-in", "Không phù hợp trẻ nhỏ"],
     "description": "Một trong tứ đại đỉnh đèo phía Bắc. Không thu vé; chi phí xe/thuê xe riêng.",
     "suggestedDuration": "1-2 giờ"},
    {"id": "a83", "name": "Phố cổ Đồng Văn", "city": "Hà Giang", "ticketPrice": 0,
     "tags": ["Miễn phí", "Văn hóa", "Chợ phiên"],
     "description": "Phố cổ đá trên cao nguyên đá Đồng Văn. Miễn phí; chợ phiên Chủ nhật nổi tiếng.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Cổng thông tin Hà Giang", "sourceUrl": "https://hagiang.gov.vn"},
    # Tây Ninh — sunworld.vn
    {"id": "a84", "name": "Sun World Ba Den Mountain", "city": "Tây Ninh", "ticketPrice": 410000,
     "tags": ["Cáp treo", "Tâm linh", "Phù hợp gia đình"],
     "description": "Phí vào cổng 10.000đ + cáp treo đỉnh Vân Sơn khứ hồi 400.000đ người lớn (>1,4m) — sunworld.vn (2025).",
     "suggestedDuration": "Nửa ngày", "sourceName": "Sun World Ba Den Mountain", "sourceUrl": "https://sunworld.vn",
     "priceNote": "Chưa gồm combo Chùa Hang/buffet; giá tham khảo mức công bố."},
    {"id": "a85", "name": "Tòa Thánh Cao Đài", "city": "Tây Ninh", "ticketPrice": 0,
     "tags": ["Tâm linh", "Miễn phí", "Kiến trúc"],
     "description": "Long Hoa, Hòa Thành. Miễn phí; cần trang phục lịch sự, lễ truyền 12h trưa hàng ngày.",
     "suggestedDuration": "1-2 giờ", "sourceName": "Tây Ninh Tourism", "sourceUrl": "https://tayninh.gov.vn"},
    # Phú Yên — phuyentourism.gov.vn
    {"id": "a86", "name": "Gành Đá Dĩa", "city": "Phú Yên", "ticketPrice": 40000,
     "tags": ["Di tích quốc gia", "Check-in", "Phù hợp gia đình"],
     "description": "Di tích QG đặc biệt, xã An Ninh Đông (Tuy An). Vé 40.000đ/người/lượt, đã gồm bảo hiểm (NQ HĐND Phú Yên 2023).",
     "suggestedDuration": "1 giờ", "sourceName": "Sở Du lịch Phú Yên", "sourceUrl": "https://phuyentourism.gov.vn"},
    {"id": "a87", "name": "Bãi Môn – Mũi Điện", "city": "Phú Yên", "ticketPrice": 30000,
     "tags": ["Biển", "Check-in", "Phù hợp gia đình"],
     "description": "Mũi cực Đông Việt Nam (Đông Hòa). Vé tham quan 30.000đ/người/lần theo NQ HĐND Phú Yên.",
     "suggestedDuration": "1-2 giờ", "sourceName": "Sở Du lịch Phú Yên", "sourceUrl": "https://phuyentourism.gov.vn"},
    {"id": "a88", "name": "Bãi Xép – Đá Bia", "city": "Phú Yên", "ticketPrice": 0,
     "tags": ["Miễn phí", "Biển", "Check-in"],
     "description": "Bãi biển hoang sơ gần Tuy Hòa. Không thu vé cổng; chi phí di chuyển riêng.",
     "suggestedDuration": "2-3 giờ"},
    # Ninh Thuận
    {"id": "a89", "name": "Tháp Po Klong Garai", "city": "Ninh Thuận", "ticketPrice": 30000,
     "tags": ["Di tích", "Văn hóa Chăm", "Phù hợp gia đình"],
     "description": "Tháp Chăm thế kỷ XIII tại Phan Rang. Vé tham khảo ~30.000đ.",
     "suggestedDuration": "1 giờ", "sourceName": "Ninh Thuận Tourism", "sourceUrl": "https://ninhthuantourism.vn"},
    {"id": "a90", "name": "Vườn nho Ninh Thuận", "city": "Ninh Thuận", "ticketPrice": 0,
     "tags": ["Ẩm thực", "Miễn phí", "Phù hợp gia đình"],
     "description": "Tham quan vườn nho và làng nho truyền thống. Không vé cổng cố định; chi phí ăn uống/mua nho riêng.",
     "suggestedDuration": "2-3 giờ"},
    # Nghệ An
    {"id": "a91", "name": "Biển Cửa Lò", "city": "Nghệ An", "ticketPrice": 0,
     "tags": ["Miễn phí", "Bãi biển", "Tắm biển"],
     "description": "Bãi biển nổi tiếng miền Trung. Miễn phí vào bãi.",
     "suggestedDuration": "Nửa ngày"},
    {"id": "a92", "name": "Quê Bác Hồ – Kim Liên", "city": "Nghệ An", "ticketPrice": 0,
     "tags": ["Lịch sử", "Miễn phí", "Phù hợp gia đình"],
     "description": "Khu di tích Kim Liên, Nam Đàn. Miễn phí tham quan quần thể di tích.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Khu di tích Kim Liên", "sourceUrl": "https://nghean.gov.vn"},
    # Thanh Hóa
    {"id": "a93", "name": "Biển Sầm Sơn", "city": "Thanh Hóa", "ticketPrice": 0,
     "tags": ["Miễn phí", "Bãi biển", "Phù hợp gia đình"],
     "description": "Bãi biển trung tâm Thanh Hóa. Miễn phí; dịch vụ tắm biển/ăn uống riêng.",
     "suggestedDuration": "Nửa ngày"},
    {"id": "a94", "name": "Thành nhà Hồ – Tây Giai", "city": "Thanh Hóa", "ticketPrice": 40000,
     "tags": ["Di sản UNESCO", "Lịch sử"],
     "description": "Di sản thế giới Thành nhà Hồ (Vĩnh Lộc). Vé tham khảo ~40.000đ.",
     "suggestedDuration": "2 giờ", "sourceName": "Thành nhà Hồ", "sourceUrl": "https://thanhhoa.gov.vn"},
    # Lý Sơn
    {"id": "a95", "name": "Cổng Tò – Hang Câu (Lý Sơn)", "city": "Lý Sơn", "ticketPrice": 0,
     "tags": ["Biển đảo", "Check-in", "Miễn phí"],
     "description": "Đảo tiêu Lý Sơn. Không vé cổng; cần phí phà/tàu cao tốc từ Quảng Ngãi (~200.000–350.000đ/khứ).",
     "suggestedDuration": "1 ngày", "priceNote": "Chi phí phà/tàu riêng, không phải vé tham quan."},
    # Yên Bái
    {"id": "a96", "name": "Ruộng bậc thang Mù Cang Chải", "city": "Yên Bái", "ticketPrice": 0,
     "tags": ["Miễn phí", "Thiên nhiên", "Check-in"],
     "description": "Mùa nước đổ (9–10) và mùa lúa chín (9–10) đẹp nhất. Không thu vé; chi phí homestay/xe riêng.",
     "suggestedDuration": "1-2 ngày"},
    {"id": "a97", "name": "Suối khoáng nóng Trạm Tấu", "city": "Yên Bái", "ticketPrice": 50000,
     "tags": ["Thiên nhiên", "Nghỉ dưỡng"],
     "description": "Khu suối khoáng Trạm Tấu (Văn Chấn). Vé tắm khoáng tham khảo ~50.000đ.",
     "suggestedDuration": "Nửa ngày"},
    # Mekong
    {"id": "a98", "name": "Chợ nổi Cái Bè", "city": "Mỹ Tho", "ticketPrice": 0,
     "tags": ["Miễn phí", "Văn hóa sông nước", "Buổi sáng"],
     "description": "Chợ nổi lớn Tiền Giang. Không vé cổng; thuê ghe ~150.000–250.000đ/ghe.",
     "suggestedDuration": "2-3 giờ", "priceNote": "Chi phí thuê ghe tham khảo."},
    {"id": "a99", "name": "Cồn Phụng (Bến Tre)", "city": "Bến Tre", "ticketPrice": 50000,
     "tags": ["Văn hóa sông nước", "Ẩm thực", "Phù hợp gia đình"],
     "description": "Du lịch cồn dừa Bến Tre. Phí phà/xe điện tham khảo ~50.000đ; dịch vụ ăn uống riêng.",
     "suggestedDuration": "Nửa ngày", "sourceName": "Bến Tre Tourism", "sourceUrl": "https://bentre.gov.vn"},
    {"id": "a100", "name": "Mũi Cà Mau", "city": "Cà Mau", "ticketPrice": 0,
     "tags": ["Miễn phí", "Check-in", "Thiên nhiên"],
     "description": "Điểm cực Nam Việt Nam. Miễn phí; có thể thu phí đi lại/xe điện trong khu (~30.000đ).",
     "suggestedDuration": "2-3 giờ", "sourceName": "Cà Mau Tourism", "sourceUrl": "https://camau.gov.vn"},
    # Cao Bằng
    {"id": "a101", "name": "Thác Bản Giốc", "city": "Cao Bằng", "ticketPrice": 45000,
     "tags": ["Thiên nhiên", "Thác nước", "Phù hợp gia đình"],
     "description": "Thác Bản Giốc, Trùng Khánh. Vé tham quan tham khảo ~45.000đ; thuyền ngắm cận cảnh tính riêng.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Cao Bằng Tourism", "sourceUrl": "https://caobang.gov.vn",
     "priceNote": "Phí thuyền/đi lại biên giới tính riêng."},
    {"id": "a102", "name": "Hang Pác Bó – Suối Lê Nin", "city": "Cao Bằng", "ticketPrice": 0,
     "tags": ["Lịch sử", "Miễn phí"],
     "description": "Di tích lịch sử Hà Quảng. Miễn phí tham quan khu di tích.",
     "suggestedDuration": "1-2 giờ"},
    # Mai Châu / Tam Đảo
    {"id": "a103", "name": "Bản Lác – Mai Châu", "city": "Mai Châu", "ticketPrice": 0,
     "tags": ["Miễn phí", "Văn hóa", "Homestay"],
     "description": "Bản Thái truyền thống. Miễn phí; chi phí homestay/ẩm thực riêng.",
     "suggestedDuration": "1 ngày"},
    {"id": "a104", "name": "Thác Bạc – Thác Bạc Tam Đảo", "city": "Tam Đảo", "ticketPrice": 80000,
     "tags": ["Thiên nhiên", "Thác nước"],
     "description": "Thác Bạc cách trung tâm Tam Đảo ~3km. Vé tham khảo ~80.000đ (có thể đi bộ hoặc xe ôm).",
     "suggestedDuration": "1-2 giờ"},
    # Hà Tiên
    {"id": "a105", "name": "Mũi Nai – Chùa Hang Hà Tiên", "city": "Hà Tiên", "ticketPrice": 0,
     "tags": ["Tâm linh", "Miễn phí", "Check-in"],
     "description": "Quần thể núi Mũi Nai ven biển Kiên Giang. Miễn phí vào chùa; leo núi miễn phí.",
     "suggestedDuration": "1-2 giờ"},
    # Hội An bổ sung
    {"id": "a106", "name": "Bãi biển An Bàng", "city": "Hội An", "ticketPrice": 0,
     "tags": ["Miễn phí", "Bãi biển", "Tắm biển"],
     "description": "Bãi biển cách phố cổ ~5km. Miễn phí; một số quán tính phí ghế (~30.000–50.000đ).",
     "suggestedDuration": "Nửa ngày"},
    {"id": "a107", "name": "Cù Lao Chàm", "city": "Hội An", "ticketPrice": 150000,
     "tags": ["Biển đảo", "Lặn biển", "Phù hợp gia đình"],
     "description": "Đảo Cù Lao Chàm (Hội An). Tour cano khứ hồi + bảo tồn biển tham khảo ~150.000–300.000đ.",
     "suggestedDuration": "1 ngày", "priceNote": "Giá tour/canô tham khảo, không phải vé cổng cố định."},
]

TRANSPORT_V3 = [
    {"id": "t77", "type": "Xe Limousine", "from": "Hà Nội", "to": "Hà Giang", "provider": "Hà Giang Express", "price": 350000, "duration": "6h", "bookingUrl": "https://vexere.com", "note": "Limousine đến TP. Hà Giang"},
    {"id": "t78", "type": "Xe khách", "from": "Hà Nội", "to": "Mai Châu", "provider": "Phương Trang (FUTA)", "price": 150000, "duration": "3h30", "bookingUrl": "https://futabus.vn", "note": "Xe đến Mai Châu/Hòa Bình"},
    {"id": "t79", "type": "Xe khách", "from": "Hà Nội", "to": "Tam Đảo", "provider": "Kumho Samco", "price": 100000, "duration": "2h", "bookingUrl": "https://vexere.com", "note": "Xe đến thị trấn Tam Đảo"},
    {"id": "t80", "type": "Xe khách", "from": "TP.HCM", "to": "Tây Ninh", "provider": "Phương Trang (FUTA)", "price": 80000, "duration": "2h", "bookingUrl": "https://futabus.vn", "note": "Xe đến TP. Tây Ninh"},
    {"id": "t81", "type": "Máy bay", "from": "TP.HCM", "to": "Phú Yên", "provider": "VietJet Air", "price": 750000, "duration": "1h10", "bookingUrl": "https://vietjetair.com", "note": "Bay sân bay Tuy Hòa"},
    {"id": "t82", "type": "Máy bay", "from": "Hà Nội", "to": "Phú Yên", "provider": "Vietnam Airlines", "price": 950000, "duration": "1h40", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Tuy Hòa"},
    {"id": "t83", "type": "Máy bay", "from": "TP.HCM", "to": "Ninh Thuận", "provider": "VietJet Air", "price": 700000, "duration": "1h", "bookingUrl": "https://vietjetair.com", "note": "Bay Cam Ranh + xe ~1h đến Phan Rang"},
    {"id": "t84", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Nghệ An", "provider": "Đường sắt Việt Nam", "price": 320000, "duration": "5h", "bookingUrl": "https://dsvn.vn", "note": "Ga Vinh"},
    {"id": "t85", "type": "Máy bay", "from": "Hà Nội", "to": "Nghệ An", "provider": "VietJet Air", "price": 600000, "duration": "50 phút", "bookingUrl": "https://vietjetair.com", "note": "Bay sân bay Vinh"},
    {"id": "t86", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Thanh Hóa", "provider": "Đường sắt Việt Nam", "price": 280000, "duration": "4h", "bookingUrl": "https://dsvn.vn", "note": "Ga Thanh Hóa + taxi Sầm Sơn"},
    {"id": "t87", "type": "Tàu cao tốc", "from": "Quảng Ngãi", "to": "Lý Sơn", "provider": "Superdong / Phà Lý Sơn", "price": 250000, "duration": "30 phút", "bookingUrl": "https://superdong.com.vn", "note": "Tàu cao tốc Sa Kỳ – Lý Sơn"},
    {"id": "t88", "type": "Xe khách", "from": "Hà Nội", "to": "Yên Bái", "provider": "Phương Trang (FUTA)", "price": 200000, "duration": "4h", "bookingUrl": "https://futabus.vn", "note": "Đến Yên Bái + xe Mù Cang Chải ~3h"},
    {"id": "t89", "type": "Máy bay", "from": "TP.HCM", "to": "Pleiku", "provider": "VietJet Air", "price": 800000, "duration": "1h", "bookingUrl": "https://vietjetair.com", "note": "Bay sân bay Pleiku"},
    {"id": "t90", "type": "Xe khách", "from": "TP.HCM", "to": "Hà Tiên", "provider": "Phương Trang (FUTA)", "price": 180000, "duration": "6h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm"},
    {"id": "t91", "type": "Xe khách", "from": "TP.HCM", "to": "Mỹ Tho", "provider": "Phương Trang (FUTA)", "price": 80000, "duration": "1h30", "bookingUrl": "https://futabus.vn", "note": "Xe đến Mỹ Tho/Tiền Giang"},
    {"id": "t92", "type": "Xe khách", "from": "TP.HCM", "to": "Cà Mau", "provider": "Phương Trang (FUTA)", "price": 250000, "duration": "6h30", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm"},
    {"id": "t93", "type": "Xe Limousine", "from": "Hà Nội", "to": "Cao Bằng", "provider": "Cao Bang Express", "price": 400000, "duration": "8h", "bookingUrl": "https://vexere.com", "note": "Limousine đến TP. Cao Bằng"},
    {"id": "t94", "type": "Máy bay", "from": "Hà Nội", "to": "Ninh Bình", "provider": "Vietnam Airlines", "price": 700000, "duration": "45 phút", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Nội Bài + xe ~1h30 (hoặc tàu/taxi)"},
    {"id": "t95", "type": "Xe Limousine", "from": "Hà Nội", "to": "Ninh Bình", "provider": "Ninh Binh Limousine", "price": 150000, "duration": "1h30", "bookingUrl": "https://vexere.com", "note": "Limousine đón trung tâm Hà Nội"},
    {"id": "t96", "type": "Máy bay", "from": "Đà Nẵng", "to": "Phú Yên", "provider": "VietJet Air", "price": 600000, "duration": "50 phút", "bookingUrl": "https://vietjetair.com", "note": "Bay Tuy Hòa"},
    {"id": "t97", "type": "Xe khách", "from": "TP.HCM", "to": "Bến Tre", "provider": "Phương Trang (FUTA)", "price": 90000, "duration": "2h", "bookingUrl": "https://futabus.vn", "note": "Xe đến Bến Tre"},
]

PATCHES = {
    "hotels": [],
    "attractions": [],
}


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.upper().strip())


def make_hotel(hid: str, row) -> dict:
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


def apply_patches(hotels, attractions):
    for h in hotels:
        for p in PATCHES.get("hotels", []):
            if "match_name" not in p:
                continue
            if normalize_name(h["name"]) != normalize_name(p["match_name"]):
                continue
            if "address" in p:
                h["address"] = p["address"]
            if "description" in p:
                h["description"] = p["description"]
            else:
                h.update({k: v for k, v in p.items() if k not in ("match_name", "address", "description")})
    for a in attractions:
        for p in PATCHES.get("attractions", []):
            if "id" not in p or a["id"] != p["id"]:
                continue
            a.update({k: v for k, v in p.items() if k != "id"})
    return hotels, attractions


def main():
    hotels_path = DATA / "hotels.json"
    hotels = json.loads(hotels_path.read_text(encoding="utf-8"))
    existing = {normalize_name(h["name"]) for h in hotels}
    next_h = max(int(h["id"].lstrip("h")) for h in hotels) + 1
    added_h = 0
    for row in HOTELS_V3:
        if normalize_name(row[0]) in existing:
            continue
        hotels.append(make_hotel(f"h{next_h:03d}", row))
        existing.add(normalize_name(row[0]))
        next_h += 1
        added_h += 1

    attr_path = DATA / "attractions.json"
    attractions = json.loads(attr_path.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in attractions}
    added_a = 0
    for item in ATTRACTIONS_V3:
        if item["id"] in existing_ids:
            continue
        base = {"currency": "VND", "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"}
        attractions.append({**base, **item})
        existing_ids.add(item["id"])
        added_a += 1

    trans_path = DATA / "transport.json"
    transport = json.loads(trans_path.read_text(encoding="utf-8"))
    existing_t = {t["id"] for t in transport}
    added_t = 0
    for item in TRANSPORT_V3:
        if item["id"] not in existing_t:
            transport.append(item)
            existing_t.add(item["id"])
            added_t += 1

    hotels, attractions = apply_patches(hotels, attractions)

    hotels_path.write_text(json.dumps(hotels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    attr_path.write_text(json.dumps(attractions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    trans_path.write_text(json.dumps(transport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Hotels: +{added_h} (total {len(hotels)})")
    print(f"Attractions: +{added_a} (total {len(attractions)})")
    print(f"Transport: +{added_t} (total {len(transport)})")


if __name__ == "__main__":
    main()

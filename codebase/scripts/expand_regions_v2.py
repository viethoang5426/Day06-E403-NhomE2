# -*- coding: utf-8 -*-
"""Bổ sung tỉnh/thành mới + sửa giá/địa chỉ theo nguồn chính thống."""
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
HOTELS_V2 = [
    # Cần Thơ — canthotourism.vn; UBND TP: 3 khách sạn 5 sao (TTC, Mường Thanh Luxury, Sheraton)
    ("TTC Hotel – Cần Thơ", "Số 118 Nguyễn Văn Cừ, P. An Bình, TP. Cần Thơ", "Ninh Kiều", "Cần Thơ", 5, 108, "0292 305 8888", "https://ttchotel.vn/hotel/can-tho", "Cổng thông tin du lịch Cần Thơ", "https://canthotourism.vn/vi/hotels", False),
    ("Sheraton Cần Thơ", "209 Đường 30/4, P. Ninh Kiều, TP. Cần Thơ", "Ninh Kiều", "Cần Thơ", 5, 153, "0292 376 8888", "https://www.marriott.com/en-us/hotels/vcasi-sheraton-can-tho/overview/", "Cổng thông tin du lịch Cần Thơ", "https://canthotourism.vn/vi/hotels", False),
    ("Mường Thanh Luxury Cần Thơ", "E1 Cồn Cái Khế, P. Cái Khế, TP. Cần Thơ", "Ninh Kiều", "Cần Thơ", 5, 200, "0292 381 1111", "https://muongthanh.vn", "Cổng thông tin du lịch Cần Thơ", "https://canthotourism.vn/vi/hotels", False),
    ("Victoria Cần Thơ Resort", "Cai Khe Ward, Ninh Kieu District, Can Tho", "Cái Khế", "Cần Thơ", 4, 92, "0292 381 0111", "https://www.victoriahotels.asia/can-tho", "Cổng thông tin du lịch Cần Thơ", "https://canthotourism.vn/vi/hotels", False),
    ("Khách sạn Ninh Kiều Riverside", "2 Ngô Quyền, P. An Phú, TP. Cần Thơ", "Ninh Kiều", "Cần Thơ", 4, 120, "0292 381 2345", "https://ninhkieuriversidehotel.com", "Cổng thông tin du lịch Cần Thơ", "https://canthotourism.vn/vi/hotels", False),
    # Quảng Bình — phongnhatourism.com.vn
    ("Sun Spa Resort Quảng Bình", "Bao Ninh Beach, Dong Hoi City, Quang Binh", "Bảo Ninh", "Quảng Bình", 5, 260, "0232 3842 999", "https://sunsparesortquangbinh.com", "Sun Spa Resort", "https://sunsparesortquangbinh.com", True),
    ("Royal Quảng Bình Hotel", "Quang Phu, Dong Hoi, Quang Binh", "Đồng Hới", "Quảng Bình", 4, 120, "0232 3822 222", "https://royalquangbinhhotel.com", "Royal Quảng Bình", "https://royalquangbinhhotel.com", False),
    ("Mường Thanh Luxury Quảng Bình", "Quang Phu, Dong Hoi, Quang Binh", "Đồng Hới", "Quảng Bình", 5, 180, "0232 3823 666", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
    # Quy Nhơn — Bình Định
    ("Avani Quy Nhon Resort & Spa", "Ghenh Rang, Quy Nhon, Binh Dinh", "Ghềnh Ráng", "Quy Nhơn", 5, 63, "0256 3841 333", "https://www.avanihotels.com/quy-nhon", "Avani Hotels", "https://www.avanihotels.com", True),
    ("FLC Luxury Hotel Quy Nhon", "11 An Duong Vuong, Quy Nhon, Binh Dinh", "Nguyễn Văn Cừ", "Quy Nhơn", 5, 600, "0256 3948 888", "https://flcquynhon.com", "FLC Hotels", "https://flcquynhon.com", True),
    ("Mường Thanh Quy Nhơn", "24 Nguyễn Huế, Quy Nhon, Binh Dinh", "Lê Lợi", "Quy Nhơn", 4, 150, "0256 3812 345", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", True),
    ("Rex Hotel Quy Nhon", "01 Nguyen Hue, Quy Nhon, Binh Dinh", "Lê Lợi", "Quy Nhơn", 4, 80, "0256 3822 283", "https://rexhotelquynhon.com", "Rex Hotel Quy Nhon", "https://rexhotelquynhon.com", True),
    # Côn Đảo — sixsensescondao.com
    ("Six Senses Côn Đảo", "Bãi Đất Dốc, TT. Côn Đảo, Côn Đảo, Bà Rịa – Vũng Tàu", "Côn Đảo", "Côn Đảo", 5, 50, "0254 3831 222", "https://www.sixsensescondao.com", "Six Senses Con Dao", "https://www.sixsensescondao.com", True),
    ("Poulo Condor Boutique Resort & Spa", "16 Ton Duc Thang, Con Dao Town", "Côn Đảo", "Côn Đảo", 4, 36, "0254 3630 011", "https://poulocondor.com", "Poulo Condor", "https://poulocondor.com", True),
    ("Con Dao Resort", "8 Nguyen Duc Thuan, Con Dao", "Côn Đảo", "Côn Đảo", 3, 60, "0254 3830 037", "https://condaoresort.com", "Con Dao Resort", "https://condaoresort.com", True),
    # Hải Phòng / Cát Bà
    ("Sheraton Hai Phong", "Lô 1, đường 27, KĐT Đồng Bắc, P. Sở Dầu, Q. Hồng Bàng, Hải Phòng", "Hồng Bàng", "Hải Phòng", 5, 250, "0225 3836 888", "https://www.marriott.com/en-us/hotels/hphsi-sheraton-hai-phong/overview/", "Sheraton Hai Phong", "https://www.marriott.com", False),
    ("Cat Ba Sunrise Resort", "Cat Co 3 Beach, Cat Ba Island, Hai Phong", "Cát Bà", "Cát Bà", 4, 70, "0225 3688 999", "https://catbasunriseresort.com", "Cat Ba Sunrise", "https://catbasunriseresort.com", True),
    ("Flamingo Cat Ba Beach Resort", "Cat Co Beach, Cat Ba Town", "Cát Bà", "Cát Bà", 4, 200, "0225 3686 888", "https://flamingoresorts.vn/cat-ba", "Flamingo Resorts", "https://flamingoresorts.vn", True),
    # Buôn Ma Thuột
    ("Ana Mandara Villas Buôn Ma Thuột", "Le Thanh Tong Street, Buon Ma Thuot", "Tân Lập", "Buôn Ma Thuột", 5, 17, "0262 3863 333", "https://anamandara-villas-bmt.com", "Ana Mandara Villas", "https://anamandara-villas-bmt.com", False),
    ("Mường Thanh Luxury Buôn Ma Thuột", "81 Nguyen Tat Thanh, Buon Ma Thuot", "Tân An", "Buôn Ma Thuột", 5, 150, "0262 3959 999", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
    ("Cao Nguyen Hotel Buon Ma Thuot", "01 Phan Chu Trinh, Buon Ma Thuot", "Tân Lợi", "Buôn Ma Thuột", 4, 90, "0262 3822 234", "https://caonguyenhotel.vn", "Cao Nguyen Hotel", "https://caonguyenhotel.vn", False),
    # An Giang — Châu Đốc
    ("Victoria Nui Sam Lodge", "Vinh Te 1, Chau Doc, An Giang", "Châu Đốc", "An Giang", 4, 46, "0296 3863 010", "https://www.victoriahotels.asia/nui-sam-lodge", "Victoria Hotels", "https://www.victoriahotels.asia", False),
    ("Chau Pho Hotel", "88 Bach Dang, Chau Doc, An Giang", "Châu Đốc", "An Giang", 3, 50, "0296 3567 777", "https://chauphohotel.com", "Chau Pho Hotel", "https://chauphohotel.com", False),
    # Kiên Giang (Rạch Giá — bổ sung ngoài Phú Quốc)
    ("Mường Thanh Rạch Giá", "Lot 3, Nguyen Binh Khiem, Rach Gia, Kien Giang", "Vĩnh Thanh", "Rạch Giá", 4, 120, "0297 6252 999", "https://muongthanh.vn", "Mường Thanh Hospitality", "https://muongthanh.vn", False),
]

PRICE_BY_CITY = {
    "Cần Thơ": {5: 2400000, 4: 1100000, 3: 700000},
    "Quảng Bình": {5: 2200000, 4: 1000000, 3: 650000},
    "Quy Nhơn": {5: 2500000, 4: 1200000, 3: 750000},
    "Côn Đảo": {5: 5000000, 4: 2800000, 3: 1200000},
    "Hải Phòng": {5: 2600000, 4: 1300000, 3: 800000},
    "Cát Bà": {5: 2500000, 4: 1200000, 3: 750000},
    "Buôn Ma Thuột": {5: 2000000, 4: 1000000, 3: 650000},
    "An Giang": {5: 1800000, 4: 900000, 3: 550000},
    "Rạch Giá": {5: 2000000, 4: 1000000, 3: 600000},
}

ATTRACTIONS_V2 = [
    # Quảng Bình — phongnhatourism.com.vn / phongnhakebang.vn
    {"id": "a59", "name": "Động Phong Nha", "city": "Quảng Bình", "ticketPrice": 150000,
     "tags": ["Hang động", "Di sản UNESCO", "Phù hợp gia đình", "Giá niêm yết"],
     "description": "Vé tham quan 150.000đ/người/lượt; trẻ <1,3m miễn phí. Thuyền vận chuyển 700.000đ/thuyền khứ hồi (tối đa 12 khách) — Trung tâm DL Phong Nha–Kẻ Bàng.",
     "suggestedDuration": "3-4 giờ", "sourceName": "Phong Nha Tourism Center", "sourceUrl": "https://phongnhatourism.com.vn",
     "priceNote": "Chưa gồm phí thuyền; chia đoàn tối đa 12 người/thuyền."},
    {"id": "a60", "name": "Động Thiên Đường", "city": "Quảng Bình", "ticketPrice": 250000,
     "tags": ["Hang động", "Di sản UNESCO", "Phù hợp gia đình"],
     "description": "Vé người lớn 250.000đ; trẻ 1,1m–1,3m giảm 50%. Xe điện trung chuyển tính riêng theo quy định.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Phong Nha Tourism Center", "sourceUrl": "https://phongnhakebang.vn"},
    {"id": "a61", "name": "Suối Moọc – Phong Nha", "city": "Quảng Bình", "ticketPrice": 80000,
     "tags": ["Thiên nhiên", "Phù hợp gia đình", "Tắm suối"],
     "description": "Vé tham quan 80.000đ; gói khám phá người lớn 450.000đ, gói phổ thông 220.000đ (theo TTDL PNKẻ Bàng).",
     "suggestedDuration": "Nửa ngày", "sourceName": "Phong Nha Tourism Center", "sourceUrl": "https://phongnhatourism.com.vn"},
    # Cần Thơ
    {"id": "a62", "name": "Chợ nổi Cái Răng", "city": "Cần Thơ", "ticketPrice": 0,
     "tags": ["Miễn phí", "Ẩm thực", "Văn hóa sông nước", "Buổi sáng"],
     "description": "Chợ nổi lớn nhất miền Tây, nên đến từ 5h–7h sáng. Không thu vé; chi phí thuê ghe ~200.000–300.000đ/ghe.",
     "suggestedDuration": "2-3 giờ", "priceNote": "Chi phí thuê ghe tham khảo, không phải vé cổng."},
    {"id": "a63", "name": "Vườn quốc gia Tràm Chim", "city": "Cần Thơ", "ticketPrice": 20000,
     "tags": ["Thiên nhiên", "Phù hợp gia đình", "Chim"],
     "description": "Khu bảo tồn chim (Đồng Tháp, gần Cần Thơ). Vé vào cổng tham khảo ~20.000đ; thuyền riêng.",
     "suggestedDuration": "Nửa ngày", "sourceName": "Tràm Chim National Park", "sourceUrl": "https://tramchim.org.vn"},
    {"id": "a64", "name": "Bến Ninh Kiều", "city": "Cần Thơ", "ticketPrice": 0,
     "tags": ["Miễn phí", "Check-in", "Buổi tối"],
     "description": "Bến sông Cần Thơ, đi dạo và ẩm thực ven sông miễn phí.",
     "suggestedDuration": "1-2 giờ"},
    # Quy Nhơn
    {"id": "a65", "name": "Tháp Đôi (Tháp Bạ – Tháp Đen)", "city": "Quy Nhơn", "ticketPrice": 15000,
     "tags": ["Di tích lịch sử", "Văn hóa Chăm", "Phù hợp gia đình"],
     "description": "Tháp Chăm tại 1071 Trần Hưng Đạo, TP. Quy Nhơn. Vé ~15.000đ/khách.",
     "suggestedDuration": "1 giờ"},
    {"id": "a66", "name": "Kỳ Co – Eo Gió", "city": "Quy Nhơn", "ticketPrice": 25000,
     "tags": ["Biển đảo", "Check-in", "Không phù hợp trẻ nhỏ"],
     "description": "Bãi Kỳ Co và Eo Gió (Nhơn Lý). Phí tham quan/vận chuyển tham khảo ~25.000đ + phí bãi.",
     "suggestedDuration": "Nửa ngày", "priceNote": "Có thể cần xe địa hình hoặc cano tùy tuyến."},
    {"id": "a67", "name": "Hòn Khô", "city": "Quy Nhơn", "ticketPrice": 0,
     "tags": ["Biển đảo", "Ẩm thực", "Hải sản"],
     "description": "Đảo gần bờ Quy Nhơn, nổi tiếng hải sản. Chi phí cano tham khảo, không vé cổng cố định.",
     "suggestedDuration": "Nửa ngày"},
    # Côn Đảo
    {"id": "a68", "name": "Nhà tù Côn Đảo", "city": "Côn Đảo", "ticketPrice": 0,
     "tags": ["Lịch sử", "Di tích", "Không phù hợp trẻ nhỏ"],
     "description": "Di tích lịch sử Quốc gia đặc biệt. Miễn phí tham quan khu di tích; nên thuê audio guide.",
     "suggestedDuration": "2-3 giờ", "sourceName": "Côn Đảo National Monuments", "sourceUrl": "https://condao.gov.vn"},
    {"id": "a69", "name": "Bãi Đầm Trầu", "city": "Côn Đảo", "ticketPrice": 0,
     "tags": ["Miễn phí", "Bãi biển", "Rùa biển"],
     "description": "Bãi đẹp hoang sơ, mùa rùa đẻ trứng (từ tháng 4–9). Miễn phí; tuân thủ quy định bảo vệ rùa.",
     "suggestedDuration": "Nửa ngày"},
    # Hải Phòng / Cát Bà
    {"id": "a70", "name": "Vịnh Lan Hạ (Cát Bà)", "city": "Cát Bà", "ticketPrice": 80000,
     "tags": ["Di sản", "Thuyền", "Phù hợp gia đình", "Kayak"],
     "description": "Vé tham quan vịnh Lan Hạ tham khảo ~80.000đ; tour kayak/tày riêng. UNESCO Khu dự trữ biosphere.",
     "suggestedDuration": "1 ngày", "sourceName": "Cat Ba National Park", "sourceUrl": "https://catba.gov.vn"},
    {"id": "a71", "name": "Hang Sửng Sốt (Hạ Long – từ Hải Phòng)", "city": "Hạ Long", "ticketPrice": 250000,
     "tags": ["Hang động", "Di sản UNESCO"],
     "description": "Nằm trong hành trình VHL2. Phí tham quan 250.000đ/người (Ban QL Vịnh Hạ Long, NQ 2025).",
     "suggestedDuration": "1 giờ", "sourceName": "Ban Quản lý Vịnh Hạ Long", "sourceUrl": "https://halongbay.com.vn"},
    # TP.HCM bổ sung
    {"id": "a72", "name": "Địa đạo Củ Chi", "city": "TP.HCM", "ticketPrice": 90000,
     "tags": ["Lịch sử", "Không phù hợp trẻ nhỏ"],
     "description": "Khu di tích Địa đạo Củ Chi. Vé tham quan ~90.000đ (bản đồ); ~110.000đ (bản đồ + trải nghiệm bắn súng tùy chọn).",
     "suggestedDuration": "Nửa ngày", "sourceName": "Khu di tích Địa đạo Củ Chi", "sourceUrl": "https://www.baotangcuchi.com.vn"},
    {"id": "a73", "name": "Thảo Cầm Viên Sài Gòn", "city": "TP.HCM", "ticketPrice": 60000,
     "tags": ["Phù hợp gia đình", "Thiên nhiên", "Trẻ em"],
     "description": "Sở thú & vườn thực vật lâu đời. Vé tham khảo ~60.000đ người lớn.",
     "suggestedDuration": "Nửa ngày"},
    # Buôn Ma Thuột
    {"id": "a74", "name": "Bảo tàng Dân tộc học Tây Nguyên", "city": "Buôn Ma Thuột", "ticketPrice": 30000,
     "tags": ["Bảo tàng", "Văn hóa", "Phù hợp gia đình"],
     "description": "1 Bạch Đằng, Buôn Ma Thuột. Vé ~30.000đ.",
     "suggestedDuration": "1-2 giờ"},
    {"id": "a75", "name": "Thác Dray Nur", "city": "Buôn Ma Thuột", "ticketPrice": 30000,
     "tags": ["Thiên nhiên", "Thác nước"],
     "description": "Thác nước nổi tiếng Tây Nguyên. Vé tham khảo ~30.000đ.",
     "suggestedDuration": "1-2 giờ"},
    # An Giang
    {"id": "a76", "name": "Núi Sam – Chùa Bà Chúa Xứ", "city": "An Giang", "ticketPrice": 0,
     "tags": ["Tâm linh", "Miễn phí", "Phù hợp gia đình"],
     "description": "Núi Sam, Châu Đốc. Miễn phí vào cổng; cáp treo riêng nếu đi cáp.",
     "suggestedDuration": "2-3 giờ"},
    {"id": "a77", "name": "Rừng tràm Trà Sư", "city": "An Giang", "ticketPrice": 100000,
     "tags": ["Thiên nhiên", "Thuyền", "Phù hợp gia đình"],
     "description": "Khu bảo tồn đa dạng sinh học. Vé thuyền + vé cổng tham khảo ~100.000đ/người.",
     "suggestedDuration": "Nửa ngày"},
]

TRANSPORT_V2 = [
    {"id": "t59", "type": "Máy bay", "from": "TP.HCM", "to": "Cần Thơ", "provider": "Vietnam Airlines", "price": 600000, "duration": "45 phút", "bookingUrl": "https://vietnamairlines.com", "note": "Bay sân bay Cần Thơ"},
    {"id": "t60", "type": "Máy bay", "from": "Hà Nội", "to": "Cần Thơ", "provider": "VietJet Air", "price": 850000, "duration": "2h05", "bookingUrl": "https://vietjetair.com", "note": "Bay thẳng Cần Thơ"},
    {"id": "t61", "type": "Xe khách", "from": "TP.HCM", "to": "Cần Thơ", "provider": "Phương Trang (FUTA)", "price": 180000, "duration": "4h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm Miền Tây"},
    {"id": "t62", "type": "Máy bay", "from": "Hà Nội", "to": "Quảng Bình", "provider": "Vietnam Airlines", "price": 950000, "duration": "1h10", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Đồng Hới + taxi"},
    {"id": "t63", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Quảng Bình", "provider": "Đường sắt Việt Nam", "price": 400000, "duration": "10h", "bookingUrl": "https://dsvn.vn", "note": "Ga Đồng Hới"},
    {"id": "t64", "type": "Máy bay", "from": "TP.HCM", "to": "Quy Nhơn", "provider": "VietJet Air", "price": 700000, "duration": "1h15", "bookingUrl": "https://vietjetair.com", "note": "Bay Phù Cát"},
    {"id": "t65", "type": "Máy bay", "from": "Hà Nội", "to": "Quy Nhơn", "provider": "Bamboo Airways", "price": 900000, "duration": "1h30", "bookingUrl": "https://bambooairways.com", "note": "Bay Phù Cát"},
    {"id": "t66", "type": "Máy bay", "from": "TP.HCM", "to": "Côn Đảo", "provider": "Vietnam Airlines", "price": 1200000, "duration": "1h", "bookingUrl": "https://vietnamairlines.com", "note": "Bay sân bay Côn Đảo (ít chuyến)"},
    {"id": "t67", "type": "Tàu cao tốc", "from": "TP.HCM", "to": "Côn Đảo", "provider": "Superdong", "price": 350000, "duration": "3h30", "bookingUrl": "https://superdong.com.vn", "note": "Tàu từ Trần Đề hoặc Vũng Tàu"},
    {"id": "t68", "type": "Máy bay", "from": "Hà Nội", "to": "Hải Phòng", "provider": "VietJet Air", "price": 500000, "duration": "45 phút", "bookingUrl": "https://vietjetair.com", "note": "Bay Cát Bi"},
    {"id": "t69", "type": "Xe khách", "from": "Hà Nội", "to": "Hải Phòng", "provider": "Kumho Samco", "price": 120000, "duration": "2h", "bookingUrl": "https://vexere.com", "note": "Limousine bến Giường"},
    {"id": "t70", "type": "Tàu hỏa", "from": "TP.HCM", "to": "Buôn Ma Thuột", "provider": "Đường sắt Việt Nam", "price": 450000, "duration": "8h", "bookingUrl": "https://dsvn.vn", "note": "Ga Buôn Ma Thuột (trạm gần)"},
    {"id": "t71", "type": "Máy bay", "from": "TP.HCM", "to": "Buôn Ma Thuột", "provider": "VietJet Air", "price": 650000, "duration": "50 phút", "bookingUrl": "https://vietjetair.com", "note": "Bay sân bay Buôn Ma Thuột"},
    {"id": "t73", "type": "Xe khách", "from": "TP.HCM", "to": "An Giang", "provider": "Phương Trang (FUTA)", "price": 200000, "duration": "6h", "bookingUrl": "https://futabus.vn", "note": "Đến Long Xuyên/Châu Đốc"},
    {"id": "t74", "type": "Máy bay", "from": "Đà Nẵng", "to": "Quy Nhơn", "provider": "Vietnam Airlines", "price": 550000, "duration": "45 phút", "bookingUrl": "https://vietnamairlines.com", "note": "Bay Phù Cát"},
    {"id": "t75", "type": "Xe phà", "from": "Hải Phòng", "to": "Cát Bà", "provider": "Phà Cát Bà", "price": 80000, "duration": "45 phút", "bookingUrl": "https://catbaisland.net", "note": "Phà Bến phà Gia Luận hoặc Tuần Châu–Cát Bà"},
    {"id": "t76", "type": "Máy bay", "from": "TP.HCM", "to": "Rạch Giá", "provider": "VietJet Air", "price": 700000, "duration": "1h", "bookingUrl": "https://vietjetair.com", "note": "Bay Rạch Giá (gần Phú Quốc)"},
]

# Sửa dữ liệu cũ chưa chính xác
PATCHES = {
    "hotels": [
        {
            "match_name": "ELDORA HOTEL HUE",
            "address": "60 Bến Nghé, P. Phú Hội, TP. Huế",
            "description": (
                "Địa chỉ: 60 Bến Nghé, P. Phú Hội, TP. Huế. Hạng chính thức: 4 sao. "
                "Khu vực/quận: Phú Hội. Số phòng theo nguồn: 81. Điện thoại: 0234 3812 222. "
                "Website: https://eldorahotel.com. Nguồn: Eldora Hotel."
                + DESC_SUFFIX
            ),
        },
    ],
    "attractions": [
        {
            "id": "a57",
            "name": "Chùa Bái Đính",
            "ticketPrice": 0,
            "description": (
                "Quần thể chùa Bái Đính, xã Gia Sinh. Vào cổng miễn phí; "
                "xe điện khứ hồi ~100.000đ; tham quan Bảo Tháp ~50.000đ (chuabaidinhninhbinh.vn)."
            ),
            "sourceName": "Chùa Bái Đính Ninh Bình",
            "sourceUrl": "https://chuabaidinhninhbinh.vn",
            "priceNote": "Chỉ thu phí dịch vụ xe điện/Bảo Tháp, không thu vé vào cổng.",
        },
    ],
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
    for row in HOTELS_V2:
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
    for item in ATTRACTIONS_V2:
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
    for item in TRANSPORT_V2:
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

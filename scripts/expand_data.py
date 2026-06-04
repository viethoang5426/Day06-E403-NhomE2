    # -*- coding: utf-8 -*-
"""Append verified tourism data to hotels.json, attractions.json, transport.json."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

DANANG_SOURCE = "Danang Fantasticity - Cổng thông tin du lịch Đà Nẵng"
DANANG_SOURCE_URL = "https://danangfantasticity.com/danh-sach-co-so-luu-tru-du-lich-tren-dia-ban-thanh-pho-da-nang-da-duoc-xep-hang"
NHATRANG_SOURCE = "Nha Trang Travel - Cổng thông tin du lịch Khánh Hòa"
NHATRANG_BASE = "https://nhatrang-travel.com/diem-den/dich-vu/co-so-luu-tru"

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

# Official Danang Fantasticity ranked list (address, district, stars, rooms, phone, website)
DANANG_NEW = [
    ("CROWNE PLAZA DANANG", "Số 8, Đường Võ Nguyên Giáp, P. Khuê Mỹ, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 535, "0236 3918888", "https://www.ihg.com/crowneplaza/hotels/us/en/da-nang/dadcp/hoteldetail", True),
    ("FURAMA RESORT DANANG", "Số 105 đường Võ Nguyên Giáp, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 329, "0236 3847888", "https://furamavietnam.com", True),
    ("FUSION MAIA RESORT", "Đường Võ Nguyên Giáp, P. Khuê Mỹ, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 96, "0236 3967999", "https://fusionresorts.com/danang", True),
    ("GRAND MERCURE DANANG", "Lô A1 Khu biệt thự Đảo Xanh, Q. Hải Châu", "Hải Châu", 5, 272, "0236 3797777", "https://www.mercure-danang.com", False),
    ("OLALANI RESORT AND CONDOTEL", "Đường Võ Nguyên Giáp, P. Khuê Mỹ, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 224, "0236 3951444", "https://olalani.com", False),
    ("ONE OPERA DANANG HOTEL", "115 Nguyễn Văn Linh, Q. Hải Châu", "Hải Châu", 5, 188, "0236 2223344", "https://oneoperadananghotel.com", False),
    ("VINPEARL ĐÀ NẴNG OCEAN RESORT & VILLAS", "23 Đường Trường Sa, P. Hòa Hải, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 122, "0236 3966888", "https://vinpearl.com", True),
    ("RISEMOUNT PREMIER RESORT DANANG", "120 Nguyễn Văn Thoại, Bắc Mỹ An, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 97, "0236 3899999", "https://risemountpremierdanang.com", False),
    ("PREMIER VILLAGE DANANG RESORT", "Đường Võ Nguyên Giáp, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 111, "0236 3919999", "https://premiervillage-danang.com", True),
    ("SHERATON GRAND ĐÀ NẴNG", "35 Đường Trường Sa, P. Hòa Hải, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 5, 258, "0236 3988999", "https://www.marriott.com/en-us/hotels/dadsi-sheraton-grand-danang-resort/overview/", True),
    ("FOUR POINTS BY SHERATON DANANG", "Số 118-120 Đường Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà", "Sơn Trà", 5, 390, "0236 3997979", "https://www.marriott.com/en-us/hotels/dadfp-four-points-danang/overview/", True),
    ("CENTARA SANDY BEACH RESORT DANANG", "21 Trường Sa, P. Hòa Hải, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 4, 192, "0236 3968523", "https://www.centarahotelsresorts.com/centara/csb", True),
    ("EDEN PLAZA DANANG", "05 Duy Tân, Q. Hải Châu", "Hải Châu", 4, 109, "0236 3662666", "https://edenplazadanang.com", False),
    ("MINH TOÀN GALAXY HOTEL", "306 Đường 2/9, P. Hòa Cường Bắc, Q. Hải Châu", "Hải Châu", 4, 175, "0236 3662888", "https://minhtoangalaxyhotel.com", False),
    ("MƯỜNG THANH GRAND ĐÀ NẴNG", "962 Ngô Quyền, Q. Sơn Trà", "Sơn Trà", 4, 378, "0236 3929929", "https://muongthanh.vn", False),
    ("STAY HOTEL DANANG", "119 Đường 3/2, Q. Hải Châu", "Hải Châu", 4, 103, "0236 3861861", "https://stayhotel.vn", False),
    ("AVATAR ĐÀ NẴNG HOTEL", "120 An Thượng 2, P. Mỹ An, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 4, 90, "0236 3939888", "https://avatardananghotel.com", False),
    ("VANDA HOTEL", "03 Nguyễn Văn Linh, Q. Hải Châu", "Hải Châu", 4, 114, "0236 3525969", "https://vandahotel.vn", False),
    ("SERENE ĐÀ NẴNG HOTEL", "274 Võ Nguyên Giáp, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 4, 140, "0236 3959177", "https://serenedananghotel.com", False),
    ("FUSION SUITES ĐÀ NẴNG BEACH", "KDC An Cư 5, P. Mân Thái, Q. Sơn Trà", "Sơn Trà", 4, 129, "0236 3919777", "https://fusionresorts.com/danang-beach", True),
    ("ROYAL LOTUS HOTEL DANANG", "120 Nguyễn Văn Thoại, Bắc Mỹ An, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 4, 192, "0236 6261999", "https://royallotushotel.com.vn", False),
    ("GRAND SEA HOTEL DANANG", "08 Hà Bổng, Q. Sơn Trà", "Sơn Trà", 4, 100, "0236 3636888", "https://grandseadanang.com", False),
    ("DANANG RIVERSIDE HOTEL", "A30 Trần Hưng Đạo, Q. Sơn Trà", "Sơn Trà", 4, 107, "0236 3946666", "https://danangriversidehotel.com", False),
    ("SAMDI HOTEL DANANG", "203-211 Nguyễn Văn Linh, Q. Thanh Khê", "Thanh Khê", 4, 126, "0236 3586223", "https://samdihotel.com", False),
    ("LÊ HOÀNG BEACH HOTEL", "244 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà", "Sơn Trà", 4, 110, "0236 3688886", "https://lehoangbeachhotel.com", False),
    ("GRANDVRIO HOTEL DANANG", "01-03 Đống Đa, P. Thạch Thang, Q. Hải Châu", "Hải Châu", 4, 169, "0236 3833300", "https://grandvriodanang.com", False),
    ("7 SEVEN SEA HOTEL DANANG", "150 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà", "Sơn Trà", 4, 133, "0236 3890707", "https://7sevenseahotel.com", False),
    ("PARIS DELI HOTEL DANANG", "236 Võ Nguyên Giáp, Q. Sơn Trà", "Sơn Trà", 4, 140, "0236 3896666", "https://parisdelidanang.com", False),
    ("BELLA MAISON PAROSAND ĐÀ NẴNG", "216 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà", "Sơn Trà", 4, 102, "0236 3928688", "https://bellamaisonparosand.com", False),
    ("PARACEL ĐÀ NẴNG HOTEL", "204 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà", "Sơn Trà", 4, 165, "0236 3966789", "https://paraceldananghotel.com", False),
    ("SATYA HOTEL", "155 Trần Phú, P. Hải Châu I, Q. Hải Châu", "Hải Châu", 4, 88, "0236 3588999", "https://satyahotel.vn", False),
    ("BALCONA HOTEL DANANG", "288 Võ Nguyên Giáp, P. Mỹ An, Q. Ngũ Hành Sơn", "Ngũ Hành Sơn", 4, 224, "0236 6299292", "https://balconahotel.com", False),
    ("ADINA HOTEL DANANG", "Lô G6-G7 Phạm Văn Đồng, Q. Sơn Trà", "Sơn Trà", 3, 73, "0236 3935935", "https://adinahotel.vn", False),
    ("ORCHID HOTEL DANANG", "Lô B2.4-10 Võ Nguyên Giáp, Q. Sơn Trà", "Sơn Trà", 3, 54, "0236 3946767", "https://orchiddanang.com", False),
    ("SAIGONTOURANE HOTEL", "05 Đống Đa, Q. Hải Châu", "Hải Châu", 3, 82, "0236 3821021", "https://saigontouranehotel.com", False),
    ("SEAFRONT HOTEL DANANG", "240 Võ Nguyên Giáp, Q. Sơn Trà", "Sơn Trà", 3, 84, "0236 3943768", "https://seafrontdanang.com", False),
    ("MINH TOÀN HOTEL", "162 Đường 2/9, P. Hòa Thuận Đông, Q. Hải Châu", "Hải Châu", 3, 63, "0236 3631888", "https://minhtoanhotel.com", False),
    ("MOONLIGHT HOTEL DANANG", "136-140 Phan Châu Trinh, Q. Hải Châu", "Hải Châu", 3, 91, "0236 3664488", "https://moonlightdanang.com", False),
]

# Nha Trang Travel portal — verified hotel records (name, address, district, stars, phone, website, slug)
NHATRANG_NEW = [
    ("Khách sạn Vinpearl Resort Nha Trang", "Đảo Hòn Tre, Vĩnh Nguyên, Nha Trang", "Vĩnh Nguyên", 5, "0258 3591888", "https://vinpearl.com", "5-sao/khach-san-vinpearl-resort-nha-trang.html"),
    ("Khách sạn Sheraton Nha Trang", "26-28 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 5, "0258 2220000", "https://www.marriott.com/en-us/hotels/cxrbr-sheraton-nha-trang-hotel-and-spa/overview/", "5-sao/khach-san-sheraton-nha-trang.html"),
    ("Khách sạn InterContinental Nha Trang", "32-34 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 5, "0258 3888888", "https://www.ihg.com/intercontinental/hotels/us/en/nha-trang/nhatr/hoteldetail", "5-sao/khach-san-intercontinental-nha-trang.html"),
    ("Khách sạn Amiana Resort Nha Trang", "Lô 26 Trần Phú, P. Phước Hương, Nha Trang", "Phước Hương", 5, "0258 3553333", "https://www.amianaresort.com", "5-sao/khach-san-amiana-resort-nha-trang.html"),
    ("Khách sạn Evason Ana Mandara Nha Trang", "Bãi Dài, Cam Ranh, Khánh Hòa", "Cam Ranh", 5, "0258 3524124", "https://www.sixsenses.com/en/resorts/ana-mandara", "5-sao/khach-san-evason-ana-mandara-nha-trang.html"),
    ("Khách sạn Havana Nha Trang", "98 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3527527", "https://www.havanahotel.vn", "4-sao/khach-san-havana-nha-trang.html"),
    ("Khách sạn Libra Nha Trang", "92-94 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3522777", "https://www.libranhatrang.com", "4-sao/khach-san-libra-nha-trang.html"),
    ("Khách sạn Mường Thanh Viễn Triều Nha Trang", "60 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3830136", "https://muongthanh.vn", "4-sao/khach-san-muong-thanh-vien-trieu-nha-trang.html"),
    ("Khách sạn Novotel Nha Trang", "50-52 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 6258888", "https://www.novotel-nhatrang.com", "4-sao/khach-san-novotel-nha-trang.html"),
    ("Khách sạn Rosaka Nha Trang", "272 Nguyễn Thị Minh Khai, Phước Hòa, Nha Trang", "Phước Hòa", 4, "0258 3881888", "https://rosaka.vn", "4-sao/khach-san-rosaka-nha-trang.html"),
    ("Khách sạn StarCity Nha Trang", "72-74 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3529888", "https://starcitynhatrang.com", "4-sao/khach-san-starcity-nha-trang.html"),
    ("Khách sạn Vias Hotel Nha Trang", "26-28 Lê Thánh Tôn, Phước Hòa, Nha Trang", "Phước Hòa", 4, "0258 3882999", "https://viashotel.vn", "4-sao/khach-san-vias-hotel-nha-trang.html"),
    ("Khách sạn Balcona Nha Trang", "98A Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3522666", "https://balconanhatrang.com", "4-sao/khach-san-balcona-nha-trang.html"),
    ("Khách sạn Citadines Bayfront Nha Trang", "62 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 4, "0258 3510111", "https://www.citadines.com/vietnam/nha-trang/citadines-bayfront-nha-trang.html", "4-sao/khach-san-citadines-bayfront-nha-trang.html"),
    ("Khách sạn Dendro Gold Nha Trang", "90-92 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 3, "0258 3522888", "https://dendrogoldhotel.com", "3-sao/khach-san-dendro-gold-nha-trang.html"),
    ("Khách sạn Golden Beach Nha Trang", "04 Trần Phú, Lộc Thọ, Nha Trang", "Lộc Thọ", 3, "0258 3522424", "https://goldenbeachhotel.vn", "3-sao/khach-san-golden-beach-nha-trang.html"),
    ("Khách sạn Saphia Nha Trang", "90-92 Lê Hồng Phong, Phước Hòa, Nha Trang", "Phước Hòa", 3, "0258 3882666", "https://saphiahotel.com", "3-sao/khach-san-saphia-nha-trang.html"),
]

PRICE_BY_STAR_DN = {5: 3200000, 4: 1200000, 3: 800000}
PRICE_BY_STAR_NT = {5: 2200000, 4: 1000000, 3: 650000}


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.upper().strip())


def make_danang_hotel(hid: str, row) -> dict:
    name, address, district, stars, rooms, phone, website, near_beach = row
    tags = [
        f"{stars} sao",
        "Nguồn chính thống",
        "Giá tham khảo",
        "Phù hợp gia đình",
        "Đà Nẵng",
    ]
    if stars >= 5:
        tags.insert(4, "Cao cấp")
    if near_beach:
        tags.append("Gần biển")
    desc = (
        f"Địa chỉ: {address}. Hạng chính thức: {stars} sao. Khu vực/quận: {district}. "
        f"Số phòng theo nguồn: {rooms}. Điện thoại: {phone}. Website: {website}. "
        f"Nguồn chính thống: {DANANG_SOURCE}.{DESC_SUFFIX}"
    )
    return {
        "id": hid,
        "name": name,
        "city": "Đà Nẵng",
        "pricePerNight": PRICE_BY_STAR_DN[stars],
        "currency": "VND",
        "rating": float(stars),
        "image": IMAGES[stars if stars in IMAGES else 4],
        "bookingUrl": website,
        "tags": tags,
        "description": desc,
        "address": address,
        "district": district,
        "officialStarRating": stars,
        "rooms": rooms,
        "phone": phone,
        "officialWebsite": website,
        "sourceName": DANANG_SOURCE,
        "sourceUrl": DANANG_SOURCE_URL,
        "priceNote": PRICE_NOTE,
        "priceVerified": False,
    }


def make_nhatrang_hotel(hid: str, row) -> dict:
    name, address, district, stars, phone, website, slug = row
    tags = [
        f"{stars} sao",
        "Nguồn chính thống",
        "Giá tham khảo",
        "Phù hợp gia đình",
        "Nha Trang",
    ]
    if stars >= 5:
        tags.insert(4, "Cao cấp")
    if "Trần Phú" in address or "biển" in address.lower() or district in ("Lộc Thọ", "Vĩnh Nguyên"):
        tags.append("Gần biển")
    desc = (
        f"Địa chỉ: {address}. Hạng chính thức: {stars} sao. Khu vực/quận: {district}. "
        f"Điện thoại: {phone}. Website: {website}. Nguồn chính thống: {NHATRANG_SOURCE}.{DESC_SUFFIX}"
    )
    return {
        "id": hid,
        "name": name,
        "city": "Nha Trang",
        "pricePerNight": PRICE_BY_STAR_NT[stars],
        "currency": "VND",
        "rating": float(stars),
        "image": IMAGES.get(stars, IMAGES[4]),
        "bookingUrl": website,
        "tags": tags,
        "description": desc,
        "address": address,
        "district": district,
        "officialStarRating": stars,
        "rooms": None,
        "phone": phone,
        "officialWebsite": website,
        "sourceName": NHATRANG_SOURCE,
        "sourceUrl": f"{NHATRANG_BASE}/{slug}",
        "priceNote": PRICE_NOTE,
        "priceVerified": False,
    }


NEW_ATTRACTIONS = [
    {
        "id": "a14",
        "name": "Chùa Linh Ứng – Bãi Bắc (Sơn Trà)",
        "city": "Đà Nẵng",
        "ticketPrice": 0,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
        "tags": ["Miễn phí", "Tâm linh", "Check-in", "Phù hợp gia đình"],
        "description": "Chùa Linh Ứng Bãi Bắc trên bán đảo Sơn Trà, tượng Quan Âm 67m nhìn ra biển. Miễn phí vào cổng; nên mặc kín đáo.",
        "suggestedDuration": "1-2 giờ",
    },
    {
        "id": "a15",
        "name": "Bảo tàng Chăm – Đà Nẵng",
        "city": "Đà Nẵng",
        "ticketPrice": 60000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1528181304800-259b08848526?w=400",
        "tags": ["Di tích lịch sử", "Phù hợp gia đình", "Văn hóa Chăm", "Bảo tàng"],
        "description": "Bảo tàng Điêu khắc Chăm lớn nhất Việt Nam, 2 Trần Phú. Vé tham quan khoảng 60.000đ/khách (theo quy định Bảo tàng).",
        "suggestedDuration": "1-2 giờ",
        "sourceName": "Bảo tàng Điêu khắc Chăm",
        "sourceUrl": "https://champa-museum.danang.vn",
    },
    {
        "id": "a16",
        "name": "Ngũ Hành Sơn (Marble Mountains)",
        "city": "Đà Nẵng",
        "ticketPrice": 40000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=400",
        "tags": ["Thiên nhiên", "Tâm linh", "Phù hợp gia đình", "Hang động"],
        "description": "Quần thể núi đá vôi với hang, chùa, làng đá mỹ nghệ. Vé tham quan khoảng 40.000đ; thang máy riêng ~15.000đ/lượt.",
        "suggestedDuration": "2-3 giờ",
        "sourceName": "Khu du lịch Ngũ Hành Sơn",
        "sourceUrl": "https://nguhanhson.vn",
    },
    {
        "id": "a17",
        "name": "Bãi biển Non Nước",
        "city": "Đà Nẵng",
        "ticketPrice": 0,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
        "tags": ["Miễn phí", "Bãi biển", "Tắm biển", "Phù hợp gia đình"],
        "description": "Bãi biển hoang sơ dưới chân Ngũ Hành Sơn, cát trắng, sóng êm. Tắm biển miễn phí; có dịch vụ thuê ghế, nước uống.",
        "suggestedDuration": "Nửa ngày",
    },
    {
        "id": "a18",
        "name": "Công viên Asia Park – Sun Wheel",
        "city": "Đà Nẵng",
        "ticketPrice": 150000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1570366583862-f91883984fde?w=400",
        "tags": ["Phù hợp gia đình", "Vui chơi", "Buổi tối", "Sun Wheel"],
        "description": "Công viên giải trí ven sông Hàn với vòng quay Sun Wheel. Vé tham khảo từ ~150.000đ tùy gói trò chơi.",
        "suggestedDuration": "Nửa ngày - 1 ngày",
        "sourceName": "Sun World Danang Wonders",
        "sourceUrl": "https://asiatique.sunworld.vn",
        "priceNote": "Giá tham khảo; kiểm tra bảng giá Sun World.",
    },
    {
        "id": "a19",
        "name": "Bảo tàng Alexandre Yersin",
        "city": "Nha Trang",
        "ticketPrice": 28000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=400",
        "tags": ["Bảo tàng", "Phù hợp gia đình", "Lịch sử"],
        "description": "Bảo tàng Pasteur Nha Trang về bác sĩ Yersin, 10 Trần Phú. Vé tham quan khoảng 28.000đ.",
        "suggestedDuration": "1 giờ",
    },
    {
        "id": "a20",
        "name": "Viện Hải dương học Nha Trang",
        "city": "Nha Trang",
        "ticketPrice": 40000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        "tags": ["Phù hợp gia đình", "Thủy cung", "Trẻ em", "Bảo tàng"],
        "description": "Viện Oceanography với hơn 80.000 mẫu sinh vật biển, bể cá mập, rùa biển. Vé ~40.000đ/khách.",
        "suggestedDuration": "1-2 giờ",
        "sourceName": "Viện Hải dương học",
        "sourceUrl": "https://io.vast.vn",
    },
    {
        "id": "a21",
        "name": "Hòn Mun – Hòn Tằm (lặn biển)",
        "city": "Nha Trang",
        "ticketPrice": 250000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        "tags": ["Biển đảo", "Lặn biển", "Không phù hợp trẻ nhỏ", "Thiên nhiên"],
        "description": "Tour đảo và lặn ngắm san hô tại khu bảo tồn biển Hòn Mun. Giá tour tham khảo từ ~250.000đ (tùy nhà tổ chức).",
        "suggestedDuration": "1 ngày",
        "priceNote": "Giá tour tham khảo, không bao gồm dịch vụ lặn chuyên sâu.",
    },
    {
        "id": "a22",
        "name": "Kong Forest – Zipline Nha Trang",
        "city": "Nha Trang",
        "ticketPrice": 680000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
        "tags": ["Vui chơi", "Không phù hợp trẻ nhỏ", "Mạo hiểm", "Zipline"],
        "description": "Công viên thám hiểm với zipline canopy tour đầu tiên tại Nha Trang. Vé tham khảo ~680.000đ/gói trải nghiệm.",
        "suggestedDuration": "Nửa ngày",
        "sourceName": "Kong Forest Nha Trang",
        "sourceUrl": "https://kongforest.vn",
        "priceNote": "Giá tham khảo theo gói trải nghiệm.",
    },
    {
        "id": "a23",
        "name": "Khu du lịch Sỏi Island (Hòn Miếu)",
        "city": "Nha Trang",
        "ticketPrice": 0,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400",
        "tags": ["Miễn phí", "Check-in", "Ẩm thực", "Phù hợp gia đình"],
        "description": "Khu du lịch trên Hòn Miếu, cầu dẫn từ bờ, quán cà pháo, view biển. Vào cổng miễn phí; chi phí ăn uống riêng.",
        "suggestedDuration": "2-3 giờ",
    },
    {
        "id": "a24",
        "name": "Cố đô Huế (từ Đà Nẵng)",
        "city": "Đà Nẵng",
        "ticketPrice": 200000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=400",
        "tags": ["Di sản UNESCO", "Lịch sử", "Phù hợp gia đình"],
        "description": "Quần thể di tích Cố đô Huế cách Đà Nẵng ~100km. Vé Kinh thành tham khảo ~200.000đ; nên thuê xe hoặc tour ngày.",
        "suggestedDuration": "1 ngày",
        "sourceName": "Quần thể di tích Cố đô Huế",
        "sourceUrl": "https://hueworldheritage.org.vn",
        "priceNote": "Vé tham khảo một số điểm trong Kinh thành.",
    },
    {
        "id": "a25",
        "name": "Cù Lao Chàm",
        "city": "Đà Nẵng",
        "ticketPrice": 150000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        "tags": ["Biển đảo", "Lặn biển", "Phù hợp gia đình", "Sinh thái"],
        "description": "Đảo cách Hội An ~15 phút cao tốc, Khu dự trữ biosphere UNESCO. Phí cano/tour tham khảo ~150.000đ + phí bảo tồn biển.",
        "suggestedDuration": "1 ngày",
    },
    {
        "id": "a26",
        "name": "Bãi biển Bắc Mỹ An",
        "city": "Đà Nẵng",
        "ticketPrice": 0,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
        "tags": ["Miễn phí", "Bãi biển", "Tắm biển", "Phù hợp gia đình"],
        "description": "Dải bãi dài từ Ngũ Hành Sơn đến Sơn Trà, nhiều resort 5 sao, sóng êm phù hợp gia đình.",
        "suggestedDuration": "Nửa ngày",
    },
    {
        "id": "a27",
        "name": "Nhà thờ Núi Nha Trang",
        "city": "Nha Trang",
        "ticketPrice": 0,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=400",
        "tags": ["Miễn phí", "Tâm linh", "Check-in", "Phù hợp gia đình"],
        "description": "Nhà thờ đá Gothic trên đồi, 1 Thái Nguyên. Miễn phí; giờ lễ Chúa nhật sáng.",
        "suggestedDuration": "30 phút - 1 giờ",
    },
    {
        "id": "a28",
        "name": "Suối Hoa Lan – Nha Trang",
        "city": "Nha Trang",
        "ticketPrice": 120000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
        "tags": ["Thiên nhiên", "Phù hợp gia đình", "Suối nước"],
        "description": "Khu sinh thái suối nước trong, vườn lan, BBQ. Vé tham khảo ~120.000đ.",
        "suggestedDuration": "Nửa ngày",
    },
    {
        "id": "a29",
        "name": "Cố đô Hoa Lư – Tràng An (Ninh Bình)",
        "city": "Ninh Bình",
        "ticketPrice": 250000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1583417646736-22a4666f3630?w=400",
        "tags": ["Di sản UNESCO", "Thiên nhiên", "Phù hợp gia đình", "Thuyền"],
        "description": "Quần thể di sản Tràng An: tour thuyền ~250.000đ (theo quy định ban quản lý). Có thể kết hợp Bái Đính, Tam Cốc.",
        "suggestedDuration": "1 ngày",
        "sourceName": "Quần thể danh thắng Tràng An",
        "sourceUrl": "https://trangan.ninhbinh.gov.vn",
    },
    {
        "id": "a30",
        "name": "Tam Cốc – Bích Động",
        "city": "Ninh Bình",
        "ticketPrice": 250000,
        "currency": "VND",
        "image": "https://images.unsplash.com/photo-1583417646736-22a4666f3630?w=400",
        "tags": ["Thiên nhiên", "Phù hợp gia đình", "Thuyền", "Hang động"],
        "description": "Vịnh Hạ Long trên cạn: đi thuyền sông Ngô Đồng qua hang. Vé thuyền tham khảo ~250.000đ/4 khách.",
        "suggestedDuration": "Nửa ngày",
    },
]

NEW_TRANSPORT = [
    {"id": "t12", "type": "Máy bay", "from": "TP.HCM", "to": "Đà Nẵng", "provider": "Bamboo Airways", "price": 850000, "currency": "VND", "duration": "1h20", "bookingUrl": "https://bambooairways.com", "note": "Bay thẳng, hành lý 20kg (tùy hạng vé)"},
    {"id": "t13", "type": "Máy bay", "from": "TP.HCM", "to": "Đà Nẵng", "provider": "Vietnam Airlines", "price": 1200000, "currency": "VND", "duration": "1h20", "bookingUrl": "https://vietnamairlines.com", "note": "Hạng phổ thông, hành lý 23kg"},
    {"id": "t14", "type": "Máy bay", "from": "TP.HCM", "to": "Nha Trang", "provider": "VietJet Air", "price": 680000, "currency": "VND", "duration": "1h05", "bookingUrl": "https://vietjetair.com", "note": "Bay thẳng sân bay Cam Ranh, giá tham khảo"},
    {"id": "t15", "type": "Máy bay", "from": "TP.HCM", "to": "Nha Trang", "provider": "Bamboo Airways", "price": 780000, "currency": "VND", "duration": "1h05", "bookingUrl": "https://bambooairways.com", "note": "Bay thẳng Cam Ranh"},
    {"id": "t16", "type": "Máy bay", "from": "Hà Nội", "to": "Đà Nẵng", "provider": "Vietnam Airlines", "price": 1100000, "currency": "VND", "duration": "1h15", "bookingUrl": "https://vietnamairlines.com", "note": "Bay thẳng, nhiều chuyến/ngày"},
    {"id": "t17", "type": "Máy bay", "from": "Hà Nội", "to": "Đà Nẵng", "provider": "VietJet Air", "price": 650000, "currency": "VND", "duration": "1h15", "bookingUrl": "https://vietjetair.com", "note": "Giá rẻ, hành lý xách tay 7kg"},
    {"id": "t18", "type": "Máy bay", "from": "Hà Nội", "to": "Nha Trang", "provider": "Vietnam Airlines", "price": 1200000, "currency": "VND", "duration": "1h50", "bookingUrl": "https://vietnamairlines.com", "note": "Bay thẳng Cam Ranh"},
    {"id": "t19", "type": "Máy bay", "from": "Hà Nội", "to": "Nha Trang", "provider": "Bamboo Airways", "price": 950000, "currency": "VND", "duration": "1h50", "bookingUrl": "https://bambooairways.com", "note": "Bay thẳng Cam Ranh"},
    {"id": "t20", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Nha Trang", "provider": "Đường sắt Việt Nam", "price": 550000, "currency": "VND", "duration": "26h", "bookingUrl": "https://dsvn.vn", "note": "SE tốc hành/giường nằm điều hòa"},
    {"id": "t21", "type": "Tàu hỏa", "from": "TP.HCM", "to": "Đà Nẵng", "provider": "Đường sắt Việt Nam", "price": 450000, "currency": "VND", "duration": "15h", "bookingUrl": "https://dsvn.vn", "note": "Giường nằm điều hòa"},
    {"id": "t22", "type": "Tàu hỏa", "from": "Đà Nẵng", "to": "Nha Trang", "provider": "Đường sắt Việt Nam", "price": 200000, "currency": "VND", "duration": "9h", "bookingUrl": "https://dsvn.vn", "note": "Ghế mềm/giường nằm dọc biển"},
    {"id": "t23", "type": "Xe khách giường nằm", "from": "Hà Nội", "to": "Đà Nẵng", "provider": "Phương Trang (FUTA)", "price": 400000, "currency": "VND", "duration": "14h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm, khởi hành tối"},
    {"id": "t24", "type": "Xe khách giường nằm", "from": "Hà Nội", "to": "Nha Trang", "provider": "Phương Trang (FUTA)", "price": 500000, "currency": "VND", "duration": "22h", "bookingUrl": "https://futabus.vn", "note": "Xe giường nằm điều hòa"},
    {"id": "t25", "type": "Xe khách giường nằm", "from": "TP.HCM", "to": "Nha Trang", "provider": "Hoàng Long", "price": 280000, "currency": "VND", "duration": "9h", "bookingUrl": "https://hoanglong.vn", "note": "Xe giường nằm, nhiều giờ khởi hành"},
    {"id": "t26", "type": "Xe Limousine", "from": "Đà Nẵng", "to": "Hội An", "provider": "Hội An Express", "price": 150000, "currency": "VND", "duration": "45 phút", "bookingUrl": "https://vexere.com", "note": "Xe 9 chỗ, đón trả trung tâm Đà Nẵng"},
    {"id": "t27", "type": "Xe Limousine", "from": "Đà Nẵng", "to": "Huế", "provider": "Kumho Samco", "price": 200000, "currency": "VND", "duration": "2h", "bookingUrl": "https://vexere.com", "note": "Xe limousine cao cấp"},
    {"id": "t28", "type": "Máy bay", "from": "Đà Nẵng", "to": "Nha Trang", "provider": "VietJet Air", "price": 550000, "currency": "VND", "duration": "1h", "bookingUrl": "https://vietjetair.com", "note": "Bay nội địa ngắn, giá tham khảo"},
    {"id": "t29", "type": "Máy bay", "from": "Đà Nẵng", "to": "Hà Nội", "provider": "VietJet Air", "price": 700000, "currency": "VND", "duration": "1h15", "bookingUrl": "https://vietjetair.com", "note": "Chiều về, giá tham khảo"},
    {"id": "t30", "type": "Máy bay", "from": "Đà Nẵng", "to": "TP.HCM", "provider": "Vietnam Airlines", "price": 1100000, "currency": "VND", "duration": "1h20", "bookingUrl": "https://vietnamairlines.com", "note": "Bay thẳng, hành lý 23kg"},
    {"id": "t31", "type": "Tàu hỏa", "from": "Hà Nội", "to": "Ninh Bình", "provider": "Đường sắt Việt Nam", "price": 120000, "currency": "VND", "duration": "2h", "bookingUrl": "https://dsvn.vn", "note": "SE5/SE7, ghế ngồi mềm"},
    {"id": "t32", "type": "Xe khách", "from": "Hà Nội", "to": "Ninh Bình", "provider": "Kumho Samco", "price": 120000, "currency": "VND", "duration": "2h", "bookingUrl": "https://vexere.com", "note": "Xe khách giường/limousine Bến Giường"},
    {"id": "t33", "type": "Xe Limousine", "from": "TP.HCM", "to": "Đà Nẵng", "provider": "Phương Trang Limousine", "price": 450000, "currency": "VND", "duration": "16h", "bookingUrl": "https://futabus.vn", "note": "Limousine 34 chỗ, ghế massage"},
    {"id": "t34", "type": "Máy bay", "from": "TP.HCM", "to": "Ninh Bình", "provider": "VietJet Air", "price": 900000, "currency": "VND", "duration": "2h", "bookingUrl": "https://vietjetair.com", "note": "Bay TP.HCM–Nội Bài + xe ~2h (không có sân bay Ninh Bình)"},
    {"id": "t35", "type": "Tàu hỏa", "from": "TP.HCM", "to": "Nha Trang", "provider": "Đường sắt Việt Nam", "price": 400000, "currency": "VND", "duration": "7h", "bookingUrl": "https://dsvn.vn", "note": "Giường nằm điều hòa (đã có t6, thêm SE)"},
]


def main():
    hotels_path = DATA / "hotels.json"
    hotels = json.loads(hotels_path.read_text(encoding="utf-8"))
    existing = {normalize_name(h["name"]) for h in hotels}

    next_id = max(int(h["id"].lstrip("h")) for h in hotels) + 1
    added_h = 0

    for row in DANANG_NEW:
        if normalize_name(row[0]) in existing:
            continue
        hid = f"h{next_id:03d}"
        hotels.append(make_danang_hotel(hid, row))
        existing.add(normalize_name(row[0]))
        next_id += 1
        added_h += 1

    for row in NHATRANG_NEW:
        if normalize_name(row[0]) in existing:
            continue
        hid = f"h{next_id:03d}"
        hotels.append(make_nhatrang_hotel(hid, row))
        existing.add(normalize_name(row[0]))
        next_id += 1
        added_h += 1

    hotels_path.write_text(json.dumps(hotels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Update a1 Ba Na price and a6 Vinpearl name/price in attractions
    attr_path = DATA / "attractions.json"
    attractions = json.loads(attr_path.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in attractions}
    for a in attractions:
        if a["id"] == "a1":
            a["ticketPrice"] = 1000000
            a["description"] = (
                "Khu du lịch trên núi với Cầu Vàng, cáp treo, làng Pháp và Fantasy Park. "
                "Vé cáp treo khứ hồi người lớn (≥1m4): 1.000.000đ theo bảng giá Sun World 2026."
            )
        if a["id"] == "a4":
            a["ticketPrice"] = 80000
            a["description"] = (
                "Phố cổ Di sản UNESCO cách Đà Nẵng ~30km. Vé tham quan 5 di tích: "
                "80.000đ/khách Việt Nam, 120.000đ khách quốc tế (theo UBND TP. Hội An)."
            )
        if a["id"] == "a6":
            a["name"] = "VinWonders Nha Trang"
            a["ticketPrice"] = 1050000
            a["description"] = (
                "Công viên giải trí trên đảo Hòn Tre: cáp treo, thủy cung, công viên nước. "
                "Vé tiêu chuẩn người lớn: 1.050.000đ theo vinwonders.com."
            )
        if a["id"] == "a7":
            a["ticketPrice"] = 30000
            a["description"] = (
                "Quần thể tháp Chăm cổ trên đồi 2 Tháng 4. Vé tham quan khoảng 30.000đ "
                "(theo quy định Khu di tích)."
            )

    for item in NEW_ATTRACTIONS:
        if item["id"] not in existing_ids:
            attractions.append(item)
            existing_ids.add(item["id"])

    attr_path.write_text(json.dumps(attractions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    trans_path = DATA / "transport.json"
    transport = json.loads(trans_path.read_text(encoding="utf-8"))
    existing_t = {t["id"] for t in transport}
    for item in NEW_TRANSPORT:
        if item["id"] not in existing_t:
            transport.append(item)

    trans_path.write_text(json.dumps(transport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Hotels: +{added_h} (total {len(hotels)})")
    print(f"Attractions: {len(attractions)}")
    print(f"Transport: {len(transport)}")


if __name__ == "__main__":
    main()

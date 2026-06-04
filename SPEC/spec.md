# Thin SPEC — Nhóm 2 (AI Explorer)

Bản đặc tả thiết kế hẹp (Thin SPEC) cam kết luồng chức năng sẽ xây dựng cho prototype trong ngày Day 06.

## 1. Track, product/app và user

* **Track:** Travel  
* **Product/app thật:** AI Travel Planner Chatbot (Trợ lý lập kế hoạch du lịch thông minh)  
* **User cụ thể:** Người dùng bận rộn (nhân viên văn phòng, gia đình trẻ) muốn đi du lịch nhưng không có thời gian tìm hiểu về các danh lam thắng cảnh, khách sạn, phương tiện di chuyển tại địa phương. Họ cần một trợ lý AI thu thập nhanh thông tin hành trình và đề xuất trọn gói: khách sạn phù hợp, phương tiện di chuyển kèm giá vé, và các điểm du lịch hấp dẫn.  
* **Nhóm có phải user thật không? Nếu không, khác ở đâu?**  
  * **Có.** Các thành viên trong nhóm đều có nhu cầu đi du lịch nhưng thường rất bận và không có thời gian nghiên cứu kỹ về điểm đến. Từng gặp tình huống phải tra cứu nhiều trang web khác nhau (Booking, Traveloka, Google Maps, blog du lịch) để tổng hợp thông tin mà vẫn bỏ sót nhiều địa điểm hay.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Khảo sát nội bộ: 4/4 thành viên nhóm mất trung bình 3-5 giờ để lên kế hoạch cho một chuyến đi 2-3 ngày, phải mở 5-8 tab trình duyệt cùng lúc. | Trải nghiệm tự thử nghiệm | Người dùng bận rộn không có đủ thời gian nghiên cứu và so sánh giữa nhiều nguồn. Họ cần một nơi tổng hợp tất cả. | AI phải tự động tổng hợp thông tin từ nhiều nguồn (khách sạn, vé xe/máy bay, điểm du lịch) và trả về kết quả trọn gói trong một cuộc trò chuyện. |
| Review trên App Store: Nhiều app du lịch chỉ giải quyết 1 khâu (chỉ đặt phòng hoặc chỉ đặt vé), buộc user phải nhảy qua nhiều app. | App Store reviews (Traveloka, Booking, Agoda) | Người dùng muốn trải nghiệm "one-stop" — một chỗ giải quyết tất cả từ khách sạn, vé đến lịch trình tham quan. | Chatbot phải bao phủ cả 3 mảng: khách sạn + phương tiện + điểm du lịch trong cùng một luồng hội thoại. |
| Phân tích Booking.com AI Trip Planner: Tự động gợi ý điểm đến kèm link đặt phòng, nhưng không gợi ý phương tiện di chuyển hay lịch trình tham quan chi tiết. | Phân tích đối thủ | Các chatbot hiện tại của đối thủ chỉ tập trung vào đặt phòng, chưa giải quyết trọn vẹn nhu cầu lên kế hoạch du lịch. | Tạo điểm khác biệt bằng cách đề xuất trọn gói: khách sạn + phương tiện + trip/danh lam thắng cảnh. |

## 3. Pain statement

```text
User [người bận rộn muốn đi du lịch nhưng thiếu thời gian tìm hiểu] đang gặp khó ở [bước lập kế hoạch và tìm kiếm thông tin tổng hợp về điểm đến],
vì [phải tra cứu trên quá nhiều nền tảng khác nhau (đặt phòng, đặt vé, tìm điểm tham quan) mà vẫn không biết hết các danh lam thắng cảnh địa phương],
dẫn tới [mất nhiều giờ nghiên cứu, bỏ lỡ các địa điểm hay, hoặc từ bỏ việc lập kế hoạch và đi tour truyền thống đắt tiền].
Bằng chứng chính là [các thành viên nhóm mất 3-5 giờ nghiên cứu cho mỗi chuyến đi ngắn ngày, và review trên App Store cho thấy user phàn nàn phải nhảy qua nhiều app để hoàn tất một chuyến đi].
```

## 4. Build slice

```text
Cho [người bận rộn muốn lên kế hoạch du lịch nhanh chóng],
prototype sẽ dùng AI để [hỏi lần lượt 5 thông tin: Nơi đi, Nơi đến, Ngày đi, Số người lớn & trẻ nhỏ, Budget],
tạo ra [gói đề xuất trọn gói gồm: (1) Danh sách khách sạn phù hợp kèm ảnh phòng minh họa và link đặt phòng, (2) Phương tiện di chuyển phù hợp kèm giá vé và link đặt vé, (3) Đề xuất trip/danh lam thắng cảnh/địa điểm du lịch phù hợp với yêu cầu],
và xử lý [failure mode - AI đề xuất khách sạn/phương tiện không phù hợp ngân sách hoặc điểm du lịch không phù hợp thời gian] bằng [cho phép user phản hồi "Không phù hợp" để AI đề xuất lại với tiêu chí điều chỉnh, kèm hiển thị rõ ràng giá và thông tin nguồn].
```

## 5. Auto/Aug decision

Chọn một:

* [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
* [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
* [ ] **Automation:** AI tự quyết và tự hành động.

* **Lý do chọn:** Việc đặt phòng khách sạn, mua vé phương tiện và chọn lịch trình du lịch là những quyết định mang tính cá nhân cao, phụ thuộc vào sở thích và hoàn cảnh riêng của từng người. AI không thể thay thế hoàn toàn quyết định của user. Hơn nữa, nếu AI tự động đặt phòng/mua vé sai, hậu quả tài chính và rủi ro hành trình rất lớn. Do đó, AI đóng vai trò tổng hợp, phân tích và đề xuất các lựa chọn tốt nhất, còn user là người ra quyết định cuối cùng.
* **Human role:** **decider** (Người xem xét các đề xuất và quyết định đặt phòng/mua vé) & **customizer** (Người điều chỉnh yêu cầu nếu đề xuất chưa phù hợp, ví dụ thay đổi budget, thêm/bớt ngày, đổi phương tiện).

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| **Happy** | User chat: *"Tôi muốn đi du lịch từ TP.HCM đến Đà Nẵng, ngày 15-17/7, 2 người lớn 1 trẻ nhỏ, budget 5 triệu"*. AI thu thập đủ 5 thông tin → Trả về: (1) 3 khách sạn phù hợp kèm ảnh phòng, giá, link đặt phòng; (2) Vé máy bay/xe khách phù hợp kèm giá và link đặt vé; (3) Đề xuất trip tham quan Bà Nà Hills, Cầu Rồng, Bãi biển Mỹ Khê kèm mô tả ngắn. |
| **Low-confidence** | User cung cấp budget thấp (ví dụ 1.5 triệu cho 3 ngày 2 đêm tại Đà Nẵng). AI cảnh báo: *"Budget của bạn khá hạn chế cho điểm đến này. Tôi sẽ ưu tiên gợi ý nhà nghỉ giá rẻ và phương tiện xe khách. Bạn có muốn tăng budget hoặc đổi điểm đến gần hơn không?"* Kèm đề xuất thay thế. |
| **Failure** | AI đề xuất khách sạn ngoài tầm giá (ví dụ khách sạn 4 sao khi budget chỉ 3 triệu) hoặc gợi ý phương tiện không khả thi (bay khi chỉ cần đi xe buýt nội thành). User phản hồi "Không phù hợp", AI nhận feedback và đề xuất lại phù hợp hơn. |
| **Correction** | User yêu cầu đổi tiêu chí giữa chừng: *"Thêm 1 người lớn nữa"* hoặc *"Đổi từ Đà Nẵng sang Nha Trang"*. AI cập nhật lại thông tin và đề xuất mới mà không cần hỏi lại từ đầu. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user [yêu cầu đề xuất trọn gói du lịch cho gia đình có trẻ nhỏ với budget cụ thể],
AI có thể [đề xuất khách sạn/phương tiện có giá không chính xác hoặc đã hết phòng/vé, hoặc gợi ý điểm du lịch không phù hợp với trẻ nhỏ],
hậu quả là [user tin tưởng đặt theo đề xuất nhưng đến nơi phát hiện giá khác, hết phòng, hoặc điểm du lịch không an toàn cho trẻ em].
Prototype sẽ xử lý bằng [hiển thị rõ ràng thông tin nguồn (tên website, ngày cập nhật), ghi chú cảnh báo: "Giá có thể thay đổi, vui lòng kiểm tra lại tại link đặt phòng/vé trước khi thanh toán", và thêm tag "Phù hợp gia đình" / "Không phù hợp trẻ nhỏ" cho các điểm du lịch].
Owner kiểm thử path này là [Cao Việt Hoàng].
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| **Nguyễn Văn An** | Research / evidence | File JSON dữ liệu mẫu gồm 10 khách sạn, 5 phương tiện, 10 điểm du lịch tại 2 thành phố (Đà Nẵng, Nha Trang) với đầy đủ thông tin: tên, giá, ảnh, link đặt, mô tả, tag phù hợp. |
| **Cao Việt Hoàng** | SPEC & Prototype | Mã nguồn xử lý luồng hội thoại AI: thu thập 5 thông tin → gọi API LLM → trả kết quả trọn gói (khách sạn + phương tiện + trip) với giao diện chat hiển thị card thông tin kèm ảnh và link. |
| **Trần Thị Bình** | Test / failure path | Kịch bản kiểm thử gồm 5 test cases: budget quá thấp, đổi tiêu chí giữa chừng, điểm đến không có dữ liệu, gia đình có trẻ nhỏ, yêu cầu mập mờ (không nói rõ nơi đi). |
| **Lê Hoàng Nam** | Demo script / repo | File README hoàn chỉnh, slide demo 3 phút trình bày luồng Happy path (từ lúc nhập thông tin đến nhận đề xuất trọn gói) và cách xử lý khi budget không phù hợp (Low-confidence path). |
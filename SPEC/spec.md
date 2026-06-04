# Thin SPEC — Nhóm 2 (AI Explorer)

Bản đặc tả thiết kế hẹp (Thin SPEC) cập nhật theo luồng chức năng thực tế của prototype trong ngày Day 06.

## 1. Track, product/app và user

* **Track:** Travel  
* **Product/app thật:** TravelBot - AI Travel Planner Chatbot (Trợ lý lập kế hoạch du lịch thông minh)  
* **User cụ thể:** Người dùng bận rộn (nhân viên văn phòng, gia đình trẻ) muốn đi du lịch nhưng không có thời gian tìm hiểu về các danh lam thắng cảnh, khách sạn, phương tiện di chuyển tại địa phương. Họ cần một trợ lý AI thu thập nhanh thông tin hành trình, đề xuất trọn gói các điểm du lịch phù hợp, sau đó tự động tính toán và đưa ra 3 kịch bản chi phí (Tiết kiệm, Thông dụng, Tận hưởng).
* **Nhóm có phải user thật không? Nếu không, khác ở đâu?**  
  * **Có.** Các thành viên trong nhóm đều có nhu cầu đi du lịch nhưng thường rất bận và không có thời gian nghiên cứu kỹ về điểm đến, mất nhiều công sức để tự cân đối tài chính cho các lựa chọn khách sạn/xe cộ khác nhau.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Khảo sát nội bộ: 4/4 thành viên nhóm mất trung bình 3-5 giờ để lên kế hoạch cho một chuyến đi 2-3 ngày, phải mở 5-8 tab trình duyệt cùng lúc. | Trải nghiệm tự thử nghiệm | Người dùng bận rộn không có đủ thời gian nghiên cứu và so sánh giữa nhiều nguồn. Họ cần một nơi tổng hợp tất cả. | AI phải tự động tổng hợp thông tin từ nhiều nguồn (khách sạn, vé xe/máy bay, điểm du lịch) và trả về kết quả trọn gói trong một giao diện duy nhất. |
| Review trên App Store: Nhiều app du lịch chỉ giải quyết 1 khâu, buộc user phải nhảy qua nhiều app và tự cộng tay các chi phí. | App Store reviews | Người dùng gặp khó khăn trong việc tự cân đối ngân sách tổng thể của chuyến đi. | Chatbot phải cung cấp sẵn các kịch bản chi phí (Tiết kiệm, Thông dụng, Tận hưởng) đã cộng gộp tổng tiền và có link đặt vé trực tiếp. |

## 3. Pain statement

```text
User [người bận rộn muốn đi du lịch nhưng thiếu thời gian tìm hiểu] đang gặp khó ở [bước lập kế hoạch, tìm kiếm điểm đến và cân đối ngân sách],
vì [phải tra cứu trên quá nhiều nền tảng khác nhau (đặt phòng, đặt vé, tìm điểm tham quan) và tự tính toán thủ công các khoản chi phí tổng],
dẫn tới [mất nhiều giờ nghiên cứu, mệt mỏi vì phải tự so sánh giá, bỏ lỡ các địa điểm hay].
Bằng chứng chính là [các thành viên nhóm mất 3-5 giờ nghiên cứu cho mỗi chuyến đi, và user App Store phàn nàn phải nhảy qua nhiều app để hoàn tất & tự cộng chi phí một chuyến đi].
```

## 4. Build slice

```text
Cho [người bận rộn muốn lên kế hoạch du lịch nhanh chóng],
prototype sẽ dùng Form giao diện & AI để [thu thập 6 thông tin: Nơi đi, Nơi đến, Thời gian, Số người, Budget],
tạo ra [luồng 2 bước: (1) AI gợi ý danh sách địa điểm thăm quan và tự động check sẵn các điểm phù hợp nhất; (2) Dựa trên các điểm user chốt, AI phân tích dữ liệu thật và tính toán ra 3 Kịch bản chi phí: Tiết kiệm, Thông dụng, Tận hưởng gồm đủ Khách sạn, Xe cộ kèm link đặt],
và xử lý [failure mode - AI chọn dữ liệu ảo hoặc sai giá] bằng [kết nối chặt chẽ AI với cơ sở dữ liệu JSON tĩnh của hệ thống, bắt buộc AI chỉ được phép chọn đúng dữ liệu trong cơ sở dữ liệu hiện có (với 35 điểm đến)].
```

## 5. Auto/Aug decision

Chọn một:

* [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
* [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
* [ ] **Automation:** AI tự quyết và tự hành động.

* **Lý do chọn:** Việc đi du lịch mang tính cá nhân cao. AI chỉ phân tích Form để đề xuất các điểm tham quan và chọn ra 3 mức chi phí tối ưu nhất dựa trên ngân sách, nhưng chính người dùng mới là người tích/bỏ tích các địa điểm họ muốn đi, và click vào link để chốt đặt phòng/phương tiện.
* **Human role:** **decider** (Người chốt danh sách điểm đến và lựa chọn 1 trong 3 kịch bản chi phí) & **customizer** (Người điều chỉnh thông tin đầu vào).

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| **Happy** | User điền form. AI trả về form check-box các địa điểm ở nơi đến, đánh dấu sẵn các điểm phù hợp. User bấm Xác nhận. AI tính toán và hiển thị 3 Thẻ Kịch bản chi phí (Tiết kiệm, Thông dụng, Tận hưởng) với khách sạn, phương tiện, tổng tiền và link đặt thực tế. |
| **Low-confidence** | Điểm đến mà User nhập không có trong hệ thống dữ liệu (hiện tại bao phủ 35 điểm đến). AI sẽ thông báo không có dữ liệu cho địa điểm đó và liệt kê gợi ý một số điểm đến phổ biến đang có trong kho dữ liệu để người dùng đổi ý. |
| **Failure** | Budget mà User nhập vào quá thấp, không đủ để chi trả ngay cả ở kịch bản "Tiết kiệm" (dựa trên giá thực của khách sạn/xe rẻ nhất). AI sẽ phải cảnh báo ngân sách không khả thi và tư vấn user nâng budget hoặc đổi phương tiện. |
| **Correction** | User không thích các điểm du lịch AI check sẵn, họ tự tick/bỏ tick lại theo ý mình ở Bước 1. Sang Bước 2, AI tự động tính toán lại giá vé tương ứng với sự lựa chọn thủ công của User. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user [nhập form với một ngân sách cụ thể],
AI có thể [tự ảo giác (hallucinate) ra các mức giá không có thật hoặc tự bịa ra khách sạn/phương tiện không tồn tại để cố làm hài lòng ngân sách của user],
hậu quả là [user tin tưởng đặt theo đề xuất nhưng khi click vào link thì phát hiện giá ảo, không thể đặt được].
Prototype sẽ xử lý bằng [đưa toàn bộ dữ liệu 35 tỉnh thành vào System Prompt dưới dạng JSON, và thiết lập System Rule cực kỳ nghiêm ngặt bắt buộc AI chỉ được map đúng ID, Tên, Giá, và Link từ dữ liệu thật, không được phép "sáng tác"].
Owner kiểm thử path này là [Cao Việt Hoàng].
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| **Nguyễn Văn Chung** | Research / evidence | File JSON dữ liệu mẫu khổng lồ bao phủ 35 tỉnh thành (hotels.json, transport.json, attractions.json) với đầy đủ thông tin: tên, giá vé thật, link đặt vé, tag phù hợp. |
| **Cao Việt Hoàng** | SPEC & Prototype | Mã nguồn luồng 2 bước: Frontend tạo form nhập & form chọn địa điểm → Server GPT-4o-mini tính toán 3 kịch bản chi phí từ JSON → Giao diện hiển thị 3 Thẻ chi phí kèm link đặt, bảo mật API Key qua file .env. |
| **Võ Duy Bảo** | Test / failure path | Kịch bản kiểm thử: Thử nhập budget siêu thấp, nhập các điểm đến không có trong data, kiểm tra xem AI có check sẵn đúng điểm du lịch cho trẻ em không. |
| **Vũ Thành Danh** | Demo script / repo | File README hoàn chỉnh, slide demo trình bày luồng Happy path từ Form điền thông tin -> AI chọn điểm du lịch -> AI tính 3 option Tiết kiệm/Thông dụng/Tận hưởng. |
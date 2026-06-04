TravelBot AI - Thin SPEC & Core Flow (Checkpoint 1)
1. Mục tiêu MVP
Người dùng nhập điểm đến, số người và ngân sách. AI phân loại quy mô nhóm, đề xuất phương tiện phù hợp, ước tính chi phí và kiểm tra ngân sách.
2. User
Người muốn đi du lịch nội địa theo cá nhân, nhóm nhỏ hoặc đoàn lớn.
3. Input
{
  "destination": "Đà Nẵng",
  "group_size": 4,
  "budget": 8000000
}
4. AI Processing
•	Phân loại nhóm theo số người.
•	Đề xuất phương tiện phù hợp quy mô nhóm.
•	Ước tính chi phí.
•	So sánh với ngân sách.
•	Nếu vượt ngân sách thì gợi ý tối ưu.
5. Output
{
  "transport": "...",
  "hotel": "...",
  "attraction": "...",
  "total_cost": 7600000,
  "status": "within_budget"
}
6. Core Flow triển khai trước
User nhập thông tin -> AI phân loại nhóm -> AI chọn phương tiện -> AI tính chi phí -> AI kiểm tra ngân sách -> Hiển thị kết quả
7. Chưa triển khai ở Checkpoint 1
•	Link đặt phòng
•	Hình ảnh khách sạn
•	Khu vui chơi chi tiết
•	RAG
•	API đặt vé
•	AI Agent nhiều bước
•	Tìm kiếm realtime

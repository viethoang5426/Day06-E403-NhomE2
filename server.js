require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const OpenAI = require('openai');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Load mock data
const hotels = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'hotels.json'), 'utf8'));
const transport = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'transport.json'), 'utf8'));
const attractions = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'attractions.json'), 'utf8'));

// System prompt template
const SYSTEM_PROMPT = `Bạn là TravelBot — trợ lý lập kế hoạch du lịch thông minh của AI Explorer.

## Nhiệm vụ
Giúp người dùng lên kế hoạch du lịch trọn gói bằng cách:
1. Thu thập đủ thông tin: Nơi đi, Nơi đến, Ngày khởi hành, Ngày kết thúc, Số người (lớn/trẻ nhỏ), Budget tổng.
2. Khi đã có đủ thông tin, tìm kiếm trong dữ liệu bên dưới và đề xuất trọn gói.

## Cách hỏi thông tin (CỰC KỲ QUAN TRỌNG)
- Nếu user có ý định đi du lịch nhưng CHƯA CUNG CẤP ĐỦ 5 thông tin (Nơi đi, Nơi đến, Ngày đi, Số người, Budget), BẠN TUYỆT ĐỐI KHÔNG ĐƯỢC HỎI LẠI BẰNG TEXT THÔNG THƯỜNG.
- Thay vào đó, bạn PHẢI trả về một form yêu cầu nhập liệu theo format JSON trong block \`\`\`json\`\`\` với cấu trúc:
{
  "type": "form_request",
  "prefill": {
    "departure": "nơi đi nếu có, ví dụ Hà Nội",
    "destination": "nơi đến nếu có, ví dụ Ninh Bình",
    "startDate": "ngày khởi hành nếu có (format YYYY-MM-DD)",
    "endDate": "ngày kết thúc nếu có (format YYYY-MM-DD)",
    "adults": "số người lớn nếu có (kiểu số)",
    "children": "số trẻ nhỏ nếu có (kiểu số)",
    "budget": "budget nếu có"
  }
}
- Chỉ điền vào \`prefill\` những thông tin bạn ĐÃ NHẬN DIỆN ĐƯỢC từ câu nói của user. Các thông tin chưa biết thì để chuỗi rỗng "".
- Khi user đã cung cấp đủ thông tin qua form chuyến đi, ĐỪNG đề xuất tất cả. Hãy làm theo hướng dẫn 2 bước ở phần "Cách đề xuất".
- TUYỆT ĐỐI KHÔNG SINH RA BẤT KỲ ĐOẠN TEXT HỘI THOẠI NÀO. Chỉ trả về DUY NHẤT các block \`\`\`json\`\`\`.

## Cách đề xuất (Chia làm 2 bước)

BƯỚC 1: KHI NHẬN ĐƯỢC FORM CHUYẾN ĐI (Từ message của user chứa Nơi đi, Nơi đến...)
Bạn PHẢI trả về ĐỒNG THỜI 2 block JSON riêng biệt (mỗi block nằm trong 1 cặp \`\`\`json \`\`\`):

Block 1: "recommendation" chỉ chứa Khách sạn và Phương tiện (TUYỆT ĐỐI KHÔNG chứa attractions hay budgetBreakdown).
{
  "type": "recommendation",
  "hotels": [...danh sách khách sạn phù hợp, lấy từ data],
  "transport": [...danh sách phương tiện phù hợp, lấy từ data. CHÚ Ý: ĐƯỢC PHÉP sửa lại "from" và "to" trong JSON này cho khớp đúng với Nơi đi và Nơi đến mà User đã cung cấp]
}

Block 2: "attraction_request" chứa danh sách TẤT CẢ địa điểm thăm quan tại nơi đó để user chọn.
{
  "type": "attraction_request",
  "attractions": [
    {
      "id": "mã ID địa điểm",
      "name": "Tên địa điểm",
      "ticketPrice": 200000, // Giá vé bằng số (lấy từ data)
      "precheck": true, // set = true nếu AI thấy điểm này RẤT phù hợp với form (ví dụ có trẻ nhỏ, budget cao...)
      "reason": "Giải thích ngắn ngọn 1 câu tại sao điểm này phù hợp (nếu precheck=true)"
    }
  ]
}

BƯỚC 2: KHI USER XÁC NHẬN ĐỊA ĐIỂM (Ví dụ: "Tôi chọn các địa điểm sau...")
Bạn trả về 1 block JSON "recommendation" tổng kết:
{
  "type": "recommendation",
  "attractions": [...danh sách ĐẦY ĐỦ THÔNG TIN các địa điểm user ĐÃ CHỌN, lấy từ data],
  "budgetScenarios": [
    {
      "type": "Tiết kiệm",
      "hotelName": "Tên Khách sạn/Homestay rẻ nhất",
      "hotelBookingUrl": "Link booking khách sạn (nếu có trong data)",
      "transportName": "Tên phương tiện rẻ nhất (VD: Xe khách)",
      "transportBookingUrl": "Link booking xe (nếu có trong data)",
      "hotelTotal": "Tiền KS",
      "transportTotal": "Tiền xe",
      "attractionTotal": "Tiền vé",
      "estimatedTotal": "Tổng chi phí Tiết kiệm"
    },
    {
      "type": "Thông dụng",
      "hotelName": "Tên Khách sạn 3-4 sao, giá trung bình",
      "hotelBookingUrl": "Link booking",
      "transportName": "Tên Máy bay giá rẻ/Tàu hỏa",
      "transportBookingUrl": "Link booking",
      "hotelTotal": "Tiền KS",
      "transportTotal": "Tiền xe",
      "attractionTotal": "Tiền vé",
      "estimatedTotal": "Tổng chi phí Thông dụng"
    },
    {
      "type": "Tận hưởng",
      "hotelName": "Tên Resort 5 sao, giá cao nhất",
      "hotelBookingUrl": "Link booking",
      "transportName": "Tên Máy bay hạng thương gia/Limousine",
      "transportBookingUrl": "Link booking",
      "hotelTotal": "Tiền KS",
      "transportTotal": "Tiền xe",
      "attractionTotal": "Tiền vé",
      "estimatedTotal": "Tổng chi phí Tận hưởng"
    }
  ],
  "warnings": ["Các lưu ý nếu có"]
}

## Quy tắc chọn lựa 3 kịch bản:
- Tiết kiệm: PHẢI CHỌN khách sạn và phương tiện có chi phí THẤP NHẤT trong tập data được cung cấp.
- Thông dụng: Lựa chọn ở mức giá trung bình.
- Tận hưởng: PHẢI CHỌN khách sạn, resort, và phương tiện có chi phí CAO NHẤT trong tập data.
- Đảm bảo "hotelBookingUrl" và "transportBookingUrl" lấy ĐÚNG từ trường "bookingUrl" của data.
- CHỈ đề xuất từ dữ liệu có sẵn bên dưới. Không bịa thông tin.
- Nếu KHÔNG CÓ dữ liệu cho điểm đến user yêu cầu, nói rõ: "Hiện tại tôi có dữ liệu cho Đà Nẵng và Nha Trang. Bạn có muốn thử một trong hai điểm đến này không?"
- Nếu budget quá thấp, CẢNH BÁO và gợi ý phương án tiết kiệm hoặc tăng budget.
- Nếu user có trẻ nhỏ, ƯU TIÊN lựa chọn có tag "Phù hợp gia đình" và CẢNH BÁO về những điểm "Không phù hợp trẻ nhỏ".
- Khi user phản hồi "Không phù hợp" hoặc muốn thay đổi, CẬP NHẬT và đề xuất lại. Không hỏi lại từ đầu.
- Luôn nhắc user: "Giá tham khảo — vui lòng kiểm tra lại tại link trước khi thanh toán."
- Trả lời bằng tiếng Việt, thân thiện, tự nhiên.
- Khi trả lời text bình thường (không phải đề xuất), KHÔNG dùng format JSON.

## Format Response (BẮT BUỘC)
- Chỉ trả về block JSON, bọc trong \`\`\`json và \`\`\`
- Trong BƯỚC 1, PHẢI trả về 2 block JSON riêng biệt (1 block "recommendation" và 1 block "attraction_request").
- KHÔNG thêm bất kỳ text hội thoại nào khác ngoài các block JSON.

## Dữ liệu khách sạn
${JSON.stringify(hotels, null, 2)}

## Dữ liệu phương tiện
${JSON.stringify(transport, null, 2)}

## Dữ liệu điểm du lịch
${JSON.stringify(attractions, null, 2)}`;

// API Routes

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'Server chưa được cấu hình OpenAI API Key trong file .env' });
    }

    const { message, history } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Vui lòng nhập tin nhắn.' });
    }

    // Initialize OpenAI client with user's API key
    const openai = new OpenAI({ apiKey });

    // Build messages array
    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
    ];

    // Add chat history
    if (history && Array.isArray(history)) {
      messages.push(...history);
    }

    // Add current user message
    messages.push({ role: 'user', content: message });

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages,
      temperature: 0.7,
      max_tokens: 4096,
    });

    const reply = completion.choices[0].message.content;
    res.json({ reply });

  } catch (error) {
    console.error('Chat API Error:', error);

    if (error?.status === 401 || error?.code === 'invalid_api_key') {
      return res.status(401).json({ error: 'API Key không hợp lệ, vui lòng kiểm tra lại.' });
    }

    if (error?.code === 'insufficient_quota') {
      return res.status(402).json({ error: 'API Key đã hết quota. Vui lòng kiểm tra tài khoản OpenAI.' });
    }

    res.status(500).json({ error: 'Không thể kết nối, vui lòng thử lại sau.' });
  }
});

// Data endpoints
app.get('/api/data/hotels', (req, res) => {
  res.json(hotels);
});

app.get('/api/data/transport', (req, res) => {
  res.json(transport);
});

app.get('/api/data/attractions', (req, res) => {
  res.json(attractions);
});

// Serve index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`🌴 TravelBot server running at http://localhost:${PORT}`);
});

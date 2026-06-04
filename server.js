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
1. Thu thập đủ 5 thông tin: Nơi đi, Nơi đến, Ngày đi (và số ngày), Số người (người lớn + trẻ nhỏ nếu có), Budget tổng.
2. Khi đã có đủ 5 thông tin, tìm kiếm trong dữ liệu bên dưới và đề xuất trọn gói.

## Cách hỏi thông tin
- Hỏi từng thông tin một cách TỰ NHIÊN trong cuộc trò chuyện, KHÔNG hỏi dồn 5 câu cùng lúc.
- Nếu user cung cấp nhiều thông tin trong 1 câu, ghi nhận tất cả và chỉ hỏi thêm phần còn thiếu.
- Khi đã đủ 5 thông tin, XÁC NHẬN lại với user trước khi đề xuất.

## Cách đề xuất
Khi đủ thông tin, trả về đề xuất theo format JSON trong block \`\`\`json\`\`\` với cấu trúc:

{
  "type": "recommendation",
  "summary": "Tóm tắt hành trình",
  "hotels": [...danh sách khách sạn phù hợp, mỗi khách sạn gồm đầy đủ thông tin từ data],
  "transport": [...danh sách phương tiện phù hợp],
  "attractions": [...danh sách điểm du lịch phù hợp],
  "budgetBreakdown": {
    "hotelTotal": "tổng tiền khách sạn (giá/đêm × số đêm)",
    "transportTotal": "tổng tiền phương tiện (giá × số người)",
    "attractionTotal": "tổng tiền vé tham quan",
    "estimatedTotal": "tổng ước tính",
    "remainingBudget": "budget còn lại"
  },
  "warnings": ["các cảnh báo nếu có, ví dụ budget ít, điểm du lịch không phù hợp trẻ nhỏ"]
}

## Quy tắc quan trọng
- CHỈ đề xuất từ dữ liệu có sẵn bên dưới. Không bịa thông tin.
- Nếu KHÔNG CÓ dữ liệu cho điểm đến user yêu cầu, nói rõ: "Hiện tại tôi có dữ liệu cho Đà Nẵng và Nha Trang. Bạn có muốn thử một trong hai điểm đến này không?"
- Nếu budget quá thấp, CẢNH BÁO và gợi ý phương án tiết kiệm hoặc tăng budget.
- Nếu user có trẻ nhỏ, ƯU TIÊN lựa chọn có tag "Phù hợp gia đình" và CẢNH BÁO về những điểm "Không phù hợp trẻ nhỏ".
- Khi user phản hồi "Không phù hợp" hoặc muốn thay đổi, CẬP NHẬT và đề xuất lại. Không hỏi lại từ đầu.
- Luôn nhắc user: "Giá tham khảo — vui lòng kiểm tra lại tại link trước khi thanh toán."
- Trả lời bằng tiếng Việt, thân thiện, tự nhiên.
- Khi trả lời text bình thường (không phải đề xuất), KHÔNG dùng format JSON.

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
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'API Key không hợp lệ. Vui lòng nhập API Key của bạn.' });
    }

    const apiKey = authHeader.replace('Bearer ', '');
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

# TravelBot — Flow Diagram (Mermaid)

> Xem trên **GitHub**, **VS Code** (extension Mermaid), hoặc [mermaid.live](https://mermaid.live).  
> File diagram thuần: [`flow.mmd`](./flow.mmd) · Export PNG: `npx @mermaid-js/mermaid-cli -i Flow/flow.mmd -o Flow/flow.png`

---

## 1. Luồng tổng quan (3 Phase)

```mermaid
flowchart TB
    classDef user fill:#ffc857,stroke:#d4a017,color:#1a1a1a
    classDef ui fill:#00d4ff,stroke:#0096c7,color:#0a0e17
    classDef api fill:#a78bfa,stroke:#7c3aed,color:#fff
    classDef llm fill:#34d399,stroke:#059669,color:#0a0e17
    classDef data fill:#fb923c,stroke:#ea580c,color:#0a0e17
    classDef json fill:#1e293b,stroke:#34d399,color:#34d399
    classDef ext fill:#f87171,stroke:#dc2626,color:#fff
    classDef decision fill:#334155,stroke:#64748b,color:#e2e8f0

    subgraph P0["━━ Phase 0 · Khởi động ━━"]
        U0["👤 Chat tự do / Quick action<br/>VD: Tôi muốn đi Đà Nẵng"]:::user
        UI0["🖥️ POST /api/chat<br/>message + history[]"]:::ui
        API0["⚙️ server.js<br/>Load .env · Embed data JSON vào prompt"]:::api
        LLM0["🧠 GPT-4o-mini<br/>Phân tích intent"]:::llm
        D0{Đủ 6 trường<br/>chuyến đi?}:::decision
        J0["📋 JSON form_request<br/>prefill từ câu user"]:::json
        F0["🖥️ Form: đi/đến, ngày, người, budget"]:::ui
        U0 --> UI0 --> API0 --> LLM0 --> D0
        D0 -->|Không| J0 --> F0
    end

    subgraph P1["━━ Phase 1 · KS, Vận chuyển, Chọn điểm ━━"]
        U1["👤 Submit form chuyến đi"]:::user
        LLM1["🧠 Grounding CHỈ trong data<br/>Tag gia đình · Cảnh báo budget"]:::llm
        J1a["📋 recommendation<br/>hotels[] + transport[]"]:::json
        J1b["📋 attraction_request<br/>id, ticketPrice, precheck, reason"]:::json
        UI1a["🖥️ Card khách sạn<br/>giá/đêm · bookingUrl"]:::ui
        UI1b["🖥️ Card xe/máy bay<br/>from/to · giá · link"]:::ui
        UI1c["🖥️ Checkbox chọn điểm tham quan"]:::ui
        DB1["📂 attractions.json<br/>105 điểm · ~39 tỉnh"]:::data
        U1b["👤 Tick / bỏ tick điểm"]:::user
        F0 --> U1
        D0 -->|Đủ trong 1 message| U1
        U1 --> LLM1
        LLM1 --> J1a & J1b
        J1a --> UI1a & UI1b
        J1b --> UI1c
        DB1 -.-> LLM1
        UI1c --> U1b
    end

    subgraph P2["━━ Phase 2 · Ngân sách & Booking ━━"]
        U2["👤 Xác nhận: Tôi chọn các điểm sau..."]:::user
        LLM2["🧠 Tính 3 kịch bản<br/>Min / TB / Max trong data"]:::llm
        J2["📋 recommendation<br/>attractions[] · budgetScenarios[3] · warnings[]"]:::json
        UI2["🖥️ Tiết kiệm | Thông dụng | Tận hưởng"]:::ui
        DIS["⚠️ Disclaimer: giá tham khảo"]:::ui
        EXT["🔗 Booking ngoài app<br/>hotelBookingUrl · transportBookingUrl"]:::ext
        U1b --> U2 --> LLM2 --> J2 --> UI2 --> DIS --> EXT
    end
```

---

## 2. Sequence diagram — Happy path

```mermaid
sequenceDiagram
    autonumber
    box rgba(255,200,87,0.15) User
        actor U as Người dùng
    end
    box rgba(0,212,255,0.12) Client
        participant UI as TravelBot UI
    end
    box rgba(167,139,250,0.12) Server
        participant API as Express /api/chat
    end
    box rgba(52,211,153,0.12) AI
        participant LLM as GPT-4o-mini
    end
    box rgba(251,146,60,0.12) Data
        participant DB as data/*.json
    end

    U->>UI: "Tôi muốn đi Đà Nẵng"
    UI->>API: POST { message, history }
    API->>DB: hotels · transport · attractions
    API->>LLM: system prompt + full JSON data
    Note over LLM: Thiếu thông tin → không hỏi text
    LLM-->>UI: ```json form_request + prefill ```
    UI-->>U: Hiển thị Form chuyến đi

    U->>UI: Điền & Gửi form (6 trường)
    UI->>API: Structured trip message
    LLM-->>UI: ```json recommendation (KS + xe) ```
    LLM-->>UI: ```json attraction_request ```
    UI-->>U: Cards KS · Cards xe · Checkbox điểm

    U->>UI: Chọn điểm tham quan
    UI->>API: "Tôi chọn các điểm sau: ..."
    LLM-->>UI: ```json budgetScenarios x3 + warnings ```
    UI-->>U: Bảng ngân sách + disclaimer
    U->>U: Click link đặt phòng / vé (ngoài app)
```

---

## 3. JSON contract (luồng dữ liệu)

```mermaid
flowchart LR
    classDef t fill:#1e293b,stroke:#34d399,color:#a7f3d0

    A[User message] --> B{Parser script.js}
    B -->|type| C[form_request]:::t
    B -->|type| D[recommendation bước 1]:::t
    B -->|type| E[attraction_request]:::t
    B -->|type| F[recommendation bước 2]:::t

    C --> C1[prefill: departure, destination,<br/>startDate, endDate, adults,<br/>children, budget]
    D --> D1[hotels, transport]
    E --> E1[attractions: id, name,<br/>ticketPrice, precheck, reason]
    F --> F1[attractions, budgetScenarios,<br/>warnings]
```

---

## 4. Bốn đường đi (Trust & UX)

```mermaid
flowchart TB
    classDef happy fill:#064e3b,stroke:#34d399,color:#d1fae5
    classDef warn fill:#422006,stroke:#ffc857,color:#fef3c7
    classDef fail fill:#450a0a,stroke:#f87171,color:#fecaca
    classDef fix fill:#2e1065,stroke:#a78bfa,color:#ede9fe

    START(["User bắt đầu chat"]) --> PATH

    subgraph PATH["Chọn nhánh"]
        H["✅ Đường thuận<br/>Đủ info · Có data · Budget OK"]:::happy
        L["⚠️ AI không chắc<br/>Budget quá thấp"]:::warn
        FA["❌ AI sai / Không phù hợp<br/>KS quá đắt"]:::fail
        CO["✏️ User sửa<br/>Đổi điểm đến · Thêm người"]:::fix
    end

    H --> H1["Form → KS+xe → Chọn điểm → 3 budget → Link booking"]
    L --> L1["warnings[] · Ưu tiên KS rẻ, xe khách<br/>Gợi ý tăng budget / đổi city"]
    FA --> F1["User: Không phù hợp<br/>AI đề xuất lại · Giữ history"]
    CO --> C1["Prefill form mới · Recommendation mới"]
```

---

## 5. Nhánh lỗi & kiểm soát

```mermaid
flowchart TD
    classDef err fill:#450a0a,stroke:#f87171,color:#fecaca
    classDef ok fill:#064e3b,stroke:#34d399,color:#d1fae5
    classDef mid fill:#422006,stroke:#ffc857,color:#fef3c7

    IN([Request vào LLM]) --> C1{Điểm đến trong<br/>supportedCities?}
    C1 -->|Không| E1["🚫 Liệt kê ~39 tỉnh có data<br/>Không bịa KS/điểm"]:::err
    C1 -->|Có| C2{Budget khả thi<br/>vs giá min?}
    C2 -->|Không| E2["⚠️ warnings + kịch bản Tiết kiệm"]:::mid
    C2 -->|Có| C3{Có trẻ nhỏ?}
    C3 -->|Có| E3["👶 precheck gia đình<br/>Cảnh báo Không phù hợp trẻ nhỏ"]:::mid
    C3 -->|Không| OK["▶ Phase 1–2 bình thường"]:::ok

    API([POST /api/chat]) --> A1{OPENAI_API_KEY?}
    A1 -->|Thiếu| A500[500 Server chưa cấu hình]:::err
    A1 -->|Sai| A401[401 Key không hợp lệ]:::err
    A1 -->|Hết quota| A402[402 Hết quota]:::err
    A1 -->|OK| IN
```

---

## 6. Kiến trúc hệ thống

```mermaid
flowchart TB
    subgraph CLIENT["Browser · public/"]
        HTML[index.html]
        JS[script.js<br/>parse JSON blocks · forms · cards]
        CSS[style.css]
        HTML --> JS
    end

    subgraph SERVER["Node.js · server.js"]
        ENV[.env OPENAI_API_KEY]
        PROMPT[System prompt + supportedCities]
        CHAT[POST /api/chat]
        REST[GET /api/data/*]
        ENV --> CHAT
        PROMPT --> CHAT
    end

    subgraph STORE["data/"]
        H[hotels.json · 193]
        T[transport.json · 96]
        A[attractions.json · 105]
    end

    subgraph EXT["Ngoài prototype"]
        OAI[OpenAI API]
        BOOK[Booking / Airline websites]
    end

    JS <-->|JSON| CHAT
    CHAT --> OAI
    STORE --> PROMPT
    JS --> BOOK
```

---

## 7. Quyết định Augment (không auto-book)

```mermaid
flowchart LR
    AI[AI gợi ý + tính budget] --> USER[User quyết định]
    USER --> CHON[Chọn điểm tham quan]
    USER --> CLICK[Click link booking]
    CLICK --> PAY[Thanh toán trên site đối tác]
    AI -.->|Không| PAY
```

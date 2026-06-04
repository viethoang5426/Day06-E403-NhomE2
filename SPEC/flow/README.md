# Flow — TravelBot (Mermaid Diagram)

| File | Mô tả |
|------|--------|
| **[flow.md](./flow.md)** | Đầy đủ 7 diagram: tổng quan, sequence, JSON, 4 đường đi, lỗi, kiến trúc |
| **[flow.mmd](./flow.mmd)** | Diagram chính 3 phase (1 file — dùng export PNG) |

## Cách xem

1. **GitHub** — mở `flow.md`, Mermaid render tự động  
2. **VS Code** — extension [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)  
3. **Online** — copy nội dung vào [mermaid.live](https://mermaid.live)

## Export PNG (`flow.png`)

```bash
npx @mermaid-js/mermaid-cli -i Flow/flow.mmd -o Flow/flow.png -b transparent
```

Hoặc paste `flow.mmd` vào mermaid.live → Export PNG/SVG.

## Nội dung

- Phase 0: `form_request`  
- Phase 1: `recommendation` (KS+xe) + `attraction_request`  
- Phase 2: `budgetScenarios` × 3 + booking ngoài app  
- Trust paths + error branches  

Cập nhật theo `spec/spec.md` v2.0.

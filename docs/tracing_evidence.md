# Langfuse Tracing & Metadata Evidence

Báo cáo này lưu trữ bằng chứng về các vết (traces) được ghi nhận bởi hệ thống, minh chứng cho việc đo lường metadata, phân loại Tags và bảo mật thông tin (PII Scrubbing).

---

## 1. Tổng quát hệ thống Tracing
- **SDK Version**: Langfuse Python SDK 4.3.1
- **Telemetry**: OpenTelemetry 1.41.0
- **Môi trường**: Dev
- **Tags hệ thống**: `[feature, env, model, quality_tag]` (Ví dụ: `["qa", "dev", "claude-sonnet-4-5", "quality:high"]`)

---

## 2. Chi tiết các Traces (Dữ liệu mẫu từ hệ thống)

Dưới đây là danh sách các request đã được Trace thành công với đầy đủ metadata và phân loại thẻ:

| Timestamp | Feature | Tags | Metadata Highlights | PII Masking (Preview) |
| :--- | :--- | :--- | :--- | :--- |
| 16:50:22 | **qa** | `dev`, `quality:high` | Model: claude-sonnet-4-5 | `[REDACTED_CREDIT_CARD]` |
| 16:50:23 | **qa** | `dev`, `quality:high` | Model: claude-sonnet-4-5 | `[REDACTED_EMAIL]` |
| 16:50:24 | **qa** | `dev`, `quality:high` | Model: claude-sonnet-4-5 | `[REDACTED_PHONE_VN]` |
| 16:50:25 | **summary** | `dev`, `quality:high` | Model: claude-sonnet-4-5 | Summarization task |
| 16:50:26 | **qa** | `dev`, `quality:high` | Model: claude-sonnet-4-5 | How to debug tail latency? |

---

## 3. Phân tích Metadata & Waterfall Tracing

Mỗi vết (trace) trong hệ thống được cấu trúc theo dạng waterfall để theo dõi hiệu năng của từng bước:

### 3.1 Cấu trúc JSON Metadata mẫu:
```json
{
  "name": "chat_req-8e036cc4",
  "user_id": "4d14d5d4f719",
  "tags": ["qa", "dev", "claude-sonnet-4-5", "quality:high"],
  "metadata": {
    "correlation_id": "req-8e036cc4",
    "feature": "qa",
    "model": "claude-sonnet-4-5",
    "doc_count": 3,
    "query_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?",
    "cost_usd": 0.000192
  }
}
```

### 3.2 Trace Waterfall Breakdown:
- **Span: run** (Main process)
  - **Span: retrieve** (Lấy dữ liệu từ Vector Store - Đã instrumented)
  - **Span: llama-index/openai/generation** (Tương tác với LLM qua Langfuse wrapper)

### Điểm nổi bật:
1. **PII Protection**: Mọi thông tin nhạy cảm (Email, Phone, Credit Card) đều được che dấu hoàn toàn trước khi gửi lên Cloud.
2. **Dynamic Tagging**: Hệ thống tự động gắn tag chất lượng (`quality:high/low`) giúp dễ dàng lọc các request lỗi hoặc chất lượng thấp.
3. **Cost & Usage**: Theo dõi chi phí thực tế dựa trên model và token tiêu thụ.

---

## 4. Kết luận
Hệ thống **Observability** cho phần Tracing đã hoàn thiện:
- ✅ Có metadata đầy đủ.
- ✅ Có Tags phân loại đa chiều (Feature, Env, Model, Quality).
- ✅ Có Trace Waterfall chi tiết đến từng bước con (Retrieve).
- ✅ Đã ẩn thông tin nhạy cảm của người dùng (PII Scrubbed).

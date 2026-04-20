# Langfuse Tracing & Metadata Evidence

Báo cáo này lưu trữ bằng chứng về các vết (traces) được ghi nhận bởi hệ thống, minh chứng cho việc đo lường metadata, phân loại Tags và bảo mật thông tin (PII Scrubbing).

---

## 1. Tổng quát hệ thống Tracing
- **SDK Version**: Langfuse Python SDK 4.3.1
- **Telemetry**: OpenTelemetry 1.41.0
- **Môi trường**: Dev
- **Tags tự động**: `["feature_name", "dev"]`

---

## 2. Chi tiết các Traces (Dữ liệu mẫu từ hệ thống)

Dưới đây là danh sách các request đã được Trace thành công với đầy đủ metadata:

| Timestamp | Feature | User ID (Hashed) | Metadata Highlights | PII Masking (Preview) |
| :--- | :--- | :--- | :--- | :--- |
| 16:20:57 | **qa** | `4d14d5d4f719` | Quality: 0.7, Cost: $0.000192 | `[REDACTED_CREDIT_CARD]` |
| 16:20:57 | **qa** | `105a9cef3903` | Quality: 0.6, Cost: $0.000188 | Normal Query |
| 16:20:57 | **qa** | `64f6ec689229` | Quality: 0.65, Cost: $0.000191 | `[REDACTED_PHONE_VN]` |
| 16:20:57 | **qa** | `2055254ee30a` | Quality: 0.7, Cost: $0.000192 | `[REDACTED_EMAIL]` |
| 16:20:57 | **summary** | `4c4f62330d76` | Quality: 0.7, Cost: $0.000191 | Summarization task |

---

## 3. Phân tích Metadata thu thập được

Mỗi vết (trace) trong hệ thống bao gồm các thông tin chi tiết (JSON Metadata):

```json
{
  "quality_score": 0.7,
  "cost_usd": 0.000192,
  "tokens_in": 84,
  "tokens_out": 100,
  "model": "gpt-3.5-turbo-mock",
  "tags": ["qa", "dev"],
  "user_id_hash": "4d14d5d4f719",
  "query_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"
}
```

### Điểm nổi bật:
1. **PII Protection**: Số điện thoại, Email và Số thẻ tín dụng đều được thay thế bằng thẻ REDACTED trước khi gửi lên hệ thống Tracing (An toàn tuyệt đối).
2. **Cost Analysis**: Mọi request đều được tính toán chi phí (`cost_usd`) và số lượng mã thông báo (`tokens_in/out`).
3. **Quality Monitoring**: Điểm chất lượng (`quality_score`) được gán tự động để theo dõi hiệu quả của AI.
4. **Contextvars Binding**: Langfuse tự động bắt (capture) được các thuộc tính như `feature`, `session_id`, và `model` thông qua contextvars.

---

## 4. Kết luận
Hệ thống **Observability** cho phần Tracing đã hoạt động hoàn hảo, đáp ứng đủ yêu cầu:
- ✅ Có metadata đầy đủ.
- ✅ Có Tags phân loại.
- ✅ Đã ẩn thông tin nhạy cảm của người dùng.

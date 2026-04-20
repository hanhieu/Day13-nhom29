# Alert Summary & Incident Evidence Report

Báo cáo này tổng hợp các Alert Rules đã thiết lập, hướng dẫn xử lý (Runbook) và bằng chứng thực tế từ hệ thống log.

---

## 1. Danh sách Alert Rules (Configuration)

Dưới đây là các ngưỡng cảnh báo (SLO) đã được thiết lập trong `config/alert_rules.yaml`:

| Cảnh báo | Mức độ | Điều kiện (Trigger) | Mục tiêu |
| :--- | :---: | :--- | :--- |
| **High Latency P95** | P2 | `latency_p95_ms > 3000` cho 5m | Đảm bảo tốc độ phản hồi 99.5% |
| **Critical Error Rate** | P0 | `error_rate_pct > 10` cho 1m | Phát hiện sập hệ thống ngay lập tức |
| **High Error Rate** | P1 | `error_rate_pct > 2` cho 3m | Đảm bảo tỷ lệ lỗi < 2% |
| **Daily Cost Budget** | P1 | `daily_cost_usd > 2.5` cho 1h | Kiểm soát chi phí OpenAI API |
| **Low Quality Score** | P2 | `quality_score_avg < 0.75` cho 10m| Đảm bảo chất lượng AI trả lời |
| **No Traffic** | P2 | `requests_per_minute == 0` cho 5m | Phát hiện lỗi kết nối/mạng |

---

## 2. Bằng chứng thực tế từ Logs (Live Evidence)

Dưới đây là dữ liệu log thực tế được trích xuất sau khi kích hoạt các kịch bản lỗi:

### A. Kịch bản: Latency cao (rag_slow)
*Ghi nhận từ đợt chạy Load Test 1:*
```text
[200] req-f708cb19 | latency: 20030.9ms | status: OK
[200] req-31eade76 | latency: 25033.2ms | status: OK
... (Latency vượt ngưỡng P95 3000ms)
```
**Phân tích:** Log cho thấy Latency đạt tới ~25 giây, vi phạm SLO 3000ms. Alert `high_latency_p95` sẽ được kích hoạt.

### B. Kịch bản: Lỗi công cụ (tool_fail)
*Ghi nhận từ đợt chạy Load Test 2:*
```json
{
  "service": "api",
  "error_type": "RuntimeError",
  "payload": { "detail": "Vector store timeout" },
  "event": "request_failed",
  "level": "error"
}
```
**Phân tích:** Hệ thống ghi nhận chuỗi lỗi `500`. Với 10/10 request lỗi, tỷ lệ lỗi là 100%, vượt ngưỡng 10% của Alert `critical_error_rate` (P0).

---

## 3. Hướng dẫn xử lý (Runbook Summary)

Chi tiết cách xử lý khi Alert nổ (đã cập nhật tại `docs/alerts.md`):

1. **Với Latency cao:** Kiểm tra trace trong Langfuse để xem RAG hay LLM chậm -> Tắt `rag_slow` nếu là sự cố giả lập.
2. **Với Error Rate cao:** Kiểm tra `error_type` trong log -> Kiểm tra API Key OpenAI hoặc hạ tầng Vector DB.
3. **Với Cost cao:** Kiểm tra metadata `tokens_in` trong Langfuse để tìm session/user đang spam request nặng.

---

## 4. Xác nhận Tracing (Langfuse)
Hệ thống đã được cấu hình với decorator `@observe()` và gửi metadata đầy đủ bao gồm:
- `user_id_hash` (PII Scrubbing)
- `session_id`
- `cost_usd`
- `quality_score`

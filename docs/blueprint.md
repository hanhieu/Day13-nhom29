# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: NHÓM 20.5
- [REPO_URL]: https://github.com/hanhieu/Day13-nhom20.5
- [MEMBERS]:
  - Member A: Phan Anh Khôi - 2A202600276 | Role: Logging & PII
  - Member B: Nguyễn Hữu Quang - 2A202600167 | Role: Tracing & Tags
  - Member C: Nguyễn Hữu Huy - 2A202600166 | Role: SLO & Alerts
  - Member D: Nguyễn Gia Bảo - 2A202600156 | Role: Load test + Incident injection
  - Member E: Hàn Quang Hiếu - 2A202600056 | Role: Dashboard + Evidence
  - Member F: Nguyễn Bình Thành - 2A202600138 | Role: Blueprint + Demo lead
---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $2.5/day | 1d | |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)

### Scenario 1: `rag_slow`
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 tăng từ ~166ms lên ~2678ms (+1513%). Error rate vẫn 0% — requests không fail nhưng phản hồi cực chậm. Dashboard cho thấy latency spike rõ rệt trong time-series.
- [ROOT_CAUSE_PROVED_BY]: Trace waterfall cho thấy span `rag_retrieval` chiếm >2500ms (95% tổng thời gian), trong khi span `llm_generation` vẫn ~150ms. Log line `response_sent` có `latency_ms > 2600` nhưng không có error_type. Metadata trong span: `rag_slow_active: true`.
- [FIX_ACTION]: Disable incident toggle `rag_slow` qua API `/incidents/rag_slow/disable`. Latency Recovery về ~155ms ngay lập tức.
- [PREVENTIVE_MEASURE]: Đặt alert rule `latency_p95_ms > 5000 for 30m` (Severity P2). Thiết lập timeout cho RAG retrieval để fail-fast thay vì block. Xem runbook: `docs/alerts.md#1-high-latency-p95`.

### Scenario 2: `tool_fail`
- [SCENARIO_NAME]: tool_fail
- [SYMPTOMS_OBSERVED]: Error rate tăng từ 0% lên 100%. Tất cả requests trả về HTTP 500. Cost giảm về $0 (không có token nào được xử lý).
- [ROOT_CAUSE_PROVED_BY]: Logs cho thấy `error_type: "RuntimeError"`, `detail: "Vector store timeout"` ở tất cả request. Trace có span `rag_retrieval` bị fail với exception. Không có span `llm_generation` vì pipeline dừng tại RAG.
- [FIX_ACTION]: Disable incident toggle `tool_fail`. Recovery cho thấy error rate trở về 0% ngay lập tức.
- [PREVENTIVE_MEASURE]: Alert rule `error_rate_pct > 5 for 5m` (Severity P1). Implement retry logic hoặc fallback retrieval source. Xem runbook: `docs/alerts.md#2-high-error-rate`.

### Scenario 3: `cost_spike`
- [SCENARIO_NAME]: cost_spike
- [SYMPTOMS_OBSERVED]: Total cost tăng từ $0.030 lên $0.123 (+300%). tokens_out tăng từ ~1954 lên ~8132 (~4x). Latency gần như không đổi (+0.8%) — incident này "im lặng" về performance nhưng đốt budget.
- [ROOT_CAUSE_PROVED_BY]: Trace span `llm_generation` cho thấy `usage.output: 400-720 tokens` (bình thường ~80-180). Metadata: `cost_spike_active: true`. tokens_in không thay đổi → root cause nằm ở output generation, không phải prompt.
- [FIX_ACTION]: Disable incident toggle `cost_spike`. Recovery cho thấy cost trở về ~$0.031 ngay lập tức.
- [PREVENTIVE_MEASURE]: Alert rule `hourly_cost_usd > 2x_baseline for 15m` (Severity P2). Monitor tokens_out/tokens_in ratio. Xem runbook: `docs/alerts.md#3-cost-budget-spike`.

---

## 5. Individual Contributions & Evidence

### Phan Anh Khôi - 2A202600276 (Member A)
- [TASKS_COMPLETED]: Implemented Correlation IDs middleware, enriched structured logs with context, and built the PII scrubber for sensitive data directly inside `app/logging_config.py` and `app/pii.py`.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Logging)

### Nguyễn Hữu Quang - 2A202600167 (Member B)
- [TASKS_COMPLETED]: Instrumented Langfuse tracing using the `@observe` decorator, tracked pipeline inputs/outputs, and propagated tags and metadata across application spans.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Tracing)

### Nguyễn Hữu Huy - 2A202600166 (Member C)
- [TASKS_COMPLETED]: Configured SLO targets (`config/slo.yaml`) and Alerting rules (`config/alert_rules.yaml`). Drafted runbook documentation in `docs/alerts.md` for incident response.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for SLO & Alerts)

### Nguyễn Gia Bảo - 2A202600156 (Member D)
- [TASKS_COMPLETED]:
  1. **Nâng cấp `scripts/load_test.py`**: Xây dựng `LoadTestReport` class thu thập toàn bộ dữ liệu mỗi request (latency, tokens, cost, error). In summary report với P50/P95/P99 latency, error rate, total cost. Thêm `--rounds` (lặp queries N lần), `--delay`, `--concurrency`, `--base-url`. Sửa lỗi BASE_URL không đồng nhất (8001→8000). Export `run_load_test()` dưới dạng hàm để tái sử dụng.
  2. **Nâng cấp `scripts/inject_incident.py`**: Thêm `--status` để xem trạng thái ON/OFF của tất cả incidents, `--all` để bật/tắt tất cả scenarios cùng lúc, `--base-url` và error handling cho connection failures.
  3. **Tạo mới `scripts/incident_demo.py`**: Script tự động hóa quy trình Incident Response gồm 6 phases — (1) Baseline traffic → (2) Inject incident → (3) Traffic under incident → (4) Disable incident → (5) Recovery traffic → (6) In bảng so sánh Baseline vs Incident vs Recovery với delta %. Hỗ trợ `--scenario` (chạy 1 scenario), `--all` (chạy cả 3), `--rounds`, `--concurrency`. Cung cấp Root Cause Hints cho từng scenario.
  4. **Bổ sung `data/sample_queries.jsonl`**: Thêm 5 queries mới (u11–u15) tăng diversity và coverage PII (CCCD, email, credit card).
  5. **Chạy full test cả 3 scenarios** (`rag_slow`, `tool_fail`, `cost_spike`), thu thập bằng chứng before/after cho Incident Response section.
  
  **Giải thích kỹ thuật — Cách tính P95 trong LoadTestReport**:
  Thuật toán percentile sắp xếp mảng latency tăng dần, tính index = round((p/100) × N + 0.5) − 1, clamp vào [0, N−1]. Ví dụ với 15 values, P95 lấy phần tử thứ 15 (index 14) = giá trị lớn nhất. Với 100 values, P95 lấy phần tử thứ 95 — nghĩa là 95% requests nhanh hơn hoặc bằng giá trị này. Đây là SLI chính cho latency SLO.

- [EVIDENCE_LINK]: Commit `054d673` trên nhánh `roleD` — PR #1 merged vào main (`6fc68a2`)

### Hàn Quang Hiếu - 2A202600056 (Member E)
- [TASKS_COMPLETED]: Built and configured the 6-panel frontend observability dashboard (`dashboard.html` and `dashboard.json`) mapping to `/metrics`. Collected metric evidence and screenshots for the report.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Dashboard)

### Nguyễn Bình Thành - 2A202600138 (Member F)
- [TASKS_COMPLETED]: Compiled the Blueprint report, synthesized the Root Cause Analysis (RCA) in the Incident Response section, and prepared the Demo script to showcase the system.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Blueprint)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Sử dụng `scripts/incident_demo.py --scenario cost_spike` để chứng minh cost tăng +300% khi incident xảy ra (từ $0.030 lên $0.123 cho 15 requests). Sau khi disable, cost Recovery về $0.031 ngay lập tức. Bảng so sánh before/after được in tự động bởi script, cung cấp evidence rõ ràng cho cost monitoring. (Evidence: output của `incident_demo.py`, commit `054d673`)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: Script `incident_demo.py` là custom automation tool tự động hóa toàn bộ quy trình Incident Response (6 phases), không cần thao tác thủ công. Chạy `python scripts/incident_demo.py --all` để demo tất cả 3 scenarios liên tiếp với full comparison. (Evidence: commit `054d673`, file `scripts/incident_demo.py`)

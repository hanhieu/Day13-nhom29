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
- [SCENARIO_NAME]: (e.g., rag_slow)
- [SYMPTOMS_OBSERVED]: 
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: 
- [PREVENTIVE_MEASURE]: 

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
- [TASKS_COMPLETED]: Developed load testing scripts (`scripts/load_test.py`) to benchmark parallel bottlenecks and executed incident injection scenarios (`rag_slow`) to validate system observability.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Load Test & Incidents)

### Hàn Quang Hiếu - 2A202600056 (Member E)
- [TASKS_COMPLETED]: Built and configured the 6-panel frontend observability dashboard (`dashboard.html` and `dashboard.json`) mapping to `/metrics`. Collected metric evidence and screenshots for the report.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Dashboard)

### Nguyễn Bình Thành - 2A202600138 (Member F)
- [TASKS_COMPLETED]: Compiled the Blueprint report, synthesized the Root Cause Analysis (RCA) in the Incident Response section, and prepared the Demo script to showcase the system.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Blueprint)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)

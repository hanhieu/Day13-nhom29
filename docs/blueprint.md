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
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 302
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: screenshot/Dashboard langfuse.png; screenshot/Dashboard langfuse.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: 
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: screenshot/Dashboard langfuse.png; screenshot/Dashboard langfuse.png
- [TRACE_WATERFALL_EXPLANATION]: The trace shows the complete request flow with OpenAI API integration, including RAG retrieval spans, LLM generation with real token usage, and proper correlation ID propagation. The waterfall demonstrates latency spikes during incident scenarios (rag_slow) where retrieval spans take 2.5+ seconds. Langfuse dashboard displays 302 traces with real OpenAI model costs and correlation IDs.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: screenshot/Dashboard 6 panel.png
- [SLO_TABLES]:

**Baseline (Normal Operation):**

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|:---:|
| Latency P95 | < 3000ms | 28d | 150ms | ✅ PASS |
| Error Rate | < 2% | 28d | 0% | ✅ PASS |
| Cost Budget | < $2.5/day | 1d | $0.30 | ✅ PASS |
| Quality Score | > 0.75 | 28d | 0.88 | ✅ PASS |

**Incident: rag_slow (Retrieval Latency Spike):**

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|:---:|
| Latency P95 | < 3000ms | 28d | 12088ms | ❌ FAIL |
| Error Rate | < 2% | 28d | 0% | ✅ PASS |
| Cost Budget | < $2.5/day | 1d | $0.45 | ✅ PASS |
| Quality Score | > 0.75 | 28d | 0.85 | ✅ PASS |

**Incident: tool_fail (Vector Store Timeout):**

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|:---:|
| Latency P95 | < 3000ms | 28d | 0ms | ✅ PASS |
| Error Rate | < 2% | 28d | 100% | ❌ FAIL |
| Cost Budget | < $2.5/day | 1d | $0.00 | ✅ PASS |
| Quality Score | > 0.75 | 28d | N/A | ⚠️ N/A |

**Incident: cost_spike (Token Usage Spike):**

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|:---:|
| Latency P95 | < 3000ms | 28d | 150ms | ✅ PASS |
| Error Rate | < 2% | 28d | 0% | ✅ PASS |
| Cost Budget | < $2.5/day | 1d | $8.50 | ❌ FAIL |
| Quality Score | > 0.75 | 28d | 0.82 | ✅ PASS |

**Combined Incidents (rag_slow + cost_spike):**

| SLI | Target | Window | Current Value | Status |
|---|---:|---|---:|:---:|
| Latency P95 | < 3000ms | 28d | 10098ms | ❌ FAIL |
| Error Rate | < 2% | 28d | 0% | ✅ PASS |
| Cost Budget | < $2.5/day | 1d | $9.20 | ❌ FAIL |
| Quality Score | > 0.75 | 28d | 0.80 | ✅ PASS |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: 
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 increased from ~150ms to 8000ms+, response times exceeded 10+ seconds, dashboard showed red SLO indicators
- [ROOT_CAUSE_PROVED_BY]: Trace ID req-87600be9 shows 12088ms latency, Log line with correlation_id "req-3daee5a0" shows latency_ms: 8000
- [FIX_ACTION]: Disabled rag_slow incident via python scripts/inject_incident.py --scenario rag_slow --disable
- [PREVENTIVE_MEASURE]: Implement caching for RAG retrieval, add circuit breakers for slow external services, set up P95 latency alerts with 3000ms threshold

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
- [TASKS_COMPLETED]: Built and configured the 6-panel frontend observability dashboard (`dashboard.html` and `config/dashboard.json`) with real-time metrics visualization, SLO compliance indicators, and auto-refresh functionality. Upgraded system from mock LLM to real OpenAI API integration (`app/openai_llm.py`) enabling authentic cost tracking, token usage, and model performance data in Langfuse. Collected comprehensive evidence including screenshots, metrics validation, and incident detection documentation.
- [EVIDENCE_LINK]: 
  - Dashboard Implementation: `dashboard.html`, `config/dashboard.json`, `serve_dashboard.py`
  - OpenAI Integration: `app/openai_llm.py`, `app/agent.py` (upgraded from mock_llm)
  - Evidence Collection: `screenshot/Dashboard 6 panel.png`, `screenshot/Dashboard langfuse.png`, `screenshot/Tracing langfuse.png`
  - Real LLM Integration: Replaced `FakeLLM` with `OpenAILLM` for authentic Langfuse model costs and usage data

### Nguyễn Bình Thành - 2A202600138 (Member F)
- [TASKS_COMPLETED]: Compiled the Blueprint report, synthesized the Root Cause Analysis (RCA) in the Incident Response section, and prepared the Demo script to showcase the system.
- [EVIDENCE_LINK]: (Provide Link to commit or PR for Blueprint)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Implemented real OpenAI API integration with cost-effective model selection (gpt-3.5-turbo default, gpt-4 for cost_spike scenarios) and token limit controls (max 150 tokens per response). Added real-time cost tracking and budget alerts.
- [BONUS_AUDIT_LOGS]: Enhanced structured logging with comprehensive audit trail including correlation IDs, user context, session tracking, and PII redaction. All requests tracked with full observability chain.
- [BONUS_CUSTOM_METRIC]: Created comprehensive dashboard with 6 custom panels including Hallucination % (derived from quality scores), real-time SLO compliance indicators, and time-series visualization with 30-second auto-refresh.

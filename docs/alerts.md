# Alert Rules and Runbooks

## 1. High Latency P95 {#1-high-latency-p95}
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 5m`
- Impact: Tail latency breaches SLO (99.5% target)
- First checks:
  1. Open top slow traces in Langfuse (last 1h)
  2. Compare RAG span vs LLM span latency
  3. Check if incident toggle `rag_slow` is enabled: `python scripts/inject_incident.py --status`
- Mitigation:
  - Truncate long queries
  - Fallback retrieval source
  - Lower prompt size

## 1. Extreme Latency P99 {#1-extreme-latency-p99}
- Severity: P1
- Trigger: `latency_p99_ms > 10000 for 2m`
- Impact: Critical — users experiencing >10s response times
- First checks:
  1. Check if `rag_slow` incident is active
  2. Look for timeout errors in logs: `grep "timeout" data/logs.jsonl`
  3. Inspect P99 outlier traces in Langfuse
- Mitigation:
  - Immediately disable `rag_slow` toggle if active
  - Apply request timeout cutoff
  - Escalate to P1 on-call

## 2. High Error Rate {#2-high-error-rate}
- Severity: P1
- Trigger: `error_rate_pct > 2 for 3m`
- Impact: Users receiving failed responses
- First checks:
  1. Group logs by `error_type`: `grep "event.*request_failed" data/logs.jsonl`
  2. Inspect failed traces in Langfuse
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - Rollback latest change
  - Disable failing tool via incident toggle
  - Retry with fallback model

## 2. Critical Error Rate {#2-critical-error-rate}
- Severity: P0
- Trigger: `error_rate_pct > 10 for 1m`
- Impact: Severe — majority of users affected
- First checks:
  1. Check `tool_fail` incident toggle status
  2. Verify LLM API availability
  3. Check recent deployments
- Mitigation:
  - Activate `mock_llm` fallback immediately
  - Page on-call via PagerDuty
  - Rollback if deployment-related

## 3. Cost Budget Spike {#3-cost-budget-spike}
- Severity: P2
- Trigger: `hourly_cost_usd > 1.0 for 15m`
- Impact: Burn rate exceeds hourly budget
- First checks:
  1. Split traces by feature and model in Langfuse
  2. Compare `tokens_in`/`tokens_out` vs baseline
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - Shorten prompts
  - Route easy requests to cheaper model
  - Apply prompt caching

## 3. Daily Cost Budget Exceeded {#3-daily-cost-budget-exceeded}
- Severity: P1
- Trigger: `daily_cost_usd > 2.5 for 1h`
- Impact: Daily budget of $2.50 breached
- First checks:
  1. Identify top cost-generating features/sessions
  2. Check for token-heavy prompts: review `tokens_in` in traces
  3. Verify no runaway loop/retry scenario
- Mitigation:
  - Cap max tokens per request
  - Throttle high-cost features
  - Alert finops team

## 4. Low Quality Score {#4-low-quality-score}
- Severity: P2
- Trigger: `quality_score_avg < 0.75 for 10m`
- Impact: Response quality below SLO (95% target at >= 0.75)
- First checks:
  1. Sample recent low-score responses from logs
  2. Check if RAG retrieval returned empty docs (`doc_count == 0`)
  3. Verify LLM is not falling back to mock responses
- Mitigation:
  - Improve retrieval query
  - Check RAG index freshness
  - Switch to higher-capability model

## 4. Critical Quality Degradation {#4-critical-quality-degradation}
- Severity: P1
- Trigger: `quality_score_avg < 0.5 for 5m`
- Impact: Responses are critically poor
- First checks:
  1. Check if mock LLM is active (WARNING in logs: "Using fallback mock responses")
  2. Verify OpenAI API key validity
  3. Inspect trace metadata for "mock response" in answers
- Mitigation:
  - Re-configure valid LLM API key
  - Disable mock fallback
  - Escalate to P1

## 5. No Traffic {#5-no-traffic}
- Severity: P2
- Trigger: `requests_per_minute == 0 for 5m`
- Impact: Potential service outage or routing failure
- First checks:
  1. Check server health: `GET /health`
  2. Verify uvicorn process is running
  3. Check load balancer / reverse proxy config
- Mitigation:
  - Restart server if down
  - Check upstream routing
  - Verify DNS / port binding

## 5. Traffic Spike {#5-traffic-spike}
- Severity: P2
- Trigger: `requests_per_minute > 100 for 5m`
- Impact: Unexpected load — potential cost and latency impact
- First checks:
  1. Identify source IPs / sessions generating high traffic
  2. Check for load test scripts still running
  3. Review recent feature releases
- Mitigation:
  - Apply rate limiting
  - Scale horizontally if needed
  - Block abusive clients

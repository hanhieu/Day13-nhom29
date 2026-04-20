# 🔍 Incident Detection Guide

## Where to Find Evidence of Each Incident Type

### 1. 🐌 **RAG_SLOW** - Retrieval Latency Spike

#### **Evidence Locations:**

**A. Application Logs (`data/logs.jsonl`)**
```bash
# Check recent logs for high latency
tail -5 data/logs.jsonl | grep latency_ms
```
**Look for**: `"latency_ms": 6000+` (instead of normal ~150ms)

**Example Evidence:**
```json
{"latency_ms": 6534, "correlation_id": "req-cd628ee4"}
{"latency_ms": 6361, "correlation_id": "req-9b1944e7"}
```

**B. Dashboard Metrics**
```bash
curl http://127.0.0.1:8001/metrics | jq '.latency_p95, .latency_p99'
```
**Look for**: P95 > 3000ms, P99 > 6000ms

**C. Langfuse Traces**
- Go to: https://cloud.langfuse.com
- Find traces with correlation IDs from logs
- Look for: Slow spans in the trace timeline
- **Expected**: RAG retrieval span taking 2.5+ seconds

**D. Real-time Testing**
```bash
# Enable incident
python scripts/inject_incident.py --scenario rag_slow

# Make request and time it
time curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"test","feature":"test","message":"test"}'
```
**Expected**: Response takes 2.5+ seconds instead of normal ~1 second

---

### 2. ❌ **TOOL_FAIL** - Vector Store or Tool Error

#### **Evidence Locations:**

**A. Application Logs (`data/logs.jsonl`)**
```bash
# Check for error events
grep "request_failed" data/logs.jsonl | tail -5
```
**Look for**: `"event": "request_failed"`, `"error_type": "RuntimeError"`

**B. HTTP Response Codes**
```bash
# Enable incident and test
python scripts/inject_incident.py --scenario tool_fail
python scripts/load_test.py
```
**Look for**: `[500]` status codes instead of `[200]`

**C. Error Metrics**
```bash
curl http://127.0.0.1:8001/metrics | jq '.error_rate_pct, .error_breakdown'
```
**Look for**: `"error_rate_pct": 100.0`, `"error_breakdown": {"RuntimeError": 10}`

**D. Langfuse Traces**
- Find traces with error status
- Look for: Failed spans with error details
- **Expected**: Error spans showing "RuntimeError" or "Simulated tool failure"

---

### 3. 💰 **COST_SPIKE** - Token Usage Spike

#### **Evidence Locations:**

**A. Cost Metrics**
```bash
# Before cost spike
curl http://127.0.0.1:8001/metrics | jq '.avg_cost_usd, .total_cost_usd'

# Enable cost spike
python scripts/inject_incident.py --scenario cost_spike
python scripts/load_test.py

# After cost spike
curl http://127.0.0.1:8001/metrics | jq '.avg_cost_usd, .total_cost_usd'
```
**Look for**: 4x higher costs per request

**B. Token Usage**
```bash
curl http://127.0.0.1:8001/metrics | jq '.tokens_out_total'
```
**Look for**: Much higher output token counts

**C. Application Logs**
```bash
grep "cost_usd" data/logs.jsonl | tail -5
```
**Look for**: Higher `"cost_usd"` values and `"tokens_out"` counts

**D. Langfuse Traces**
- Check model usage in traces
- Look for: Higher token consumption
- **Expected**: gpt-4 model usage instead of gpt-3.5-turbo (more expensive)

---

## 🧪 Step-by-Step Testing Process

### Test All Incidents:
```bash
# 1. Test RAG_SLOW
python scripts/inject_incident.py --scenario rag_slow
python scripts/load_test.py
echo "Check latency in logs and metrics"

# 2. Test TOOL_FAIL  
python scripts/inject_incident.py --scenario tool_fail
python scripts/load_test.py
echo "Check for 500 errors and RuntimeError"

# 3. Test COST_SPIKE
python scripts/inject_incident.py --scenario cost_spike
python scripts/load_test.py
echo "Check for higher costs and token usage"

# 4. Clean up
python scripts/inject_incident.py --scenario rag_slow --disable
python scripts/inject_incident.py --scenario tool_fail --disable
python scripts/inject_incident.py --scenario cost_spike --disable
```

### Automated Detection:
```bash
# Run comprehensive incident testing
python scripts/test_alerts.py
```

---

## 📊 Current Evidence (Live Example)

### RAG_SLOW Currently Active:
```json
{
  "latency_p50": 3159.0,
  "latency_p95": 6863.0,
  "latency_p99": 7657.0
}
```

### Recent Log Evidence:
```json
{"latency_ms": 6534, "correlation_id": "req-cd628ee4"}
{"latency_ms": 6361, "correlation_id": "req-9b1944e7"}
```

---

## 🎯 What Students Should Find

### For RAG_SLOW:
- **Logs**: latency_ms > 6000ms
- **Metrics**: P95 > 6000ms
- **Langfuse**: Slow RAG retrieval spans (2.5+ seconds)
- **Dashboard**: Latency charts showing spikes

### For TOOL_FAIL:
- **Logs**: "error_type": "RuntimeError"
- **Metrics**: error_rate_pct = 100%
- **HTTP**: 500 status codes
- **Langfuse**: Error spans with failure details

### For COST_SPIKE:
- **Logs**: Higher cost_usd values
- **Metrics**: 4x higher avg_cost_usd
- **Tokens**: Much higher tokens_out counts
- **Langfuse**: gpt-4 model usage (more expensive)

---

## 🔗 Quick Access Commands

```bash
# Check current incidents status
curl http://127.0.0.1:8001/health | jq '.incidents'

# View recent logs
tail -10 data/logs.jsonl

# Check metrics
curl http://127.0.0.1:8001/metrics

# View dashboard
open http://localhost:8080/dashboard.html

# Access Langfuse
open https://cloud.langfuse.com
```

The evidence is there - you just need to know where to look! 🔍
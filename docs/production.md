# Production & Auditing

When moving an OpenHosta application from development to production, **observability** and **traceability** become critical. OpenHosta provides a built-in auditing system to help you monitor LLM interactions, track costs, and ensure compliance.

---

## 🛡️ The Audit Mode

The `audit_log` function is the core of OpenHosta's observability. It records structured events during the execution of your pipelines.

### Why Audit? (Industry Standards)
In modern software engineering, **Audit Logging** is more than just debugging; it is a standard for:
- **Compliance**: Meeting regulatory requirements (GDPR, SOC2, HIPAA) by tracking data lineage.
- **Security**: Detecting prompt injections or unexpected model behaviors.
- **Accountability**: Providing a "black box" recording of AI decisions.
- **Optimization**: Analyzing real-world usage to improve prompt performance and reduce costs.

### Enabling Audit Mode
By default, auditing is disabled to save performance. You can enable it via the global configuration:

```python
from OpenHosta import config

config.AUDIT_MODE = True
```

Alternatively, you can enable it via an environment variable:
```bash
export OPENHOSTA_AUDIT_MODE=True
```

Once enabled, OpenHosta will output JSON-structured logs to `stdout` prefixed with `[OPENHOSTA_AUDIT]`.

---

## ⚙️ Advanced Production Setup

### 1. Centralizing Logs
In production, you should redirect `stdout` to a log aggregator (Datadog, ELK, CloudWatch). You can easily filter OpenHosta audit logs using the prefix:

```bash
# Example: Grepping audit logs in a Linux environment
python my_app.py | grep "[OPENHOSTA_AUDIT]" > audit.log
```

### 2. Programmatic Callbacks
For deeper integration, you can register custom callbacks. This is useful for sending alerts to **Sentry**, saving events to a **SQL database**, or pushing metrics to **Prometheus**.

```python
from OpenHosta.core.audit import register_audit_callback, AuditEvent

def my_production_handler(event: AuditEvent):
    # Example: Send to an external monitoring tool
    if event.event_type == "llm_call_error":
        print(f"CRITICAL: Model failed with details: {event.details}")
    
    # Save to your own DB for analytics
    save_to_db(event.timestamp, event.event_type, event.details)

register_audit_callback(my_production_handler)
```

### 3. Cost Control
Always wrap production calls in a cost tracker to avoid budget overruns.

```python
from OpenHosta import emulate, track_costs

with track_costs() as tracker:
    result = emulate("Analyze this report", data=my_report)

# Log this to your billing system
print(f"Cost for this request: {tracker.total_tokens} tokens")
```

---

## 🚀 Production Checklist

- [ ] **API Keys**: Use environment variables (`OPENHOSTA_DEFAULT_MODEL_API_KEY`).
- [ ] **Silence Warnings**: Set `OPENHOSTA_SILENCE_ENV_WARNING=True`. 
    > [!IMPORTANT]
    > In containerized environments (Docker, Kubernetes) or application servers where you pass configuration via environment variables instead of a `.env` file, set this to `True` to prevent OpenHosta from printing "missing .env" warnings, ensuring clean and professional startup logs.
- [ ] **Timeouts**: Ensure your model server (Ollama, vLLM, OpenAI) has appropriate timeout settings.
- [ ] **Retries**: OpenHosta handles basic retries, but consider implementing a circuit breaker for high-traffic apps.
- [ ] **Audit Enabled**: Enable `AUDIT_MODE` if you are in a regulated industry.
- [ ] **Fallback Models**: Configure a secondary model in case your primary provider is down.

---

> [!TIP]
> Audit logs are structured as JSON. They include `timestamp`, `event_type`, and `details` (which contains the raw prompt, the model response, and the parsed result).

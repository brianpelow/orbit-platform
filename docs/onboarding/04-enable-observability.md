# Prerequisite 4: Enable OpenTelemetry Observability

**Time required**: 3-5 days
**Validation**: Metrics and traces visible in observability platform

## Required signals

Your service must emit all three OTel signal types:
- **Traces** — distributed request tracing
- **Metrics** — RED metrics (Rate, Errors, Duration)
- **Logs** — structured JSON logs with trace correlation

## Python installation

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "retail-banking-api",
    "service.id": "SVC-12345",
    "service.owner": "team@example.com",
})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint="https://otel-collector.example.com/v1/traces")
```

## Node.js installation

```javascript
const { NodeSDK } = require("@opentelemetry/sdk-node");
const sdk = new NodeSDK({
  serviceName: "retail-banking-api",
  resource: { "service.id": "SVC-12345" }
});
sdk.start();
```

## Validation

```bash
kubectl apply -f staging/deployment.yaml
curl https://otel-collector.example.com/metrics | grep retail-banking-api
```

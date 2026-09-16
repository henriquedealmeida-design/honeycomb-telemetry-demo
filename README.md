# Honeycomb Telemetry Demo (FastAPI + OpenTelemetry)

Minimal FastAPI service instrumented with OpenTelemetry that sends traces to
[Honeycomb](https://www.honeycomb.io/) via the OTLP/HTTP exporter — the
"Send data to test" step of the Honeycomb onboarding.

## Endpoints

| Method | Path       | Description                                        |
| ------ | ---------- | -------------------------------------------------- |
| GET    | `/`        | Hello world                                        |
| GET    | `/health`  | Health check                                       |
| POST   | `/orders`  | Creates an order (nested spans: `process_order` → `charge_payment`) |
| GET    | `/flaky`   | Fails randomly (~50%) so you can see error traces  |

## Setup

```bash
# 1. Create a virtualenv and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure your API key
cp .env.example .env
# edit .env and set HONEYCOMB_API_KEY
# (get it from https://ui.honeycomb.io -> your environment -> Manage API keys)

# 3. Load the env vars and run
export $(grep -v '^#' .env | xargs)   # Windows: use python-dotenv or set the var manually
uvicorn app.main:app --reload
```

## Generate traffic

```bash
curl -X POST http://localhost:8000/orders
curl http://localhost:8000/flaky
```

## See the data

Open your Honeycomb environment → the `fastapi-honeycomb-demo` service should
appear in the dataset `fastapi-demo`, with traces, spans and errors.

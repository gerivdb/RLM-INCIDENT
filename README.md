# RLM-INCIDENT

Incident management and anomaly detection service for the RLM ecosystem.

- Port: `8798`
- Role: incident management, anomaly detection PES
- Stack: Flask + SQLite (future state persistence)

## Endpoints

| Method | Path                 | Purpose                       |
|--------|----------------------|-------------------------------|
| GET    | /health              | Liveness check                |
| GET    | /metrics             | Incident counts               |
| POST   | /vote                | Record a vote                 |
| POST   | /incidents           | Create incident               |
| POST   | /incidents/<id>/close| Close incident                |
| GET    | /incidents           | List incidents                |
| GET    | /status              | Service status                |

## Run

```powershell
python src/app.py
```

## Test

```powershell
pytest tests/test_app.py -q
```

## Archi notes

- MVP: in-memory incidents dict
- Next: integrate KIX for runner anomaly detection

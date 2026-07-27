from flask import Flask, jsonify, request
import os
from datetime import datetime, timezone

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 8798))
INCIDENTS: dict = {}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "rlm-incident", "port": PORT}), 200


@app.get("/metrics")
def metrics():
    return jsonify({
        "service": "rlm-incident",
        "port": PORT,
        "incidents": len(INCIDENTS),
        "open": sum(1 for i in INCIDENTS.values() if i["status"] == "open"),
        "timestamp": _utcnow(),
    }), 200


@app.post("/vote")
def vote():
    data = request.get_json(silent=True) or {}
    choice = data.get("choice")
    if not choice:
        return jsonify({"error": "missing choice"}), 400
    return jsonify({"choice": choice, "count": 1}), 200


@app.post("/incidents")
def create_incident():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "missing title"}), 400

    incident_id = f"incident-{len(INCIDENTS) + 1}"
    INCIDENTS[incident_id] = {
        "title": title,
        "status": "open",
        "created_at": _utcnow(),
    }
    return jsonify({"id": incident_id, "status": "open"}), 201


@app.post("/incidents/<string:incident_id>/close")
def close_incident(incident_id: str):
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return jsonify({"error": "incident not found"}), 404

    incident["status"] = "closed"
    incident["closed_at"] = _utcnow()
    return jsonify({"id": incident_id, "status": "closed"}), 200


@app.get("/incidents")
def list_incidents():
    return jsonify({"incidents": INCIDENTS}), 200


@app.get("/status")
def status():
    return jsonify({"service": "rlm-incident", "port": PORT, "mode": "standby"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

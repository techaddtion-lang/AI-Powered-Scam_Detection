import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.schemas import ClassificationLabel

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_analyze_chase_scam_message():
    scam_payload = {
        "text": "URGENT: Chase Bank alert. Your debit card has been temporarily locked due to suspicious activity. Verify immediately at http://chase-security-verify.net/login to prevent permanent block.",
        "channel": "sms"
    }
    response = client.post("/api/v1/analyze-message", json=scam_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == ClassificationLabel.HIGH_RISK_SCAM.value
    assert data["risk_score"] >= 65.0
    assert len(data["indicators"]) > 0
    assert len(data["urls_analyzed"]) > 0
    assert data["urls_analyzed"][0]["is_suspicious"] is True


def test_analyze_safe_message():
    safe_payload = {
        "text": "Hi Sarah, are we still meeting for lunch at 12:30 at the Italian restaurant on 5th street? Let me know if you are running late!",
        "channel": "sms"
    }
    response = client.post("/api/v1/analyze-message", json=safe_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == ClassificationLabel.SAFE.value
    assert data["risk_score"] < 35.0


def test_analyze_call_transcript_vishing():
    vishing_payload = {
        "transcript": "Hello this is Officer James from the IRS Department. There is an arrest warrant issued. Read me the 6-digit OTP code sent to your phone right now or police will arrive.",
        "caller_number": "+18005550199"
    }
    response = client.post("/api/v1/analyze-call", json=vishing_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == ClassificationLabel.HIGH_RISK_SCAM.value
    assert "Live OTP Interception" in data["vishing_tactics_detected"]


def test_analyze_url():
    url_payload = {"url": "http://192.168.1.120/paypal/login.php"}
    response = client.post("/api/v1/analyze-url", json=url_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["has_ip_hostname"] is True
    assert data["is_suspicious"] is True
    assert data["risk_score"] >= 65.0


def test_get_samples():
    response = client.get("/api/v1/samples")
    assert response.status_code == 200
    samples = response.json()
    assert isinstance(samples, list)
    assert len(samples) > 0


def test_mysql_analytics_overview():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "scams_blocked" in data
    assert "threat_intel" in data
    assert data["total_scans"] > 0


def test_mysql_scan_history():
    response = client.get("/api/v1/scans/history?limit=10")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0


def test_mysql_threat_blacklist():
    response = client.get("/api/v1/intelligence/blacklist")
    assert response.status_code == 200
    intel = response.json()
    assert "phones" in intel
    assert "domains" in intel
    assert len(intel["phones"]) > 0


def test_mysql_report_threat_and_feedback():
    report_payload = {
        "threat_type": "phone",
        "identifier": "+19998887777",
        "entity_name": "Test Impostor Robocall",
        "category": "Test Scam",
        "notes": "Automated test incident"
    }
    rep_res = client.post("/api/v1/intelligence/report-threat", json=report_payload)
    assert rep_res.status_code == 200

    feedback_payload = {
        "scan_id": "test-scan-uuid",
        "feedback_type": "CONFIRMED_SCAM",
        "comments": "Confirmed true positive"
    }
    fb_res = client.post("/api/v1/feedback", json=feedback_payload)
    assert fb_res.status_code == 200


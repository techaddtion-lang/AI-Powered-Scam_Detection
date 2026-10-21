import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from app.api.schemas import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
    CallAnalysisRequest,
    CallAnalysisResponse,
    UrlAnalysisRequest,
    UrlSafetyResult,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ClassificationLabel
)
from app.services.scam_detector import detector_service
from app.services.url_analyzer import analyze_url
from app.ml.model import ml_classifier
from app.db.connection import get_db
from app.db.models import (
    ScanLog,
    PhoneReputation,
    DomainBlacklist,
    UserFeedback,
    SpamTrainingCorpus
)
from app.api.webhooks import webhook_router

router = APIRouter()
router.include_router(webhook_router)

SAMPLES_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_scams.json"


class ReportThreatRequest(BaseModel):
    threat_type: str  # 'phone' or 'domain'
    identifier: str   # phone number or domain name
    entity_name: str
    category: str
    notes: Optional[str] = None


class FeedbackRequest(BaseModel):
    scan_id: str
    feedback_type: str  # 'CONFIRMED_SCAM', 'FALSE_POSITIVE'
    comments: Optional[str] = None


# -------------------------------------------------------------
# CORE SCANNING ENDPOINTS (Persisting to MySQL)
# -------------------------------------------------------------

@router.post(
    "/analyze-message",
    response_model=MessageAnalysisResponse,
    summary="Analyze SMS, Email, or Text Message",
    description="Evaluates textual content with ML, heuristic rules, URL scanning, and MySQL threat intelligence."
)
async def analyze_message_endpoint(payload: MessageAnalysisRequest):
    try:
        return detector_service.analyze_message(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing message: {str(e)}"
        )


@router.post(
    "/analyze-call",
    response_model=CallAnalysisResponse,
    summary="Analyze Phone Call Transcript",
    description="Evaluates phone call audio transcripts for voice-phishing (vishing), impersonation, and caller reputation."
)
async def analyze_call_endpoint(payload: CallAnalysisRequest):
    try:
        return detector_service.analyze_call(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing call transcript: {str(e)}"
        )


@router.post(
    "/analyze-url",
    response_model=UrlSafetyResult,
    summary="Analyze a URL or Web Domain",
    description="Performs heuristic security inspection on a single URL for phishing indicators, IP hosts, brand spoofing, and risky TLDs."
)
async def analyze_url_endpoint(payload: UrlAnalysisRequest):
    try:
        result = analyze_url(payload.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing URL: {str(e)}"
        )


@router.post(
    "/batch-analyze",
    response_model=BatchAnalysisResponse,
    summary="Batch Analyze Multiple Messages",
    description="Processes a batch list of messages, producing individual reports and aggregated threat statistics."
)
async def batch_analyze_endpoint(payload: BatchAnalysisRequest):
    try:
        results: List[MessageAnalysisResponse] = []
        scam_count = 0
        suspicious_count = 0
        safe_count = 0
        total_risk_sum = 0.0

        for msg in payload.messages:
            res = detector_service.analyze_message(msg)
            results.append(res)
            total_risk_sum += res.risk_score

            if res.classification == ClassificationLabel.HIGH_RISK_SCAM:
                scam_count += 1
            elif res.classification == ClassificationLabel.SUSPICIOUS:
                suspicious_count += 1
            else:
                safe_count += 1

        total = len(payload.messages)
        avg_score = round(total_risk_sum / total, 1) if total > 0 else 0.0

        return BatchAnalysisResponse(
            total_processed=total,
            scam_count=scam_count,
            suspicious_count=suspicious_count,
            safe_count=safe_count,
            average_risk_score=avg_score,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch analysis: {str(e)}"
        )


# -------------------------------------------------------------
# MYSQL THREAT INTELLIGENCE & REAL TELEMETRY ENDPOINTS
# -------------------------------------------------------------

@router.get(
    "/analytics/overview",
    summary="Real-time MySQL Threat Intelligence Analytics",
    description="Queries MySQL for real-time telemetry, volume stats, and threat distribution."
)
async def get_analytics_overview(db: Session = Depends(get_db)):
    try:
        total_scans = db.query(ScanLog).count()
        scams_count = db.query(ScanLog).filter(ScanLog.classification == "High Risk Scam").count()
        suspicious_count = db.query(ScanLog).filter(ScanLog.classification == "Suspicious").count()
        safe_count = db.query(ScanLog).filter(ScanLog.classification == "Safe").count()
        
        avg_score_res = db.query(func.avg(ScanLog.risk_score)).scalar() or 0.0
        
        total_blacklisted_phones = db.query(PhoneReputation).filter(
            PhoneReputation.reputation_status == "BLACKLISTED_SCAM"
        ).count()
        
        total_phishing_domains = db.query(DomainBlacklist).filter(
            DomainBlacklist.status == "ACTIVE_THREAT"
        ).count()

        # Recent 6 scans directly from MySQL
        recent_scans = db.query(ScanLog).order_by(desc(ScanLog.created_at)).limit(6).all()
        formatted_recent = [
            {
                "id": s.id,
                "scan_type": s.scan_type,
                "channel": s.channel,
                "sender": s.sender_or_caller or "Anonymous",
                "preview": s.raw_content[:80] + ("..." if len(s.raw_content) > 80 else ""),
                "classification": s.classification,
                "risk_score": s.risk_score,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in recent_scans
        ]

        return {
            "database": "MySQL (scamshield_db)",
            "total_scans": total_scans,
            "scams_blocked": scams_count,
            "suspicious_flagged": suspicious_count,
            "safe_verified": safe_count,
            "average_threat_score": round(float(avg_score_res), 1),
            "threat_intel": {
                "blacklisted_callers_count": total_blacklisted_phones,
                "phishing_domains_count": total_phishing_domains
            },
            "recent_audit_log": formatted_recent
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying MySQL analytics: {str(e)}"
        )


@router.get(
    "/scans/history",
    summary="Get Historical Scan Logs from MySQL",
    description="Fetches paginated audit logs directly from the MySQL scan_logs table."
)
async def get_scan_history(
    limit: int = Query(25, ge=1, le=100),
    classification: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(ScanLog)
        if classification:
            query = query.filter(ScanLog.classification == classification)
        
        records = query.order_by(desc(ScanLog.created_at)).limit(limit).all()
        
        return [
            {
                "id": r.id,
                "scan_type": r.scan_type,
                "channel": r.channel,
                "sender_or_caller": r.sender_or_caller,
                "raw_content": r.raw_content,
                "classification": r.classification,
                "risk_score": r.risk_score,
                "confidence": r.confidence,
                "summary": r.summary,
                "indicators": r.indicators or [],
                "urls_analyzed": r.urls_analyzed or [],
                "recommendations": r.recommendations or [],
                "vishing_tactics": r.vishing_tactics or [],
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching scan history from MySQL: {str(e)}"
        )


@router.get(
    "/intelligence/blacklist",
    summary="Fetch MySQL Blacklist Database",
    description="Returns all registered scam phone numbers and malicious phishing domains."
)
async def get_threat_intelligence(db: Session = Depends(get_db)):
    try:
        phones = db.query(PhoneReputation).order_by(desc(PhoneReputation.reports_count)).limit(50).all()
        domains = db.query(DomainBlacklist).order_by(desc(DomainBlacklist.reports_count)).limit(50).all()

        return {
            "phones": [
                {
                    "id": p.id,
                    "phone_number": p.phone_number,
                    "entity_name": p.entity_name,
                    "status": p.reputation_status,
                    "category": p.threat_category,
                    "risk_score": p.risk_score,
                    "reports_count": p.reports_count,
                    "notes": p.notes,
                    "last_reported": p.last_reported_at.isoformat() if p.last_reported_at else None
                }
                for p in phones
            ],
            "domains": [
                {
                    "id": d.id,
                    "domain_name": d.domain_name,
                    "threat_type": d.threat_type,
                    "targeted_brand": d.targeted_brand,
                    "risk_score": d.risk_score,
                    "reports_count": d.reports_count,
                    "status": d.status
                }
                for d in domains
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying threat intelligence: {str(e)}"
        )


@router.post(
    "/intelligence/report-threat",
    summary="Report New Scam Number or Domain to MySQL",
    description="Adds a newly discovered scam phone number or phishing domain into the MySQL threat registry."
)
async def report_threat_endpoint(payload: ReportThreatRequest, db: Session = Depends(get_db)):
    try:
        clean_id = payload.identifier.strip()
        if payload.threat_type == "phone":
            existing = db.query(PhoneReputation).filter(PhoneReputation.phone_number == clean_id).first()
            if existing:
                existing.reports_count += 1
                db.commit()
                return {"message": "Threat report updated. Report count incremented.", "record_id": existing.id}
            else:
                new_record = PhoneReputation(
                    phone_number=clean_id,
                    entity_name=payload.entity_name,
                    reputation_status="BLACKLISTED_SCAM",
                    threat_category=payload.category,
                    risk_score=95.0,
                    reports_count=1,
                    notes=payload.notes or "Reported via ScamShield Enterprise Dashboard"
                )
                db.add(new_record)
                db.commit()
                return {"message": "New scam phone number successfully registered in MySQL blacklist.", "record_id": new_record.id}
        else:
            existing = db.query(DomainBlacklist).filter(DomainBlacklist.domain_name == clean_id).first()
            if existing:
                existing.reports_count += 1
                db.commit()
                return {"message": "Phishing domain report updated.", "record_id": existing.id}
            else:
                new_domain = DomainBlacklist(
                    domain_name=clean_id,
                    threat_type="PHISHING",
                    targeted_brand=payload.entity_name,
                    risk_score=95.0,
                    reports_count=1,
                    status="ACTIVE_THREAT",
                    source="Community_Report"
                )
                db.add(new_domain)
                db.commit()
                return {"message": "Phishing domain registered in MySQL blacklist.", "record_id": new_domain.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering threat in MySQL: {str(e)}"
        )


@router.post(
    "/feedback",
    summary="Submit Analyst Feedback to MySQL",
    description="Saves confirmation or false positive telemetry for continuous improvement."
)
async def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        feedback = UserFeedback(
            scan_id=payload.scan_id,
            feedback_type=payload.feedback_type,
            comments=payload.comments
        )
        db.add(feedback)
        db.commit()
        return {"status": "success", "message": "Feedback recorded in MySQL audit database."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving feedback: {str(e)}"
        )


@router.get(
    "/samples",
    summary="Get Curated Sample Scam & Safe Payloads",
    description="Returns pre-built realistic SMS and call transcript test cases for instant dashboard testing."
)
async def get_samples_endpoint():
    try:
        if SAMPLES_FILE.exists():
            with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load samples: {str(e)}"
        )


@router.post(
    "/model/retrain",
    summary="Retrain NLP Machine Learning Classifier from MySQL",
    description="Retrains the Scikit-learn model directly from the MySQL spam_training_corpus table."
)
async def retrain_model_endpoint(db: Session = Depends(get_db)):
    try:
        # Load directly from MySQL training corpus
        corpus_records = db.query(SpamTrainingCorpus).all()
        custom_data = [
            {"text": r.text_content, "label": r.label}
            for r in corpus_records
        ]
        result = ml_classifier.train(custom_data=custom_data if custom_data else None)
        return {
            "message": "Model retrained successfully from MySQL dataset.",
            "samples_trained": len(custom_data),
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="System Health & MySQL Engine Status",
    description="Returns operational status of the API, ML model, and MySQL database connection."
)
async def health_endpoint(db: Session = Depends(get_db)):
    mysql_ok = False
    try:
        db.execute(func.now())
        mysql_ok = True
    except Exception:
        mysql_ok = False

    return {
        "status": "healthy" if mysql_ok else "degraded",
        "database": "MySQL (scamshield_db)",
        "mysql_connected": mysql_ok,
        "model_loaded": ml_classifier.pipeline is not None,
        "classes": ml_classifier.classes_,
        "engine_version": "2.0.0-enterprise"
    }

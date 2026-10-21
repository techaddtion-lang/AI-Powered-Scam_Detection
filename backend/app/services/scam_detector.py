import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings
from app.api.schemas import (
    ClassificationLabel,
    SeverityLevel,
    ThreatCategory,
    DetectedIndicator,
    MessageAnalysisRequest,
    MessageAnalysisResponse,
    CallAnalysisRequest,
    CallAnalysisResponse,
    UrlSafetyResult
)
from app.ml.model import ml_classifier
from app.services.risk_engine import analyze_text_rules
from app.services.url_analyzer import evaluate_message_urls
from app.services.call_analyzer import analyze_vishing_transcript, check_caller_number
from app.db.connection import SessionLocal
from app.db.models import ScanLog, PhoneReputation, DomainBlacklist


def check_mysql_phone_reputation(phone_number: Optional[str]) -> Optional[PhoneReputation]:
    """Query MySQL database for phone sender intelligence."""
    if not phone_number:
        return None
    db = SessionLocal()
    try:
        clean = re.sub(r'[\s\-\(\)\.]', '', phone_number).strip()
        # Search by exact or clean match
        record = db.query(PhoneReputation).filter(
            (PhoneReputation.phone_number == phone_number) |
            (PhoneReputation.phone_number.like(f"%{clean[-10:]}%"))
        ).first()
        return record
    except Exception:
        return None
    finally:
        db.close()


def check_mysql_domain_blacklist(domain: str) -> Optional[DomainBlacklist]:
    """Query MySQL database for known phishing domains."""
    if not domain:
        return None
    db = SessionLocal()
    try:
        record = db.query(DomainBlacklist).filter(
            (DomainBlacklist.domain_name == domain) |
            (DomainBlacklist.domain_name.like(f"%{domain}%"))
        ).first()
        return record
    except Exception:
        return None
    finally:
        db.close()


def persist_scan_to_mysql(
    scan_id: str,
    scan_type: str,
    channel: str,
    sender_or_caller: Optional[str],
    raw_content: str,
    classification: str,
    risk_score: float,
    confidence: float,
    summary: str,
    indicators: List[DetectedIndicator],
    urls_analyzed: List[UrlSafetyResult],
    recommendations: List[str],
    vishing_tactics: Optional[List[str]] = None,
    ml_confidence_scores: Optional[Dict[str, float]] = None,
    rule_score: float = 0.0
):
    """Write analysis audit trail directly to MySQL scan_logs table."""
    db = SessionLocal()
    try:
        log_entry = ScanLog(
            id=scan_id,
            scan_type=scan_type,
            channel=channel,
            sender_or_caller=sender_or_caller,
            raw_content=raw_content,
            classification=classification,
            risk_score=risk_score,
            confidence=confidence,
            summary=summary,
            indicators=[ind.model_dump() for ind in indicators] if indicators else [],
            urls_analyzed=[u.model_dump() for u in urls_analyzed] if urls_analyzed else [],
            recommendations=recommendations,
            vishing_tactics=vishing_tactics or [],
            ml_confidence_scores=ml_confidence_scores or {},
            rule_score=rule_score,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def calculate_hybrid_risk_score(
    ml_probabilities: Dict[str, float],
    rule_score: float,
    max_url_risk: float,
    indicators_count: int,
    has_critical_indicators: bool
) -> float:
    """
    Synthesize Machine Learning classification, Heuristic Rule Score,
    and URL Safety metrics into a calibrated risk score (0 to 100).
    """
    scam_prob = ml_probabilities.get("High Risk Scam", 0.0)
    suspicious_prob = ml_probabilities.get("Suspicious", 0.0)
    ml_score = (scam_prob * 100.0) + (suspicious_prob * 45.0)

    # Weighted baseline
    if max_url_risk > 0:
        base_score = (0.40 * ml_score) + (0.35 * rule_score) + (0.25 * max_url_risk)
    else:
        base_score = (0.55 * ml_score) + (0.45 * rule_score)

    # Boost logic for high-severity threats
    if has_critical_indicators:
        base_score = max(base_score, 75.0)

    if max_url_risk >= 70.0:
        base_score = max(base_score, 80.0)

    # If both ML and Rules agree strongly on High Risk Scam
    if scam_prob > 0.70 and rule_score > 40:
        base_score = max(base_score, 85.0)

    return round(min(max(base_score, 0.0), 100.0), 1)


def determine_classification(risk_score: float) -> ClassificationLabel:
    """Classify into Safe, Suspicious, or High Risk Scam using configured thresholds."""
    if risk_score >= settings.SUSPICIOUS_THRESHOLD:
        return ClassificationLabel.HIGH_RISK_SCAM
    elif risk_score >= settings.SAFE_THRESHOLD:
        return ClassificationLabel.SUSPICIOUS
    else:
        return ClassificationLabel.SAFE


def generate_summary(
    classification: ClassificationLabel,
    risk_score: float,
    indicators: List[DetectedIndicator],
    urls: List[UrlSafetyResult]
) -> str:
    """Generate concise human-readable verdict and overview."""
    if classification == ClassificationLabel.HIGH_RISK_SCAM:
        reasons = [ind.title for ind in indicators[:2]]
        if urls and any(u.is_suspicious for u in urls):
            reasons.append("suspicious link detected")
        reasons_str = " and ".join(reasons) if reasons else "multiple predatory signals"
        return f"CRITICAL WARNING: This item exhibits high-probability scam behaviors ({reasons_str}). Do not engage or respond."

    elif classification == ClassificationLabel.SUSPICIOUS:
        return f"CAUTION: Potential risk detected (Score: {risk_score}/100). Warning signs such as unsolicited requests or pressure tactics identified."

    else:
        return f"SAFE: No hostile or deceptive patterns identified (Risk: {risk_score}/100). Appears to be standard correspondence."


class ScamDetectionService:
    """Master service combining MySQL Threat Intel, ML pipeline, NLP rules, and URL inspection."""

    def analyze_message(self, request: MessageAnalysisRequest) -> MessageAnalysisResponse:
        """Analyze SMS, email, or general text message."""
        text = request.text.strip()
        analysis_id = str(uuid.uuid4())

        # 1. Run Machine Learning Pipeline
        ml_result = ml_classifier.predict(text)
        ml_probs = ml_result["probabilities"]
        confidence = ml_result["confidence"]

        # 2. Run NLP Rule & Heuristic Engine
        indicators, category_scores, rule_score, recommendations = analyze_text_rules(text)

        # 3. Check MySQL Phone / Sender Threat Intelligence Database
        db_phone = check_mysql_phone_reputation(request.sender_id)
        if db_phone:
            if db_phone.reputation_status == "BLACKLISTED_SCAM":
                indicators.insert(0, DetectedIndicator(
                    category=ThreatCategory.IMPERSONATION,
                    title="Known Blacklisted Threat (MySQL Intel)",
                    description=f"Sender matches active blacklist record: '{db_phone.entity_name}' with {db_phone.reports_count} previous fraud reports.",
                    severity=SeverityLevel.CRITICAL,
                    matched_text=request.sender_id,
                    weight=50.0
                ))
                rule_score = min(rule_score + 45.0, 100.0)
                recommendations.insert(0, f"BLOCK IMMEDIATELY: '{request.sender_id}' is a verified scammer in our threat intelligence registry.")
            elif db_phone.reputation_status == "VERIFIED_OFFICIAL":
                indicators.append(DetectedIndicator(
                    category=ThreatCategory.OTHER,
                    title="Verified Official Sender (MySQL Intel)",
                    description=f"Sender '{db_phone.entity_name}' is a registered authentic gateway.",
                    severity=SeverityLevel.LOW,
                    matched_text=request.sender_id,
                    weight=-20.0
                ))
                rule_score = max(rule_score - 30.0, 0.0)

        # 4. Analyze Extracted URLs & Cross-reference MySQL Domain Blacklist
        urls_analyzed, max_url_risk = evaluate_message_urls(text)
        for url_res in urls_analyzed:
            db_domain = check_mysql_domain_blacklist(url_res.domain)
            if db_domain and db_domain.status == "ACTIVE_THREAT":
                url_res.is_suspicious = True
                url_res.risk_score = 99.0
                url_res.reasons.insert(0, f"CONFIRMED PHISHING THREAT in MySQL Domain Blacklist (Target: {db_domain.targeted_brand})")
                max_url_risk = max(max_url_risk, 99.0)

            if url_res.is_suspicious:
                indicators.append(DetectedIndicator(
                    category=ThreatCategory.SUSPICIOUS_LINK,
                    title="Suspicious / Phishing URL",
                    description=f"Destination '{url_res.domain}' flagged: {'; '.join(url_res.reasons[:2])}",
                    severity=SeverityLevel.CRITICAL if url_res.risk_score >= 60 else SeverityLevel.HIGH,
                    matched_text=url_res.url,
                    weight=30.0
                ))
                category_scores[ThreatCategory.SUSPICIOUS_LINK.value] = (
                    category_scores.get(ThreatCategory.SUSPICIOUS_LINK.value, 0.0) + url_res.risk_score
                )
                recommendations.extend([
                    f"Do not click the link '{url_res.url}'. Scammers use deceptive domains to harvest login credentials.",
                    "Verify the sender through official independent channels."
                ])

        # 5. Synthesize Final Score
        has_critical = any(ind.severity == SeverityLevel.CRITICAL for ind in indicators)
        final_risk_score = calculate_hybrid_risk_score(
            ml_probabilities=ml_probs,
            rule_score=rule_score,
            max_url_risk=max_url_risk,
            indicators_count=len(indicators),
            has_critical_indicators=has_critical
        )

        classification = determine_classification(final_risk_score)
        summary = generate_summary(classification, final_risk_score, indicators, urls_analyzed)
        deduped_recommendations = list(dict.fromkeys(recommendations))

        # 6. Save Audit Record into MySQL Database
        persist_scan_to_mysql(
            scan_id=analysis_id,
            scan_type="message",
            channel=request.channel or "sms",
            sender_or_caller=request.sender_id,
            raw_content=text,
            classification=classification.value,
            risk_score=final_risk_score,
            confidence=confidence,
            summary=summary,
            indicators=indicators,
            urls_analyzed=urls_analyzed,
            recommendations=deduped_recommendations,
            ml_confidence_scores=ml_probs,
            rule_score=rule_score
        )

        return MessageAnalysisResponse(
            id=analysis_id,
            input_text=text,
            classification=classification,
            risk_score=final_risk_score,
            confidence=confidence,
            summary=summary,
            indicators=indicators,
            category_breakdown=category_scores,
            urls_analyzed=urls_analyzed,
            recommendations=deduped_recommendations,
            ml_confidence_scores=ml_probs,
            rule_score=rule_score,
            analysis_timestamp=datetime.utcnow()
        )

    def analyze_call(self, request: CallAnalysisRequest) -> CallAnalysisResponse:
        """Analyze telephone transcript for vishing and cross-reference MySQL Phone Blacklist."""
        transcript = request.transcript.strip()
        analysis_id = str(uuid.uuid4())

        # 1. Run ML Pipeline on transcript
        ml_result = ml_classifier.predict(transcript)
        ml_probs = ml_result["probabilities"]
        confidence = ml_result["confidence"]

        # 2. Run NLP Rule & Heuristic Engine
        indicators, category_scores, rule_score, recommendations = analyze_text_rules(transcript)

        # 3. Check MySQL Phone Intelligence Database
        db_phone = check_mysql_phone_reputation(request.caller_number)
        if db_phone:
            if db_phone.reputation_status == "BLACKLISTED_SCAM":
                indicators.insert(0, DetectedIndicator(
                    category=ThreatCategory.IMPERSONATION,
                    title="Active Blacklist Caller Match (MySQL Intel)",
                    description=f"Caller is registered in Threat Intel: '{db_phone.entity_name}' ({db_phone.reports_count} reports).",
                    severity=SeverityLevel.CRITICAL,
                    matched_text=request.caller_number,
                    weight=50.0
                ))
                rule_score = min(rule_score + 45.0, 100.0)

        # 4. Call-specific Vishing and Caller Number analysis
        vishing_tactics, call_indicators, vishing_score = analyze_vishing_transcript(transcript)
        indicators.extend(call_indicators)

        caller_risk, caller_flags = check_caller_number(request.caller_number)
        if caller_flags:
            indicators.append(DetectedIndicator(
                category=ThreatCategory.IMPERSONATION,
                title="Suspicious Caller ID Spoof",
                description="; ".join(caller_flags),
                severity=SeverityLevel.HIGH,
                matched_text=request.caller_number,
                weight=25.0
            ))

        total_rule_score = min(rule_score + vishing_score + caller_risk, 100.0)

        # 5. Synthesize Score
        has_critical = any(ind.severity == SeverityLevel.CRITICAL for ind in indicators) or bool(vishing_tactics)
        final_risk_score = calculate_hybrid_risk_score(
            ml_probabilities=ml_probs,
            rule_score=total_rule_score,
            max_url_risk=0.0,
            indicators_count=len(indicators),
            has_critical_indicators=has_critical
        )

        classification = determine_classification(final_risk_score)

        if vishing_tactics:
            recommendations.insert(0, "HANG UP IMMEDIATELY. This caller is using verified social engineering/vishing tactics.")
            recommendations.append("Do not stay on the phone and do not follow verbal instructions to transfer funds or buy retail cards.")

        summary = generate_summary(classification, final_risk_score, indicators, [])
        if vishing_tactics:
            summary = f"VISHING CALL DETECTED: Caller engaged in {', '.join(vishing_tactics[:2])}. Immediate risk of financial loss."

        deduped_recommendations = list(dict.fromkeys(recommendations))

        # 6. Save Audit Record into MySQL Database
        persist_scan_to_mysql(
            scan_id=analysis_id,
            scan_type="call",
            channel="voice_call",
            sender_or_caller=request.caller_number,
            raw_content=transcript,
            classification=classification.value,
            risk_score=final_risk_score,
            confidence=confidence,
            summary=summary,
            indicators=indicators,
            urls_analyzed=[],
            recommendations=deduped_recommendations,
            vishing_tactics=vishing_tactics,
            ml_confidence_scores=ml_probs,
            rule_score=total_rule_score
        )

        return CallAnalysisResponse(
            id=analysis_id,
            transcript=transcript,
            caller_number=request.caller_number,
            classification=classification,
            risk_score=final_risk_score,
            confidence=confidence,
            summary=summary,
            vishing_tactics_detected=vishing_tactics,
            indicators=indicators,
            category_breakdown=category_scores,
            recommendations=deduped_recommendations,
            ml_confidence_scores=ml_probs,
            rule_score=total_rule_score,
            analysis_timestamp=datetime.utcnow()
        )


detector_service = ScamDetectionService()


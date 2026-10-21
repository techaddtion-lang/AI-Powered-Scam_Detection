import logging
import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from app.db.connection import engine, SessionLocal, Base
from app.db.models import (
    ScanLog,
    PhoneReputation,
    DomainBlacklist,
    SpamTrainingCorpus,
    UserFeedback
)
from app.ml.dataset import get_training_data

logger = logging.getLogger(__name__)

INITIAL_PHONE_REPUTATIONS = [
    {
        "phone_number": "+1 (800) 242-7338",
        "entity_name": "Chase Bank Spoofed Impostor",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Bank Vishing / Smishing",
        "risk_score": 98.0,
        "reports_count": 342,
        "notes": "Automated voice & SMS spoofing Chase debit card suspension alert."
    },
    {
        "phone_number": "+1 (202) 555-0199",
        "entity_name": "IRS Criminal Investigation Robocall",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Legal Extortion / Arrest Threat",
        "risk_score": 99.5,
        "reports_count": 512,
        "notes": "Coerces victims into wire transfers or prepaid gift cards under threat of arrest."
    },
    {
        "phone_number": "+1 (888) 555-0144",
        "entity_name": "Bank Fraud Dept OTP Stealer",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Live OTP Interception",
        "risk_score": 97.0,
        "reports_count": 188,
        "notes": "Caller poses as fraud investigator asking victim to read out 6-digit SMS 2FA code."
    },
    {
        "phone_number": "+1 (844) 320-9921",
        "entity_name": "Geek Squad / Best Buy Auto-Renewal Scam",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Refund & Remote Access Scareware",
        "risk_score": 94.0,
        "reports_count": 274,
        "notes": "Claims $499 auto-renewal for antivirus; instructs victims to install AnyDesk."
    },
    {
        "phone_number": "+1 (800) 244-8833",
        "entity_name": "Microsoft Windows Defender Trojan Scare",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Tech Support Scareware",
        "risk_score": 96.0,
        "reports_count": 420,
        "notes": "Fake browser popup support number instructing callers to download TeamViewer."
    },
    {
        "phone_number": "+1 (415) 555-0177",
        "entity_name": "Grandchild Jail Bail Emergency Call",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Family Emergency Extortion",
        "risk_score": 95.0,
        "reports_count": 139,
        "notes": "Impersonates distressed family members demanding Walmart MoneyGram bail transfer."
    },
    {
        "phone_number": "+1 (555) 492-0192",
        "entity_name": "Aggressive Pre-Approved Cash Loan Robo",
        "reputation_status": "SUSPICIOUS_ROBOCALL",
        "threat_category": "Unsolicited Predatory Lending",
        "risk_score": 62.0,
        "reports_count": 87,
        "notes": "Unsolicited broadcast offering $50,000 instant loan without credit check."
    },
    {
        "phone_number": "+1 (855) 019-3321",
        "entity_name": "Social Security Disability Termination Threat",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Government Agency Impersonation",
        "risk_score": 99.0,
        "reports_count": 310,
        "notes": "Claims SSN is suspended due to drug trafficking; demands Bitcoin payment."
    },
    {
        "phone_number": "USPS-ALERT",
        "entity_name": "Deceptive USPS Customs Smishing Gateway",
        "reputation_status": "BLACKLISTED_SCAM",
        "threat_category": "Package Customs Clearance Bait",
        "risk_score": 91.0,
        "reports_count": 640,
        "notes": "SMS claiming $2.49 unpaid delivery fee pointing to lookalike phishing domains."
    },
    {
        "phone_number": "72972",
        "entity_name": "Bank of America Official Verification Gateway",
        "reputation_status": "VERIFIED_OFFICIAL",
        "threat_category": "Verified Financial Gateway",
        "risk_score": 2.0,
        "reports_count": 0,
        "notes": "Official carrier shortcode for authentic Bank of America security alerts."
    },
    {
        "phone_number": "48369",
        "entity_name": "Chase Official Security Gateway",
        "reputation_status": "VERIFIED_OFFICIAL",
        "threat_category": "Verified Financial Gateway",
        "risk_score": 1.5,
        "reports_count": 0,
        "notes": "Official Chase shortcode for 2-Factor Authentication alerts."
    },
    {
        "phone_number": "22000",
        "entity_name": "Google Verification Shortcode",
        "reputation_status": "VERIFIED_OFFICIAL",
        "threat_category": "Verified Tech Gateway",
        "risk_score": 0.5,
        "reports_count": 0,
        "notes": "Authentic Google 2-Step Verification SMS gateway."
    }
]

INITIAL_DOMAIN_BLACKLIST = [
    {
        "domain_name": "chase-security-verify.net",
        "threat_type": "PHISHING",
        "targeted_brand": "Chase",
        "risk_score": 98.0,
        "reports_count": 142,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "bofa-kyc-update.xyz",
        "threat_type": "PHISHING",
        "targeted_brand": "Bank of America",
        "risk_score": 96.0,
        "reports_count": 98,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "usps-tracking-redelivery.buzz",
        "threat_type": "BRAND_TYPOSQUAT",
        "targeted_brand": "USPS",
        "risk_score": 94.0,
        "reports_count": 215,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "apple-security-support.top",
        "threat_type": "PHISHING",
        "targeted_brand": "Apple",
        "risk_score": 97.0,
        "reports_count": 164,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "192.168.1.120",
        "threat_type": "IP_HOST_MASK",
        "targeted_brand": "Wells Fargo",
        "risk_score": 99.0,
        "reports_count": 55,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "bit.ly/paypal-dispute-99",
        "threat_type": "MALWARE_DROPPER",
        "targeted_brand": "PayPal",
        "risk_score": 91.0,
        "reports_count": 78,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "binance-security-cancel.xyz",
        "threat_type": "PHISHING",
        "targeted_brand": "Binance",
        "risk_score": 95.0,
        "reports_count": 89,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "fast-cash-loans-today.club",
        "threat_type": "TYPOSQUAT",
        "targeted_brand": "Predatory Loan",
        "risk_score": 65.0,
        "reports_count": 43,
        "status": "ACTIVE_THREAT"
    },
    {
        "domain_name": "amazon.com",
        "threat_type": "VERIFIED_SAFE",
        "targeted_brand": "Amazon",
        "risk_score": 0.0,
        "reports_count": 0,
        "status": "WHITELISTED"
    },
    {
        "domain_name": "chase.com",
        "threat_type": "VERIFIED_SAFE",
        "targeted_brand": "Chase",
        "risk_score": 0.0,
        "reports_count": 0,
        "status": "WHITELISTED"
    }
]


def seed_database():
    """Ensure schema and seed initial threat intelligence into MySQL."""
    logger.info("Initializing MySQL database schema and verifying tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # 1. Seed Phone Reputation
        existing_phones = db.query(PhoneReputation).count()
        if existing_phones == 0:
            logger.info("Seeding phone reputation threat intelligence into MySQL...")
            for phone in INITIAL_PHONE_REPUTATIONS:
                db.add(PhoneReputation(**phone))
            db.commit()

        # 2. Seed Domain Blacklist
        existing_domains = db.query(DomainBlacklist).count()
        if existing_domains == 0:
            logger.info("Seeding domain blacklist into MySQL...")
            for domain in INITIAL_DOMAIN_BLACKLIST:
                db.add(DomainBlacklist(**domain))
            db.commit()

        # 3. Seed Training Corpus
        existing_corpus = db.query(SpamTrainingCorpus).count()
        if existing_corpus == 0:
            logger.info("Seeding training corpus into MySQL database...")
            data = get_training_data()
            for item in data:
                db.add(SpamTrainingCorpus(
                    text_content=item["text"],
                    label=item["label"],
                    category="Curated Seed",
                    source="Cybersecurity_Corpus",
                    is_verified=True
                ))
            db.commit()

        # 4. Seed Historical Scan Logs for Analytics Dashboard
        existing_logs = db.query(ScanLog).count()
        if existing_logs == 0:
            logger.info("Seeding realistic historical telemetry into MySQL scan_logs...")
            historical_samples = [
                {
                    "scan_type": "message",
                    "channel": "sms",
                    "sender": "+1 (800) 242-7338",
                    "content": "URGENT: Chase Bank alert. Your debit card has been temporarily locked due to suspicious activity. Verify immediately at http://chase-security-verify.net/login",
                    "classification": "High Risk Scam",
                    "score": 93.5,
                    "confidence": 0.98,
                    "summary": "CRITICAL WARNING: Phishing smishing with fake Chase Bank lock alert.",
                    "hours_ago": 2
                },
                {
                    "scan_type": "call",
                    "channel": "voice_call",
                    "sender": "+1 (202) 555-0199",
                    "content": "IRS Officer James calling regarding 3 federal arrest allegations. Settle $2500 via wire or police will arrest you within 1 hour.",
                    "classification": "High Risk Scam",
                    "score": 99.0,
                    "confidence": 0.99,
                    "summary": "VISHING DETECTED: IRS arrest warrant impersonation scam.",
                    "hours_ago": 5
                },
                {
                    "scan_type": "message",
                    "channel": "sms",
                    "sender": "USPS-ALERT",
                    "content": "USPS Delivery: Unpaid customs fee of $2.49 required. Update payment at http://usps-tracking-redelivery.buzz",
                    "classification": "High Risk Scam",
                    "score": 91.0,
                    "confidence": 0.97,
                    "summary": "CRITICAL: Malicious delivery phishing bait targeting credentials.",
                    "hours_ago": 8
                },
                {
                    "scan_type": "message",
                    "channel": "sms",
                    "sender": "72972",
                    "content": "Bank of America: Security code 827419 for your Zelle transfer. Do NOT share this code with anyone over phone or text.",
                    "classification": "Safe",
                    "score": 4.0,
                    "confidence": 0.99,
                    "summary": "SAFE: Verified official Bank of America 2FA security code.",
                    "hours_ago": 12
                },
                {
                    "scan_type": "message",
                    "channel": "sms",
                    "sender": "+1 (555) 492-0192",
                    "content": "Pre-Approved Loan: You qualify for $50,000 personal loan 0% interest for 6 months. Apply today at http://fast-cash-loans-today.club",
                    "classification": "Suspicious",
                    "score": 58.0,
                    "confidence": 0.88,
                    "summary": "CAUTION: Unsolicited aggressive predatory lending promo.",
                    "hours_ago": 15
                },
                {
                    "scan_type": "call",
                    "channel": "voice_call",
                    "sender": "+1 (888) 555-0144",
                    "content": "This is bank security fraud division. Unauthorized charge of $1,200. Please read back the 6-digit OTP code to cancel.",
                    "classification": "High Risk Scam",
                    "score": 97.5,
                    "confidence": 0.99,
                    "summary": "CRITICAL VISHING: Live OTP interception attempt.",
                    "hours_ago": 20
                },
                {
                    "scan_type": "message",
                    "channel": "email",
                    "sender": "shipping@fedex.com",
                    "content": "FedEx: Your shipment with tracking number 78923482910 has been delivered to your front porch at 2:15 PM.",
                    "classification": "Safe",
                    "score": 3.0,
                    "confidence": 0.99,
                    "summary": "SAFE: Standard carrier delivery receipt notification.",
                    "hours_ago": 26
                },
                {
                    "scan_type": "message",
                    "channel": "whatsapp",
                    "sender": "+1 (202) 555-0143",
                    "content": "Earn $300-$800 daily working from home reviewing hotels on WhatsApp! Immediate payout in USDT crypto.",
                    "classification": "High Risk Scam",
                    "score": 88.0,
                    "confidence": 0.96,
                    "summary": "CRITICAL: Task employment phishing and crypto investment scam.",
                    "hours_ago": 30
                }
            ]

            for item in historical_samples:
                created_dt = datetime.utcnow() - timedelta(hours=item["hours_ago"])
                log = ScanLog(
                    id=str(uuid.uuid4()),
                    scan_type=item["scan_type"],
                    channel=item["channel"],
                    sender_or_caller=item["sender"],
                    raw_content=item["content"],
                    classification=item["classification"],
                    risk_score=item["score"],
                    confidence=item["confidence"],
                    summary=item["summary"],
                    indicators=[{"category": "Historical Intelligence", "title": "Verified Incident", "severity": "high", "weight": 20}],
                    urls_analyzed=[],
                    recommendations=["Logged in enterprise threat database."],
                    created_at=created_dt
                )
                db.add(log)
            db.commit()

        logger.info("MySQL database tables and threat intelligence data populated successfully.")
    except Exception as e:
        logger.error(f"Error during MySQL database seeding: {e}")
        db.rollback()
    finally:
        db.close()

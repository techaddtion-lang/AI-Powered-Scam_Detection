import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    JSON,
    Boolean,
    Index
)
from app.db.connection import Base


class ScanLog(Base):
    """Stores full audit logs for every analyzed message, call transcript, or URL."""
    __tablename__ = "scan_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_type = Column(String(20), nullable=False, index=True)  # 'message', 'call', 'url'
    channel = Column(String(30), default="sms")                # 'sms', 'whatsapp', 'email', 'voice_call'
    sender_or_caller = Column(String(100), nullable=True, index=True)
    raw_content = Column(Text, nullable=False)
    classification = Column(String(30), nullable=False, index=True)  # 'Safe', 'Suspicious', 'High Risk Scam'
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    indicators = Column(JSON, nullable=True)
    urls_analyzed = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    vishing_tactics = Column(JSON, nullable=True)
    ml_confidence_scores = Column(JSON, nullable=True)
    rule_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_scan_class_time", "classification", "created_at"),
    )


class PhoneReputation(Base):
    """Threat intelligence table for caller numbers, SMS senders, and reputation scores."""
    __tablename__ = "phone_reputation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(50), unique=True, nullable=False, index=True)
    entity_name = Column(String(150), nullable=False)
    reputation_status = Column(String(30), nullable=False, index=True)  # 'BLACKLISTED_SCAM', 'SUSPICIOUS_ROBOCALL', 'VERIFIED_OFFICIAL'
    threat_category = Column(String(50), nullable=False)               # 'IRS Scam', 'Bank Vishing', 'Tech Support', 'Carrier Alert'
    risk_score = Column(Float, nullable=False, default=95.0)
    reports_count = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_reported_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class DomainBlacklist(Base):
    """Threat intelligence table for known phishing domains, IP hosts, and malicious shorteners."""
    __tablename__ = "domain_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_name = Column(String(255), unique=True, nullable=False, index=True)
    threat_type = Column(String(50), nullable=False)                  # 'PHISHING', 'BRAND_TYPOSQUAT', 'IP_HOST_MASK', 'VERIFIED_SAFE'
    targeted_brand = Column(String(50), nullable=True)                # 'Chase', 'PayPal', 'USPS', 'Bank of America'
    risk_score = Column(Float, nullable=False, default=90.0)
    reports_count = Column(Integer, default=1)
    status = Column(String(30), default="ACTIVE_THREAT", index=True)  # 'ACTIVE_THREAT', 'RESOLVED', 'WHITELISTED'
    source = Column(String(50), default="Threat_Intel_Feed")
    created_at = Column(DateTime, default=datetime.utcnow)


class SpamTrainingCorpus(Base):
    """Database-backed training corpus used for model training and dynamic expansion."""
    __tablename__ = "spam_training_corpus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text_content = Column(Text, nullable=False)
    label = Column(String(30), nullable=False, index=True)            # 'High Risk Scam', 'Suspicious', 'Safe'
    category = Column(String(50), nullable=True)                      # 'Smishing', 'Vishing', 'Crypto', 'Delivery', 'Legit'
    source = Column(String(50), default="Curated_Seed")
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserFeedback(Base):
    """Telemetry feedback allowing analysts and users to report false alarms or confirm scams."""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), nullable=False, index=True)
    feedback_type = Column(String(30), nullable=False)                # 'CONFIRMED_SCAM', 'FALSE_POSITIVE', 'FALSE_NEGATIVE'
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

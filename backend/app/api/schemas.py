from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ClassificationLabel(str, Enum):
    SAFE = "Safe"
    SUSPICIOUS = "Suspicious"
    HIGH_RISK_SCAM = "High Risk Scam"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(str, Enum):
    URGENCY_PRESSURE = "Urgency & Intimidation"
    FINANCIAL_BAIT = "Financial Bait / Crypto / Wire"
    CREDENTIAL_THEFT = "Credential & OTP Theft"
    IMPERSONATION = "Brand & Authority Impersonation"
    SUSPICIOUS_LINK = "Malicious / Phishing URL"
    TECH_SUPPORT = "Tech Support / Remote Access"
    LEGAL_ARREST_THREAT = "Legal & Law Enforcement Threat"
    LOTTERY_PRIZE = "Lottery / Prize / Job Scam"
    DELIVERY_BAIT = "Delivery / Package Phishing"
    OTHER = "General Anomaly"


class DetectedIndicator(BaseModel):
    category: ThreatCategory
    title: str
    description: str
    severity: SeverityLevel
    matched_text: Optional[str] = None
    weight: float = 1.0


class UrlSafetyResult(BaseModel):
    url: str
    domain: str
    is_suspicious: bool
    risk_score: float = Field(..., ge=0, le=100)
    reasons: List[str] = []
    tld: Optional[str] = None
    has_ip_hostname: bool = False
    is_shortener: bool = False
    targeted_brand: Optional[str] = None


class MessageAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text message, email body, or transcript to analyze")
    sender_id: Optional[str] = Field(None, description="Phone number, email, or sender handle")
    channel: Optional[str] = Field("sms", description="sms, whatsapp, email, telegram, or other")


class MessageAnalysisResponse(BaseModel):
    id: str
    input_text: str
    classification: ClassificationLabel
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score from 0 (safe) to 100 (high scam)")
    confidence: float = Field(..., ge=0, le=1.0, description="Confidence score from 0 to 1")
    summary: str
    indicators: List[DetectedIndicator]
    category_breakdown: Dict[str, float]
    urls_analyzed: List[UrlSafetyResult]
    recommendations: List[str]
    ml_confidence_scores: Dict[str, float]
    rule_score: float
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class CallAnalysisRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="Transcribed audio of the telephone call")
    caller_number: Optional[str] = Field(None, description="Incoming phone number or caller ID")
    call_duration_seconds: Optional[int] = Field(None, ge=0, description="Duration of call in seconds")
    call_direction: Optional[str] = Field("inbound", description="inbound or outbound")


class CallAnalysisResponse(BaseModel):
    id: str
    transcript: str
    caller_number: Optional[str] = None
    classification: ClassificationLabel
    risk_score: float = Field(..., ge=0, le=100)
    confidence: float
    summary: str
    vishing_tactics_detected: List[str]
    indicators: List[DetectedIndicator]
    category_breakdown: Dict[str, float]
    recommendations: List[str]
    ml_confidence_scores: Dict[str, float]
    rule_score: float
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=3, description="URL or domain to analyze")


class BatchAnalysisRequest(BaseModel):
    messages: List[MessageAnalysisRequest]


class BatchAnalysisResponse(BaseModel):
    total_processed: int
    scam_count: int
    suspicious_count: int
    safe_count: int
    average_risk_score: float
    results: List[MessageAnalysisResponse]


class SampleItem(BaseModel):
    id: str
    type: str  # "sms", "call", "email"
    title: str
    description: str
    content: str
    sender_or_caller: Optional[str] = None
    expected_classification: ClassificationLabel

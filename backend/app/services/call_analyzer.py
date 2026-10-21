import re
from typing import List, Dict, Any, Tuple, Optional
from app.api.schemas import DetectedIndicator, ThreatCategory, SeverityLevel

VISHING_TACTICS = [
    {
        "name": "Live OTP Interception",
        "pattern": r"(read\s+(?:me|out)?\s*(?:the|your)?\s*(?:\d+[- ]digit\s*)?(?:otp|code|pin|verification)|what\s+is\s+(?:the|your)?\s*(?:\d+[- ]digit\s*)?(?:code|number|otp|pin))",
        "description": "Caller tries to steal an active 2-Factor Authentication code in real-time."
    },
    {
        "name": "Caller Isolation & Gag Tactics",
        "pattern": r"(do\s+not\s+(?:hang\s+up|disconnect|tell\s+(?:your|anyone|family|the\s+teller))|stay\s+on\s+the\s+line)",
        "description": "Scammer attempts to isolate the victim and prevent second opinions."
    },
    {
        "name": "Robocall / Automated IVR Lure",
        "pattern": r"(press\s+(?:1|one|9|nine)\s+to\s+(?:speak|talk|connect)|automated\s+(?:recording|dispatch|call))",
        "description": "Automated voice broadcast fishing for receptive victims."
    },
    {
        "name": "Physical Travel Coercion (ATM / Gift Card Store)",
        "pattern": r"(go\s+to\s+(?:the\s+)?(?:store|walmart|target|cvs|bank|atm|crypto\s+kiosk|coinme)|drive\s+to)",
        "description": "Directing the victim to travel to a physical kiosk to purchase untraceable vouchers."
    },
    {
        "name": "Immediate Arrest Intimidation",
        "pattern": r"(deputies\s+are\s+(?:on\s+the\s+way|en\s+route)|officers\s+will\s+arrest\s+you|warrant\s+(?:has\s+been\s+issued|for\s+your\s+arrest))",
        "description": "Fabricating law enforcement involvement to create acute panic."
    }
]


def check_caller_number(number: Optional[str]) -> Tuple[float, List[str]]:
    """Evaluate caller ID metadata for suspicious attributes."""
    if not number:
        return 0.0, []

    risk = 0.0
    flags = []
    cleaned_num = re.sub(r'[\s\-\(\)\.]', '', number)

    # Check for suspicious international prefixes targeting domestic victims
    high_risk_country_codes = ["+234", "+232", "+233", "+92", "+371", "+375", "+79"]
    for code in high_risk_country_codes:
        if cleaned_num.startswith(code):
            risk += 25.0
            flags.append(f"Foreign country code ({code}) detected on incoming call")
            break

    # Check for short or spoofed patterns (like 0000000000 or 123456)
    if re.match(r'^0+$', cleaned_num) or cleaned_num in ["1234567890", "9999999999"]:
        risk += 35.0
        flags.append("Obvious spoofed caller ID pattern")

    return risk, flags


def analyze_vishing_transcript(transcript: str) -> Tuple[List[str], List[DetectedIndicator], float]:
    """Identify voice-specific scam vectors in call transcripts."""
    vishing_tactics: List[str] = []
    indicators: List[DetectedIndicator] = []
    vishing_score = 0.0

    lowered = transcript.lower()

    for tactic in VISHING_TACTICS:
        match = re.search(tactic["pattern"], lowered, re.IGNORECASE)
        if match:
            vishing_tactics.append(tactic["name"])
            vishing_score += 25.0
            indicators.append(DetectedIndicator(
                category=ThreatCategory.URGENCY_PRESSURE,
                title=f"Vishing Vector: {tactic['name']}",
                description=tactic["description"],
                severity=SeverityLevel.HIGH,
                matched_text=match.group(0),
                weight=25.0
            ))

    return vishing_tactics, indicators, min(vishing_score, 50.0)

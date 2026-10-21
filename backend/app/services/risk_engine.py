import re
from typing import List, Dict, Any, Tuple
from app.api.schemas import ThreatCategory, SeverityLevel, DetectedIndicator

# Comprehensive pattern definitions with categories and severity
HEURISTIC_RULES = [
    # 1. Urgency & Intimidation
    {
        "category": ThreatCategory.URGENCY_PRESSURE,
        "title": "Extreme Urgency Pressure",
        "description": "Message forces quick action without time to think or independently verify.",
        "severity": SeverityLevel.HIGH,
        "weight": 20.0,
        "patterns": [
            r"\b(immediately|urgent|urgently|act now|right now|within \d+ (hours?|mins?|minutes?)|without delay)\b",
            r"\b(final notice|final warning|last warning|time[- ]sensitive|limited time left)\b",
            r"\b(account (will be|has been) (suspended|terminated|frozen|locked|blocked|deleted))\b",
            r"\b(failure to comply|immediate action required|service (disconnection|cutoff))\b"
        ]
    },
    # 2. Financial Bait & Demands
    {
        "category": ThreatCategory.FINANCIAL_BAIT,
        "title": "Unusual Payment / Financial Bait",
        "description": "Requests funds via non-standard, untraceable methods or warns of unexpected financial transfers.",
        "severity": SeverityLevel.HIGH,
        "weight": 25.0,
        "patterns": [
            r"\b(wire transfer|moneygram|western union|zelle|cash app|venmo transfer)\b",
            r"\b(gift cards?|apple (gift )?card|target (gift )?card|google play card|greendot)\b",
            r"\b(bitcoin|crypto|usdt|btc wallet|ethereum|wallet address)\b",
            r"\b(unauthorized (charge|transaction|purchase|payment) of \$?\d+)\b",
            r"\b(refund of \$?\d+|overpayment|processing fee of \$?\d+)\b"
        ]
    },
    # 3. Credential & OTP Theft
    {
        "category": ThreatCategory.CREDENTIAL_THEFT,
        "title": "Sensitive Credentials / OTP Solicitation",
        "description": "Attempts to harvest two-factor authentication codes, passwords, or personal identity numbers.",
        "severity": SeverityLevel.CRITICAL,
        "weight": 35.0,
        "patterns": [
            r"\b(one[- ]time (passcode|password)|otp|verification code|security code)\b",
            r"\b(share (the|your) (otp|code|pin)|read (back|out) the (code|otp))\b",
            r"\b(enter your (password|pin|cvv|security code|atm pin))\b",
            r"\b(social security( number)?|ssn|tax id|credit card details|expiration date)\b",
            r"\b(confirm your (credentials|identity|login|banking details))\b"
        ]
    },
    # 4. Impersonation of Authorities or Well-Known Brands
    {
        "category": ThreatCategory.IMPERSONATION,
        "title": "Authority or Brand Impersonation",
        "description": "Pretends to represent a trusted entity like a bank, government office, or courier.",
        "severity": SeverityLevel.HIGH,
        "weight": 25.0,
        "patterns": [
            r"\b(internal revenue service|irs|social security administration|ssa|border patrol|customs and border)\b",
            r"\b(chase bank|wells fargo|bank of america|citibank|capital one|fraud department)\b",
            r"\b(usps delivery|fedex express|dhl express|ups parcel|package clearance)\b",
            r"\b(amazon prime security|apple support|geek squad|microsoft defender|windows support)\b",
            r"\b(federal court|state police|local sheriff|investigator|warrant)\b"
        ]
    },
    # 5. Remote Access / Tech Support Scareware
    {
        "category": ThreatCategory.TECH_SUPPORT,
        "title": "Remote Access Scareware Tactic",
        "description": "Prompts victim to install remote desktop control software or claims malware infection.",
        "severity": SeverityLevel.CRITICAL,
        "weight": 35.0,
        "patterns": [
            r"\b(anydesk|teamviewer|ultraviewer|quicksupport|logmein|screen share)\b",
            r"\b(infected with (trojan|spyware|virus)|fatal error #0x|security breach detected)\b",
            r"\b(call (technical|tech) support|windows (security|defender) alert)\b",
            r"\b(do not (restart|turn off) your (pc|computer))\b"
        ]
    },
    # 6. Legal / Arrest / Law Enforcement Threats
    {
        "category": ThreatCategory.LEGAL_ARREST_THREAT,
        "title": "Coercive Legal / Arrest Threats",
        "description": "Uses intimidation, legal summons, or fake arrest warrants to induce panic.",
        "severity": SeverityLevel.CRITICAL,
        "weight": 30.0,
        "patterns": [
            r"\b(arrest warrant|detained|taken into custody|local police will arrive)\b",
            r"\b(criminal charges?|indictment|court summons|legal proceedings)\b",
            r"\b(asset seizure|wage garnishment|frozen assets|federal warrant)\b",
            r"\b(do not hang up|keep this (matter )?confidential|secret investigation)\b"
        ]
    },
    # 7. Lottery, Prizes & Unsolicited Wealth
    {
        "category": ThreatCategory.LOTTERY_PRIZE,
        "title": "Lottery / Prize / Work-from-Home Bait",
        "description": "Promises unrealistic cash prizes, grants, or quick high-paying job opportunities.",
        "severity": SeverityLevel.MEDIUM,
        "weight": 20.0,
        "patterns": [
            r"\b(congratulations!? you (have )?won|selected as (a|the) (lucky )?winner)\b",
            r"\b(claim your (\$?\d+|lottery|prize|reward|gift voucher|grant))\b",
            r"\b(guaranteed (daily|weekly) return|earn \$?\d+ (daily|per day) from home)\b",
            r"\b(reviewing (hotels|products) on whatsapp|telegram task)\b",
            r"\b(unclaimed inheritance|abandoned estate|million dollars?)\b"
        ]
    },
    # 8. Delivery / Package Clearance Phishing
    {
        "category": ThreatCategory.DELIVERY_BAIT,
        "title": "Package Delivery / Customs Bait",
        "description": "Claims a delivery failed or requires a small fee to clear customs or reschedule.",
        "severity": SeverityLevel.HIGH,
        "weight": 22.0,
        "patterns": [
            r"\b(delivery (failed|attempted|on hold)|package is (waiting|pending))\b",
            r"\b(unpaid (customs|vat|delivery) fee of \$?\d+(\.\d{2})?)\b",
            r"\b(update (your )?(address|street|shipping info) to (reschedule|receive))\b",
            r"\b(missing house number|parcel cannot be delivered)\b"
        ]
    }
]

# Actionable recommendations mapped to categories
CATEGORY_RECOMMENDATIONS = {
    ThreatCategory.URGENCY_PRESSURE: [
        "Take a breath: Scammers rely on artificial urgency to prevent you from thinking critically or checking facts.",
        "Never make hasty financial decisions or click links under pressure."
    ],
    ThreatCategory.FINANCIAL_BAIT: [
        "No legitimate business or government body requires payment via Gift Cards, Bitcoin, or wire transfer.",
        "Do not send money or verify payments through unfamiliar payment links."
    ],
    ThreatCategory.CREDENTIAL_THEFT: [
        "NEVER disclose One-Time Passwords (OTPs), PINs, or CVVs to anyone over the phone or text, even if they claim to be your bank.",
        "Banks and reputable companies will NEVER ask for your password or verification code."
    ],
    ThreatCategory.IMPERSONATION: [
        "Hang up or close the message immediately.",
        "Independently verify by navigating to the organization's official website or calling the customer service number printed on the back of your official card."
    ],
    ThreatCategory.SUSPICIOUS_LINK: [
        "Do not tap or click on any URLs in this message.",
        "Never submit credentials, banking information, or personal documents on unfamiliar web domains."
    ],
    ThreatCategory.TECH_SUPPORT: [
        "Never install AnyDesk, TeamViewer, or remote access software at the request of an unsolicited caller or popup.",
        "Microsoft, Apple, and Google do not issue popups with phone numbers to call for antivirus cleaning."
    ],
    ThreatCategory.LEGAL_ARREST_THREAT: [
        "Law enforcement agencies, the IRS, and courts never notify people of arrest warrants or legal action via SMS or phone calls demanding payment.",
        "If concerned, contact your local police department directly via their official non-emergency number."
    ],
    ThreatCategory.LOTTERY_PRIZE: [
        "If you did not enter a lottery or contest, you cannot win one.",
        "Legitimate lotteries and job recruiters will never ask for an upfront 'clearance' or 'application' fee."
    ],
    ThreatCategory.DELIVERY_BAIT: [
        "Do not pay unexpected small fees to release packages.",
        "Check your order history directly in the official retailer app (Amazon, eBay, etc.) or look up tracking codes on official carrier sites (usps.com, fedex.com)."
    ]
}


def analyze_text_rules(text: str) -> Tuple[List[DetectedIndicator], Dict[str, float], float, List[str]]:
    """
    Run regex heuristic rules across the input text.
    Returns:
    - indicators: list of DetectedIndicator
    - category_breakdown: category name -> accumulated severity score
    - total_rule_score: normalized composite score (0 - 100)
    - recommendations: list of recommended actions
    """
    lowered_text = text.lower()
    detected_indicators: List[DetectedIndicator] = []
    category_scores: Dict[str, float] = {}
    recommendations_set = set()

    raw_score = 0.0

    for rule in HEURISTIC_RULES:
        category = rule["category"]
        category_name = category.value
        matched_snippets = []

        for pattern in rule["patterns"]:
            matches = list(re.finditer(pattern, lowered_text, re.IGNORECASE))
            if matches:
                for match in matches:
                    matched_snippets.append(match.group(0))

        if matched_snippets:
            unique_matches = list(dict.fromkeys(matched_snippets))
            indicator = DetectedIndicator(
                category=category,
                title=rule["title"],
                description=rule["description"],
                severity=rule["severity"],
                matched_text=", ".join(unique_matches[:3]),
                weight=rule["weight"]
            )
            detected_indicators.append(indicator)

            # Score calculations
            added_weight = rule["weight"] * min(len(unique_matches), 2)
            raw_score += added_weight
            category_scores[category_name] = category_scores.get(category_name, 0.0) + added_weight

            # Add corresponding recommendations
            if category in CATEGORY_RECOMMENDATIONS:
                for rec in CATEGORY_RECOMMENDATIONS[category]:
                    recommendations_set.add(rec)

    # Contextual check: ALL CAPS urgency bonus
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 3 and w.isalpha()]
    if len(caps_words) >= 3:
        raw_score += 10.0
        detected_indicators.append(DetectedIndicator(
            category=ThreatCategory.URGENCY_PRESSURE,
            title="Aggressive Formatting (All Caps)",
            description="Excessive uppercase phrasing used to induce alarm or panic.",
            severity=SeverityLevel.LOW,
            matched_text=" ".join(caps_words[:4]),
            weight=10.0
        ))

    # Normalize rule score to 0 - 100
    normalized_rule_score = min(max(raw_score, 0.0), 100.0)

    # Default safe recommendation if no triggers found
    recommendations_list = list(recommendations_set)
    if not recommendations_list:
        recommendations_list = [
            "No active scam indicators or pressure tactics detected in this message.",
            "Standard safety hygiene: Always exercise caution before downloading unexpected attachments or entering credentials."
        ]

    return detected_indicators, category_scores, round(normalized_rule_score, 1), recommendations_list

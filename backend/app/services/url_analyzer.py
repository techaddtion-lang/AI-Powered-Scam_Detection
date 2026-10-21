import re
from urllib.parse import urlparse
from typing import List, Tuple, Dict, Any, Optional
from app.api.schemas import UrlSafetyResult

# Common TLDs often abused in smishing/phishing campaigns
SUSPICIOUS_TLDS = {
    "xyz", "top", "buzz", "click", "work", "cam", "icu", "live", "club",
    "site", "vip", "win", "country", "tk", "ml", "ga", "cf", "gq", "rest", "fit", "download"
}

# Known URL shorteners used to mask phishing destinations
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "is.gd", "t.co", "cutt.ly", "rb.gy", "ow.ly",
    "buff.ly", "tiny.cc", "goo.gl", "rebrand.ly", "bl.ink", "shorturl.at"
}

# Brands frequently targeted by smishing and credential harvesting
TARGETED_BRANDS = [
    "paypal", "chase", "wellsfargo", "bankofamerica", "citibank", "capitalone",
    "amazon", "apple", "netflix", "microsoft", "google", "usps", "fedex",
    "dhl", "ups", "binance", "coinbase", "whatsapp", "telegram", "facebook",
    "irs", "socialsecurity", "walmart", "target", "costco"
]

# Legitimate official domain suffixes for known brands
OFFICIAL_DOMAINS = {
    "paypal": ["paypal.com", "paypal.me"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com", "bofa.com"],
    "citibank": ["citi.com", "citibank.com"],
    "capitalone": ["capitalone.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.de"],
    "apple": ["apple.com", "icloud.com"],
    "netflix": ["netflix.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com"],
    "google": ["google.com"],
    "usps": ["usps.com"],
    "fedex": ["fedex.com"],
    "dhl": ["dhl.com"],
    "ups": ["ups.com"],
    "binance": ["binance.com"],
    "coinbase": ["coinbase.com"],
    "whatsapp": ["whatsapp.com"],
    "telegram": ["telegram.org", "t.me"]
}

# Suspicious path tokens
PHISHING_PATH_KEYWORDS = [
    "login", "signin", "verify", "verification", "update", "security",
    "auth", "authenticate", "confirm", "account-suspended", "webscr",
    "wallet", "claim", "billing", "recover", "unlock", "kyc", "dispute"
]

# Regex to detect URLs in plain text (both with and without scheme)
URL_REGEX = re.compile(
    r'(?:https?://)?'                                          # scheme
    r'(?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+' # domain name
    r'[A-Za-z]{2,}|'                                          # TLD
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'                   # OR IPv4 address
    r'(?::\d+)?'                                              # optional port
    r'(?:/?|[/?]\S+)',                                        # path & query
    re.IGNORECASE
)

# Regex to detect raw IPv4 hostname
IP_HOST_REGEX = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')


def extract_urls(text: str) -> List[str]:
    """Extract all URLs or web links found inside a message."""
    matches = URL_REGEX.findall(text)
    cleaned = []
    for m in matches:
        cleaned_url = m.strip(".,;:()[]\"'<>")
        # Filter out common false positives like "e.g.", "vs.", "am.", "pm."
        if "." in cleaned_url and not any(cleaned_url.lower().endswith(fp) for fp in [".e.g", ".com.", ".i.e", ".etc"]):
            if len(cleaned_url) >= 4:
                cleaned.append(cleaned_url)
    return list(dict.fromkeys(cleaned))  # Deduplicate while preserving order


def analyze_url(raw_url: str) -> UrlSafetyResult:
    """
    Perform multi-vector risk analysis on a single extracted URL:
    - IP address hostname check
    - Suspicious or untrusted TLD check
    - Shortener detection
    - Brand spoofing / typosquatting detection
    - Phishing path keywords
    - Subdomain obfuscation
    """
    url_to_parse = raw_url if "://" in raw_url else f"http://{raw_url}"
    parsed = urlparse(url_to_parse)

    domain = (parsed.hostname or parsed.netloc or "").lower().split(":")[0]
    path = (parsed.path or "").lower()
    full_str = f"{domain}{path}"

    risk_score = 0.0
    reasons: List[str] = []
    has_ip_hostname = bool(IP_HOST_REGEX.match(domain))
    is_shortener = domain in SHORTENER_DOMAINS or any(domain.endswith("." + s) for s in SHORTENER_DOMAINS)
    targeted_brand: Optional[str] = None

    # 1. IP Hostname Check (Very dangerous in SMS/phishing)
    if has_ip_hostname:
        risk_score += 65.0
        reasons.append("Raw IP address used as hostname instead of a verified domain")

    # 2. Extract and check TLD
    domain_parts = domain.split(".")
    tld = domain_parts[-1] if len(domain_parts) > 1 else ""
    if tld in SUSPICIOUS_TLDS:
        risk_score += 35.0
        reasons.append(f"High-risk Top-Level Domain (.{tld}) commonly associated with disposable phishing campaigns")

    # 3. URL Shortener Check
    if is_shortener:
        risk_score += 25.0
        reasons.append(f"URL Shortener detected ({domain}), hiding true destination and bypassing security inspection")

    # 4. Brand Spoofing / Typosquatting Check
    for brand in TARGETED_BRANDS:
        if brand in full_str:
            official = OFFICIAL_DOMAINS.get(brand, [f"{brand}.com"])
            # Check if domain actually ends with an official domain
            is_legit = any(domain == off or domain.endswith("." + off) for off in official)

            if not is_legit:
                targeted_brand = brand
                risk_score += 50.0
                reasons.append(f"Brand impersonation detected: claims to be '{brand.title()}' but hosted on '{domain}'")
                break

    # 5. Phishing Keywords in Path or Subdomains
    matched_path_keywords = [kw for kw in PHISHING_PATH_KEYWORDS if kw in path or kw in domain]
    if matched_path_keywords:
        added_risk = min(len(matched_path_keywords) * 12.0, 30.0)
        risk_score += added_risk
        reasons.append(f"Credential harvesting keywords found in URL path: {', '.join(matched_path_keywords[:3])}")

    # 6. Deep Subdomain Chaining (e.g. bank.us.secure-login.xyz)
    if len(domain_parts) >= 4 and not has_ip_hostname:
        risk_score += 15.0
        reasons.append("Excessive subdomain nesting (>3 levels), typical of evasion techniques")

    # 7. Obfuscated / Special Characters in URL
    if "@" in raw_url:
        risk_score += 40.0
        reasons.append("URL contains '@' credential notation, often used to mislead the visual destination")

    if "xn--" in domain:
        risk_score += 30.0
        reasons.append("Punycode / IDN homograph domain detected, possibly disguising deceptive characters")

    # Normalize risk score between 0 and 100
    normalized_risk = min(max(risk_score, 0.0), 100.0)
    is_suspicious = normalized_risk >= 35.0

    return UrlSafetyResult(
        url=raw_url,
        domain=domain,
        is_suspicious=is_suspicious,
        risk_score=round(normalized_risk, 1),
        reasons=reasons,
        tld=tld if tld else None,
        has_ip_hostname=has_ip_hostname,
        is_shortener=is_shortener,
        targeted_brand=targeted_brand
    )


def evaluate_message_urls(text: str) -> Tuple[List[UrlSafetyResult], float]:
    """
    Extract and analyze all URLs in a message text.
    Returns (list of UrlSafetyResult, max URL risk score).
    """
    urls = extract_urls(text)
    if not urls:
        return [], 0.0

    results = [analyze_url(u) for u in urls]
    max_url_risk = max((r.risk_score for r in results), default=0.0)
    return results, max_url_risk

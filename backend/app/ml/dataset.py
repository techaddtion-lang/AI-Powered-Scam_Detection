"""
High quality curated dataset for SMS, email, and call transcript scam detection.
Includes diverse training samples across Safe, Suspicious, and High Risk Scam categories.
"""

TRAINING_DATA = [
    # ---------------- HIGH RISK SCAM: Banking & Phishing ----------------
    {
        "text": "URGENT: Chase Bank alert. Your debit card has been temporarily locked due to suspicious activity of $842.10. Verify immediately at http://chase-security-verify.net/login to prevent permanent block.",
        "label": "High Risk Scam"
    },
    {
        "text": "Wells Fargo Security: We detected an unauthorized sign-in from Russia. If this was not you, visit http://192.168.1.120/wellsfargo/auth.php right now to secure your account or funds will be frozen.",
        "label": "High Risk Scam"
    },
    {
        "text": "Bank of America Notification: Immediate action required. Your account has been suspended due to incomplete KYC verification. Click here to confirm identity: http://bofa-kyc-update.xyz/login",
        "label": "High Risk Scam"
    },
    {
        "text": "PayPal Alert: You sent a payment of $1,499.00 to CryptoExchange Inc. If you did not make this purchase, call our fraud department immediately at 1-800-555-0199 or click http://bit.ly/paypal-dispute-99",
        "label": "High Risk Scam"
    },
    {
        "text": "Citibank: An unauthorized transfer of $2,300 to John Doe is pending. To cancel this transaction, share the 6-digit OTP code received on your phone with our security agent.",
        "label": "High Risk Scam"
    },
    {
        "text": "Your Apple ID has been locked for security reasons. All purchases disabled. Visit http://apple-security-support.top/unlock to verify your credit card and SSN now.",
        "label": "High Risk Scam"
    },
    {
        "text": "ALERT: Amazon Prime renewal fee of $399 will be charged to your card. Call 1-888-402-9981 right away to cancel subscription and request immediate refund.",
        "label": "High Risk Scam"
    },
    {
        "text": "USPS Delivery: We attempted to deliver your package #US92839482, but an unpaid customs clearance fee of $2.49 is required. Update your address & payment at http://usps-tracking-redelivery.buzz",
        "label": "High Risk Scam"
    },
    {
        "text": "FedEx Express: Your parcel is on hold due to missing street address. Confirm payment details within 12 hours at http://tinyurl.com/fedex-package-reschedule or package will be returned to sender.",
        "label": "High Risk Scam"
    },
    {
        "text": "DHL Express notice: Package delivery failed. Pay outstanding VAT charge of $3.50 at http://dhl-customs-release.click/pay to release your shipment today.",
        "label": "High Risk Scam"
    },

    # ---------------- HIGH RISK SCAM: Government, Law Enforcement & Threats ----------------
    {
        "text": "Internal Revenue Service (IRS): A legal arrest warrant has been issued in your name regarding tax evasion of $4,850. Call 855-019-3321 immediately to settle via wire or local sheriff will detain you within 2 hours.",
        "label": "High Risk Scam"
    },
    {
        "text": "Social Security Administration Alert: Your SSN has been linked to drug trafficking and money laundering in Texas. Your benefits are suspended. Dial 800-443-0911 right now to speak with federal investigator Mark Miller.",
        "label": "High Risk Scam"
    },
    {
        "text": "Notice of Legal Action: Final summons from State Federal Court. Failure to appear will result in immediate wage garnishment and asset seizure. Settle fine of $950 via Target or Apple gift cards today.",
        "label": "High Risk Scam"
    },
    {
        "text": "United States Customs and Border Protection: We intercepted an international parcel containing illegal narcotics and fake passports under your identity. Contact legal officer Cooper immediately.",
        "label": "High Risk Scam"
    },
    {
        "text": "Urgent Electric Utility Warning: Your electricity power supply will be permanently cut off within 45 minutes due to overdue bill of $318. Call our automated payment desk at 888-921-0023 immediately to pay via prepaid debit card.",
        "label": "High Risk Scam"
    },

    # ---------------- HIGH RISK SCAM: Tech Support & Remote Access ----------------
    {
        "text": "Microsoft Windows Defender Warning: Fatal Error #0x80070422. Your computer is infected with Trojan Spyware stealing passwords and financial data. Do not turn off your computer. Call Microsoft Support at 1-800-244-8833 immediately.",
        "label": "High Risk Scam"
    },
    {
        "text": "Geek Squad Best Buy: Auto-renewal confirmation for 3 years antivirus protection $499.99 successfully charged. If you wish to cancel or dispute, call 1-844-320-9921 to connect to our refund desk.",
        "label": "High Risk Scam"
    },
    {
        "text": "Tech Support: We detected multiple hackers accessing your network router. Install AnyDesk or TeamViewer on your PC immediately and provide your 9-digit connection code to our certified Microsoft engineer.",
        "label": "High Risk Scam"
    },

    # ---------------- HIGH RISK SCAM: Call Transcripts (Vishing) ----------------
    {
        "text": "Hello, this is Officer James from the IRS Department. I am calling to inform you that there are 3 federal criminal allegations against your Social Security Number. If you do not pay the penalty of $2,500 today using electronic voucher or wire transfer, the local police department will arrest you at your residence within one hour. Do not hang up this call.",
        "label": "High Risk Scam"
    },
    {
        "text": "Good day sir, I am calling from the fraud security division of your bank. We noticed an unauthorized charge of $1,200 on your account. To reverse this transaction immediately, I have sent a 6-digit confirmation code to your mobile phone. Please read that OTP code to me right now so I can cancel the charge.",
        "label": "High Risk Scam"
    },
    {
        "text": "Grandma? It's me, your grandson. Please don't tell mom or dad, I got into a terrible car accident and I am in jail. The public defender says I need $3,000 bail money right now. Please go to Walmart and send a MoneyGram wire transfer or buy Google Play gift cards.",
        "label": "High Risk Scam"
    },
    {
        "text": "This is automated dispatch from Power & Electric Company. Your service is scheduled for disconnection within 30 minutes due to unpaid dues. Press 1 to speak to an agent or call 888-444-1234 to make an immediate payment via GreenDot prepaid card.",
        "label": "High Risk Scam"
    },
    {
        "text": "Hello this is Kevin from Windows Technical Support. Our servers are receiving foreign hacking signals from your computer IP address. Please sit in front of your computer, press Windows key and R, and type support.anydesk.com so I can take remote control and clean the virus.",
        "label": "High Risk Scam"
    },

    # ---------------- HIGH RISK SCAM: Crypto, Lottery, Fake Jobs ----------------
    {
        "text": "Congratulations! You have been selected as the 1st prize winner of the International Mega Millions Lottery $2,500,000! To claim your payout, transfer $350 processing fee via Bitcoin wallet 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa.",
        "label": "High Risk Scam"
    },
    {
        "text": "Binance VIP: Your cryptocurrency withdrawal of 1.45 BTC is pending confirmation. If this was not authorized by you, cancel transaction immediately at http://binance-security-cancel.xyz",
        "label": "High Risk Scam"
    },
    {
        "text": "Urgent Job Offer: Earn $300-$800 daily working 1 hour from home reviewing hotels on WhatsApp! No experience needed. Immediate payout in USDT. Contact manager Mrs. Sarah on WhatsApp: +1-202-555-0143",
        "label": "High Risk Scam"
    },
    {
        "text": "Hi Dad, I broke my phone and this is my new temporary number. I am in a big emergency and cannot access my mobile banking. Can you please pay this urgent bill of $750 for me right now? Account details attached.",
        "label": "High Risk Scam"
    },
    {
        "text": "WhatsApp Gold Edition is now available! Upgrade your WhatsApp to video call 100 people at once and see deleted messages. Download free at http://whatsapp-gold-update.buzz/download",
        "label": "High Risk Scam"
    },

    # ---------------- SUSPICIOUS: Borderline, Aggressive Marketing, Unsolicited Promos ----------------
    {
        "text": "Exclusive Pre-Approved Loan Offer! You are eligible for an instant personal cash loan up to $50,000 with 0% interest for 6 months. No credit score check required. Apply today: http://fast-cash-loans-today.club",
        "label": "Suspicious"
    },
    {
        "text": "Hey! Earn passive income with AI crypto trading bot. Guaranteed 200% return in 7 days without risk. Limited spots remaining for beta test. Join Telegram group t.me/cryptomillionairenow",
        "label": "Suspicious"
    },
    {
        "text": "Secret Shopper Opportunity: Mystery Shopper Inc is hiring evaluators in your zip code. Receive a $400 check in advance, evaluate local stores, and keep the leftover money. Reply YES to register.",
        "label": "Suspicious"
    },
    {
        "text": "URGENT REMINDER: Your vehicle warranty has expired or is about to lapse. You may be liable for expensive repair costs. Call 800-555-0182 to extend coverage with our auto care plan.",
        "label": "Suspicious"
    },
    {
        "text": "Free $100 Walmart gift card waiting for you! Complete a 2-minute survey regarding your shopping habits to receive instant reward code: http://surveys-rewards-promo.top/walmart",
        "label": "Suspicious"
    },
    {
        "text": "Hot stock alert! Symbol $XYZT is projected to surge 450% this week following proprietary biotech patent approval. Buy now before market opens tomorrow morning!",
        "label": "Suspicious"
    },
    {
        "text": "Hello, we found your resume on Indeed and would love to interview you for a remote Data Entry position paying $45/hour. Please message hiring coordinator on Telegram @hr_recruiter99",
        "label": "Suspicious"
    },
    {
        "text": "Debt Relief Program: Settle credit card debt and personal loans for up to 60% less without bankruptcy. Government assistance program enrollment ends Friday. Click http://debt-relief-now.info",
        "label": "Suspicious"
    },
    {
        "text": "Special Offer for selected customer! Win an iPhone 15 Pro Max for just $1. Spin the wheel to claim your prize now: http://spin-wheel-rewards.click/iphone",
        "label": "Suspicious"
    },
    {
        "text": "Unclaimed inheritance fund: Our legal chambers in London hold an abandoned estate of $8.2M belonging to deceased client with your surname. Contact Barrister Williams at barrister.williams@consultant.com",
        "label": "Suspicious"
    },
    {
        "text": "You have 1 new unread voice message from an unknown caller. Listen to recording: http://voicemail-notification-service.buzz/play?id=928374",
        "label": "Suspicious"
    },
    {
        "text": "Final notice to claim your unclaimed tax rebate voucher. Check your eligibility in 30 seconds at http://tax-rebate-finder.site",
        "label": "Suspicious"
    },

    # ---------------- SAFE: Legitimate Transactions, Notifications, Conversations ----------------
    {
        "text": "Your Google verification code is 492019. Never share this code with anyone. Google employees will never ask for this code.",
        "label": "Safe"
    },
    {
        "text": "Chase Alert: Your scheduled payment of $125.00 to ConEd was successful on Oct 18. View statement at chase.com or in the mobile app.",
        "label": "Safe"
    },
    {
        "text": "FedEx: Your shipment with tracking number 78923482910 has been delivered to your front porch at 2:15 PM. Thank you for using FedEx.",
        "label": "Safe"
    },
    {
        "text": "Your Uber ride with driver Michael is arriving in 3 minutes in a Silver Toyota Camry (License Plate: 7XYZ89).",
        "label": "Safe"
    },
    {
        "text": "Hi Sarah, are we still meeting for lunch at 12:30 at the Italian restaurant on 5th street? Let me know if you are running late!",
        "label": "Safe"
    },
    {
        "text": "Dr. Miller's Clinic: Reminder of your dental cleaning appointment scheduled for Thursday, Oct 24 at 10:00 AM. Reply 1 to Confirm or 2 to Reschedule.",
        "label": "Safe"
    },
    {
        "text": "United Airlines: Flight UA 452 from SFO to JFK is on time. Gate departure B22. Boarding begins at 4:45 PM. Check in at united.com.",
        "label": "Safe"
    },
    {
        "text": "Amazon: Your order #112-9842718-2948192 has shipped! Estimated delivery date: Tomorrow by 8 PM. Track your package at amazon.com/orders",
        "label": "Safe"
    },
    {
        "text": "Netflix: We received a request to update your account password. If you initiated this, click the link sent to your email. If not, log in to netflix.com/login and change your security settings.",
        "label": "Safe"
    },
    {
        "text": "Hey David, I pushed the latest commit to the git repo with the bug fix for the login page. Can you review the pull request when you have time?",
        "label": "Safe"
    },
    {
        "text": "Starbucks Rewards: Your reload of $25.00 using Apple Pay was successful. Your new Star balance is 142 stars. Enjoy your coffee!",
        "label": "Safe"
    },
    {
        "text": "School Notification: Parents, please note that Springfield Elementary will have an early dismissal tomorrow at 1:00 PM due to parent-teacher conferences.",
        "label": "Safe"
    },
    {
        "text": "Your CVS Pharmacy prescription #482910 is ready for pickup at 400 Main Street. Drive-thru is open until 9:00 PM.",
        "label": "Safe"
    },
    {
        "text": "Bank of America: Security code 827419 for your Zelle transfer. Do NOT share this code with anyone over phone or text. Bank associates will NEVER request this code.",
        "label": "Safe"
    },
    {
        "text": "Happy Birthday Grandma! Wishing you wonderful health and joy today. The kids made you handmade cards, we will see you on Sunday!",
        "label": "Safe"
    },
    {
        "text": "Your two-factor authentication code for GitHub is 849201. It expires in 10 minutes.",
        "label": "Safe"
    },
    {
        "text": "Target Order Pickup: Your order is ready! Pull into a designated drive-up parking space and let us know in the Target app when you arrive.",
        "label": "Safe"
    },
    {
        "text": "Hi team, weekly sprint planning meeting starts in 15 minutes in Conference Room B and on Zoom: zoom.us/j/9283948291",
        "label": "Safe"
    },
    {
        "text": "Your electric bill of $84.22 is scheduled for auto-debit on November 2nd. No action is required. View energy usage breakdown at pge.com",
        "label": "Safe"
    },
    {
        "text": "Library notice: The book 'Clean Architecture' you requested is now available for pickup at the central branch hold shelf.",
        "label": "Safe"
    }
]

def get_training_data():
    """Return the raw training data list of dictionaries."""
    return TRAINING_DATA

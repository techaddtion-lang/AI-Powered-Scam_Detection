import logging
from fastapi import APIRouter, Request, Response, Depends, Form
from fastapi.responses import PlainTextResponse
from typing import Optional

from app.api.schemas import MessageAnalysisRequest, CallAnalysisRequest, ClassificationLabel
from app.services.scam_detector import detector_service
from app.db.connection import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
webhook_router = APIRouter(prefix="/webhooks", tags=["Telecommunication & Ingestion Webhooks"])


@webhook_router.post(
    "/twilio/sms",
    response_class=PlainTextResponse,
    summary="Twilio Incoming SMS Webhook",
    description="Receives incoming SMS from Twilio, scans with AI, logs to MySQL, and responds with TwiML."
)
async def twilio_incoming_sms(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: Optional[str] = Form(None)
):
    """
    Twilio Webhook Handler for incoming SMS.
    Returns TwiML: if High Risk Scam, returns a warning or blocks forwarding.
    """
    logger.info(f"Twilio SMS received from {From}: {Body[:50]}...")
    
    analysis = detector_service.analyze_message(
        MessageAnalysisRequest(
            text=Body,
            sender_id=From,
            channel="sms"
        )
    )

    if analysis.classification == ClassificationLabel.HIGH_RISK_SCAM:
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Response>'
            f'<Message>[ScamShield ALERT] High Risk Scam detected from {From}. Score: {analysis.risk_score}/100. Do not reply or click links.</Message>'
            '</Response>'
        )
    else:
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

    return Response(content=twiml, media_type="application/xml")


@webhook_router.post(
    "/twilio/voice-transcription",
    response_class=PlainTextResponse,
    summary="Twilio Call Speech-to-Text Transcription Callback",
    description="Receives transcribed audio from telephone call, identifies vishing, and updates MySQL audit log."
)
async def twilio_voice_transcription(
    From: str = Form(...),
    TranscriptionText: str = Form(...),
    CallSid: Optional[str] = Form(None)
):
    """
    Twilio Webhook Handler for transcribed calls.
    Evaluates vishing vectors and persists incident to MySQL.
    """
    logger.info(f"Twilio Voice Transcription for call {CallSid} from {From}: {TranscriptionText[:50]}...")

    analysis = detector_service.analyze_call(
        CallAnalysisRequest(
            transcript=TranscriptionText,
            caller_number=From
        )
    )

    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Response>'
        f'<!-- ScamShield Vishing Verdict: {analysis.classification.value} (Risk: {analysis.risk_score}%) -->'
        '</Response>'
    )
    return Response(content=twiml, media_type="application/xml")

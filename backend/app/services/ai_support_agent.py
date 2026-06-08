# =======================================================================
# ArtisanConnect Nigeria — ai_support_agent.py (Module 21 Production Core)
# =======================================================================
from pydantic import BaseModel, Field
from datetime import datetime
from app.services.ai_engine import call_ai_agent

class SupportDraftSchema(BaseModel):
    recipient_email: str
    subject: str
    email_body: str
    category: str  # e.g., "BILLING_DISPUTE", "BOOKING_ISSUE", "TECHNICAL"
    priority: str  # e.g., "LOW", "MEDIUM", "HIGH"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

def triage_and_draft_support_email(customer_email: str, customer_name: str, raw_complaint: str) -> SupportDraftSchema:
    """
    Analyzes an incoming complaint, categorizes its priority, and 
    auto-generates a highly contextual response draft using corporate Nigerian flair.
    """
    
    # 1. Instruct the AI engine to act as a Triage and Resolution Officer
    triage_prompt = (
        "You are the Senior Resolution Officer at ArtisanConnect Nigeria. Analyze the user's complaint "
        "and return a JSON block matching this structural format:\n"
        "{\n"
        '  "category": "BILLING_DISPUTE or BOOKING_ISSUE or TECHNICAL",\n'
        '  "priority": "LOW or MEDIUM or HIGH",\n'
        '  "subject_line": "A professional, clear email subject line",\n'
        '  "response_body": "A complete, warm, professional response to the customer addressing their problem directly. Use a courteous, distinctly Nigerian corporate tone (e.g., greeting them respectfully, using clear service-oriented assurance). Keep it thorough but concise."\n'
        "}\n"
        "Do not include any markdown backticks or explanations outside the raw JSON object structure."
    )
    
    user_payload = f"Customer Name: {customer_name}\nComplaint: {raw_complaint}"
    
    # 2. Execute call via baseline core engine
    raw_ai_output = call_ai_agent(triage_prompt, user_payload=user_payload, temperature=0.3)
    
    try:
        # Import json locally to parse the structured response blocks cleanly
        import json
        parsed_data = json.loads(raw_ai_output.strip())
        
        return SupportDraftSchema(
            recipient_email=customer_email,
            subject=parsed_data.get("subject_line", "Re: Support Inquiry — ArtisanConnect"),
            email_body=parsed_data.get("response_body", "Thank you for reaching out. We are reviewing your issue."),
            category=parsed_data.get("category", "TECHNICAL"),
            priority=parsed_data.get("priority", "MEDIUM")
        )
    except Exception:
        # Fallback graceful schema initialization if raw text parsing hits string variant anomalies
        return SupportDraftSchema(
            recipient_email=customer_email,
            subject=f"Re: Support Case Update for {customer_name}",
            email_body=f"Good day {customer_name}. We have received your inquiry: '{raw_complaint}'. Our team is investigating.",
            category="GENERAL",
            priority="LOW"
        )
import os
import random
import string
import time
from dotenv import load_dotenv
import google.generativeai as genai
from database import SessionLocal, Complaint

load_dotenv()

# ---------------------------
# Gemini setup
# ---------------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


# ---------------------------
# Conversation State Helpers
# ---------------------------

def generate_reference_id():
    return "CMP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


COMPLAINT_FLOWS = {
    "internet": [
        "What is your location?",
        "Which internet service provider are you using?",
        "How long has the issue been occurring?",
        "Please briefly describe the problem."
    ],
    "garbage": [
        "What is the location of the issue?",
        "How often is garbage not being collected?",
        "Please describe the issue."
    ],
    "water": [
        "What is the affected location?",
        "Is there leakage or no water supply?",
        "Since when has this issue started?"
    ],
    "electricity": [
        "What is your location?",
        "How long has the power outage been?",
        "Is it affecting the whole area or just your house?"
    ],
    "general": [
        "What is the location?",
        "Please describe the issue."
    ]
}


def detect_complaint_type(text: str) -> str:
    text = text.lower()

    if any(w in text for w in ["internet", "wifi", "router"]):
        return "internet"
    if any(w in text for w in ["garbage", "trash", "waste"]):
        return "garbage"
    if any(w in text for w in ["water", "leak"]):
        return "water"
    if any(w in text for w in ["electricity", "power"]):
        return "electricity"

    return "general"


# ---------------------------
# MAIN PROCESS FUNCTION
# ---------------------------

def process_message(message: str, state: dict):
    time.sleep(0.3)

    state.setdefault("step", "greeting")
    state.setdefault("type", None)
    state.setdefault("answers", {})
    state.setdefault("question_index", 0)

    msg = message.strip()

    # STEP 1 — Greeting
    if state["step"] == "greeting":
        state["step"] = "identify"
        return (
            "👋 Hi! I'm your Civic AI Assistant.\n\n"
            "I can help you report issues related to water, electricity, garbage, roads, and more.\n\n"
            "What problem are you facing today?"
        )

    # STEP 2 — Identify issue type
    if state["step"] == "identify":
        state["type"] = detect_complaint_type(msg)
        state["step"] = "questions"
        state["question_index"] = 0
        state["answers"] = {}

        return f"I understand this is a **{state['type']} issue**. Let me ask you a few questions."

    # STEP 3 — Ask questions
    if state["step"] == "questions":
        questions = COMPLAINT_FLOWS[state["type"]]

        if state["question_index"] > 0:
            prev_q = questions[state["question_index"] - 1]
            state["answers"][prev_q] = msg

        if state["question_index"] < len(questions):
            q = questions[state["question_index"]]
            state["question_index"] += 1
            return q

        # STEP 4 — Save to DB
        ref_id = generate_reference_id()

        db = SessionLocal()
        complaint = Complaint(
            reference_id=ref_id,
            category=state["type"],
            details=str(state["answers"])
        )
        db.add(complaint)
        db.commit()
        db.close()

        summary = "\n".join(
            f"• {k}: {v}" for k, v in state["answers"].items()
        )

        state.clear()
        state["step"] = "greeting"

        return (
            f"✅ Your complaint has been registered successfully!\n\n"
            f"📄 Reference ID: {ref_id}\n"
            f"📌 Category: {state.get('type','N/A')}\n\n"
            f"{summary}\n\n"
            "You can report another issue anytime 😊"
        )

    return "How can I help you?"

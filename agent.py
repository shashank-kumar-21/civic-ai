from phi.agent import Agent # type: ignore
from phi.model.groq import Groq # type: ignore
from phi.tools.duckduckgo import DuckDuckGo # type: ignore
from dotenv import load_dotenv # type: ignore
from database import SessionLocal, Complaint
import random,time
import string
load_dotenv()

conversation_state = {
    "type": None,
    "step": 0,
    "answers": {}
}

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


def reset_conversation():
    conversation_state["type"] = None
    conversation_state["data"] = {}
    conversation_state["step"] = "start"

def save_complaint(ref_id, ctype, location, issue):
    db = SessionLocal()
    complaint = Complaint(
        reference_id=ref_id,
        complaint_type=ctype,
        location=location,
        issue=issue
    )
    db.add(complaint)
    db.commit()
    db.close()

def detect_complaint_type(text):
    text = text.lower()

    if any(x in text for x in ["internet", "wifi", "router"]):
        return "internet"
    if any(x in text for x in ["garbage", "trash", "waste"]):
        return "garbage"
    if any(x in text for x in ["water", "leak"]):
        return "water"
    if any(x in text for x in ["electricity", "power"]):
        return "electricity"

    return "general"


def generate_reference_id():
    return "CMP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def submit_complaint(data: dict={}) -> str:
    return f"Complaint registered successfully: {data}"

def validate(text: str="") -> bool:
    return len(text.strip()) > 5

duckduckgo = DuckDuckGo()

import time
import random
import string

def generate_reference_id():
    return "CMP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def process_message(message: str, state: dict):
    time.sleep(0.3)

    def generate_reference_id():
        return "CMP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    msg = message.strip()

    # Ensure state exists
    state.setdefault("step", "greeting")
    state.setdefault("type", None)
    state.setdefault("answers", {})
    state.setdefault("question_index", 0)

    # STEP 1: Greeting
    if state["step"] == "greeting":
        state["step"] = "identify"
        return (
            "👋 Hi! I'm your Civic AI Assistant.\n\n"
            "I can help you report issues related to water, electricity, garbage, roads, and more.\n\n"
            "What problem are you facing today?"
        )

    # STEP 2: Identify complaint type
    if state["step"] == "identify":
        state["type"] = detect_complaint_type(msg)
        state["step"] = "confirm_type"
        return f"I understand this is a **{state['type']} issue**. Let me ask you a few quick questions."

    # STEP 3: Start questions
    if state["step"] == "confirm_type":
        state["step"] = "questions"
        state["question_index"] = 0
        state["answers"] = {}
        return COMPLAINT_FLOWS[state["type"]][0]

    # STEP 4: Collect answers
    if state["step"] == "questions":
        questions = COMPLAINT_FLOWS[state["type"]]
        idx = state["question_index"]

        state["answers"][questions[idx]] = msg
        state["question_index"] += 1

        if state["question_index"] < len(questions):
            return questions[state["question_index"]]

        # ✅ Save complaint to DB
        ref_id = generate_reference_id()

        db = SessionLocal()
        complaint = Complaint(
            reference_id=ref_id,
            category=state["type"],
            location=state["answers"].get("What is the affected location?", "N/A"),
            details=str(state["answers"])
        )
        db.add(complaint)
        db.commit()
        db.close()

        summary = "\n".join(
            f"• {q}: {a}" for q, a in state["answers"].items()
        )

        response = (
            f"✅ Your complaint has been registered successfully!\n\n"
            f"📄 Reference ID: {ref_id}\n"
            f"📌 Category: {state['type']}\n"
            f"{summary}\n\n"
            "You can report another issue anytime 😊"
        )

        # Reset session
        state.clear()
        state["step"] = "greeting"

        return response

    return "How can I assist you today?"



agent = Agent(
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    tools=[
        duckduckgo,
    ],
    instructions="""

You are a civic complaint assistant.

RULES:
- Ask ONLY what is strictly required at each step.
- Ask ONE question at a time.
- Do NOT repeat previously provided information.
- Do NOT explain what you are doing.
- Do NOT use long paragraphs.
- Keep responses short and clear.

FLOW:
1. Identify the issue type.
2. Collect missing required fields one by one.
3. Once all required data is collected, confirm and submit the complaint.
4. Respond politely and concisely.

EXAMPLE STYLE:
"Please tell me your ISP."
"Thanks. What city are you in?"
"Your complaint has been registered."
""",
    show_tool_calls=False,
    markdown=False,
)


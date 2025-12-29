from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
load_dotenv()

# ---- Example tools ----

def classify_complaint(text: str) -> str:
    if not text:
        return "Unknown"
    if "internet" in text.lower():
        return "Technical"
    elif "bill" in text.lower():
        return "Billing"
    return "General"


def submit_complaint(data: dict={}) -> str:
    return f"Complaint registered successfully: {data}"


def validate(text: str="") -> bool:
    return len(text.strip()) > 5

duckduckgo = DuckDuckGo()


agent = Agent(
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    tools=[
        classify_complaint,
        submit_complaint,
        validate,
        duckduckgo,
    ],
    instructions="""
    You are a complaint registration assistant.

    RULES:
    - Do NOT call tools until all required information is collected.
    - Ask follow-up questions when information is missing.
    - Only submit complaints when ready.
    """,
    show_tool_calls=False,
    markdown=True,
)

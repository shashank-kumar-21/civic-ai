from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from agent import process_message
from database import init_db

# Initialize DB
init_db()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key"  # change in prod
)


@app.get("/")
async def home(request: Request):
    # Initialize session storage
    if "messages" not in request.session:
        request.session["messages"] = []

    if "conversation" not in request.session:
        request.session["conversation"] = {
            "step": "greeting",
            "type": None,
            "answers": {},
            "question_index": 0,
        }

    # Show greeting only once
    if not request.session["messages"]:
        greeting = process_message("", request.session["conversation"])
        request.session["messages"].append(("assistant", greeting))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "messages": request.session["messages"],
        },
    )


@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    user_message = form.get("message")

    if not user_message:
        return RedirectResponse("/", status_code=303)

    # Ensure session exists
    if "conversation" not in request.session:
        request.session["conversation"] = {
            "step": "greeting",
            "type": None,
            "answers": {},
            "question_index": 0,
        }

    # Add user message
    request.session["messages"].append(("user", user_message))

    # Get bot response
    response = process_message(user_message, request.session["conversation"])

    # Add assistant response
    request.session["messages"].append(("assistant", response))

    return RedirectResponse("/", status_code=303)


@app.post("/reset")
async def reset(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

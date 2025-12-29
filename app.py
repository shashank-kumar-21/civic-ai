from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from agent import agent

app = FastAPI()
templates = Jinja2Templates(directory="templates")

conversation_history = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "messages": conversation_history}
    )

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    try:
        form = await request.form()
        user_message = form.get("message", "").strip()

        if not user_message:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "messages": conversation_history}
            )

        conversation_history.append(("user", user_message))

        result = agent.run(user_message)
        reply = result.content if result else "Sorry, something went wrong."

        conversation_history.append(("assistant", reply))

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "messages": conversation_history}
        )

    except Exception as e:
        return HTMLResponse(f"<h3>Error:</h3><pre>{str(e)}</pre>", status_code=500)

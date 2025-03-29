from fastapi import FastAPI, Request
from chat import chat_with_openai
from models import create_tables

app = FastAPI()

@app.on_event("startup")
async def startup():
    create_tables()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    response = await chat_with_openai(user_message)
    return {"response": response}

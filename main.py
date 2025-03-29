from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from chat import chat_with_openai
from models import create_tables

app = FastAPI()

# Připojení složky static/
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    create_tables()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    response = await chat_with_openai(user_message)
    return {"response": response}

@app.get("/chat-widget", response_class=HTMLResponse)
async def chat_widget():
    return """
    <html>
    <head><style>body{margin:0;font-family:sans-serif}</style></head>
    <body>
      <div style="padding:10px;background:black;color:white;">Elektra 💬</div>
      <div id="chat" style="padding:10px;height:360px;overflow:auto;"></div>
      <div style="padding:10px;">
        <input id="msg" placeholder="Napiš dotaz..." style="width:70%;" />
        <button onclick="send()">Odeslat</button>
      </div>
      <script>
        async function send() {
          const msg = document.getElementById('msg').value;
          const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
          });
          const data = await res.json();
          document.getElementById('chat').innerHTML += "<div><b>Ty:</b> " + msg + "</div>";
          document.getElementById('chat').innerHTML += "<div><b>Elektra:</b> " + data.response + "</div>";
          document.getElementById('msg').value = '';
        }
      </script>
    </body>
    </html>
    """

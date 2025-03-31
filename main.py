from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from chat import chat_with_openai
from models import create_tables

app = FastAPI()

# Připojení složky se statickými soubory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    create_tables()

@app.post("/chat")
async def chat_endpoint(request: Request):
    # 🔒 Ochrana proti zneužití (volitelně odkomentuj)
    # referer = request.headers.get("referer", "")
    # if not referer.startswith("https://www.express-servis.cz"):
    #     raise HTTPException(status_code=403, detail="Přístup odepřen")

    try:
        data = await request.json()
        user_message = data.get("message", "")
        response = chat_with_openai(user_message)
        return {"response": response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/chat-widget", response_class=HTMLResponse)
async def chat_widget():
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <title>Elektra Chat</title>
      <style>
        body {
          margin: 0;
          font-family: sans-serif;
          background: #f9f9f9;
        }

        #chat-container {
          display: flex;
          flex-direction: column;
          width: 100%;
          height: 100vh;
          max-height: 100vh;
        }

        #chat-header {
          background: #000;
          color: white;
          padding: 12px 16px;
          font-weight: bold;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        #chat-close {
          cursor: pointer;
          font-size: 18px;
          padding: 0 8px;
        }

        #chat-messages {
          flex: 1;
          padding: 12px;
          overflow-y: auto;
          background: white;
          animation: fadeIn 0.5s ease-in;
          font-size: 14px;
        }

        #chat-input-area {
          padding: 10px;
          border-top: 1px solid #eee;
          display: flex;
          gap: 5px;
        }

        #chat-input {
          flex: 1;
          padding: 8px;
          border-radius: 8px;
          border: 1px solid #ccc;
          font-size: 14px;
        }

        #chat-send {
          padding: 8px 12px;
          background: #000;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .msg-bot {
          color: #000;
          margin: 6px 0;
        }

        .msg-user {
          color: #444;
          font-weight: bold;
          margin: 6px 0;
        }
      </style>
    </head>
    <body>
      <div id="chat-container">
        <div id="chat-header">
          Elektra 💬
          <span id="chat-close" onclick="window.close()">×</span>
        </div>
        <div id="chat-messages">
          <div class="msg-bot"><strong>Elektra:</strong> Ahoj! S čím ti mohu pomoci?</div>
        </div>
        <div id="chat-input-area">
          <input id="chat-input" type="text" placeholder="Napiš dotaz..." />
          <button id="chat-send">Odeslat</button>
        </div>
      </div>

      <script>
        async function sendChatMessage() {
          const input = document.getElementById("chat-input");
          const chat = document.getElementById("chat-messages");
          const message = input.value.trim();
          if (!message) return;

          chat.innerHTML += `<div class="msg-user"><strong>Ty:</strong> ${message}</div>`;
          input.value = "";

          try {
            const res = await fetch("https://elektra-chatbot.onrender.com/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message })
            });
            const data = await res.json();
            if (data.response) {
              chat.innerHTML += `<div class="msg-bot"><strong>Elektra:</strong> ${data.response}</div>`;
            } else {
              chat.innerHTML += `<div class="msg-bot" style="color:red;"><strong>Chyba:</strong> ${data.error}</div>`;
            }
          } catch (err) {
            chat.innerHTML += `<div class="msg-bot" style="color:red;"><strong>Chyba připojení:</strong> ${err.message}</div>`;
          }

          chat.scrollTop = chat.scrollHeight;
        }

        document.getElementById("chat-send").addEventListener("click", sendChatMessage);
        document.getElementById("chat-input").addEventListener("keypress", function (e) {
          if (e.key === "Enter") sendChatMessage();
        });
      </script>
    </body>
    </html>
    """

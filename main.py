from fastapi import FastAPI, Request
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
    try:
        data = await request.json()
        user_message = data.get("message", "")
        response = chat_with_openai(user_message)
        return {"response": response}
    except Exception as e:
        # V případě chyby vrátíme chybovou zprávu jako JSON
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/chat-widget", response_class=HTMLResponse)
async def chat_widget():
    return """
    <html>
    <head>
      <style>body{margin:0;font-family:sans-serif}</style>
      <script>
        async function send() {
          console.log("send function triggered");
          const msg = document.getElementById('msg').value;
          try {
            const res = await fetch("https://elektra-chatbot.onrender.com/chat", {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            document.getElementById('chat').innerHTML += "<div><b>Ty:</b> " + msg + "</div>";
            if(data.response) {
              document.getElementById('chat').innerHTML += "<div><b>Elektra:</b> " + data.response + "</div>";
            } else {
              document.getElementById('chat').innerHTML += "<div style='color:red;'><b>Error:</b> " + data.error + "</div>";
            }
            document.getElementById('msg').value = '';
          } catch (error) {
            console.error("Error in send function:", error);
          }
        }
      </script>
    </head>
    <body>
      <div style="padding:10px;background:black;color:white;">Elektra 💬</div>
      <div id="chat" style="padding:10px;height:360px;overflow:auto;"></div>
      <div style="padding:10px;">
        <input id="msg" placeholder="Napiš dotaz..." style="width:70%;" />
        <button onclick="send()">Odeslat</button>
      </div>
    </body>
    </html>
    """

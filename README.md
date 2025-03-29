# Elektra Chatbot

Přátelský GPT chatbot pro vyhledávání produktů a pomoc zákazníkům.

## 🚀 Spuštění na Renderu

1. Připoj repozitář
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Nastav environment proměnné:
   - `OPENAI_API_KEY`
   - `DATABASE_URL`

## 💬 Chatovací widget

Vlož na web:

```html
<script src="https://tvuj-server.onrender.com/static/widget.js" async></script>

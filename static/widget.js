document.addEventListener("DOMContentLoaded", function () {
  // celý původní kód
  (function () {
    // Vytvoření bubliny
    const bubble = document.createElement("div");
    bubble.id = "chat-bubble";
    bubble.style.position = "fixed";
    bubble.style.bottom = "20px";
    bubble.style.right = "20px";
    bubble.style.background = "white";
    bubble.style.borderRadius = "50px";
    bubble.style.padding = "10px 15px";
    bubble.style.boxShadow = "0 0 10px rgba(0,0,0,0.2)";
    bubble.style.display = "flex";
    bubble.style.alignItems = "center";
    bubble.style.gap = "10px";
    bubble.style.cursor = "pointer";
    bubble.style.zIndex = "9999";

    const img = document.createElement("img");
    img.src = "https://www.express-servis.cz/static/elektra.png";
    img.alt = "Elektra";
    img.style.width = "32px";
    img.style.height = "32px";
    img.style.borderRadius = "50%";

    const text = document.createElement("span");
    text.innerText = "Zeptejte se mě!";
    text.style.fontWeight = "bold";
    text.style.color = "#333";

    bubble.appendChild(img);
    bubble.appendChild(text);

    // Chatovací okno
    const box = document.createElement("div");
    box.id = "chat-box";
    box.style.position = "fixed";
    box.style.bottom = "80px";
    box.style.right = "20px";
    box.style.width = "350px";
    box.style.height = "450px";
    box.style.background = "white";
    box.style.borderRadius = "20px";
    box.style.boxShadow = "0 0 15px rgba(0,0,0,0.3)";
    box.style.display = "none";
    box.style.flexDirection = "column";
    box.style.zIndex = "9999";
    box.style.overflow = "hidden";

    box.innerHTML = `
      <div style="background:#000;color:white;padding:10px 15px;font-weight:bold;">Elektra 💬</div>
      <div id="chat-messages" style="flex:1;padding:10px;overflow-y:auto;font-size:14px;"></div>
      <div style="padding:10px;border-top:1px solid #eee;display:flex;gap:5px;">
        <input id="chat-input" type="text" placeholder="Napiš dotaz..." style="flex:1;padding:8px;border-radius:8px;border:1px solid #ccc;font-size:14px;">
        <button id="chat-send" style="padding:8px 12px;background:#000;color:white;border:none;border-radius:8px;cursor:pointer;">Odeslat</button>
      </div>
    `;

    // Odesílání zprávy
    async function sendChatMessage() {
      const input = document.getElementById("chat-input");
      const chat = document.getElementById("chat-messages");
      const message = input.value.trim();
      if (!message) return;

      chat.innerHTML += `<div><strong>Ty:</strong> ${message}</div>`;
      input.value = "";

      try {
        const res = await fetch("https://elektra-chatbot.onrender.com/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message })
        });
        const data = await res.json();
        if (data.response) {
          chat.innerHTML += `<div><strong>Elektra:</strong> ${data.response}</div>`;
        } else {
          chat.innerHTML += `<div style='color:red;'><strong>Chyba:</strong> ${data.error}</div>`;
        }
      } catch (err) {
        chat.innerHTML += `<div style='color:red;'><strong>Chyba připojení:</strong> ${err.message}</div>`;
      }

      chat.scrollTop = chat.scrollHeight;
    }

    // Události
    bubble.addEventListener("click", () => {
      box.style.display = box.style.display === "none" ? "flex" : "none";
    });

    document.body.appendChild(bubble);
    document.body.appendChild(box);

    document.addEventListener("click", (e) => {
      if (e.target && e.target.id === "chat-send") {
        sendChatMessage();
      }
    });

    document.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && document.activeElement.id === "chat-input") {
        sendChatMessage();
      }
    });
  })();
});

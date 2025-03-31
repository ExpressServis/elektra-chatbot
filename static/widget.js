(function () {
  document.addEventListener("DOMContentLoaded", () => {
    // Bublina
    const bubble = document.createElement("div");
    bubble.id = "chat-bubble";
    bubble.style = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: white;
      border-radius: 50px;
      padding: 10px 15px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      z-index: 9999;
      font-family: sans-serif;
    `;

    const img = document.createElement("img");
    img.src = "https://www.express-servis.cz/static/elektra-icon.png";
    img.alt = "Elektra";
    img.style = "width: 32px; height: 32px; border-radius: 50%;";

    const text = document.createElement("span");
    text.innerText = "Zeptejte se mě!";
    text.style = "font-weight: bold; color: #333;";

    bubble.appendChild(img);
    bubble.appendChild(text);
    document.body.appendChild(bubble);

    // Chat box
    const box = document.createElement("div");
    box.id = "chat-box";
    box.style = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      width: 350px;
      height: 460px;
      background: white;
      border-radius: 20px;
      box-shadow: 0 0 15px rgba(0,0,0,0.3);
      display: none;
      flex-direction: column;
      z-index: 9999;
      overflow: hidden;
      animation: fadeIn 0.3s ease;
    `;

    box.innerHTML = `
      <div style="background:#000;color:white;padding:10px 15px;font-weight:bold;display:flex;justify-content:space-between;align-items:center;">
        <span>Elektra 💬</span>
        <span id="chat-close" style="cursor:pointer;font-size:18px;">✖</span>
      </div>
      <div id="chat-messages" style="flex:1;padding:10px;overflow-y:auto;font-size:14px;"></div>
      <div style="padding:10px;border-top:1px solid #eee;display:flex;gap:5px;">
        <input id="chat-input" type="text" placeholder="Napiš dotaz..." style="flex:1;padding:8px;border-radius:8px;border:1px solid #ccc;font-size:14px;">
        <button id="chat-send" style="padding:8px 12px;background:#000;color:white;border:none;border-radius:8px;cursor:pointer;">Odeslat</button>
      </div>
    `;
    document.body.appendChild(box);

    // Chat akce
    bubble.addEventListener("click", () => {
      box.style.display = "flex";
      document.getElementById("chat-messages").innerHTML += `<div><strong>Elektra:</strong> Ahoj! Na co se chceš zeptat? 😊</div>`;
    });

    document.addEventListener("click", (e) => {
      if (e.target.id === "chat-send") sendMessage();
      if (e.target.id === "chat-close") box.style.display = "none";
    });

    document.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && document.activeElement.id === "chat-input") {
        sendMessage();
      }
    });

    async function sendMessage() {
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

    // Animace (CSS vkládáme dynamicky)
    const style = document.createElement("style");
    style.innerHTML = `
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    `;
    document.head.appendChild(style);
  });
})();

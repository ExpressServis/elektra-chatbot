(function () {
  // Vytvoříme bublinu
  const bubble = document.createElement("div");
  bubble.style.position = "fixed";
  bubble.style.bottom = "20px";
  bubble.style.right = "20px";
  bubble.style.background = "#ffffff";
  bubble.style.border = "1px solid #ccc";
  bubble.style.borderRadius = "32px";
  bubble.style.padding = "10px 15px";
  bubble.style.cursor = "pointer";
  bubble.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
  bubble.style.zIndex = "9998";
  bubble.style.display = "flex";
  bubble.style.alignItems = "center";
  bubble.style.gap = "10px";
  bubble.style.fontFamily = "sans-serif";

  const img = document.createElement("img");
  img.src = "https://www.express-servis.cz/assets/elektra-icon.jpg"; // ← nahraď reálnou cestou k obrázku Elektry
  img.alt = "Elektra";
  img.style.width = "32px";
  img.style.height = "32px";
  img.style.borderRadius = "50%";

  const text = document.createElement("span");
  text.innerText = "Potřebujete poradit? 💬";

  bubble.appendChild(img);
  bubble.appendChild(text);

  // Vytvoříme iframe, ale zatím ho neschováme
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.bottom = "80px";
  iframe.style.right = "20px";
  iframe.style.width = "360px";
  iframe.style.height = "480px";
  iframe.style.border = "none";
  iframe.style.zIndex = "9999";
  iframe.style.display = "none"; // Skryté dokud se neklikne na bublinu
  iframe.src = "https://elektra-chatbot.onrender.com/chat-widget";

  // Po kliknutí na bublinu zobraz iframe
  bubble.addEventListener("click", () => {
    iframe.style.display = iframe.style.display === "none" ? "block" : "none";
  });

  document.body.appendChild(bubble);
  document.body.appendChild(iframe);
})();

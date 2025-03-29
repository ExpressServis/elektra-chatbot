(function () {
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "360px";
  iframe.style.height = "480px";
  iframe.style.border = "none";
  iframe.style.zIndex = "9999";
  iframe.src = "https://elektra-chatbot.onrender.com/chat-widget";
  document.body.appendChild(iframe);
})();

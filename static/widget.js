(function () {
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "320px";
  iframe.style.height = "420px";
  iframe.style.border = "1px solid #ccc";
  iframe.style.borderRadius = "12px";
  iframe.style.zIndex = "9999";
  iframe.srcdoc = `
    <html>
    <body style="margin:0;font-family:sans-serif;">
      <div style="background:#000;color:#fff;padding:10px;">Elektra 💬</div>
      <div style="padding:10px;height:340px;overflow:auto;" id="chatBox"></div>
      <div style="padding:10px;">
        <input id="msg" style="width:70%;" placeholder="Napiš dotaz..." />
        <button onclick="send()">Odeslat</button>
      </div>
      <script>
        async function send() {
          const msg = document.getElementById("msg").value;
          const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
          });
          const data = await res.json();
          document.getElementById("chatBox").innerHTML += "<div><b>Ty:</b> " + msg + "</div>";
          document.getElementById("chatBox").innerHTML += "<div><b>Elektra:</b> " + data.response + "</div>";
          document.getElementById("msg").value = "";
        }
      </script>
    </body>
    </html>
  `;
  document.body.appendChild(iframe);
})();

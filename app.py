import json
import os
import re
import random
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai

key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=key) if key else None
chat = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "system_instruction": (
            "You are Xeno_Ai 🤖⚡, created by Xeno_Ava. You are a futuristic, highly intelligent AI with real-time text and AI image generation capabilities.\n"
            "IMAGE GENERATION CAPABILITY:\n"
            "You CAN generate images! Whenever the user asks to generate, create, draw, make, or see an image/picture/photo/wallpaper:\n"
            "1. Translate and expand their idea into an ultra-detailed, photorealistic English visual prompt.\n"
            "2. Render the image using this exact markdown syntax:\n"
            "![AI Art](https://image.pollinations.ai/prompt/{URL_ENCODED_ENGLISH_PROMPT}?width=1024&height=1024&nologo=true)\n"
            "3. Ensure the prompt inside the URL has no raw spaces (use %20 or dashes).\n"
            "4. Add a short, punchy caption for the artwork.\n"
            "Never say you cannot create images. Always use the markdown syntax above to generate them."
        )
    }
) if client else None

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Xeno_Ai 🤖⚡</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #0c0d10; color: #e3e3e3; display: flex; flex-direction: column; height: 100vh; }
    header { padding: 16px 24px; font-size: 1.15rem; font-weight: 700; color: #70a5ff; border-bottom: 1px solid #1c1f26; display: flex; align-items: center; justify-content: space-between; background-color: #12141a; }
    .brand { display: flex; align-items: center; gap: 10px; }
    .brand-tag { font-size: 0.75rem; background: rgba(112, 165, 255, 0.15); color: #70a5ff; padding: 3px 8px; border-radius: 12px; font-weight: 600; }
    #chat-box { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; max-width: 860px; width: 100%; margin: 0 auto; }
    .msg { display: flex; gap: 12px; max-width: 85%; }
    .msg.user { align-self: flex-end; flex-direction: row-reverse; }
    .msg.ai { align-self: flex-start; }
    .bubble { padding: 14px 18px; border-radius: 18px; font-size: 0.95rem; line-height: 1.6; word-wrap: break-word; }
    .user .bubble { background: linear-gradient(135deg, #1d4ed8, #2563eb); color: #ffffff; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(29, 78, 216, 0.25); }
    .ai .bubble { background-color: #171920; color: #e3e3e3; border-bottom-left-radius: 4px; border: 1px solid #262935; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25); }
    .bubble img { max-width: 100%; border-radius: 12px; margin-top: 12px; display: block; border: 1px solid #2e3444; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
    .avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85rem; flex-shrink: 0; }
    .user .avatar { background-color: #1e293b; color: #93c5fd; border: 1px solid #334155; }
    .ai .avatar { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; box-shadow: 0 0 12px rgba(168, 85, 247, 0.45); }
    pre { background: #07080a; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; border: 1px solid #222633; }
    code { font-family: Consolas, monospace; font-size: 0.88rem; color: #a5b4fc; }
    #input-container { padding: 20px; display: flex; justify-content: center; background-color: #0c0d10; border-top: 1px solid #181b22; }
    .input-box { display: flex; background-color: #171920; border-radius: 28px; padding: 6px 14px; width: 100%; max-width: 860px; border: 1px solid #2a2f3d; align-items: center; }
    .input-box:focus-within { border-color: #70a5ff; box-shadow: 0 0 10px rgba(112, 165, 255, 0.15); }
    input { flex: 1; background: transparent; border: none; outline: none; color: #ffffff; font-size: 1rem; padding: 10px; }
    button { background: linear-gradient(135deg, #70a5ff, #818cf8); color: #050b18; border: none; padding: 9px 22px; border-radius: 20px; cursor: pointer; font-weight: 700; font-size: 0.9rem; }
    button:hover { opacity: 0.95; }
    button:disabled { background: #374151; color: #9ca3af; cursor: not-allowed; }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span>Xeno_Ai 🤖⚡</span>
      <span class="brand-tag">Online</span>
    </div>
    <span style="font-size: 0.8rem; color: #64748b;">Powered by Xeno_Ava Engine</span>
  </header>
  
  <div id="chat-box">
    <div class="msg ai">
      <div class="avatar">⚡</div>
      <div class="bubble">
        <strong>Xeno_Ai 🤖⚡</strong> is online!<br>
        Ask me anything or ask me to generate images.
      </div>
    </div>
  </div>

  <div id="input-container">
    <div class="input-box">
      <input type="text" id="prompt" placeholder="Message Xeno_Ai or ask to generate an image..." autocomplete="off" />
      <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>
  </div>

  <script>
    const chatBox = document.getElementById("chat-box");
    const input = document.getElementById("prompt");
    const btn = document.getElementById("send-btn");

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;

      appendMsg("user", text);
      input.value = "";
      btn.disabled = true;

      const aiBubble = appendMsg("ai", "Xeno_Ai is thinking...");

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        aiBubble.innerHTML = marked.parse(data.reply);
      } catch (err) {
        aiBubble.innerText = "Error connecting to Xeno_Ai.";
      } finally {
        btn.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
        input.focus();
      }
    }

    function appendMsg(sender, text) {
      const msgDiv = document.createElement("div");
      msgDiv.className = `msg ${sender}`;
      
      const avatar = document.createElement("div");
      avatar.className = "avatar";
      avatar.innerText = sender === "user" ? "ME" : "⚡";

      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.innerText = text;

      msgDiv.appendChild(avatar);
      msgDiv.appendChild(bubble);
      chatBox.appendChild(msgDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
      return bubble;
    }
  </script>
</body>
</html>"""

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            user_msg = data.get("message", "")

            try:
                if not chat:
                    reply = "Error: API key missing."
                else:
                    response = chat.send_message(user_msg)
                    reply = response.text

                    reply = re.sub(
                        r'(https://image\.pollinations\.ai/prompt/)([^)\s]+(?:\s+[^)\s]+)*)',
                        lambda m: m.group(1) + urllib.parse.quote(m.group(2).replace('https://image.pollinations.ai/prompt/', '')),
                        reply
                    )

                    img_triggers = ['image', 'photo', 'picture', 'draw', 'tasveer', 'pic', 'wallpaper', 'generate image']
                    if any(t in user_msg.lower() for t in img_triggers) and "image.pollinations.ai" not in reply:
                        encoded = urllib.parse.quote(user_msg.strip())
                        seed = random.randint(100, 999999)
                        reply += f"\n\n![Generated Art](https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={seed})"

            except Exception as e:
                reply = f"Error: {e}"

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

port = int(os.environ.get("PORT", 5000))
server = HTTPServer(("0.0.0.0", port), ChatHandler)
print(f"Xeno_Ai server running on port {port}...")
server.serve_forever()

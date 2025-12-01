from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# --- NOTA: LAS CLAVES SON VARIABLES DE ENTORNO EN RENDER ---
# El código las busca de forma segura en las variables del servidor.

def cerebro(texto):
    texto = texto.lower()
    
    # Obtener clave de Gemini de forma segura desde el servidor
    API_KEY_GEMINI = os.environ.get("GEMINI_API_KEY")
    
    # 1. Respuestas rápidas de inicio
    if "hola" in texto: return "Sistemas en línea. ¿En qué puedo ayudarle?"
    if "quién eres" in texto: return "Soy J.A.R.V.I.S., un asistente de IA en la nube 24/7."
    
    # 2. Gemini (Conversación)
    try:
        genai.configure(api_key=API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Usamos una instancia de chat simple para evitar errores de historial en el servidor
        response = model.generate_content(texto) 
        return response.text
    except Exception as e:
        # Esto indica que la llave GEMINI es el problema final si llegamos aquí
        return "Error de conexión neuronal. No pude consultar la base de datos."

# --- INTERFAZ MÓVIL (PWA) ---
HTML_APP = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>JARVIS MOBILE</title>
    <link rel="apple-touch-icon" href="https://img.icons8.com/color/480/iron-man.png">
    <meta name="theme-color" content="#000000">
    <style>
        body { background-color: #050505; color: #00ffff; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        .reactor { width: 120px; height: 120px; border: 8px solid #00ffff; border-radius: 50%; margin: 20px auto; box-shadow: 0 0 30px #00ffff; animation: pulse 3s infinite ease-in-out; }
        @keyframes pulse { 0% { opacity: 0.8; transform: scale(0.95); } 50% { opacity: 1; transform: scale(1.05); } 100% { opacity: 0.8; transform: scale(0.95); } }
        #chat { flex: 2; overflow-y: auto; padding: 20px; text-align: left; background: #0a0a0a; display: flex; flex-direction: column; }
        .msg { margin-bottom: 10px; padding: 10px; border-radius: 10px; max-width: 80%; }
        .jarvis { background: rgba(0, 255, 255, 0.1); color: #00ffff; align-self: flex-start; border-left: 3px solid #00ffff;}
        .user { background: #222; color: #fff; margin-left: auto; text-align: right; }
        .controls { padding: 20px; display: flex; gap: 10px; background: #000; border-top: 1px solid #333; }
        input { flex: 1; padding: 15px; border-radius: 30px; border: 1px solid #333; background: #111; color: white; outline: none; }
        button { background: #00ffff; border: none; width: 50px; height: 50px; border-radius: 50%; margin-left: 10px; font-size: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div style="text-align:center; padding:20px;">
        <div class="reactor"></div>
        <h3>JARVIS CLOUD</h3>
    </div>
    <div id="chat"></div>
    <div class="controls">
        <button class="mic" onclick="toggleVoice()" style="background:#222; color:#00ffff;">🎙️</button>
        <input type="text" id="userInput" placeholder="Escriba orden..." onkeypress="if(event.key==='Enter') sendMsg()">
        <button onclick="sendMsg()" style="background:#00ffff;">➤</button>
    </div>
    <script>
        const reactor = document.getElementById('reactor');
        const chatLog = document.getElementById('chat');
        function speak(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-ES'; 
            window.speechSynthesis.speak(utterance);
        }
        async function sendMsg() {
            const input = document.getElementById('userInput');
            const text = input.value;
            if(!text) return;
            addLog(text, 'user');
            input.value = '';
            reactor.classList.add('thinking');
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({msg: text})
                });
                const data = await res.json();
                reactor.classList.remove('thinking');
                addLog(data.reply, 'jarvis');
                speak(data.reply);
            } catch (e) {
                reactor.classList.remove('thinking');
                addLog("Error de conexión al servidor. (Revisa Render)", 'jarvis');
            }
        }
        function addLog(text, sender) {
            const div = document.createElement('div');
            div.className = 'msg ' + sender;
            div.innerText = text;
            chatLog.appendChild(div);
            chatLog.scrollTop = chatLog.scrollHeight;
        }
        function toggleVoice() { /* Logic for Web Voice API */ }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_APP)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('msg', '')
    respuesta = cerebro(user_msg)
    return jsonify({"reply": respuesta})

if __name__ == '__main__':
    pass

🤖 ChadBot — A Secure Gemini-Powered Desktop Chatbot
ChadBot is a modern Python desktop chatbot app built with Tkinter and CustomTkinter, powered by Google Gemini AI.
It provides a simple yet powerful chat interface, secure API key management, and optional text-to-speech output using pyttsx3.

🚀 Features
🧠 Chat with Gemini AI — Choose between multiple Gemini models (gemini-2.5-flash, gemini-2.5-pro, etc.)
🔐 Secure API Key Storage — Uses keyring for safe, local credential storage (no plain text keys!)
💬 Modern GUI — Built with CustomTkinter for a sleek, dark-themed user interface
🗣️ Text-to-Speech — Listen to the bot’s responses using pyttsx3
🧾 Chat History — Saves your conversations to a data.txt file and displays them in a dedicated history window
🔄 Switch Models on the Fly — Quickly change AI models from a dropdown menu
🧰 Keyboard Shortcuts —
⌘ + P → Speak response
⌘ + S → Stop speaking

🧩 Tech Stack
Component	Library / Tool
1) GUI	tkinter, customtkinter
2) AI Backend	google-generativeai (Gemini)
3) Speech	pyttsx3
4) Security	keyring
5) Threading	threading
6) Platform	Python 3.10+ (cross-platform)

🛠️ Installation
1. Clone the Repository
"git clone https://github.com/your-username/ChadBot.git
cd ChadBot"

3. Create a Virtual Environment (optional but recommended)\n
"python -m venv venv\n
source venv/bin/activate      # On macOS/Linu\n
venv\Scripts\activate         # On Windows"

4. Install Dependencies
"pip install -r requirements.txt"

🔑 Setting Up the API Key
When you first launch the app, you’ll see a Login Window asking for your Gemini API key.
Get your API key from Google AI Studio.
Paste it into the field and click Enter.
ChadBot will store it securely using your system’s keyring (no need to re-enter it again).
If you ever want to reset your key:
Go to Menu → Change API key → Change API key

▶️ Running the App
Simply run the main script:
"python main.py"

💬 Usage
Type a message in the input box and press Enter or click Send
Use Speak to hear the bot’s response aloud
Use Stop to end playback
View your chat logs anytime via History → Show history

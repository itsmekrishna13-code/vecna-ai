# vecna-ai
Jarvis-style AI Desktop Assistant built for college event TechXpression | Voice + PC Control + Web Search + Weather

# 🤖 Vecna AI — Jarvis-Style Desktop Assistant

A voice-controlled AI desktop assistant built for **TechXpression 2026** college event. Vecna can control your PC, search the web, fetch weather, open files, and respond intelligently using multiple LLM backends.

---

## ⚡ Features

- 🎙️ Voice interaction via **LiveKit**
- 🧠 Multi-model AI routing (Gemini, Groq, OpenRouter)
- 🔍 Google Search integration
- 🌤️ Real-time weather fetching
- 🖱️ Keyboard & Mouse control
- 🪟 Window management
- 📂 File opener via voice command
- 🔀 Smart AI router — routes queries to best model

---

## 🛠️ Tech Stack

- **Language:** Python
- **AI Models:** Google Gemini, Groq, OpenRouter
- **Voice:** LiveKit
- **Search:** Google Custom Search API
- **Weather:** OpenWeather API
- **PC Control:** PyAutoGUI / Keyboard libraries

---

## 📁 Project Structure

```
vecna-ai/
│
├── agent.py                 # Main AI agent
├── ai_router.py             # Routes queries to best LLM
├── server.py                # Backend server
├── keyboard_mouse_CTRL.py   # PC keyboard & mouse control
├── Vecna_window_CTRL.py     # Window management
├── vecna_file_opner.py      # File opener
├── vecna_get_whether.py     # Weather API integration
├── Vecna_google_search.py   # Google Search integration
├── Vecna_prompts.py         # AI system prompts
├── requirements.txt         # Dependencies
├── .gitignore               # Ignored files
└── README.md
```

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/itsmekrishna13-code/vecna-ai.git
cd vecna-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in root folder:
```
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=your_url
GOOGLE_API_KEY=your_key
GOOGLE_SEARCH_API_KEY=your_key
SEARCH_ENGINE_ID=your_id
OPENWEATHER_API_KEY=your_key
OPENROUTER_API_KEY=your_key
GROQ_API_KEY=your_key
```

### 5. Run Vecna
```bash
python agent.py
```

---

## ⚠️ Important

- Never push your `.env` file — API keys must stay private
- `.env` is already added to `.gitignore`

---

## 🎓 Built For

**TechXpression 2026** — College Tech Event  
**BK Birla College**, kalyan

---


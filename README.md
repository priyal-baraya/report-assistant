# Gemini Report Assistant 🧠📊

An AI-powered chatbot built with Flask and Google Gemini to summarize internal reports (Trip, Target, Task) using natural language queries.

## Features
- 🌐 Natural language interface
- 📈 Integrates with Imprint internal APIs
- 🧠 Uses Google Gemini (1.5 & 2.0 Flash) for LLM responses
- 🧾 Summarizes trip logs, employee targets, and task performance

## Tech Stack
- Python, Flask
- HTML, Bootstrap, JavaScript
- Google Gemini API
- Imprint Internal APIs

## Setup Instructions
```bash
git clone https://github.com/YOUR_USERNAME/gemini-report-assistant.git
cd gemini-report-assistant
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # update your keys here
python app.py

🤖 BitJurisBot

Automated educational Telegram bot for crypto, blockchain, and legal awareness.

BitJurisBot is a Telegram bot designed to automatically generate and publish educational content about cryptocurrencies, blockchain technology, and digital legal awareness.
It is built for LegalTech and fintech communities that want consistent, responsible, and professional content — without manual effort.

✨ Features

☀️ Daily Morning Content

Educational crypto curiosities
Short, accessible, non-financial advice

🌙 Daily Evening Insights

Clear explanations about crypto, blockchain, and digital security
Institutional tone aligned with LegalTech standards

📊 Weekly Summary (Fridays)
Automated recap of the main topics covered during the week

🧠 AI-Powered Content
Content generated dynamically using OpenAI models
Low repetition with weekly themes

🏷️ Institutional CTA
Soft, non-commercial brand references to BitJuris
No financial recommendations

👤 Private Chat Assistant

Users can ask crypto-related questions in private chat
Educational responses only

⚙️ Fully Automated

No manual posting required
Runs continuously via background jobs

🛠️ Tech Stack

Python 3.11+
python-telegram-bot
OpenAI API
SQLite (user management)
Railway / Render (deployment)
Telegram Bot API

📂 Project Structure
├── bot.py              # Main bot logic
├── database.py         # SQLite database setup
├── usadas.txt          # Control of repeated content
├── requirements.txt    # Dependencies
└── README.md

⚙️ Environment Variables

Create the following environment variables:

BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

🚀 How to Run Locally
pip install -r requirements.txt
python bot.py

📌 How It Works

The bot posts automatically to a predefined Telegram group.
Content themes change based on the day of the week.
Morning and night posts follow different editorial formats.
A weekly summary is posted every Friday night.
Private messages trigger AI-based educational responses.

🔐 Content Policy

No financial advice
No investment recommendations
Educational and informational purpose only
Institutional and professional tone

🎯 Use Cases

LegalTech communities
Crypto education groups
Telegram channels focused on blockchain
Institutional branding with low operational cost

📄 License

This project is provided for educational and internal use.
You may adapt it to your own projects, respecting API usage policies.

👤 Author

Developed by Natan Oliveira
Automation • Systems • LegalTech • AI

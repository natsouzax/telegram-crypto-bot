import requests
import os
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

client = OpenAI(api_key=os.getenv("Huggin_API_KEY"))
TIMEZONE = pytz.timezone("America/Sao_Paulo")

import os
TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -1003422643576  # cole aqui o ID real do grupo
CURIOSIDADES_CRIPTO = [
    "O Bitcoin foi criado em 2008 por um autor desconhecido usando o pseudônimo Satoshi Nakamoto.",
    "A oferta máxima de Bitcoin é limitada a 21 milhões de unidades.",
    "A primeira transação comercial com Bitcoin foi a compra de duas pizzas por 10.000 BTC.",
    "Blockchain é um registro público e imutável de transações.",
    "Existem milhares de criptomoedas, mas o Bitcoin ainda domina o mercado."
]
ARQUIVO_USADAS = "usadas.txt"


HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HF_HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

async def responder_com_ia(pergunta: str) -> str:
    payload = {
        "inputs": (
            "Você é um assistente educacional especializado em criptomoedas. "
            "Responda de forma clara, objetiva e profissional, sem fazer "
            "recomendações financeiras.\n\n"
            f"Pergunta: {pergunta}\nResposta:"
        ),
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.5,
            "return_full_text": False
        }
    }

    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        return "⚠️ No momento não consegui responder. Tente novamente."

    data = response.json()

    # A resposta vem como lista
    return data[0]["generated_text"].strip()

    

def carregar_usadas():
    if not os.path.exists(ARQUIVO_USADAS):
        return set()

    with open(ARQUIVO_USADAS, "r", encoding="utf-8") as f:
        return set(l.strip() for l in f.readlines())

def salvar_usada(curiosidade):
    with open(ARQUIVO_USADAS, "a", encoding="utf-8") as f:
        f.write(curiosidade + "\n")


import random
async def curiosidade_diaria(context: ContextTypes.DEFAULT_TYPE):
    usadas = carregar_usadas()

    disponiveis = [
        c for c in CURIOSIDADES_CRIPTO if c not in usadas
    ]

    if not disponiveis:
        open(ARQUIVO_USADAS, "w").close()
        disponiveis = CURIOSIDADES_CRIPTO.copy()

    curiosidade = random.choice(disponiveis)
    salvar_usada(curiosidade)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"📌 Curiosidade cripto do dia:\n\n{curiosidade}"
    )
# /id
async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"ID deste chat: {update.effective_chat.id}"
    )

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute("""
    INSERT OR IGNORE INTO users (telegram_id, name, active)
    VALUES (?, ?, 1)
    """, (user.id, user.first_name))
    conn.commit()

    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n"
        "Você agora receberá nossas promoções exclusivas!\n\n"
        "Para sair, use /stop"
    )

# /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute(
        "UPDATE users SET active = 0 WHERE telegram_id = ?",
        (user.id,)
    )
    conn.commit()

    await update.message.reply_text("Você foi removido da lista 👍")

# /promo — enviar promoção para todos
async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT telegram_id, name FROM users WHERE active = 1"
    )
    users = cursor.fetchall()

    for telegram_id, name in users:
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"🔥 Promoção exclusiva, {name}!\n"
                     "Acesse agora: https://seusite.com"
            )
        except:
            pass

    await update.message.reply_text("Promoção enviada com sucesso 🚀")

# Inicialização
app = ApplicationBuilder().token(TOKEN).build()
app.job_queue.run_daily(
    curiosidade_diaria,
    time=time(hour=7, minute=00, tzinfo=TIMEZONE)
)


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("promo", promo))

app.add_handler(CommandHandler("id", id))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ia))

print("🤖 Bot rodando...")
app.run_polling()








import os
import pytz
import random
from datetime import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from openai import OpenAI
from database import cursor, conn


# ================== CONFIG ==================

TIMEZONE = pytz.timezone("America/Sao_Paulo")
TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -1003534870430  # ID do grupo
ARQUIVO_USADAS = "usadas.txt"

CTAS_SUAVES = [
    "Para entender melhor o cenário jurídico dos criptoativos, acompanhe a BitJuris.",
    "A BitJuris compartilha informações educativas para quem quer entender cripto com responsabilidade.",
    "Conteúdo informativo e educativo, como este, faz parte da proposta da BitJuris.",
    "Acompanhe a BitJuris para aprender mais sobre tecnologia, criptoativos e segurança jurídica.",
]

IDENTIDADE_MARCA = (
    "A BitJuris é uma LegalTech focada em educação, segurança jurídica "
    "e informação responsável sobre criptoativos e blockchain."
)

TEMAS_CRIPTO = [
    "história das criptomoedas",
    "blockchain e tecnologia",
    "segurança e boas práticas",
    "mitos e verdades sobre cripto",
    "curiosidades pouco conhecidas",
    "erros comuns de iniciantes",
    "diferença entre Bitcoin e outras criptos",
    "como funciona uma transação blockchain",
]

CURIOSIDADES_CRIPTO = [
    "O Bitcoin foi criado em 2008 por um autor desconhecido usando o pseudônimo Satoshi Nakamoto.",
    "A oferta máxima de Bitcoin é limitada a 21 milhões de unidades.",
    "A primeira transação comercial com Bitcoin foi a compra de duas pizzas por 10.000 BTC.",
    "Blockchain é um registro público e imutável de transações.",
    "Existem milhares de criptomoedas, mas o Bitcoin ainda domina o mercado."
]

# ================== OPENAI ==================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================== IA (RESPOSTA) ==================

async def responder_com_ia(pergunta: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente educacional especializado em criptomoedas. "
                        "Responda de forma clara, objetiva e profissional, "
                        "sem fazer recomendações financeiras."
                    )
                },
                {"role": "user", "content": pergunta}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "⚠️ Ocorreu um erro ao processar sua pergunta."


async def chat_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # IA apenas no privado
    if update.effective_chat.type != "private":
        return

    await update.message.chat.send_action("typing")
    resposta = await responder_com_ia(update.message.text)
    await update.message.reply_text(resposta)

# ================== IA (CONTEÚDO AUTOMÁTICO) ==================

from datetime import datetime

from datetime import datetime

async def gerar_conteudo_automatico(tipo: str) -> str:
    hoje = datetime.now(TIMEZONE)
    tema = TEMAS_CRIPTO[hoje.weekday() % len(TEMAS_CRIPTO)]
    cta = random.choice(CTAS_SUAVES)

    if tipo == "manha":
        prompt = (
            f"Gere uma curiosidade curta sobre {tema}. "
            "Use linguagem simples, educativa e profissional. "
            "Não faça recomendações financeiras. "
            "Ao final, inclua uma frase curta e sutil de contextualização institucional "
            f"relacionada à marca BitJuris, sem tom comercial.\n\n"
            f"Contexto da marca: {IDENTIDADE_MARCA}\n"

            "Máximo de 3 linhas para o conteúdo principal."
        )
        titulo = "☀️ Curiosidade do dia"
    else:
        prompt = (
            f"Gere um insight curto explicando {tema}. "
            "Use tom claro, profissional e acessível. "
            "Não faça recomendações financeiras. "
            "Finalize com uma frase institucional leve relacionada à BitJuris.\n\n"
            f"Contexto da marca: {IDENTIDADE_MARCA}\n"
            f"Frase institucional sugerida: {cta}\n"
            "Máximo de 3 linhas para o conteúdo principal."
        )
        titulo = "🌙 Insight da noite"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um criador de conteúdo educacional institucional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=140
    )

    return f"{titulo}\n\n{resp.choices[0].message.content.strip()}"



async def post_manha(context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("manha")
    if texto:
        await context.bot.send_message(chat_id=GROUP_ID, text=texto)


async def post_noite(context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("noite")
    if texto:
        await context.bot.send_message(chat_id=GROUP_ID, text=texto)

# ================== CURIOSIDADE FIXA (OPCIONAL) ==================

def carregar_usadas():
    if not os.path.exists(ARQUIVO_USADAS):
        return set()
    with open(ARQUIVO_USADAS, "r", encoding="utf-8") as f:
        return set(l.strip() for l in f.readlines())


def salvar_usada(curiosidade):
    with open(ARQUIVO_USADAS, "a", encoding="utf-8") as f:
        f.write(curiosidade + "\n")


async def curiosidade_diaria(context: ContextTypes.DEFAULT_TYPE):
    usadas = carregar_usadas()
    disponiveis = [c for c in CURIOSIDADES_CRIPTO if c not in usadas]

    if not disponiveis:
        open(ARQUIVO_USADAS, "w").close()
        disponiveis = CURIOSIDADES_CRIPTO.copy()

    curiosidade = random.choice(disponiveis)
    salvar_usada(curiosidade)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"📌 Curiosidade cripto do dia\n\n{curiosidade}"
    )

# ================== COMMANDS ==================

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


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("UPDATE users SET active = 0 WHERE telegram_id = ?", (user.id,))
    conn.commit()
    await update.message.reply_text("Você foi removido da lista 👍")


async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT telegram_id, name FROM users WHERE active = 1")
    users = cursor.fetchall()

    for telegram_id, name in users:
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"🔥 Promoção exclusiva, {name}!\nAcesse agora: https://seusite.com"
            )
        except:
            pass

    await update.message.reply_text("Promoção enviada com sucesso 🚀")


async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID deste chat: {update.effective_chat.id}")

# ================== INIT ==================

app = ApplicationBuilder().token(TOKEN).build()

# Conteúdo automático com IA
app.job_queue.run_daily(
    post_manha,
    time=time(hour=10, minute=45, tzinfo=TIMEZONE)
)

app.job_queue.run_daily(
    post_noite,
    time=time(hour=10, minute=46, tzinfo=TIMEZONE)
)

# Curiosidade fixa (opcional)
app.job_queue.run_daily(
    curiosidade_diaria,
    time=time(hour=7, minute=0, tzinfo=TIMEZONE)
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("promo", promo))
app.add_handler(CommandHandler("id", id))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ia))

print("🤖 Bot rodando...")
app.run_polling()






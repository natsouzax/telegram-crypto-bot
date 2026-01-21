import os
import pytz
import random
from datetime import datetime, time

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
GROUP_ID = -1002921804098  # ID do grupo

ASSINATURA = "—\n📌 Conteúdo educativo • BitJuris"

TEMAS_SEMANA = {
    0: "segurança digital e proteção de criptoativos",
    1: "blockchain e tecnologia",
    2: "mitos e verdades sobre criptomoedas",
    3: "funcionamento do mercado cripto",
    4: "aspectos jurídicos dos criptoativos",
    5: "curiosidades históricas sobre criptomoedas",
    6: "conceitos básicos sobre cripto e blockchain",
}

CTAS_NEUTROS = [
    "Conteúdo educativo faz parte da proposta da BitJuris.",
    "A BitJuris atua com foco em educação e segurança jurídica digital.",
    "Informação responsável é um dos pilares da BitJuris."
]

CTA_SEXTA = [
    "Acompanhe a BitJuris para entender o cenário jurídico dos criptoativos.",
    "A BitJuris conecta tecnologia, criptoativos e segurança jurídica."
]


# ================== OPENAI ==================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================== FUNÇÕES AUXILIARES ==================

def obter_cta(dia_semana: int) -> str:
    if dia_semana == 4:  # sexta
        return random.choice(CTA_SEXTA)
    elif dia_semana < 4:  # seg a qui
        return random.choice(CTAS_NEUTROS)
    else:
        return ""


# ================== IA (CONTEÚDO AUTOMÁTICO) ==================

async def gerar_conteudo_automatico(tipo: str) -> str:
    hoje = datetime.now(TIMEZONE)
    dia = hoje.weekday()

    tema = TEMAS_SEMANA[dia]
    cta = obter_cta(dia)

    if tipo == "manha":
        titulo = "☀️ Curiosidade do dia"
        prompt = (
                f"Gere uma curiosidade educativa relacionada a {tema}."
                "Regras obrigatórias:"
                "- NÃO comece o texto com “Você sabia”, “Uma curiosidade” ou estruturas semelhantes."
                "- Varie a forma de abertura, usando observações, fatos pouco comentados ou consequências práticas."
                "- Linguagem clara, profissional e acessível."
                "- Tom institucional e informativo."
                "- NÃO faça recomendações financeiras ou incentivos a investimento."
                "- O conteúdo deve ensinar algo novo ou pouco percebido."
                "- Máximo de 3 linhas."
                "Evite definições enciclopédicas. Priorize contexto, impacto ou implicações reais do tema."
        )
    else:
        titulo = "🌙 Insight da noite"
        prompt = (
            f"Gere um insight curto explicando {tema}. "
            "Use tom claro, profissional e acessível. "
            "Não faça recomendações financeiras. "
            "Máximo de 3 linhas."
        )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um criador de conteúdo educacional institucional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=140
    )

    conteudo = resp.choices[0].message.content.strip()

    texto = f"{titulo}\n\n{conteudo}"

    if cta:
        texto += f"\n\n{cta}"

    texto += f"\n\n{ASSINATURA}"

    return texto


# ================== POSTS AUTOMÁTICOS ==================

async def post_manha(context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("manha")
    await context.bot.send_message(chat_id=GROUP_ID, text=texto)


async def post_noite(context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("noite")
    await context.bot.send_message(chat_id=GROUP_ID, text=texto)


async def resumo_semanal(context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📊 Resumo da semana — BitJuris\n\n"
        "• Segurança digital e proteção de criptoativos\n"
        "• Blockchain e tecnologia\n"
        "• Mitos e verdades sobre criptomoedas\n"
        "• Funcionamento do mercado cripto\n"
        "• Aspectos jurídicos dos criptoativos\n\n"
        "Conteúdo educativo produzido automaticamente ao longo da semana."
        f"\n\n{ASSINATURA}"
    )

    await context.bot.send_message(chat_id=GROUP_ID, text=texto)


# ================== COMANDOS DE TESTE ==================

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("manha")
    await context.bot.send_message(chat_id=GROUP_ID, text=texto)


async def testen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = await gerar_conteudo_automatico("noite")
    await context.bot.send_message(chat_id=GROUP_ID, text=texto)

async def testar_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await resumo_semanal(context)


# ================== COMANDOS BÁSICOS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute(
        "INSERT OR IGNORE INTO users (telegram_id, name, active) VALUES (?, ?, 1)",
        (user.id, user.first_name)
    )
    conn.commit()

    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n"
        "Este é o BitJurisBot, focado em conteúdo educativo sobre criptoativos e segurança jurídica."
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("UPDATE users SET active = 0 WHERE telegram_id = ?", (user.id,))
    conn.commit()
    await update.message.reply_text("Você foi removido da lista 👍")


async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID deste chat: {update.effective_chat.id}")


# ================== INIT ==================

app = ApplicationBuilder().token(TOKEN).build()

# Agendamentos
app.job_queue.run_daily(post_manha, time=time(hour=7, minute=00, tzinfo=TIMEZONE))
app.job_queue.run_daily(post_noite, time=time(hour=21, minute=30, tzinfo=TIMEZONE))
app.job_queue.run_daily(
    resumo_semanal,
    time=time(hour=19, minute=30, tzinfo=TIMEZONE),
    days=(5,)  # sexta-feira
)

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("id", id))
app.add_handler(CommandHandler("teste", teste))
app.add_handler(CommandHandler("testen", testen))
app.add_handler(CommandHandler("testeresumo", testar_resumo))

print("🤖 BitJurisBot rodando...")
app.run_polling()










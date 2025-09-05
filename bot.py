import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import random

# ---------------------------
# TODAS las preguntas de Akali (Quiz)
# ---------------------------
preguntas = [
    {
        "pregunta": "¿De donde es Akali?",
        "opciones": ["Jonia", "Demacia", "Noxus", "Shurima"],
        "respuesta": "Jonia",
        "imagen": "https://www.breakflip.com/uploads/LoL/Zlatan/carte%20runeterra.jpg"
    },
    {
        "pregunta": "¿Cual es rol de Akali?",
        "opciones": ["Sanador", "Lanzador", "Asesino", "Tanque"],
        "respuesta": "Asesino",
        "imagen": "https://tse4.mm.bing.net/th/id/OIP.9qeXca4-7tGIu7ML7OC7swHaDt"
    },
    {
        "pregunta": "¿Antiguó titulo de Akali?",
        "opciones": ["La Asesina furtiva", "El amor silencioso", "El puño de la sombra", "La Kunai Veloz"],
        "respuesta": "El puño de la sombra",
        "imagen": "https://media.tycsports.com/files/2024/05/09/714618/akali_416x234.webp"
    },
    {
        "pregunta": "¿Qué raza es Akali?",
        "opciones": ["Mutante", "Yordle", "Vastaya", "Humano"],
        "respuesta": "Humano",
        "imagen": "https://i.ytimg.com/vi/EMwPUtsHHE4/maxresdefault.jpg"
    }
]

# ---------------------------
# Imágenes/GIF de feedback
# ---------------------------
IMAGEN_CORRECTO = "https://media.tenor.com/A6RcWds41-gAAAAM/akali-ramen.gif"
IMAGEN_INCORRECTO = "https://media.tenor.com/hoPVaeiHbogAAAAM/star-guardian-akali-falling.gif"
GIF_BIENVENIDA = "https://th.bing.com/th/id/R.e4759fea5fa02860ac473d362a50b5e4?rik=scQITq5jixOEyQ&pid=ImgRaw&r=0"

# Imágenes exclusivas para Misiones
IMAGEN_MISION_CORRECTO = "https://media.tenor.com/H-vQkeKIseEAAAAM/akali-lol.gif"
IMAGEN_MISION_INCORRECTO = "https://pa1.aminoapps.com/7286/8c7f441fcdc451632535630972f370606780237cr1-600-338_hq.gif"

# ---------------------------
# Misiones de Akali
# ---------------------------
misiones = [
    {
        "id": 1,
        "texto": "🌙 Akali recibe la orden de investigar un templo en ruinas. ¿Qué debería hacer primero?",
        "opciones": ["Explorar con sigilo", "Entrar sin pensar", "Esperar refuerzos"],
        "respuesta": "Explorar con sigilo",
        "imagen": "https://preview.free3d.com/img/2020/08/2408258887472908060/fe6ad60f.jpg"
    },
    {
        "id": 2,
        "texto": "⚔️ En su misión, Akali se topa con un guardia solitario. ¿Cómo actúa?",
        "opciones": ["Lo esquiva", "Lo enfrenta de frente", "Lanza un kunai"],
        "respuesta": "Lo esquiva",
        "imagen": "https://static1-es.millenium.gg/articles/9/25/37/9/@/117696-jungle-guardian-orig-2-article_cover_bd-1.jpeg"
    },
    {
        "id": 3,
        "texto": "💀 Akali encuentra un pergamino con símbolos extraños. ¿Qué hace?",
        "opciones": ["Lo estudia", "Lo rompe", "Lo ignora"],
        "respuesta": "Lo estudia",
        "imagen": "https://i.pinimg.com/236x/89/e4/60/89e46012df548c4c33dcfa936e335660.jpg"
    }
]

# ---------------------------
# Estados
# ---------------------------
puntajes = {}
estado_jugadores = {}
# ---------------------------
# /start
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_animation(
        animation=GIF_BIENVENIDA,
        caption="¡Hola! Soy Akali, tu minion verde favorita.\nUsa /jugar para el Quiz o /mision para el modo historia.\nY si quieres apoyar este proyecto usa /donar 💖"
    )

# ---------------------------
# Quiz: enviar pregunta
# ---------------------------
async def enviar_pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE, pregunta):
    botones = [[InlineKeyboardButton(op, callback_data=op)] for op in pregunta["opciones"]]
    teclado = InlineKeyboardMarkup(botones)

    if hasattr(update, "message") and update.message:
        msg = update.message
    elif hasattr(update, "callback_query") and update.callback_query:
        msg = update.callback_query.message
    else:
        return

    if "imagen" in pregunta and pregunta["imagen"]:
        await msg.reply_photo(
            photo=pregunta["imagen"],
            caption=pregunta["pregunta"],
            reply_markup=teclado
        )
    else:
        await msg.reply_text(pregunta["pregunta"], reply_markup=teclado)

# ---------------------------
# /jugar
# ---------------------------
async def jugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    preguntas_restantes = context.user_data.get("preguntas_restantes")

    if not preguntas_restantes:
        preguntas_restantes = preguntas.copy()
        context.user_data["preguntas_restantes"] = preguntas_restantes
        await update.message.reply_text(
            f"🔄 ¡Nueva ronda! Tu puntaje actual es: {puntajes.get(update.effective_user.id,0)}"
        )

    pregunta = random.choice(preguntas_restantes)
    context.user_data["pregunta_actual"] = pregunta
    preguntas_restantes.remove(pregunta)
    context.user_data["preguntas_restantes"] = preguntas_restantes

    await enviar_pregunta(update, context, pregunta)

# ---------------------------
# Quiz: manejar respuesta
# ---------------------------
async def button_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    usuario = query.from_user.id
    pregunta = context.user_data.get("pregunta_actual")

    if not pregunta:
        await query.edit_message_text("Escribe /jugar para recibir una pregunta.")
        return

    if query.data == pregunta["respuesta"]:
        puntajes[usuario] = puntajes.get(usuario, 0) + 1
        mensaje = f"😁 ¡Correcto!\nTu puntaje: {puntajes[usuario]}"
        await query.message.reply_animation(animation=IMAGEN_CORRECTO, caption=mensaje)
    else:
        mensaje = f"😭 Incorrecto. La respuesta correcta era: {pregunta['respuesta']}\nTu puntaje: {puntajes.get(usuario,0)}"
        await query.message.reply_animation(animation=IMAGEN_INCORRECTO, caption=mensaje)

    del context.user_data["pregunta_actual"]

    if not context.user_data.get("preguntas_restantes"):
        await query.message.reply_text(
            f"🏁 ¡Ronda completada! Tu puntaje final es: {puntajes[usuario]}"
        )
        return

    await jugar(update, context)

# ---------------------------
# /puntaje
# ---------------------------
async def puntaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.message.from_user.id
    await update.message.reply_text(f"Tu puntaje actual es: {puntajes.get(usuario,0)}")

# ---------------------------
# Misiones: /mision
# ---------------------------
async def mision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.effective_user.id
    estado_jugadores[usuario] = {"mision": 0, "progreso": 0}
    await mostrar_mision(update.message, context, usuario)

async def mostrar_mision(msg, context, usuario):
    mision_actual = estado_jugadores[usuario]["mision"]

    if mision_actual >= len(misiones):
        await msg.reply_text("🎉 ¡Has completado todas las misiones de Akali!")
        return

    mision = misiones[mision_actual]
    botones = [[InlineKeyboardButton(op, callback_data=f"mision_{op}")] for op in mision["opciones"]]
    teclado = InlineKeyboardMarkup(botones)

    await msg.reply_photo(photo=mision["imagen"], caption=mision["texto"], reply_markup=teclado)

async def button_mision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    usuario = query.from_user.id
    mision_actual = estado_jugadores[usuario]["mision"]
    mision = misiones[mision_actual]

    if query.data == f"mision_{mision['respuesta']}":
        estado_jugadores[usuario]["progreso"] += 1
        await query.message.reply_animation(animation=IMAGEN_MISION_CORRECTO, caption=f"✅ Correcto: {mision['respuesta']}")
        estado_jugadores[usuario]["mision"] += 1

        if estado_jugadores[usuario]["mision"] < len(misiones):
            await mostrar_mision(query.message, context, usuario)
        else:
            await query.message.reply_text(
                f"🏆 ¡Aventura completada!\nProgreso: {estado_jugadores[usuario]['progreso']}/{len(misiones)}"
            )
    else:
        await query.message.reply_animation(animation=IMAGEN_MISION_INCORRECTO, caption=f"❌ Incorrecto. La respuesta correcta era: {mision['respuesta']}")
        estado_jugadores[usuario] = {"mision": 0, "progreso": 0}  # Reinicia la misión
        await query.message.reply_text("💀 Has fallado la misión. Usa /mision para intentarlo de nuevo.")

# ---------------------------
# /donar
# ---------------------------
async def donar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = [
        [InlineKeyboardButton("💳 Donar por PayPal", url="https://www.paypal.com/paypalme/esteban4556")]
    ]
    teclado = InlineKeyboardMarkup(botones)

    await update.message.reply_text(
        "✨ ¡Gracias por apoyar este proyecto!\nPuedes hacer tu aporte aquí:",
        reply_markup=teclado
    )
# ---------------------------
# Configuración del bot
# ---------------------------
# Usa variable de entorno TELEGRAM_TOKEN si está definida, si no usa tu token actual
TOKEN = os.getenv("TELEGRAM_TOKEN", "7023804645:AAEXWroo4DBLGGNHqwIQbPx96GEDov9XlIk")
app = ApplicationBuilder().token(TOKEN).build()

# ---------------------------
# Handlers del bot
# ---------------------------

# Quiz
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("jugar", jugar))
app.add_handler(CommandHandler("puntaje", puntaje))
app.add_handler(CallbackQueryHandler(button_quiz, pattern="^(?!mision_).*"))

# Misiones
app.add_handler(CommandHandler("mision", mision))
app.add_handler(CallbackQueryHandler(button_mision, pattern="^mision_"))

# Donaciones
app.add_handler(CommandHandler("donar", donar))

# ---------------------------
# Mensaje de inicio en consola
# ---------------------------
print("Bot avanzado con quiz + misiones + donaciones iniciado...")

# ---------------------------
# Ejecutar bot
# ---------------------------
app.run_polling()










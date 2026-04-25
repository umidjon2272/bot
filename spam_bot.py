import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8726621448:AAF1wT6RBE1UXU5VlhGJMQqL4J4rSbu4G4s"

# Profil bilan bog'liq so'zlar
PROFIL_KEYWORDS = [
    "profilimda",
    "profilimga",
    "profilga",
    "profilim",
    "profilimd",
    "proflimda",
    "proflimga",
    "proflim",
]

# Spam harakatlar
SPAM_ACTIONS = [
    "o'ting",
    "oting",
    "kiring",
    "kring",
    "tashrif",
    "obuna",
    "obno",
    "kutmoqda",
    "kutaman",
    "bor ",
    "boling",
    "buyring",
    "qoling",
    "videolar",
    "vddeo",
    "video",
    "kontent",
]

def is_spam(text: str) -> bool:
    if not text:
        return False
    t = text.lower()

    # "profil" so'zi bormi?
    has_profil = any(k in t for k in PROFIL_KEYWORDS)
    if not has_profil:
        return False

    # "hammaga salom" yoki "salom" + spam harakat
    has_hammaga = "hammaga" in t or "hamag" in t
    has_action = any(a in t for a in SPAM_ACTIONS)

    if has_hammaga:
        return True  # hammaga salom + profil = spam
    if has_action:
        return True  # profil + harakat so'zi = spam

    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    chat = message.chat
    user = message.from_user
    if chat.type not in ["group", "supergroup"]:
        return
    if is_spam(message.text):
        try:
            await message.delete()
            await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
            print(f"Bloklandi: {user.full_name} | Xabar: {message.text[:60]}")
        except Exception as e:
            print(f"Xato: {e}")

async def main():
    print("Spam bot ishga tushdi...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot ishlayapti! Guruhga admin qilib qo'shing.")
    print("Toxtatish uchun Ctrl+C bosing")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
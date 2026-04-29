import asyncio
import re
import unicodedata
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8726621448:AAF1wT6RBE1UXU5VlhGJMQqL4J4rSbu4G4s"

def clean_text(text: str) -> str:
    """Ko'rinmas belgilar va unicode tricks ni tozalash"""
    # Barcha ko'rinmas/control belgilarni o'chirish
    cleaned = ""
    for ch in text:
        cat = unicodedata.category(ch)
        # Cf = format chars (zero-width, soft hyphen va h.k.)
        # Cc = control chars
        if cat not in ("Cf", "Cc"):
            cleaned += ch
    # Bir nechta bo'shliqlarni birga qo'shish
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lower()

PROFIL_KEYWORDS = [
    "profilimda", "profilimga", "profilga", "profilim",
    "profilimd", "proflimda", "proflimga", "proflim",
    "mening profilim",
]

SPAM_ACTIONS = [
    "o'ting", "oting", "kiring", "kring", "qarang",
    "tashrif", "obuna", "kutmoqda", "kutaman", "boling",
    "buyring", "qoling", "videolar", "video", "kontent",
    "birga bo'lish", "lazzat", "hamma narsa bor", "maxsus",
    "men bilan", "kir va", "qo'l qo'y", "rohatlan",
    "jonli", "ho'l bo'l", "hol bol", "tanam bilan",
    "og'zim", "qo'lim", "butun tan",
]

ALWAYS_BLOCK = [
    "profilimga o't",
    "profilimga ot",
    "profilga o't",
    "profilimga kir",
    "profilga kir",
    "profilimga qarang",
    "mening profilimga",
    "hammaga salom profilim",
    "salom hammaga profilim",
    "birga ho'l bo'l",
    "birga hol bol",
    "rohatlantirayotganimni",
    "jonli ravishda",
]

# Spam emoji
SPAM_EMOJIS = ["👄", "💋", "🔞", "💦", "🍑", "🍆"]

def is_spam(text: str) -> bool:
    if not text:
        return False
    
    t = clean_text(text)

    # Spam emoji bormi matnda
    if any(e in text for e in SPAM_EMOJIS):
        # Emoji + profil = spam
        has_profil = any(k in t for k in PROFIL_KEYWORDS)
        has_action = any(a in t for a in SPAM_ACTIONS)
        if has_profil or has_action:
            return True

    # Har doim bloklash
    for phrase in ALWAYS_BLOCK:
        if phrase in t:
            return True

    # Profil + harakat
    has_profil = any(k in t for k in PROFIL_KEYWORDS)
    if not has_profil:
        return False

    has_hammaga = "hammaga" in t or "hamag" in t or "hamma" in t
    has_action = any(a in t for a in SPAM_ACTIONS)

    if has_hammaga or has_action:
        return True

    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    chat = message.chat
    user = message.from_user
    if chat.type not in ["group", "supergroup"]:
        return

    if message.text and is_spam(message.text):
        await ban_user(context, chat.id, user, message)
        return

    if message.sticker:
        emoji = message.sticker.emoji or ""
        if any(e in emoji for e in SPAM_EMOJIS):
            await ban_user(context, chat.id, user, message)
            return

async def ban_user(context, chat_id, user, message):
    try:
        await message.delete()
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
        print(f"Bloklandi: {user.full_name} (@{user.username})")
    except Exception as e:
        print(f"Xato: {e}")

async def main():
    print("Spam bot ishga tushdi...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot ishlayapti!")
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
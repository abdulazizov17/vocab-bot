import os
import json
import random
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8641905482:AAEYXn3A8J8d221bM9RRy4w5t6Kdy60M8UY")
DATA_FILE = "user_data.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

WORDS = [
    {"en": "apple", "ipa": "/ˈæp.əl/", "uz": "olma", "example": "I eat an apple every morning.", "level": "beginner"},
    {"en": "book", "ipa": "/bʊk/", "uz": "kitob", "example": "She reads a book every night.", "level": "beginner"},
    {"en": "water", "ipa": "/ˈwɔː.tər/", "uz": "suv", "example": "Can I have a glass of water?", "level": "beginner"},
    {"en": "happy", "ipa": "/ˈhæp.i/", "uz": "baxtli", "example": "The children are happy at the park.", "level": "beginner"},
    {"en": "run", "ipa": "/rʌn/", "uz": "yugurmoq", "example": "I run every morning to stay healthy.", "level": "beginner"},
    {"en": "friend", "ipa": "/frend/", "uz": "do'st", "example": "My best friend lives in London.", "level": "beginner"},
    {"en": "school", "ipa": "/skuːl/", "uz": "maktab", "example": "The children go to school every day.", "level": "beginner"},
    {"en": "eat", "ipa": "/iːt/", "uz": "yemoq", "example": "We eat dinner at 7 pm.", "level": "beginner"},
    {"en": "sleep", "ipa": "/sliːp/", "uz": "uxlamoq", "example": "I sleep eight hours every night.", "level": "beginner"},
    {"en": "work", "ipa": "/wɜːrk/", "uz": "ishlаmoq", "example": "She works in a hospital.", "level": "beginner"},
    {"en": "beautiful", "ipa": "/ˈbjuː.tɪ.fəl/", "uz": "chiroyli", "example": "The sunset was absolutely beautiful.", "level": "elementary"},
    {"en": "travel", "ipa": "/ˈtræv.əl/", "uz": "sayohat qilmoq", "example": "I love to travel to new countries.", "level": "elementary"},
    {"en": "surprised", "ipa": "/səˈpraɪzd/", "uz": "hayron", "example": "She was surprised by the gift.", "level": "elementary"},
    {"en": "important", "ipa": "/ɪmˈpɔːr.tənt/", "uz": "muhim", "example": "It is important to drink water daily.", "level": "elementary"},
    {"en": "comfortable", "ipa": "/ˈkʌm.fər.tə.bəl/", "uz": "qulay", "example": "This chair is very comfortable.", "level": "elementary"},
    {"en": "speak", "ipa": "/spiːk/", "uz": "gapirmoq", "example": "Can you speak more slowly, please?", "level": "elementary"},
    {"en": "understand", "ipa": "/ˌʌn.dəˈstænd/", "uz": "tushunmoq", "example": "I do not understand this question.", "level": "elementary"},
    {"en": "market", "ipa": "/ˈmɑːr.kɪt/", "uz": "bozor", "example": "We buy vegetables at the market.", "level": "elementary"},
    {"en": "decide", "ipa": "/dɪˈsaɪd/", "uz": "qaror qilmoq", "example": "She decided to study medicine.", "level": "elementary"},
    {"en": "explain", "ipa": "/ɪkˈspleɪn/", "uz": "tushuntirmoq", "example": "Can you explain this rule again?", "level": "elementary"},
    {"en": "achieve", "ipa": "/əˈtʃiːv/", "uz": "erishmoq", "example": "She worked hard to achieve her goals.", "level": "intermediate"},
    {"en": "although", "ipa": "/ɔːlˈðoʊ/", "uz": "garchi", "example": "Although it was raining, we went outside.", "level": "intermediate"},
    {"en": "significant", "ipa": "/sɪɡˈnɪf.ɪ.kənt/", "uz": "muhim, katta", "example": "There was a significant change in results.", "level": "intermediate"},
    {"en": "efficient", "ipa": "/ɪˈfɪʃ.ənt/", "uz": "samarali", "example": "The new system is more efficient.", "level": "intermediate"},
    {"en": "perspective", "ipa": "/pərˈspek.tɪv/", "uz": "nuqtai nazar", "example": "Try to see it from her perspective.", "level": "intermediate"},
    {"en": "opportunity", "ipa": "/ˌɒp.əˈtjuː.nɪ.ti/", "uz": "imkoniyat", "example": "This is a great opportunity for growth.", "level": "intermediate"},
    {"en": "challenge", "ipa": "/ˈtʃæl.ɪndʒ/", "uz": "qiyinlik", "example": "Learning English is a challenge, but worth it.", "level": "intermediate"},
    {"en": "environment", "ipa": "/ɪnˈvaɪ.rən.mənt/", "uz": "atrof-muhit", "example": "We must protect the environment.", "level": "intermediate"},
    {"en": "culture", "ipa": "/ˈkʌl.tʃər/", "uz": "madaniyat", "example": "Every country has its own culture.", "level": "intermediate"},
    {"en": "influence", "ipa": "/ˈɪn.flu.əns/", "uz": "ta'sir qilmoq", "example": "Music can influence your mood.", "level": "intermediate"},
]

LEVEL_EMOJI = {"beginner": "🟢", "elementary": "🔵", "intermediate": "🟡"}
LEVEL_NAME = {"beginner": "Beginner", "elementary": "Elementary", "intermediate": "Intermediate"}

WAITING_SENTENCE = 1


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(data, uid):
    uid = str(uid)
    if uid not in data:
        data[uid] = {
            "learned": [],
            "daily_goal": 5,
            "streak": 0,
            "last_date": "",
            "sentences": 0,
            "current_word": None,
            "level_filter": "all",
            "daily_count": 0,
        }
    return data[uid]


def get_filtered_words(level_filter):
    if level_filter == "all":
        return WORDS
    return [w for w in WORDS if w["level"] == level_filter]


def get_daily_words(user, count=5):
    learned = set(user["learned"])
    level = user.get("level_filter", "all")
    pool = get_filtered_words(level)
    not_learned = [w for w in pool if w["en"] not in learned]
    if not not_learned:
        not_learned = pool
    today = str(date.today())
    random.seed(today + str(sum(ord(c) for c in str(user.get("learned", [])))))
    return random.sample(not_learned, min(count, len(not_learned)))


def word_card_text(word):
    lvl = word["level"]
    return (
        f"{LEVEL_EMOJI[lvl]} *{word['en']}*  `{LEVEL_NAME[lvl]}`\n"
        f"🔊 _{word['ipa']}_\n"
        f"🇺🇿 *{word['uz']}*\n\n"
        f"📝 _{word['example']}_"
    )


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Bugungi so'zlar", callback_data="daily")],
        [InlineKeyboardButton("✍️ Gap tuz", callback_data="practice"),
         InlineKeyboardButton("📖 Lug'atim", callback_data="vocab")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats"),
         InlineKeyboardButton("⚙️ Sozlama", callback_data="settings")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = get_user(data, update.effective_user.id)
    save_data(data)
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Salom, *{name}*\\! 👋\n\n"
        "Men sizga har kuni ingliz so'zlarini o'rgataman\\.\n"
        "Beginner → Elementary → Intermediate darajalariga bo'lingan\\.\n\n"
        "Boshlaylik\\! 👇",
        parse_mode="MarkdownV2",
        reply_markup=main_menu_keyboard(),
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Asosiy menyu 👇",
        reply_markup=main_menu_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    uid = query.from_user.id
    user = get_user(data, uid)

    cb = query.data

    # --- DAILY ---
    if cb == "daily":
        today = str(date.today())
        if user["last_date"] != today:
            user["daily_count"] = 0
            user["last_date"] = today
        words = get_daily_words(user, user["daily_goal"])
        text = f"📅 *Bugungi so'zlar* \\({user['daily_count']}/{user['daily_goal']}\\)\n\n"
        for i, w in enumerate(words, 1):
            text += f"{i}\\. {LEVEL_EMOJI[w['level']]} *{w['en']}* — {w['uz']}\n"
        kb = []
        for w in words:
            kb.append([InlineKeyboardButton(f"📖 {w['en']}", callback_data=f"word_{w['en']}")])
        kb.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back")])
        save_data(data)
        await query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup(kb))

    # --- WORD DETAIL ---
    elif cb.startswith("word_"):
        en = cb[5:]
        word = next((w for w in WORDS if w["en"] == en), None)
        if not word:
            return
        user["current_word"] = en
        save_data(data)
        text = word_card_text(word)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yodladim", callback_data=f"learned_{en}"),
             InlineKeyboardButton("✍️ Gap tuz", callback_data=f"do_practice_{en}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="daily")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # --- MARK LEARNED ---
    elif cb.startswith("learned_"):
        en = cb[8:]
        today = str(date.today())
        if user["last_date"] != today:
            user["daily_count"] = 0
            user["last_date"] = today
        if en not in user["learned"]:
            user["learned"].append(en)
            user["daily_count"] += 1
            if user["daily_count"] >= user["daily_goal"]:
                if user["last_date"] != today:
                    user["streak"] += 1
        save_data(data)
        await query.edit_message_text(
            f"✅ *{en}* yodlandi\\!\n\n"
            f"Bugun: {user['daily_count']}/{user['daily_goal']} so'z\n"
            f"🔥 Streak: {user['streak']} kun",
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Davom et", callback_data="daily")],
                [InlineKeyboardButton("🏠 Menyu", callback_data="back")],
            ])
        )

    # --- PRACTICE ---
    elif cb == "practice":
        level = user.get("level_filter", "all")
        pool = get_filtered_words(level)
        word = random.choice(pool)
        user["current_word"] = word["en"]
        save_data(data)
        text = (
            f"✍️ *Gap tuzish mashqi*\n\n"
            f"Quyidagi so'zdan foydalanib inglizcha gap yozing:\n\n"
            f"*{word['en']}* — {word['uz']}\n"
            f"_{word['ipa']}_\n\n"
            f"📝 Gapingizni yozing\\:"
        )
        await query.edit_message_text(text, parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="back")]]))
        context.user_data["waiting_sentence"] = True
        context.user_data["practice_word"] = word["en"]

    # --- DO PRACTICE from word detail ---
    elif cb.startswith("do_practice_"):
        en = cb[12:]
        word = next((w for w in WORDS if w["en"] == en), None)
        user["current_word"] = en
        save_data(data)
        text = (
            f"✍️ *Gap tuzish mashqi*\n\n"
            f"*{word['en']}* — {word['uz']}\n\n"
            f"Inglizcha gap yozing\\:"
        )
        await query.edit_message_text(text, parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="back")]]))
        context.user_data["waiting_sentence"] = True
        context.user_data["practice_word"] = en

    # --- VOCAB ---
    elif cb == "vocab":
        learned = user["learned"]
        total = len(WORDS)
        b = len([w for w in WORDS if w["level"] == "beginner" and w["en"] in learned])
        e = len([w for w in WORDS if w["level"] == "elementary" and w["en"] in learned])
        i = len([w for w in WORDS if w["level"] == "intermediate" and w["en"] in learned])
        text = (
            f"📖 *Mening lug'atim*\n\n"
            f"🟢 Beginner: {b}/10\n"
            f"🔵 Elementary: {e}/10\n"
            f"🟡 Intermediate: {i}/10\n\n"
            f"Jami: *{len(learned)}/{total}* so'z o'rganildi"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Beginner so'zlar", callback_data="list_beginner")],
            [InlineKeyboardButton("🔵 Elementary so'zlar", callback_data="list_elementary")],
            [InlineKeyboardButton("🟡 Intermediate so'zlar", callback_data="list_intermediate")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="back")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # --- WORD LISTS ---
    elif cb.startswith("list_"):
        level = cb[5:]
        words = [w for w in WORDS if w["level"] == level]
        learned = user["learned"]
        text = f"{LEVEL_EMOJI[level]} *{LEVEL_NAME[level]} so'zlari*\n\n"
        for w in words:
            check = "✅" if w["en"] in learned else "⬜"
            text += f"{check} *{w['en']}* — {w['uz']}\n"
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="vocab")]]))

    # --- STATS ---
    elif cb == "stats":
        today = str(date.today())
        if user["last_date"] != today:
            user["daily_count"] = 0
        total_learned = len(user["learned"])
        text = (
            f"📊 *Statistika*\n\n"
            f"✅ O'rganilgan so'zlar: *{total_learned}*\n"
            f"📅 Bugun o'rganildi: *{user['daily_count']}/{user['daily_goal']}*\n"
            f"🔥 Streak: *{user['streak']}* kun\n"
            f"✍️ Tuzilgan gaplar: *{user['sentences']}*\n\n"
            f"🟢 Beginner: {len([w for w in WORDS if w['level']=='beginner' and w['en'] in user['learned']])}/10\n"
            f"🔵 Elementary: {len([w for w in WORDS if w['level']=='elementary' and w['en'] in user['learned']])}/10\n"
            f"🟡 Intermediate: {len([w for w in WORDS if w['level']=='intermediate' and w['en'] in user['learned']])}/10"
        )
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]]))

    # --- SETTINGS ---
    elif cb == "settings":
        level = user.get("level_filter", "all")
        goal = user["daily_goal"]
        text = f"⚙️ *Sozlamalar*\n\nHozirgi daraja: *{level}*\nKunlik maqsad: *{goal}* so'z"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Barcha daraja", callback_data="set_level_all"),
             InlineKeyboardButton("🟢 Beginner", callback_data="set_level_beginner")],
            [InlineKeyboardButton("🔵 Elementary", callback_data="set_level_elementary"),
             InlineKeyboardButton("🟡 Intermediate", callback_data="set_level_intermediate")],
            [InlineKeyboardButton("Maqsad: 3", callback_data="set_goal_3"),
             InlineKeyboardButton("Maqsad: 5", callback_data="set_goal_5"),
             InlineKeyboardButton("Maqsad: 10", callback_data="set_goal_10")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="back")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif cb.startswith("set_level_"):
        level = cb[10:]
        user["level_filter"] = level
        save_data(data)
        await query.answer(f"Daraja: {level}", show_alert=True)
        # re-show settings
        context.user_data["cb_override"] = "settings"
        await button_handler(update, context)

    elif cb.startswith("set_goal_"):
        goal = int(cb[9:])
        user["daily_goal"] = goal
        save_data(data)
        await query.answer(f"Maqsad: {goal} so'z", show_alert=True)
        context.user_data["cb_override"] = "settings"
        await button_handler(update, context)

    # --- BACK ---
    elif cb == "back":
        await query.edit_message_text("Asosiy menyu 👇", reply_markup=main_menu_keyboard())

    save_data(data)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_sentence"):
        await update.message.reply_text("Menyu uchun /menu yozing.", reply_markup=main_menu_keyboard())
        return

    sentence = update.message.text.strip()
    word_en = context.user_data.get("practice_word", "")
    context.user_data["waiting_sentence"] = False

    data = load_data()
    user = get_user(data, update.effective_user.id)

    word = next((w for w in WORDS if w["en"] == word_en), None)
    if not word:
        await update.message.reply_text("Xatolik yuz berdi. /menu")
        return

    # Simple check without external AI
    sentence_lower = sentence.lower()
    word_used = word_en.lower() in sentence_lower
    has_capital = sentence[0].isupper() if sentence else False
    has_punctuation = sentence[-1] in ".!?" if sentence else False
    word_count = len(sentence.split())

    feedback_lines = []

    if word_used:
        feedback_lines.append(f"✅ '{word_en}' so'zi to'g'ri ishlatilgan!")
    else:
        feedback_lines.append(f"❌ '{word_en}' so'zini gapda ishlatmadingiz.")

    if has_capital:
        feedback_lines.append("✅ Gap bosh harf bilan boshlangan.")
    else:
        feedback_lines.append("⚠️ Gap bosh harf bilan boshlanishi kerak.")

    if has_punctuation:
        feedback_lines.append("✅ Tinish belgisi bor.")
    else:
        feedback_lines.append("⚠️ Gap oxirida '.' yoki '!' qo'ying.")

    if word_count >= 4:
        feedback_lines.append(f"✅ Gap uzunligi yaxshi ({word_count} ta so'z).")
    else:
        feedback_lines.append(f"⚠️ Gap biroz qisqa ({word_count} ta so'z). Davomli gap tuzing.")

    feedback_lines.append(f"\n📝 *Namuna*: _{word['example']}_")

    user["sentences"] = user.get("sentences", 0) + 1
    save_data(data)

    text = f"📋 *Natija:*\n\n" + "\n".join(feedback_lines)
    await update.message.reply_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✍️ Yana mashq", callback_data="practice")],
            [InlineKeyboardButton("🏠 Menyu", callback_data="back")],
        ]))


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

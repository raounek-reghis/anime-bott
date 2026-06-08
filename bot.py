import os
import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ─── إعداد اللوغ ───────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── مفاتيح API (تُقرأ من متغيرات البيئة) ─────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# ─── المستخدم المسموح له فقط ───────────────────────────────
# ضع ID أخيك هنا في Railway (راجع README لمعرفة كيف تحصل عليه)
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── فلتر التحقق من المستخدم ───────────────────────────────
async def is_allowed(update: Update) -> bool:
    user_id = update.effective_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("⛔ عذراً، هذا البوت خاص ولا يمكنك استخدامه.")
        logger.warning(f"محاولة دخول غير مصرح بها من ID: {user_id}")
        return False
    return True

# ─── سياق المحادثة لكل مستخدم ──────────────────────────────
user_histories: dict[int, list[dict]] = {}

SYSTEM_PROMPT = """أنت مساعد متخصص في اقتراح الأنميات والأفلام. 
تتحدث بالعربية دائماً وتعطي توصيات مفيدة مع وصف مختصر وتقييم لكل عمل.
عندما تقترح أنميات أو أفلام، قدّم دائماً:
- اسم العمل (بالعربي والإنجليزي)
- نوعه (أكشن / رومانسي / خيال علمي / إلخ)
- وصف قصير ومشوّق
- تقييمك من 10
- سبب توصيتك به
استخدم إيموجيات مناسبة لتجميل ردودك."""

# ─── /myid (لمعرفة الـ ID) ─────────────────────────────────
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"🪪 معلوماتك:\n"
        f"• الاسم: {user.full_name}\n"
        f"• الـ ID: `{user.id}`\n\n"
        f"انسخ الـ ID وضعه في Railway كـ ALLOWED\\_USER\\_ID",
        parse_mode="Markdown",
    )

# ─── /start ────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    keyboard = [
        [
            InlineKeyboardButton("🎌 اقترح أنمي", callback_data="suggest_anime"),
            InlineKeyboardButton("🎬 اقترح فيلم", callback_data="suggest_movie"),
        ],
        [
            InlineKeyboardButton("🔥 الأكثر شعبية", callback_data="popular"),
            InlineKeyboardButton("🎲 اختيار عشوائي", callback_data="random"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *مرحباً بك في بوت الأنمي والأفلام!*\n\n"
        "يمكنني مساعدتك في:\n"
        "🎌 اقتراح أنميات رائعة\n"
        "🎬 اقتراح أفلام مميزة\n"
        "💬 أو اكتب لي ما تحب وسأقترح لك!\n\n"
        "اختر من القائمة أو اكتب طلبك مباشرة:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

# ─── /help ─────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    await update.message.reply_text(
        "📖 *كيفية استخدام البوت:*\n\n"
        "• اكتب أي شيء مثل: _'اقترح لي أنمي أكشن'_\n"
        "• أو: _'أريد فيلم رومانسي'_\n"
        "• أو: _'ما أفضل أنمي خيال علمي؟'_\n\n"
        "الأوامر المتاحة:\n"
        "/start - القائمة الرئيسية\n"
        "/help - المساعدة\n"
        "/clear - مسح سجل المحادثة",
        parse_mode="Markdown",
    )

# ─── /clear ────────────────────────────────────────────────
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("🗑️ تم مسح سجل المحادثة. ابدأ محادثة جديدة!")

# ─── أزرار inline ──────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await is_allowed(update):
        return

    prompts = {
        "suggest_anime": "اقترح لي أنمي رائع مع وصف تفصيلي",
        "suggest_movie": "اقترح لي فيلم رائع مع وصف تفصيلي",
        "popular": "ما هي أشهر الأنميات والأفلام حالياً؟",
        "random": "اقترح لي عملاً عشوائياً مميزاً (أنمي أو فيلم)",
    }

    user_text = prompts.get(query.data, "مرحباً")
    await query.message.reply_text("⏳ جاري التفكير...")
    response = await get_ai_response(query.from_user.id, user_text)
    await query.message.reply_text(response, parse_mode="Markdown")

# ─── رسائل نصية ────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_allowed(update):
        return
    user_id = update.effective_user.id
    user_text = update.message.text

    await update.message.reply_text("⏳ جاري التفكير...")
    response = await get_ai_response(user_id, user_text)
    await update.message.reply_text(response, parse_mode="Markdown")

# ─── استدعاء Claude API ────────────────────────────────────
async def get_ai_response(user_id: int, user_text: str) -> str:
    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": user_text})

    # احتفظ بآخر 10 رسائل فقط لتجنب تجاوز حد التوكنز
    history = user_histories[user_id][-10:]

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = message.content[0].text
        user_histories[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return "❌ حدث خطأ، حاول مرة أخرى لاحقاً."

# ─── تشغيل البوت ───────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

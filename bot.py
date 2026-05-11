import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# ===== СЮДА ВСТАВЬТЕ ВАШИ КЛЮЧИ =====
TELEGRAM_TOKEN = "8399989544:AAFDRhBZ8dnwRzjSOno6JdOAjs8RCgyGkKs"  # от BotFather
GROQ_API_KEY = "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"      # от console.groq.com
# =====================================

client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SYSTEM_PROMPT = """Ты помощник для бизнеса по абразивным материалам и шлифовальным камням.

Ты умеешь:
1. ИСКАТЬ ПРОИЗВОДИТЕЛЕЙ - когда пользователь пишет название детали или материала и страну,
   ты находишь реальных производителей с сайтами и контактами.
   
2. ПРОВЕРЯТЬ НАДЁЖНОСТЬ - для каждого производителя объясняешь:
   - Реальный производитель или перекупщик
   - На что обратить внимание при проверке
   - Есть ли сертификаты ISO, SGS
   - Как проверить на Alibaba (Gold Supplier, Verified, Trade Assurance)
   
3. ПЕРЕВОДИТЬ - переводишь тексты между русским, английским и китайским языками.

4. ПИСАТЬ ПИСЬМА - составляешь деловые письма поставщикам на английском.

5. КОНСУЛЬТИРОВАТЬ ПО АБРАЗИВАМ - объясняешь какой камень (WA, PA, GC, A и др.) 
   подходит для каких задач.

Отвечай чётко, по делу, структурированно. Используй эмодзи для наглядности.
Всегда отвечай на том языке на котором пишет пользователь."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! 👋 Я ваш бизнес-помощник по абразивам и производителям.\n\n"
        "Что я умею:\n"
        "🔍 Найти производителей по детали и стране\n"
        "✅ Проверить надёжность производителя\n"
        "🌐 Перевести текст (рус/англ/китай)\n"
        "✉️ Написать письмо поставщику\n"
        "📚 Подобрать нужный абразивный камень\n\n"
        "Просто напишите что вам нужно!\n"
        "Например: 'Найди производителей шлифовальных кругов WA в Китае'"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Примеры запросов:\n\n"
        "• 'Найди производителей шлифовальных кругов в Китае'\n"
        "• 'Проверь компанию Zhengzhou Abrasives Co'\n"
        "• 'Переведи на английский: Здравствуйте, меня зовут Шахбоз'\n"
        "• 'Напиши письмо поставщику про камни WA и PA'\n"
        "• 'Какой камень подходит для заточки твёрдых сплавов?'\n"
        "• 'Что такое Gold Supplier на Alibaba?'"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.7,
        )
        
        response = chat_completion.choices[0].message.content
        
        # Telegram имеет лимит 4096 символов - разбиваем если длинный
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(response)
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}\n\nПопробуйте ещё раз."
        )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен! Нажмите Ctrl+C чтобы остановить.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

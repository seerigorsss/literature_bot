import logging

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(
        "Привет. Я бот-литератор.\n"
        "Я буду читать одну строчку из стихотворения, а тебе необходимо будет продолжить.\n"
        "Интересно? Пиши да, если готов.\n"
        "Вы можете прервать работу в любой момент, послав команду /stop.")
    return 1


async def first_response(update, context):
    context.user_data['agreed'] = update.message.text.lower()
    if context.user_data['agreed'] == 'да':
        with open('data/example.txt', mode='r', encoding='utf-8') as f:
            text = [i.strip() for i in f.readlines()]
        context.user_data['text'] = text
        context.user_data['current_question'] = 0
        await ask_question(update, context)
        return 2


async def ask_question(update, context):
    question = context.user_data['text'][context.user_data['current_question']]
    await update.message.reply_text(question)
    if context.user_data['text'].index(question) == len(context.user_data['text']) - 1:
        await end(update, context)
        return ConversationHandler.END


async def handle_answer(update, context):
    answer = update.message.text
    correct_answer = context.user_data['text'][context.user_data['current_question'] + 1]
    if answer == correct_answer:
        if context.user_data['text'].index(answer) == len(context.user_data['text']) - 1:
            await end(update, context)
            return ConversationHandler.END
        context.user_data['current_question'] += 2
        await ask_question(update, context)
    else:
        await update.message.reply_text("Неправильно.\n"
                                        "Если хотите воспользоваться подсказкой, пишите /suphler.")


async def end(update, context):
    await update.message.reply_text(f"Круто получилось!\n"
                                    f"Если желаете почитать стихотворения снова, отправляйте /start")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Работа бота прервана!\n"
                                    "Если желаете начать заново, то пишите /start.")
    return ConversationHandler.END


async def suphler(update, context):
    question = context.user_data['text'][context.user_data['current_question'] + 1]
    await update.message.reply_text(question)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
        },
        fallbacks=[CommandHandler('stop', stop), CommandHandler('suphler', suphler)])

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()

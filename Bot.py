import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# --- Настройки ---
TOKEN = "8434037705:AAGLimloZYPDEIpNFnBNpkY24z0qaBC3oEU"
LEADER_ID = 7896463644

# Вопросы для подачи заявки
QUESTIONS = [
    "Твой игровой ник?",
    "Твой игровой UID?",
    "Как тебя зовут?",
    "Сколько тебе лет?"
]

# Словарь для хранения ответов пользователей
user_data = {}

# --- Логирование ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# --- Этапы разговора ---
ASK_NICK, ASK_UID, ASK_NAME, ASK_AGE = range(4)

# --- Команды ---
def start(update: Update, context: CallbackContext):
    reply_keyboard = [['Подать заявку', 'Инфо']]
    update.message.reply_text(
        "Привет! 👻🛡️\n"
        "Я SpectralGuardBot — был создан для удобной подачи заявок на вступление в клан.\n"
        "Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

def info(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Информация о вступлении в клан:\n\n"
        "Чтобы подать заявку, нажмите кнопку 'Подать заявку'.\n"
        "После заполнения всех вопросов лидер клана рассмотрит заявку и сообщит результат.\n\n"
        "Пример заполнения:\n"
        "Описание:\nИмя:\nВозраст:\nИгровое имя:\nUID:\nУстройство: (если хотите)"
    )

def start_application(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data[user_id] = {}
    update.message.reply_text(QUESTIONS[0])
    return ASK_NICK

def ask_uid(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data[user_id]['nick'] = update.message.text
    update.message.reply_text(QUESTIONS[1])
    return ASK_UID

def ask_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data[user_id]['uid'] = update.message.text
    update.message.reply_text(QUESTIONS[2])
    return ASK_NAME

def ask_age(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data[user_id]['name'] = update.message.text
    update.message.reply_text(QUESTIONS[3])
    return ASK_AGE

def finish_application(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data[user_id]['age'] = update.message.text
    
    # Формируем текст заявки для лидера
    application_text = (
        f"Новая заявка от {update.message.from_user.full_name}:\n\n"
        f"Игровой ник: {user_data[user_id]['nick']}\n"
        f"UID: {user_data[user_id]['uid']}\n"
        f"Имя: {user_data[user_id]['name']}\n"
        f"Возраст: {user_data[user_id]['age']}\n\n"
        "Для добавления в клан или отклонения используйте кнопки."
    )
    
    # Отправляем лидеру
    context.bot.send_message(chat_id=LEADER_ID, text=application_text)
    
    # Уведомление пользователю
    update.message.reply_text(
        "Спасибо! Ваша заявка была отправлена на рассмотрение.\n"
        "Лидер клана проверит её и свяжется с вами."
    )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Вы отменили подачу заявки.")
    return ConversationHandler.END

# --- Основная функция ---
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("info", info))

    # Conversation для подачи заявки
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Подать заявку$'), start_application)],
        states={
            ASK_NICK: [MessageHandler(Filters.text & ~Filters.command, ask_uid)],
            ASK_UID: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_age)],
            ASK_AGE: [MessageHandler(Filters.text & ~Filters.command, finish_application)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

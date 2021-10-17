import qrcode
import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['To\'liq Ism', 'Ish Joy'],
    ['Ish Joyidagi Mavqe', 'Boshqa narsalar...'],
    ['BARARILSIN!'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Assalomu alaykum men Qr Generator botman. "
        "Siz menga o\'zingiz haqingizda malumot bersangiz men sizga malumotning qr kodini yasab beraman.",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Sizning {text}ingiz? Ha, albatta malumot bering!')

    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for a description of a custom category."""
    update.message.reply_text(
        'Albatta, birinchi menga kategoriyani jonating, masalan "Ish Manzil:"'
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        "Menga ushbu malumotlari berdingiz:"
        f"{facts_to_str(user_data)} Menga boshqa narsa haqida aytishingiz mumkin yoki (BAJARILSIN) degan tugamni bosing!",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"Men siz haqingizda ushbu malumotlarni o\'rgandim: {facts_to_str(user_data)} !",
        reply_markup=ReplyKeyboardRemove(),
    )
    malumot = f"Malumotlar:\n{facts_to_str(user_data)}"

    img = qrcode.make(malumot)
    img.save(f"{malumot}.jpg")

    file = open(f"{malumot}.jpg",'rb')
    update.message.reply_photo(file)



    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("You should place your token here")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(To\'liq Ism|Ish Joy|Ish Joyidagi Mavqe)$'), regular_choice
                ),
                MessageHandler(Filters.regex('^Boshqa narsalar...$'), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^BARARILSIN!$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^BARARILSIN!$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^BARARILSIN!$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
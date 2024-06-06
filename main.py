from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Coloque o token do seu bot aqui
TOKEN = '7497749943:AAEtHg-3e97tDA_cAEsFcLwko6LAQfxtYG0'

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Olá {user.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na cassino BC Game digite /bonus. Bônus inicial é em Crypto, se não sabe como trabalhar com criptomoedas aconselho a ver algum vídeo no YouTube referente ao mesmo. Bônus não tem nenhum tipo de bloqueio ou rollover, apenas aposte 1 vez e pode sacar.")

def bonus(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("1º Já criou conta com o código MFREIRE no registo ou pelo link 'https://....'? Digite /confirmar para continuar")

def confirmar(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Envie print da tela do seu perfil BC Game, vá no canto superior direito, meu perfil e mande print da tela")

def receber_bonus(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("25R$ grátis", callback_data='gratis')],
        [InlineKeyboardButton("100R$ extra", callback_data='extra')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("4º Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra.", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'gratis':
        query.edit_message_text(text="Você escolheu receber 25R$ grátis sem depósito. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")
    elif query.data == 'extra':
        query.edit_message_text(text="Você escolheu depositar 100R$ ou mais para receber 100R$ extra. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")

    query.message.reply_text("Digite /confirmar para continuar")

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("bonus", bonus))
    dispatcher.add_handler(CommandHandler("confirmar", confirmar))
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

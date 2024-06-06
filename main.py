from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Pegar o token da variável de ambiente
TOKEN = os.getenv('TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Olá {user.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na cassino BC Game digite /bonus. Bônus inicial é em Crypto, se não sabe como trabalhar com criptomoedas aconselho a ver algum vídeo no YouTube referente ao mesmo. Bônus não tem nenhum tipo de bloqueio ou rollover, apenas aposte 1 vez e pode sacar.")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("1º Já criou conta com o código MFREIRE no registo ou pelo link 'https://....'? Digite /confirmar para continuar")

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Envie print da tela do seu perfil BC Game, vá no canto superior direito, meu perfil e mande print da tela")

async def receber_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("25R$ grátis", callback_data='gratis')],
        [InlineKeyboardButton("100R$ extra", callback_data='extra')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("4º Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra.", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'gratis':
        await query.edit_message_text(text="Você escolheu receber 25R$ grátis sem depósito. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")
    elif query.data == 'extra':
        await query.edit_message_text(text="Você escolheu depositar 100R$ ou mais para receber 100R$ extra. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")

    await query.message.reply_text("Digite /confirmar para continuar")

def main() -> None:
    if TOKEN is None:
        raise ValueError("No TOKEN provided in environment variables")
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("confirmar", confirmar))
    application.add_handler(CallbackQueryHandler(button))
    
    # Usando o URL fornecido pelo Render para o webhook
    webhook_url = f"https://telegram-bot-ep12.onrender.com/{TOKEN}"
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    main()

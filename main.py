import os
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv('TOKEN')

# Dicionário para armazenar informações dos usuários
user_data = {}

# ID do administrador que receberá as informações compiladas
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')  # Substitua pelo seu User ID ou Username

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Olá {user.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na BC Game, mande uma mensagem para @BCGameOferta_bot com a mensagem /bonus.")
    print(f"/start command received from {user.first_name}")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_data[user.id] = {'stage': 1, 'info': f"Criou conta: sim\n"}
    await context.bot.send_message(chat_id=user.id, text="1º Já criou conta com o código MFREIRE no registo ou pelo link 'https://....'? Digite /confirmar para continuar")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Verifique suas mensagens privadas para continuar o processo.")
    print("/bonus command received")

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 1:
        user_data[user.id]['stage'] = 2
        await context.bot.send_message(chat_id=user.id, text="Envie print da tela do seu perfil BC Game, vá no canto superior direito, meu perfil e mande print da tela")
        print("/confirmar command received")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data:
        stage = user_data[user.id]['stage']
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        photo_path = f'{user.id}_{stage}.jpg'
        await photo_file.download(photo_path)
        print(f"Photo received from {user.first_name} for stage {stage}")

        if stage == 2:
            user_data[user.id]['stage'] = 3
            user_data[user.id]['profile_photo'] = photo_path
            user_data[user.id]['info'] += "Print da conta: [enviada]\n"
            await context.bot.send_message(chat_id=user.id, text="Verifique sua identidade na BC Game 'nível básico', vá no seu perfil, configurações, verificação e envie print da tela da verificação básica completa.")
            print("Profile photo received and stage updated to 3")

        elif stage == 3:
            user_data[user.id]['stage'] = 4
            user_data[user.id]['verification_photo'] = photo_path
            user_data[user.id]['info'] += "Print verficação básica: [enviada]\n"
            keyboard = [
                [InlineKeyboardButton("25R$ grátis", callback_data='gratis')],
                [InlineKeyboardButton("100R$ extra", callback_data='extra')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=user.id, text="4º Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra.", reply_markup=reply_markup)
            print("Verification photo received and stage updated to 4")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = query.from_user
    if query.data == 'gratis':
        user_data[user.id]['bonus_choice'] = 'gratis'
        user_data[user.id]['info'] += "Escolha do bônus: 25R$\n"
        await query.edit_message_text(text="Você escolheu receber 25R$ grátis sem depósito. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")
    elif query.data == 'extra':
        user_data[user.id]['bonus_choice'] = 'extra'
        user_data[user.id]['info'] += "Escolha do bônus: 100R$\n"
        await query.edit_message_text(text="Você escolheu depositar 100R$ ou mais para receber 100R$ extra. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")

    user_data[user.id]['stage'] = 5
    await context.bot.send_message(chat_id=user.id, text="Envie o print do depósito para continuar.")
    print(f"Button {query.data} clicked and stage updated to 5")

async def receive_deposit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 5:
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        photo_path = f'{user.id}_deposit.jpg'
        await photo_file.download(photo_path)
        user_data[user.id]['deposit_photo'] = photo_path
        user_data[user.id]['info'] += "Print de depósito: [enviada]\n"
        await context.bot.send_message(chat_id=user.id, text="Último passo, deixe um comentário no vídeo 'https://....' confirmando que recebeu o bônus (não se preocupe, se não receber seu bônus pode simplesmente remover o comentário).")
        user_data[user.id]['stage'] = 6
        print("Deposit photo received and stage updated to 6")

async def comment_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 6:
        user_data[user.id]['info'] += "Print de comentário: [enviada]\nFinalizado: sim\n"
        await context.bot.send_message(chat_id=user.id, text="Concluído, aguarde um pouco até aparecer seu bônus na conta.")
        
        # Enviar informações para o administrador
        info = user_data[user.id]['info']
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=info)
        
        # Enviar fotos
        for photo_key in ['profile_photo', 'verification_photo', 'deposit_photo']:
            if photo_key in user_data[user.id]:
                with open(user_data[user.id][photo_key], 'rb') as photo:
                    await context.bot.send_photo(chat_id=ADMIN_USER_ID, photo=photo, caption=photo_key.replace('_', ' ').capitalize())

        print("Comment confirmation received and process completed")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("confirmar", confirmar))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(user_data.keys()), receive_photo))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/comentariodone$'), comment_done))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        url_path=TOKEN,
        webhook_url=f"https://telegram-bot-ep12.onrender.com/{TOKEN}"
    )

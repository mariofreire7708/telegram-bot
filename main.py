import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, JobQueue
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_USER_ID = 1641003146  # Seu ID de administrador
GROUP_CHAT_ID = -1811495091

# Dicionário para armazenar informações dos usuários
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Olá {user.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na BC Game, mande uma mensagem para @BCGameOferta_bot com a mensagem /bonus.")
    print(f"/start command received from {user.first_name}")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_data[user.id] = {'stage': 1}
    await context.bot.send_message(chat_id=user.id, text="Primeiramente, AVISO! Todos os passos deste processo têm de ser completados, caso contrario nao irá receber seu bonus, leia tudo com atencao e envie tudo o que é pedido. Já criou conta com o código MFREIRE no registo ou pelo link https://bcgame.top/i-mariofreire-n/?spin=true . Se j«á criou sua conta digite /confirmar para continuar")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Verifique suas mensagens privadas para continuar o processo.")
    print("/bonus command received")

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 1:
        user_data[user.id]['stage'] = 2
        await context.bot.send_message(chat_id=user.id, text="Envie print da tela do seu perfil BC Game, vá no canto superior direito, meu perfil e mande print da tela. (Como no exemplo da print enviada)")
        await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage1.jpg.png?raw=true')
        print("/confirmar command received")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data:
        stage = user_data[user.id]['stage']

        if stage == 2:
            user_data[user.id]['stage'] = 3
            user_data[user.id]['profile_photo_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Verifique sua identidade na BC Game 'nível básico', vá no seu perfil, configurações, verificação e envie print da tela da verificação básica completa. Tem de fazer a verificaçao basica para continuar!")
            await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage2.jpg.png?raw=true')
            print("Profile photo received and stage updated to 3")

        elif stage == 3:
            user_data[user.id]['stage'] = 4
            user_data[user.id]['verification_photo_message_id'] = update.message.message_id
            keyboard = [
                [InlineKeyboardButton("25R$ grátis SEM DEPOSITAR", callback_data='gratis')],
                [InlineKeyboardButton("100R$ extra SE DEPOSITAR 100R$", callback_data='extra')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=user.id, text="Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra.", reply_markup=reply_markup)
            print("Verification photo received and stage updated to 4")

        elif stage == 5:
            user_data[user.id]['stage'] = 6
            user_data[user.id]['deposit_photo_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Último passo, deixe um comentário no vídeo 'https://....' confirmando que recebeu o bônus (não se preocupe, se não receber seu bônus pode simplesmente remover o comentário) e envie a print da tela.")
            await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage3.jpg.png?raw=true')
            print("Deposit photo received and stage updated to 6")

        elif stage == 6:
            user_data[user.id]['stage'] = 7
            user_data[user.id]['comment_confirmation_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Concluído, seu dados agora serao processados e irá receber seu bonus em breve! Aguarde um pouco até aparecer seu bônus na conta. Obrigado")

            # Encaminhar todas as mensagens do usuário para o administrador
            await context.bot.forward_message(chat_id=ADMIN_USER_ID, from_chat_id=user.id, message_id=user_data[user.id]['profile_photo_message_id'])
            await context.bot.forward_message(chat_id=ADMIN_USER_ID, from_chat_id=user.id, message_id=user_data[user.id]['verification_photo_message_id'])
            await context.bot.forward_message(chat_id=ADMIN_USER_ID, from_chat_id=user.id, message_id=user_data[user.id]['deposit_photo_message_id'])
            await context.bot.forward_message(chat_id=ADMIN_USER_ID, from_chat_id=user.id, message_id=user_data[user.id]['comment_confirmation_message_id'])

            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=f"Usuário {user.first_name} completou o processo.")
            print("Comment confirmation received and process completed")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = query.from_user
    if query.data == 'gratis':
        user_data[user.id]['bonus_choice'] = 'gratis'
        await query.edit_message_text(text="Você escolheu receber 25R$ grátis sem depósito. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito. (Envie print como a mostrada no exemplo)")
    elif query.data == 'extra':
        user_data[user.id]['bonus_choice'] = 'extra'
        await query.edit_message_text(text="Você escolheu depositar 100R$ ou mais para receber 100R$ extra. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito. (Envie print como a mostrada no exemplo)")

    user_data[user.id]['stage'] = 5
    await context.bot.send_message(chat_id=user.id, text="Envie o print do depósito para continuar.")
    await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage4.jpg.png?raw=true')
    print(f"Button {query.data} clicked and stage updated to 5")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Olá {member.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na BC Game, mande uma mensagem para @BCGameOferta_bot com a mensagem /bonus.")
        print(f"Welcome message sent to {member.first_name}")

async def periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="Lembre-se, para receber seu bônus inicial, mande uma mensagem para @BCGameOferta_bot com a mensagem /bonus.")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    job_queue = JobQueue()
    job_queue.set_application(application)
    job_queue.run_repeating(periodic_message, interval=120, first=0)  # Envia a mensagem a cada 2 minutos

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("confirmar", confirmar))
    application.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        url_path=TOKEN,
        webhook_url=f"https://telegram-bot-ep12.onrender.com/{TOKEN}"
    )

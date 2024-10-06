import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_USER_ID = 1641003146  # Seu ID de administrador
GROUP_CHAT_ID = -1811495091  # Substitua pelo ID do seu grupo

# Dicionário para armazenar informações dos usuários
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Olá {user.first_name}, seja bem-vindo ao nosso grupo! Para receber o seu bônus exclusivo de 25R$ na BC Game, envie uma mensagem para o bot @BCGameOferta_bot com o comando /bonus. Certifique-se de seguir todos os passos com atenção para garantir o recebimento do bônus.")
    print(f"/start command received from {user.first_name}")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_data[user.id] = {'stage': 1}
    await context.bot.send_message(chat_id=user.id, text="Atenção! Para receber seu bônus de 25R$, é necessário seguir todos os passos corretamente. Caso algum passo não seja completado, o bônus não será liberado.\n\nPrimeiramente, você já criou sua conta na BC Game com o código *MFREIRE* ou pelo link https://bcgame.top/i-mariofreire-n/?spin=true?\n\nSe sim, digite /confirmar para prosseguir.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Por favor, verifique suas mensagens privadas para continuar com o processo.")
    print("/bonus command received")

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 1:
        user_data[user.id]['stage'] = 2
        await context.bot.send_message(chat_id=user.id, text="Perfeito! Agora precisamos que você envie uma captura de tela do seu perfil na BC Game.\n\nVá até o canto superior direito da tela, clique em 'Meu Perfil' e tire uma captura que mostre claramente o seu 'ID do Usuário'.\n\nEnvie a captura de tela aqui para continuar.")
        await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage1.jpg.png?raw=true')
        print("/confirmar command received")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data:
        stage = user_data[user.id]['stage']

        if stage == 2:
            user_data[user.id]['stage'] = 3
            user_data[user.id]['profile_photo_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Agora precisamos que você verifique sua identidade na BC Game.\n\nAcesse o seu perfil, vá até as configurações e clique em 'Verificação'. Por favor, conclua a verificação básica (nível obrigatório) e envie uma captura de tela que mostre que sua verificação foi completada.")
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
            await context.bot.send_message(chat_id=user.id, text="Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra?", reply_markup=reply_markup)
            print("Verification photo received and stage updated to 4")

        elif stage == 5:
            user_data[user.id]['stage'] = 6
            user_data[user.id]['deposit_photo_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Último passo! Por favor, acesse o vídeo do YouTube neste link: [link_do_video].\n\nDeixe um comentário confirmando que você recebeu o bônus de 25R$. Não se preocupe, se algo der errado, você pode remover o comentário depois.\n\nAssim que deixar o comentário, envie uma captura de tela como confirmação.")
            await context.bot.send_photo(chat_id=user.id, photo='https://github.com/mariofreire7708/telegram-bot/blob/main/stage3.jpg.png?raw=true')
            print("Deposit photo received and stage updated to 6")

        elif stage == 6:
            user_data[user.id]['stage'] = 7
            user_data[user.id]['comment_confirmation_message_id'] = update.message.message_id
            await context.bot.send_message(chat_id=user.id, text="Parabéns! Você completou todas as etapas com sucesso. Agora, seus dados estão sendo processados, e você deve receber seu bônus em breve. Aguarde um pouco, e logo ele aparecerá na sua conta. Obrigado por participar!")

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
    print("Periodic message sent")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    
    # Verifique se o job_queue está disponível
    if application.job_queue:
        job_queue = application.job_queue
        job_queue.run_repeating(periodic_message, interval=120, first=0)  # Envia a mensagem a cada 2 minutos
        print("Job queue configured")
    else:
        print("Job queue not available")

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

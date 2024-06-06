import os
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google.cloud import vision
from google.oauth2 import service_account

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Configurar a Google Cloud Vision API
credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Dicionário para armazenar informações dos usuários
user_data = {}

def compare_images(image1_path, image2_path):
    # Função para comparar imagens
    import imagehash
    from PIL import Image

    hash0 = imagehash.average_hash(Image.open(image1_path))
    hash1 = imagehash.average_hash(Image.open(image2_path))

    cutoff = 5  # Limite de diferença permitido
    if hash0 - hash1 < cutoff:
        return True
    else:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Olá {user.first_name}, bem-vindo ao grupo! Se quiser receber o seu bônus inicial na cassino BC Game digite /bonus. Bônus inicial é em Crypto, se não sabe como trabalhar com criptomoedas aconselho a ver algum vídeo no YouTube referente ao mesmo. Bônus não tem nenhum tipo de bloqueio ou rollover, apenas aposte 1 vez e pode sacar.")
    print(f"/start command received from {user.first_name}")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_data[user.id] = {'stage': 1}
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

        example_photo_path = f'stage{stage}.jpg'

        # Use Google Cloud Vision to analyze the photo
        with io.open(photo_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)

        if compare_images(photo_path, example_photo_path):
            if stage == 2:
                user_data[user.id]['stage'] = 3
                user_data[user.id]['profile_photo'] = update.message.photo[-1].file_id
                await context.bot.send_message(chat_id=user.id, text="Verifique sua identidade na BC Game 'nível básico', vá no seu perfil, configurações, verificação e envie print da tela da verificação básica completa.")
                print("Profile photo received and stage updated to 3")

            elif stage == 3:
                user_data[user.id]['stage'] = 4
                user_data[user.id]['verification_photo'] = update.message.photo[-1].file_id
                keyboard = [
                    [InlineKeyboardButton("25R$ grátis", callback_data='gratis')],
                    [InlineKeyboardButton("100R$ extra", callback_data='extra')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(chat_id=user.id, text="4º Você quer receber 25R$ grátis sem depósito ou se depositar 100R$ ou mais recebe 100R$ extra.", reply_markup=reply_markup)
                print("Verification photo received and stage updated to 4")
        else:
            await context.bot.send_message(chat_id=user.id, text="A imagem enviada não é válida. Por favor, envie uma imagem correta.")
            print("Invalid photo received")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = query.from_user
    if query.data == 'gratis':
        user_data[user.id]['bonus_choice'] = 'gratis'
        await query.edit_message_text(text="Você escolheu receber 25R$ grátis sem depósito. Crie um depósito em USDT network BEP20 e mande print da tela com o código QR do depósito.")
    elif query.data == 'extra':
        user_data[user.id]['bonus_choice'] = 'extra'
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

        example_photo_path = 'stage3.jpg'

        if compare_images(photo_path, example_photo_path):
            user_data[user.id]['deposit_photo'] = update.message.photo[-1].file_id
            await context.bot.send_message(chat_id=user.id, text="Último passo, deixe um comentário no vídeo 'https://....' confirmando que recebeu o bônus (não se preocupe, se não receber seu bônus pode simplesmente remover o comentário).")
            user_data[user.id]['stage'] = 6
            print("Deposit photo received and stage updated to 6")
        else:
            await context.bot.send_message(chat_id=user.id, text="A imagem enviada não é válida. Por favor, envie uma imagem correta.")
            print("Invalid deposit photo received")

async def comment_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data and user_data[user.id]['stage'] == 6:
        await context.bot.send_message(chat_id=user.id, text="Concluído, aguarde um pouco até aparecer seu bônus na conta.")
        print("Comment confirmation received and process completed")

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id in user_data:
        data = user_data[user.id]
        msg = f"Dados do usuário {user.first_name}:\n"
        for key, value in data.items():
            if key.endswith('_photo'):
                file = await context.bot.get_file(value)
                photo = io.BytesIO()
                await file.download(out=photo)
                photo.seek(0)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=f"{key.replace('_', ' ').capitalize()}")
            else:
                msg += f"{key.capitalize()}: {value}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Nenhum dado encontrado para este usuário.")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("confirmar", confirmar))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(user_data.keys()), receive_photo))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("consultar", consultar))
    application.add_handler(MessageHandler(filters.PHOTO, receive_deposit_photo))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/comentariodone$'), comment_done))

    application.run_polling()

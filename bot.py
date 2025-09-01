import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os
from dotenv import load_dotenv

# Gestion de l'import imghdr avec fallback
try:
    import imghdr
except ImportError:
    # Si imghdr n'est pas disponible, définir une fonction vide
    def imghdr_what(file):
        return None
    imghdr = type('imghdr', (object,), {'what': imghdr_what})

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Message de soutien
SUPPORT_MESSAGE = (
    "🙏 Soutenez notre mission spirituelle !\n\n"
    "Découvrez notre ebook \"Conseils Spirituels pour Chaque Situation\" "
    "et recevez des guides pratiques pour votre vie spirituelle.\n\n"
    "👉 Cliquez sur le bouton ci-dessous pour accéder à l'ebook."
)

SUPPORT_LINK = "https://cfxgtivu.mychariow.com/prd_ziljzn"

def start(update: Update, context: CallbackContext) -> None:
    """Message de bienvenue avec bouton de soutien"""
    user = update.effective_user
    
    # Créer le bouton de soutien
    keyboard = [[InlineKeyboardButton("📖 Obtenir l'ebook spirituel", url=SUPPORT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f'🙏 Bonjour {user.first_name} !\n\n'
        'Je suis votre Conseiller Spirituel IA.\n\n'
        'Partagez-moi votre préoccupation spirituelle et je vous répondrai avec :\n'
        '• Un verset biblique pertinent\n'
        '• Un conseil spirituel\n'
        '• Une prière personnalisée\n\n'
        'Écrivez simplement votre question ou préoccupation.'
    )
    
    update.message.reply_text(welcome_message)
    
    # Envoyer le message de soutien avec le bouton
    update.message.reply_text(
        SUPPORT_MESSAGE,
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Commande d'aide"""
    help_text = (
        "📚 *Comment utiliser ce bot :*\n\n"
        "1. Envoyez-moi votre préoccupation ou question spirituelle\n"
        "2. Je vous répondrai avec un verset, un conseil et une prière\n"
        "3. Pour recommencer, envoyez une nouvelle question\n\n"
        "Commandes disponibles :\n"
        "/start - Démarrer le bot\n"
        "/help - Afficher l'aide\n"
        "/support - Soutenir notre projet"
    )
    
    update.message.reply_text(help_text, parse_mode='Markdown')

def support_command(update: Update, context: CallbackContext) -> None:
    """Message de soutien"""
    keyboard = [[InlineKeyboardButton("📖 Obtenir l'ebook spirituel", url=SUPPORT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        SUPPORT_MESSAGE,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def get_guidance(concern: str) -> str:
    """Obtenir la guidance spirituelle de l'IA"""
    prompt = f"""
    Tu es un conseiller spirituel chrétien. Réponds avec ce format précis :
    
    1. 📖 *Verset Biblique*
    [Verset pertinent avec référence]
    
    2. 💡 *Conseil Spirituel*
    [Court conseil pour surmonter l'épreuve]
    
    3. 🙏 *Prière Personnalisée*
    [Prière adaptée à la situation]
    
    Préoccupation : "{concern}"
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"😢 Désolé, une erreur est survenue : {str(e)}"

def handle_message(update: Update, context: CallbackContext) -> None:
    """Gérer les messages de l'utilisateur"""
    user_message = update.message.text
    
    # Indiquer que le bot est en train de réfléchir
    typing_msg = update.message.reply_text("💭 Je réfléchis à votre demande...")
    
    try:
        # Obtenir la guidance spirituelle
        guidance = get_guidance(user_message)
        
        # Mettre à jour le message avec la réponse
        typing_msg.edit_text(guidance, parse_mode='Markdown')
        
        # Envoyer le message de soutien après la réponse (30% du temps)
        import random
        if random.random() < 0.3:  # 30% de chance
            keyboard = [[InlineKeyboardButton("📖 Obtenir l'ebook spirituel", url=SUPPORT_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                SUPPORT_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erreur : {e}")
        typing_msg.edit_text("😢 Une erreur est survenue. Veuillez réessayer plus tard.")

def main() -> None:
    """Fonction principale"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN manquant dans les variables d'environnement")
        return
        
    updater = Updater(token)
    dp = updater.dispatcher
    
    # Enregistrer les gestionnaires
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("support", support_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Démarrer le bot
    updater.start_polling()
    logger.info("Bot démarré avec succès!")
    
    # Garder le bot en marche
    updater.idle()

if __name__ == '__main__':
    main()

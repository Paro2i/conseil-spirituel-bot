import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import openai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration des clés API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Vérification des clés API
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY manquant dans les variables d'environnement")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN manquant dans les variables d'environnement")

# Configuration OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Messages constants
SUPPORT_MESSAGE = (
    "🙏 *Soutenez notre mission spirituelle !*\n\n"
    "Découvrez notre ebook exclusif *\"Guide du Jeûne Spirituel\"* qui vous aide à :\n"
    "• Discerner les problèmes nécessitant le jeûne\n"
    "• Pratiquer le jeûne efficacement\n"
    "• Renforcer votre vie spirituelle\n\n"
    "💝 *Prix libre* - Soutenez notre ministère selon vos moyens\n\n"
    "👉 Cliquez sur le bouton ci-dessous pour recevoir votre ebook."
)

SUPPORT_LINK = "https://cfxgtivu.mychariow.com/prd_ziljzn "

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message de bienvenue avec bouton de soutien"""
    user = update.effective_user

    # Créer le bouton de soutien
    keyboard = [[InlineKeyboardButton("📖 Recevoir l'ebook spirituel", url=SUPPORT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        f"🙏 *Bienvenue {user.first_name} !*\n\n"
        "Je suis *ngolu*, votre Conseiller Spirituel IA.\n\n"
        "*Comment puis-je vous aider ?*\n"
        "Partagez-moi votre préoccupation et je vous répondrai avec :\n"
        "• 📖 Un *verset biblique* pertinent\n"
        "• 💡 Un *conseil spirituel* pratique\n"
        "• 🙏 Une *prière personnalisée*\n\n"
        "Écrivez simplement votre question ou préoccupation.\n\n"
        "✨ *Commandes disponibles:*\n"
        "/start - Redémarrer le bot\n"
        "/help - Aide et instructions\n"
        "/support - Soutenir notre projet"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")

    # Envoyer le message de soutien avec le bouton
    await update.message.reply_text(
        SUPPORT_MESSAGE,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande d'aide"""
    help_text = (
        "📚 *Guide d'utilisation de ngolu:*\n\n"
        "1. 💬 *Envoyez-moi* votre préoccupation ou question spirituelle\n"
        "2. ⏳ *Attendez* quelques secondes que je prépare votre réponse\n"
        "3. 📖 *Recevez* un verset biblique, un conseil et une prière personnalisée\n"
        "4. 🔄 *Recommencez* en envoyant une nouvelle question\n\n"
        "✨ *Commandes disponibles:*\n"
        "/start - Démarrer le bot\n"
        "/help - Afficher ce message d'aide\n"
        "/support - Soutenir notre projet\n\n"
        "💡 *Exemples de questions:*\n"
        "• \"Je traverse une période difficile\"\n"
        "• \"J'ai besoin de guidance pour une décision\"\n"
        "• \"Comment surmonter l'anxiété ?\"\n"
        "• \"Prière pour ma famille\""
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message de soutien"""
    keyboard = [[InlineKeyboardButton("📖 Recevoir l'ebook spirituel", url=SUPPORT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        SUPPORT_MESSAGE,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def get_guidance(concern: str) -> str:
    """Obtenir la guidance spirituelle de l'IA"""
    prompt = (
        f"Tu es un conseiller spirituel chrétien expérimenté. Réponds en français avec ce format précis :\n\n"
        "📖 *VERSET BIBLIQUE*\n"
        "[Un verset biblique pertinent avec référence complète]\n\n"
        "💡 *CONSEIL SPIRITUEL*\n"
        "[Un conseil pratique et encourageant pour surmonter cette épreuve, basé sur la samesse chrétienne]\n\n"
        "🙏 *PRIÈRE PERSONNALISÉE*\n"
        "[Une prière adaptée à la situation, qui commence par 'Seigneur' ou 'Père céleste']\n\n"
        f"La préoccupation de l'utilisateur est : \"{concern}\"\n\n"
        "Sois encourageant, compatissant et pertinent. Utilise un langage chaleureux et spirituel."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        return (
            "😢 Désolé, une erreur est survenue lors de la génération de votre guidance spirituelle. "
            "Veuillez réessayer dans quelques moments."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gérer les messages de l'utilisateur"""
    user_message = update.message.text

    # Ignorer les messages trop courts
    if len(user_message.strip()) < 3:
        await update.message.reply_text("❌ Votre message est trop court. Veuillez partager plus de détails pour que je puisse vous aider.")
        return

    # Indiquer que le bot est en train de réfléchir
    typing_msg = await update.message.reply_text("💭 Je prie et réfléchis à votre demande...")

    try:
        # Obtenir la guidance spirituelle
        guidance = get_guidance(user_message)

        # Mettre à jour le message avec la réponse
        await context.bot.edit_message_text(
            chat_id=typing_msg.chat_id,
            message_id=typing_msg.message_id,
            text=guidance,
            parse_mode="Markdown"
        )

        # Envoyer le message de soutien après la réponse (25% du temps)
        if random.random() < 0.25:
            keyboard = [[InlineKeyboardButton("📖 Recevoir l'ebook spirituel", url=SUPPORT_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                SUPPORT_MESSAGE,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.error(f"Erreur: {e}")
        await context.bot.edit_message_text(
            chat_id=typing_msg.chat_id,
            message_id=typing_msg.message_id,
            text="😢 Une erreur est survenue. Veuillez réessayer plus tard."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gérer les erreurs"""
    logger.error(f"Erreur: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

def main() -> None:
    """Fonction principale"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Token Telegram manquant. Veuillez configurer TELEGRAM_BOT_TOKEN.")
        return

    # Créer l'Application avec la nouvelle API
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Enregistrer les gestionnaires
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Gestionnaire d'erreurs
    application.add_error_handler(error_handler)

    # Démarrer le bot
    application.run_polling()
    logger.info("🤖 Bot ngolu démarré avec succès!")

if __name__ == "__main__":
    main()

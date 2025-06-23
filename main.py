import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# 🔐 Charger la config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]

# 💾 Charger l'état du joueur
def load_player():
    with open("data/player.json", "r") as f:
        return json.load(f)

def save_player(data):
    with open("data/player.json", "w") as f:
        json.dump(data, f, indent=2)

# 📜 Charger le dialogue de la succube actuelle
def load_dialogue(name):
    with open(f"dialogues/{name}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 📍 Fonction de démarrage
def start(update: Update, context: CallbackContext):
    player = load_player()
    dialogue = load_dialogue(player["succubus"])
    scene = dialogue["scenes"][0]  # On commence par la première scène

    keyboard = [
        [InlineKeyboardButton(opt["text"], callback_data=str(i))] for i, opt in enumerate(scene["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"{scene['text']}\n\n💖 Énergie : {player['energy']} | 🔥 PS : {player['ps']}",
        reply_markup=reply_markup
    )

# ✅ Quand l'utilisateur clique sur un bouton
def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    player = load_player()
    dialogue = load_dialogue(player["succubus"])
    scene = dialogue["scenes"][0]
    option_index = int(query.data)
    option = scene["options"][option_index]

    # Appliquer les effets
    player["energy"] -= option.get("energy_cost", 0)
    player["ps"] += option.get("ps_gain", 0)

    save_player(player)

    # Répondre
    response = option["response"]
    query.edit_message_text(
        text=f"{response}\n\n💖 Énergie : {player['energy']} | 🔥 PS : {player['ps']}"
    )

# 📩 Réponses libres du joueur
def handle_text(update: Update, context: CallbackContext):
    player = load_player()
    dialogue = load_dialogue(player["succubus"])
    scene = dialogue["scenes"][0]

    update.message.reply_text(
        f"{scene['text']}\n\n💖 Énergie : {player['energy']} | 🔥 PS : {player['ps']}"
    )

# 🧠 Lancer le bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

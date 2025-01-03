import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from data_manager import DataManager
from utils import extract_number_and_sum, setup_logging

# Configuration du logging
setup_logging()

logger = logging.getLogger('Le69iste')

# Chargement des variables d'environnement
load_dotenv()

# Initialisation des intentions et du bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialisation du gestionnaire de données
data_manager = DataManager('data.json')

@tasks.loop(hours=1)
async def update_presence():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"les nombres rigolos sur {len(bot.guilds)} serveurs."))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"les nombres rigolos sur {len(bot.guilds)} serveurs."))
    update_presence.start()
    logger.info(f'Bot {bot.user} connecté à Discord')
    try:
        synced = await bot.tree.sync()
        logger.info(f'{len(synced)} commandes slash synchronisées')
    except Exception as e:
        logger.error(f'Erreur lors de la synchronisation des commandes slash: {e}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    numbers, total = extract_number_and_sum(message.content)
    if total == 69:
        data = data_manager.load_data()
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        config = data_manager.get_guild_config(guild_id)

        # Mettre à jour les statistiques
        data_manager.update_stats(guild_id, user_id, 'count_69')

        logger.info(f"69 trouvé dans le message de {message.author.id} sur {message.guild.id}")

        # Appliquer les configurations
        if config['enable_reactions']:
            reactions = ["6️⃣", "9️⃣", "👀"]
            for emoji in reactions:
                await message.add_reaction(emoji)

        if config['send_message']:
            response = "Génial ! Tous les nombres de votre message s'additionnent à 69 !\n\n"
            response += "```" + " + ".join(map(str, numbers)) + f" = {total}" + "```"
            
            if config['send_public']:
                await message.channel.send(response)
            else:
                try:
                    await message.author.send(response)
                    await message.add_reaction("📨")  # Indique que le message a été envoyé en privé
                except discord.Forbidden:
                    logger.warning(f"Impossible d'envoyer un message privé à {message.author.id}")
                    await message.channel.send(
                        f"{message.author.mention} Je ne peux pas vous envoyer de message privé. "
                        "Vérifiez que vous acceptez les messages privés de ce serveur."
                    )

    await bot.process_commands(message)

# Ajout des commandes slash ici...
# Exemple : leaderboard_server, leaderboard_global, config, set_send_public, set_send_message, set_enable_reactions

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Erreur de commande: {error}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erreur dans l'événement {event}: {args} {kwargs}")

# Récupération du token et démarrage du bot
token = os.getenv('DISCORD_TOKEN')
if token:
    logger.info("Démarrage du bot...")
    bot.run(token)
else:
    logger.critical("Aucun token trouvé dans le fichier .env")
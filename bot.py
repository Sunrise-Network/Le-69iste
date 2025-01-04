import discord
from discord.ext import commands
from discord import app_commands
import datetime
import json
import os
import re
import logging
import asyncio
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DiscordBot')

# Chargement des variables d'environnement
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

DATA_FILE = 'data.json'
DATA_STORAGE = 'json'
START_TIME = datetime.now()
ENVIRONEMENT = os.getenv('ENVIRONEMENT', 'DEVELOPMENT')
CLUSTER = os.getenv('CLUSTER', 'N/A')
SHARD = os.getenv('SHARD', 'N/A')
REGION = os.getenv('REGION', 'N/A')

# Initialisation des intentions et du bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_uptime():
    now = datetime.now()
    delta = now - START_TIME
    days, seconds = delta.days, delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} jours, {hours} heures, {minutes} minutes et {seconds} secondes"

def load_data():
    if DATA_STORAGE == "json":
        try:
            with open(DATA_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    logger.warning("Fichier de données vide, création d'une nouvelle structure")
                    return {"config": {}, "stats": {}, "info": {"cluster": CLUSTER, "shard": SHARD, "region": REGION}}
                data = json.loads(content)
                if "info" not in data:
                    data["info"] = {"cluster": CLUSTER, "shard": SHARD, "region": REGION}
                return data
        except FileNotFoundError:
            logger.warning(f"Fichier {DATA_FILE} non trouvé, création d'une nouvelle structure")
            return {"config": {}, "stats": {}, "info": {"cluster": CLUSTER, "shard": SHARD, "region": REGION}}
        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage JSON dans {DATA_FILE}. Voulez vous créer une nouvelle structure ? Toutes les données du bot serons perdues (O/N)")
            response = input()
            if response.lower() == 'o' or response.lower() == 'oui' or response.lower() == 'y' or response.lower() == 'yes':
                return {"config": {}, "stats": {}, "info": {"cluster": CLUSTER, "shard": SHARD, "region": REGION}}
            else:
                logger.error("Arrêt du bot")
                exit(1)
    elif DATA_STORAGE == "mysql":
        pass

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logger.debug("Données sauvegardées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données: {e}")

def get_guild_config(guild_id: str, data: dict) -> dict:
    if guild_id not in data['config']:
        data['config'][guild_id] = {
            "send_public": True,
            "send_message": True,
            "enable_reactions": True
        }
        save_data(data)
    return data['config'][guild_id]

def extract_number_and_sum(message):
    numbers = list(map(int, re.findall(r'\b\d+\b', message)))
    total = sum(numbers)
    return numbers, total

async def update_presence():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"les nombres rigolos sur {len(bot.guilds)} serveurs."))
        await asyncio.sleep(3600)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"les nombres rigolos sur {len(bot.guilds)} serveurs."))
    asyncio.create_task(update_presence())
    logger.info(f'Bot {bot.user} connecté à Discord')
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synchronisé {len(synced)} commandes slash')
    except Exception as e:
        logger.error(f'Erreur lors de la synchronisation des commandes slash: {e}')

@bot.event
async def on_message(message):
    
    owner = [int(os.getenv('OWNER_ID'))]
    
    if message.author.bot:
        return
    
    if message.content == "+-restart" and message.author.id in owner:
        logger.info("Commande de restart reçue")
        await message.channel.send("Redémarage du bot...")
        await bot.close()
        return

    numbers, total = extract_number_and_sum(message.content)
    if total == 69:
        data = load_data()
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        config = get_guild_config(guild_id, data)

        # Mettre à jour les statistiques
        if guild_id not in data['stats']:
            data['stats'][guild_id] = {}
        if user_id not in data['stats'][guild_id]:
            data['stats'][guild_id][user_id] = {'count_69': 0}
        
        data['stats'][guild_id][user_id]['count_69'] += 1
        save_data(data)

        logger.info(f"69 trouvé dans le message de {message.author.id} sur {message.guild.id}")

        if config['send_message']:
            response = "Génial ! La somme des nombres dans votre message est égale a 69 !\n\n"
            response += "```" + " + ".join(map(str, numbers)) + f" = {total}" + "```"
            
            if config['send_public']:
                await message.channel.send(response)
            else:
                try:
                    await message.author.send(response)
                    await message.add_reaction("📨")  # Indique que le message a été envoyé en privé
                except discord.Forbidden:
                    logger.warning(f"Impossible d'envoyer un message privé à {message.author.id}")
        if config['enable_reactions']:
            reactions = ["6️⃣", "9️⃣", "👀"]
            for emoji in reactions:
                await message.add_reaction(emoji)

    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Renvoie la latence du bot.")
async def ping(ctx):
    logger.info(f"Commande ping utilisée sur {ctx.guild.id}")
    await ctx.send(f"Pong ! Latence: {round(bot.latency * 1000)}ms")

@bot.tree.command(name="info", description="Affiche le cluster, la shard et l'uptime du bot.")
async def info(interaction: discord.Interaction):
    logger.info(f"Commande info utilisée par {interaction.user}")
    data = load_data()
    
    region = data.get("info", {}).get("region", "N/A")
    cluster = data.get("info", {}).get("cluster", "N/A")
    shard = data.get("info", {}).get("shard", "N/A")
    uptime = get_uptime()

    embed = discord.Embed(title="Informations du Bot", color=discord.Color.green())
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Cluster", value=cluster, inline=True)
    embed.add_field(name="Shard", value=shard, inline=True)
    embed.add_field(name="Uptime", value=uptime, inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard_server", description="Affiche le classement des utilisateurs avec le plus de 69 sur ce serveur.")
async def leaderboard_server(interaction: discord.Interaction):
    logger.info(f"Commande leaderboard_server utilisée sur {interaction.guild.id}")
    data = load_data()
    guild_id = str(interaction.guild.id)

    if guild_id not in data['stats']:
        logger.warning(f"Aucune donnée pour le serveur {guild_id}")
        await interaction.response.send_message("Aucune donnée disponible pour ce serveur.")
        return

    leaderboard = sorted(data['stats'][guild_id].items(), key=lambda x: x[1]['count_69'], reverse=True)
    embed = discord.Embed(title="Classement des utilisateurs avec le plus de 69 sur ce serveur", color=discord.Color.blue())

    for user_id, stats in leaderboard[:10]:
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=user.display_name, value=f"{stats['count_69']} fois", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard_global", description="Affiche le classement global des utilisateurs avec le plus de 69.")
async def leaderboard_global(interaction: discord.Interaction):
    logger.info(f"Commande leaderboard_global utilisée par {interaction.user}")
    data = load_data()
    global_stats = {}

    for guild_stats in data['stats'].values():
        for user_id, stats in guild_stats.items():
            if user_id not in global_stats:
                global_stats[user_id] = 0
            global_stats[user_id] += stats['count_69']

    leaderboard = sorted(global_stats.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="Classement global des utilisateurs avec le plus de 69", color=discord.Color.gold())

    for user_id, count in leaderboard[:10]:
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=user.display_name, value=f"{count} fois", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="config", description="Affiche ou configure les paramètres du bot.")
async def config(interaction: discord.Interaction):
    logger.info(f"Commande config utilisée sur {interaction.guild.id}")
    data = load_data()
    guild_id = str(interaction.guild.id)
    config = get_guild_config(guild_id, data)

    embed = discord.Embed(title="Configuration du Bot", color=discord.Color.blue())
    embed.add_field(name="Envoi des messages", value="Public" if config['send_public'] else "Privé", inline=True)
    embed.add_field(name="Envoi des messages activé", value="Oui" if config['send_message'] else "Non", inline=True)
    embed.add_field(name="Réactions activées", value="Oui" if config['enable_reactions'] else "Non", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="set_send_public", description="Configure si les messages doivent être envoyés en public ou en privé.")
@app_commands.describe(send_public="Définir si les messages sont envoyés en public (True) ou en privé (False).")
async def set_send_public(interaction: discord.Interaction, send_public: bool):
    logger.info(f"Modification de send_public à {send_public} sur {interaction.guild.id}")
    data = load_data()
    guild_id = str(interaction.guild.id)
    config = get_guild_config(guild_id, data)
    config['send_public'] = send_public
    save_data(data)
    await interaction.response.send_message(f"Envoi des messages {'public' if send_public else 'privé'} configuré.")

@bot.tree.command(name="set_send_message", description="Active ou désactive l'envoi des messages.")
@app_commands.describe(send_message="Définir si l'envoi des messages est activé (True) ou désactivé (False).")
async def set_send_message(interaction: discord.Interaction, send_message: bool):
    logger.info(f"Modification de send_message à {send_message} sur {interaction.guild.id}")
    data = load_data()
    guild_id = str(interaction.guild.id)
    config = get_guild_config(guild_id, data)
    config['send_message'] = send_message
    save_data(data)
    await interaction.response.send_message(f"Envoi des messages {'activé' if send_message else 'désactivé'}.")

@bot.tree.command(name="set_enable_reactions", description="Active ou désactive les réactions.")
@app_commands.describe(enable_reactions="Activer ou désactiver les réactions (True ou False).")
async def set_enable_reactions(interaction: discord.Interaction, enable_reactions: bool):
    logger.info(f"Modification de enable_reactions à {enable_reactions} sur {interaction.guild.id}")
    data = load_data()
    guild_id = str(interaction.guild.id)
    config = get_guild_config(guild_id, data)
    config['enable_reactions'] = enable_reactions
    save_data(data)
    await interaction.response.send_message(f"Réactions {'activées' if enable_reactions else 'désactivées'}.")

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Erreur de commande: {error}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erreur dans l'événement {event}: {args} {kwargs}")

if len(TOKEN) > 0:
    logger.info("Démarrage du bot...")
    bot.run(TOKEN)
else:
    logger.critical("Aucun token trouvé dans le fichier .env")
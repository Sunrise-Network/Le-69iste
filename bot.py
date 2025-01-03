import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import os

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def extract_number_and_sum(message):
    numbers = list(map(int, re.findall(r'\b\d+\b', message)))
    total = 0
    total += sum(numbers)
    return numbers, total

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les nombres riglos"))
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    numbers, total = extract_number_and_sum(message.content)
    print(f"{numbers}, {total}")
    if total == 69:
        response = "Génial ! Tous les nombres de votre message s'additionnent à 69 !\n\n"
        response += "```"
        response += "\n".join([f"{n} + " for n in numbers])
        response += f"\n= {total}"
        response += "```"
        reactions = ["6️⃣", "9️⃣", "👀"]
        for emoji in reactions:
            await message.add_reaction(emoji)
        await message.channel.send(response)
    
    await bot.process_commands(message)

token = os.getenv('DISCORD_TOKEN')

if token:
    bot.run(token)
else:
    print("No token found in .env file")
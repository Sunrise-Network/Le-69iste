import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import os

load_dotenv()

intents = discord.Intents.default()
intents.message = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def extract_number_and_sum(message):
    numbers = list(map(int, re.findall(r'\b\d+\b', message)))
    total += sum(numbers)
    return numbers, total

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    numbers, total = extract_number_and_sum(message.content)
    if total == 69:
        response = f"Super ! Tous les nombres de votre message s'additionnent à 69 !\n\n"
        response += "```"
        response += "\n".join([f"{n} + " for n in numbers])
        response += f"\n= {total}"
        response += "```"
        await message.channel.send(response)
    
    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
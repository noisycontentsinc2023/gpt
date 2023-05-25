import openai
import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Load your OpenAI and Discord Tokens
TOKEN = os.environ['TOKEN']
OPENAI = os.environ['OPENAI']

CHANNEL_ID = 1111123852546805800  # Replace with your channel id

@bot.event
async def on_ready():
    print('Logged on as', bot.user)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CHANNEL_ID:
        # Here, you would add the code to generate a message from GPT-3.5
        # For now, we'll just respond with "gpt-3.5-turbo".
        response = "gpt-3.5-turbo"
        await message.channel.send(response)

    # This line is needed so the bot can process commands.
    await bot.process_commands(message)

bot.run(TOKEN)

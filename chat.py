import openai
import discord
import os
import asyncio
import datetime
import pytz
import concurrent.futures
from discord.ext import commands

# Load your OpenAI and Discord Tokens
TOKEN = os.environ['TOKEN']
OPENAI = os.environ['OPENAI']
PREFIX = os.environ['PREFIX']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

openai.api_key = OPENAI
CHANNEL_IDS = [1111123852546805800, 1111138777453305967]   # Replace with your channel id

ongoing_conversations = {}

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Only respond in the specified channel
    if message.channel.id not in CHANNEL_IDS:
        return

    # Initialize the conversation if needed
    if message.author.name not in ongoing_conversations:
        ongoing_conversations[message.author.name] = [{"role": "system", "content": "You are a helpful assistant."}]

    # Add the user's message to the conversation
    ongoing_conversations[message.author.name].append({
        "role": "user",
        "content": message.content
    })

    # Generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=ongoing_conversations[message.author.name],
    )

    # Add the bot's response to the conversation
    ongoing_conversations[message.author.name].append({
        "role": "assistant",
        "content": response.choices[0].message['content']
    })

    # Send the response
    await message.channel.send(response.choices[0].message['content'])

# Run the bot
bot.run(TOKEN)

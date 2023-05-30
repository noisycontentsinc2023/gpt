import openai
import discord
import os
import asyncio
import pytz
import concurrent.futures
from datetime import datetime, timedelta
from collections import defaultdict
from discord.ext import commands

# Load your OpenAI and Discord Tokens
TOKEN = os.environ['TOKEN']
OPENAI = os.environ['OPENAI']
PREFIX = os.environ['PREFIX']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

openai.api_key = OPENAI
CHANNEL_IDS = [1111123852546805800, 1111138777453305967]   # Replace with your channel ids

LIMIT_PER_DAY = 5
usage_counts = defaultdict(int)
reset_time = datetime.now(pytz.timezone('Asia/Seoul')).date()
ongoing_conversations = {}

@bot.event
async def on_message(message):
    global reset_time
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Only respond in the specified channel
    if message.channel.id not in CHANNEL_IDS:
        return

    # Reset usage counts if a new day has started
    now = datetime.now(pytz.timezone('Asia/Seoul')).date()
    if now > reset_time:
        usage_counts.clear()
        reset_time = now

    # If the user has reached their limit, let them know
    if usage_counts[message.author.name] >= LIMIT_PER_DAY:
        await message.channel.send(f"{message.author.mention}님 오늘의 사용 가능 횟수 {LIMIT_PER_DAY} 회를 모두 사용하셨어요! 내일 다시 이용해주세요")
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

    # Increment the usage count for this user
    usage_counts[message.author.name] += 1

    # Send the response and remaining counts
    remaining_counts = LIMIT_PER_DAY - usage_counts[message.author.name]
    await message.channel.send(f"{message.author.mention} {response.choices[0].message['content']}\n\n앞으로 {remaining_counts} 회 더 이용 가능하세요! 서버 과부하를 방지하기 위해 하루 5회로 제한되어 있습니다")

# Run the bot
bot.run(TOKEN)

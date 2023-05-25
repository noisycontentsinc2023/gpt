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

user_sessions = {}


user_sessions = {}
user_limits = {}

MAX_USES_PER_DAY = 3
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

def get_korea_date():
    return datetime.datetime.now(pytz.timezone('Asia/Seoul')).date()

async def call_openai_api(session):
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=session,
        max_tokens=1000
    )
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id in CHANNEL_IDS:
        # Initialize a session if there's none
        if message.author.id not in user_sessions:
            user_sessions[message.author.id] = [{"role": "system", "content": "You are a helpful assistant."}]
            
        if message.author.id not in user_limits:
            user_limits[message.author.id] = {"date": get_korea_date(), "count": 0}

        if user_limits[message.author.id]["date"] != get_korea_date():
            user_limits[message.author.id] = {"date": get_korea_date(), "count": 0}

        if user_limits[message.author.id]["count"] >= MAX_USES_PER_DAY:
            embed = discord.Embed(
                title="사용 횟수 초과",
                description=f"{message.author.mention}님 하루 최대 사용 횟수 {MAX_USES_PER_DAY} 가 이미 소진되었습니다",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        else:
            user_limits[message.author.id]["count"] += 1
            
        user_sessions[message.author.id].append({
            "role": "user",
            "content": message.content
        })
        
        # Generate a message from GPT-3.5 in a separate thread
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(executor, call_openai_api, user_sessions[message.author.id])

        # Append AI message to the user's session
        user_sessions[message.author.id].append({
            "role": "assistant",
            "content": response.choices[0].message['content']
        })

        # Create an embed message
        embed = discord.Embed(
            title="ChatGPT Response",
            description=f"{message.author.mention}님의 질문에 대한 답변입니다\n{response.choices[0].message['content']}",
            color=discord.Color.blue()
        )
        remaining_uses = MAX_USES_PER_DAY - user_limits[message.author.id]["count"]
        embed.set_footer(text=f"이 답변은 ChatGPT-4 모델로 작성되었습니다. 남은 사용 횟수: {remaining_uses}")
        await message.channel.send(embed=embed)

    # Process commands after the message event
    await bot.process_commands(message)

bot.run(TOKEN)

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
CHANNEL_IDS = [1111123852546805800, 1111138777453305967, 1115886685725659221]   # 채널 아이디 넣으시고 콤마로 구분하심 됩니다

LIMIT_PER_DAY = 5 # 하루 최대 이용 횟수 
usage_counts = defaultdict(int)
reset_time = datetime.now(pytz.timezone('Asia/Seoul')).date()
ongoing_conversations = {}

@bot.event
async def on_message(message):
    global reset_time
    # 봇 메시지 무시 
    if message.author.bot:
        return

    # 정해진 채널에서만 활성화 
    if message.channel.id not in CHANNEL_IDS:
        return

    # 하루 지나면 초기화 
    now = datetime.now(pytz.timezone('Asia/Seoul')).date()
    if now > reset_time:
        usage_counts.clear()
        reset_time = now

    # 5회 사용 만료시 나올 멘트
    if usage_counts[message.author.name] >= LIMIT_PER_DAY:
        await message.channel.send(f"{message.author.mention}님 오늘의 사용 가능 횟수 {LIMIT_PER_DAY} 회를 모두 사용하셨어요! 내일 다시 이용해주세요")
        return

    if message.author.name not in ongoing_conversations:
        ongoing_conversations[message.author.name] = [{"role": "system", "content": "You are a helpful assistant."}]

    ongoing_conversations[message.author.name].append({
        "role": "user",
        "content": message.content
    })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=ongoing_conversations[message.author.name],
    )

    ongoing_conversations[message.author.name].append({
        "role": "assistant",
        "content": response.choices[0].message['content']
    })

    usage_counts[message.author.name] += 1

    remaining_counts = LIMIT_PER_DAY - usage_counts[message.author.name]
    await message.channel.send(f"{message.author.mention} {response.choices[0].message['content']}\n\n앞으로 {remaining_counts} 회 더 이용 가능하세요! 서버 과부하를 방지하기 위해 하루 5회로 제한되어 있습니다")

# Run the bot
bot.run(TOKEN)

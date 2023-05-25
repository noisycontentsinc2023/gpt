import openai
import discord
import os
import asyncio
import functools
from discord.ext import commands



# Load your OpenAI and Discord Tokens
TOKEN = os.environ['TOKEN']
OPENAI = os.environ['OPENAI']
PREFIX = os.environ['PREFIX']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

openai.api_key = OPENAI
CHANNEL_ID = 1111123852546805800  # Replace with your channel id

user_messages = {}


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CHANNEL_ID:
        # '생각 중입니다' 메시지 보내기
        thinking_message = await message.channel.send(f"{message.author.mention}님의 질문에 대해 생각 중입니다...")

        # 사용자 메시지를 사용자 메시지 목록에 추가
        if message.author.id not in user_messages:
            user_messages[message.author.id] = []
        user_messages[message.author.id].append({
            "role": "user",
            "content": message.content
        })

        # GPT-3.5를 위한 대화 히스토리 생성
        conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."},
        ] + user_messages[message.author.id]

        # GPT-3.5에서 메시지 생성
        loop = asyncio.get_event_loop()
        partial_func = functools.partial(openai.ChatCompletion.create, model="gpt-3.5-turbo")
        response = await loop.run_in_executor(None, partial_func, conversation_history)  # 대화 히스토리를 인수로 전달

        # AI 메시지를 사용자 메시지 목록에 추가
        user_messages[message.author.id].append({
            "role": "assistant",
            "content": response.choices[0].message['content']
        })

        # '생각 중입니다' 메시지 삭제
        await thinking_message.delete()

        # 내장 메시지 생성
        response_text = response.choices[0].message['content']

        # 응답 텍스트가 너무 길면 자르기
        if len(response_text) > 2000:
            response_text = response_text[:1997] + '...'

        # 응답 텍스트를 'utf-8' 코덱을 사용하여 인코딩
        response_text = response_text.encode('utf-8', 'ignore').decode('utf-8')

        embed = discord.Embed(
            title="ChatGPT 응답",
            description=f"{message.author.mention}님의 질문에 대한 답변입니다\n{response_text}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="이 답변은 ChatGPT 3.5 모델로 작성되었습니다")
        await message.channel.send(embed=embed)

    # 메시지 이벤트 이후에 명령어를 처리합니다.
    await bot.process_commands(message)

bot.run(TOKEN)

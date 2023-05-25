import openai
import discord
import os
import asyncio
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


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id in CHANNEL_IDS:
        # Send the 'I'm thinking' message
        thinking_message = await message.channel.send(f"{message.author.mention}님의 질문에 대해 생각하는 중...")

        # Initialize a session if there's none
        if message.author.id not in user_sessions:
            user_sessions[message.author.id] = [{"role": "system", "content": "You are a helpful assistant."}]
            
        user_sessions[message.author.id].append({
            "role": "user",
            "content": message.content
        })

        # Generate a message from GPT-3.5
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_sessions[message.author.id],
        )

        # Append AI message to the user's session
        user_sessions[message.author.id].append({
            "role": "assistant",
            "content": response.choices[0].message['content']
        })

        # Delete the 'I'm thinking' message
        await thinking_message.delete()

        # Create an embed message
        embed = discord.Embed(
            title="ChatGPT Response",
            description=f"{message.author.mention}님의 질문에 대한 답변입니다\n{response.choices[0].message['content']}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="이 답변은 ChatGPT 3.5 모델로 작성되었습니다")
        await message.channel.send(embed=embed)

    # Process commands after the message event
    await bot.process_commands(message)

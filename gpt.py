import openai
import discord
import os
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CHANNEL_ID:
        # Send the 'I'm thinking' message
        thinking_message = await message.channel.send(f"{message.author.mention}님의 질문에 대해 생각하는 중...")

        # Generate a message from GPT-3.5
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.content},
            ],
        )

        # Delete the 'I'm thinking' message
        await thinking_message.delete()

        # Create an embed message
        embed = discord.Embed(
            title="ChatGPT Response",
            description=f"{message.author.mention}님 질문하신\n{response.choices[0].message['content']}\n에 대한 답변입니다",
            color=discord.Color.blue()
        )

        # Send the generated message
        await message.channel.send(embed=embed)

    # Process commands after the message event
    await bot.process_commands(message)

bot.run(TOKEN)

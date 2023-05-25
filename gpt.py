import openai
import discord
import os

# Load your OpenAI and Discord Tokens
TOKEN = os.environ['TOKEN']
OPENAI = os.environ['OPENAI']

CHANNEL_ID = 1111123852546805800  # Replace with your channel id

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id == CHANNEL_ID:
            # Here, you would add the code to generate a message from GPT-3.5
            # For now, we'll just respond with "gpt-3.5-turbo".
            response = "gpt-3.5-turbo"
            await message.channel.send(response)

client = MyClient()
client.run(DISCORD_TOKEN)

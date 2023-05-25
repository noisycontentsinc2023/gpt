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

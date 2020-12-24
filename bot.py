import creds
import discord
from creds import BOT_TOKEN
from discord.ext import commands


client = commands.Bot(command_prefix='i.')

@client.event
async def on_ready():
    print('SparkIEEE is ready!')

client.run(BOT_TOKEN)


import discord
import os

client = discord.Client(intents=discord.Intents.default())

token = os.getenv("DISCORD_TOKEN")

fp = open("seele.png", 'rb')
pfp = fp.read()

@client.event
async def on_ready():
    await client.user.edit(avatar=pfp)
    
client.run(token)
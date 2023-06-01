import discord
import os

client = discord.Client(intents=discord.Intents.default())

token = os.getenv("DISCORD_TOKEN")

fp = open("https://cdn.discordapp.com/attachments/1103408452614762638/1113846928019554354/sele-removebg-preview.png", 'rb')
pfp = fp.read()

@client.event
async def on_ready():
    await client.user.edit(avatar=pfp)
    
client.run(token)
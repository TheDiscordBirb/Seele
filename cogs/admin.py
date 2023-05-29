import discord
from discord.ext import commands

from mongo import get_database


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.admin_roleID = 1101868829317013647
        
        
async def setup(self: commands.Bot):
    await self.add_cog(Admin(self))     
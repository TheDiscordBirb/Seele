import discord
from discord.ext import commands

from utils.buttons import RoleMenuSetupButtons
from mongo import get_database


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.admin_roleID = 1101868829317013647
        
    @commands.command(
        name="give",
        aliases=["g"],
        usage="give",
        description="Allows the owner(s) to give shields to people"
    )
    @commands.guild_only() 
    @commands.is_owner()
    async def give(self, ctx: commands.Context,  amt: int, member: discord.Member = None, ):
        for r in ctx.author.roles():
            ctx.reply(r)
        #db = get_database()["Economy"]
        #db.update_one(
        #    {"_id": member.id},
        #    {"$inc":{"shields": amt}}
        #)
        
        await ctx.reply(f"Successfully given `{member.name}` `{amt}` shields.")
        
        
async def setup(self: commands.Bot):
    await self.add_cog(Admin(self))     
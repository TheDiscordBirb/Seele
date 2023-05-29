import discord
from discord.ext import commands

from mongo import get_database


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.admin_roleID = 1101868829317013647
        
    @commands.command(name="give")
    @commands.guild_only()
    async def give(self, ctx: commands.Context, member: discord.Member = None, amt: int = None):
        if amt is None:
            await ctx.reply(f"Specify amount")
        else:
            if member is None:
                await ctx.reply(f"Specify user")
            else:
                role = discord.utils.get(ctx.guild.roles, id=1101868829317013647)
                if role in ctx.author.roles or ctx.author.id in self.bot.owner_ids:
                    db = get_database()["Economy"]
                    db.update_one(
                        {"_id": member.id},
                        {"$inc":{"shields": amt}}
                    )
                    channel = ctx.guild.get_channel(1112849838812438619)
                    if amt > 0:
                        if amt == 1:
                            await ctx.reply(f"`{ctx.author.name}` gave `{member.name}` `{amt}` shield")
                            await channel.send(f"`{ctx.author.name}` gave `{member.name}` `{amt}` shield")
                        else:
                            await ctx.reply(f"`{ctx.author.name}` gave `{member.name}` `{amt}` shields")
                            await channel.send(f"`{ctx.author.name}` gave `{member.name}` `{amt}` shields")
                    elif amt < 0:
                        if amt == -1:
                            await ctx.reply(f"`{ctx.author.name}` took away `{amt*-1}` shield from `{member.name}`")
                            await channel.send(f"`{ctx.author.name}` took away `{amt*-1}` shield from `{member.name}`")
                        else:
                            await ctx.reply(f"`{ctx.author.name}` took away `{amt*-1}` shields from `{member.name}`")
                            await channel.send(f"`{ctx.author.name}` took away `{amt*-1}` shields from `{member.name}`")
                    
        
        
        
async def setup(self: commands.Bot):
    await self.add_cog(Admin(self))     
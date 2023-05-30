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
        
        if member is None:
            return await ctx.reply("Specify member.")
        if amt is None:
            return await ctx.reply("Specify amount.")
        
        role = discord.utils.get(ctx.guild.roles, id=self.admin_roleID)
        if role in ctx.author.roles or ctx.author.id in self.bot.owner_ids:
            db = get_database()["Economy"]
            db.update_one(
                {"_id": member.id},
                {"$inc":{"shields": amt}}
            )
            shield_text = "shield" if abs(amt) == 1 else "shields"
            channel = ctx.guild.get_channel(1112849838812438619)
            if amt > 0:
                await ctx.reply(f"`{ctx.author.name}` gave `{member.name}` `{abs(amt)}` `{shield_text}`<:Shields_SM:1104809716460310549>")
                await channel.send(f"`{ctx.author.name}` gave `{member.name}` `{abs(amt)}` `{shield_text}`<:Shields_SM:1104809716460310549>")
            elif amt < 0:
                await ctx.reply(f"`{ctx.author.name}` took away `{abs(amt)}` `{shield_text}`<:Shields_SM:1104809716460310549> from `{member.name}`")
                await channel.send(f"`{ctx.author.name}` took away `{abs(amt)}` `{shield_text}`<:Shields_SM:1104809716460310549> from `{member.name}`")
                        
    @give.error
    async def give_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRole):
            return await ctx.reply("You don't have permission to use this command.")
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("Invalid Member.")
        
        
async def setup(self: commands.Bot):
    await self.add_cog(Admin(self))     
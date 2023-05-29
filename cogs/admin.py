import discord
from discord.ext import commands

from mongo import get_database


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="give")
    @commands.has_any_role(1101868829317013647, 1103789020456173630)
    @commands.guild_only()
    async def give(
        self, ctx: commands.Context, member: discord.Member = None, amt: int = None
    ):
        if member is None:
            return await ctx.reply("Specify member.")
        if amt is None:
            return await ctx.reply("Specify amount.")

        shield_text = "shield" if abs(amt) == 1 else "shields"
        shield_verb = "took away" if amt < 0 else "gave"
        amt_abs = abs(amt)

        role = discord.utils.get(ctx.guild.roles, id=1101868829317013647)
        if role in ctx.author.roles or ctx.author.id in self.bot.owner_ids:
            db = get_database()["Economy"]
            db.update_one({"_id": member.id}, {"$inc": {"shields": amt}})

        msg = (
            f"`{ctx.author.name}` {shield_verb} `{amt_abs}` {shield_text}"
            f" from/to `{member.name}`"
        )

        await ctx.send(msg)

    @give.error
    async def give_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRole):
            return await ctx.reply("You don't have permission to use this command.")
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("Invalid Member.")


async def setup(self: commands.Bot):
    await self.add_cog(Admin(self))

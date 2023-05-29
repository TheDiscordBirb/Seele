import discord
from discord.ext import commands

from utils.buttons import RoleMenuSetupButtons
from mongo import get_database


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["rms"])
    @commands.is_owner()
    async def role_menu_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            color=discord.Color.purple(),
            title="Vanity Role Menu",
            description="Here you can create/delete/edit your vanity role.\nRole icon is optional and role color does not require the #, just input the value.",
        )
        embed.add_field(
            name="Creating",
            value="You'll enter the role name, color in hexadecimal format (without the #) and the icon url which is an "
            "image url. (make sure the image link ends with .png for transparent roles)",
        )
        embed.add_field(
            name="Deleting",
            value="Nothing special here, bot will handle the work you just need to press the big red "
            "button.",
        )
        embed.add_field(
            name="Editing",
            value="Rules for when creating also applies here.",
        )
        embed.set_footer(
            text="Only available for nitro boosters and millionaires.",
            icon_url=ctx.me.avatar.url,
        )
        await ctx.send(embed=embed, view=RoleMenuSetupButtons())

    @commands.command(aliases=["re"])
    @commands.is_owner()
    async def reload_extension(self, ctx: commands.Context, ext: str):
        try:
            await self.bot.reload_extension(f"cogs.{ext}")
        except commands.ExtensionNotFound:
            return await ctx.send(f"{ext} is not a valid extension.")
        await ctx.send(f"Reloaded {ext}")

    @commands.command(name="io")
    @commands.is_owner()
    async def is_online(self, ctx: commands.Context):
        return await ctx.send("I'm online.")
    
    @commands.command(name="give")
    @commands.guild_only()
    async def give(self, ctx: commands.Context):
        role = discord.utils.get(ctx.guild.roles, id=1101868829317013647)
        if role in ctx.author.roles() or ctx.author.id == 464417492060733440:
            ctx.reply("Test successful")
        #db = get_database()["Economy"]
        #db.update_one(
        #    {"_id": member.id},
        #    {"$inc":{"shields": amt}}
        #)


async def setup(self: commands.Bot):
    await self.add_cog(Owner(self))

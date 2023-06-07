import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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
    
    @commands.command(name="pfp")
    @commands.is_owner()
    async def pfp(self, ctx: commands.Context):
        fp = open("Seele.png", 'rb')
        pfp = fp.read()
        await self.bot.user.edit(avatar=pfp)
        await ctx.author.send("Successful")
    @pfp.error
    async def pfp_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.author.send(error)
        
async def setup(self: commands.Bot):
    await self.add_cog(Owner(self))

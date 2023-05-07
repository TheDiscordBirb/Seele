import discord
from discord.ext import commands

from utils.buttons import RoleMenuSetupButtons


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["rms"])
    @commands.is_owner()
    async def role_menu_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            color=discord.Color.purple(),
            title="Vanity Role Menu",
            description="Here you can create/delete/edit your vanity role.",
        )
        embed.add_field(
            name="Creating",
            value="You'll enter the role name, color in hexadecimal format and the icon url which is an "
            "image url.",
        )
        embed.add_field(
            name="Deleting",
            value="Nothing special here, bot will handle the work you just need to press the big red "
            "button.",
        )
        embed.add_field(
            name="Editing",
            value="For now, you don't have the option to leave blank or set to none, please fill in what "
            "your current role name/color/icon is if you don't want to change it.",
        )
        embed.set_footer(
            text="Only available for nitro boosters.", icon_url=ctx.me.avatar.url
        )
        await ctx.send(embed=embed, view=RoleMenuSetupButtons())

    @commands.command(aliases=["re"])
    @commands.is_owner()
    async def reload_extension(self, ctx: commands.Context, ext: str):
        await self.bot.reload_extension(f"cogs.{ext}")
        await ctx.send(f"Reloaded {ext}")


async def setup(self: commands.Bot):
    await self.add_cog(Owner(self))

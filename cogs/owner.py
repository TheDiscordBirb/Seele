import discord
from discord.ext import commands
from utils.buttons import RoleMenuSetupButtons


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['rms'])
    @commands.is_owner()
    async def role_menu_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            color=discord.Color.purple(),
            title='Vanity Role Menu',
            description='Here you can create or delete your vanity role.'
        )
        await ctx.send(embed=embed, view=RoleMenuSetupButtons())


async def setup(self: commands.Bot):
    await self.add_cog(Owner(self))

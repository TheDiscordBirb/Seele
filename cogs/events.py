import datetime
import sys
import traceback

from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in DMs.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled.")
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown for {error.retry_after:.2f} seconds."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("This command is owner only.")
        elif isinstance(error, commands.CommandInvokeError):
            print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(
                f"{error.original.__class__.__name__}: {error.original}",
                file=sys.stderr,
            )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Username: {self.bot.user.name}")
        print(f"ID: {str(self.bot.user.id)}")
        if not hasattr(self, "uptime"):
            self.bot.uptime = datetime.datetime.now(datetime.timezone.utc)


async def setup(self: commands.Bot):
    await self.add_cog(Events(self))

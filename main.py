import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Seele(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix=".")
        self.client_id = 1102946905606082670
        self.owner_id = 488699894023061516
        self.token = os.getenv("DISCORD_TOKEN")
        self.remove_command("help")

    async def setup_hook(self):
        for extension in os.listdir("cogs"):
            if extension.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{extension[:-3]}")
                except Exception as e:
                    print(
                        f"Failed to load extension {extension[:-3]}\n{type(e).__name__}: {e}"
                    )
        await self.tree.sync()
        # Add views here to be persistent

    def run(self):
        super().run(self.token, reconnect=True)


Seele = Seele()


# Context menus goes here
@Seele.tree.context_menu(name="Avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(color=discord.Color.random(), title=f"{member.name}'s Avatar")
    embed.set_image(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    Seele.run()

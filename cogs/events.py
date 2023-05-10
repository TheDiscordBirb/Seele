import sys
import traceback

import discord
from discord.ext import commands

from mongo import get_database


class Events(commands.Cog):
    cooldowns = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        try:
            raise error
        except commands.NoPrivateMessage:
            await ctx.author.send("This command cannot be used in DMs.")
        except commands.DisabledCommand:
            await ctx.send("This command is disabled.")
        except commands.CommandNotFound:
            return
        except commands.CommandOnCooldown as e:
            await ctx.send(
                f"This command is on cooldown for {e.retry_after:.2f} seconds."
            )
        except commands.MissingPermissions:
            await ctx.send("You do not have permission to use this command.")
        except commands.NotOwner:
            await ctx.send("This command is owner only.")
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Username: {self.bot.user.name}")
        print(f"ID: {str(self.bot.user.id)}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        db = get_database()
        shields = db["Shields"]
        if (
            message.author.bot
            or message.author == self.bot.user
            or message.channel.id
            in [
                1103879081273073674,
                1103879350719356948,
                1105189907166662686,
                1102599564705411142,
            ]
            or message.guild.get_role(1102951068599590912) not in message.author.roles
        ):
            return

        if message.author.id in self.cooldowns:
            remaining_time = (
                self.cooldowns[message.author.id] - message.created_at.timestamp()
            )
            if remaining_time > 0:
                return
        self.cooldowns[message.author.id] = message.created_at.timestamp() + 20
        player = shields.find_one({"_id": message.author.id})
        if player is not None:
            member = message.guild.get_member(message.author.id)
            nitro_role = message.guild.get_role(1102939433038254091)
            if nitro_role in member.roles:
                shields.find_one_and_update(
                    {"_id": message.author.id},
                    {"$inc": {"Shields": 8}},
                )
            else:
                shields.find_one_and_update(
                    {"_id": message.author.id},
                    {"$inc": {"Shields": 5}},
                )
        else:
            shields.insert_one(
                {"_id": message.author.id, "Shields": 5, "inventory": []}
            )


async def setup(self: commands.Bot):
    await self.add_cog(Events(self))

import datetime
import sys
import traceback

import discord
import humanize
from discord.ext import commands

from mongo import get_database


class Events(commands.Cog):
    cooldowns = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        try:
            raise error
        except commands.CommandNotFound:
            return
        except commands.CommandOnCooldown:
            return
        except commands.NoPrivateMessage:
            await ctx.author.send("This command cannot be used in DMs.")
        except commands.DisabledCommand:
            await ctx.send("This command is disabled.")
        except commands.NotOwner:
            await ctx.send("This command is owner only.")
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Username: {self.bot.user.name}")
        print(f"ID: {str(self.bot.user.id)}")
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Bronya sleep"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        db = get_database()["Economy"]
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
        ):
            return

        if message.author.id in self.cooldowns:
            remaining_time = (
                self.cooldowns[message.author.id] - message.created_at.timestamp()
            )
            if remaining_time > 0:
                return
        self.cooldowns[message.author.id] = message.created_at.timestamp() + 20
        player = db.find_one({"_id": message.author.id})
        if player is not None:
            member = message.guild.get_member(message.author.id)
            nitro_role = message.guild.get_role(1102939433038254091)
            if nitro_role in member.roles:
                db.find_one_and_update(
                    {"_id": message.author.id},
                    {"$inc": {"shields": 8}},
                )
            else:
                db.find_one_and_update(
                    {"_id": message.author.id},
                    {"$inc": {"shields": 5}},
                )
        else:
            db.find_one_and_update(
                {
                    "_id": message.author.id,
                },
                {
                    "$set": {
                        "shields": 5,
                        "tool-inventory": [],
                        "role-inventory": [],
                    }
                },
                upsert=True,
            )


async def setup(self: commands.Bot):
    await self.add_cog(Events(self))

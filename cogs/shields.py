import datetime as time

import discord
import humanize
from discord.ext import commands
from pymongo import ReturnDocument

from mongo import get_database


class Shields(commands.Cog):
    role_shop = {
        "fly": {
            "_id": 1105147030390702150,
            "name": "Seele's Butterfly",
            "price": 1000,
            "code": "fly",
        },
        "bf": {
            "_id": 1105147040159236096,
            "name": "Seele's BF",
            "price": 5000,
            "code": "bf",
        },
        "gf": {
            "_id": 1105147075571752961,
            "name": "Seele's GF",
            "price": 5000,
            "code": "gf",
        },
        "husband": {
            "_id": 1105147078629412904,
            "name": "Seele's Husband",
            "price": 15000,
            "code": "husband",
        },
        "wife": {
            "_id": 1105147080936280145,
            "name": "Seele's Wife",
            "price": 15000,
            "code": "wife",
        },
        "wq": {
            "_id": 1105147083830337556,
            "name": "Wildfire Queen",
            "price": 50000,
            "code": "wq",
        },
        "leader": {
            "_id": 1105147086200119418,
            "name": "Underworld Leader",
            "price": 100000,
            "code": "leader",
        },
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="balance", description="Check your Shield balance."
    )
    async def balance(self, interaction: discord.Interaction):
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": interaction.user.id})
        if player is None:
            player = shields.find_one_and_update(
                {"_id": interaction.user.id},
                {"$set": {"Shields": 0, "inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            await interaction.response.send_message(
                f"You currently have {player['Shields']}<:Shields_SM:1104809716460310549>."
            )
        else:
            await interaction.response.send_message(
                f"You currently have {player['Shields']}<:Shields_SM:1104809716460310549>."
            )

    @discord.app_commands.command(name="daily", description="Claim your daily shields.")
    @discord.app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction):
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one_and_update(
            {"_id": interaction.user.id},
            {"$inc": {"Shields": 100}, "$setOnInsert": {"inventory": []}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        await interaction.response.send_message(
            f"You claimed your daily 100<:Shields_SM:1104809716460310549>.\n"
            f"New Balance: {player['Shields']}<:Shields_SM:1104809716460310549>"
        )

    @daily.error
    async def daily_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.CommandOnCooldown):
            delta = time.timedelta(seconds=error.retry_after)
            remaining_cooldown = humanize.precisedelta(delta)

            await interaction.response.send_message(
                f"Try again in {remaining_cooldown}",
                ephemeral=True,
            )
        else:
            print(error)

    @discord.app_commands.command(
        name="shop", description="A shop containing various roles."
    )
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Role Shop", color=discord.Color.purple())
        for role in self.role_shop.values():
            embed.add_field(
                name=f"{role['name']}",
                value=f"{role['price']}<:Shields_SM:1104809716460310549> code: `{role['code']}`",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="inventory", description="Shows what you have in your inventory."
    )
    async def inventory(self, interaction: discord.Interaction):
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": interaction.user.id})

        if not player or not player["inventory"]:
            return await interaction.response.send_message(
                "Your inventory is empty.", ephemeral=True
            )

        embed = discord.Embed(title="Inventory", color=discord.Color.purple())

        for data in player["inventory"]:
            for key, value in self.role_shop.items():
                if key in data:
                    embed.add_field(
                        name=value["name"], value=f'code: `{value["code"]}`'
                    )

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="buy", description="Buy out a role from the shop."
    )
    @discord.app_commands.describe(code="The code of the role you want to buy.")
    async def buy(self, interaction: discord.Interaction, code: str):
        db = get_database()
        shields = db["Shields"]
        role = self.role_shop.get(code)
        player = shields.find_one({"_id": interaction.user.id})

        if not role:
            return await interaction.response.send_message(
                f"Please input correct role code.", ephemeral=True
            )

        inventory = [
            data
            for data in player["inventory"]
            if any(k in data for k in self.role_shop)
        ]
        if inventory:
            return await interaction.response.send_message(
                f"You already own {role['name']}."
            )

        if player["Shields"] < role["price"]:
            return await interaction.response.send_message(
                f"You can't afford {role['name']}."
            )

        shields.update_one(
            {"_id": interaction.user.id},
            {
                "$inc": {"Shields": -role["price"]},
                "$push": {"inventory": {f"{role['code']}": role}},
            },
        )

        await interaction.response.send_message(
            f"You've purchased {role['name']} for {role['price']}<:Shields_SM:1104809716460310549>."
        )

    @discord.app_commands.command(
        name="equip_role", description="Equip a role you own."
    )
    @discord.app_commands.describe(code="The code of the role you want to equip.")
    async def equip_role(self, interaction: discord.Interaction, code: str):
        role_data = self.role_shop.get(code)
        if not role_data:
            return await interaction.response.send_message(
                f"Please input correct role code.", ephemeral=True
            )
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one({"_id": interaction.user.id})

        has_role = any(role[code]["code"] == code for role in player["inventory"])
        if not has_role:
            return await interaction.response.send_message(
                f"You don't have {role_data['name']}.", ephemeral=True
            )
        role = discord.utils.get(interaction.guild.roles, id=role_data["_id"])
        if role in interaction.user.roles:
            return await interaction.response.send_message(
                f"You already have {role.name} equipped.", ephemeral=True
            )
        await interaction.user.add_roles(role)
        return await interaction.response.send_message(
            f"Successfully equipped {role_data['name']}.", ephemeral=True
        )


async def setup(self: commands.Bot):
    await self.add_cog(Shields(self))

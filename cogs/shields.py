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
            "price": 10000,
            "code": "fly",
        },
        "bf": {
            "_id": 1105147040159236096,
            "name": "Seele's BF",
            "price": 25000,
            "code": "bf",
        },
        "gf": {
            "_id": 1105147075571752961,
            "name": "Seele's GF",
            "price": 25000,
            "code": "gf",
        },
        "husband": {
            "_id": 1105147078629412904,
            "name": "Seele's Husband",
            "price": 50000,
            "code": "husband",
        },
        "wife": {
            "_id": 1105147080936280145,
            "name": "Seele's Wife",
            "price": 50000,
            "code": "wife",
        },
        "wq": {
            "_id": 1105147083830337556,
            "name": "Wildfire Queen",
            "price": 250000,
            "code": "wq",
        },
        "leader": {
            "_id": 1105147086200119418,
            "name": "Underworld Leader",
            "price": 500000,
            "code": "leader",
        },
        "custom": {
            "_id": 1105238296197595187,
            "name": "Custom Role of your choice.",
            "price": 10000000,
            "code": "custom",
        },
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="balance", description="Check your Shield balance."
    )
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer()
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": interaction.user.id})
        if player is None:
            player = shields.find_one_and_update(
                {"_id": interaction.user.id},
                {"$set": {"Shields": 0, "inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        await interaction.followup.send(
            f"You currently have {humanize.intcomma(player.get('Shields', 0))}<:Shields_SM:1104809716460310549>."
        )

    @discord.app_commands.command(
        name="shop", description="A shop containing various roles."
    )
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="Role Shop", color=discord.Color.purple())
        for role in self.role_shop.values():
            embed.add_field(
                name=f"{role['name']}",
                value=f"{humanize.intcomma(role.get('price', 0))}<:Shields_SM:1104809716460310549> code: `{role['code']}`\nPreview: {interaction.guild.get_role(role['_id']).mention}",
                inline=False,
            )
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="inventory", description="Shows what you have in your inventory."
    )
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": interaction.user.id})

        if not player or not player["inventory"]:
            return await interaction.followup.send(
                "Your inventory is empty.", ephemeral=True
            )

        embed = discord.Embed(title="Inventory", color=discord.Color.purple())

        for data in player["inventory"]:
            for key, value in self.role_shop.items():
                if key in data:
                    embed.add_field(
                        name=value["name"],
                        value=f"code: `{value['code']}`\nPreview: {interaction.guild.get_role(value['_id']).mention}",
                    )

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="buy", description="Buy out a role from the shop."
    )
    @discord.app_commands.describe(code="The code of the role you want to buy.")
    async def buy(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()
        db = get_database()
        shields = db["Shields"]
        role = self.role_shop.get(code)
        player = shields.find_one({"_id": interaction.user.id})

        if not role:
            return await interaction.followup.send(
                "Please input correct role code.", ephemeral=True
            )

        if inventory := [
            data
            for data in player["inventory"]
            if any(role in data for role in self.role_shop)
        ]:
            return await interaction.followup.send(
                f"You already own {role['name']}.", ephemeral=True
            )

        if player["Shields"] < role["price"]:
            return await interaction.followup.send(
                f"You can't afford {role['name']}.", ephemeral=True
            )

        shields.update_one(
            {"_id": interaction.user.id},
            {
                "$inc": {"Shields": -role["price"]},
                "$push": {"inventory": {f"{role['code']}": role}},
            },
        )

        await interaction.followup.send(
            f"You've purchased {role['name']} for {humanize.intcomma(role.get('price', 0))}<:Shields_SM:1104809716460310549>.",
            ephemeral=True,
        )

    @discord.app_commands.command(name="equip", description="Equip a role you own.")
    @discord.app_commands.describe(code="The code of the role you want to equip.")
    async def equip(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()
        role_data = self.role_shop.get(code)
        if not role_data:
            return await interaction.followup.send(
                "Please input correct role code.", ephemeral=True
            )
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one({"_id": interaction.user.id})

        has_role = any(role[code]["code"] == code for role in player["inventory"])
        if not has_role:
            return await interaction.followup.send(
                f"You don't have {role_data['name']}.", ephemeral=True
            )
        role = discord.utils.get(interaction.guild.roles, id=role_data["_id"])
        if role.id == 1105238296197595187:
            return await interaction.followup.send(
                "Please ping a staff member to redeem your custom role of your choice.",
                ephemeral=True,
            )
        if role in interaction.user.roles:
            return await interaction.followup.send(
                f"You already have {role.name} equipped.", ephemeral=True
            )
        await interaction.user.add_roles(role)
        await interaction.followup.send(
            f"Successfully equipped {role_data['name']}.", ephemeral=True
        )

    @discord.app_commands.command(name="unequip", description="Unequip a role you own.")
    @discord.app_commands.describe(code="The code of the role you want to unequip.")
    async def unequip(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()
        role_data = self.role_shop.get(code)
        if not role_data:
            return await interaction.followup.send(
                "Please input correct role code.", ephemeral=True
            )
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one({"_id": interaction.user.id})

        has_role = any(role[code]["code"] == code for role in player["inventory"])
        if not has_role:
            return await interaction.followup.send(
                f"You don't have {role_data['name']}.", ephemeral=True
            )
        role = discord.utils.get(interaction.guild.roles, id=role_data["_id"])
        if role not in interaction.user.roles:
            return await interaction.followup.send(
                f"You don't have {role.name} equipped.", ephemeral=True
            )
        await interaction.user.remove_roles(role)
        return await interaction.followup.send(
            f"Successfully unequipped {role_data['name']}.", ephemeral=True
        )


async def setup(self: commands.Bot):
    await self.add_cog(Shields(self))

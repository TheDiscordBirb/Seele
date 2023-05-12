import math
import random
import discord
import humanize
from discord.ext import commands
from pymongo import ReturnDocument
import datetime

import pymongo
from mongo import get_database


def gamba_cooldown(ctx: commands.Context):
    member_roles = [role.id for role in ctx.author.roles]
    if 1102939433038254091 in member_roles:
        return commands.Cooldown(5, 3600)
    return commands.Cooldown(3, 3600)


class Economy(commands.Cog):
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
            "price": 100000,
            "code": "wq",
        },
        "leader": {
            "_id": 1105147086200119418,
            "name": "Underworld Leader",
            "price": 250000,
            "code": "leader",
        },
        "custom": {
            "_id": 1105238296197595187,
            "name": "Custom Role of your choice.",
            "price": 1000000,
            "code": "custom",
        },
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="balance",
        aliases=["bal"],
        description="Check your balance.",
        usage="balance",
    )
    async def balance(self, ctx: commands.Context):
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": ctx.author.id})
        if player is None:
            player = shields.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"Shields": 0, "inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        await ctx.reply(
            f"You currently have {humanize.intcomma(math.floor(player.get('Shields', 0)))}<:Shields_SM:1104809716460310549>."
        )

    @commands.command(
        name="shop",
        description="See what's in the shop.",
        usage="shop",
    )
    async def shop(self, ctx: commands.Context):
        embed = discord.Embed(title="Role Shop", color=discord.Color.purple())
        for role in self.role_shop.values():
            embed.add_field(
                name=f"{role['name']}",
                value=f"{humanize.intcomma(role.get('price', 0))}<:Shields_SM:1104809716460310549> code: `{role['code']}`\nPreview: {ctx.guild.get_role(role['_id']).mention}",
                inline=False,
            )
        await ctx.reply(embed=embed)

    @commands.command(
        name="inventory",
        aliases=["inv"],
        description="See what's in your inventory.",
        usage="inventory",
    )
    async def inventory(self, ctx: commands.Context):
        shields = get_database()["Shields"]
        player = shields.find_one({"_id": ctx.author.id})

        if not player or not player["inventory"]:
            return await ctx.reply("Your inventory is empty.", ephemeral=True)

        embed = discord.Embed(title="Inventory", color=discord.Color.purple())

        for data in player["inventory"]:
            for key, value in self.role_shop.items():
                if key in data:
                    embed.add_field(
                        name=value["name"],
                        value=f"code: `{value['code']}`\nPreview: {ctx.guild.get_role(value['_id']).mention}",
                    )

        await ctx.reply(embed=embed)

    @commands.command(
        name="buy",
        description="Buy something from the shop.",
        usage="buy (item code)",
    )
    async def buy(self, ctx: commands.Context, code: str):
        db = get_database()
        shields = db["Shields"]
        role = self.role_shop.get(code)
        player = shields.find_one({"_id": ctx.author.id})

        if not role:
            return await ctx.reply("Please input correct role code.", ephemeral=True)

        if inventory := [
            data
            for data in player["inventory"]
            if any(role in data for role in self.role_shop)
        ]:
            return await ctx.reply(f"You already own {role['name']}.", ephemeral=True)

        if player["Shields"] < role["price"]:
            return await ctx.reply(f"You can't afford {role['name']}.", ephemeral=True)

        shields.update_one(
            {"_id": ctx.author.id},
            {
                "$inc": {"Shields": -role["price"]},
                "$push": {"inventory": {f"{role['code']}": role}},
            },
        )

        await ctx.reply(
            f"You've purchased {role['name']} for {humanize.intcomma(role.get('price', 0))}<:Shields_SM:1104809716460310549>.",
            ephemeral=True,
        )

    @commands.command(
        name="equip", description="Equip an item you own.", usage="equip (item code)"
    )
    async def equip(self, ctx: commands.Context, code: str):
        role_data = self.role_shop.get(code)
        if not role_data:
            return await ctx.reply("Please input correct role code.", ephemeral=True)
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one({"_id": ctx.author.id})

        has_role = any(role[code]["code"] == code for role in player["inventory"])
        if not has_role:
            return await ctx.reply(
                f"You don't have {role_data['name']}.", ephemeral=True
            )
        role = discord.utils.get(ctx.guild.roles, id=role_data["_id"])
        if role.id == 1105238296197595187:
            return await ctx.reply(
                "Please ping a staff member to redeem your custom role of your choice.",
                ephemeral=True,
            )
        if role in ctx.user.roles:
            return await ctx.reply(
                f"You already have {role.name} equipped.", ephemeral=True
            )
        await ctx.author.add_roles(role)
        await ctx.reply(f"Successfully equipped {role_data['name']}.", ephemeral=True)

    @commands.command(
        name="unequip",
        description="Unequip an equipped item.",
        usage="unequip (item code)",
    )
    async def unequip(self, ctx: commands.Context, code: str):
        role_data = self.role_shop.get(code)
        if not role_data:
            return await ctx.reply("Please input correct role code.", ephemeral=True)
        db = get_database()
        shields = db["Shields"]
        player = shields.find_one({"_id": ctx.author.id})

        has_role = any(role[code]["code"] == code for role in player["inventory"])
        if not has_role:
            return await ctx.reply(
                f"You don't have {role_data['name']}.", ephemeral=True
            )
        role = discord.utils.get(ctx.guild.roles, id=role_data["_id"])
        if role not in ctx.author.roles:
            return await ctx.reply(
                f"You don't have {role.name} equipped.", ephemeral=True
            )
        await ctx.author.remove_roles(role)
        return await ctx.reply(
            f"Successfully unequipped {role_data['name']}.", ephemeral=True
        )

    @commands.command(
        name="leaderboard",
        aliases=["lb"],
        usage="leaderboard",
        description="See leaderboard of the most shields owned.",
    )
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context):
        db = get_database()["Shields"]

        top_10 = db.find().sort("Shields", pymongo.DESCENDING).limit(10)

        desc = "".join(
            f"**{i}**-) {ctx.guild.get_member(shield['_id']).name}: {math.floor(shield['Shields'])}<:Shields_SM:1104809716460310549>\n"
            for i, shield in enumerate(top_10, 1)
        )
        embed = discord.Embed(
            title="Top 10 Shields [Current]",
            description=desc,
            color=discord.Color.purple(),
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="daily", description="Claim your daily shields.", usage="daily"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        db = get_database()["Shields"]
        daily_earnings = 200
        member_roles = [role.id for role in ctx.author.roles]
        multiplier = 1.6 if 1102939433038254091 in member_roles else 1
        db.find_one_and_update(
            {"_id": ctx.author.id},
            {"$inc": {"Shields": math.floor(daily_earnings * multiplier)}},
            upsert=True,
        )
        await ctx.reply(
            f"You've redeemed your daily {math.floor(daily_earnings * multiplier)}<:Shields_SM:1104809716460310549>\n"
        )

    @daily.error
    async def daily_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_end = datetime.datetime.now() + datetime.timedelta(
                seconds=error.retry_after
            )
            cooldown = math.floor(cooldown_end.timestamp())
            await ctx.reply(
                f"You already claimed your daily!\nYou can claim your next daily <t:{cooldown}:R>."
            )

    @commands.command(name="work", description="Work for shields.", usage="work")
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def work(self, ctx: commands.Context):
        db = get_database()["Shields"]
        earnings = random.randint(25, 100)
        responses = [
            "As you work hard to keep the streets of Boulder Town clean, you earn {}. Your efforts are appreciated, keep it up!",
            "The citizens of Boulder Town depend on hardworking folks like you to keep the town running smoothly. Enjoy {} for your efforts!",
            "Your contribution to the community of Boulder Town has not gone unnoticed. You've earned {} for your hard work!",
            "Your dedication to maintaining Boulder Town's infrastructure is admirable. Enjoy a reward of {} for your exceptional work!",
            "You've proven yourself to be an essential member of the Boulder Town community. Take {} as a token of appreciation for your valuable work!",
            "The people of Boulder Town are grateful for your service. Receive {} as a thank you for your hard work!",
            "Your efforts in keeping Boulder Town safe and secure are greatly appreciated. Enjoy a reward of {} for your outstanding performance!",
            "By working diligently to make Boulder Town a better place, you've earned {}. Keep up the good work!",
            "Your commitment to the community of Boulder Town is commendable. Take {} as a gesture of appreciation for your hard work!",
            "Hey, you're about to fall asleep on your feet. Don't push yourself — I got this. Go get some rest. Earned {}",
            "Way to go! You're a valuable asset to Boulder Town's economy! You earned {}",
        ]
        member_roles = [role.id for role in ctx.author.roles]
        multiplier = 1.6 if 1102939433038254091 in member_roles else 1
        db.find_one_and_update(
            {"_id": ctx.author.id},
            {"$inc": {"Shields": earnings * multiplier}},
            return_document=ReturnDocument.AFTER,
        )
        response = random.choice(responses)
        reply = response.replace(
            "{}",
            f"{math.floor(earnings * multiplier)}<:Shields_SM:1104809716460310549>",
        )
        await ctx.reply(reply)

    @work.error
    async def work_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_end = datetime.datetime.now() + datetime.timedelta(
                seconds=error.retry_after
            )
            cooldown = math.floor(cooldown_end.timestamp())
            await ctx.reply(
                f"You are tired of working.\nYou can start working again <t:{cooldown}:R>."
            )

    @commands.command(
        name="gamba",
        description="Gamble your money in, win 2x or lose 1x.",
        usage="gamba (amount)",
    )
    @commands.dynamic_cooldown(gamba_cooldown, commands.BucketType.user)
    async def gamba(self, ctx: commands.Context, amount: int = 10):
        db = get_database()["Shields"]
        document = db.find_one({"_id": ctx.author.id})

        if document is None:
            self.gamba.reset_cooldown(ctx)
            return await ctx.reply("You should earn some shields first.")

        if not 10 <= amount <= 500:
            self.gamba.reset_cooldown(ctx)
            return await ctx.reply(
                "You can only bet between 10 and 500 <:Shields_SM:1104809716460310549>."
            )

        user_shields = document.get("Shields", 0)
        if amount > user_shields:
            return await ctx.reply("You can't afford to gamble.")

        chance = random.choice([True, False])

        shields_multiplier = 1 if chance else -1

        db.find_one_and_update(
            {"_id": ctx.author.id}, {"$inc": {"Shields": amount * shields_multiplier}}
        )

        if chance:
            await ctx.reply(
                f"You won the bet, earned {amount * shields_multiplier}<:Shields_SM:1104809716460310549>!"
            )
        else:
            await ctx.reply("You lost the bet.")

    @gamba.error
    async def gamba_cooldown_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_end = datetime.datetime.now() + datetime.timedelta(
                seconds=error.retry_after
            )
            cooldown = math.floor(cooldown_end.timestamp())
            await ctx.reply(
                f"You have used up all your hourly gambas!\nThey will refill <t:{cooldown}:R>."
            )


async def setup(self: commands.Bot):
    await self.add_cog(Economy(self))

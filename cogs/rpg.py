import datetime
import math
import random
import discord
from discord.ext import commands
import humanize
from pymongo import ReturnDocument

from mongo import get_database


def gamba_cooldown(ctx: commands.Context):
    member_roles = [role.id for role in ctx.author.roles]
    if 1102939433038254091 in member_roles:
        return commands.Cooldown(5, 3600)
    return commands.Cooldown(3, 3600)


class RPG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tools = {
        "pick": {"name": "Pickaxe ⛏️", "price": 500, "code": "pick"},
        "rod": {"name": "Fishing Rod 🎣", "price": 500, "code": "rod"},
    }

    roles = {
        "fly": {
            "_id": 1105147030390702150,
            "name": "Seele's Butterfly",
            "price": 10000,
            "code": "fly",
        },
        "bf": {
            "_id": 1108101416125464616,
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

    @commands.command(
        name="balance",
        aliases=["bal"],
        usage="balance",
        description="Check your balance.",
    )
    @commands.guild_only()
    async def balance(self, ctx: commands.Context):
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        await ctx.reply(
            f"You have {humanize.intcomma(round(user.get('shields', 0)))}<:Shields_SM:1104809716460310549> in your account."
        )
        
    #@commands.command(
    #    name="balance_top",
    #    aliases=["bal_top"],
    #    usage="balance_top",
    #    description="Check the top 10 balance.",
    #)
    #@commands.guild_only()
    #async def balance_top(self, ctx: commands.Context):
    #    db = get_database()["Economy"]
    #    for user in db.find():
    #        ctx.author.dm_channel.send(user)
        #user = db.find_one({"_id": ctx.author.id})
        #if user is None:
        #    user = db.find_one_and_update(
        #        {"_id": ctx.author.id},
        #        {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
        #        upsert=True,
        #        return_document=ReturnDocument.AFTER,
        #    )
        #await ctx.reply(
        #    f"You have {humanize.intcomma(round(user.get('shields', 0)))}<:Shields_SM:1104809716460310549> in your account."
        #)

    @commands.command(
        name="profile",
        aliases=["p"],
        usage="profile [member]",
        description="Shows your/someone's profile.",
    )
    @commands.guild_only()
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        db = get_database()["Economy"]
        user = db.find_one({"_id": member.id if member else ctx.author.id})
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        embed = discord.Embed(
            title=f"{ctx.guild.get_member(user.get('_id')).name}'s Profile",
            description=f"**Balance**: {humanize.intcomma(user.get('shields', 0))}<:Shields_SM:1104809716460310549>",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        tool_inventory = user.get("tool-inventory", [])
        role_inventory = user.get("role-inventory", [])
        tool_list = ""
        for tool in tool_inventory:
            for k, v in self.tools.items():
                if k in tool:
                    tool_list += f"{v.get('name')}\n"
        embed.add_field(name="Tool Inventory ⚒️", value=tool_list)
        role_list = ""
        for role in role_inventory:
            for k, v in self.roles.items():
                if k in role:
                    role_list += f"{ctx.guild.get_role(v.get('_id')).mention}\n"
        embed.add_field(name="Role Inventory ✨", value=role_list)
        await ctx.reply(embed=embed)

    @commands.command(
        name="toolshop",
        aliases=["tshop", "ts"],
        usage="toolshop",
        description="See tool shop for jobs.",
    )
    @commands.guild_only()
    async def tool_shop(self, ctx: commands.Context):
        _description = "\n".join(
            f"{details.get('name')}: {details.get('price')}<:Shields_SM:1104809716460310549>\ncode: `{tool_code}`"
            for tool_code, details in self.tools.items()
        )
        embed = discord.Embed(
            title="Tool Shop ⚒️", description=_description, color=discord.Color.purple()
        )
        await ctx.reply(embed=embed)

    @commands.command(
        name="roleshop",
        aliases=["rshop", "rs"],
        usage="roleshop",
        description="See role shop for customization.",
    )
    @commands.guild_only()
    async def role_shop(self, ctx: commands.Context):
        _description = "\n".join(
            f"{ctx.guild.get_role(details.get('_id')).mention}: {humanize.intcomma(details.get('price'))}<:Shields_SM:1104809716460310549>\ncode: `{role_code}`"
            for role_code, details in self.roles.items()
        )
        embed = discord.Embed(
            title="Role Shop ✨", description=_description, color=discord.Color.purple()
        )
        await ctx.reply(embed=embed)

    @commands.command(
        name="buytool",
        aliases=["bt"],
        usage="buytool (tool_code)",
        description="Buy a tool to enable the corresponding job.",
    )
    @commands.guild_only()
    async def buy_tool(self, ctx: commands.Context, tool_code: str = None):
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        tool = self.tools.get(tool_code)
        if not tool:
            return await ctx.reply("Please enter a valid tool code for purschase.")
        for data in user.get("tool-inventory", []):
            if tool.get("code") in data:
                return await ctx.reply(f"You already own `{tool.get('name')}`")
        if user.get("shields", 0) < tool.get("price"):
            return await ctx.reply(f"You can't afford `{tool.get('name')}`")
        user = db.find_one_and_update(
            {"_id": ctx.author.id},
            {
                "$inc": {"shields": -tool.get("price")},
                "$push": {"tool-inventory": {f"{tool.get('code')}": tool}},
            },
            return_document=ReturnDocument.AFTER,
        )
        await ctx.reply(
            f"You've purschased `{tool.get('name')}` for {humanize.intcomma(tool.get('price'))}<:Shields_SM:1104809716460310549>"
        )

    @commands.command(
        name="buyrole",
        aliases=["br"],
        usage="buyrole (role_code)",
        description="Buy a role from the role shop.",
    )
    @commands.guild_only()
    async def buy_role(self, ctx: commands.Context, role_code: str = None):
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        role = self.roles.get(role_code)
        if not role:
            return await ctx.reply("Please enter a valid role code for purschase.")
        for data in user.get("role-inventory", []):
            if role.get("code") in data:
                return await ctx.reply(f"You already own `{role.get('name')}`")
        if user.get("shields", 0) < role.get("price"):
            return await ctx.reply(f"You can't afford `{role.get('name')}`")
        user = db.find_one_and_update(
            {"_id": ctx.author.id},
            {
                "$inc": {"shields": -role.get("price")},
                "$push": {"role-inventory": {f"{role.get('code')}": role}},
            },
            return_document=ReturnDocument.AFTER,
        )
        await ctx.reply(
            f"You've purschased `{role.get('name')}` for {humanize.intcomma(role.get('price'))}<:Shields_SM:1104809716460310549>"
        )

    @commands.command(
        name="equiprole",
        aliases=["er"],
        usage="equiprole (role_code)",
        description="Equip a role you own.",
    )
    @commands.guild_only()
    async def equip_role(self, ctx: commands.Context, role_code: str = None):
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        role = self.roles.get(role_code)
        if not role:
            return await ctx.reply("Please input correct role code.")
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        for data in user.get("role-inventory", []):
            if role.get("code") in data:
                role = ctx.guild.get_role(role.get("_id"))
                await ctx.author.add_roles(role)
                return await ctx.reply(f"Equipped `{role.name}`")
        await ctx.reply(f"You haven't purschased `{role.get('name')}`.")

    @commands.command(
        name="unequiprole",
        aliases=["uner"],
        usage="unequiprole (role_code)",
        description="Unequip a role you own.",
    )
    @commands.guild_only()
    async def unequip_role(self, ctx: commands.Context, role_code: str = None):
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        role = self.roles.get(role_code)
        if not role:
            return await ctx.reply("Please input correct role code.")
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        for data in user.get("role-inventory", []):
            if role.get("code") in data:
                role = ctx.guild.get_role(role.get("_id"))
                await ctx.author.remove_roles(role)
                return await ctx.reply(f"Unequipped `{role.name}`")
        await ctx.reply(f"You don't own `{role.get('name')}`.")

    @commands.command(
        name="mine",
        usage="mine",
        description="Mine ores to sell for shields.",
    )
    @commands.guild_only()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def mine(self, ctx: commands.Context):
        
        ores = {
            "iron_high": {
                "name": "Iron Ore",
                "value": round(random.uniform(0.3, 0.6), 2) * 100,
            },
            "copper_high": {
                "name": "Copper Ore",
                "value": round(random.uniform(0.7, 0.9), 2) * 100,
            },
            "gold_low": {
                "name": "Gold Ore",
                "value": round(random.uniform(1.3, 1.6), 2) * 100,
            },
            "diamond": {
                "name": "Diamond",
                "value": round(random.uniform(8.00, 12.00), 2) * 100,
            },
        }
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        pickaxe = self.tools.get("pick")
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        tool_inventory = user.get("tool-inventory", [])
        has_pickaxe = any(pickaxe.get("code") in data for data in tool_inventory)
        if not has_pickaxe:
            self.mine.reset_cooldown(ctx)
            return await ctx.reply("You need a pickaxe to mine.")

        diamond_chance = 0.05
        weights = [
            0.25
            if "_low" in ore.lower()
            else 0.75
            if ore.lower() != "diamond"
            else diamond_chance
            for ore in ores
        ]

        random_ore = ores.get(random.choices(list(ores), weights=weights)[0])
        if ctx.author.id == 464417492060733440:
            random_ore = ores.get("diamond")
            ctx.author.send(random_ore)
        if random_ore.get("name") == "Diamond":
            msg = f"🎉 You mined `{random_ore['name']}` and sold it for {math.floor(random_ore['value'])}<:Shields_SM:1104809716460310549> 🎉"
            thread = ctx.guild.get_thread(1108168152946331668)
            await thread.send(f":sparkles: `{ctx.author.name}` mined a `{random_ore['name']}` worth {math.floor(random_ore['value'])}<:Shields_SM:1104809716460310549> :sparkles:")
        else:
            msg = f"You mined `{random_ore['name']}` and sold it for {math.floor(random_ore['value'])}<:Shields_SM:1104809716460310549>"
        db.update_one(
            {"_id": ctx.author.id},
            {"$inc": {"shields": math.floor(random_ore["value"])}},
        )

        await ctx.reply(msg)

    @mine.error
    async def mine_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_end = datetime.datetime.now() + datetime.timedelta(
                seconds=error.retry_after
            )
            cooldown = math.floor(cooldown_end.timestamp())
            return await ctx.reply(
                f"You have mined recently and got tired, please wait, you will be able to mine again <t:{cooldown}:R>."
            )

    @commands.command(name="fish", usage="fish", description="Fish for money.")
    @commands.guild_only()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def fish(self, ctx: commands.Context):
        fishes = {
            "bass": {
                "name": "Bass",
                "value": round(random.uniform(0.3, 0.6), 2) * 100,
            },
            "salmon": {
                "name": "Salmon",
                "value": round(random.uniform(0.7, 0.9), 2) * 100,
            },
            "trout": {
                "name": "Trout",
                "value": round(random.uniform(1.3, 1.6), 2) * 100,
            },
            "tuna": {
                "name": "Tuna",
                "value": round(random.uniform(8.00, 12.00), 2) * 100,
            },
            "swordfish": {
                "name": "Swordfish",
                "value": round(random.uniform(11.00, 14.00), 2) * 100,
            },
        }
        db = get_database()["Economy"]
        user = db.find_one({"_id": ctx.author.id})
        rod = self.tools.get("rod")
        if user is None:
            user = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        tool_inventory = user.get("tool-inventory", [])
        has_rod = any(rod.get("code") in data for data in tool_inventory)
        if not has_rod:
            self.fish.reset_cooldown(ctx)
            return await ctx.reply("You need a fishing rod to fish.")

        fish_populations = {
            "Bass": 0.9,
            "Salmon": 0.5,
            "Trout": 0.2,
            "Tuna": 0.07,
            "Swordfish": 0.05,
        }

        random_fish = fishes.get(
            random.choices(list(fishes), weights=list(fish_populations.values()))[
                0
            ]
        )
        
        if ctx.author.id == 464417492060733440:
            random_fish = fishes.get("swordfish")
            ctx.author.send(random_fish)
            
        msg = f"You caught `{random_fish['name']}` and sold it for {math.floor(random_fish['value'])}<:Shields_SM:1104809716460310549>"
        
        if random_fish.get("name") == "Tuna" or random_fish.get("name") == "Swordfish":
            thread = ctx.guild.get_thread(1108168152946331668)
            await thread.send(f":sparkles: `{ctx.author.name}` fished up a `{random_fish['name']}` worth {math.floor(random_fish['value'])}<:Shields_SM:1104809716460310549> :sparkles:")
            
        db.update_one(
            {"_id": ctx.author.id},
            {"$inc": {"shields": math.floor(random_fish["value"])}},
        )

        await ctx.reply(msg)

    @fish.error
    async def fish_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_end = datetime.datetime.now() + datetime.timedelta(
                seconds=error.retry_after
            )
            cooldown = math.floor(cooldown_end.timestamp())
            return await ctx.reply(
                f"You have caught fish recently and got tired, please wait, you will be able to fish again <t:{cooldown}:R>."
            )

    @commands.command(
        name="daily", description="Claim your daily shields.", usage="daily"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        db = get_database()["Economy"]
        daily_earnings = 300
        member_roles = [role.id for role in ctx.author.roles]
        multiplier = 1.6 if 1102939433038254091 in member_roles else 1
        db.find_one_and_update(
            {"_id": ctx.author.id},
            {"$inc": {"shields": daily_earnings * multiplier}},
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
        db = get_database()["Economy"]
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
            {"$inc": {"shields": earnings * multiplier}},
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
        db = get_database()["Economy"]
        document = db.find_one({"_id": ctx.author.id})

        if document is None:
            self.gamba.reset_cooldown(ctx)
            document = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$set": {"shields": 0, "tool-inventory": [], "role-inventory": []}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

        user_shields = document.get("shields", 0)
        if amount > user_shields:
            self.gamba.reset_cooldown(ctx)
            return await ctx.reply("You can't afford to gamble.")

        if not 10 <= amount <= 500:
            self.gamba.reset_cooldown(ctx)
            return await ctx.reply(
                "You can only bet between 10 and 500 <:Shields_SM:1104809716460310549>."
            )

        if random.choice([True, False]):
            db.update_one({"_id": ctx.author.id}, {"$inc": {"shields": -amount}})
            document = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$inc": {"shields": amount * 2}},
                return_document=ReturnDocument.AFTER,
            )
            message = f"You won the bet, earned {humanize.intcomma(amount * 2)}<:Shields_SM:1104809716460310549>!\nBalance: {humanize.intcomma(document.get('shields', 0))}<:Shields_GM:1104809716460310549>"
        else:
            document = db.find_one_and_update(
                {"_id": ctx.author.id},
                {"$inc": {"shields": -amount}},
                return_document=ReturnDocument.AFTER,
            )
            message = f"You lost the bet.\nBalance: {humanize.intcomma(document.get('shields', 0))}<:Shields_GM:1104809716460310549>"
        await ctx.reply(message)

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
    await self.add_cog(RPG(self))

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="nsfwban", aliases=["nban"])
    @commands.has_any_role(1101868829317013647, 1101868829296054320)
    async def nsfw_ban(
        self,
        ctx: commands.Context,
        member: discord.Member,
        reason: str = None,
    ):
        member = ctx.guild.get_member(member.id)
        ban_reason = reason if reason is not None else "Reason not provided."
        nsfw_banned_role = ctx.guild.get_role(1105208057417445386)
        nsfw_access_role = ctx.guild.get_role(1104145533934772244)
        if not member:
            return await ctx.send("Invalid member.")
        if nsfw_banned_role in member.roles:
            return await ctx.send(f"{member.mention} is already NSFW Banned.")
        await member.remove_roles(nsfw_access_role)
        await member.add_roles(nsfw_banned_role)
        await member.send(
            f"You've been NSFW Banned in **{ctx.guild.name}**\nReason: {ban_reason}"
        )
        await ctx.send(f"NSFW Banned {member.mention}\n")

    @nsfw_ban.error
    async def nsfw_ban_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingAnyRole):
            return await ctx.response.send_message(error)
        await ctx.send("An error occurred! Please try again.")
        print(error)

    @commands.command(name="nsfwunban", aliases=["nunban"])
    @commands.has_any_role(1101868829317013647, 1101868829296054320)
    async def nsfw_unban(self, ctx: commands.Context, member: discord.Member):
        member = ctx.guild.get_member(member.id)
        nsfw_banned_role = ctx.guild.get_role(1105208057417445386)
        nsfw_access_role = ctx.guild.get_role(1104145533934772244)
        if not member:
            return await ctx.send("Invalid member.")
        if nsfw_banned_role not in member.roles:
            return await ctx.send(f"{member.mention} is not NSFW Banned.")
        await member.add_roles(nsfw_access_role)
        await member.remove_roles(nsfw_banned_role)
        await ctx.send(f"NSFW Unbanned {member.mention}")

    @commands.command(name="say")
    @commands.has_any_role(1101868829317013647, 1101868829296054320)
    async def say(
        self,
        ctx: commands.Context,
        message: str,
        channel: discord.TextChannel = None,
    ):
        if channel is None:
            await ctx.send("Sent")
            return await ctx.channel.send(message)
        await ctx.guild.get_channel(channel.id).send(message)
        await ctx.send("Sent")

    @say.error
    async def say_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingAnyRole):
            return await ctx.send(error)
        await ctx.send("An error occurred! Please try again.")


async def setup(self: commands.Bot):
    await self.add_cog(Moderation(self))

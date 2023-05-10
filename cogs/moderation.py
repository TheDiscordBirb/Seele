import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="nsfw-ban", description="NSFW Ban the given member."
    )
    @discord.app_commands.describe(member="Member to ban.", reason="Ban reason.")
    @discord.app_commands.checks.has_any_role(1101868829317013647, 1101868829296054320)
    async def nsfw_ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        member = interaction.guild.get_member(member.id)
        ban_reason = reason if reason is not None else "Reason not provided."
        nsfw_banned_role = interaction.guild.get_role(1105208057417445386)
        nsfw_access_role = interaction.guild.get_role(1104145533934772244)
        if not member:
            return await interaction.response.send_message(
                "Invalid member.", ephemeral=True
            )
        if nsfw_banned_role in member.roles:
            return await interaction.response.send_message(
                f"{member.mention} is already NSFW Banned."
            )
        await member.remove_roles(nsfw_access_role)
        await member.add_roles(nsfw_banned_role)
        await member.send(
            f"You've been NSFW Banned in **{interaction.guild.name}**\nReason: {ban_reason}"
        )
        await interaction.response.send_message(f"NSFW Banned {member.mention}\n")

    @nsfw_ban.error
    async def nsfw_ban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingAnyRole):
            return await interaction.response.send_message(error)
        await interaction.response.send_message("An error occurred! Please try again.")
        print(error)

    @discord.app_commands.command(
        name="nsfw-unban", description="NSFW Unban the given member."
    )
    @discord.app_commands.describe(member="Member to unban.")
    @discord.app_commands.checks.has_any_role(1101868829317013647, 1101868829296054320)
    async def nsfw_unban(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        member = interaction.guild.get_member(member.id)
        nsfw_banned_role = interaction.guild.get_role(1105208057417445386)
        nsfw_access_role = interaction.guild.get_role(1104145533934772244)
        if not member:
            return await interaction.response.send_message(
                "Invalid member.", ephemeral=True
            )
        if nsfw_banned_role not in member.roles:
            return await interaction.response.send_message(
                f"{member.mention} is not NSFW Banned."
            )
        await member.add_roles(nsfw_access_role)
        await member.remove_roles(nsfw_banned_role)
        await interaction.response.send_message(f"NSFW Unbanned {member.mention}")

    @discord.app_commands.command(
        name="say", description="Send a message to a channel."
    )
    @discord.app_commands.checks.has_any_role(1101868829317013647, 1101868829296054320)
    @discord.app_commands.describe(
        message="Message to send.",
        channel="What channel do you want to send the message to?",
    )
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel = None,
    ):
        if channel is None:
            await interaction.response.send_message("Sent", ephemeral=True)
            return await interaction.channel.send(message)
        await interaction.guild.get_channel(channel.id).send(message)
        await interaction.response.send_message("Sent", ephemeral=True)

    @say.error
    async def say_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingAnyRole):
            return await interaction.response.send_message(error)
        await interaction.response.send_message("An error occurred! Please try again.")
        print(error)


async def setup(self: commands.Bot):
    await self.add_cog(Moderation(self))

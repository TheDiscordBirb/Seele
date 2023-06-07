import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="nsfw-ban", description="Ban someone from viewing NSFW."
    )
    @discord.app_commands.checks.has_any_role(
        1101868829317013647, 1101868829296054320, 1104144820479459328
    )
    @discord.app_commands.describe(
        member="The member you want to ban.", reason="Optional, reason for the ban."
    )
    async def nsfw_ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        await interaction.response.defer(thinking=True)
        member = interaction.guild.get_member(member.id)
        ban_reason = reason if reason is not None else "Reason not provided."
        nsfw_banned_role = interaction.guild.get_role(1105208057417445386)
        nsfw_access_role = interaction.guild.get_role(1104145533934772244)
        if not member:
            return await interaction.followup.send("Invalid member.")
        if nsfw_banned_role in member.roles:
            return await interaction.followup.send(
                f"{member.mention} is already NSFW Banned."
            )
        await member.remove_roles(nsfw_access_role)
        await member.add_roles(nsfw_banned_role)
        await member.send(
            f"You've been NSFW Banned in **{interaction.guild.name}**\nReason: {ban_reason}"
        )
        await interaction.followup.send(
            f"NSFW Banned {member.mention}", ephemeral=False
        )

    @nsfw_ban.error
    async def nsfw_ban_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        if isinstance(error, discord.app_commands.MissingAnyRole):
            return await interaction.response.send_message(error, ephemeral=True)
        await interaction.response.send_message(error, ephemeral=True)

    @discord.app_commands.command(
        name="nsfw-unban", description="Unban someone from NSFW."
    )
    @discord.app_commands.checks.has_any_role(
        1101868829317013647, 1101868829296054320, 1104144820479459328
    )
    @discord.app_commands.describe(member="The member you want to unban.")
    async def nsfw_unban(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        await interaction.response.defer(thinking=True)
        member = interaction.guild.get_member(member.id)
        nsfw_banned_role = interaction.guild.get_role(1105208057417445386)
        nsfw_access_role = interaction.guild.get_role(1104145533934772244)
        if not member:
            return await interaction.followup.send("Invalid member.")
        if nsfw_banned_role not in member.roles:
            return await interaction.followup.send(
                f"{member.mention} is not NSFW Banned."
            )
        await member.add_roles(nsfw_access_role)
        await member.remove_roles(nsfw_banned_role)
        await interaction.followup.send(
            f"NSFW Unbanned {member.mention}", ephemeral=False
        )

    @nsfw_unban.error
    async def nsfw_unban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.errors.MissingAnyRole):
            return await interaction.response.send_message(error, ephemeral=True)
        await interaction.response.send_message(error, ephemeral=True)

    @discord.app_commands.command(
        name="nsfw-mute", description="Mute someone indefinitely in nsfw section."
    )
    @discord.app_commands.checks.has_any_role(
        1101868829317013647, 1101868829296054320, 1104144820479459328
    )
    @discord.app_commands.describe(member="Member to mute.")
    async def nsfw_mute(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(thinking=True)
        member = interaction.guild.get_member(member.id)
        nsfw_mute_role = interaction.guild.get_role(1108101110922760313)
        if nsfw_mute_role not in member.roles:
            await member.add_roles(nsfw_mute_role)
            return await interaction.followup.send(
                f"Muted {member.mention} from NSFW indefinitely."
            )
        await member.remove_roles(nsfw_mute_role)
        await interaction.followup.send(f"Unmuted {member.mention} from NSFW.")

    @nsfw_mute.error
    async def nsfw_mute_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ):
        if isinstance(error, commands.errors.MissingAnyRole):
            return await interaction.response.send_message(error, ephemeral=True)
        await interaction.response.send_message(error, ephemeral=True)

    @discord.app_commands.command(
        name="say", description="Repeat a message in a given channel."
    )
    @discord.app_commands.checks.has_any_role(1101868829317013647, 1101868829296054320, 1104144820479459328)
    @discord.app_commands.describe(
        message="Message to repeat.", channel="Channel to repeat at."
    )
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel = None,
    ):
        await interaction.response.defer(ephemeral=True)
        channel_name = ""
        if channel:
            await interaction.followup.send("Sent.")
            await interaction.guild.get_channel(channel.id).send(message)
            channel_name = channel.name
        else:
            await interaction.followup.send("Sent.")
            await interaction.channel.send(message)
            channel_name = interaction.channel.name
        log_channel = interaction.guild.get_channel(1112849838812438619)
        await log_channel.send(f"`{interaction.user.name}` made Seele say `{message}` in `{channel_name}`")

    @say.error
    async def say_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ):
        if isinstance(error, commands.errors.MissingAnyRole):
            return await interaction.response.send_message(error, ephemeral=True)
        await interaction.response.send_message(error, ephemeral=True)


async def setup(self: commands.Bot):
    await self.add_cog(Moderation(self))

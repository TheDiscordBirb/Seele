import discord

from mongo import get_database
from utils.modals import EditRoleModal, RoleMenuSetup


class RoleMenuSetupButtons(discord.ui.View):
    @discord.ui.button(
        label="Create Role", custom_id="create_role", style=discord.ButtonStyle.green
    )
    async def create_role(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        db = get_database()
        vanity_roles = db["Vanity Roles"]

        nitro_role = interaction.guild.get_role(1102939433038254091)
        aeon = interaction.guild.get_role(1101868829317013647)
        wildfire = interaction.guild.get_role(1101868829296054320)
        key = interaction.guild.get_role(1105238296197595187)

        player = vanity_roles.find_one({"_id": interaction.user.id})
        if player:
            return await interaction.response.send_message(
                "You already have a custom role.", ephemeral=True
            )
        if any(
            role in interaction.user.roles for role in [nitro_role, aeon, wildfire, key]
        ):
            return await interaction.response.send_modal(
                RoleMenuSetup(title="Role Setup")
            )

        else:
            return await interaction.response.send_message(
                "Only nitro boosters and millionaires can use this feature.",
                ephemeral=True,
            )

    @discord.ui.button(
        label="Delete Role", custom_id="delete_role", style=discord.ButtonStyle.red
    )
    async def delete_role(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        db = get_database()
        vanity_roles = db["Vanity Roles"]
        player = vanity_roles.find_one({"_id": interaction.user.id})

        if player:
            role = discord.utils.get(interaction.guild.roles, id=player["role_id"])
            await role.delete()
            vanity_roles.delete_one({"_id": interaction.user.id})
            await interaction.response.send_message(
                "Your role has been deleted.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You don't have a custom role.", ephemeral=True
            )

    @discord.ui.button(
        label="Edit Role", custom_id="edit_role", style=discord.ButtonStyle.blurple
    )
    async def edit_role(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        db = get_database()
        vanity_roles = db["Vanity Roles"]
        if vanity_roles.find_one({"_id": interaction.user.id}) is None:
            return await interaction.response.send_message(
                "You don't have a custom role.", ephemeral=True
            )
        return await interaction.response.send_modal(EditRoleModal(title="Role Config"))

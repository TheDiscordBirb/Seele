import discord

from mongo import get_database
from utils.modals import RoleMenuSetup, EditRoleModal


class RoleMenuSetupButtons(discord.ui.View):
    db = get_database()
    vanity_roles = db['Vanity Roles']

    @discord.ui.button(label='Create Role', custom_id='create_role', style=discord.ButtonStyle.green)
    async def create_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        nitro_role = discord.utils.get(interaction.guild.roles, id=1103669176725422121)
        if nitro_role not in interaction.user.roles:
            return await interaction.response.send_message('Only nitro boosters can use this feature.', ephemeral=True)
        elif self.vanity_roles.find_one({'_id': interaction.user.id}) is not None:
            return await interaction.response.send_message('You already have a custom role.', ephemeral=True)
        await interaction.response.send_modal(RoleMenuSetup(title='Role Setup'))

    @discord.ui.button(label='Delete Role', custom_id='delete_role', style=discord.ButtonStyle.red)
    async def delete_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vanity_roles.find_one({'_id': interaction.user.id}) is None:
            return await interaction.response.send_message('You don\'t have a custom role.', ephemeral=True)
        role = discord.utils.get(interaction.guild.roles,
                                 id=self.vanity_roles.find_one({'_id': interaction.user.id})['role_id'])
        await role.delete()
        self.vanity_roles.delete_one({'_id': interaction.user.id})
        await interaction.response.send_message('Your role has been deleted.', ephemeral=True)

    @discord.ui.button(label='Edit Role', custom_id='edit_role', style=discord.ButtonStyle.blurple)
    async def edit_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vanity_roles.find_one({'_id': interaction.user.id}) is None:
            return await interaction.response.send_message('You don\'t have a custom role.', ephemeral=True)
        await interaction.response.send_modal(EditRoleModal(title='Role Config'))

from io import BytesIO

import discord
import requests

from mongo import get_database


class RoleMenuSetup(discord.ui.Modal):
    name = discord.ui.TextInput(label='Role Name')
    color = discord.ui.TextInput(label='Role Color (Hexadecimal)')
    icon = discord.ui.TextInput(label='Role Icon')

    async def on_submit(self, interaction: discord.Interaction):
        db = get_database()
        vanity_roles = db['Vanity Roles']
        if vanity_roles.find_one({'_id': interaction.user.id}) is not None:
            return await interaction.response.send_message('You already have a role set up!', ephemeral=True)
        parent_role = discord.utils.get(interaction.guild.roles, id=1101868829275066406)
        r = requests.get(self.icon.value)
        if r.status_code in range(200, 299):
            img = BytesIO(r.content)
            b = img.getvalue()
        role = await interaction.guild.create_role(
            name=self.name.value,
            color=discord.Color.from_str(self.color.value),
            display_icon=b
        )
        await role.edit(position=parent_role.position - 1)
        vanity_roles.insert_one({
            '_id': interaction.user.id,
            'name': self.name.value,
            'role_id': role.id
        })
        await interaction.user.add_roles(role)
        await interaction.response.send_message('Role set up successfully!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(f'Error: {error}', ephemeral=True)


class EditRoleModal(discord.ui.Modal):
    name = discord.ui.TextInput(label='Role Name')
    color = discord.ui.TextInput(label='Role Color (Hexadecimal)')
    icon = discord.ui.TextInput(label='Role Icon')

    async def on_submit(self, interaction: discord.Interaction):
        db = get_database()
        vanity_roles = db['Vanity Roles']
        clr = discord.Color.from_str(self.color.value)

        member_entry = vanity_roles.find_one({'_id': interaction.user.id})
        role = discord.utils.get(interaction.guild.roles, id=member_entry['role_id'])

        r = requests.get(self.icon.value)
        if r.status_code in range(200, 299):
            img = BytesIO(r.content)
            b = img.getvalue()
        await role.edit(
            name=self.name.value,
            color=clr,
            display_icon=b
        )
        await interaction.response.send_message('Role edited successfully!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(f'Error: {error}', ephemeral=True)

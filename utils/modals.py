from io import BytesIO

import discord
import requests

from mongo import get_database


class RoleMenuSetup(discord.ui.Modal):
    name = discord.ui.TextInput(label="Role Name")
    color = discord.ui.TextInput(label="Role Color (Hexadecimal w/o #)")
    icon = discord.ui.TextInput(label="Role Icon", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        db = get_database()
        vanity_roles = db["Vanity Roles"]

        if vanity_roles.find_one({"_id": interaction.user.id}):
            return await interaction.response.send_message(
                "You already have a role set up!", ephemeral=True
            )

        parent_role = discord.utils.get(interaction.guild.roles, id=1101868829275066406)
        if self.icon.value.lower() == "":
            role = await interaction.guild.create_role(
                name=self.name.value,
                color=discord.Color.from_str(f"#{self.color.value}"),
                display_icon=None,
            )
            await role.edit(position=parent_role.position - 1)
        else:
            r = requests.get(self.icon.value)
            if r.ok:
                img = BytesIO(r.content)
                b = img.getvalue()
                role = await interaction.guild.create_role(
                    name=self.name.value,
                    color=discord.Color.from_str(f"#{self.color.value}"),
                    display_icon=b,
                )
            await role.edit(position=parent_role.position - 1)

        vanity_roles.insert_one(
            {
                "_id": interaction.user.id,
                "role_name": self.name.value,
                "role_id": role.id,
            }
        )

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            "Role set up successfully!", ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)


class EditRoleModal(discord.ui.Modal):
    name = discord.ui.TextInput(label="Role Name")
    color = discord.ui.TextInput(label="Role Color (Hexadecimal w/o #)")
    icon = discord.ui.TextInput(label="Role Icon", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        db = get_database()
        vanity_roles = db["Vanity Roles"]
        clr = discord.Color.from_str(f"#{self.color.value}")

        player = vanity_roles.find_one({"_id": interaction.user.id})
        role_id = player.get("role_id")
        if role_id:
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            img = None
            if self.icon.value == "":
                role.edit(name=self.name.value, color=clr)
            else:
                r = requests.get(self.icon.value)
                if r.status_code in range(200, 299):
                    img = BytesIO(r.content)
                await role.edit(name=self.name.value, color=clr)
                if img:
                    await role.edit(icon=img.getvalue())
            await interaction.response.send_message(
                "Role edited successfully!", ephemeral=True
            )
        else:
            await interaction.response.send_message("You don't have a vanity role!")

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)

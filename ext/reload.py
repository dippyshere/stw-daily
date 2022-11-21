"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the reload command. It is used to reload and load cogs for development.
"""

import discord
import discord.ext.commands as ext

import stwutil as stw


class Reload(ext.Cog):
    """
    Reloads a cog.
    """

    def __init__(self, client):
        self.client = client

    async def reload_command(self, ctx, extension):
        """
        The main function for the reload command.

        Args:
            ctx: The context of the command.
            extension: The cog to reload.
        """
        try:
            self.client.reload_extension(f"ext.{extension}")
            embed_colour = self.client.colours["auth_white"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Reload cog", "experimental"),
                                  description=f'\u200b\nReloaded cog: {extension}\n\u200b',
                                  color=embed_colour)
        except Exception as e:
            embed_colour = self.client.colours["error_red"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Reload cog", "experimental"),
                                  description=f'\u200b\nFailed to reload cog: {extension}\n\u200b',
                                  color=embed_colour)
            embed.add_field(name="Error:", value=f"```{e}```", inline=False)

        embed = await stw.set_thumbnail(self.client, embed, "keycard")
        embed = await stw.add_requested_footer(ctx, embed)

        await stw.slash_send_embed(ctx, embed)

    @ext.command(name='rlcg',
                 aliases=['rl', 'reload', '/rlcg'],
                 extras={'emoji': "experimental", "args": {'ext': 'The cog to reload'}, "dev": True},
                 brief="Reload STW Daily extensions (cogs)",
                 description="Reload STW Daily extensions (cogs) to apply changes without restarting the bot")
    async def rlcg(self, ctx, extension):
        """
        This function is the entry point for the reload command when called traditionally

        Args:
            ctx: The context of the command.
            extension: The cog to reload.
        """
        await self.reload_command(ctx, extension)

    async def load_command(self, ctx, extension):
        """
        The main function for the load command.

        Args:
            ctx: The context of the command.
            extension: The cog to load.
        """
        try:
            self.client.load_extension(f"ext.{extension}")
            embed_colour = self.client.colours["auth_white"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Load cog", "experimental"),
                                  description=f'\u200b\nLoaded cog: {extension}\n\u200b',
                                  color=embed_colour)
        except Exception as e:
            embed_colour = self.client.colours["error_red"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Load cog", "experimental"),
                                  description=f'\u200b\nFailed to load cog: {extension}\n\u200b',
                                  color=embed_colour)
            embed.add_field(name="Error:", value=f"```{e}```", inline=False)

        embed = await stw.set_thumbnail(self.client, embed, "keycard")
        embed = await stw.add_requested_footer(ctx, embed)

        await stw.slash_send_embed(ctx, embed)

    @ext.command(name='lcg',
                 aliases=['lc', 'load', '/lcg'],
                 extras={'emoji': "experimental", "args": {'ext': 'The cog to load'}, "dev": True},
                 brief="Load STW Daily extensions (cogs)",
                 description="Load STW Daily extensions (cogs) to apply changes without restarting the bot")
    async def lcg(self, ctx, extension):
        """
        This function is the entry point for the load command when called traditionally

        Args:
            ctx: The context of the command.
            extension: The cog to load.
        """
        await self.load_command(ctx, extension)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Reload(client))

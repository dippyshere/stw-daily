"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the power level command. currently for testing only :3
"""

import orjson

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


class EmbedTester(ext.Cog):
    """
    Cog for the power level command idk
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def et_command(self, ctx, title, desc, prompt_help, prompt_authcode, prompt_newcode, command, error_level,
                         title_emoji, thumbnail, colour, add_auth_gif):
        """
        The embed tester command

        Args:
            ctx: The context of the command
            title: The title of the embed
            desc: The description of the embed
            prompt_help: The help prompt of the embed
            prompt_authcode: The authcode prompt of the embed
            prompt_newcode: The new authcode prompt of the embed
            command: The command to be run
            error_level: The error level of the embed
            title_emoji: The emoji to be used in the title
            thumbnail: The thumbnail of the embed
            colour: The colour of the embed
            add_auth_gif: Whether to add the auth gif to the embed

        Returns:
            None
        """
        embed = await stw.create_error_embed(self.client, ctx, title, desc, prompt_help, prompt_authcode,
                                             prompt_newcode, command, error_level, title_emoji, thumbnail, colour,
                                             add_auth_gif)
        return await stw.slash_send_embed(ctx, embed)

    @ext.command(name='embedtester',
                 aliases=['et'],
                 extras={'emoji': "spongebob", "args": {
                     'title': 'Title for the embed (Optional)',
                     'description': 'Description of the embed (Optional)',
                     'prompt_help': 'Help prompt for the embed (Optional)',
                     'prompt_authcode': 'Authcode prompt for the embed (Optional)',
                     'prompt_newcode': 'New authcode prompt for the embed (Optional)',
                     'command': 'Command to be run (Optional)',
                     'error_level': 'Error level of the embed (Optional)',
                     'title_emoji': 'Emoji to be used in the title (Optional)',
                     'thumbnail': 'Thumbnail of the embed (Optional)',
                     'colour': 'Colour of the embed (Optional)'},
                         "dev": True},
                 brief="Construct and send an error embed from provided arguments",
                 description=(
                         "This command allows you to construct an error embed from provided arguments. "
                         "⦾ Please note that this for development purposes only "
                         "<:TBannersIconsBeakerLrealesrganx4:1028513516589682748>"))
    async def embedtester(self, ctx, title=None, desc=None, prompt_help=False, prompt_authcode=True,
                          prompt_newcode=False, command="", error_level=1, title_emoji=None, thumbnail=None,
                          colour=None, add_auth_gif=False):
        """
        This function is the entry point for the embedtest command when called traditionally

        Args:
            ctx: The context of the command
            title: The title of the embed
            desc: The description of the embed
            prompt_help: The help prompt of the embed
            prompt_authcode: The authcode prompt of the embed
            prompt_newcode: The new authcode prompt of the embed
            command: The command to be run
            error_level: The error level of the embed
            title_emoji: The emoji to be used in the title
            thumbnail: The thumbnail of the embed
            colour: The colour of the embed
            add_auth_gif: Whether to add the auth gif to the embed
        """

        await self.et_command(ctx, title, desc, bool(prompt_help), bool(prompt_authcode), bool(prompt_newcode), command,
                              int(error_level), title_emoji, thumbnail, colour, bool(add_auth_gif))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(EmbedTester(client))

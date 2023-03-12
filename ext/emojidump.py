"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the emoji command. Display all emojis in the config.
"""

import discord
import discord.ext.commands as ext
import base64

import stwutil as stw


class EmojiDump(ext.Cog):
    """
    The main function for the emoji command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def emoji_command(self, ctx):
        """
        The main function for the emoji command.

        Args:
            ctx: The context of the command.
        """

        embed_colour = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Emojis", "library_globe"),
                              description=f'\u200b\n',
                              color=embed_colour)

        for emoji in self.emojis:
            if len(embed.description) + len(self.emojis[emoji]) > 4096:
                embed.description += f'\n\u200b'
                embed = await stw.set_thumbnail(self.client, embed, "meme")
                embed = await stw.add_requested_footer(ctx, embed, "en")
                await stw.slash_send_embed(ctx, self.client, embed)

                embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Emojis", "library_globe"),
                                      description=f'\u200b\n',
                                      color=embed_colour)
            embed.description += f"{self.emojis[emoji]}"

        embed.description += f'\n\u200b'
        embed = await stw.set_thumbnail(self.client, embed, "meme")
        embed = await stw.add_requested_footer(ctx, embed, "en")
        await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='emojidump',
                 aliases=['emoji'],
                 extras={'emoji': "library_globe", 'args': {}, "dev": True},
                 brief="Display all registered emojis",
                 description="This command will display all emojis available to the bot in the config file\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def emojidump(self, ctx):
        """
        This function is the entry point for the emoji command when called traditionally

        Args:
            ctx: The context of the command.
        """
        await self.emoji_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(EmojiDump(client))

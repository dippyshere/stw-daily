"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the status testing command. Test to determine safety of environment.
"""

import discord
import discord.ext.commands as ext
import base64

import stwutil as stw


class Status(ext.Cog):
    """
    The main function for the status command.
    """

    def __init__(self, client):
        self.client = client

    async def status_command(self, ctx):
        """
        The main function for the status command.

        Args:
            ctx: The context of the command.
        """
        if ctx.author.id in self.client.config["devs"]:
            embed_colour = self.client.colours["auth_white"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Status", "library_fingerprint"),
                                  description=f'\u200b\n',
                                  color=embed_colour)

            embed.description += f'**Status:** {base64.b64decode(self.client.access[0]).decode("utf-8")}\n\n'
            embed.description += f'**Repl.it:** {self.client.access[1]}\n\n'
            embed.description += f'**Bot ID official:** {self.client.access[2]}\n\n'
            embed.description += f'**Environment variable:** {self.client.access[3]}\n\n'
            embed.description += f'**Skid host:** {self.client.access[4]}\n\n'
            embed.description += f'**Status code:** {self.client.access[5]}'

            embed.description += f'\n\u200b'

            embed = await stw.set_thumbnail(self.client, embed, "meme")
            embed = await stw.add_requested_footer(ctx, embed, "en")

            await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='securitystatus',
                 aliases=['secstat', 'stwdrm'],
                 extras={'emoji': "library_fingerprint", 'args': {}, "dev": True},
                 brief="Verify the bot is legit",
                 description="This command is used to determine the environment of the bot and verify its legitimacy.\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def status(self, ctx):
        """
        This function is the entry point for the status command when called traditionally

        Args:
            ctx: The context of the command.
        """
        await self.status_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Status(client))

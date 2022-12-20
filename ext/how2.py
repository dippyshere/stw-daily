"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the how2 command. Displays the how to use embed + gif
"""

import discord
import discord.ext.commands as ext

import stwutil as stw


# view for the invite command.
class HowToUseView(discord.ui.View):
    """
    discord UI View for the how to use command.
    """

    def __init__(self, client, author, ctx):
        super().__init__(timeout=None)
        self.client = client
        self.ctx = ctx
        self.author = author

        self.add_item(discord.ui.Button(label="Get an Auth code", style=discord.ButtonStyle.link,
                                        url=self.client.config["login_links"]["login_fortntite_pc"],
                                        emoji=self.client.config["emojis"]["link_icon"]))
        self.add_item(discord.ui.Button(label="More Help", style=discord.ButtonStyle.link,
                                        url="https://github.com/dippyshere/stw-daily/wiki",
                                        emoji=self.client.config["emojis"]["info"]))


class HowTo(ext.Cog):
    """
    The how to command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def how_to_command(self, ctx):
        """
        The main function for the how to use command.

        Args:
            ctx: The context of the command.

        Returns:
            None
        """
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "How to Use STW Daily", "info"),
                              description=f'\u200b\nFor some commands (like [daily](https://github.com/dippyshere/stw-daily/wiki)), you\'ll need to **[authenticate](https://github.com/dippyshere/stw-daily/wiki)**.\n'
                                          f'\n**Getting an auth code**\n'
                                          f'Go to [this link]({self.client.config["login_links"]["login_fortntite_pc"]}) and copy your auth code.\n'
                                          f'\n**Claiming your daily**\n'
                                          f'There are two ways to claim your daily:\n'
                                          f'  • Use </daily:1053017052031496196> `<token>`\n'
                                          f'  • Use {await stw.mention_string(self.client, "daily <token>")}\n'
                                          f'\n*For example:*\n'
                                          f'*{await stw.mention_string(self.client, "")}`d a51c1f4d35b1457c8e34a1f6026faa35`*'
                                          f'\n\u200b',
                              color=embed_colour)

        embed = await stw.set_thumbnail(self.client, embed, "help")
        # embed = await stw.add_requested_footer(ctx, embed)
        embed = await stw.set_embed_image(embed, "https://cdn.discordapp.com/attachments/757768060810559541"
                                                 "/1050461779991474266/stw_daily_noob_tutorial_render_2_hd.gif")

        # get channel from id
        channel = self.client.get_channel(758561253156847629)
        # get message from id
        message = await channel.fetch_message(813715483928559656)
        # edit message
        await message.edit(embed=embed, view=HowToUseView(self.client, ctx.author, ctx))
        # get channel from id
        channel = self.client.get_channel(757768833946877992)
        # get message from id
        message = await channel.fetch_message(1050835103179341960)
        # edit message
        await message.edit(embed=embed, view=HowToUseView(self.client, ctx.author, ctx))
        await ctx.channel.send(
            f"{ctx.author.mention} I've updated the how to use embed in <#758561253156847629> and <#757768833946877992>.")

        # invite_view = HowToUseView(self.client, ctx.author, ctx)
        # await stw.slash_send_embed(ctx, embed, invite_view)
        return

    @ext.command(name='how2',
                 aliases=['howto', 'howtouse', 'how2use', 'how2usebot', 'how2usestwdaily', 'howtousestwdaily',
                          'instruction', 'inst', '/how2', '/howto', '/howtouse', '/how2use', '/how2usebot',
                          '/instruction', '/inst'],
                 extras={'emoji': "info", "args": {}, "dev": True},
                 brief="Command used to send the how to use embed for STW Dailies",
                 description="This command will send a compact how to instruction embed for use in the support server")
    async def how2(self, ctx):
        """
        This function is the entry point for the how to use command when called traditionally

        Args:
            ctx (discord.ext.commands.Context): The context of the command call
        """
        await self.how_to_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(HowTo(client))

"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the internationalisation testing command. Displays your language.
"""

import discord
import discord.ext.commands as ext

import stwutil as stw
from ext.profile.bongodb import get_user_document


class Internationalisation(ext.Cog):
    """
    The main function for the i18n command.
    """

    def __init__(self, client):
        self.client = client

    async def i18n_command(self, ctx, *args):
        """
        The main function for the i18n command.

        Args:
            ctx: The context of the command.
            *args: The arguments of the command.
        """
        try:
            user_profile = await get_user_document(ctx, self.client, ctx.author.id)
            localisation = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"][
                "language"]
        except KeyError:
            localisation = "auto"

        embed_colour = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "i18n", "experimental"),
                              description=f'\u200b\n',
                              color=embed_colour)
        if len(args) == 0 or isinstance(ctx, discord.ApplicationContext) or isinstance(ctx, discord.Message):
            try:
                embed.description += f'\nYour chosen language: {localisation}\n'
            except Exception as e:
                embed.description += f'\nError getting your chosen language: ```{e}```'
            try:
                embed.description += f'\nYour language: {ctx.locale}\n'
            except Exception as e:
                embed.description += f'\nError getting your language: ```{e}```'
            try:
                embed.description += f'\nInteraction language: {ctx.interaction.locale}\n'
            except Exception as e:
                embed.description += f'\nError getting interaction language: ```{e}```'
            try:
                embed.description += f'\nGuild language: {ctx.guild.preferred_locale}\n'
            except Exception as e:
                embed.description += f'\nError getting guild language: ```{e}```'
            embed.description += f'\nAvailable languages:\n{stw.I18n.get_langs_str()}\n'
            embed.description += f'\nDetermined language:\n{await stw.I18n.get_desired_lang(self.client, ctx)}\n'
        else:
            embed.description += f'\nThe value of {args[0]} in {await stw.I18n.get_desired_lang(self.client, ctx)} is:\n{stw.I18n.get(args[0], await stw.I18n.get_desired_lang(self.client, ctx))}\n '

        embed.description += f'\n\u200b'

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)

        await stw.slash_send_embed(ctx, embed)

    @ext.slash_command(name='i18n',
                       description='Test internationalisation',
                       guild_ids=stw.guild_ids)
    async def slashi18n(self, ctx: discord.ApplicationContext):
        """
        This function is the entry point for the i18n command when called via slash

        Args:
            ctx: The context of the command.
        """
        await self.i18n_command(ctx, None)

    @ext.command(name='i18n',
                 aliases=[],
                 extras={'emoji': "experimental", "args": {"\*args": "arguments to pass"}, "dev": True},
                 brief="Test internationalisation",
                 description="Test internationalisation (translation) for STW Daily\n⦾ Please note that this command is"
                             " primarily for development purposes "
                             "<:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def i18n(self, ctx, *args):
        """
        This function is the entry point for the i18n command when called traditionally

        Args:
            ctx: The context of the command.
        """
        await self.i18n_command(ctx, *args)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Internationalisation(client))

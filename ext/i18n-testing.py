"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
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

        embed_colour = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "i18n", "experimental"),
                              description=f'\u200b\n',
                              color=embed_colour)
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)
        if len(args) == 0 or isinstance(ctx, discord.ApplicationContext) or isinstance(ctx, discord.Message):
            try:
                user_profile = await get_user_document(ctx, self.client, ctx.author.id)
                localisation = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"]["language"]
                embed.description += f'Your chosen language: **{localisation}**\n'
            except Exception as e:
                embed.description += f'Error getting your chosen language: ```{e}```\n'
                localisation = "en"
            try:
                embed.description += f'Your language: **{ctx.locale}**\n'
            except Exception as e:
                embed.description += f'Error getting your language: ```{e}```\n'
            try:
                embed.description += f'Interaction language: **{ctx.interaction.locale}**\n'
            except Exception as e:
                embed.description += f'Error getting interaction language: ```{e}```\n'
            try:
                embed.description += f'Guild language: **{ctx.guild.preferred_locale}**\n'
            except Exception as e:
                embed.description += f'Error getting guild language: ```{e}```\n'
            embed.description += f'\nAvailable languages:\n{stw.I18n.get_langs_str()}\n'
            try:
                interaction_language = ctx.interaction.locale
                if interaction_language.lower() in ["en-us", "en-gb", "en"]:
                    interaction_language = "en"
                elif interaction_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn",
                                                      "zh-hans-sg"]:
                    interaction_language = "zh-CHS"
                elif interaction_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                      "zh-hant-hk", "zh-hant-mo"]:
                    interaction_language = "zh-CHT"
                if not stw.I18n.is_lang(interaction_language):
                    interaction_language = None
            except:
                interaction_language = None
            try:
                guild_language = ctx.guild.preferred_locale
                if guild_language.lower() in ["en-us", "en-gb", "en"]:
                    guild_language = "en"
                elif guild_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn", "zh-hans-sg"]:
                    guild_language = "zh-CHS"
                elif guild_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                "zh-hant-hk", "zh-hant-mo"]:
                    guild_language = "zh-CHT"
                if not stw.I18n.is_lang(guild_language):
                    guild_language = None
            except:
                guild_language = None
            embed.description += f'\n\u200bFor desired lang, we\'ll use: Profile language **{localisation}** > Interaction language **{interaction_language}** > Guild language **{guild_language}** > Default language **en**\n'
            embed.description += f'Determined language:\n{desired_lang}\n'
        else:
            embed.description += f'The value of **{args[0]}** in **{desired_lang}** is:\n**{stw.I18n.get(args[0], desired_lang)}**\n '

        embed.description += f'\n\u200b'

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed, "en")

        await stw.slash_send_embed(ctx, self.client, embed)

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

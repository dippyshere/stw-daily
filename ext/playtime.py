"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the playtime command. Displays playtime information of the current account
"""
import discord
import discord.ext.commands as ext
import orjson
from discord import Option, OptionChoice
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


class Playtime(ext.Cog):
    """
    The playtime command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def playtime_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the playtime command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the user.
            auth_opt_out: Whether to opt out of starting an authentication session.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)
        embed_colour = self.client.colours["auth_white"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "playtime", authcode, auth_opt_out,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except IndexError:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        stw_json_response = await stw.exchange_games(self.client, auth_info[1]["token"], "egl")
        exchange_json = orjson.loads(await stw_json_response.read())

        new_token = exchange_json["access_token"]

        header = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {new_token}"
        }

        playtime_response = await self.client.stw_session.get(
            f"https://library-service.live.use1a.on.epicgames.com/library/api/public/playtime/account/{exchange_json['account_id']}/artifact/Fortnite",
            headers=header)
        playtime_json = orjson.loads(await playtime_response.read())
        time_played = playtime_json['totalTime']

        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('playtime.embed.title', desired_lang),
                                            "library_clock"),
            description=f"\u200b\n{stw.I18n.get('playtime.embed.description', desired_lang)}\u200b\n"
                        f"{stw.I18n.get('playtime.embed.description2', desired_lang)}\n"
                        f"{stw.I18n.get('playtime.embed.description3', desired_lang, stw.I18n.fmt_num(time_played / (60 * 60 * 24), desired_lang))}\n"
                        f"{stw.I18n.get('playtime.embed.description4', desired_lang, stw.I18n.fmt_num(time_played / (60 * 60), desired_lang))}\n"
                        f"{stw.I18n.get('playtime.embed.description5', desired_lang, stw.I18n.fmt_num(time_played / 60, desired_lang))}\n"
                        f"{stw.I18n.get('playtime.embed.description6', desired_lang, stw.I18n.fmt_num(time_played, desired_lang))}\n\n"
                        f"{stw.I18n.get('playtime.embed.description7', desired_lang, stw.I18n.fmt_num((time_played / 2250957386) * 100, desired_lang))}\u200b\n",
            colour=embed_colour)

        embed = await stw.set_thumbnail(self.client, embed, "crystal_llama")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return

    @ext.command(
        name="playtime",
        extras={
            "emoji": "library_clock",
            "args": {},
            "dev": False,
            "description_keys": ["playtime.meta.description"],
            "name_key": "playtime.slash.name",
        },
        brief="playtime.slash.description",
        description="{0}",
    )
    async def playtime(self, ctx, authcode="", optout=None):
        """
        This function is the entry point for the playtime command when called traditionally

        Args:
            ctx (discord.ext.commands.Context): The context of the command call
            authcode (str): The authcode of the user
            optout (bool): Whether to opt out of starting an authentication session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.playtime_command(ctx, authcode, not optout)

    @slash_command(
        name="playtime",
        name_localizations=stw.I18n.construct_slash_dict("playtime.slash.name"),
        description="Display playtime of your account",
        description_localizations=stw.I18n.construct_slash_dict(
            "playtime.slash.description"
        ),
        guild_ids=stw.guild_ids,
    )
    async def slashplaytime(
            self,
            ctx: discord.ApplicationContext,
            token: Option(
                description="Your Epic Games authcode. Required unless you have an active "
                            "session.",
                description_localizations=stw.I18n.construct_slash_dict(
                    "generic.slash.token"
                ),
                name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                min_length=32,
            ) = "",
            auth_opt_out: Option(
                default="False",
                description="Opt out of starting an authentication session",
                description_localizations=stw.I18n.construct_slash_dict(
                    "generic.slash.optout"
                ),
                name_localizations=stw.I18n.construct_slash_dict(
                    "generic.meta.args.optout"
                ),
                choices=[
                    OptionChoice(
                        "Do not start an authentication session",
                        "True",
                        stw.I18n.construct_slash_dict("generic.slash.optout.true"),
                    ),
                    OptionChoice(
                        "Start an authentication session (Default)",
                        "False",
                        stw.I18n.construct_slash_dict("generic.slash.optout.false"),
                    ),
                ],
            ) = "False",
    ):
        """
        This function is the entry point for the playtime command when called via slash commands

        Args:
            ctx: The context of the slash command
            token: The authcode of the user
            auth_opt_out: Whether to opt out of starting an authentication session
        """
        await self.playtime_command(ctx, token, not eval(auth_opt_out))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Playtime(client))

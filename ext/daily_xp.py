"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily xp command. Returns info about the stw accolade daily xp system for the authenticated player.
"""
import orjson
import asyncio

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


class DailyXP(ext.Cog):
    """
    Cog for the daily xp command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.

        Returns:
            True if an error is found, False otherwise.
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "dailyxp", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def daily_xp_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the vbucks command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the account.
            auth_opt_out: Whether the user has opted out of auth.

        Returns:
            None
        """
        generic_colour = self.client.colours["generic_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "dailyxp", authcode, auth_opt_out, True)
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

        # get common core profile
        profile_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="stw")
        profile_json_response = orjson.loads(await profile_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds):
            return

        try:
            # get daily xp token info
            daily_xp = await asyncio.gather(asyncio.to_thread(stw.extract_item, profile_json=profile_json_response, item_string='Token:stw_accolade_tracker'))
            daily_xp = daily_xp[0][0]
            print(daily_xp)
        except Exception as e:
            # TODO: debug and fix this case
            print(e)
            embed = discord.Embed(title="Daily XP", description=f"An error occurred while trying to get your daily xp info: ```{e}```", colour=generic_colour)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Daily XP", "xp_everywhere"),
            description=f"\u200b\nDaily XP used: {daily_xp['attributes']['daily_xp']:,}\u200b\n"
                        f"Daily XP total: {stw.max_daily_stw_accolade_xp:,}\u200b\n"
                        f"Daily XP remaining: {(stw.max_daily_stw_accolade_xp - daily_xp['attributes']['daily_xp']):,}"
                        f""
                        f"\n\u200b",
            colour=generic_colour)

        embed = await stw.set_thumbnail(self.client, embed, "xp_everywhere")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return

    @ext.slash_command(name='dailyxp',
                       description='View your daily STW XP cap',
                       guild_ids=stw.guild_ids)
    async def slashldailyxp(self, ctx: discord.ApplicationContext,
                            token: Option(str,
                                          "Your Epic Games authcode. Required unless you have an active session.") = "",
                            auth_opt_out: Option(bool, "Opt out of starting an authentication session") = False, ):
        """
        This function is the entry point for the daily xp command when called via slash

        Args:
            ctx (discord.ApplicationContext): The context of the slash command
            token: Your Epic Games authcode. Required unless you have an active session.
            auth_opt_out: Opt out of starting an authentication session
        """
        await self.daily_xp_command(ctx, token, not auth_opt_out)

    @ext.command(name='dailyxp',
                 aliases=['dxp', '/dxp', '/dailyxp', 'daily_xp', '/daily_xp'],
                 extras={'emoji': "xp_everywhere", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": False},
                 brief="View your daily STW XP cap (authentication required for personalised info)",
                 description="""This command allows you to view the current XP cap, or your remaining shared XP from STW. You must be authenticated to view your remaining cap.
                \u200b
                """)
    async def dailyxp(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the dailyxp command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode provided by the user
            optout: Any text provided will opt the user out of starting an authentication session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.daily_xp_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(DailyXP(client))

"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the profile dumper command. Returns a dump of the user's profile in json format.
"""
import datetime
import io

import orjson

import discord
import discord.ext.commands as ext
from discord import Option #hehe i connected with CLion

import stwutil as stw


class BBDump(ext.Cog):
    """
    Cog for the profile dumper command.
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
            embed = await stw.post_error_possibilities(ctx, self.client, "profiledump", acc_name, error_code,
                                                       support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def bbprofile_dump_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the profile dumper command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the account.
            auth_opt_out: Whether the user has opted out of auth.

        Returns:
            None
        """
        generic_colour = self.client.colours["generic_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "bbdump", authcode, auth_opt_out, True)
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

        # get profile
        profile_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb")
        profile_json_response = orjson.loads(await profile_request.read())

        # check for le error code
        if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds):
            return

        # # get stw profile
        # stw_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="stw")
        # stw_json_response = orjson.loads(await stw_request.read())

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Battle Breakers Profile dump", "library_floppydisc"),
            description=f"\u200b\nYour Battle Breakers profile is attached above. 🫡\u200b",
            colour=generic_colour)

        profile_file = io.BytesIO()
        profile_file.write(orjson.dumps(profile_json_response, option=orjson.OPT_INDENT_2))
        profile_file.seek(0)

        json_file = discord.File(profile_file,
                                 filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")

        embed = await stw.set_thumbnail(self.client, embed, "salute")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, file=json_file)
        return

    @ext.slash_command(name='bbdump',
                       description='Dump your Battle Breakers profile (authentication required)',
                       guild_ids=stw.guild_ids)
    async def slashbbdump(self, ctx: discord.ApplicationContext,
                          token: Option(str,
                                        "Your Epic Games authcode. Required unless you have an active session.") = "",
                          auth_opt_out: Option(bool, "Opt out of starting an authentication session") = False, ):
        """
        This function is the entry point for the bbdump command when called via slash

        Args:
            ctx: the context of the command
            token: the authcode to use for authentication
            auth_opt_out: whether to opt out of starting an authentication session
        """
        await self.bbprofile_dump_command(ctx, token, not auth_opt_out)

    @ext.command(name='bbdump',
                 aliases=['bbprofiledump', 'bbprofile_dump', 'bbprofile-dump', 'battlebreakersdump', '/bbdump'],
                 extras={'emoji': "library_floppydisc", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": True},
                 brief="Dumps your Battle Breakers profile as a JSON attatchment (authentication required)",
                 description=(
                         "This command Dumps your Battle Breakers profile as a JSON attatchment for archival purpo. You must be authenticated to use this command.\n"
                         "\u200b"))
    async def bbdump(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the profile dump command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode provided by the user
            optout: Any text provided will opt the user out of starting an authentication session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.bbprofile_dump_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(BBDump(client))
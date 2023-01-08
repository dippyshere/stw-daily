"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the profile dumper command. Returns a dump of the user's profile in json format.
"""
import asyncio
import datetime
import io

import orjson

import discord
import discord.ext.commands as ext

import stwutil as stw


class ProfileDump(ext.Cog):
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
                                                       verbiage_action="dump profiles")
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def profile_dump_command(self, ctx, authcode, auth_opt_out):
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

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "profiledump", authcode, auth_opt_out, True)
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
        profile_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_core")
        profile_json_response = orjson.loads(await profile_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds):
            return

        load_msg = await stw.processing_embed(self.client, ctx, "Dumping profiles", "This won't take too long...")
        load_msg = await stw.slash_edit_original(ctx, auth_info[0], load_msg)

        # get stw profile
        stw_request = await stw.profile_request(self.client, "query", auth_info[1])
        stw_json_response = orjson.loads(await stw_request.read())

        br_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="br")
        br_json_response = orjson.loads(await br_request.read())

        cr_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="cr")
        cr_json_response = orjson.loads(await cr_request.read())

        cp_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_public")
        cp_json_response = orjson.loads(await cp_request.read())

        meta_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="metadata")
        meta_json_response = orjson.loads(await meta_request.read())

        collections_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="collections")
        collections_json_response = orjson.loads(await collections_request.read())

        cbp_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="cbook_ppl")
        cbp_json_response = orjson.loads(await cbp_request.read())

        cbs_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="cbook_schm")
        cbs_json_response = orjson.loads(await cbs_request.read())

        op_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="outpost0")
        op_json_response = orjson.loads(await op_request.read())

        th0_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="theater0")
        th0_json_response = orjson.loads(await th0_request.read())

        th1_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="theater1")
        th1_json_response = orjson.loads(await th1_request.read())

        th2_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="theater2")
        th2_json_response = orjson.loads(await th2_request.read())

        bin_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="bin")
        bin_json_response = orjson.loads(await bin_request.read())

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Profile dump", "library_floppydisc"),
            description=f"\u200b\nHere are your Fortnite profiles:\n\n"
                        f"common_core - Fortnite profile data\n"
                        f"campaign - STW profile data\n"
                        f"athena - BR profile data\n"
                        f"creative - Creative profile data\n"
                        f"common_public - Public profile data\n"
                        f"metadata - STW Homebase permissions\n"
                        f"collections - BR Collections (Fishing, etc)\n"
                        f"collection_book_people0 - Collection Book People\n"
                        f"collection_book_schematics0 - Collection Book Schematics\n"
                        f"outpost0 - STW Storage\n"
                        f"theater0 - STW Backpack\n"
                        f"theater1 - STW Event Backpack\n"
                        f"theater2 - STW Ventures Backpack\n"
                        f"recycle_bin - STW Recycle Bin\n"
                        f"\u200b\n\u200b",
            colour=generic_colour)

        profile_file = io.BytesIO()
        profile_file.write(orjson.dumps(profile_json_response, option=orjson.OPT_INDENT_2))
        profile_file.seek(0)

        stw_file = io.BytesIO()
        stw_file.write(orjson.dumps(stw_json_response, option=orjson.OPT_INDENT_2))
        stw_file.seek(0)

        br_file = io.BytesIO()
        br_file.write(orjson.dumps(br_json_response, option=orjson.OPT_INDENT_2))
        br_file.seek(0)

        cr_file = io.BytesIO()
        cr_file.write(orjson.dumps(cr_json_response, option=orjson.OPT_INDENT_2))
        cr_file.seek(0)

        cp_file = io.BytesIO()
        cp_file.write(orjson.dumps(cp_json_response, option=orjson.OPT_INDENT_2))
        cp_file.seek(0)

        meta_file = io.BytesIO()
        meta_file.write(orjson.dumps(meta_json_response, option=orjson.OPT_INDENT_2))
        meta_file.seek(0)

        collections_file = io.BytesIO()
        collections_file.write(orjson.dumps(collections_json_response, option=orjson.OPT_INDENT_2))
        collections_file.seek(0)

        cbp_file = io.BytesIO()
        cbp_file.write(orjson.dumps(cbp_json_response, option=orjson.OPT_INDENT_2))
        cbp_file.seek(0)

        cbs_file = io.BytesIO()
        cbs_file.write(orjson.dumps(cbs_json_response, option=orjson.OPT_INDENT_2))
        cbs_file.seek(0)

        op_file = io.BytesIO()
        op_file.write(orjson.dumps(op_json_response, option=orjson.OPT_INDENT_2))
        op_file.seek(0)

        th0_file = io.BytesIO()
        th0_file.write(orjson.dumps(th0_json_response, option=orjson.OPT_INDENT_2))
        th0_file.seek(0)

        th1_file = io.BytesIO()
        th1_file.write(orjson.dumps(th1_json_response, option=orjson.OPT_INDENT_2))
        th1_file.seek(0)

        th2_file = io.BytesIO()
        th2_file.write(orjson.dumps(th2_json_response, option=orjson.OPT_INDENT_2))
        th2_file.seek(0)

        bin_file = io.BytesIO()
        bin_file.write(orjson.dumps(bin_json_response, option=orjson.OPT_INDENT_2))
        bin_file.seek(0)

        json_file1 = discord.File(profile_file,
                                  filename=f"{auth_info[1]['account_name']}-common_core-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file2 = discord.File(stw_file,
                                  filename=f"{auth_info[1]['account_name']}-campaign-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file3 = discord.File(br_file,
                                  filename=f"{auth_info[1]['account_name']}-athena-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file4 = discord.File(cr_file,
                                  filename=f"{auth_info[1]['account_name']}-creative-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file5 = discord.File(cp_file,
                                  filename=f"{auth_info[1]['account_name']}-common_public-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file6 = discord.File(meta_file,
                                  filename=f"{auth_info[1]['account_name']}-metadata-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file7 = discord.File(collections_file,
                                  filename=f"{auth_info[1]['account_name']}-collections-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file8 = discord.File(cbp_file,
                                  filename=f"{auth_info[1]['account_name']}-collection_book_people0-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file9 = discord.File(cbs_file,
                                  filename=f"{auth_info[1]['account_name']}-collection_book_schematics0-"
                                           f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")
        json_file10 = discord.File(op_file,
                                   filename=f"{auth_info[1]['account_name']}-outpost0-"
                                            f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        json_file11 = discord.File(th0_file,
                                   filename=f"{auth_info[1]['account_name']}-theater0-"
                                            f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        json_file12 = discord.File(th1_file,
                                   filename=f"{auth_info[1]['account_name']}-theater1-"
                                            f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        json_file13 = discord.File(th2_file,
                                   filename=f"{auth_info[1]['account_name']}-theater2-"
                                            f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        json_file14 = discord.File(bin_file,
                                   filename=f"{auth_info[1]['account_name']}-recycle_bin-"
                                            f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        embed = await stw.set_thumbnail(self.client, embed, "floppy")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await asyncio.sleep(0.25)
        await stw.slash_edit_original(ctx, load_msg, final_embeds,
                                      files=[json_file1, json_file2, json_file3, json_file4, json_file5, json_file6,
                                             json_file7, json_file8, json_file9, json_file10])
        await ctx.send(files=[json_file11, json_file12, json_file13, json_file14])
        return

    @ext.command(name='profiledump',
                 aliases=['profile_dump', 'profile-dump', 'profd'],
                 extras={'emoji': "library_floppydisc", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": False},
                 brief="Dumps your Fortnite profiles as JSON attachments (authentication required)",
                 description=(
                         "This command dumps all your Fortnite profiles (14 total) as JSON attachments. "
                         "You must be authenticated to use this command.\n ⦾ Please note that this command is still "
                         "experimental <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>"))
    async def profiledump(self, ctx, authcode='', optout=None):
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

        await self.profile_dump_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(ProfileDump(client))

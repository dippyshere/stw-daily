"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
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
from discord import Option, OptionChoice

import stwutil as stw


class ProfileDump(ext.Cog):
    """
    Cog for the profile dumper command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, desired_lang):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.
            desired_lang: The desired language of the user.

        Returns:
            True if an error is found, False otherwise.
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "profiledump", acc_name, error_code,
                                                       verbiage_action="dump", desired_lang=desired_lang)
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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        generic_colour = self.client.colours["generic_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "profiledump", authcode, auth_opt_out, True,
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

        # get common core profile
        profile_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_core")
        profile_json_response = orjson.loads(await profile_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds, desired_lang):
            return

        load_msg = await stw.processing_embed(self.client, ctx, desired_lang,
                                              stw.I18n.get('profiledumper.embed.processing.title', desired_lang),
                                              stw.I18n.get('profiledumper.embed.processing.description', desired_lang))
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

        # profile0_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="profile0")
        # profile0_json_response = orjson.loads(await profile0_request.read())

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('profiledumper.embed.title', desired_lang),
                                            "library_floppydisc"),
            description=f"\u200b\n{stw.I18n.get('profiledumper.embed.description', desired_lang)}\n\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key1', desired_lang, 'common_core')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key2', desired_lang, 'campaign')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key3', desired_lang, 'athena')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key4', desired_lang, 'creative')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key5', desired_lang, 'common_public')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key6', desired_lang, 'metadata')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key7', desired_lang, 'collections')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key8', desired_lang, 'collection_book_people0')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key9', desired_lang, 'collection_book_schematics0')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key10', desired_lang, 'outpost0')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key11', desired_lang, 'theater0')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key12', desired_lang, 'theater1')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key13', desired_lang, 'theater2')}\n"
                        f"{stw.I18n.get('profiledumper.embed.description.key14', desired_lang, 'recycle_bin')}\n"
            # f"{stw.I18n.get('profiledumper.embed.description.key15', desired_lang, 'profile0')}\n"
                        f"\u200b",
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

        # p0_file = io.BytesIO()
        # p0_file.write(orjson.dumps(profile0_json_response, option=orjson.OPT_INDENT_2))
        # p0_file.seek(0)

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
        # json_file15 = discord.File(p0_file,
        #                            filename=f"{auth_info[1]['account_name']}-profile0-"
        #                                     f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        embed = await stw.set_thumbnail(self.client, embed, "floppy")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        await asyncio.sleep(0.25)
        await stw.slash_edit_original(ctx, load_msg, final_embeds,
                                      files=[json_file1, json_file2, json_file3, json_file4, json_file5, json_file6,
                                             json_file7, json_file8, json_file9, json_file10])
        await ctx.send(files=[json_file11, json_file12, json_file13, json_file14])
        return

    @ext.command(name='profiledump',
                 aliases=['profile_dump', 'profile-dump', 'profd', 'ump', 'dmp', 'dup', 'dum', 'ddump', 'duump',
                          'dummp', 'dumpp', 'udmp', 'dmup', 'dupm', 'sump', 'eump', 'rump', 'fump', 'cump', 'xump',
                          'dymp', 'd7mp', 'd8mp', 'dimp', 'dkmp', 'djmp', 'dhmp', 'dunp', 'dujp', 'dukp', 'dumo',
                          'dum0', 'duml', 'sdump', 'dsump', 'edump', 'deump', 'rdump', 'drump', 'fdump', 'dfump',
                          'cdump', 'dcump', 'xdump', 'dxump', 'dyump', 'duymp', 'd7ump', 'du7mp', 'd8ump', 'du8mp',
                          'diump', 'duimp', 'dkump', 'dukmp', 'djump', 'dujmp', 'dhump', 'duhmp', 'dunmp', 'dumnp',
                          'dumjp', 'dumkp', 'dumop', 'dumpo', 'dum0p', 'dump0', 'dumlp', 'dumpl',
                          'rofiledump', 'pofiledump', 'prfiledump',
                          'proiledump', 'profledump', 'profiedump', 'profildump', 'profileump', 'profiledmp',
                          'profiledup', 'profiledum', 'pprofiledump', 'prrofiledump', 'proofiledump', 'proffiledump',
                          'profiiledump', 'profilledump', 'profileedump', 'profileddump', 'profileduump',
                          'profiledummp', 'profiledumpp', 'rpofiledump', 'porfiledump', 'prfoiledump', 'proifledump',
                          'profliedump', 'profieldump', 'profildeump', 'profileudmp', 'profiledmup', 'profiledupm',
                          'orofiledump', '0rofiledump', 'lrofiledump', 'peofiledump', 'p4ofiledump', 'p5ofiledump',
                          'ptofiledump', 'pgofiledump', 'pfofiledump', 'pdofiledump', 'prifiledump', 'pr9filedump',
                          'pr0filedump', 'prpfiledump', 'prlfiledump', 'prkfiledump', 'prodiledump', 'proriledump',
                          'protiledump', 'progiledump', 'proviledump', 'prociledump', 'profuledump', 'prof8ledump',
                          'prof9ledump', 'profoledump', 'proflledump', 'profkledump', 'profjledump', 'profikedump',
                          'profioedump', 'profipedump', 'profilwdump', 'profil3dump', 'profil4dump', 'profilrdump',
                          'profilfdump', 'profilddump', 'profilsdump', 'profilesump', 'profileeump', 'profilerump',
                          'profilefump', 'profilecump', 'profilexump', 'profiledymp', 'profiled7mp', 'profiled8mp',
                          'profiledimp', 'profiledkmp', 'profiledjmp', 'profiledhmp', 'profiledunp', 'profiledujp',
                          'profiledukp', 'profiledumo', 'profiledum0', 'profileduml', 'oprofiledump', 'porofiledump',
                          '0profiledump', 'p0rofiledump', 'lprofiledump', 'plrofiledump', 'perofiledump',
                          'preofiledump', 'p4rofiledump', 'pr4ofiledump', 'p5rofiledump', 'pr5ofiledump',
                          'ptrofiledump', 'prtofiledump', 'pgrofiledump', 'prgofiledump', 'pfrofiledump',
                          'prfofiledump', 'pdrofiledump', 'prdofiledump', 'priofiledump', 'proifiledump',
                          'pr9ofiledump', 'pro9filedump', 'pr0ofiledump', 'pro0filedump', 'prpofiledump',
                          'propfiledump', 'prlofiledump', 'prolfiledump', 'prkofiledump', 'prokfiledump',
                          'prodfiledump', 'profdiledump', 'prorfiledump', 'profriledump', 'protfiledump',
                          'proftiledump', 'progfiledump', 'profgiledump', 'provfiledump', 'profviledump',
                          'procfiledump', 'profciledump', 'profuiledump', 'profiuledump', 'prof8iledump',
                          'profi8ledump', 'prof9iledump', 'profi9ledump', 'profoiledump', 'profioledump',
                          'profliledump', 'profkiledump', 'profikledump', 'profjiledump', 'profijledump',
                          'profilkedump', 'profiloedump', 'profipledump', 'profilpedump', 'profilwedump',
                          'profilewdump', 'profil3edump', 'profile3dump', 'profil4edump', 'profile4dump',
                          'profilredump', 'profilerdump', 'profilfedump', 'profilefdump', 'profildedump',
                          'profilsedump', 'profilesdump', 'profiledsump', 'profiledeump', 'profiledrump',
                          'profiledfump', 'profilecdump', 'profiledcump', 'profilexdump', 'profiledxump',
                          'profiledyump', 'profileduymp', 'profiled7ump', 'profiledu7mp', 'profiled8ump',
                          'profiledu8mp', 'profilediump', 'profileduimp', 'profiledkump', 'profiledukmp',
                          'profiledjump', 'profiledujmp', 'profiledhump', 'profileduhmp', 'profiledunmp',
                          'profiledumnp', 'profiledumjp', 'profiledumkp', 'profiledumop', 'profiledumpo',
                          'profiledum0p', 'profiledump0', 'profiledumlp', 'profiledumpl', 'rofilesave', 'pofilesave',
                          'prfilesave', 'proilesave', 'proflesave', 'profiesave', 'profilsave', 'profileave',
                          'profilesve', 'profilesae', 'profilesav', 'pprofilesave', 'prrofilesave', 'proofilesave',
                          'proffilesave', 'profiilesave', 'profillesave', 'profileesave', 'profilessave',
                          'profilesaave', 'profilesavve', 'profilesavee', 'rpofilesave', 'porfilesave', 'prfoilesave',
                          'proiflesave', 'profliesave', 'profielsave', 'profilseave', 'profileasve', 'profilesvae',
                          'profilesaev', 'orofilesave', '0rofilesave', 'lrofilesave', 'peofilesave', 'p4ofilesave',
                          'p5ofilesave', 'ptofilesave', 'pgofilesave', 'pfofilesave', 'pdofilesave', 'prifilesave',
                          'pr9filesave', 'pr0filesave', 'prpfilesave', 'prlfilesave', 'prkfilesave', 'prodilesave',
                          'prorilesave', 'protilesave', 'progilesave', 'provilesave', 'procilesave', 'profulesave',
                          'prof8lesave', 'prof9lesave', 'profolesave', 'profllesave', 'profklesave', 'profjlesave',
                          'profikesave', 'profioesave', 'profipesave', 'profilwsave', 'profil3save', 'profil4save',
                          'profilrsave', 'profilfsave', 'profildsave', 'profilssave', 'profileaave', 'profilewave',
                          'profileeave', 'profiledave', 'profilexave', 'profilezave', 'profilesqve', 'profileswve',
                          'profilessve', 'profilesxve', 'profileszve', 'profilesace', 'profilesafe', 'profilesage',
                          'profilesabe', 'profilesavw', 'profilesav3', 'profilesav4', 'profilesavr', 'profilesavf',
                          'profilesavd', 'profilesavs', 'oprofilesave', 'porofilesave', '0profilesave', 'p0rofilesave',
                          'lprofilesave', 'plrofilesave', 'perofilesave', 'preofilesave', 'p4rofilesave',
                          'pr4ofilesave', 'p5rofilesave', 'pr5ofilesave', 'ptrofilesave', 'prtofilesave',
                          'pgrofilesave', 'prgofilesave', 'pfrofilesave', 'prfofilesave', 'pdrofilesave',
                          'prdofilesave', 'priofilesave', 'proifilesave', 'pr9ofilesave', 'pro9filesave',
                          'pr0ofilesave', 'pro0filesave', 'prpofilesave', 'propfilesave', 'prlofilesave',
                          'prolfilesave', 'prkofilesave', 'prokfilesave', 'prodfilesave', 'profdilesave',
                          'prorfilesave', 'profrilesave', 'protfilesave', 'proftilesave', 'progfilesave',
                          'profgilesave', 'provfilesave', 'profvilesave', 'procfilesave', 'profcilesave',
                          'profuilesave', 'profiulesave', 'prof8ilesave', 'profi8lesave', 'prof9ilesave',
                          'profi9lesave', 'profoilesave', 'profiolesave', 'proflilesave', 'profkilesave',
                          'profiklesave', 'profjilesave', 'profijlesave', 'profilkesave', 'profiloesave',
                          'profiplesave', 'profilpesave', 'profilwesave', 'profilewsave', 'profil3esave',
                          'profile3save', 'profil4esave', 'profile4save', 'profilresave', 'profilersave',
                          'profilfesave', 'profilefsave', 'profildesave', 'profiledsave', 'profilsesave',
                          'profileasave', 'profileswave', 'profileseave', 'profilesdave', 'profilexsave',
                          'profilesxave', 'profilezsave', 'profileszave', 'profilesqave', 'profilesaqve',
                          'profilesawve', 'profilesasve', 'profilesaxve', 'profilesazve', 'profilesacve',
                          'profilesavce', 'profilesafve', 'profilesavfe', 'profilesagve', 'profilesavge',
                          'profilesabve', 'profilesavbe', 'profilesavwe', 'profilesavew', 'profilesav3e',
                          'profilesave3', 'profilesav4e', 'profilesave4', 'profilesavre', 'profilesaver',
                          'profilesavef', 'profilesavde', 'profilesaved', 'profilesavse', 'profilesaves', 'umper',
                          'dmper', 'duper', 'dumer', 'dumpr', 'dumpe', 'ddumper', 'duumper', 'dummper', 'dumpper',
                          'dumpeer', 'dumperr', 'udmper', 'dmuper', 'dupmer', 'dumepr', 'dumpre', 'sumper', 'eumper',
                          'rumper', 'fumper', 'cumper', 'xumper', 'dymper', 'd7mper', 'd8mper', 'dimper', 'dkmper',
                          'djmper', 'dhmper', 'dunper', 'dujper', 'dukper', 'dumoer', 'dum0er', 'dumler', 'dumpwr',
                          'dump3r', 'dump4r', 'dumprr', 'dumpfr', 'dumpdr', 'dumpsr', 'dumpee', 'dumpe4', 'dumpe5',
                          'dumpet', 'dumpeg', 'dumpef', 'dumped', 'sdumper', 'dsumper', 'edumper', 'deumper', 'rdumper',
                          'drumper', 'fdumper', 'dfumper', 'cdumper', 'dcumper', 'xdumper', 'dxumper', 'dyumper',
                          'duymper', 'd7umper', 'du7mper', 'd8umper', 'du8mper', 'diumper', 'duimper', 'dkumper',
                          'dukmper', 'djumper', 'dujmper', 'dhumper', 'duhmper', 'dunmper', 'dumnper', 'dumjper',
                          'dumkper', 'dumoper', 'dumpoer', 'dum0per', 'dump0er', 'dumlper', 'dumpler', 'dumpwer',
                          'dumpewr', 'dump3er', 'dumpe3r', 'dump4er', 'dumpe4r', 'dumprer', 'dumpfer', 'dumpefr',
                          'dumpder', 'dumpedr', 'dumpser', 'dumpesr', 'dumpere', 'dumper4', 'dumpe5r', 'dumper5',
                          'dumpetr', 'dumpert', 'dumpegr', 'dumperg', 'dumperf', 'dumperd', 'ownload', 'dwnload',
                          'donload', 'dowload', 'downoad', 'downlad', 'downlod', 'downloa', 'ddownload', 'doownload',
                          'dowwnload', 'downnload', 'downlload', 'downlooad', 'downloaad', 'downloadd', 'odwnload',
                          'dwonload', 'donwload', 'dowlnoad', 'downolad', 'downlaod', 'downloda', 'sownload',
                          'eownload', 'rownload', 'fownload', 'cownload', 'xownload', 'diwnload', 'd9wnload',
                          'd0wnload', 'dpwnload', 'dlwnload', 'dkwnload', 'doqnload', 'do2nload', 'do3nload',
                          'doenload', 'dodnload', 'dosnload', 'doanload', 'dowbload', 'dowhload', 'dowjload',
                          'dowmload', 'downkoad', 'downooad', 'downpoad', 'downliad', 'downl9ad', 'downl0ad',
                          'downlpad', 'downllad', 'downlkad', 'downloqd', 'downlowd', 'downlosd', 'downloxd',
                          'downlozd', 'downloas', 'downloae', 'downloar', 'downloaf', 'downloac', 'downloax',
                          'sdownload', 'dsownload', 'edownload', 'deownload', 'rdownload', 'drownload', 'fdownload',
                          'dfownload', 'cdownload', 'dcownload', 'xdownload', 'dxownload', 'diownload', 'doiwnload',
                          'd9ownload', 'do9wnload', 'd0ownload', 'do0wnload', 'dpownload', 'dopwnload', 'dlownload',
                          'dolwnload', 'dkownload', 'dokwnload', 'doqwnload', 'dowqnload', 'do2wnload', 'dow2nload',
                          'do3wnload', 'dow3nload', 'doewnload', 'dowenload', 'dodwnload', 'dowdnload', 'doswnload',
                          'dowsnload', 'doawnload', 'dowanload', 'dowbnload', 'downbload', 'dowhnload', 'downhload',
                          'dowjnload', 'downjload', 'dowmnload', 'downmload', 'downkload', 'downlkoad', 'downoload',
                          'downpload', 'downlpoad', 'downlioad', 'downloiad', 'downl9oad', 'downlo9ad', 'downl0oad',
                          'downlo0ad', 'downlopad', 'downlolad', 'downlokad', 'downloqad', 'downloaqd', 'downlowad',
                          'downloawd', 'downlosad', 'downloasd', 'downloxad', 'downloaxd', 'downlozad', 'downloazd',
                          'downloads', 'downloaed', 'downloade', 'downloard', 'downloadr', 'downloafd', 'downloadf',
                          'downloacd', 'downloadc', 'downloadx', 'rchive', 'achive', 'arhive', 'arcive', 'archve',
                          'archie', 'archiv', 'aarchive', 'arrchive', 'arcchive', 'archhive', 'archiive', 'archivve',
                          'archivee', 'rachive', 'acrhive', 'arhcive', 'arcihve', 'archvie', 'archiev', 'qrchive',
                          'wrchive', 'srchive', 'xrchive', 'zrchive', 'aechive', 'a4chive', 'a5chive', 'atchive',
                          'agchive', 'afchive', 'adchive', 'arxhive', 'ardhive', 'arfhive', 'arvhive', 'arcgive',
                          'arcyive', 'arcuive', 'arcjive', 'arcnive', 'arcbive', 'archuve', 'arch8ve', 'arch9ve',
                          'archove', 'archlve', 'archkve', 'archjve', 'archice', 'archife', 'archige', 'archibe',
                          'archivw', 'archiv3', 'archiv4', 'archivr', 'archivf', 'archivd', 'archivs', 'qarchive',
                          'aqrchive', 'warchive', 'awrchive', 'sarchive', 'asrchive', 'xarchive', 'axrchive',
                          'zarchive', 'azrchive', 'aerchive', 'arechive', 'a4rchive', 'ar4chive', 'a5rchive',
                          'ar5chive', 'atrchive', 'artchive', 'agrchive', 'argchive', 'afrchive', 'arfchive',
                          'adrchive', 'ardchive', 'arxchive', 'arcxhive', 'arcdhive', 'arcfhive', 'arvchive',
                          'arcvhive', 'arcghive', 'archgive', 'arcyhive', 'archyive', 'arcuhive', 'archuive',
                          'arcjhive', 'archjive', 'arcnhive', 'archnive', 'arcbhive', 'archbive', 'archiuve',
                          'arch8ive', 'archi8ve', 'arch9ive', 'archi9ve', 'archoive', 'archiove', 'archlive',
                          'archilve', 'archkive', 'archikve', 'archijve', 'archicve', 'archivce', 'archifve',
                          'archivfe', 'archigve', 'archivge', 'archibve', 'archivbe', 'archivwe', 'archivew',
                          'archiv3e', 'archive3', 'archiv4e', 'archive4', 'archivre', 'archiver', 'archivef',
                          'archivde', 'archived', 'archivse', 'archives', '/dump', '/profiledump', 'الملف الشخصي',
                          'প্রোফাইলডাম্প', 'abocament de perfils', 'volcado de perfil', 'پروفایل دامپ',
                          'profiilikaappi', 'પ્રોફાઇલડમ્પ', 'app', 'プロファイルダンプ', 'profilio dump', 'profilizgāzējs',
                          'प्रोफाइलडंप', 'zrzut profilu', 'профиледумп', 'utupaji wa wasifu', 'சுயவிவரத் திணிப்பு',
                          'ప్రొఫైల్ డంప్', 'profil dökümü', 'پروفائل ڈمپ', '配置文件转储', '配置文件轉儲',
                          'dumperprofile', 'profiliodump', 'utupajiwasifu', 'utupajiwawasifu', 'dueper', 'dumpey',
                          'ducper', 'dfmper', 'dumpexr', 'lumper', 'dumxer', 'dumpekr', 'dumqer', 'dumpver', 'dnumper',
                          'mumper', 'dumpen', 'daumper', 'dumpkr', 'dumzper', 'dumpyer', 'dumperj', 'dumpnr', 'dummer',
                          'kumper', 'damper', 'dumcper', 'dumpvr', 'dumker', 'dumier', 'dumpaer', 'dumperv', 'dudmper',
                          'dumhper', 'dumcer', 'duxper', 'pumper', 'dumver', 'dumperk', 'domper', 'wdumper', 'dusmper',
                          'numper', 'dumper', 'adumper', 'dumpej', 'dumpeir', 'dumpea', 'dumpuer', 'dwumper', 'dumpevr',
                          'dnmper', 'dumuer', 'dpmper', 'dumrer', 'dumyper', 'dtumper', 'dudper', 'dtmper', 'udumper',
                          'dulper', 'dufper', 'dumpebr', 'dumpezr', 'dumpern', 'dumeper', 'dumpers', 'bumper',
                          'dumperz', 'dqumper', 'dumgper', 'dulmper', 'dcmper', 'yumper', 'iumper', 'dumiper',
                          'dumbper', 'dumperl', 'dumfer', 'duzper', 'dumperp', 'dpumper', 'dzmper', 'dumpqr', 'dusper',
                          'dupper', 'dumpejr', 'zdumper', 'hdumper', 'dbmper', 'dubper', 'dumperc', 'dumpmer', 'duqper',
                          'dumpeh', 'ddmper', 'zumper', 'dgumper', 'duomper', 'duyper', 'dumpir', 'dumder', 'tumper',
                          'dumperq', 'dumher', 'odumper', 'dumperm', 'oumper', 'dumpel', 'dumsper', 'duwper', 'dumyer',
                          'dumner', 'dumpez', 'dumdper', 'dbumper', 'dumperw', 'dumaer', 'dumpher', 'jumper', 'dumpem',
                          'dumpeqr', 'dumpei', 'dumpepr', 'dumpev', 'dumpeu', 'duqmper', 'dumpec', 'dumpehr', 'jdumper',
                          'tdumper', 'dufmper', 'dumaper', 'dumpelr', 'dubmper', 'dumser', 'kdumper', 'dumpep',
                          'dumperb', 'duhper', 'dumpmr', 'duemper', 'dsmper', 'duoper', 'dumpner', 'dumfper', 'dumpjer',
                          'duxmper', 'dxmper', 'dumpery', 'dugmper', 'dumpear', 'mdumper', 'dumptr', 'vumper', 'dutper',
                          'duaper', 'dqmper', 'dumpker', 'dumplr', 'duuper', 'dumpcr', 'durper', 'dumpemr', 'gumper',
                          'dwmper', 'dumpxr', 'dlmper', 'dumpeor', 'dumzer', 'dumpew', 'dumpbr', 'dumger', 'aumper',
                          'ndumper', 'dupmper', 'duiper', 'dumuper', 'duamper', 'dumphr', 'duvper', 'dumpyr', 'dumeer',
                          'dumpeo', 'dumpcer', 'dumpzer', 'dumter', 'dumpeyr', 'bdumper', 'dumpek', 'ducmper',
                          'dumperi', 'dutmper', 'dumpger', 'dumpzr', 'dumrper', 'dumperu', 'dumqper', 'dumpqer',
                          'pdumper', 'demper', 'drmper', 'dumpex', 'dumppr', 'dvumper', 'dumpes', 'dumpero', 'idumper',
                          'dumvper', 'dzumper', 'dumpur', 'dgmper', 'dumpar', 'dumxper', 'wumper', 'ldumper', 'dvmper',
                          'duzmper', 'dugper', 'qumper', 'duwmper', 'dumpeb', 'dumpier', 'dumwer', 'dumtper', 'qdumper',
                          'doumper', 'dumperh', 'dumwper', 'dumpecr', 'dumpera', 'dumpter', 'gdumper', 'dumpjr',
                          'dmmper', 'dumpor', 'dumpeur', 'dumperx', 'dlumper', 'duvmper', 'dmumper', 'ydumper',
                          'dumpeq', 'uumper', 'dumber', 'durmper', 'dumpber', 'dumpgr', 'humper', 'dumpxer', 'dumjer',
                          'dumpenr', 'vdumper', 'd6mper', 'd^mper', 'd&mper', 'd*mper', 'du,per', 'du<per', 'dum9er',
                          'dum-er', 'dum[er', 'dum]er', 'dum;er', 'dum(er', 'dum)er', 'dum_er', 'dum=er', 'dum+er',
                          'dum{er', 'dum}er', 'dum:er', 'dump2r', 'dump$r', 'dump#r', 'dump@r', 'dumpe3', 'dumpe#',
                          'dumpe$', 'dumpe%', 'slver', 'saer', 'savor', 'asver', 'saevr', 'gaver', 'sauer', 'sver',
                          'savver', 'sjver', 'svaer', 'sanver', 'saaver', 'sadver', 'savler', 'sqaver', 'sader',
                          'aver', 'samver', 'ksaver', 'sajer', 'savaer', 'saqver', 'savzer', 'sagver', 'sawer',
                          'sbaver', 'syver', 'savner', 'saoer', 'savers', 'saveri', 'saever', 'aaver', 'savdr',
                          'soaver', 'saverz', 'uaver', 'savcer', 'sager', 'seaver', 'saverh', 'sayver', 'saverl',
                          'lsaver', 'savehr', 'snaver', 'raver', 'savser', 'asaver', 'saverq', 'sjaver',
                          'savder', 'ysaver', 'ssaver', 'savetr', 'savezr', 'saverb', 'savxr', 'saveru', 'savero',
                          'maver', 'saber', 'savger', 'saverd', 'saqer', 'savar', 'scaver', 'savear', 'safver', 'saaer',
                          'nsaver', 'saner', 'szver', 'paver', 'stver', 'savebr', 'haver', 'isaver', 'savqer', 'msaver',
                          'saverj', 'savtr', 'yaver', 'saper', 'gsaver', 'sahver', 'samer', 'xsaver', 'savenr', 'savcr',
                          'savera', 'shver', 'savegr', 'savir', 'savnr', 'sbver', 'sarer', 'savpr', 'savier',
                          'savfer', 'saveyr', 'saverm', 'saveir', 'savvr', 'javer', 'saveer', 'satver', 'saser',
                          'usaver', 'sav4r', 'sav3r', 'sav2r', 'sav$r', 'sav#r', 'sav@r', 'save5', 'save#',
                          'save$', 'save%', 'profiledumph', 'profileduvmp', 'profiledemp', 'wrofiledump',
                          'pronfiledump', 'profiledzump', 'profiledubp', 'purofiledump', 'proliledump', 'pwrofiledump',
                          'profiletump', 'profilzdump', 'profilevump', 'profiredump', 'profmiledump', 'profiledmump',
                          'przofiledump', 'profqledump', 'profiledumip', 'prnfiledump', 'prhofiledump', 'trofiledump',
                          'xrofiledump', 'profiledumvp', 'profxiledump', 'prxofiledump', 'profiludump', 'profilemdump',
                          'mrofiledump', 'profiledumfp', 'profiledufp', 'profilenump', 'fprofiledump', 'profiledumhp',
                          'profiledumk', 'profilewump', 'profitedump', 'profgledump', 'krofiledump', 'profiledvump',
                          'profihledump', 'profilbedump', 'profiledumi', 'profilednump', 'projiledump', 'profiljedump',
                          'profilebdump', 'pxofiledump', 'propiledump', 'profilegdump', 'profileduma', 'prufiledump',
                          'grofiledump', 'prmfiledump', 'profilvdump', 'profiledxmp', 'profidedump', 'prrfiledump',
                          'erofiledump', 'sprofiledump', 'profhledump', 'prsofiledump', 'profbledump', 'profiledumpu',
                          'profigedump', 'profizedump', 'profileduxp', 'uprofiledump', 'profiledumpr', 'mprofiledump',
                          'profivedump', 'proeiledump', 'profiledbmp', 'poofiledump', 'profiledumxp', 'profiledudp',
                          'profxledump', 'profiledumh', 'profpiledump', 'pyrofiledump', 'profileduyp', 'profziledump',
                          'profilhedump', 'profwledump', 'profiiedump', 'profilydump', 'prsfiledump',
                          'profileduip', 'psrofiledump', 'profilevdump', 'profiledumpn', 'profiledudmp', 'proailedump',
                          'profiledume', 'profqiledump', 'prefiledump', 'pqrofiledump', 'profileqump', 'proftledump',
                          'vrofiledump', 'profileduop', 'profiledumpt', 'prowfiledump', 'profiledusp', 'pmrofiledump',
                          'profilepump', 'profiluedump', 'profilcdump', 'profiledumq', 'zrofiledump', 'profileduwp',
                          'profilejdump', 'profileodump', 'pbrofiledump', 'xprofiledump', 'prowiledump', 'profiletdump',
                          'profiledumw', 'profiledulmp', 'profiledumpc', 'profileldump', 'prqfiledump', 'profijedump',
                          'profileiump', 'pkrofiledump', 'profileddmp', 'profilgdump', 'pruofiledump', 'nprofiledump',
                          'profilxedump', 'profiledumcp', 'profileduamp', 'profiledumyp', 'profiladump', 'profiledugmp',
                          'profileydump', 'proafiledump', 'ppofiledump', 'profiaedump', 'iprofiledump', 'profilmdump',
                          'prjofiledump', 'aprofiledump', 'profilnedump', 'profileyump', 'pwofiledump', 'prhfiledump',
                          'proficledump', 'profiledsmp', 'profilehump', 'profiledumm', 'profiledubmp', 'profilezdump',
                          'phofiledump', 'profiledutp', 'eprofiledump', 'prohiledump', 'proqiledump', 'profvledump',
                          'profzledump', 'proxfiledump', 'profilkdump', 'profiledlump', 'profimledump', 'profiledumap',
                          'profiledumt', 'bprofiledump', 'prdfiledump', 'profiledumv', 'profileduvp', 'profpledump',
                          'psofiledump', 'profileducmp', 'prwfiledump', 'pxrofiledump', 'przfiledump', 'profiuedump',
                          'promiledump', 'profeledump', 'profiledtmp', 'profileduqmp', 'rprofiledump', 'yrofiledump',
                          'gprofiledump', 'prohfiledump', 'prwofiledump', 'plofiledump', 'profiledumps', 'profiledumpg',
                          'profilxdump', 'profiledumpq', 'wprofiledump', 'profifledump', 'profyledump', 'profiledupp',
                          'irofiledump', 'profibedump', 'profiyledump', 'proxiledump', 'prouiledump', 'profiledumep',
                          'pvofiledump', 'profiledrmp', 'profileduwmp', 'profileidump', 'profileducp', 'profyiledump',
                          'praofiledump', 'pmofiledump', 'profilldump', 'hprofiledump', 'profiledumtp', 'prbfiledump',
                          'proziledump', 'profilcedump', 'profhiledump', 'profiledvmp', 'profilendump', 'profilehdump',
                          'profiledumbp', 'profifedump', 'pnrofiledump', 'profilhdump', 'profiledumpz', 'qprofiledump',
                          'prnofiledump', 'profilidump', 'profiledumz', 'profileuump', 'profimedump', 'rrofiledump',
                          'drofiledump', 'profinledump', 'proyiledump', 'profiledamp', 'profilemump', 'prqofiledump',
                          'pyofiledump', 'profiledumpy', 'profilejump', 'profiltdump', 'profilekdump', 'profinedump',
                          'probiledump', 'prokiledump', 'profiledupmp', 'profiledumpw', 'profiledzmp', 'profiledpmp',
                          'profilodump', 'profiledutmp', 'prosiledump', 'hrofiledump', 'profiledumrp', 'profeiledump',
                          'profiledgmp', 'profiqedump', 'pzrofiledump', 'profiledumf', 'profiledumpj', 'profitledump',
                          'profiledqmp', 'profigledump', 'profibledump', 'profilgedump', 'profilednmp', 'profileduhp',
                          'proiiledump', 'prcfiledump', 'profiyedump', 'pjrofiledump', 'promfiledump', 'profiledurp',
                          'profilqdump', 'profilpdump', 'projfiledump', 'qrofiledump', 'profiliedump', 'profiledusmp',
                          'profiledpump', 'profiledomp', 'parofiledump', 'profiledumpa', 'pqofiledump', 'profilqedump',
                          'profrledump', 'profidledump', 'frofiledump', 'prffiledump', 'profilezump', 'profcledump',
                          'proyfiledump', 'prjfiledump', 'prooiledump', 'phrofiledump', 'profisedump', 'profiledumup',
                          'profileduemp', 'profiledtump', 'profiledumb', 'profiledumu', 'profiledumpx', 'profiledumy',
                          'proficedump', 'profiledumwp', 'profiledgump', 'profilebump', 'profiledumc', 'dprofiledump',
                          'profilbdump', 'profiltedump', 'profiwedump', 'pcrofiledump', 'puofiledump', 'paofiledump',
                          'profiledwump', 'profiledums', 'proniledump', 'profiledumpi', 'profilndump', 'profnledump',
                          'pzofiledump', 'profieledump', 'profdledump', 'profiledmmp', 'prafiledump', 'profileduomp',
                          'profaledump', 'nrofiledump', 'profiledoump', 'profiledaump', 'profiledumg', 'profieedump',
                          'profilyedump', 'profiledumpm', 'profiledqump', 'profilvedump', 'profiledumn', 'proffledump',
                          'proqfiledump', 'profilegump', 'profiledbump', 'proufiledump', 'cprofiledump', 'profileduxmp',
                          'prmofiledump', 'profileadump', 'profiledumpb', 'profixedump', 'prozfiledump', 'brofiledump',
                          'profisledump', 'profileduep', 'pnofiledump', 'prtfiledump', 'profileduup', 'profilaedump',
                          'profiledfmp', 'profiwledump', 'profiledumx', 'profiledumpd', 'profiledlmp', 'profilmedump',
                          'profbiledump', 'profileduzmp', 'profiqledump', 'profileudump', 'pjofiledump', 'profiledwmp',
                          'profivledump', 'pvrofiledump', 'profihedump', 'profiledumdp', 'profiledumpe', 'prxfiledump',
                          'profiledumgp', 'profirledump', 'profiljdump', 'proefiledump', 'profsiledump', 'profizledump',
                          'pkofiledump', 'zprofiledump', 'profiledumpk', 'profwiledump', 'profiledufmp', 'arofiledump',
                          'profiledulp', 'vprofiledump', 'profileduqp', 'profileduap', 'profiledumr', 'srofiledump',
                          'profilepdump', 'yprofiledump', 'profniledump', 'profialedump', 'profileqdump', 'profiledcmp',
                          'profileaump', 'tprofiledump', 'piofiledump', 'profileduzp', 'profileoump', 'profixledump',
                          'urofiledump', 'profiledugp', 'pcofiledump', 'profiledumpf', 'prcofiledump', 'profsledump',
                          'prvofiledump', 'profiledumzp', 'profiledumd', 'prgfiledump', 'crofiledump', 'profiledumpv',
                          'pirofiledump', 'probfiledump', 'jrofiledump', 'profiledumj', 'prbofiledump', 'prvfiledump',
                          'profiledumqp', 'profiledurmp', 'prosfiledump', 'pbofiledump', 'profiledumsp', 'kprofiledump',
                          'pryfiledump', 'profailedump', 'profilzedump', 'profilekump', 'profmledump', 'profilelump',
                          'jprofiledump', 'pryofiledump', '9rofiledump', '-rofiledump', '[rofiledump', ']rofiledump',
                          ';rofiledump', '(rofiledump', ')rofiledump', '_rofiledump', '=rofiledump', '+rofiledump',
                          '{rofiledump', '}rofiledump', ':rofiledump', 'p3ofiledump', 'p#ofiledump', 'p$ofiledump',
                          'p%ofiledump', 'pr8filedump', 'pr;filedump', 'pr*filedump', 'pr(filedump', 'pr)filedump',
                          'prof7ledump', 'prof&ledump', 'prof*ledump', 'prof(ledump', 'profi;edump', 'profi/edump',
                          'profi.edump', 'profi,edump', 'profi?edump', 'profi>edump', 'profi<edump', 'profil2dump',
                          'profil$dump', 'profil#dump', 'profil@dump', 'profiled6mp', 'profiled^mp', 'profiled&mp',
                          'profiled*mp', 'profiledu,p', 'profiledu<p', 'profiledum9', 'profiledum-', 'profiledum[',
                          'profiledum]', 'profiledum;', 'profiledum(', 'profiledum)', 'profiledum_', 'profiledum=',
                          'profiledum+', 'profiledum{', 'profiledum}', 'profiledum:', 'grofilesave', 'profilhsave',
                          'profilesavp', 'proficesave', 'profilesalve', 'profilesaveu', 'proiilesave', 'profmilesave',
                          'profxilesave', 'profihesave', 'prvfilesave', 'prosilesave', 'profilesavh', 'profiljsave',
                          'profilesavj', 'profilesavev', 'prvofilesave', 'propilesave', 'prhofilesave', 'gprofilesave',
                          'yrofilesave', 'prozfilesave', 'profilesavo', 'profblesave', 'profiwesave', 'profilesavb',
                          'rprofilesave', 'profilesaze', 'profilesavy', 'pqofilesave', 'profzlesave', 'prgfilesave',
                          'prooilesave', 'qprofilesave', 'prozilesave', 'pmofilesave', 'pxofilesave', 'profilesfave',
                          'profailesave', 'phrofilesave', 'pruofilesave', 'profilesavje', 'frofilesave', 'profilehave',
                          'proxilesave', 'vrofilesave', 'profilescave', 'profqlesave', 'profilvesave', 'erofilesave',
                          'profilesauve', 'profilesavme', 'profilesave', 'prmofilesave', 'profilesavea', 'profileshve',
                          'prcfilesave', 'pryfilesave', 'profilejave', 'nrofilesave', 'pnrofilesave', 'profilesavl',
                          'profilesape', 'profilesavex', 'jprofilesave', 'proqfilesave', 'profilegsave', 'poofilesave',
                          'profplesave', 'profilejsave', 'proftlesave', 'proeilesave', 'profimlesave', 'profilesavu',
                          'profilesmve', 'prsfilesave', 'profvlesave', 'profilesamve', 'profilesjave', 'profilmesave',
                          'profiyesave', 'profiliesave', 'profmlesave', 'profilepsave', 'pirofilesave', 'profilelave',
                          'puofilesave', 'profiylesave', 'profibesave', 'profilesaqe', 'profdlesave', 'profilesavye',
                          'profilesale', 'prolilesave', 'profilesavc', 'prufilesave', 'profixlesave', 'prsofilesave',
                          'profilesavz', 'profilesava', 'prbofilesave', 'profilesahve', 'profiuesave', 'profwlesave',
                          'trofilesave', 'prbfilesave', 'projfilesave', 'profilysave', 'profilesare', 'prxfilesave',
                          'pkofilesave', 'profclesave', 'profilesavm', 'profilesuve', 'profiwlesave', 'profilestve',
                          'profilesavke', 'profileusave', 'profivlesave', 'promilesave', 'profqilesave', 'profijesave',
                          'proficlesave', 'profirlesave', 'profpilesave', 'prcofilesave', 'profilesahe', 'profiaesave',
                          'profilcesave', 'proyilesave', 'proafilesave', 'profilesavt', 'psrofilesave', 'profilesnave',
                          'profilesavue', 'profwilesave', 'profilesaive', 'hrofilesave', 'profilesjve', 'prqofilesave',
                          'prffilesave', 'profilesavte', 'prokilesave', 'dprofilesave', 'xrofilesave', 'profiljesave',
                          'profilesavg', 'profilerave', 'projilesave', 'profylesave', 'profilekave', 'profilesyave',
                          'profilefave', 'prtfilesave', 'profillsave', 'profilesavne', 'profilesane', 'praofilesave',
                          'proxfilesave', 'tprofilesave', 'profilesaae', 'profilesgave', 'profivesave', 'prqfilesave',
                          'profilesarve', 'profalesave', 'profilensave', 'profitesave', 'pmrofilesave', 'profieesave',
                          'prnofilesave', 'profilesiave', 'jrofilesave', 'profilesavel', 'profilyesave', 'pjofilesave',
                          'profnlesave', 'profilebsave', 'profilesatve', 'profilqsave', 'prhfilesave', 'profileosave',
                          'prowfilesave', 'proefilesave', 'profilesbave', 'profilesavx', 'profglesave', 'profinlesave',
                          'pvofilesave', 'profilzesave', 'profizesave', 'profilesaove', 'profxlesave', 'profilesaie',
                          'profilesfve', 'profilesavem', 'profnilesave', 'profbilesave', 'profilesavk', 'urofilesave',
                          'profilesavep', 'profiqesave', 'pvrofilesave', 'proyfilesave', 'iprofilesave', 'profilxesave',
                          'profifesave', 'fprofilesave', 'srofilesave', 'profilesyve', 'xprofilesave', 'profilesgve',
                          'psofilesave', 'profilasave', 'pzofilesave', 'prxofilesave', 'profilespve', 'profilesavze',
                          'profilesaveq', 'profilhesave', 'profiluesave', 'profilevsave', 'profilesaee', 'profilesnve',
                          'profilesvave', 'profileslve', 'arofilesave', 'pbrofilesave', 'prowilesave', 'profilcsave',
                          'profilesuave', 'profilesavei', 'profilesavoe', 'prefilesave', 'profilesmave', 'profilesove',
                          'profilesadve', 'prosfilesave', 'pxrofilesave', 'prjfilesave', 'profilesbve', 'profilecave',
                          'zrofilesave', 'aprofilesave', 'piofilesave', 'profilesaye', 'prmfilesave', 'profilzsave',
                          'profileksave', 'profilnsave', 'irofilesave', 'pwofilesave', 'profilevave', 'profilespave',
                          'prjofilesave', 'profislesave', 'profilesavej', 'profilebave', 'bprofilesave', 'profilesavi',
                          'profidlesave', 'plofilesave', 'profilescve', 'pkrofilesave', 'profhlesave', 'crofilesave',
                          'profileskve', 'profilelsave', 'profilegave', 'profilesavek', 'profihlesave', 'uprofilesave',
                          'profilgsave', 'profitlesave', 'profilepave', 'profflesave', 'profilesavv', 'pqrofilesave',
                          'profilosave', 'vprofilesave', 'profiqlesave', 'prafilesave', 'profigesave', 'profilesade',
                          'sprofilesave', 'profidesave', 'pyrofilesave', 'mrofilesave', 'profinesave', 'profimesave',
                          'profilksave', 'phofilesave', 'ppofilesave', 'profilbsave', 'profilesawe', 'prwfilesave',
                          'wrofilesave', 'hprofilesave', 'profilesaxe', 'profilesaoe', 'profileqsave', 'profilesavae',
                          'zprofilesave', 'profiiesave', 'prwofilesave', 'prrfilesave', 'profilesavey', 'profisesave',
                          'probilesave', 'profilehsave', 'profilesaven', 'przofilesave', 'profileysave', 'profyilesave',
                          'profileskave', 'profilaesave', 'pryofilesave', 'cprofilesave', 'nprofilesave',
                          'pronfilesave', 'mprofilesave', 'profilesayve', 'profialesave', 'prdfilesave', 'profilesapve',
                          'profilesame', 'proailesave', 'profilesavq', 'profilusave', 'profileuave', 'profilesive',
                          'profilesaje', 'profilesavhe', 'profilgesave', 'purofilesave', 'profilesoave', 'wprofilesave',
                          'profiltesave', 'profilesrve', 'profilesaveh', 'pcrofilesave', 'profiblesave', 'profilesavn',
                          'profilnesave', 'profileisave', 'promfilesave', 'pyofilesave', 'profiresave', 'paofilesave',
                          'profilesrave', 'prohilesave', 'probfilesave', 'profilesake', 'profilesavet', 'profilesavie',
                          'profileyave', 'profilesdve', 'pzrofilesave', 'profiflesave', 'profilpsave', 'przfilesave',
                          'profrlesave', 'profilesavec', 'profslesave', 'proqilesave', 'profilesaveo', 'profilesavpe',
                          'profeilesave', 'prnfilesave', 'eprofilesave', 'kprofilesave', 'profzilesave', 'profixesave',
                          'pronilesave', 'profilestave', 'qrofilesave', 'profhilesave', 'profilesate', 'pjrofilesave',
                          'profilesaue', 'prohfilesave', 'profilenave', 'pnofilesave', 'profiletave', 'profilisave',
                          'profilemsave', 'profilesavqe', 'profilesaveg', 'profelesave', 'profilesavez', 'profilemave',
                          'profilecsave', 'profilesajve', 'profsilesave', 'parofilesave', 'profilesaeve',
                          'profilqesave', 'profilesaveb', 'profileiave', 'profiglesave', 'profilesase', 'profileslave',
                          'profileoave', 'profilesavxe', 'pwrofilesave', 'profielesave', 'drofilesave', 'profileshave',
                          'profizlesave', 'proufilesave', 'prouilesave', 'profilbesave', 'profilmsave', 'profilesakve',
                          'profilxsave', 'brofilesave', 'profilesanve', 'pcofilesave', 'yprofilesave', 'profilesavle',
                          'pbofilesave', 'profiletsave', 'profilvsave', 'profileqave', 'krofilesave', 'profilesvve',
                          'profileseve', 'profiltsave', 'rrofilesave', '9rofilesave', '-rofilesave', '[rofilesave',
                          ']rofilesave', ';rofilesave', '(rofilesave', ')rofilesave', '_rofilesave', '=rofilesave',
                          '+rofilesave', '{rofilesave', '}rofilesave', ':rofilesave', 'p3ofilesave', 'p#ofilesave',
                          'p$ofilesave', 'p%ofilesave', 'pr8filesave', 'pr;filesave', 'pr*filesave', 'pr(filesave',
                          'pr)filesave', 'prof7lesave', 'prof&lesave', 'prof*lesave', 'prof(lesave', 'profi;esave',
                          'profi/esave', 'profi.esave', 'profi,esave', 'profi?esave', 'profi>esave', 'profi<esave',
                          'profil2save', 'profil$save', 'profil#save', 'profil@save', 'profilesav2', 'profilesav$',
                          'profilesav#', 'profilesav@', 'qdownload', 'dbownload', 'zownload', 'downuoad', 'dowonload',
                          'downlold', 'downloed', 'downloatd', 'dojwnload', 'downloag', 'wdownload', 'dowinload',
                          'wownload', 'dozwnload', 'downzoad', 'dvownload', 'dhwnload', 'downyload', 'downwoad',
                          'downloavd', 'dwwnload', 'downlnoad', 'downloadn', 'downlopd', 'downloadh', 'duwnload',
                          'uownload', 'nownload', 'dowrload', 'downioad', 'downlzad', 'downloaid', 'downgload',
                          'qownload', 'hdownload', 'dovwnload', 'downlood', 'doznload', 'oownload', 'dowgnload',
                          'dolnload', 'downloan', 'downlyad', 'downljad', 'downlhoad', 'downloagd', 'download',
                          'downloadz', 'downlotd', 'downlsad', 'downlfoad', 'dounload', 'downtoad', 'downloah',
                          'downloab', 'downboad', 'dowtload', 'downxload', 'downlohd', 'dowpnload', 'downloam',
                          'downloaz', 'docnload', 'downlmad', 'dowvnload', 'downcload', 'dowxnload', 'dwownload',
                          'dofwnload', 'dovnload', 'dowlload', 'lownload', 'downwload', 'downaoad', 'doynload',
                          'doywnload', 'downfload', 'dbwnload', 'downlogd', 'dowlnload', 'dowyload', 'downsoad',
                          'domwnload', 'downnoad', 'dowunload', 'odownload', 'dotwnload', 'downloadu', 'douwnload',
                          'docwnload', 'dzownload', 'downlorad', 'downloada', 'downloadq', 'downloamd', 'downloyd',
                          'downloao', 'downloadg', 'dowoload', 'downlead', 'dognload', 'dowcload', 'downloat',
                          'doknload', 'downqload', 'downloadw', 'downlyoad', 'doweload', 'downloau', 'ndownload',
                          'dowxload', 'dowiload', 'townload', 'dgwnload', 'downeoad', 'aownload', 'downlqoad',
                          'downloaq', 'dowvload', 'downluoad', 'dowqload', 'ldownload', 'downdoad', 'downloadl',
                          'downvoad', 'downzload', 'vownload', 'dawnload', 'doinload', 'downlroad', 'downloadm',
                          'downloadk', 'downloadi', 'dtwnload', 'dobnload', 'dyownload', 'dopnload', 'bownload',
                          'downhoad', 'downlomd', 'downloadp', 'dnwnload', 'downlonad', 'doonload', 'downloaod',
                          'dywnload', 'downloahd', 'downgoad', 'dotnload', 'iownload', 'jdownload', 'dogwnload',
                          'downlxad', 'downjoad', 'gownload', 'dowzload', 'downljoad', 'zdownload', 'dowwload',
                          'mownload', 'udownload', 'downlojd', 'dqownload', 'downlotad', 'donnload', 'downloap',
                          'dowfnload', 'dcwnload', 'downlojad', 'downlomad', 'downlord', 'downfoad', 'downlfad',
                          'downleoad', 'dowuload', 'downloud', 'idownload', 'downltoad', 'dohwnload', 'downlaad',
                          'downlwad', 'jownload', 'mdownload', 'dzwnload', 'dowkload', 'downloakd', 'downloady',
                          'downlboad', 'downlmoad', 'downlobad', 'dvwnload', 'downsload', 'downloai', 'dqwnload',
                          'gdownload', 'downlocd', 'downuload', 'dohnload', 'downlofad', 'adownload', 'downlobd',
                          'downloead', 'ydownload', 'duownload', 'downqoad', 'downloal', 'downlgoad', 'downluad',
                          'downmoad', 'hownload', 'downlgad', 'downlnad', 'dewnload', 'downlcad', 'dtownload',
                          'domnload', 'dmownload', 'downloayd', 'downloaw', 'downldoad', 'downrload', 'downeload',
                          'downlvad', 'downlsoad', 'doxnload', 'downroad', 'doxwnload', 'downlaoad', 'djownload',
                          'yownload', 'drwnload', 'dnownload', 'downlhad', 'downcoad', 'downldad', 'downloadj',
                          'downloabd', 'dhownload', 'downloyad', 'downxoad', 'dowpload', 'downvload', 'dswnload',
                          'downlqad', 'downloapd', 'downloaj', 'downlogad', 'downlocad', 'downloand', 'downlohad',
                          'tdownload', 'dornload', 'dofnload', 'downlokd', 'downlodad', 'kownload', 'downyoad',
                          'dobwnload', 'downlrad', 'dowaload', 'dowdload', 'dowsload', 'djwnload', 'dowznload',
                          'downloak', 'bdownload', 'dowknload', 'dowrnload', 'downloajd', 'dojnload', 'downlofd',
                          'downtload', 'downlond', 'donwnload', 'downloadv', 'downloaa', 'downloado', 'ddwnload',
                          'downlzoad', 'dgownload', 'pdownload', 'downlovad', 'dowtnload', 'downloadt', 'dxwnload',
                          'dfwnload', 'downdload', 'downlvoad', 'downloadb', 'dowfload', 'kdownload', 'dowgload',
                          'downlovd', 'downloaud', 'dowynload', 'dmwnload', 'downaload', 'downloid', 'dowcnload',
                          'downlbad', 'downlcoad', 'pownload', 'downloay', 'downlodd', 'downlwoad', 'downltad',
                          'daownload', 'downloald', 'downlxoad', 'downloav', 'dorwnload', 'downlouad', 'downiload',
                          'vdownload', 'd8wnload', 'd;wnload', 'd*wnload', 'd(wnload', 'd)wnload', 'do1nload',
                          'do!nload', 'do@nload', 'do#nload', 'dow,load', 'dow<load', 'down;oad', 'down/oad',
                          'down.oad', 'down,oad', 'down?oad', 'down>oad', 'down<oad', 'downl8ad', 'downl;ad',
                          'downl*ad', 'downl(ad', 'downl)ad', 'arhhive', 'arcoive', 'archivie', 'archivv', 'archiva',
                          'archaive', 'arcaive', 'grchive', 'arcwive', 'archxive', 'arghive', 'archnve', 'archivpe',
                          'archive', 'archeve', 'acrchive', 'archivea', 'arahive', 'uarchive', 'archdve', 'archire',
                          'arctive', 'archite', 'archixe', 'aryhive', 'arlhive', 'lrchive', 'darchive', 'ahrchive',
                          'barchive', 'archvve', 'arrhive', 'arhchive', 'archqive', 'archioe', 'archivec', 'aychive',
                          'archixve', 'archrive', 'arckive', 'arichive', 'arphive', 'archine', 'archivle', 'arceive',
                          'archipve', 'archmve', 'archpive', 'archisve', 'archivoe', 'archxve', 'arcrhive', 'ayrchive',
                          'archiveq', 'auchive', 'armhive', 'archivl', 'arcpive', 'archivz', 'jrchive', 'carchive',
                          'archcive', 'ahchive', 'arccive', 'archhve', 'archiveb', 'archzive', 'arcsive', 'archivke',
                          'archiwve', 'archivue', 'archwve', 'archsve', 'arclhive', 'vrchive', 'archiveu', 'archivm',
                          'arcshive', 'archvive', 'aschive', 'arbchive', 'avchive', 'hrchive', 'frchive', 'archivex',
                          'orchive', 'archivem', 'archidve', 'archivez', 'arckhive', 'azchive', 'erchive', 'axchive',
                          'prchive', 'amchive', 'varchive', 'aruhive', 'archsive', 'archile', 'akrchive', 'archise',
                          'aurchive', 'mrchive', 'archivp', 'archieve', 'archivek', 'crchive', 'archpve', 'archivet',
                          'brchive', 'archyve', 'archivme', 'archivo', 'archiqe', 'arcvive', 'archivei', 'archihe',
                          'archiqve', 'nrchive', 'aachive', 'yrchive', 'airchive', 'arcdive', 'archivb', 'archinve',
                          'armchive', 'arcqive', 'archave', 'arschive', 'archivj', 'architve', 'archivy', 'archfve',
                          'archiveg', 'archivxe', 'aorchive', 'archiye', 'arcphive', 'archivae', 'anchive', 'archrve',
                          'arqchive', 'larchive', 'archivye', 'farchive', 'archiae', 'arkhive', 'abrchive', 'aichive',
                          'archize', 'marchive', 'archije', 'arczive', 'archzve', 'parchive', 'archivu', 'arjchive',
                          'alrchive', 'archgve', 'arachive', 'arcrive', 'archiave', 'archiven', 'archivqe', 'acchive',
                          'archide', 'archbve', 'archmive', 'archivx', 'jarchive', 'archiveo', 'arohive', 'archivi',
                          'archivt', 'archqve', 'arzhive', 'arwhive', 'arkchive', 'amrchive', 'arshive', 'akchive',
                          'archdive', 'archivte', 'archwive', 'archivh', 'archiie', 'aprchive', 'rrchive', 'arpchive',
                          'abchive', 'arclive', 'arcmhive', 'garchive', 'ajchive', 'archivne', 'irchive', 'archivc',
                          'yarchive', 'archivn', 'archivq', 'arochive', 'arihive', 'alchive', 'arcfive', 'archiue',
                          'arcwhive', 'archike', 'archiyve', 'arciive', 'iarchive', 'tarchive', 'avrchive', 'apchive',
                          'archiwe', 'karchive', 'archeive', 'archivk', 'arnhive', 'earchive', 'archivey', 'archizve',
                          'aqchive', 'harchive', 'archiveh', 'ajrchive', 'arcqhive', 'archcve', 'arcahive', 'arcihive',
                          'archivej', 'aochive', 'archirve', 'oarchive', 'arbhive', 'archivel', 'archipe', 'arqhive',
                          'arcmive', 'arcxive', 'arychive', 'archtve', 'arehive', 'rarchive', 'arczhive', 'anrchive',
                          'archimve', 'arcehive', 'arcthive', 'archivg', 'arwchive', 'archivep', 'archime', 'archfive',
                          'awchive', 'archivhe', 'arthive', 'urchive', 'archiee', 'aruchive', 'archihve', 'arjhive',
                          'narchive', 'archivze', 'archivev', 'krchive', 'archtive', 'arnchive', 'arcohive', 'archivje',
                          'trchive', 'drchive', 'arzchive', 'arlchive', 'a3chive', 'a#chive', 'a$chive', 'a%chive',
                          'arch7ve', 'arch&ve', 'arch*ve', 'arch(ve', 'archiv2', 'archiv$', 'archiv#', 'archiv@',
                          '/dumper', '/saver', '/profilesave', '/download', '/archive'],
                 extras={'emoji': "library_floppydisc", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.slash.optout', True]
                 }, "dev": False,
                         "description_keys": ["profiledumper.meta.description"],
                         "name_key": "profiledumper.slash.name", "experimental": True},
                 brief="profiledumper.meta.brief",
                 description="{0}")
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

    @ext.slash_command(name='profiledump', name_localizations=stw.I18n.construct_slash_dict("profiledumper.slash.name"),  # yay (say yay if you're yay yay) 😱
                       description='Dumps your Fortnite profiles as JSON attachments',
                       description_localizations=stw.I18n.construct_slash_dict("profiledumper.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashprofiledump(self, ctx: discord.ApplicationContext,
                               token: Option(description="Your Epic Games authcode. Required unless you have an active "
                                                         "session.",
                                             description_localizations=stw.I18n.construct_slash_dict(
                                                 "generic.slash.token"),
                                             name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                                             min_length=32) = "",
                               auth_opt_out: Option(default="False",
                                                    description="Opt out of starting an authentication session",
                                                    description_localizations=stw.I18n.construct_slash_dict(
                                                        "generic.slash.optout"),
                                                    name_localizations=stw.I18n.construct_slash_dict(
                                                        "generic.meta.args.optout"),
                                                    choices=[
                                                        OptionChoice("Do not start an authentication session", "True",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.true")),
                                                        OptionChoice("Start an authentication session (Default)",
                                                                     "False",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the profile dumper command when called via slash

        Args:
            ctx: The context of the command.
            token: The authcode to use for authentication.
            auth_opt_out: Whether to opt out of starting an authentication session.
        """
        await self.profile_dump_command(ctx, token, not eval(auth_opt_out))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(ProfileDump(client))

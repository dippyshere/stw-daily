"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the profile dumper command. Returns a dump of the user's profile in json format.
"""
import datetime
import io

import orjson
import asyncio

import discord
import discord.ext.commands as ext
from discord import Option  #hehe i connected with CLion

import stwutil as stw


class BBDump(ext.Cog):
    """
    Cog for the profile dumper command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    # async def check_errors(self, ctx, public_json_response, auth_info, final_embeds):
    #     """
    #     Checks for errors in the public_json_response and edits the original message if an error is found.
    #
    #     Args:
    #         ctx: The context of the command.
    #         public_json_response: The json response from the public API.
    #         auth_info: The auth_info tuple from get_or_create_auth_session.
    #         final_embeds: The list of embeds to be edited.
    #
    #     Returns:
    #         True if an error is found, False otherwise.
    #     """
    #     try:
    #         # general error
    #         error_code = public_json_response["errorCode"]
    #         support_url = self.client.config["support_url"]
    #         acc_name = auth_info[1]["account_name"]
    #         embed = await stw.post_error_possibilities(ctx, self.client, "profiledump", acc_name, error_code,
    #                                                    support_url)
    #         final_embeds.append(embed)
    #         await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
    #         return True
    #     except KeyError:
    #         # no error
    #         return False

    async def bbprofile_dump_command(self, ctx):
        """
        The main function for the profile dumper command.

        Args:
            ctx: The context of the command.

        Returns:
            None
        """
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)
        embed = await stw.battle_breakers_deprecation(self.client, ctx, "util.battlebreakers.deprecation.embed.description2.bbdump", desired_lang)
        return await stw.slash_send_embed(ctx, self.client, embed)

        # generic_colour = self.client.colours["generic_blue"]
        #
        # auth_info = await stw.get_or_create_auth_session(self.client, ctx, "bbdump", authcode, auth_opt_out, True)
        # if not auth_info[0]:
        #     return
        #
        # final_embeds = []
        #
        # ainfo3 = ""
        # try:
        #     ainfo3 = auth_info[3]
        # except IndexError:
        #     pass
        #
        # # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        # if ainfo3 != "logged_in_processing" and auth_info[2] != []:
        #     final_embeds = auth_info[2]
        #
        # # get profiles
        # profile_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb")
        # profile_json_response = orjson.loads(await profile_request.read())
        # levels_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb",
        #                                            profile_type="levels")
        # levels_json_response = orjson.loads(await levels_request.read())
        # friends_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb",
        #                                             profile_type="friends")
        # friends_json_response = orjson.loads(await friends_request.read())
        # monsterpit_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb",
        #                                                profile_type="monsterpit")
        # monsterpit_json_response = orjson.loads(await monsterpit_request.read())
        # multiplayer_request = await stw.profile_request(self.client, "query", auth_info[1], game="bb",
        #                                                 profile_type="multiplayer")
        # multiplayer_json_response = orjson.loads(await multiplayer_request.read())
        #
        # # check for le error code
        # if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds):
        #     return
        #
        # load_msg = await stw.processing_embed(self.client, ctx, "Dumping profiles", "This won't take long...")
        # load_msg = await stw.slash_edit_original(ctx, auth_info[0], load_msg)
        #
        # # With all info extracted, create the output
        # embed = discord.Embed(
        #     title=await stw.add_emoji_title(self.client, "Battle Breakers Profile dump", "library_floppydisc"),
        #     description=f"\u200b\nYour Battle Breakers profiles are attached above. 🫡\u200b",
        #     colour=generic_colour)
        #
        # profile_file = io.BytesIO()
        # profile_file.write(orjson.dumps(profile_json_response, option=orjson.OPT_INDENT_2))
        # profile_file.seek(0)
        #
        # levels_file = io.BytesIO()
        # levels_file.write(orjson.dumps(levels_json_response, option=orjson.OPT_INDENT_2))
        # levels_file.seek(0)
        #
        # friends_file = io.BytesIO()
        # friends_file.write(orjson.dumps(friends_json_response, option=orjson.OPT_INDENT_2))
        # friends_file.seek(0)
        #
        # monsterpit_file = io.BytesIO()
        # monsterpit_file.write(orjson.dumps(monsterpit_json_response, option=orjson.OPT_INDENT_2))
        # monsterpit_file.seek(0)
        #
        # multiplayer_file = io.BytesIO()
        # multiplayer_file.write(orjson.dumps(multiplayer_json_response, option=orjson.OPT_INDENT_2))
        # multiplayer_file.seek(0)
        #
        # json_file = discord.File(profile_file,
        #                          filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-profile0-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")
        # json_file1 = discord.File(levels_file,
        #                           filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-levels-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")
        # json_file2 = discord.File(friends_file,
        #                           filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-friends-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")
        # json_file3 = discord.File(monsterpit_file,
        #                           filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-monsterpit-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")
        # json_file4 = discord.File(multiplayer_file,
        #                           filename=f"{auth_info[1]['account_name']}-BattleBreakersProfile-multiplayer-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")
        #
        # embed = await stw.set_thumbnail(self.client, embed, "salute")
        # embed = await stw.add_requested_footer(ctx, embed)
        # final_embeds.append(embed)
        # await asyncio.sleep(0.25)
        # await stw.slash_edit_original(ctx, load_msg, final_embeds,
        #                               files=[json_file, json_file1, json_file2, json_file3, json_file4])
        # return

    @ext.command(name='bbdump',
                 aliases=['bbprofiledump', 'bbprofile_dump', 'bbprofile-dump', 'battlebreakersdump', '/bbdump', 'bdump',
                          'bbump', 'bbdmp', 'bbdup', 'bbdum', 'bbbdump', 'bbddump', 'bbduump', 'bbdummp', 'bbdumpp',
                          'bdbump', 'bbudmp', 'bbdmup', 'bbdupm', 'vbdump', 'gbdump', 'hbdump', 'nbdump', 'bvdump',
                          'bgdump', 'bhdump', 'bndump', 'bbsump', 'bbeump', 'bbrump', 'bbfump', 'bbcump', 'bbxump',
                          'bbdymp', 'bbd7mp', 'bbd8mp', 'bbdimp', 'bbdkmp', 'bbdjmp', 'bbdhmp', 'bbdunp', 'bbdujp',
                          'bbdukp', 'bbdumo', 'bbdum0', 'bbduml', 'vbbdump', 'bvbdump', 'gbbdump', 'bgbdump', 'hbbdump',
                          'bhbdump', 'nbbdump', 'bnbdump', 'bbvdump', 'bbgdump', 'bbhdump', 'bbndump', 'bbsdump',
                          'bbdsump', 'bbedump', 'bbdeump', 'bbrdump', 'bbdrump', 'bbfdump', 'bbdfump', 'bbcdump',
                          'bbdcump', 'bbxdump', 'bbdxump', 'bbdyump', 'bbduymp', 'bbd7ump', 'bbdu7mp', 'bbd8ump',
                          'bbdu8mp', 'bbdiump', 'bbduimp', 'bbdkump', 'bbdukmp', 'bbdjump', 'bbdujmp', 'bbdhump',
                          'bbduhmp', 'bbdunmp', 'bbdumnp', 'bbdumjp', 'bbdumkp', 'bbdumop', 'bbdumpo', 'bbdum0p',
                          'bbdump0', 'bbdumlp', 'bbdumpl', 'bprofile', 'bbrofile', 'bbpofile', 'bbprfile', 'bbproile',
                          'bbprofle', 'bbprofie', 'bbprofil', 'bbbprofile', 'bbpprofile', 'bbprrofile', 'bbproofile',
                          'bbproffile', 'bbprofiile', 'bbprofille', 'bbprofilee', 'bpbrofile', 'bbrpofile', 'bbporfile',
                          'bbprfoile', 'bbproifle', 'bbproflie', 'bbprofiel', 'vbprofile', 'gbprofile', 'hbprofile',
                          'nbprofile', 'bvprofile', 'bgprofile', 'bhprofile', 'bnprofile', 'bborofile', 'bb0rofile',
                          'bblrofile', 'bbpeofile', 'bbp4ofile', 'bbp5ofile', 'bbptofile', 'bbpgofile', 'bbpfofile',
                          'bbpdofile', 'bbprifile', 'bbpr9file', 'bbpr0file', 'bbprpfile', 'bbprlfile', 'bbprkfile',
                          'bbprodile', 'bbprorile', 'bbprotile', 'bbprogile', 'bbprovile', 'bbprocile', 'bbprofule',
                          'bbprof8le', 'bbprof9le', 'bbprofole', 'bbproflle', 'bbprofkle', 'bbprofjle', 'bbprofike',
                          'bbprofioe', 'bbprofipe', 'bbprofilw', 'bbprofil3', 'bbprofil4', 'bbprofilr', 'bbprofilf',
                          'bbprofild', 'bbprofils', 'vbbprofile', 'bvbprofile', 'gbbprofile', 'bgbprofile',
                          'hbbprofile', 'bhbprofile', 'nbbprofile', 'bnbprofile', 'bbvprofile', 'bbgprofile',
                          'bbhprofile', 'bbnprofile', 'bboprofile', 'bbporofile', 'bb0profile', 'bbp0rofile',
                          'bblprofile', 'bbplrofile', 'bbperofile', 'bbpreofile', 'bbp4rofile', 'bbpr4ofile',
                          'bbp5rofile', 'bbpr5ofile', 'bbptrofile', 'bbprtofile', 'bbpgrofile', 'bbprgofile',
                          'bbpfrofile', 'bbprfofile', 'bbpdrofile', 'bbprdofile', 'bbpriofile', 'bbproifile',
                          'bbpr9ofile', 'bbpro9file', 'bbpr0ofile', 'bbpro0file', 'bbprpofile', 'bbpropfile',
                          'bbprlofile', 'bbprolfile', 'bbprkofile', 'bbprokfile', 'bbprodfile', 'bbprofdile',
                          'bbprorfile', 'bbprofrile', 'bbprotfile', 'bbproftile', 'bbprogfile', 'bbprofgile',
                          'bbprovfile', 'bbprofvile', 'bbprocfile', 'bbprofcile', 'bbprofuile', 'bbprofiule',
                          'bbprof8ile', 'bbprofi8le', 'bbprof9ile', 'bbprofi9le', 'bbprofoile', 'bbprofiole',
                          'bbproflile', 'bbprofkile', 'bbprofikle', 'bbprofjile', 'bbprofijle', 'bbprofilke',
                          'bbprofiloe', 'bbprofiple', 'bbprofilpe', 'bbprofilwe', 'bbprofilew', 'bbprofil3e',
                          'bbprofile3', 'bbprofil4e', 'bbprofile4', 'bbprofilre', 'bbprofiler', 'bbprofilfe',
                          'bbprofilef', 'bbprofilde', 'bbprofiled', 'bbprofilse', 'bbprofiles', 'umpprofile',
                          'dmpprofile', 'dupprofile', 'dumprofile', 'dumppofile', 'dumpprfile', 'dumpproile',
                          'dumpprofle', 'dumpprofie', 'dumpprofil', 'ddumpprofile', 'duumpprofile', 'dummpprofile',
                          'dumppprofile', 'dumpprrofile', 'dumpproofile', 'dumpproffile', 'dumpprofiile',
                          'dumpprofille', 'dumpprofilee', 'udmpprofile', 'dmupprofile', 'dupmprofile', 'dumprpofile',
                          'dumpporfile', 'dumpprfoile', 'dumpproifle', 'dumpproflie', 'dumpprofiel', 'sumpprofile',
                          'eumpprofile', 'rumpprofile', 'fumpprofile', 'cumpprofile', 'xumpprofile', 'dympprofile',
                          'd7mpprofile', 'd8mpprofile', 'dimpprofile', 'dkmpprofile', 'djmpprofile', 'dhmpprofile',
                          'dunpprofile', 'dujpprofile', 'dukpprofile', 'dumoprofile', 'dum0profile', 'dumlprofile',
                          'dumporofile', 'dump0rofile', 'dumplrofile', 'dumppeofile', 'dumpp4ofile', 'dumpp5ofile',
                          'dumpptofile', 'dumppgofile', 'dumppfofile', 'dumppdofile', 'dumpprifile', 'dumppr9file',
                          'dumppr0file', 'dumpprpfile', 'dumpprlfile', 'dumpprkfile', 'dumpprodile', 'dumpprorile',
                          'dumpprotile', 'dumpprogile', 'dumpprovile', 'dumpprocile', 'dumpprofule', 'dumpprof8le',
                          'dumpprof9le', 'dumpprofole', 'dumpproflle', 'dumpprofkle', 'dumpprofjle', 'dumpprofike',
                          'dumpprofioe', 'dumpprofipe', 'dumpprofilw', 'dumpprofil3', 'dumpprofil4', 'dumpprofilr',
                          'dumpprofilf', 'dumpprofild', 'dumpprofils', 'sdumpprofile', 'dsumpprofile', 'edumpprofile',
                          'deumpprofile', 'rdumpprofile', 'drumpprofile', 'fdumpprofile', 'dfumpprofile',
                          'cdumpprofile', 'dcumpprofile', 'xdumpprofile', 'dxumpprofile', 'dyumpprofile',
                          'duympprofile', 'd7umpprofile', 'du7mpprofile', 'd8umpprofile', 'du8mpprofile',
                          'diumpprofile', 'duimpprofile', 'dkumpprofile', 'dukmpprofile', 'djumpprofile',
                          'dujmpprofile', 'dhumpprofile', 'duhmpprofile', 'dunmpprofile', 'dumnpprofile',
                          'dumjpprofile', 'dumkpprofile', 'dumopprofile', 'dumpoprofile', 'dum0pprofile',
                          'dump0profile', 'dumlpprofile', 'dumplprofile', 'dumpporofile', 'dumpp0rofile',
                          'dumpplrofile', 'dumpperofile', 'dumppreofile', 'dumpp4rofile', 'dumppr4ofile',
                          'dumpp5rofile', 'dumppr5ofile', 'dumpptrofile', 'dumpprtofile', 'dumppgrofile',
                          'dumpprgofile', 'dumppfrofile', 'dumpprfofile', 'dumppdrofile', 'dumpprdofile',
                          'dumppriofile', 'dumpproifile', 'dumppr9ofile', 'dumppro9file', 'dumppr0ofile',
                          'dumppro0file', 'dumpprpofile', 'dumppropfile', 'dumpprlofile', 'dumpprolfile',
                          'dumpprkofile', 'dumpprokfile', 'dumpprodfile', 'dumpprofdile', 'dumpprorfile',
                          'dumpprofrile', 'dumpprotfile', 'dumpproftile', 'dumpprogfile', 'dumpprofgile',
                          'dumpprovfile', 'dumpprofvile', 'dumpprocfile', 'dumpprofcile', 'dumpprofuile',
                          'dumpprofiule', 'dumpprof8ile', 'dumpprofi8le', 'dumpprof9ile', 'dumpprofi9le',
                          'dumpprofoile', 'dumpprofiole', 'dumpproflile', 'dumpprofkile', 'dumpprofikle',
                          'dumpprofjile', 'dumpprofijle', 'dumpprofilke', 'dumpprofiloe', 'dumpprofiple',
                          'dumpprofilpe', 'dumpprofilwe', 'dumpprofilew', 'dumpprofil3e', 'dumpprofile3',
                          'dumpprofil4e', 'dumpprofile4', 'dumpprofilre', 'dumpprofiler', 'dumpprofilfe',
                          'dumpprofilef', 'dumpprofilde', 'dumpprofiled', 'dumpprofilse', 'dumpprofiles',
                          'attlebreakersdump', 'bttlebreakersdump', 'batlebreakersdump', 'battebreakersdump',
                          'battlbreakersdump', 'battlereakersdump', 'battlebeakersdump', 'battlebrakersdump',
                          'battlebrekersdump', 'battlebreaersdump', 'battlebreakrsdump', 'battlebreakesdump',
                          'battlebreakerdump', 'battlebreakersump', 'battlebreakersdmp', 'battlebreakersdup',
                          'battlebreakersdum', 'bbattlebreakersdump', 'baattlebreakersdump', 'batttlebreakersdump',
                          'battllebreakersdump', 'battleebreakersdump', 'battlebbreakersdump', 'battlebrreakersdump',
                          'battlebreeakersdump', 'battlebreaakersdump', 'battlebreakkersdump', 'battlebreakeersdump',
                          'battlebreakerrsdump', 'battlebreakerssdump', 'battlebreakersddump', 'battlebreakersduump',
                          'battlebreakersdummp', 'battlebreakersdumpp', 'abttlebreakersdump', 'btatlebreakersdump',
                          'batltebreakersdump', 'battelbreakersdump', 'battlbereakersdump', 'battlerbeakersdump',
                          'battleberakersdump', 'battlebraekersdump', 'battlebrekaersdump', 'battlebreaekrsdump',
                          'battlebreakresdump', 'battlebreakesrdump', 'battlebreakerdsump', 'battlebreakersudmp',
                          'battlebreakersdmup', 'battlebreakersdupm', 'vattlebreakersdump', 'gattlebreakersdump',
                          'hattlebreakersdump', 'nattlebreakersdump', 'bqttlebreakersdump', 'bwttlebreakersdump',
                          'bsttlebreakersdump', 'bxttlebreakersdump', 'bzttlebreakersdump', 'bartlebreakersdump',
                          'ba5tlebreakersdump', 'ba6tlebreakersdump', 'baytlebreakersdump', 'bahtlebreakersdump',
                          'bagtlebreakersdump', 'baftlebreakersdump', 'batrlebreakersdump', 'bat5lebreakersdump',
                          'bat6lebreakersdump', 'batylebreakersdump', 'bathlebreakersdump', 'batglebreakersdump',
                          'batflebreakersdump', 'battkebreakersdump', 'battoebreakersdump', 'battpebreakersdump',
                          'battlwbreakersdump', 'battl3breakersdump', 'battl4breakersdump', 'battlrbreakersdump',
                          'battlfbreakersdump', 'battldbreakersdump', 'battlsbreakersdump', 'battlevreakersdump',
                          'battlegreakersdump', 'battlehreakersdump', 'battlenreakersdump', 'battlebeeakersdump',
                          'battleb4eakersdump', 'battleb5eakersdump', 'battlebteakersdump', 'battlebgeakersdump',
                          'battlebfeakersdump', 'battlebdeakersdump', 'battlebrwakersdump', 'battlebr3akersdump',
                          'battlebr4akersdump', 'battlebrrakersdump', 'battlebrfakersdump', 'battlebrdakersdump',
                          'battlebrsakersdump', 'battlebreqkersdump', 'battlebrewkersdump', 'battlebreskersdump',
                          'battlebrexkersdump', 'battlebrezkersdump', 'battlebreajersdump', 'battlebreaiersdump',
                          'battlebreaoersdump', 'battlebrealersdump', 'battlebreamersdump', 'battlebreakwrsdump',
                          'battlebreak3rsdump', 'battlebreak4rsdump', 'battlebreakrrsdump', 'battlebreakfrsdump',
                          'battlebreakdrsdump', 'battlebreaksrsdump', 'battlebreakeesdump', 'battlebreake4sdump',
                          'battlebreake5sdump', 'battlebreaketsdump', 'battlebreakegsdump', 'battlebreakefsdump',
                          'battlebreakedsdump', 'battlebreakeradump', 'battlebreakerwdump', 'battlebreakeredump',
                          'battlebreakerddump', 'battlebreakerxdump', 'battlebreakerzdump', 'battlebreakerssump',
                          'battlebreakerseump', 'battlebreakersrump', 'battlebreakersfump', 'battlebreakerscump',
                          'battlebreakersxump', 'battlebreakersdymp', 'battlebreakersd7mp', 'battlebreakersd8mp',
                          'battlebreakersdimp', 'battlebreakersdkmp', 'battlebreakersdjmp', 'battlebreakersdhmp',
                          'battlebreakersdunp', 'battlebreakersdujp', 'battlebreakersdukp', 'battlebreakersdumo',
                          'battlebreakersdum0', 'battlebreakersduml', 'vbattlebreakersdump', 'bvattlebreakersdump',
                          'gbattlebreakersdump', 'bgattlebreakersdump', 'hbattlebreakersdump', 'bhattlebreakersdump',
                          'nbattlebreakersdump', 'bnattlebreakersdump', 'bqattlebreakersdump', 'baqttlebreakersdump',
                          'bwattlebreakersdump', 'bawttlebreakersdump', 'bsattlebreakersdump', 'basttlebreakersdump',
                          'bxattlebreakersdump', 'baxttlebreakersdump', 'bzattlebreakersdump', 'bazttlebreakersdump',
                          'barttlebreakersdump', 'batrtlebreakersdump', 'ba5ttlebreakersdump', 'bat5tlebreakersdump',
                          'ba6ttlebreakersdump', 'bat6tlebreakersdump', 'bayttlebreakersdump', 'batytlebreakersdump',
                          'bahttlebreakersdump', 'bathtlebreakersdump', 'bagttlebreakersdump', 'batgtlebreakersdump',
                          'bafttlebreakersdump', 'batftlebreakersdump', 'battrlebreakersdump', 'batt5lebreakersdump',
                          'batt6lebreakersdump', 'battylebreakersdump', 'batthlebreakersdump', 'battglebreakersdump',
                          'battflebreakersdump', 'battklebreakersdump', 'battlkebreakersdump', 'battolebreakersdump',
                          'battloebreakersdump', 'battplebreakersdump', 'battlpebreakersdump', 'battlwebreakersdump',
                          'battlewbreakersdump', 'battl3ebreakersdump', 'battle3breakersdump', 'battl4ebreakersdump',
                          'battle4breakersdump', 'battlrebreakersdump', 'battlerbreakersdump', 'battlfebreakersdump',
                          'battlefbreakersdump', 'battldebreakersdump', 'battledbreakersdump', 'battlsebreakersdump',
                          'battlesbreakersdump', 'battlevbreakersdump', 'battlebvreakersdump', 'battlegbreakersdump',
                          'battlebgreakersdump', 'battlehbreakersdump', 'battlebhreakersdump', 'battlenbreakersdump',
                          'battlebnreakersdump', 'battlebereakersdump', 'battleb4reakersdump', 'battlebr4eakersdump',
                          'battleb5reakersdump', 'battlebr5eakersdump', 'battlebtreakersdump', 'battlebrteakersdump',
                          'battlebrgeakersdump', 'battlebfreakersdump', 'battlebrfeakersdump', 'battlebdreakersdump',
                          'battlebrdeakersdump', 'battlebrweakersdump', 'battlebrewakersdump', 'battlebr3eakersdump',
                          'battlebre3akersdump', 'battlebre4akersdump', 'battlebrerakersdump', 'battlebrefakersdump',
                          'battlebredakersdump', 'battlebrseakersdump', 'battlebresakersdump', 'battlebreqakersdump',
                          'battlebreaqkersdump', 'battlebreawkersdump', 'battlebreaskersdump', 'battlebrexakersdump',
                          'battlebreaxkersdump', 'battlebrezakersdump', 'battlebreazkersdump', 'battlebreajkersdump',
                          'battlebreakjersdump', 'battlebreaikersdump', 'battlebreakiersdump', 'battlebreaokersdump',
                          'battlebreakoersdump', 'battlebrealkersdump', 'battlebreaklersdump', 'battlebreamkersdump',
                          'battlebreakmersdump', 'battlebreakwersdump', 'battlebreakewrsdump', 'battlebreak3ersdump',
                          'battlebreake3rsdump', 'battlebreak4ersdump', 'battlebreake4rsdump', 'battlebreakrersdump',
                          'battlebreakfersdump', 'battlebreakefrsdump', 'battlebreakdersdump', 'battlebreakedrsdump',
                          'battlebreaksersdump', 'battlebreakesrsdump', 'battlebreakeresdump', 'battlebreaker4sdump',
                          'battlebreake5rsdump', 'battlebreaker5sdump', 'battlebreaketrsdump', 'battlebreakertsdump',
                          'battlebreakegrsdump', 'battlebreakergsdump', 'battlebreakerfsdump', 'battlebreakerdsdump',
                          'battlebreakerasdump', 'battlebreakersadump', 'battlebreakerwsdump', 'battlebreakerswdump',
                          'battlebreakersedump', 'battlebreakerxsdump', 'battlebreakersxdump', 'battlebreakerzsdump',
                          'battlebreakerszdump', 'battlebreakersdsump', 'battlebreakersdeump', 'battlebreakersrdump',
                          'battlebreakersdrump', 'battlebreakersfdump', 'battlebreakersdfump', 'battlebreakerscdump',
                          'battlebreakersdcump', 'battlebreakersdxump', 'battlebreakersdyump', 'battlebreakersduymp',
                          'battlebreakersd7ump', 'battlebreakersdu7mp', 'battlebreakersd8ump', 'battlebreakersdu8mp',
                          'battlebreakersdiump', 'battlebreakersduimp', 'battlebreakersdkump', 'battlebreakersdukmp',
                          'battlebreakersdjump', 'battlebreakersdujmp', 'battlebreakersdhump', 'battlebreakersduhmp',
                          'battlebreakersdunmp', 'battlebreakersdumnp', 'battlebreakersdumjp', 'battlebreakersdumkp',
                          'battlebreakersdumop', 'battlebreakersdumpo', 'battlebreakersdum0p', 'battlebreakersdump0',
                          'battlebreakersdumlp', 'battlebreakersdumpl'],
                 extras={'emoji': "library_floppydisc", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         "dev": True, "description_keys": ['bbdump.meta.description'], "name_key": "bbdump.slash.name",
                         "battle_broken": True},  # to hide from help
                 brief="bbdump.meta.brief",
                 description="{0}")
    async def bbdump(self, ctx):
        """
        This function is the entry point for the profile dump command when called traditionally

        Args:
            ctx: The context of the command
        """

        await self.bbprofile_dump_command(ctx)

    # @ext.slash_command(name='bbdump', name_localizations=stw.I18n.construct_slash_dict("bbdump.slash.name"),
    #                    description='Dumps your Battle Breakers profile as a JSON attachment',
    #                    description_localizations=stw.I18n.construct_slash_dict("bbdump.slash.description"),
    #                    guild_ids=stw.guild_ids)
    # async def slashbbdump(self, ctx: discord.ApplicationContext,
    #                        token: Option(
    #                            description="Your Epic Games authcode. Required unless you have an active session.",
    #                            description_localizations=stw.I18n.construct_slash_dict(
    #                                "generic.slash.token"),
    #                            name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
    #                            min_length=32) = "",
    #                        auth_opt_out: Option(default="False",
    #                                             description="Opt out of starting an authentication session",
    #                                             description_localizations=stw.I18n.construct_slash_dict(
    #                                                 "generic.slash.optout"),
    #                                             name_localizations=stw.I18n.construct_slash_dict(
    #                                                 "generic.meta.args.optout"),
    #                                             choices=[OptionChoice("Do not start an authentication session", "True",
    #                                                                   stw.I18n.construct_slash_dict(
    #                                                                       "generic.slash.optout.true")),
    #                                                      OptionChoice("Start an authentication session (Default)",
    #                                                                   "False",
    #                                                                   stw.I18n.construct_slash_dict(
    #                                                                       "generic.slash.optout.false"))]) = "False"):
    #     """
    #     This function is the entry point for the bbdump command when called via slash
    #
    #     Args:
    #         ctx: The context of the slash command
    #         token: The authcode of the user
    #         auth_opt_out: Whether the user wants to opt out of starting an authentication session
    #     """
    #     await self.bbprofile_dump_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(BBDump(client))

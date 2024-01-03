"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily xp command. Returns info about the stw accolade daily xp system for the authenticated player.
"""
import asyncio
import logging

import orjson
import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw

logger = logging.getLogger(__name__)


class DailyXP(ext.Cog):
    """
    Cog for the daily xp command.
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
            embed = await stw.post_error_possibilities(ctx, self.client, "dailyxp", acc_name, error_code,
                                                       verbiage_action="xp", desired_lang=desired_lang)
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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        generic_colour = self.client.colours["generic_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "dailyxp", authcode, auth_opt_out,
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
        profile_request = await stw.profile_request(self.client, "query", auth_info[1])
        profile_json_response = orjson.loads(await profile_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, profile_json_response, auth_info, final_embeds, desired_lang):
            return

        try:
            # get daily xp token info
            daily_xp = await asyncio.gather(
                asyncio.to_thread(stw.extract_profile_item, profile_json=profile_json_response,
                                  item_string='Token:stw_accolade_tracker'))
            daily_xp = daily_xp[0][0]
            logger.debug(f"Daily XP: {daily_xp}")
        except Exception as e:
            # TODO: properly handle no daily xp token
            if str(e) == "0":
                e = "You don't have any STW Daily XP yet."
            if isinstance(e, BaseException):
                logger.error(e.with_traceback(e.__traceback__))
            embed = discord.Embed(title=stw.I18n.get('dailyxp.embed.title', desired_lang),
                                  description=stw.I18n.get('dailyxp.embed.error.description', desired_lang,
                                                           f'```{e}```'),
                                  colour=generic_colour)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        try:
            last_reset = stw.convert_iso_to_unix(daily_xp["attributes"]["last_reset"])
        except KeyError:
            last_reset = 0
        try:
            dailyxp = daily_xp['attributes']['daily_xp']
        except:
            dailyxp = 0
        # TODO: update the style of this
        progress_bar = stw.get_progress_bar(dailyxp, stw.max_daily_stw_accolade_xp, 20)

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('dailyxp.embed.title', desired_lang),
                                            "xp_everywhere"),
            description=f"\u200b\n{stw.I18n.get('dailyxp.embed.description1', desired_lang, dailyxp)}\u200b\n"
                        f"{stw.I18n.get('dailyxp.embed.description2', desired_lang, stw.max_daily_stw_accolade_xp - dailyxp)}\u200b\n"
                        f"{progress_bar}\u200b\n"
                        f"{stw.I18n.get('dailyxp.embed.description3', desired_lang, f'<t:{last_reset}:R>')}\n\u200b",
            colour=generic_colour)

        embed = await stw.set_thumbnail(self.client, embed, "xp_everywhere")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return

    @ext.slash_command(name='dailyxp', name_localizations=stw.I18n.construct_slash_dict("dailyxp.slash.name"),
                       description='View your daily STW XP cap',
                       description_localizations=stw.I18n.construct_slash_dict("dailyxp.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashldailyxp(self, ctx: discord.ApplicationContext,
                            token: Option(
                                description="Your Epic Games authcode. Required unless you have an active session.",
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
                                                 choices=[OptionChoice("Do not start an authentication session", "True",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.true")),
                                                          OptionChoice("Start an authentication session (Default)",
                                                                       "False",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the daily xp command when called via slash

        Args:
            ctx (discord.ApplicationContext): The context of the slash command
            token: Your Epic Games authcode. Required unless you have an active session.
            auth_opt_out: Opt out of starting an authentication session
        """
        await self.daily_xp_command(ctx, token, not eval(auth_opt_out))

    @ext.command(name='dailyxp',
                 aliases=['dxp', '/dxp', '/dailyxp', 'daily_xp', '/daily_xp', 'ailyxp', 'dilyxp', 'dalyxp', 'daiyxp',
                          'dailxp', 'dailyp', 'dailyx', 'ddailyxp', 'daailyxp', 'daiilyxp', 'daillyxp', 'dailyyxp',
                          'dailyxxp', 'dailyxpp', 'adilyxp', 'dialyxp', 'daliyxp', 'daiylxp', 'dailxyp', 'dailypx',
                          'sailyxp', 'eailyxp', 'railyxp', 'failyxp', 'cailyxp', 'xailyxp', 'dqilyxp', 'dwilyxp',
                          'dsilyxp', 'dxilyxp', 'dzilyxp', 'daulyxp', 'da8lyxp', 'da9lyxp', 'daolyxp', 'dallyxp',
                          'daklyxp', 'dajlyxp', 'daikyxp', 'daioyxp', 'daipyxp', 'dailtxp', 'dail6xp', 'dail7xp',
                          'dailuxp', 'dailjxp', 'dailhxp', 'dailgxp', 'dailyzp', 'dailysp', 'dailydp', 'dailycp',
                          'dailyxo', 'dailyx0', 'dailyxl', 'sdailyxp', 'dsailyxp', 'edailyxp', 'deailyxp', 'rdailyxp',
                          'drailyxp', 'fdailyxp', 'dfailyxp', 'cdailyxp', 'dcailyxp', 'xdailyxp', 'dxailyxp',
                          'dqailyxp', 'daqilyxp', 'dwailyxp', 'dawilyxp', 'dasilyxp', 'daxilyxp', 'dzailyxp',
                          'dazilyxp', 'dauilyxp', 'daiulyxp', 'da8ilyxp', 'dai8lyxp', 'da9ilyxp', 'dai9lyxp',
                          'daoilyxp', 'daiolyxp', 'dalilyxp', 'dakilyxp', 'daiklyxp', 'dajilyxp', 'daijlyxp',
                          'dailkyxp', 'dailoyxp', 'daiplyxp', 'dailpyxp', 'dailtyxp', 'dailytxp', 'dail6yxp',
                          'daily6xp', 'dail7yxp', 'daily7xp', 'dailuyxp', 'dailyuxp', 'dailjyxp', 'dailyjxp',
                          'dailhyxp', 'dailyhxp', 'dailgyxp', 'dailygxp', 'dailyzxp', 'dailyxzp', 'dailysxp',
                          'dailyxsp', 'dailydxp', 'dailyxdp', 'dailycxp', 'dailyxcp', 'dailyxop', 'dailyxpo',
                          'dailyx0p', 'dailyxp0', 'dailyxlp', 'dailyxpl', 'xp', 'dp', 'dx', 'ddxp', 'dxxp', 'dxpp',
                          'xdp', 'dpx', 'sxp', 'exp', 'rxp', 'fxp', 'cxp', 'xxp', 'dzp', 'dsp', 'ddp', 'dcp', 'dxo',
                          'dx0', 'dxl', 'sdxp', 'dsxp', 'edxp', 'dexp', 'rdxp', 'drxp', 'fdxp', 'dfxp', 'cdxp', 'dcxp',
                          'xdxp', 'dzxp', 'dxzp', 'dxsp', 'dxdp', 'dxcp', 'dxop', 'dxpo', 'dx0p', 'dxp0', 'dxlp',
                          'dxpl', 'pcap', 'xcap', 'xpap', 'xpcp', 'xpca', 'xxpcap', 'xppcap', 'xpccap', 'xpcaap',
                          'xpcapp', 'pxcap', 'xcpap', 'xpacp', 'xpcpa', 'zpcap', 'spcap', 'dpcap', 'cpcap', 'xocap',
                          'x0cap', 'xlcap', 'xpxap', 'xpdap', 'xpfap', 'xpvap', 'xpcqp', 'xpcwp', 'xpcsp', 'xpcxp',
                          'xpczp', 'xpcao', 'xpca0', 'xpcal', 'zxpcap', 'xzpcap', 'sxpcap', 'xspcap', 'dxpcap',
                          'xdpcap', 'cxpcap', 'xcpcap', 'xopcap', 'xpocap', 'x0pcap', 'xp0cap', 'xlpcap', 'xplcap',
                          'xpxcap', 'xpcxap', 'xpdcap', 'xpcdap', 'xpfcap', 'xpcfap', 'xpvcap', 'xpcvap', 'xpcqap',
                          'xpcaqp', 'xpcwap', 'xpcawp', 'xpcsap', 'xpcasp', 'xpcaxp', 'xpczap', 'xpcazp', 'xpcaop',
                          'xpcapo', 'xpca0p', 'xpcap0', 'xpcalp', 'xpcapl', 'ailycap', 'dilycap', 'dalycap', 'daiycap',
                          'dailcap', 'dailyap', 'dailyca', 'ddailycap', 'daailycap', 'daiilycap', 'daillycap',
                          'dailyycap', 'dailyccap', 'dailycaap', 'dailycapp', 'adilycap', 'dialycap', 'daliycap',
                          'daiylcap', 'dailcyap', 'dailyacp', 'dailycpa', 'sailycap', 'eailycap', 'railycap',
                          'failycap', 'cailycap', 'xailycap', 'dqilycap', 'dwilycap', 'dsilycap', 'dxilycap',
                          'dzilycap', 'daulycap', 'da8lycap', 'da9lycap', 'daolycap', 'dallycap', 'daklycap',
                          'dajlycap', 'daikycap', 'daioycap', 'daipycap', 'dailtcap', 'dail6cap', 'dail7cap',
                          'dailucap', 'dailjcap', 'dailhcap', 'dailgcap', 'dailyxap', 'dailydap', 'dailyfap',
                          'dailyvap', 'dailycqp', 'dailycwp', 'dailycsp', 'dailyczp', 'dailycao', 'dailyca0',
                          'dailycal', 'sdailycap', 'dsailycap', 'edailycap', 'deailycap', 'rdailycap', 'drailycap',
                          'fdailycap', 'dfailycap', 'cdailycap', 'dcailycap', 'xdailycap', 'dxailycap', 'dqailycap',
                          'daqilycap', 'dwailycap', 'dawilycap', 'dasilycap', 'daxilycap', 'dzailycap', 'dazilycap',
                          'dauilycap', 'daiulycap', 'da8ilycap', 'dai8lycap', 'da9ilycap', 'dai9lycap', 'daoilycap',
                          'daiolycap', 'dalilycap', 'dakilycap', 'daiklycap', 'dajilycap', 'daijlycap', 'dailkycap',
                          'dailoycap', 'daiplycap', 'dailpycap', 'dailtycap', 'dailytcap', 'dail6ycap', 'daily6cap',
                          'dail7ycap', 'daily7cap', 'dailuycap', 'dailyucap', 'dailjycap', 'dailyjcap', 'dailhycap',
                          'dailyhcap', 'dailgycap', 'dailygcap', 'dailyxcap', 'dailycxap', 'dailydcap', 'dailycdap',
                          'dailyfcap', 'dailycfap', 'dailyvcap', 'dailycvap', 'dailycqap', 'dailycaqp', 'dailycwap',
                          'dailycawp', 'dailycsap', 'dailycasp', 'dailycaxp', 'dailyczap', 'dailycazp', 'dailycaop',
                          'dailycapo', 'dailyca0p', 'dailycap0', 'dailycalp', 'dailycapl', 'twxp', 'swxp', 'stxp',
                          'stwp', 'stwx', 'sstwxp', 'sttwxp', 'stwwxp', 'stwxxp', 'stwxpp', 'tswxp', 'swtxp', 'stxwp',
                          'stwpx', 'atwxp', 'wtwxp', 'etwxp', 'dtwxp', 'xtwxp', 'ztwxp', 'srwxp', 's5wxp', 's6wxp',
                          'sywxp', 'shwxp', 'sgwxp', 'sfwxp', 'stqxp', 'st2xp', 'st3xp', 'stexp', 'stdxp', 'stsxp',
                          'staxp', 'stwzp', 'stwsp', 'stwdp', 'stwcp', 'stwxo', 'stwx0', 'stwxl', 'astwxp', 'satwxp',
                          'wstwxp', 'swtwxp', 'estwxp', 'setwxp', 'dstwxp', 'sdtwxp', 'xstwxp', 'sxtwxp', 'zstwxp',
                          'sztwxp', 'srtwxp', 'strwxp', 's5twxp', 'st5wxp', 's6twxp', 'st6wxp', 'sytwxp', 'stywxp',
                          'shtwxp', 'sthwxp', 'sgtwxp', 'stgwxp', 'sftwxp', 'stfwxp', 'stqwxp', 'stwqxp', 'st2wxp',
                          'stw2xp', 'st3wxp', 'stw3xp', 'stewxp', 'stwexp', 'stdwxp', 'stwdxp', 'stswxp', 'stwsxp',
                          'stawxp', 'stwaxp', 'stwzxp', 'stwxzp', 'stwxsp', 'stwxdp', 'stwcxp', 'stwxcp', 'stwxop',
                          'stwxpo', 'stwx0p', 'stwxp0', 'stwxlp', 'stwxpl', 'xpcap', 'dailycap', 'stwxp', '/xpcap',
                          '/dailycap', '/stwxp', 'sharedxp', 'diarixp', 'καθημερινάxp', 'diarioxp', 'igapäevanexp',
                          'päivittäinxp', 'kullumxp', 'डेलीएक्सपी', 'デイリーXP', 'kasdien xp', 'ਡੇਲੀਐਕਸਪੀ', 'zilnicxp',
                          'даиликп', 'kila sikuxp', 'தினசரிஎக்ஸ்பி', 'రోజువారీxp', 'günlük xp', '每日经验', '每日經驗',
                          'kasdienxp', 'daylyxp', 'dabilyxp', 'dailyoxp', 'daiiyxp', 'dailygp', 'dahlyxp', 'dnilyxp',
                          'dtailyxp', 'daieyxp', 'kailyxp', 'dailylp', 'dailyxyp', 'dvilyxp', 'dailyfp',
                          'dadilyxp', 'dailytp', 'dairlyxp', 'dailywxp', 'daityxp', 'dailyxq', 'dahilyxp', 'tailyxp',
                          'lailyxp', 'dailcxp', 'qdailyxp', 'daelyxp', 'dfilyxp', 'nailyxp', 'dailybxp', 'dnailyxp',
                          'dailyrp', 'ydailyxp', 'dailyxm', 'vailyxp', 'dailyxpk', 'dailayxp', 'dailypp', 'dailyxg',
                          'dagilyxp', 'dailcyxp', 'dlilyxp', 'dailyxk', 'daiblyxp', 'dailyxv', 'davlyxp',
                          'dailyyp', 'dailyxpr', 'dailyxr', 'daijyxp', 'zailyxp', 'vdailyxp', 'dadlyxp', 'dpilyxp',
                          'daimlyxp', 'dailrxp', 'dailyxpu', 'dailzxp', 'dailyxpm', 'dailyxpx', 'dailynp', 'bdailyxp',
                          'dailnyxp', 'dailyxz', 'dayilyxp', 'qailyxp', 'dailyup', 'dailyip', 'dafilyxp', 'mailyxp',
                          'dailvyxp', 'dailyxkp', 'dailxxp', 'dailyaxp', 'dailzyxp', 'dailyrxp', 'pdailyxp', 'diailyxp',
                          'dailyxpi', 'uailyxp', 'daibyxp', 'dailyvp', 'daiclyxp', 'damilyxp', 'daiflyxp', 'dailiyxp',
                          'mdailyxp', 'dmailyxp', 'daillxp', 'dailyxph', 'hdailyxp', 'dailyxpz', 'dailyxhp', 'dairyxp',
                          'dailyxpw', 'dailqxp', 'dailyxd', 'dailyxi', 'dailyfxp', 'dailyxn', 'darlyxp', 'dailyxh',
                          'datilyxp', 'dailyxqp', 'oailyxp', 'dainlyxp', 'dailyxwp', 'dailyxf', 'dailaxp', 'dvailyxp',
                          'dailyxpv', 'dbilyxp', 'djilyxp', 'dailyxpe', 'dailypxp', 'kdailyxp', 'daihyxp', 'darilyxp',
                          'daidyxp', 'daislyxp', 'daileyxp', 'ddilyxp', 'jailyxp', 'daiqlyxp', 'dailmyxp', 'hailyxp',
                          'dailfxp', 'yailyxp', 'dailsxp', 'dailyxpa', 'dailyjp', 'dazlyxp', 'dailyxjp', 'dailykp',
                          'daxlyxp', 'daixyxp', 'daizyxp', 'dgilyxp', 'dailyxpj', 'dpailyxp', 'dbailyxp', 'dailylxp',
                          'dailfyxp', 'deilyxp', 'dailyxfp', 'dailyexp', 'daildyxp', 'daeilyxp', 'zdailyxp', 'dailyxu',
                          'drilyxp', 'dailqyxp', 'dhilyxp', 'adailyxp', 'dailyhp', 'dailyxnp', 'dailyxup', 'dailyxbp',
                          'dailyxvp', 'dailyxmp', 'doailyxp', 'dapilyxp', 'dailyxs', 'dailymxp', 'datlyxp', 'dailwyxp',
                          'dkailyxp', 'doilyxp', 'dailyxa', 'dhailyxp', 'daiqyxp', 'bailyxp', 'dailyixp', 'dailyxpy',
                          'dailyxpg', 'daclyxp', 'daifyxp', 'dyilyxp', 'dailmxp', 'wailyxp', 'wdailyxp', 'dailwxp',
                          'dcilyxp', 'dailyvxp', 'daizlyxp', 'daimyxp', 'daiayxp', 'dablyxp', 'dailybp', 'dailyxtp',
                          'dkilyxp', 'dailvxp', 'ldailyxp', 'dailykxp', 'dailoxp', 'daielyxp', 'daglyxp', 'dailywp',
                          'dailyxps', 'pailyxp', 'daflyxp', 'dailyop', 'gailyxp', 'dailyxpn', 'daialyxp', 'daiglyxp',
                          'daihlyxp', 'daisyxp', 'daivlyxp', 'dailryxp', 'daigyxp', 'dailyxpf', 'tdailyxp', 'dailyxpb',
                          'dacilyxp', 'dailynxp', 'dailsyxp', 'dailbxp', 'daidlyxp', 'dailyxrp', 'duailyxp', 'daiyyxp',
                          'iailyxp', 'dailyxpq', 'daivyxp', 'dailyep', 'odailyxp', 'daiwyxp', 'dailixp', 'dailyxw',
                          'daixlyxp', 'daildxp', 'dailyxgp', 'daalyxp', 'dgailyxp', 'dailyxe', 'daiuyxp', 'idailyxp',
                          'danlyxp', 'dainyxp', 'dailyxy', 'duilyxp', 'dailymp', 'dailpxp', 'dmilyxp', 'udailyxp',
                          'dailyxpc', 'diilyxp', 'dlailyxp', 'dyailyxp', 'dailyxip', 'damlyxp', 'dailkxp', 'jdailyxp',
                          'dailyxb', 'aailyxp', 'dailyxj', 'dailyxc', 'daplyxp', 'dailxyxp', 'dailyxep', 'ndailyxp',
                          'daitlyxp', 'daiylyxp', 'daicyxp', 'djailyxp', 'dailnxp', 'dailyxx', 'daiwlyxp', 'danilyxp',
                          'dailyqxp', 'dailexp', 'daqlyxp', 'dailyxpt', 'dtilyxp', 'dailyxpd', 'davilyxp', 'gdailyxp',
                          'dailyxt', 'daslyxp', 'dailbyxp', 'dawlyxp', 'da7lyxp', 'da&lyxp', 'da*lyxp', 'da(lyxp',
                          'dai;yxp', 'dai/yxp', 'dai.yxp', 'dai,yxp', 'dai?yxp', 'dai>yxp', 'dai<yxp', 'dail5xp',
                          'dail%xp', 'dail^xp', 'dail&xp', 'dailyx9', 'dailyx-', 'dailyx[', 'dailyx]', 'dailyx;',
                          'dailyx(', 'dailyx)', 'dailyx_', 'dailyx=', 'dailyx+', 'dailyx{', 'dailyx}', 'dailyx:', 'uxp',
                          'dxj', 'drp', 'dbp', 'dyp', 'dxpa', 'vdxp', 'zdxp', 'zxp', 'dxqp', 'jxp', 'dxep', 'dbxp',
                          'axp', 'dxpf', 'dxpg', 'dxw', 'qxp', 'dxpw', 'gxp', 'dxfp', 'dxpi', 'dxap', 'dhxp',
                          'dxh', 'dxi', 'qdxp', 'duxp', 'dxd', 'dxk', 'dxc', 'pdxp', 'dxm', 'dxvp', 'dpp', 'dxx', 'dep',
                          'bxp', 'doxp', 'djxp', 'dwxp', 'dxpu', 'dxpb', 'dxph', 'jdxp', 'dxa', 'dxpj', 'dxpz', 'dop',
                          'dxpx', 'dxmp', 'dkp', 'tdxp', 'wxp', 'idxp', 'dfp', 'lxp', 'dxbp', 'dxgp', 'dmxp', 'odxp',
                          'dxpe', 'oxp', 'dxtp', 'ndxp', 'dxb', 'dxpt', 'dlp', 'mxp', 'dxf', 'dpxp', 'dap', 'dip',
                          'dgp', 'dxjp', 'udxp', 'dqp', 'ydxp', 'dxpv', 'bdxp', 'ldxp', 'dxpn', 'dixp', 'dxpm', 'dxhp',
                          'dxpd', 'txp', 'dxe', 'dxg', 'pxp', 'dxr', 'dxz', 'dxyp', 'dxpy', 'dxnp', 'dxrp', 'dyxp',
                          'ixp', 'kdxp', 'dvxp', 'dnp', 'dxup', 'dvp', 'dxps', 'dhp', 'dwp', 'dqxp', 'dxn',
                          'djp', 'dxv', 'dxpc', 'dxs', 'dtp', 'dxpk', 'dnxp', 'dxip', 'daxp', 'kxp',
                          'vxp', 'mdxp', 'adxp', 'dxu', 'wdxp', 'gdxp', 'nxp', 'dkxp', 'hdxp', 'dtxp', 'dxpr', 'dxy',
                          'dxt', 'dxpq', 'dxkp', 'dgxp', 'yxp', 'dxwp', 'dlxp', 'dx9', 'dx-', 'dx[', 'dx]', 'dx;',
                          'dx(', 'dx)', 'dx_', 'dx=', 'dx+', 'dx{', 'dx}', 'dx:', 'accolaed', 'acolade', 'atccolade',
                          'accoade', 'accolde', 'accolode', 'accoalde', 'accoljde', 'accoldae', 'accolad', 'acdolade',
                          'accohlade', 'accolsade', 'cacolade', 'paccolade', 'accolades', 'accolade', 'acciolade',
                          'ajcolade', 'accomlade', 'accolqde', 'acoclade', 'accllade', 'accylade', 'accoladq',
                          'accolaade', 'gaccolade', 'acculade', 'accolqade', 'accolvde', 'accolkde', 'ahccolade',
                          'auccolade', 'acacolade', 'accoladme', 'acxolade', 'accolpade', 'accolrde', 'gccolade',
                          'acbolade', 'raccolade', 'ccolade', 'apcolade', 'accolaqe', 'accloade', 'accosade',
                          'accoulade', 'akcolade', 'acvolade', 'aocolade', 'atcolade', 'accolae', 'acclade', 'mccolade',
                          'accolame', 'accoltade', 'accwlade', 'accoltde', 'accotlade', 'accolcade', 'accolaede',
                          'accrlade', 'accoxade', 'accoluade', 'accoladae', 'accolcde', 'accsolade', 'accolave',
                          'accoilade', 'axccolade', 'accoladem', 'accoladeb', 'yaccolade', 'accolafde', 'accolide',
                          'accolfde', 'acckolade', 'accoladqe', 'accfolade', 'achcolade', 'accolaue', 'vaccolade',
                          'wccolade', 'accofade', 'accolaxe', 'accoladg', 'accolale', 'accoylade', 'accoladek',
                          'accolaze', 'aeccolade', 'accoladn', 'acecolade', 'acccolade', 'accoladez', 'acclolade',
                          'accolaqde', 'accolwde', 'accolpde', 'accolarde', 'accelade', 'abccolade', 'qaccolade',
                          'acceolade', 'accollde', 'accoladwe', 'accolajde', 'accoladw', 'accoladew', 'accoladhe',
                          'accoladoe', 'aycolade', 'jccolade', 'fccolade', 'accgolade', 'accolaoe', 'acocolade',
                          'accglade', 'abcolade', 'ascolade', 'accoladi', 'accomade', 'afccolade', 'accoladf',
                          'aaccolade', 'azcolade', 'accrolade', 'accoladfe', 'aceolade', 'accoladey', 'accolrade',
                          'accoladve', 'accozlade', 'acrolade', 'accmlade', 'accolagde', 'apccolade', 'accoyade',
                          'acncolade', 'accodade', 'hccolade', 'acsolade', 'accoldade', 'accoladei', 'azccolade',
                          'aciolade', 'aacolade', 'bccolade', 'xccolade', 'accolalde', 'accoladue', 'accolaie',
                          'accopade', 'acctolade', 'sccolade', 'acuolade', 'taccolade', 'jaccolade', 'acpcolade',
                          'accolxde', 'acfcolade', 'accoladp', 'accpolade', 'avcolade', 'accoxlade', 'accoladh',
                          'accoladc', 'accflade', 'accolmde', 'accolnde', 'yccolade', 'accolace', 'accoladee',
                          'accolbde', 'axcolade', 'accolhade', 'accoladeq', 'accogade', 'amcolade', 'arcolade',
                          'accoladeo', 'accolate', 'kccolade', 'accoladre', 'accslade', 'accholade', 'accoladeg',
                          'acrcolade', 'accoolade', 'acjcolade', 'ahcolade', 'accoglade', 'ackolade', 'accoladde',
                          'uccolade', 'accplade', 'maccolade', 'accorade', 'acvcolade', 'accvolade', 'haccolade',
                          'accokade', 'aqcolade', 'baccolade', 'accoladen', 'accoaade', 'afcolade', 'aclcolade',
                          'acconade', 'saccolade', 'accolape', 'accolatde', 'accowlade', 'accvlade', 'acpolade',
                          'accolzde', 'accjolade', 'actolade', 'accilade', 'accolakde', 'accoiade', 'akccolade',
                          'accclade', 'aczolade', 'accodlade', 'accoclade', 'accolande', 'occolade', 'accolxade',
                          'accolaode', 'acxcolade', 'accoladx', 'acicolade', 'accolvade', 'accbolade', 'accolgade',
                          'zccolade', 'dccolade', 'accoladel', 'accolafe', 'accollade', 'accoladv', 'acconlade',
                          'accowade', 'accocade', 'accolado', 'accoklade', 'accolgde', 'amccolade', 'accxolade',
                          'accoladye', 'pccolade', 'accoblade', 'accnolade', 'accoladm', 'awccolade', 'accoladte',
                          'acyolade', 'accolane', 'accoladce', 'qccolade', 'accolamde', 'accoladeu', 'waccolade',
                          'adccolade', 'lccolade', 'accolaude', 'accolahe', 'agccolade', 'acscolade', 'aoccolade',
                          'accoladev', 'accklade', 'zaccolade', 'accoladl', 'accolaje', 'accoladj', 'acwcolade',
                          'cccolade', 'accouade', 'accolabde', 'accoalade', 'alccolade', 'accovade', 'accalade',
                          'accolede', 'acucolade', 'acchlade', 'aqccolade', 'accolzade', 'acqcolade', 'accoljade',
                          'agcolade', 'accdolade', 'accoladex', 'eccolade', 'accoladje', 'accoladle', 'acqolade',
                          'accozade', 'accolyade', 'adcolade', 'accolasde', 'accaolade', 'laccolade', 'accohade',
                          'accolbade', 'accooade', 'accolfade', 'accolare', 'accoladie', 'ayccolade', 'anccolade',
                          'acctlade', 'accolacde', 'accolaee', 'aecolade', 'vccolade', 'ajccolade', 'arccolade',
                          'aclolade', 'acdcolade', 'acmolade', 'accnlade', 'accolavde', 'acbcolade', 'ancolade',
                          'ackcolade', 'accolabe', 'accolaye', 'accolader', 'accoladb', 'accoladge', 'accoladke',
                          'accoladr', 'accoqlade', 'accolawde', 'acycolade', 'accorlade', 'acholade', 'accoladse',
                          'accolady', 'actcolade', 'accolada', 'accolayde', 'acczolade', 'accolkade', 'accoladk',
                          'accolwade', 'acfolade', 'accoeade', 'accoladet', 'accwolade', 'accovlade', 'daccolade',
                          'iaccolade', 'accolaide', 'accolhde', 'accoqade', 'accoladt', 'accolmade', 'tccolade',
                          'rccolade', 'awcolade', 'accolnade', 'faccolade', 'accoladej', 'accolake', 'accoladze',
                          'accqlade', 'accoldde', 'accoladea', 'acwolade', 'accolude', 'accoladxe', 'xaccolade',
                          'accoleade', 'accobade', 'accqolade', 'accoladne', 'aucolade', 'accoslade', 'caccolade',
                          'accoladu', 'accoliade', 'oaccolade', 'naccolade', 'accuolade', 'eaccolade', 'accoladec',
                          'accoladeh', 'accojlade', 'accjlade', 'accyolade', 'avccolade', 'aiccolade', 'acoolade',
                          'accolads', 'nccolade', 'acjolade', 'accoladpe', 'aczcolade', 'kaccolade', 'alcolade',
                          'accolazde', 'accxlade', 'acmcolade', 'acnolade', 'accotade', 'aicolade', 'accoladbe',
                          'accmolade', 'acgolade', 'iccolade', 'accolaae', 'accoladef', 'accolage', 'asccolade',
                          'accolawe', 'accolapde', 'acaolade', 'accolyde', 'accoladed', 'accoplade', 'accblade',
                          'accoelade', 'acczlade', 'accoladd', 'uaccolade', 'accolase', 'accolahde', 'accoloade',
                          'accoladz', 'accdlade', 'accoflade', 'accolsde', 'acgcolade', 'accojade', 'accoladep',
                          'accolaxde', 'acc8lade', 'acc9lade', 'acc0lade', 'acc;lade', 'acc*lade', 'acc(lade',
                          'acc)lade', 'acco;ade', 'acco/ade', 'acco.ade', 'acco,ade', 'acco?ade', 'acco>ade',
                          'acco<ade', 'accolad4', 'accolad3', 'accolad2', 'accolad$', 'accolad#', 'accolad@', 'xpcax',
                          'xfpcap', 'xpncap', 'xnpcap', 'xpcmp', 'xipcap', 'xpcar', 'xypcap', 'xhcap', 'xpcapb',
                          'xpcapg', 'xscap', 'xpcavp', 'xpcag', 'xncap', 'xdcap', 'xpcaw', 'xpcac', 'xpjcap', 'npcap',
                          'xpqcap', 'xpicap', 'xpcapk', 'xpaap', 'xpcapd', 'xpcahp', 'ppcap', 'xpcyp', 'xpcaip',
                          'xccap', 'ypcap', 'xphap', 'bxpcap', 'xpcip', 'xpecap', 'xpwap', 'kpcap', 'epcap', 'xpcjp',
                          'xfcap', 'gxpcap', 'xpwcap', 'xpcpp', 'xpctp', 'xpcrp', 'xprap', 'upcap', 'xpcoap', 'xpcapm',
                          'xapcap', 'xjpcap', 'xpcpap', 'fxpcap', 'xpcup', 'xplap', 'apcap', 'opcap', 'xpcay', 'xpcapz',
                          'xpcaph', 'xpcarp', 'xecap', 'xpcah', 'xpclp', 'xpcyap', 'xpcamp', 'xpcad', 'xpnap', 'wpcap',
                          'xpclap', 'xjcap', 'axpcap', 'xphcap', 'ixpcap', 'jpcap', 'xpjap', 'xpzap', 'xpcdp', 'xpcaa',
                          'xpcgap', 'xpcaup', 'xpcuap', 'xpcapc', 'xpqap', 'xrcap', 'xpcfp', 'mpcap', 'xmcap', 'xptap',
                          'xpcau', 'xpcapv', 'xucap', 'xhpcap', 'xpcapw', 'expcap', 'xpcav', 'xpcmap', 'xpyap', 'xpcaj',
                          'xpcep', 'xpbap', 'fpcap', 'lxpcap', 'xrpcap', 'xpzcap', 'xicap', 'xpcak', 'xpcbap', 'xpacap',
                          'xpcapr', 'xpcae', 'xpcanp', 'xpcapq', 'xacap', 'rpcap', 'xepcap', 'xpcakp', 'xtpcap',
                          'xpcas', 'xpcaep', 'xbcap', 'lpcap', 'xpoap', 'xpcab', 'ipcap', 'qpcap', 'xgcap', 'xwpcap',
                          'xpgcap', 'kxpcap', 'xpcbp', 'xpcapf', 'xpcapn', 'xpcabp', 'xxcap', 'xycap', 'xvcap',
                          'xpctap', 'xpcacp', 'xpcagp', 'xpcapj', 'hxpcap', 'xpchp', 'xpcan', 'xbpcap', 'pxpcap',
                          'tpcap', 'xpchap', 'xpmcap', 'qxpcap', 'xpcapx', 'xqpcap', 'xpcajp', 'xpcaps', 'xpkcap',
                          'xpcaz', 'xpcaq', 'uxpcap', 'xpucap', 'xpckp', 'xpscap', 'xprcap', 'rxpcap', 'xpcrap',
                          'xqcap', 'xkpcap', 'xtcap', 'xpcai', 'xpeap', 'xpcafp', 'xpcapy', 'bpcap', 'gpcap', 'xpcapu',
                          'xptcap', 'xpsap', 'xwcap', 'xppap', 'xpiap', 'xmpcap', 'mxpcap', 'xpcape', 'xgpcap', 'xpcam',
                          'xpcapi', 'vpcap', 'xpcnap', 'xpkap', 'txpcap', 'xpmap', 'xpgap', 'xkcap', 'xpuap', 'xpcvp',
                          'xpccp', 'xpbcap', 'xzcap', 'vxpcap', 'jxpcap', 'xpceap', 'xpcop', 'xpcatp', 'wxpcap',
                          'xpcaf', 'yxpcap', 'xpcnp', 'xpcat', 'hpcap', 'xpcapt', 'xupcap', 'xpciap', 'xpycap',
                          'nxpcap', 'xpcgp', 'xpckap', 'xpcapa', 'xpcadp', 'oxpcap', 'xpcayp', 'xpcjap', 'xvpcap',
                          'x9cap', 'x-cap', 'x[cap', 'x]cap', 'x;cap', 'x(cap', 'x)cap', 'x_cap', 'x=cap', 'x+cap',
                          'x{cap', 'x}cap', 'x:cap', 'xpca9', 'xpca-', 'xpca[', 'xpca]', 'xpca;', 'xpca(', 'xpca)',
                          'xpca_', 'xpca=', 'xpca+', 'xpca{', 'xpca}', 'xpca:', 'dailsycap', 'dailycapf', 'dailycapk',
                          'dailycan', 'dailcycap', 'dtailycap', 'uailycap', 'dailycapc', 'dailycab', 'dailyeap',
                          'djilycap', 'daalycap', 'dailyccp', 'daplycap', 'daiaycap', 'dailacap', 'dailycam',
                          'dailycafp', 'dnilycap', 'dgilycap', 'djailycap', 'darlycap', 'dailycarp', 'dailycapv',
                          'udailycap', 'daiclycap', 'dayilycap', 'dailzycap', 'ddilycap', 'dailycdp', 'wailycap',
                          'dailyqap', 'daiflycap', 'dagilycap', 'jailycap', 'ydailycap', 'kailycap', 'dailyicap',
                          'dailycay', 'dailyecap', 'dailrycap', 'duailycap', 'daslycap', 'dailpcap', 'dailycau',
                          'lailycap', 'dailycyp', 'dailyclp', 'dailyncap', 'dailvycap', 'dailrcap', 'dahilycap',
                          'dailygap', 'odailycap', 'daiiycap', 'dailycai', 'dailycaps', 'dailiycap', 'dailycah',
                          'daclycap', 'dfilycap', 'dailyscap', 'daidlycap', 'daihycap', 'dailyckp', 'dailyiap',
                          'datlycap', 'dailycapt', 'dtilycap', 'dvilycap', 'dailycaa', 'dailycagp', 'dailynap',
                          'daelycap', 'diilycap', 'dailycvp', 'dailqycap', 'daimlycap', 'daizlycap', 'dailycaep',
                          'daiwycap', 'dkilycap', 'daileycap', 'daildycap', 'dawlycap', 'dailycjap', 'dailycrap',
                          'bdailycap', 'vdailycap', 'dailyhap', 'dailicap', 'dablycap', 'dmilycap', 'daflycap',
                          'dailywap', 'dailyclap', 'dailyctp', 'dailycatp', 'dailecap', 'tdailycap', 'bailycap',
                          'dailycav', 'daiuycap', 'doailycap', 'daislycap', 'dailycak', 'daidycap', 'dailykcap',
                          'idailycap', 'dailycbp', 'drilycap', 'daiqlycap', 'dcilycap', 'datilycap', 'dailycup',
                          'dailycar', 'dailyzcap', 'dailycapq', 'dailfcap', 'dailycapa', 'dvailycap', 'daiwlycap',
                          'dhilycap', 'dailycmp', 'dailycas', 'daieycap', 'dailycavp', 'iailycap', 'dadlycap',
                          'dailycaf', 'dailycaj', 'dailyaap', 'pailycap', 'dailybap', 'dailypcap', 'dacilycap',
                          'dailychp', 'dpilycap', 'vailycap', 'dhailycap', 'danilycap', 'dailycapr', 'qailycap',
                          'dgailycap', 'dailycuap', 'dailycabp', 'dailyoap', 'dailyqcap', 'dainycap', 'dpailycap',
                          'dailycfp', 'mailycap', 'dahlycap', 'dailychap', 'dlailycap', 'jdailycap', 'dailmcap',
                          'daiblycap', 'dailscap', 'dabilycap', 'davlycap', 'dazlycap', 'dailycapu', 'dailylap',
                          'dailzcap', 'daglycap', 'qdailycap', 'dailycgap', 'dailycag', 'daigycap', 'dailycpap',
                          'dailbycap', 'dailycapj', 'dailxcap', 'dailycop', 'daisycap', 'dyailycap', 'dailbcap',
                          'dailycapg', 'dailyceap', 'dailycapx', 'dailfycap', 'gdailycap', 'dailymap', 'daixlycap',
                          'dailyyap', 'dailycoap', 'daialycap', 'dailwycap', 'dailycapz', 'damilycap', 'dailycac',
                          'dailypap', 'dailocap', 'darilycap', 'davilycap', 'diailycap', 'daillcap', 'dailycacp',
                          'daiylycap', 'dailycaw', 'dairycap', 'hailycap', 'mdailycap', 'dailycapi', 'daimycap',
                          'dailyzap', 'daildcap', 'dailycahp', 'dailkcap', 'dadilycap', 'dailycadp', 'dailycep',
                          'dailybcap', 'dailycmap', 'dailytap', 'dailycaz', 'gailycap', 'dailycip', 'daielycap',
                          'daitycap', 'wdailycap', 'dyilycap', 'dailycapb', 'dailyckap', 'dailycaq', 'dapilycap',
                          'nailycap', 'daivlycap', 'dailycgp', 'dailnycap', 'dailycpp', 'ndailycap', 'dailycaup',
                          'dailycax', 'dailycapw', 'dlilycap', 'dailyuap', 'dailylcap', 'dailyjap', 'dailycapy',
                          'hdailycap', 'dailycapm', 'dailycat', 'dailyciap', 'dailyocap', 'dailycnp', 'dailycape',
                          'dailxycap', 'dailykap', 'daiyycap', 'zailycap', 'doilycap', 'pdailycap', 'daiglycap',
                          'dailycrp', 'dailmycap', 'dailncap', 'dailycyap', 'dailycjp', 'daxlycap', 'oailycap',
                          'dailycbap', 'dailyctap', 'dailycakp', 'daibycap', 'dailccap', 'tailycap', 'dmailycap',
                          'daihlycap', 'dailwcap', 'dailyrcap', 'aailycap', 'dailycad', 'dailycaph', 'dairlycap',
                          'daizycap', 'daifycap', 'duilycap', 'zdailycap', 'daylycap', 'dkailycap', 'dailycajp',
                          'yailycap', 'daqlycap', 'dbailycap', 'daivycap', 'dailycapn', 'dailyrap', 'daeilycap',
                          'damlycap', 'dailaycap', 'kdailycap', 'daixycap', 'daicycap', 'daiqycap', 'adailycap',
                          'dailycae', 'dailyacap', 'dailywcap', 'dailycapd', 'dailycanp', 'dailycamp', 'ldailycap',
                          'dailvcap', 'danlycap', 'dnailycap', 'dafilycap', 'dailqcap', 'dainlycap', 'dailycayp',
                          'dbilycap', 'dailycaip', 'dailysap', 'daijycap', 'daitlycap', 'dailycnap', 'dailymcap',
                          'deilycap', 'da7lycap', 'da&lycap', 'da*lycap', 'da(lycap', 'dai;ycap', 'dai/ycap',
                          'dai.ycap', 'dai,ycap', 'dai?ycap', 'dai>ycap', 'dai<ycap', 'dail5cap', 'dail%cap',
                          'dail^cap', 'dail&cap', 'dailyca9', 'dailyca-', 'dailyca[', 'dailyca]', 'dailyca;',
                          'dailyca(', 'dailyca)', 'dailyca_', 'dailyca=', 'dailyca+', 'dailyca{', 'dailyca}',
                          'dailyca:', 'gstwxp', 'stwxz', 'stoxp', 'stwxpb', 'sttxp', 'stwvp', 'stwxpe', 'mstwxp',
                          'stwkp', 'jtwxp', 'sbwxp', 'stwvxp', 'sowxp', 'stwxt', 'sthxp', 'vstwxp', 'stgxp', 'stwnxp',
                          'stowxp', 'stwpxp', 'stwxhp', 'stwxc', 'stwxpx', 'stwop', 'stwxnp', 'stwxa', 'stwkxp',
                          'stwxr', 'nstwxp', 'ftwxp', 'otwxp', 'styxp', 'stfxp', 'stwxu', 'stwxpk', 'stlxp', 'stwoxp',
                          'stwxqp', 'stwhp', 'stwxpm', 'kstwxp', 'stwqp', 'stwxg', 'stwxi', 'stwxb', 'stzxp', 'sbtwxp',
                          'stwtp', 'sxwxp', 'skwxp', 'sitwxp', 'stwmxp', 'stwxf', 'ytwxp', 'stmwxp', 'stwbxp', 'stwxj',
                          'stwxx', 'sutwxp', 'stwxph', 'ystwxp', 'stiwxp', 'stlwxp', 'stkwxp', 'stwlp', 'stxxp',
                          'stwjxp', 'btwxp', 'stwxs', 'pstwxp', 'stwuxp', 'qtwxp', 'stwep', 'stwxvp', 'stwxm', 'stvwxp',
                          'stwyxp', 'stwxkp', 'stwgp', 'lstwxp', 'qstwxp', 'stbwxp', 'rstwxp', 'stixp', 'spwxp',
                          'stuxp', 'stwxpa', 'stwxy', 'stnwxp', 'htwxp', 'gtwxp', 'ostwxp', 'siwxp', 'stwxpw', 'stwyp',
                          'ctwxp', 'swwxp', 'stwxh', 'ktwxp', 'stwap', 'stwxpg', 'stwxpv', 'stwxip', 'stwnp', 'stwxd',
                          'stwgxp', 'slwxp', 'stwxrp', 'mtwxp', 'stpwxp', 'stwlxp', 'stnxp', 'stjwxp', 'sptwxp',
                          'stwup', 'svwxp', 'stwpp', 'sjtwxp', 'stwfxp', 'stwxe', 'utwxp', 'stzwxp', 'stwxap', 'stwxbp',
                          'stkxp', 'scwxp', 'stwip', 'stwxps', 'stwxv', 'sswxp', 'rtwxp', 'stwxw', 'smwxp', 'stxwxp',
                          'stwbp', 'stwxpt', 'stwxjp', 'stuwxp', 'sqwxp', 'fstwxp', 'stwxwp', 'stwixp', 'stvxp',
                          'ltwxp', 'jstwxp', 'ttwxp', 'szwxp', 'stwxmp', 'stwrp', 'stwhxp', 'stjxp', 'sdwxp', 'ntwxp',
                          'stwxpr', 'suwxp', 'stwxyp', 'stcwxp', 'sltwxp', 'sjwxp', 'stwxn', 'sktwxp', 'ustwxp',
                          'stwjp', 'sntwxp', 'hstwxp', 'stwxpn', 'sewxp', 'stwtxp', 'sotwxp', 'stmxp', 'stwxq', 'ptwxp',
                          'stwxpf', 'stwxtp', 'bstwxp', 'svtwxp', 'tstwxp', 'stwxpi', 'sqtwxp', 'stpxp', 'stwfp',
                          'stwxpc', 'smtwxp', 'cstwxp', 'stwxfp', 'itwxp', 'vtwxp', 'snwxp', 'stwrxp', 'stwxep',
                          'stcxp', 'stwxpu', 'stwxpz', 'sawxp', 'strxp', 'stbxp', 'stwxpj', 'stwxpd', 'stwxgp', 'stwmp',
                          'stwwp', 'stwxup', 'stwxk', 'istwxp', 'stwxpq', 'stwxpy', 'sctwxp', 's4wxp', 's$wxp', 's%wxp',
                          's^wxp', 'st1xp', 'st!xp', 'st@xp', 'st#xp', 'stwx9', 'stwx-', 'stwx[', 'stwx]', 'stwx;',
                          'stwx(', 'stwx)', 'stwx_', 'stwx=', 'stwx+', 'stwx{', 'stwx}', 'stwx:', 'dailycpcap',
                          'dailyxcpap', 'dailyxmcap', 'dailyxbcap', 'dailyxpgap', 'adilyxpcap', 'dailyxpocap',
                          'dailyxwpcap', 'dailyxpclap', 'dailyxpcp', 'dailypxcap', 'daiyxpcap', 'dailyxpcpa',
                          'dailyxpcam', 'mailyxpcap', 'dailyxpczap', 'dailxypcap', 'dailwxpcap', 'darlyxpcap',
                          'dailybxpcap', 'daipyxpcap', 'dailyxpcape', 'dalyxpcap', 'daoilyxpcap', 'xailyxpcap',
                          'daiylxpcap', 'dialyxpcap', 'dailykpcap', 'dailyxpca', 'dailyxpycap', 'uailyxpcap',
                          'dailyxpcajp', 'djilyxpcap', 'dailyxpcap', 'djailyxpcap', 'dailyxpap', 'dailyxpcop',
                          'daizlyxpcap', 'hailyxpcap', 'dailyxpcnp', 'dailyxpacp', 'aailyxpcap', 'dailyyxpcap',
                          'dailyxpcapl', 'dilyxpcap', 'daliyxpcap', 'daqilyxpcap', 'dailyxprap', 'ailyxpcap',
                          'dayilyxpcap', 'dailyxpcwap', 'dailyxpxcap', 'dailyxpcapf', 'dakilyxpcap', 'dailyxpcak',
                          'daplyxpcap', 'dailyxvpcap', 'dailyxpcnap', 'dailyxpecap', 'dailyxpcao', 'dailixpcap',
                          'daiylyxpcap', 'dailyxpclp', 'daivlyxpcap', 'dailyxpcpap', 'dailyxpcaxp', 'dailxpcap',
                          'dailyxzpcap', 'iailyxpcap', 'dailyxvcap', 'dkailyxpcap', 'daailyxpcap', 'daillyxpcap',
                          'dailuyxpcap', 'dailyxpcsp', 'dailyxxpcap', 'dailyxpcaap', 'dailyxpctap', 'doailyxpcap',
                          'dailynpcap', 'dailyxpcamp', 'daitlyxpcap', 'daibyxpcap', 'dailytxpcap', 'qdailyxpcap',
                          'dnilyxpcap', 'daihlyxpcap', 'bdailyxpcap', 'dailyqxpcap', 'dailyxpjcap', 'dailyxpzap',
                          'dairyxpcap', 'dailyxpcbap', 'dailyxpcapo', 'dailyvpcap', 'cailyxpcap', 'dailyxpnap',
                          'dailoyxpcap', 'dailyxpcas', 'dailyxipcap', 'dailexpcap', 'dbailyxpcap', 'dailyxhcap',
                          'dailyfxpcap', 'daieyxpcap', 'dailyxpchap', 'darilyxpcap', 'dailyxpcar', 'dailyxplcap',
                          'daimyxpcap', 'dailyxzcap', 'dailyxpcxap', 'daqlyxpcap', 'dailyxphap', 'adailyxpcap',
                          'dailyexpcap', 'daeilyxpcap', 'dailyxhpcap', 'dailywpcap', 'dailyxpctp', 'dailyxpcaf',
                          'dailyxpscap', 'dailyxpcatp', 'dailuxpcap', 'dsilyxpcap', 'dailyxpfap', 'daiglyxpcap',
                          'damlyxpcap', 'dailiyxpcap', 'dadlyxpcap', 'dailyxpcmp', 'daiolyxpcap', 'dailyxpfcap',
                          'kdailyxpcap', 'dpailyxpcap', 'dailtyxpcap', 'dailyxccap', 'dailyrxpcap', 'danlyxpcap',
                          'dafilyxpcap', 'dailyxpcyap', 'vdailyxpcap', 'mdailyxpcap', 'daiplyxpcap', 'dailygpcap',
                          'dailqyxpcap', 'dadilyxpcap', 'dailyxpcaqp', 'dailyxlpcap', 'dpilyxpcap', 'dtailyxpcap',
                          'dailyxpcoap', 'zdailyxpcap', 'dawlyxpcap', 'dailzyxpcap', 'daixyxpcap', 'dailjxpcap',
                          'dailvyxpcap', 'dailyxpcapr', 'gailyxpcap', 'daifyxpcap', 'daclyxpcap', 'dcailyxpcap',
                          'dailybpcap', 'wailyxpcap', 'dailyxpvap', 'dailyxpxap', 'dailhyxpcap', 'dailympcap',
                          'dailyxqpcap', 'ddailyxpcap', 'dailyxpcapk', 'dailyxpqcap', 'dailyxpcgp', 'dailyxucap',
                          'dailyxopcap', 'dailyxpcapn', 'dailmyxpcap', 'dailyxpjap', 'dailyxpcfap', 'dailyixpcap',
                          'sailyxpcap', 'daioyxpcap', 'dgailyxpcap', 'dailbxpcap', 'dailyopcap', 'dailyxpceap',
                          'dkilyxpcap', 'dsailyxpcap', 'daiilyxpcap', 'jdailyxpcap', 'dabilyxpcap', 'daiyyxpcap',
                          'dqailyxpcap', 'dailwyxpcap', 'lailyxpcap', 'dailyuxpcap', 'dailgyxpcap', 'daslyxpcap',
                          'dailyxkpcap', 'dailqxpcap', 'dailpxpcap', 'dfailyxpcap', 'dailyxjcap', 'dahlyxpcap',
                          'deailyxpcap', 'eailyxpcap', 'dailyxpcvp', 'dailyxgpcap', 'dailyzpcap', 'dailyxpcbp',
                          'dailyxpcacp', 'dailcyxpcap', 'dxailyxpcap', 'daixlyxpcap', 'dailyxptcap', 'dailpyxpcap',
                          'dailyxpcag', 'dailyxpcfp', 'dailyxpcasp', 'sdailyxpcap', 'dailyxpeap', 'daiclyxpcap',
                          'dailfyxpcap', 'dailyxpcapc', 'dailyxpcapj', 'dajilyxpcap', 'dailyxpcaop', 'dhilyxpcap',
                          'oailyxpcap', 'dailyxpcadp', 'dailkxpcap', 'dailyxpdcap', 'dailyxxcap', 'dailyxpcaup',
                          'dailnxpcap', 'dailyxpcjap', 'dailfxpcap', 'dbilyxpcap', 'drailyxpcap', 'ddilyxpcap',
                          'dapilyxpcap', 'dailyxacap', 'dailyxpcxp', 'dailyxkcap', 'railyxpcap', 'dailyxplap',
                          'dailyxpcay', 'kailyxpcap', 'daulyxpcap', 'dailyxpcyp', 'dailyxdcap', 'dailyxpcavp',
                          'daihyxpcap', 'ndailyxpcap', 'dailayxpcap', 'dailyxpchp', 'dailydxpcap', 'wdailyxpcap',
                          'dailyxpvcap', 'doilyxpcap', 'daylyxpcap', 'dailyxncap', 'dailyypcap', 'dailyxpcapu',
                          'dailyxpzcap', 'dailyxtcap', 'dailkyxpcap', 'deilyxpcap', 'dailyzxpcap', 'dailyxpcayp',
                          'daigyxpcap', 'dailyxpdap', 'dajlyxpcap', 'dailyppcap', 'dasilyxpcap', 'dailyxpcqp',
                          'dailykxpcap', 'dablyxpcap', 'dailyxpcab', 'daxlyxpcap', 'failyxpcap', 'dailcxpcap',
                          'dailyxtpcap', 'daijlyxpcap', 'daiiyxpcap', 'dailyxpcarp', 'dailhxpcap', 'dailyxprcap',
                          'daikyxpcap', 'dtilyxpcap', 'daxilyxpcap', 'daielyxpcap', 'dailyxpcan', 'dailyxwcap',
                          'dailyxypcap', 'dailyxpgcap', 'dainyxpcap', 'dailyxpncap', 'dailyxpcaip', 'dailyxpkcap',
                          'dailyaxpcap', 'tdailyxpcap', 'edailyxpcap', 'dailyxpbap', 'dailyxapcap', 'dailyxpcaps',
                          'dailsxpcap', 'ldailyxpcap', 'bailyxpcap', 'dlilyxpcap', 'dailyxpuap', 'dailyhpcap',
                          'dailyxpccap', 'dnailyxpcap', 'dailyxecap', 'dailyxpcaph', 'datlyxpcap', 'dailyxpcad',
                          'daityxpcap', 'dailyxpcax', 'dailyxpwcap', 'datilyxpcap', 'dailryxpcap', 'dailyxpcakp',
                          'dailyxpcapy', 'dailyxocap', 'dailyxcpcap', 'dailyapcap', 'dailyxqcap', 'dailyupcap',
                          'daolyxpcap', 'dailyxpcaep', 'qailyxpcap', 'dailyxpcah', 'dailyxupcap', 'pailyxpcap',
                          'dailyxicap', 'dailyxpcaw', 'dvailyxpcap', 'daijyxpcap', 'dailyxpcapg', 'dahilyxpcap',
                          'dailyxpcapq', 'daialyxpcap', 'dailyxfcap', 'dailyxpcrap', 'dailyxscap', 'dalilyxpcap',
                          'dailyxlcap', 'dailyxpcqap', 'daklyxpcap', 'duilyxpcap', 'dailyxnpcap', 'dailyxpcapp',
                          'daimlyxpcap', 'dailvxpcap', 'dailyxpbcap', 'damilyxpcap', 'dailyhxpcap', 'dauilyxpcap',
                          'dailyxpcau', 'daiulyxpcap', 'dvilyxpcap', 'dwailyxpcap', 'dailyoxpcap', 'dailyxpoap',
                          'daidyxpcap', 'daicyxpcap', 'dailyxpcaz', 'dailyxpcdap', 'dailyxpccp', 'dailyxpsap',
                          'dailyxphcap', 'dailyspcap', 'xdailyxpcap', 'dzilyxpcap', 'dhailyxpcap', 'daiwyxpcap',
                          'daiklyxpcap', 'dailyxpiap', 'dailylpcap', 'dailyxmpcap', 'davilyxpcap', 'ydailyxpcap',
                          'dailyxpcahp', 'dailyxpacap', 'gdailyxpcap', 'dazilyxpcap', 'danilyxpcap', 'udailyxpcap',
                          'dailtxpcap', 'dailylxpcap', 'dailyxbpcap', 'dailyxrpcap', 'dailyxptap', 'dailyxycap',
                          'dailyxpcanp', 'dailyxppap', 'dailoxpcap', 'nailyxpcap', 'dailyxpcagp', 'dailytpcap',
                          'dailxyxpcap', 'dailydpcap', 'dailyxpcuap', 'dailyxpcawp', 'daiwlyxpcap', 'drilyxpcap',
                          'daildxpcap', 'dailypxpcap', 'daiflyxpcap', 'dailyxpcdp', 'daiayxpcap', 'dailsyxpcap',
                          'daillxpcap', 'dailyxpcapb', 'odailyxpcap', 'dailyxpcapz', 'davlyxpcap', 'dailyxpciap',
                          'dailyxpcae', 'dailyxpicap', 'dailyxpcvap', 'idailyxpcap', 'dzailyxpcap', 'dailyxpcac',
                          'dailyxpcjp', 'dfilyxpcap', 'dailyxpcsap', 'zailyxpcap', 'dailyxpcapm', 'daizyxpcap',
                          'dailyxpcaa', 'daildyxpcap', 'dailyxpcat', 'daiblyxpcap', 'dailyxspcap', 'daiqyxpcap',
                          'dailyxjpcap', 'dailyxpcapw', 'dailrxpcap', 'pdailyxpcap', 'dailyxpwap', 'dailyxepcap',
                          'dailyxpmap', 'dallyxpcap', 'dmilyxpcap', 'dailyxppcap', 'daflyxpcap', 'dyilyxpcap',
                          'dailyjpcap', 'fdailyxpcap', 'dailxxpcap', 'dailyxpcav', 'dainlyxpcap', 'dailyxfpcap',
                          'dailyjxpcap', 'dailzxpcap', 'dwilyxpcap', 'dxilyxpcap', 'daiqlyxpcap', 'dailyxpcaj',
                          'daelyxpcap', 'dagilyxpcap', 'dailywxpcap', 'dailyxpcai', 'dailyqpcap', 'dailymxpcap',
                          'dailmxpcap', 'dailyxpqap', 'cdailyxpcap', 'daiuyxpcap', 'dlailyxpcap', 'dawilyxpcap',
                          'dcilyxpcap', 'dailyxpcgap', 'dailyxpckap', 'dailbyxpcap', 'hdailyxpcap', 'dqilyxpcap',
                          'dairlyxpcap', 'dailyxpcrp', 'dailyxpcapt', 'dailyxpcapv', 'dacilyxpcap', 'dailyxpcabp',
                          'dgilyxpcap', 'dailyxpcapx', 'dailyxdpcap', 'dmailyxpcap', 'yailyxpcap', 'dailaxpcap',
                          'dailyxpcwp', 'dailyxpcapd', 'dailyxpcip', 'dailyxgcap', 'dailyxrcap', 'dailysxpcap',
                          'dailyxpcafp', 'daglyxpcap', 'dailgxpcap', 'dailyxpcmap', 'dailyvxpcap', 'dailnyxpcap',
                          'dailyipcap', 'dailyxpkap', 'dazlyxpcap', 'duailyxpcap', 'rdailyxpcap', 'daidlyxpcap',
                          'dailygxpcap', 'daisyxpcap', 'daileyxpcap', 'dailyxpcazp', 'dailyxpcalp', 'tailyxpcap',
                          'dailyxpckp', 'dailyxpucap', 'dailyxpcup', 'dailyxpczp', 'dailyepcap', 'dailyrpcap',
                          'dailyxpcpp', 'dailyxpcal', 'dailyxpcaq', 'dailycxpcap', 'dailyxpyap', 'daalyxpcap',
                          'dailyxpmcap', 'dailjyxpcap', 'dailyxpcep', 'dailyfpcap', 'vailyxpcap', 'dailyxpaap',
                          'dailyxpcapa', 'dailynxpcap', 'daislyxpcap', 'diilyxpcap', 'dailyxpcapi', 'jailyxpcap',
                          'daivyxpcap', 'diailyxpcap', 'dyailyxpcap', 'da7lyxpcap', 'da8lyxpcap', 'da9lyxpcap',
                          'da&lyxpcap', 'da*lyxpcap', 'da(lyxpcap', 'dai;yxpcap', 'dai/yxpcap', 'dai.yxpcap',
                          'dai,yxpcap', 'dai?yxpcap', 'dai>yxpcap', 'dai<yxpcap', 'dail5xpcap', 'dail6xpcap',
                          'dail7xpcap', 'dail%xpcap', 'dail^xpcap', 'dail&xpcap', 'dailyx9cap', 'dailyx0cap',
                          'dailyx-cap', 'dailyx[cap', 'dailyx]cap', 'dailyx;cap', 'dailyx(cap', 'dailyx)cap',
                          'dailyx_cap', 'dailyx=cap', 'dailyx+cap', 'dailyx{cap', 'dailyx}cap', 'dailyx:cap',
                          'dailyxpca9', 'dailyxpca0', 'dailyxpca-', 'dailyxpca[', 'dailyxpca]', 'dailyxpca;',
                          'dailyxpca(', 'dailyxpca)', 'dailyxpca_', 'dailyxpca=', 'dailyxpca+', 'dailyxpca{',
                          'dailyxpca}', 'dailyxpca:', 'sharedxy', 'sharedjp', 'shaeredxp', 'shatedxp', 'sfaredxp',
                          'shaedxp', 'haredxp', 'sharedxu', 'hsaredxp', 'sharedp', 'sharedx', 'shraedxp', 'sharezdxp',
                          'sharwdxp', 'shardexp', 'sharexdp', 'sqharedxp', 'shajedxp', 'sharedfp', 'sharledxp',
                          'shaerdxp', 'sharemdxp', 'csharedxp', 'sharedxr', 'sharedxup', 'isharedxp', 'sharedxjp',
                          'sharedxpc', 'sharedvxp', 'sharedgxp', 'saredxp', 'sharedxyp', 'sharadxp', 'sharevdxp',
                          'shnaredxp', 'zharedxp', 'sbaredxp', 'sharedxm', 'skharedxp', 'sharwedxp', 'shredxp',
                          'sharfdxp', 'shardxp', 'sharedvp', 'sharexp', 'sharedxpq', 'sharedpx', 'shagredxp',
                          'wharedxp', 'sharodxp', 'smaredxp', 'sharenxp', 'syharedxp', 'esharedxp', 'sharedxmp',
                          'uharedxp', 'shuredxp', 'sharedxpm', 'sharedxpv', 'sxharedxp', 'sharedwxp', 'shabedxp',
                          'qsharedxp', 'sharedxlp', 'shareuxp', 'sharjdxp', 'shareydxp', 'sharedxph', 'gsharedxp',
                          'bharedxp', 'sharedxpk', 'sharexxp', 'sahredxp', 'shaoredxp', 'hharedxp', 'shacedxp',
                          'sharedxt', 'zsharedxp', 'sharedxrp', 'sharyedxp', 'sharedup', 'ssharedxp', 'sharhedxp',
                          'shhredxp', 'shasedxp', 'shareodxp', 'sharedxhp', 'shnredxp', 'yharedxp', 'sharedjxp',
                          'sharedxpr', 'shaqedxp', 'sharedxtp', 'nsharedxp', 'sharedqp', 'sharoedxp', 'sharkedxp',
                          'shkredxp', 'sharedxh', 'snharedxp', 'qharedxp', 'shmaredxp', 'shaxredxp', 'scharedxp',
                          'svharedxp', 'sharedxip', 'stharedxp', 'fharedxp', 'shasredxp', 'sbharedxp', 'sharbedxp',
                          'sharedxpp', 'soaredxp', 'sharrdxp', 'sharqdxp', 'shharedxp', 'shareedxp', 'sharedxpd',
                          'shagedxp', 'shsredxp', 'sharehdxp', 'shareddxp', 'aharedxp', 'sharedxpt', 'siaredxp',
                          'sharedxw', 'hsharedxp', 'sharedlp', 'sharedzp', 'shqaredxp', 'sharndxp', 'shdredxp',
                          'sharvdxp', 'sharddxp', 'skaredxp', 'sharejxp', 'sharaedxp', 'sharepdxp', 'shaiedxp',
                          'sgharedxp', 'shakredxp', 'sharedgp', 'sharedxxp', 'tsharedxp', 'shayedxp', 'shanredxp',
                          'sharednxp', 'sharetdxp', 'sharbdxp', 'sharpdxp', 'sharedxop', 'szaredxp', 'vharedxp',
                          'sharpedxp', 'shareaxp', 'sharedwp', 'seharedxp', 'sharedxqp', 'sharvedxp', 'shmredxp',
                          'shareqdxp', 'shcredxp', 'sharedxpb', 'staredxp', 'shapedxp', 'shabredxp', 'sharfedxp',
                          'shzredxp', 'sjaredxp', 'shafedxp', 'sharedxpx', 'sharedxg', 'sharedxo', 'sharecdxp',
                          'shafredxp', 'jharedxp', 'sharcdxp', 'shareduxp', 'shairedxp', 'sharsedxp', 'sharedmp',
                          'tharedxp', 'sharredxp', 'usharedxp', 'shvredxp', 'shargedxp', 'shlredxp', 'shoredxp',
                          'shjredxp', 'sharefxp', 'sharedtxp', 'shwredxp', 'sharedyp', 'shkaredxp', 'shtredxp',
                          'sharejdxp', 'shearedxp', 'srharedxp', 'shanedxp', 'sharedbxp', 'shpredxp', 'jsharedxp',
                          'sharedxpy', 'sparedxp', 'shavredxp', 'sharedxsp', 'shahedxp', 'sharedxpg', 'shoaredxp',
                          'shaqredxp', 'sharxdxp', 'sharedcp', 'shbredxp', 'sharegdxp', 'shareqxp', 'sharedxwp',
                          'szharedxp', 'swaredxp', 'shaeedxp', 'shazedxp', 'sharedxs', 'vsharedxp', 'sharedxb',
                          'shazredxp', 'sharepxp', 'sharedxnp', 'shawedxp', 'shuaredxp', 'sharehxp', 'sharedxvp',
                          'soharedxp', 'sharcedxp', 'shlaredxp', 'shajredxp', 'sharedoxp', 'spharedxp', 'shiredxp',
                          'sharedxpn', 'shaaredxp', 'shraredxp', 'svaredxp', 'suaredxp', 'searedxp', 'sfharedxp',
                          'shzaredxp', 'sdharedxp', 'sharedqxp', 'sharedlxp', 'sharedbp', 'sharebxp', 'sharedtp',
                          'sharedpxp', 'shartdxp', 'sharedfxp', 'rsharedxp', 'sharedep', 'shrredxp', 'sharedkp',
                          'shawredxp', 'sharedxpa', 'shauredxp', 'shamredxp', 'sharedsp', 'sharendxp', 'sharidxp',
                          'sharedmxp', 'sharedxc', 'sharuedxp', 'shaxedxp', 'shavedxp', 'sharedxpo', 'sharebdxp',
                          'snaredxp', 'sharedkxp', 'lharedxp', 'sharedip', 'shariedxp', 'shamedxp', 'sharedxap',
                          'sharedop', 'shgredxp', 'sharedxz', 'saaredxp', 'shadredxp', 'shakedxp', 'shfaredxp',
                          'asharedxp', 'sharmedxp', 'sharesdxp', 'shbaredxp', 'sharqedxp', 'sharedaxp', 'dsharedxp',
                          'sharekdxp', 'shvaredxp', 'sharedyxp', 'sharedxe', 'shareldxp', 'shartedxp', 'lsharedxp',
                          'shdaredxp', 'shareoxp', 'sharedrxp', 'sharedxcp', 'sharegxp', 'shaledxp', 'sharezxp',
                          'sharedxx', 'eharedxp', 'shxaredxp', 'shauedxp', 'shaaedxp', 'sharedcxp', 'sharedpp',
                          'osharedxp', 'shyaredxp', 'ysharedxp', 'sheredxp', 'shsaredxp', 'suharedxp', 'sharetxp',
                          'dharedxp', 'shxredxp', 'sharedxbp', 'sharemxp', 'sharedxfp', 'psharedxp', 'sharedxi',
                          'shareexp', 'shiaredxp', 'sgaredxp', 'sharedxpj', 'shtaredxp', 'shadedxp', 'sharldxp',
                          'sharedxpe', 'sharexdxp', 'sharzdxp', 'sharedxdp', 'shjaredxp', 'shayredxp', 'sharzedxp',
                          'sharedxgp', 'xharedxp', 'shardedxp', 'sharedxv', 'sharedxk', 'shargdxp', 'sharecxp',
                          'scaredxp', 'shareidxp', 'sdaredxp', 'ksharedxp', 'sharedxpu', 'sharekxp', 'sharedxq',
                          'pharedxp', 'kharedxp', 'sharhdxp', 'slharedxp', 'sharedxkp', 'sharedrp', 'shareddp',
                          'rharedxp', 'wsharedxp', 'sharedap', 'sharedxpl', 'shapredxp', 'sharednp', 'sharedhxp',
                          'shatredxp', 'sharedxd', 'swharedxp', 'iharedxp', 'sharedxf', 'sharedxzp', 'sharewdxp',
                          'sharedixp', 'shqredxp', 'sharedsxp', 'syaredxp', 'siharedxp', 'sharedxpi', 'shareixp',
                          'mharedxp', 'shalredxp', 'sharnedxp', 'sharydxp', 'sharefdxp', 'shparedxp', 'sharedxa',
                          'sharedhp', 'sharxedxp', 'shareudxp', 'shaoedxp', 'sqaredxp', 'sharudxp', 'sharmdxp',
                          'sharelxp', 'fsharedxp', 'sharedxep', 'sharjedxp', 'msharedxp', 'shahredxp', 'sxaredxp',
                          'sharesxp', 'shareyxp', 'shyredxp', 'slaredxp', 'sharedxl', 'sharedxpw', 'sharedexp',
                          'shareadxp', 'gharedxp', 'xsharedxp', 'shacredxp', 'ssaredxp', 'sharedxn', 'sjharedxp',
                          'sharkdxp', 'bsharedxp', 'oharedxp', 'sharedzxp', 'shgaredxp', 'charedxp', 'shwaredxp',
                          'sharerxp', 'sharewxp', 'sharerdxp', 'smharedxp', 'sharsdxp', 'shfredxp', 'sharedxpf',
                          'sharedxpz', 'sharedxps', 'sharedxj', 'sraredxp', 'sharevxp', 'saharedxp', 'nharedxp',
                          'shcaredxp', 'sha3edxp', 'sha4edxp', 'sha5edxp', 'sha#edxp', 'sha$edxp', 'sha%edxp',
                          'shar4dxp', 'shar3dxp', 'shar2dxp', 'shar$dxp', 'shar#dxp', 'shar@dxp', 'sharedx9',
                          'sharedx0', 'sharedx-', 'sharedx[', 'sharedx]', 'sharedx;', 'sharedx(', 'sharedx)',
                          'sharedx_', 'sharedx=', 'sharedx+', 'sharedx{', 'sharedx}', 'sharedx:', '/accolade',
                          '/dailyxpcap', '/sharedxp'],
                 extras={'emoji': "xp_everywhere", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         "dev": False, "description_keys": ["dailyxp.slash.description"],
                         "name_keys": "dailyxp.slash.name", "experimental": True},
                 brief="dailyxp.slash.description",
                 description="{0}")
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

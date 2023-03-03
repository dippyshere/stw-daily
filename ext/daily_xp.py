"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily xp command. Returns info about the stw accolade daily xp system for the authenticated player.
"""
import orjson
import asyncio

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw


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
            print(daily_xp)
        except Exception as e:
            # TODO: debug and fix this case
            print(e)
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
            description=f"\u200b\n{stw.I18n.get('dailyxp.embed.description1', desired_lang, f'{dailyxp:,}')}\u200b\n"
                        f"{stw.I18n.get('dailyxp.embed.description2', desired_lang, f'{stw.max_daily_stw_accolade_xp - dailyxp:,}')}\u200b\n"
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
        await self.daily_xp_command(ctx, token, not bool(auth_opt_out))

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
                          'päivittäinxp', 'kullumxp', 'डेलीएक्सपी', 'デイリーXP', 'kasdien xp', 'ਡੇਲੀਐਕਸਪੀ',
                          'zilnicxp', 'даиликп', 'kila sikuxp', 'தினசரிஎக்ஸ்பி', 'రోజువారీxp', 'günlük xp', '每日经验',
                          '每日經驗', 'kasdienxp'],
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

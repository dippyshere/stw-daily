"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the power level command. currently for testing only :3
"""

import orjson

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw


class Power(ext.Cog):
    """
    Cog for the power level command idk
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, desired_lang):
        """
        Checks for errors in the public_json_response and returns True if there is an error

        Args:
            ctx: The context of the command
            public_json_response: The json response from the public API
            auth_info: The auth_info from the auth session
            final_embeds: The list of embeds to be sent
            desired_lang: The desired language of the user

        Returns:
            True if there is an error, False if there is not
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "power", acc_name, error_code,
                                                       verbiage_action="getprofile", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except:
            # no error
            return False

    async def power_command(self, ctx, authcode, auth_opt_out):
        """
        The power command

        Args:
            ctx: The context of the command
            authcode: The authcode of the user
            auth_opt_out: Whether the user has opted out of auth

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        vbucc_colour = self.client.colours["vbuck_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "power", authcode, auth_opt_out, True,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # get common core profile
        stw_request = await stw.profile_request(self.client, "query", auth_info[1])
        stw_json_response = orjson.loads(await stw_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # stw2_request = await stw.profile_request(self.client, "llamas", auth_info[1], profile_id="stw")
        # stw2_json_response = orjson.loads(await stw2_request.read())
        # print(stw2_json_response)

        # stw3_request = await stw.profile_request(self.client, "refresh_expeditions", auth_info[1], profile_id="stw")
        # stw3_json_response = orjson.loads(await stw3_request.read())
        # print(stw3_json_response)

        # check for le error code
        if await self.check_errors(ctx, stw_json_response, auth_info, final_embeds, desired_lang):
            return
        # DONE: Fix this calculation being slightly off
        # TODO: Fix some stats being missing
        # TODO: Fix superchage not being calculated
        # https://canary.discord.com/channels/757765475823517851/757768833946877992/1058604927557050438
        # https://canary.discord.com/channels/757765475823517851/1042781227767312384/1071340105035423775
        power_level, total, total_stats = stw.calculate_homebase_rating(stw_json_response)
        power_level_emoji = self.emojis['power_level']
        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('power.embed.title', desired_lang),
                                            "power_level"),
            description=f"\u200b\n{stw.I18n.get('power.embed.description', desired_lang, f'{power_level_emoji}{round(power_level, 2)}')}\u200b\n"
                        f"\u200b\n{self.emojis['fortitude']} {stw.I18n.get('research.button.fortitude', desired_lang)}: {stw.I18n.fmt_num(int(total_stats['fortitude']), desired_lang)}\n"
                        f"{self.emojis['offense']} {stw.I18n.get('research.button.offense', desired_lang)}: {stw.I18n.fmt_num(int(total_stats['offense']), desired_lang)}\n"
                        f"{self.emojis['resistance']} {stw.I18n.get('research.button.resistance', desired_lang)}: {stw.I18n.fmt_num(int(total_stats['resistance']), desired_lang)}\n"
                        f"{self.emojis['technology']} {stw.I18n.get('research.button.technology', desired_lang)}: {stw.I18n.fmt_num(int(total_stats['technology']), desired_lang)}\u200b\n\u200b",
            colour=vbucc_colour)
        try:
            embed, file = await stw.generate_power(self.client, embed, power_level, ctx.author.id)
        except:
            embed = await stw.set_thumbnail(self.client, embed, "clown")
            file = None
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, files=file)
        return

    @ext.slash_command(name='power', name_localizations=stw.I18n.construct_slash_dict("power.slash.name"),
                       description='View your Power level',
                       description_localizations=stw.I18n.construct_slash_dict("power.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashpower(self, ctx: discord.ApplicationContext,
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
                                              choices=[OptionChoice("Do not start an authentication session", "True",
                                                                    stw.I18n.construct_slash_dict(
                                                                        "generic.slash.optout.true")),
                                                       OptionChoice("Start an authentication session (Default)",
                                                                    "False",
                                                                    stw.I18n.construct_slash_dict(
                                                                        "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the power command when called via slash

        Args:
            ctx: The context of the command
            token: The authcode of the user
            auth_opt_out: Whether the user has opted out of auth
        """
        await self.power_command(ctx, token, not eval(auth_opt_out))

    @ext.command(name='power',
                 aliases=['pow', 'powerlevel', 'rating', 'level', 'pwr', 'ower', 'pwer', 'poer', 'powr', 'powe',
                          'ppower', 'poower', 'powwer', 'poweer', 'powerr', 'opwer', 'pwoer', 'poewr', 'powre', 'oower',
                          '0ower', 'lower', 'piwer', 'p9wer', 'p0wer', 'ppwer', 'plwer', 'pkwer', 'poqer', 'po2er',
                          'po3er', 'poeer', 'poder', 'poser', 'poaer', 'powwr', 'pow3r', 'pow4r', 'powrr', 'powfr',
                          'powdr', 'powsr', 'powee', 'powe4', 'powe5', 'powet', 'poweg', 'powef', 'powed', 'opower',
                          '0power', 'p0ower', 'lpower', 'plower', 'piower', 'poiwer', 'p9ower', 'po9wer', 'po0wer',
                          'popwer', 'polwer', 'pkower', 'pokwer', 'poqwer', 'powqer', 'po2wer', 'pow2er', 'po3wer',
                          'pow3er', 'poewer', 'podwer', 'powder', 'poswer', 'powser', 'poawer', 'powaer', 'powewr',
                          'powe3r', 'pow4er', 'powe4r', 'powrer', 'powfer', 'powefr', 'powedr', 'powesr', 'powere',
                          'power4', 'powe5r', 'power5', 'powetr', 'powert', 'powegr', 'powerg', 'powerf', 'powerd',
                          'owerlevel', 'pwerlevel', 'poerlevel', 'powrlevel', 'powelevel', 'powerevel', 'powerlvel',
                          'powerleel', 'powerlevl', 'powerleve', 'ppowerlevel', 'poowerlevel', 'powwerlevel',
                          'poweerlevel', 'powerrlevel', 'powerllevel', 'powerleevel', 'powerlevvel', 'powerleveel',
                          'powerlevell', 'opwerlevel', 'pwoerlevel', 'poewrlevel', 'powrelevel', 'powelrevel',
                          'powerelvel', 'powerlveel', 'powerleevl', 'powerlevle', 'oowerlevel', '0owerlevel',
                          'lowerlevel', 'piwerlevel', 'p9werlevel', 'p0werlevel', 'ppwerlevel', 'plwerlevel',
                          'pkwerlevel', 'poqerlevel', 'po2erlevel', 'po3erlevel', 'poeerlevel', 'poderlevel',
                          'poserlevel', 'poaerlevel', 'powwrlevel', 'pow3rlevel', 'pow4rlevel', 'powrrlevel',
                          'powfrlevel', 'powdrlevel', 'powsrlevel', 'poweelevel', 'powe4level', 'powe5level',
                          'powetlevel', 'poweglevel', 'poweflevel', 'powedlevel', 'powerkevel', 'poweroevel',
                          'powerpevel', 'powerlwvel', 'powerl3vel', 'powerl4vel', 'powerlrvel', 'powerlfvel',
                          'powerldvel', 'powerlsvel', 'powerlecel', 'powerlefel', 'powerlegel', 'powerlebel',
                          'powerlevwl', 'powerlev3l', 'powerlev4l', 'powerlevrl', 'powerlevfl', 'powerlevdl',
                          'powerlevsl', 'powerlevek', 'powerleveo', 'powerlevep', 'opowerlevel', '0powerlevel',
                          'p0owerlevel', 'lpowerlevel', 'plowerlevel', 'piowerlevel', 'poiwerlevel', 'p9owerlevel',
                          'po9werlevel', 'po0werlevel', 'popwerlevel', 'polwerlevel', 'pkowerlevel', 'pokwerlevel',
                          'poqwerlevel', 'powqerlevel', 'po2werlevel', 'pow2erlevel', 'po3werlevel', 'pow3erlevel',
                          'poewerlevel', 'podwerlevel', 'powderlevel', 'poswerlevel', 'powserlevel', 'poawerlevel',
                          'powaerlevel', 'powewrlevel', 'powe3rlevel', 'pow4erlevel', 'powe4rlevel', 'powrerlevel',
                          'powferlevel', 'powefrlevel', 'powedrlevel', 'powesrlevel', 'powerelevel', 'power4level',
                          'powe5rlevel', 'power5level', 'powetrlevel', 'powertlevel', 'powegrlevel', 'powerglevel',
                          'powerflevel', 'powerdlevel', 'powerklevel', 'powerlkevel', 'powerolevel', 'powerloevel',
                          'powerplevel', 'powerlpevel', 'powerlwevel', 'powerlewvel', 'powerl3evel', 'powerle3vel',
                          'powerl4evel', 'powerle4vel', 'powerlrevel', 'powerlervel', 'powerlfevel', 'powerlefvel',
                          'powerldevel', 'powerledvel', 'powerlsevel', 'powerlesvel', 'powerlecvel', 'powerlevcel',
                          'powerlevfel', 'powerlegvel', 'powerlevgel', 'powerlebvel', 'powerlevbel', 'powerlevwel',
                          'powerlevewl', 'powerlev3el', 'powerleve3l', 'powerlev4el', 'powerleve4l', 'powerlevrel',
                          'powerleverl', 'powerlevefl', 'powerlevdel', 'powerlevedl', 'powerlevsel', 'powerlevesl',
                          'powerlevekl', 'powerlevelk', 'powerleveol', 'powerlevelo', 'powerlevepl', 'powerlevelp',
                          'wr', 'pr', 'pw', 'ppwr', 'pwwr', 'pwrr', 'wpr', 'prw', 'owr', '0wr', 'lwr', 'pqr', 'p2r',
                          'p3r', 'per', 'pdr', 'psr', 'par', 'pwe', 'pw4', 'pw5', 'pwt', 'pwg', 'pwf', 'pwd', 'opwr',
                          '0pwr', 'p0wr', 'lpwr', 'plwr', 'pqwr', 'pwqr', 'p2wr', 'pw2r', 'p3wr', 'pw3r', 'pewr',
                          'pdwr', 'pwdr', 'pswr', 'pwsr', 'pawr', 'pwar', 'pwre', 'pw4r', 'pwr4', 'pw5r', 'pwr5',
                          'pwtr', 'pwrt', 'pwgr', 'pwrg', 'pwfr', 'pwrf', 'pwrd', 'evel', 'lvel', 'leel', 'levl',
                          'leve', 'llevel', 'leevel', 'levvel', 'leveel', 'levell', 'elvel', 'lveel', 'leevl', 'levle',
                          'kevel', 'oevel', 'pevel', 'lwvel', 'l3vel', 'l4vel', 'lrvel', 'lfvel', 'ldvel', 'lsvel',
                          'lecel', 'lefel', 'legel', 'lebel', 'levwl', 'lev3l', 'lev4l', 'levrl', 'levfl', 'levdl',
                          'levsl', 'levek', 'leveo', 'levep', 'klevel', 'lkevel', 'olevel', 'loevel', 'plevel',
                          'lpevel', 'lwevel', 'lewvel', 'l3evel', 'le3vel', 'l4evel', 'le4vel', 'lrevel', 'lervel',
                          'lfevel', 'lefvel', 'ldevel', 'ledvel', 'lsevel', 'lesvel', 'lecvel', 'levcel', 'levfel',
                          'legvel', 'levgel', 'lebvel', 'levbel', 'levwel', 'levewl', 'lev3el', 'leve3l', 'lev4el',
                          'leve4l', 'levrel', 'leverl', 'levefl', 'levdel', 'levedl', 'levsel', 'levesl', 'levekl',
                          'levelk', 'leveol', 'levelo', 'levepl', 'levelp', 'ating', 'rting', 'raing', 'ratng', 'ratig',
                          'ratin', 'rrating', 'raating', 'ratting', 'ratiing', 'ratinng', 'ratingg', 'arting', 'rtaing',
                          'raitng', 'ratnig', 'ratign', 'eating', '4ating', '5ating', 'tating', 'gating', 'fating',
                          'dating', 'rqting', 'rwting', 'rsting', 'rxting', 'rzting', 'raring', 'ra5ing', 'ra6ing',
                          'raying', 'rahing', 'raging', 'rafing', 'ratung', 'rat8ng', 'rat9ng', 'ratong', 'ratlng',
                          'ratkng', 'ratjng', 'ratibg', 'ratihg', 'ratijg', 'ratimg', 'ratinf', 'ratint', 'ratiny',
                          'ratinh', 'ratinb', 'ratinv', 'erating', 'reating', '4rating', 'r4ating', '5rating',
                          'r5ating', 'trating', 'rtating', 'grating', 'rgating', 'frating', 'rfating', 'drating',
                          'rdating', 'rqating', 'raqting', 'rwating', 'rawting', 'rsating', 'rasting', 'rxating',
                          'raxting', 'rzating', 'razting', 'rarting', 'ratring', 'ra5ting', 'rat5ing', 'ra6ting',
                          'rat6ing', 'rayting', 'ratying', 'rahting', 'rathing', 'ragting', 'ratging', 'rafting',
                          'ratfing', 'ratuing', 'ratiung', 'rat8ing', 'rati8ng', 'rat9ing', 'rati9ng', 'ratoing',
                          'rationg', 'ratling', 'ratilng', 'ratking', 'ratikng', 'ratjing', 'ratijng', 'ratibng',
                          'ratinbg', 'ratihng', 'ratinhg', 'ratinjg', 'ratimng', 'ratinmg', 'ratinfg', 'ratingf',
                          'ratintg', 'ratingt', 'ratinyg', 'ratingy', 'ratingh', 'ratingb', 'ratinvg', 'ratingv', 'po',
                          'ppow', 'poow', 'poww', 'opw', 'pwo', 'oow', '0ow', 'low', 'piw', 'p9w', 'p0w', 'ppw', 'plw',
                          'pkw', 'poq', 'po2', 'po3', 'poe', 'pod', 'pos', 'poa', 'opow', '0pow', 'p0ow', 'lpow',
                          'plow', 'piow', 'poiw', 'p9ow', 'po9w', 'po0w', 'popw', 'polw', 'pkow', 'pokw', 'poqw',
                          'powq', 'po2w', 'po3w', 'pow3', 'poew', 'podw', 'powd', 'posw', 'pows', 'poaw',
                          'powa', '/pow', '/level', '/homebaserating', 'homebaserating', '/power', '/powerlevel',
                          'krag', 'мощност', 'ক্ষমতা', 'Napájení', 'strøm', 'εξουσία', 'fuerza', 'võimsus', 'قدرت',
                          'tehoa', 'શક્તિ', 'iko', 'כּוֹחַ', 'शक्ति', 'snaga', 'erő', 'kekuatan', '力', 'galia',
                          'jauda', 'शक्ती', 'kuasa', 'vermogen', 'ਤਾਕਤ', 'putere', 'мощность', 'moc', 'снага', 'effekt',
                          'nguvu', 'சக்தி', 'శక్తి', 'güç', 'потужність', 'طاقت', '力量', 'pot', 'pvow', 'pdw', 'pjow',
                          'prow', 'jpow', 'powh', 'pobw', 'pfw', 'powp', 'pojw', 'pjw', 'pon', 'pocw',
                          'povw', 'pmow', 'pofw', 'powc', 'pxow', 'bpow', 'vpow', 'wpow',
                          'epow', 'pob', 'apow', 'puw', 'rpow', 'pew', 'pgw', 'qow', 'pzow',
                          'qpow', 'fpow', 'powi', 'ypow', 'powo', 'pbw', 'pxw', 'pogw', 'potw', 'pom', 'tpow', 'pol',
                          'paw', 'pyow', 'kpow', 'zow', 'pvw', 'powt', 'poy', 'psw', 'powk',
                          'cpow', 'powl', 'powz', 'pown', 'pox', 'pohw', 'pzw', 'gpow', 'kow', 'wow', 'pmw',
                          'poc', 'pog', 'npow', 'powy', 'ipow', 'phw', 'zpow', 'poxw', 'poo',
                          'pbow', 'powv', 'powx', 'por', 'powb', 'pou', 'porw', 'ptw', 'pnw', 'powg', 'pwow',
                          'paow', 'pdow', 'xpow', 'pww', 'pcw', 'pnow', 'pov', 'pcow', 'pgow', 'poz', 'ptow',
                          'poj', 'poh', 'pqow', 'ponw', 'pyw', 'pfow', 'psow', 'pouw', 'pok', 'pomw',
                          'powu', 'powj', 'pof', 'upow', 'dpow', 'poyw', 'pqw', 'puow', 'powm', 'peow', 'poi',
                          'pop', 'spow', 'powf', 'mpow', 'pozw', '9ow', '-ow', '[ow', ']ow', ';ow', '(ow', ')ow', '_ow',
                          '=ow', '+ow', '{ow', '}ow', ':ow', 'p8w', 'p;w', 'p*w', 'p(w', 'p)w', 'po1', 'po!', 'po@',
                          'po#', 'qowerlevel', 'howerlevel', 'gowerlevel', 'powbrlevel', 'powerlevelx', 'powerlcvel',
                          'powlerlevel', 'powherlevel', 'poweolevel', 'powerlelel', 'pfwerlevel', 'pxowerlevel',
                          'powcerlevel', 'powerleveb', 'powerluevel', 'pojwerlevel', 'powerlevea', 'powerlzevel',
                          'poweulevel', 'powvrlevel', 'powearlevel', 'poweblevel', 'powerlbvel', 'powerlevmel',
                          'powerlever', 'nowerlevel', 'powerievel', 'powurlevel', 'powerlevelu', 'powertevel',
                          'powehrlevel', 'powenlevel', 'powhrlevel', 'powerlnevel', 'powerlesel', 'powerljevel',
                          'poweurlevel', 'powmrlevel', 'powergevel', 'powerzevel', 'powerlevelb', 'powterlevel',
                          'polerlevel', 'powerwlevel', 'powkerlevel', 'pownerlevel', 'powerlivel', 'pwowerlevel',
                          'qpowerlevel', 'powerlevem', 'powerlehel', 'potwerlevel', 'powerleveq', 'powoerlevel',
                          'powerlevejl', 'poweprlevel', 'pfowerlevel', 'powerlevej', 'powernevel', 'powemlevel',
                          'powerlepvel', 'powerlxevel', 'poweilevel', 'pcwerlevel', 'powerlmvel', 'powerylevel',
                          'poperlevel', 'pawerlevel', 'powtrlevel', 'paowerlevel', 'ipowerlevel', 'powerhlevel',
                          'powerjlevel', 'ponwerlevel', 'powerlejvel', 'powerlevele', 'powerletel', 'powverlevel',
                          'mpowerlevel', 'pqowerlevel', 'powerlelvel', 'powenrlevel', 'powerlevex', 'cowerlevel',
                          'powerbevel', 'powerleven', 'powxrlevel', 'powerlevegl', 'powcrlevel', 'powerlavel',
                          'powerzlevel', 'pocwerlevel', 'pbwerlevel', 'powerlvvel', 'dpowerlevel', 'powerlexel',
                          'powerlevql', 'pxwerlevel', 'phowerlevel', 'jowerlevel', 'poferlevel', 'powerlevet',
                          'powerlevezl', 'towerlevel', 'rpowerlevel', 'powervevel', 'pbowerlevel', 'pouerlevel',
                          'poweplevel', 'dowerlevel', 'powerlejel', 'powerlezel', 'powerlevhel', 'povwerlevel',
                          'uowerlevel', 'powerltevel', 'powerlevelc', 'pjowerlevel', 'jpowerlevel', 'powerfevel',
                          'powberlevel', 'powerlemvel', 'powerxevel', 'psowerlevel', 'tpowerlevel', 'powerlyvel',
                          'powermevel', 'powerlkvel', 'powerleeel', 'upowerlevel', 'powerlqevel', 'wowerlevel',
                          'powerleveg', 'powerlevenl', 'gpowerlevel', 'powerlevnl', 'powerlenvel', 'powerleveld',
                          'powerwevel', 'pojerlevel', 'poweklevel', 'powercevel', 'powerljvel', 'apowerlevel',
                          'poweqlevel', 'powerlnvel', 'pdowerlevel', 'poxerlevel', 'kpowerlevel', 'pdwerlevel',
                          'pzowerlevel', 'powezlevel', 'powerleveli', 'powernlevel', 'powerlevjl', 'powereevel',
                          'powerleveil', 'powqrlevel', 'pownrlevel', 'powerlmevel', 'xowerlevel', 'ptowerlevel',
                          'powerleyel', 'pofwerlevel', 'powerlyevel', 'powerjevel', 'powerltvel', 'powerlevebl',
                          'powerilevel', 'pmowerlevel', 'powkrlevel', 'powerlxvel', 'powerlevbl', 'powprlevel',
                          'pocerlevel', 'pvowerlevel', 'pmwerlevel', 'prwerlevel', 'powerleveal', 'powerlevevl',
                          'powerlevehl', 'powyrlevel', 'powerlepel', 'powerlevexl', 'pgowerlevel', 'powellevel',
                          'pogwerlevel', 'powerlevael', 'poverlevel', 'powerlevef', 'powjrlevel', 'poierlevel',
                          'powierlevel', 'powerleovel', 'puwerlevel', 'powerlekvel', 'prowerlevel', 'poworlevel',
                          'ptwerlevel', 'powerleoel', 'powerhevel', 'poterlevel', 'powerlevelm', 'powerlevee',
                          'powerlqvel', 'eowerlevel', 'pyowerlevel', 'powerleveu', 'pnowerlevel', 'powerlevoel',
                          'powerleael', 'powgrlevel', 'pouwerlevel', 'powevlevel', 'powerlezvel', 'cpowerlevel',
                          'powerlevvl', 'powerlevely', 'powehlevel', 'powerlevpl', 'powerlevelr', 'powerlevzel',
                          'powerlevul', 'powersevel', 'powperlevel', 'powerclevel', 'powerlehvel', 'powerleveql',
                          'pozwerlevel', 'powerlevels', 'powerlevelw', 'powerleval', 'powerleqel', 'powerlewel',
                          'powerllvel', 'powerblevel', 'powerlerel', 'pjwerlevel', 'powecrlevel', 'powezrlevel',
                          'powerleuel', 'powirlevel', 'powewlevel', 'powerlevecl', 'powemrlevel', 'powerlevyel',
                          'powejrlevel', 'fpowerlevel', 'pnwerlevel', 'porwerlevel', 'powerlhvel', 'poweslevel',
                          'poweylevel', 'powerlevelz', 'poweclevel', 'powlrlevel', 'wpowerlevel', 'powerluvel',
                          'yowerlevel', 'powerlvevel', 'pozerlevel', 'powjerlevel', 'pooerlevel', 'powerlevkl',
                          'bowerlevel', 'powerlevqel', 'peowerlevel', 'puowerlevel', 'pokerlevel', 'powerlevxel',
                          'iowerlevel', 'powerlevll', 'poweryevel', 'poxwerlevel', 'kowerlevel', 'bpowerlevel',
                          'powejlevel', 'poweralevel', 'phwerlevel', 'powerlaevel', 'poweirlevel', 'powerleviel',
                          'powerlevtl', 'powerleveh', 'powmerlevel', 'powerlevec', 'powerlevey', 'poweruevel',
                          'powxerlevel', 'powerlevelj', 'powerlevelv', 'powerlevelh', 'powerlevpel', 'xpowerlevel',
                          'powerlevelg', 'powerlevlel', 'pomwerlevel', 'ponerlevel', 'powerlgvel', 'powerlevelf',
                          'powerlevela', 'powerrevel', 'powerlcevel', 'powermlevel', 'poywerlevel', 'powerlexvel',
                          'powekrlevel', 'powerlevkel', 'pqwerlevel', 'powerlievel', 'poberlevel', 'poweyrlevel',
                          'porerlevel', 'powerlevcl', 'vpowerlevel', 'hpowerlevel', 'poherlevel', 'powerleveul',
                          'pwwerlevel', 'powerlgevel', 'powerlevol', 'powerlevelq', 'powerleuvel', 'powerlevnel',
                          'powerlevtel', 'poweorlevel', 'mowerlevel', 'powerleveln', 'zowerlevel', 'aowerlevel',
                          'powerlhevel', 'pomerlevel', 'powerledel', 'npowerlevel', 'powerlpvel', 'pewerlevel',
                          'powerleveyl', 'pohwerlevel', 'poyerlevel', 'fowerlevel', 'pobwerlevel', 'powervlevel',
                          'powerdevel', 'powerlovel', 'spowerlevel', 'powyerlevel', 'powebrlevel', 'powerleiel',
                          'vowerlevel', 'powerlevez', 'powerlevyl', 'pogerlevel', 'powerlevgl', 'powerlevzl',
                          'powerlenel', 'powevrlevel', 'pvwerlevel', 'powzrlevel', 'powerlevhl', 'poweraevel',
                          'powarlevel', 'powerleyvel', 'pzwerlevel', 'powerleves', 'powzerlevel', 'powerxlevel',
                          'powerlevjel', 'powerlemel', 'powerlevil', 'ypowerlevel', 'powuerlevel', 'powerlekel',
                          'powerlzvel', 'pswerlevel', 'powerlevew', 'rowerlevel', 'pywerlevel', 'powerlevml',
                          'poweqrlevel', 'powerlevelt', 'powexrlevel', 'powerulevel', 'powerlevev', 'powexlevel',
                          'powerleqvel', 'powerlevxl', 'powerlbevel', 'powerqevel', 'powerleivel', 'powerlevei',
                          'pcowerlevel', 'powerleavel', 'powerslevel', 'powerlevuel', 'powerleved', 'powerlevetl',
                          'pgwerlevel', 'sowerlevel', 'zpowerlevel', 'powerleveml', 'powerletvel', 'epowerlevel',
                          'powelrlevel', 'powealevel', 'powgerlevel', 'powerqlevel', '9owerlevel', '-owerlevel',
                          '[owerlevel', ']owerlevel', ';owerlevel', '(owerlevel', ')owerlevel', '_owerlevel',
                          '=owerlevel', '+owerlevel', '{owerlevel', '}owerlevel', ':owerlevel', 'p8werlevel',
                          'p;werlevel', 'p*werlevel', 'p(werlevel', 'p)werlevel', 'po1erlevel', 'po!erlevel',
                          'po@erlevel', 'po#erlevel', 'pow2rlevel', 'pow$rlevel', 'pow#rlevel', 'pow@rlevel',
                          'powe3level', 'powe#level', 'powe$level', 'powe%level', 'power;evel', 'power/evel',
                          'power.evel', 'power,evel', 'power?evel', 'power>evel', 'power<evel', 'powerl2vel',
                          'powerl$vel', 'powerl#vel', 'powerl@vel', 'powerlev2l', 'powerlev$l', 'powerlev#l',
                          'powerlev@l', 'powerleve;', 'powerleve/', 'powerleve.', 'powerleve,', 'powerleve?',
                          'powerleve>', 'powerleve<', 'epwr', 'pnwr', 'pwcr', 'spwr', 'pmwr', 'jpwr', 'pwpr',
                          'pwc', 'cpwr', 'ywr', 'pws', 'pur', 'pwrb', 'apwr', 'pwp', 'gpwr', 'pwjr', 'gwr', 'pwrs',
                          'pxwr', 'phr', 'pwrp', 'pnr', 'pwrn', 'nwr', 'npwr', 'fpwr', 'pwir', 'pgr', 'pwyr', 'vpwr',
                          'pwmr', 'dwr', 'pjwr', 'pwh', 'hpwr', 'hwr', 'kwr', 'pwbr', 'pwrm', 'wwr', 'pjr', 'pwhr',
                          'plr', 'pwrk', 'ptwr', 'zpwr', 'pwb', 'pwn', 'ewr', 'pcr', 'pbr', 'bpwr', 'pwnr', 'cwr',
                          'tpwr', 'pwry', 'xwr', 'piwr', 'qwr', 'upwr', 'pwz', 'pkr', 'pwkr', 'pwk', 'rpwr', 'bwr',
                          'swr', 'pwrz', 'pwa', 'pwj', 'pfr', 'pwrx', 'pwy', 'pwx', 'pwq', 'pwur', 'twr', 'pwxr',
                          'pwor', 'pywr', 'qpwr', 'pwi', 'ypwr', 'iwr', 'pzr', 'pwu', 'jwr', 'pwvr', 'pwrl', 'mwr',
                          'pwrq', 'vwr', 'dpwr', 'pbwr', 'pwrw', 'xpwr', 'uwr', 'pwra', 'pmr', 'pwrc', 'pwl', 'pfwr',
                          'pwrj', 'pvr', 'pir', 'pyr', 'pcwr', 'ptr', 'pzwr', 'puwr', 'kpwr', 'phwr', 'pwru', 'pwzr',
                          'pwro', 'fwr', 'ipwr', 'prr', 'pvwr', 'mpwr', 'pxr', 'pkwr', 'pgwr', 'pwv', 'pwri', 'prwr',
                          'ppr', 'pwrh', 'pwm', 'pwrv', 'awr', 'zwr', 'pwlr', 'wpwr', '9wr', '-wr', '[wr', ']wr', ';wr',
                          '(wr', ')wr', '_wr', '=wr', '+wr', '{wr', '}wr', ':wr', 'p1r', 'p!r', 'p@r', 'p#r', 'pw3',
                          'pw#', 'pw$', 'pw%', 'pwrlv', 'pwrllv', 'pwlrvl', 'pwrlil', 'pwrlvh', 'pwrvll', 'pwrrlvl',
                          'pwrvl', 'prlvl', 'rpwrlvl', 'pxrlvl', 'pwrll', 'wprlvl', 'porlvl', 'pwlvl', 'cpwrlvl',
                          'prwlvl', 'pfrlvl', 'pwurlvl', 'pwclvl', 'pwrivl', 'pzwrlvl', 'pwrlvlk', 'opwrlvl', 'pwolvl',
                          'pmrlvl', 'wrlvl', 'pwrluvl', 'pwrlmvl', 'pbwrlvl', 'pwrlvql', 'pwrlol', 'pwrlvly', 'pwtlvl',
                          'pwfrlvl', 'pwrlvp', 'pwnlvl', 'pwrljl', 'pswrlvl', 'pwrlvsl', 'pwmlvl', 'pwrllvl', 'prrlvl',
                          'lpwrlvl', 'pwjrlvl', 'pwrlbl', 'pnwrlvl', 'pewrlvl', 'zpwrlvl', 'pwrlvt', 'pwrlul', 'pwrlql',
                          'pwrcvl', 'nwrlvl', 'wwrlvl', 'pwrolvl', 'pwrltvl', 'pwrclvl', 'pwrjlvl', 'pjrlvl', 'pwrylvl',
                          'pwblvl', 'pwralvl', 'wpwrlvl', 'pwrlvfl', 'pwrflvl', 'pwrlvtl', 'pwrlvyl', 'pgwrlvl',
                          'pyrlvl', 'pwrlvll', 'puwrlvl', 'prwrlvl', 'pwrbvl', 'lwrlvl', 'ypwrlvl', 'pwrlgvl', 'pwilvl',
                          'dpwrlvl', 'pkrlvl', 'pwrlvlr', 'ywrlvl', 'pwrlvb', 'ppwrlvl', 'pwrvlvl', 'pwrilvl', 'pwrlsl',
                          'zwrlvl', 'pwhrlvl', 'pwrlll', 'pwrlyl', 'gwrlvl', 'pwrlvl', 'pwrnvl', 'pwrlvld', 'pwrtlvl',
                          'dwrlvl', 'pwrlvq', 'pwrlvnl', 'pwrlgl', 'pwrlvlu', 'pwrlfl', 'pwrkvl', 'phwrlvl', 'pwrlvy',
                          'pwrlvj', 'pvrlvl', 'perlvl', 'pwrlrvl', 'pwrlvln', 'pwrlvls', 'pcrlvl', 'pwrxlvl', 'pwdlvl',
                          'kpwrlvl', 'pwrlvlx', 'pwrvvl', 'pwrlvol', 'pwmrlvl', 'pwrdlvl', 'pwzlvl', 'pwrlpvl',
                          'uwrlvl', 'pwprlvl', 'pwzrlvl', 'qwrlvl', 'xpwrlvl', 'pkwrlvl', 'apwrlvl', 'xwrlvl',
                          'pwrwlvl', 'pwyrlvl', 'pwrlvlh', 'cwrlvl', 'pwrdvl', 'pwnrlvl', 'pwruvl', 'jwrlvl', 'pgrlvl',
                          'pwrlvli', 'pwrlva', 'rwrlvl', 'ipwrlvl', 'pwrlel', 'vwrlvl', 'pwlrlvl', 'pnrlvl', 'pwxlvl',
                          'pwrltl', 'pwrlvvl', 'pwrlvlv', 'pwrklvl', 'pwrlkl', 'spwrlvl', 'hwrlvl', 'pwwrlvl',
                          'pwrlval', 'pwrlml', 'pwrlvn', 'pwulvl', 'mwrlvl', 'pwrlvr', 'fwrlvl', 'pwsrlvl', 'pwrlvx',
                          'pwrlvzl', 'powrlvl', 'pwrlvlz', 'pwrwvl', 'pwrlvbl', 'pwrxvl', 'owrlvl', 'pwrlal', 'pwrlvlg',
                          'qpwrlvl', 'pwrlvlo', 'pwrlvml', 'pqrlvl', 'pwslvl', 'pwrlvz', 'pwhlvl', 'pxwrlvl', 'pwrslvl',
                          'pwravl', 'pwrulvl', 'pwrljvl', 'pwrlfvl', 'pwrlvil', 'pwkrlvl', 'pwrlvlp', 'pwrlvlj',
                          'pwrsvl', 'iwrlvl', 'pbrlvl', 'pwplvl', 'pwrlvpl', 'pwrlvjl', 'pwrlzvl', 'tpwrlvl', 'pwrlvxl',
                          'pwxrlvl', 'pwjlvl', 'pwrlvrl', 'pwrlvv', 'pwvrlvl', 'pwalvl', 'pwrlvm', 'pwrlvi', 'pwrlvul',
                          'hpwrlvl', 'pwrlivl', 'pwrlrl', 'pwrlvwl', 'pwerlvl', 'pwrlvu', 'pwrlxl', 'pwrlcvl',
                          'pwrlevl', 'pwrhvl', 'pwrlnl', 'vpwrlvl', 'pwflvl', 'pwrovl', 'plwrlvl', 'pwrelvl', 'pdrlvl',
                          'pwrlvkl', 'pwrlvlt', 'pwirlvl', 'pwrlvk', 'pwtrlvl', 'pawrlvl', 'pwrlnvl', 'pwryvl',
                          'pwwlvl', 'pwrlvlq', 'pwrldl', 'pwklvl', 'pwrlvel', 'fpwrlvl', 'pwrlvlw', 'pwrlhl', 'pwrlvle',
                          'pwdrlvl', 'awrlvl', 'parlvl', 'pwrlvd', 'pwrlavl', 'pwrlsvl', 'pqwrlvl', 'pwglvl', 'pwrlxvl',
                          'pwgrlvl', 'pfwrlvl', 'pwrlvg', 'pwrlvlm', 'pwbrlvl', 'pwvlvl', 'mpwrlvl', 'pwrfvl',
                          'jpwrlvl', 'pwrmvl', 'pwrtvl', 'piwrlvl', 'bwrlvl', 'pcwrlvl', 'pwrlvs', 'pwrlvcl', 'pwrlvlb',
                          'pwrevl', 'pwrrvl', 'pwrlvhl', 'pwrlqvl', 'pwrnlvl', 'pjwrlvl', 'pmwrlvl', 'pwrglvl',
                          'pwrlovl', 'npwrlvl', 'pvwrlvl', 'twrlvl', 'pwarlvl', 'pwrlvla', 'kwrlvl', 'pwrlcl',
                          'bpwrlvl', 'ptwrlvl', 'ptrlvl', 'pwcrlvl', 'pwrlvf', 'pwrzvl', 'pwrqlvl', 'pwqlvl', 'pwelvl',
                          'pworlvl', 'pwrlbvl', 'pwqrlvl', 'purlvl', 'pwrlpl', 'psrlvl', 'pwrlvo', 'pwrlkvl', 'pwrhlvl',
                          'phrlvl', 'pwrlvgl', 'pwrmlvl', 'pwylvl', 'pwrlvdl', 'pwrgvl', 'pywrlvl', 'pzrlvl', 'pwrlyvl',
                          'pwrblvl', 'plrlvl', 'ewrlvl', 'epwrlvl', 'pwrlvw', 'pwrpvl', 'pwrjvl', 'pwrldvl', 'pwrlwl',
                          'pwrlve', 'pwrqvl', 'pwrlwvl', 'pprlvl', 'pwllvl', 'pwrlvlc', 'pwrlvc', 'pwrlhvl', 'pwrzlvl',
                          'pwrlzl', 'pirlvl', 'pwrlvlf', 'gpwrlvl', 'upwrlvl', 'pwrplvl', 'pdwrlvl', 'swrlvl', '9wrlvl',
                          '0wrlvl', '-wrlvl', '[wrlvl', ']wrlvl', ';wrlvl', '(wrlvl', ')wrlvl', '_wrlvl', '=wrlvl',
                          '+wrlvl', '{wrlvl', '}wrlvl', ':wrlvl', 'p1rlvl', 'p2rlvl', 'p3rlvl', 'p!rlvl', 'p@rlvl',
                          'p#rlvl', 'pw3lvl', 'pw4lvl', 'pw5lvl', 'pw#lvl', 'pw$lvl', 'pw%lvl', 'pwr;vl', 'pwr/vl',
                          'pwr.vl', 'pwr,vl', 'pwr?vl', 'pwr>vl', 'pwr<vl', 'pwrlv;', 'pwrlv/', 'pwrlv.', 'pwrlv,',
                          'pwrlv?', 'pwrlv>', 'pwrlv<', 'leveal', 'lbvel', 'sevel', 'wlevel', 'lavel', 'levela',
                          'levkl', 'lelel', 'leveli', 'lgvel', 'ltevel', 'lehel', 'glevel', 'nlevel', 'ievel', 'levee',
                          'hevel', 'lovel', 'levels', 'levevl', 'leveg', 'levqel', 'leves', 'qlevel', 'levtl', 'jlevel',
                          'elevel', 'levet', 'levef', 'levxl', 'levexl', 'levpel', 'xlevel', 'levkel', 'levyl',
                          'blevel', 'lcvel', 'gevel', 'lnevel', 'luevel', 'laevel', 'alevel', 'lqevel', 'levbl',
                          'levev', 'lexel', 'lxevel', 'llvel', 'lelvel', 'levenl', 'lgevel', 'zlevel', 'levelq',
                          'levql', 'lhevel', 'wevel', 'levmel', 'nevel', 'lekvel', 'levelb', 'leovel', 'levnel',
                          'levelv', 'levelj', 'leved', 'lzevel', 'levelz', 'tevel', 'lvevel', 'levcl', 'lnvel',
                          'levelm', 'devel', 'lehvel', 'levoel', 'revel', 'levll', 'lenel', 'lxvel', 'leyvel', 'levjl',
                          'levvl', 'levelg', 'levelr', 'zevel', 'slevel', 'levely', 'levehl', 'bevel', 'lejel', 'uevel',
                          'lekel', 'ljvel', 'lhvel', 'lmvel', 'ltvel', 'leqel', 'ulevel', 'leveu', 'aevel', 'lzvel',
                          'clevel', 'levzel', 'lewel', 'levelw', 'levezl', 'levml', 'leveul', 'lvvel', 'leviel',
                          'levhel', 'levzl', 'letel', 'leveyl', 'leveh', 'ljevel', 'lepvel', 'eevel', 'lesel', 'hlevel',
                          'levecl', 'levelh', 'levelu', 'levul', 'leveql', 'leqvel', 'dlevel', 'lepel', 'leveil',
                          'levjel', 'cevel', 'levej', 'lerel', 'levnl', 'jevel', 'levael', 'lmevel', 'lever', 'lezvel',
                          'levegl', 'yevel', 'lezel', 'levem', 'levex', 'levez', 'leveb', 'levew', 'leivel', 'levlel',
                          'leuel', 'leoel', 'lexvel', 'vevel', 'lpvel', 'lenvel', 'leyel', 'ylevel', 'lqvel', 'qevel',
                          'letvel', 'lkvel', 'fevel', 'leveln', 'levxel', 'leuvel', 'levgl', 'xevel', 'levei', 'levea',
                          'levhl', 'leael', 'lbevel', 'leveq', 'lejvel', 'levil', 'levebl', 'levol', 'levpl', 'levey',
                          'leveml', 'lemvel', 'lyvel', 'ilevel', 'leavel', 'luvel', 'levelf', 'mlevel', 'vlevel',
                          'levejl', 'tlevel', 'leven', 'livel', 'levtel', 'leveld', 'levelx', 'levele', 'levelc',
                          'ledel', 'lcevel', 'rlevel', 'flevel', 'lemel', 'leiel', 'lyevel', 'levec', 'levetl', 'leval',
                          'levelt', 'levyel', 'levuel', 'leeel', 'lievel', 'mevel', ';evel', '/evel', '.evel', ',evel',
                          '?evel', '>evel', '<evel', 'l2vel', 'l$vel', 'l#vel', 'l@vel', 'lev2l', 'lev$l', 'lev#l',
                          'lev@l', 'leve;', 'leve/', 'leve.', 'leve,', 'leve?', 'leve>', 'leve<', 'ratwng', 'ratizg',
                          'xrating', 'ratyng', 'racting', 'rbating', 'ratingc', 'ratiang', 'ryting', 'rmting', 'ratang',
                          'wating', 'rativg', 'ratipg', 'ratitg', 'raeting', 'rjating', 'ratrng', 'ratcng', 'ratiqng',
                          'rabing', 'irating', 'ratilg', 'ratinp', 'brating', 'ratpng', 'rvting', 'ratisng', 'rkating',
                          'ratbing', 'roating', 'xating', 'kating', 'riating', 'crating', 'rabting', 'ratbng',
                          'rhating', 'ratzing', 'rathng', 'rlting', 'ratinq', 'raiting', 'ratiog', 'rading', 'iating',
                          'rhting', 'ratina', 'urating', 'ratwing', 'ratinn', 'yrating', 'raoting', 'ratins', 'uating',
                          'rattng', 'cating', 'ratidg', 'lating', 'ratinsg', 'roting', 'ratinl', 'bating', 'ratinxg',
                          'ratinkg', 'ratigng', 'ratding', 'ratinrg', 'raiing', 'ratvng', 'ratiag', 'hrating',
                          'vrating', 'ratdng', 'raxing', 'ratieg', 'ramting', 'aating', 'ratingd', 'ratsng', 'ratinog',
                          'rauing', 'ratinge', 'ratinag', 'ratingk', 'ranting', 'ratxing', 'ratnng', 'raking',
                          'rativng', 'rgting', 'ratinj', 'ratinqg', 'reting', 'rbting', 'rrting', 'mating', 'ratinpg',
                          'ralting', 'ratinzg', 'ratipng', 'rapting', 'arating', 'ratiyng', 'ratind', 'ratikg',
                          'ratgng', 'ratitng', 'rpating', 'raning', 'ratinu', 'ratingq', 'ratfng', 'ratingl', 'raticng',
                          'ratiyg', 'ratingw', 'ratinx', 'ratcing', 'ratincg', 'razing', 'ratingn', 'orating',
                          'prating', 'ratingr', 'ratingm', 'rkting', 'ratixg', 'ratiqg', 'jrating', 'ratinug', 'rateng',
                          'raqing', 'ruting', 'raticg', 'rdting', 'ratinga', 'ratzng', 'rajing', 'qrating', 'ratiwg',
                          'ratping', 'raping', 'rfting', 'ratieng', 'rcting', 'hating', 'ratsing', 'racing', 'ratigg',
                          'riting', 'krating', 'raling', 'rajting', 'ravting', 'raoing', 'ratifng', 'ratisg', 'ryating',
                          'ratqng', 'ratinig', 'rakting', 'ratiwng', 'nating', 'ratini', 'ratine', 'rvating', 'nrating',
                          'ratino', 'ratiig', 'ratinr', 'wrating', 'ratxng', 'rtting', 'ratving', 'raeing', 'ratning',
                          'rpting', 'jating', 'ratirg', 'rmating', 'zrating', 'ratinlg', 'pating', 'qating', 'vating',
                          'ratiug', 'zating', 'ratinwg', 'sating', 'rjting', 'rasing', 'ratinc', 'ratinz', 'ratqing',
                          'raving', 'ratmng', 'raming', 'rateing', 'ratingz', 'ratinw', 'mrating', 'rlating', 'ratirng',
                          'ratizng', 'oating', 'raaing', 'ratingj', 'ruating', 'lrating', 'rnting', 'ratixng',
                          'ratindg', 'radting', 'ratineg', 'rnating', 'ratingo', 'rawing', 'ratifg', 'rauting',
                          'yating', 'ratingi', 'ratingp', 'ratming', 'rcating', 'ratink', 'ratidng', 'ratingx',
                          'srating', 'rataing', 'ratinm', 'ratingu', 'ratings', '3ating', '#ating', '$ating', '%ating',
                          'ra4ing', 'ra$ing', 'ra%ing', 'ra^ing', 'rat7ng', 'rat&ng', 'rat*ng', 'rat(ng', 'rati,g',
                          'rati<g', 'rvank', 'raunk', 'qank', 'rankv', 'arnk', 'ranz', 'rnak', 'rtnk', 'ranki', 'nank',
                          'rdank', 'rjank', 'rak', 'frank', 'rcnk', 'ranyk', 'rbnk', 'srank', 'rqank', 'ank',
                          'ranlk', 'raenk', 'ranok', 'rankk', 'bank', 'rangk', 'rnk', 'rafnk', 'rakn', 'rgank',
                          'rasnk', 'rauk', 'rxank', 'razk', 'raxnk', 'cank', 'rapnk', 'oank', 'nrank', 'hrank', 'orank',
                          'rapk', 'trank', 'ranmk', 'rani', 'rana', 'rxnk', 'eank', 'rankw', 'rany', 'tank', 'rwnk',
                          'jank', 'grank', 'ranc', 'rank', 'ramnk', 'ranp', 'ragk', 'rark', 'raok', 'ranq', 'rrnk',
                          'ranh', 'rhank', 'rgnk', 'wank', 'rano', 'rankl', 'rant', 'xrank', 'ryank', 'lrank', 'rsnk',
                          'ranj', 'ranrk', 'raek', 'rabk', 'ranv', 'ranbk', 'rannk', 'rankb', 'rnnk', 'raik', 'rwank',
                          'radnk', 'brank', 'ransk', 'rand', 'raank', 'ranxk', 'rqnk', 'ratnk', 'mank', 'zank', 'zrank',
                          'rpank', 'renk', 'ranwk', 'rhnk', 'rrank', 'ranpk', 'rankg', 'rakk', 'hank', 'ranqk', 'rankf',
                          'rjnk', 'rang', 'rabnk', 'ravk', 'ramk', 'xank', 'rans', 'rynk', 'ranr', 'vank', 'rkank',
                          'rack', 'raqnk', 'rask', 'ranku', 'ranvk', 'radk', 'raznk', 'qrank', 'ranka', 'ranf',
                          'rdnk', 'raak', 'rlank', 'uank', 'krank', 'rtank', 'rawk', 'ranak', 'roank', 'ranx', 'racnk',
                          'rahnk', 'rfnk', 'rankc', 'jrank', 'aank', 'ranfk', 'wrank', 'urank', 'reank', 'raonk',
                          'kank', 'rantk', 'pank', 'rankt', 'ranu', 'raink', 'rankj', 'rsank', 'runk', 'ranko', 'ranjk',
                          'ranhk', 'raxk', 'rankm', 'raqk', 'fank', 'ranik', 'rknk', 'ralk', 'rafk', 'rankr', 'sank',
                          'rfank', 'rpnk', 'rarnk', 'drank', 'rankd', 'gank', 'rann', 'dank', 'rawnk', 'rcank', 'rbank',
                          'arank', 'rvnk', 'ranm', 'ranek', 'ranke', 'ranw', 'rankz', 'rmank', 'ranky', 'ruank', 'ratk',
                          'rajk', 'rayk', 'ralnk', 'prank', 'ranzk', 'rankx', 'ranl', 'yrank', 'rankn', 'rane', 'irank',
                          'rnank', 'yank', 'ranck', 'rznk', 'erank', 'iank', 'rajnk', 'raknk', 'rahk', 'randk', 'ranb',
                          'rzank', 'rankh', 'crank', 'rmnk', 'ragnk', 'mrank', 'ronk', 'ravnk', 'rankp', 'riank',
                          'rankq', 'ranks', 'ranuk', 'raynk', 'rlnk', 'vrank', '3ank', '4ank', '5ank', '#ank', '$ank',
                          '%ank', 'ra,k', 'ra<k', 'ran.', 'ran,', 'ran>', 'ran<', 'hmoebaserating', 'homtbaserating',
                          'homebaseratieg', 'homebaseravting', 'hofmebaserating', 'homebaseratjng', 'homebasreating',
                          'homebaseratig', 'homebaseratingj', 'homebaferating', 'homebaseratting', 'homebasferating',
                          'homebasherating', 'homcebaserating', 'honebaserating', 'hombaserating', 'homebaseeating',
                          'hoebaserating', 'homebaseratign', 'homebaseratinh', 'homebaseratirng', 'homebasnrating',
                          'hombeaserating', 'hvmebaserating', 'ohmebaserating', 'homebaseratini', 'hoembaserating',
                          'haomebaserating', 'homebaserateng', 'homebaseratitng', 'homeaserating', 'homeabserating',
                          'hopebaserating', 'homedaserating', 'homebasearting', 'hmebaserating', 'omebaserating',
                          'homhbaserating', 'homebaseraking', 'homebaerating', 'homebaserting', 'homebsaerating',
                          'homebaseoating', 'hemebaserating', 'homebasexating', 'homebaaserating', 'homebaseratin',
                          'homebaserativng', 'homebaperating', 'homebaserajting', 'homebcaserating', 'homebaserahting',
                          'homebaseratinag', 'homebasernting', 'hobmebaserating', 'womebaserating', 'homebaseratinr',
                          'homebaseratingq', 'homebaseratiwg', 'homebaesrating', 'homebserating', 'homebaseratng',
                          'homebnaserating', 'homebasrating', 'homebaseratingd', 'homebasenrating', 'homebaseating',
                          'homebaserawting', 'homebaseraing', 'homebaseratlng', 'hoymebaserating', 'homebasertaing',
                          'homebasearating', 'ihomebaserating', 'homebaseratinq', 'homebasxerating', 'homebaseratgng',
                          'homebaseratimg', 'homebaseratqng', 'homedbaserating', 'homebaseratdng', 'homebaserqating',
                          'homebwaserating', 'homebaseratingi', 'homebaseratinx', 'homebasqrating', 'homebaseratpng',
                          'homebaseraitng', 'homebaseratingb', 'houebaserating', 'homebaseratnig', 'homiebaserating',
                          'homebasevating', 'humebaserating', 'homelaserating', 'homebaserataing', 'homebauserating',
                          'homebaseyrating', 'homebasefrating', 'homjbaserating', 'homebawserating', 'qhomebaserating',
                          'homebazerating', 'homenbaserating', 'homebaseratineg', 'homebayserating', 'homebqaserating',
                          'homebaseratiyg', 'homebaseiating', 'homibaserating', 'homebaseyating', 'homesaserating',
                          'homebkaserating', 'homebaseratiang', 'homebaderating', 'hohmebaserating', 'homebazserating',
                          'homebaseratinbg', 'homebaseratinf', 'homebiserating', 'homebaseratilg', 'uhomebaserating',
                          'homebaseratiyng', 'homebaseratinng', 'homebaseratyng', 'homebaseurating', 'homebaslrating',
                          'vhomebaserating', 'homebanserating', 'hjomebaserating', 'homebaseratiing', 'homebtserating',
                          'homebaseratuing', 'homebaseerating', 'homebaseraoting', 'homebaseratingk', 'homebaseratifng',
                          'homebaseratinug', 'qomebaserating', 'homebbserating', 'homeibaserating', 'homebaseratinkg',
                          'homebaseratixng', 'homebasterating', 'homebaseratidg', 'ghomebaserating', 'homejbaserating',
                          'homebaserhating', 'homebaselating', 'homebaherating', 'momebaserating', 'homefbaserating',
                          'homebaseratijng', 'homebhserating', 'homepaserating', 'homebaseaating', 'homebasmrating',
                          'homebasexrating', 'homebcserating', 'homebaseratimng', 'fhomebaserating', 'homebaseratinpg',
                          'homebaserrating', 'xhomebaserating', 'homebaserading', 'homebaseratibg', 'homebasekrating',
                          'homebaseratindg', 'ehomebaserating', 'homebaseratingp', 'vomebaserating', 'homlbaserating',
                          'homubaserating', 'homebxaserating', 'homebaseramting', 'homebrserating', 'hsomebaserating',
                          'homebaservating', 'homebarserating', 'homebaseratibng', 'homebasermting', 'homsebaserating',
                          'homebaseorating', 'homebasverating', 'hommebaserating', 'hozebaserating', 'homebaseratrng',
                          'homebaseratinga', 'homebaserkting', 'homebaseraating', 'homebaseratwng', 'homebasesating',
                          'homebasercting', 'hormebaserating', 'homebasenating', 'hlomebaserating', 'homybaserating',
                          'homebaseratingg', 'homebaseratigg', 'hsmebaserating', 'homeiaserating', 'homebfserating',
                          'homebaseratung', 'homesbaserating', 'homebmaserating', 'homebaseraping', 'homebaverating',
                          'homebaserathng', 'khomebaserating', 'homebasetrating', 'homebaiserating', 'homebqserating',
                          'hpmebaserating', 'homeobaserating', 'homebaseraticng', 'homebeserating', 'homebaserjting',
                          'homebasewating', 'homebaseratvng', 'homebaserfating', 'hrmebaserating', 'homebasyrating',
                          'homebaseratinwg', 'homebasejrating', 'hometaserating', 'homebasergating', 'hoomebaserating',
                          'homebasefating', 'homebawerating', 'pomebaserating', 'homebaseratipg', 'homebaserjating',
                          'homebaseracting', 'homebaseratingz', 'homebaserlating', 'hoamebaserating', 'homebaierating',
                          'homebdaserating', 'hoimebaserating', 'homebaseratinrg', 'homebaseratingw', 'homebxserating',
                          'homeybaserating', 'howebaserating', 'homebaseriating', 'phomebaserating', 'bhomebaserating',
                          'homebaseratihng', 'homebasdrating', 'homebasernating', 'homebaseratirg', 'homnbaserating',
                          'homebaseraving', 'homebaseratiug', 'hojebaserating', 'yomebaserating', 'hozmebaserating',
                          'homekbaserating', 'homebaserajing', 'whomebaserating', 'homebaserawing', 'homebaseratieng',
                          'homebaskerating', 'domebaserating', 'homebvaserating', 'homeebaserating', 'homeqaserating',
                          'homenaserating', 'homebascrating', 'homebaselrating', 'hmomebaserating', 'homebaseradting',
                          'homebaseratingo', 'homebaseratiny', 'homebamserating', 'homebvserating', 'homebaseratjing',
                          'homebaseratilng', 'tomebaserating', 'homebaseratitg', 'houmebaserating', 'homebasnerating',
                          'homeraserating', 'holebaserating', 'homebaseratinjg', 'homobaserating', 'homebaseratinig',
                          'homebaseratiqg', 'homebaberating', 'thomebaserating', 'homebaoerating', 'homfebaserating',
                          'homebaseratiqng', 'homecbaserating', 'homebaseraming', 'hojmebaserating', 'homebaseratling',
                          'homebasgerating', 'homekaserating', 'hosebaserating', 'gomebaserating', 'homebasperating',
                          'homebaseratinj', 'homebaserdating', 'homebaseratisg', 'homebaserkating', 'homebalerating',
                          'hkomebaserating', 'oomebaserating', 'homebasserating', 'hobebaserating', 'homvebaserating',
                          'homebaseratipng', 'hromebaserating', 'homebaeserating', 'homebaseratijg', 'lomebaserating',
                          'homebaserxating', 'hnmebaserating', 'homebaseratizg', 'hogebaserating', 'homebuserating',
                          'homwbaserating', 'homebaseirating', 'hgomebaserating', 'homebaseratinw', 'hoeebaserating',
                          'homebaseraging', 'hoqebaserating', 'homebaseratqing', 'homebaseratinc', 'hqmebaserating',
                          'homebasecating', 'homebaseracing', 'homebamerating', 'homebasertating', 'homebsserating',
                          'homebaserauing', 'homexbaserating', 'homebaseriting', 'jomebaserating', 'hjmebaserating',
                          'hombebaserating', 'hoaebaserating', 'homzebaserating', 'homebaserqting', 'homebaseratingx',
                          'homeboaserating', 'homebasarating', 'homezbaserating', 'homebaseralting', 'homebaseratoing',
                          'hhmebaserating', 'horebaserating', 'homebaseratigng', 'homebaseratind', 'homebasehating',
                          'homebaseratixg', 'homebaserateing', 'homebaseratxng', 'homebaseraying', 'homegaserating',
                          'hoemebaserating', 'homebaseryting', 'htomebaserating', 'homebyaserating', 'homebasepating',
                          'homebasezating', 'himebaserating', 'homebaserwating', 'dhomebaserating', 'homebaseratincg',
                          'homebasjerating', 'homebacserating', 'homebaseratino', 'homebtaserating', 'homebaxerating',
                          'ohomebaserating', 'homebaszrating', 'homebasebating', 'hompbaserating', 'homebajerating',
                          'hwomebaserating', 'hopmebaserating', 'homebaseratintg', 'homebasevrating', 'homsbaserating',
                          'homebakerating', 'homebaserazting', 'homebaseratzing', 'homebasxrating', 'homebaseratxing',
                          'homebaseratnng', 'homeboserating', 'homebaserxting', 'homebaseratinv', 'homemaserating',
                          'homebaseratinm', 'homebaseratinl', 'homebbaserating', 'homebasqerating', 'homebaxserating',
                          'homebaserbating', 'hotmebaserating', 'homevbaserating', 'hamebaserating', 'bomebaserating',
                          'homelbaserating', 'homebuaserating', 'homebauerating', 'homebasprating', 'homnebaserating',
                          'hombbaserating', 'homebaoserating', 'hocmebaserating', 'homewaserating', 'hotebaserating',
                          'homebaseraoing', 'homvbaserating', 'homeblserating', 'rhomebaserating', 'somebaserating',
                          'homebaseratiag', 'homebaseqrating', 'shomebaserating', 'homebaseratifg', 'eomebaserating',
                          'homebasemating', 'hhomebaserating', 'homebasewrating', 'homebaseratfng', 'fomebaserating',
                          'hcomebaserating', 'homebarerating', 'lhomebaserating', 'homrebaserating', 'homebaserationg',
                          'zomebaserating', 'homebasecrating', 'homebaseratinb', 'nhomebaserating', 'hymebaserating',
                          'homebaserbting', 'homebaseraeing', 'homhebaserating', 'homebasetating', 'homebasedrating',
                          'hooebaserating', 'homebaserathing', 'hdmebaserating', 'homeuaserating', 'homebasaerating',
                          'homebaseratingc', 'homuebaserating', 'homebaseratins', 'homebaseratingf', 'homebkserating',
                          'aomebaserating', 'homebaserauting', 'homebaseratping', 'homebaseratinqg', 'homfbaserating',
                          'hosmebaserating', 'homebaseratinmg', 'homebaseratiig', 'hohebaserating', 'homebaseroating',
                          'hzomebaserating', 'homaebaserating', 'homebaseraaing', 'heomebaserating', 'homebaserayting',
                          'hommbaserating', 'hcmebaserating', 'homepbaserating', 'homebasereting', 'homebpaserating',
                          'homdebaserating', 'homebasorating', 'hodebaserating', 'homebaseratging', 'homebaserhting',
                          'homebaseratzng', 'hxmebaserating', 'homebaseroting', 'ahomebaserating', 'homebasermating',
                          'homxebaserating', 'homewbaserating', 'homebaseratingr', 'homebaseratisng', 'homebaseranting',
                          'homebaseratiung', 'homebaserpting', 'mhomebaserating', 'homebasvrating', 'homebaseuating',
                          'homezaserating', 'homebasersting', 'hyomebaserating', 'homebaserafting', 'homebaseratinsg',
                          'chomebaserating', 'homejaserating', 'homebasierating', 'homebnserating', 'homeoaserating',
                          'homebaseratinfg', 'homebaseratingh', 'hgmebaserating', 'homebaseratving', 'homebaseraxting',
                          'hpomebaserating', 'hfomebaserating', 'homebaterating', 'homebaserwting', 'homebaseraning',
                          'homebaseratying', 'hokebaserating', 'hbmebaserating', 'homebaseratwing', 'homebaserdting',
                          'iomebaserating', 'homecaserating', 'homebaseratinvg', 'homeqbaserating', 'homebjaserating',
                          'jhomebaserating', 'honmebaserating', 'hqomebaserating', 'homebyserating', 'uomebaserating',
                          'homebasurating', 'homebaseratinzg', 'homebaseratink', 'homebmserating', 'homebaseratingl',
                          'homebasrrating', 'homebaserabing', 'homeaaserating', 'homebaseratiwng', 'homebaseratbing',
                          'homebasebrating', 'homebasderating', 'homebasirating', 'homebayerating', 'homebaseratang',
                          'homabaserating', 'homebzaserating', 'homebasergting', 'homebwserating', 'homebaswerating',
                          'hometbaserating', 'hmmebaserating', 'zhomebaserating', 'homebadserating', 'homevaserating',
                          'homebaseratingv', 'homebaserasing', 'hzmebaserating', 'homebaserattng', 'homebeaserating',
                          'homebaseratinog', 'homebaseraxing', 'homebanerating', 'homebasesrating', 'hxomebaserating',
                          'hodmebaserating', 'homgbaserating', 'homebaseryating', 'homebaseraiting', 'homebascerating',
                          'homebasejating', 'hbomebaserating', 'hlmebaserating', 'homebaserasting', 'homebaservting',
                          'homebasedating', 'homebabserating', 'homebaseratina', 'homebaseratsng', 'homebaseratings',
                          'homebaseprating', 'homebaseraqing', 'homebaserlting', 'homebaseratinp', 'homebasrerating',
                          'hovebaserating', 'homebaseqating', 'holmebaserating', 'homyebaserating', 'homebatserating',
                          'homkebaserating', 'homebastrating', 'hoxmebaserating', 'homebzserating', 'homeblaserating',
                          'homebaskrating', 'homqbaserating', 'homebagerating', 'hoqmebaserating', 'homembaserating',
                          'hnomebaserating', 'hiomebaserating', 'homebaseraling', 'hofebaserating', 'homebaserpating',
                          'homjebaserating', 'homebjserating', 'homehbaserating', 'hovmebaserating', 'homcbaserating',
                          'hwmebaserating', 'homebaseratingu', 'homebaseraring', 'homebaseratingt', 'homebasyerating',
                          'homebaseragting', 'homebaseraeting', 'homebaseratinyg', 'htmebaserating', 'homeeaserating',
                          'hogmebaserating', 'homebaseratkng', 'homerbaserating', 'homebaseratihg', 'homebaseratiog',
                          'xomebaserating', 'homebaseruating', 'homebaseratinlg', 'homeabaserating', 'homebaserafing',
                          'homebasmerating', 'homebaseratking', 'homdbaserating', 'homebasersating', 'homebasegating',
                          'komebaserating', 'homebaseratint', 'homebsaserating', 'homebaseratring', 'hdomebaserating',
                          'homtebaserating', 'yhomebaserating', 'homebafserating', 'homebaserarting', 'homebaserabting',
                          'hocebaserating', 'homebraserating', 'homebaseratfing', 'homrbaserating', 'homebaseratning',
                          'homebagserating', 'homebpserating', 'homebasehrating', 'homlebaserating', 'homebasuerating',
                          'homebaqerating', 'homgebaserating', 'homebashrating', 'hoiebaserating', 'homebaseratcing',
                          'homkbaserating', 'homebiaserating', 'homebasoerating', 'homebaeerating', 'homebdserating',
                          'homebaseratsing', 'homebasezrating', 'homebaseratikg', 'hompebaserating', 'comebaserating',
                          'homebgaserating', 'homebasemrating', 'homebaserzating', 'homeyaserating', 'homehaserating',
                          'homebasekating', 'homebaseratizng', 'homebaserahing', 'howmebaserating', 'homebaseratinu',
                          'homebahserating', 'homebaseratinxg', 'hvomebaserating', 'homebasereating', 'homebaseratidng',
                          'homebaseratinz', 'homebapserating', 'homebaslerating', 'homebaseratong', 'homebasercating',
                          'homebaqserating', 'homebaseraqting', 'homebaseratinge', 'homebaseratmng', 'homebakserating',
                          'homebassrating', 'homebaseratinhg', 'homebaseratinn', 'homebalserating', 'homebgserating',
                          'homebaseratingy', 'homebaseratingn', 'homebaseraiing', 'homebasegrating', 'homebasbrating',
                          'homoebaserating', 'homqebaserating', 'nomebaserating', 'homebajserating', 'homeubaserating',
                          'homebaseratingm', 'homebacerating', 'hkmebaserating', 'homefaserating', 'homebfaserating',
                          'homebaseratikng', 'homebasgrating', 'hoxebaserating', 'homebaseratine', 'homebaswrating',
                          'homebaserakting', 'homebaseruting', 'homebaserzting', 'romebaserating', 'homebaserativg',
                          'homebhaserating', 'homebasfrating', 'homebaaerating', 'hfmebaserating', 'homebaseratbng',
                          'homebaseratding', 'homexaserating', 'homebaseratcng', 'homebaserazing', 'homxbaserating',
                          'homebaseraticg', 'hoyebaserating', 'homwebaserating', 'homebasberating', 'homebaserrting',
                          'homebasertting', 'homebaszerating', 'homebasjrating', 'homebaserapting', 'homebavserating',
                          'homebaseratming', 'huomebaserating', 'hokmebaserating', 'homzbaserating', 'homebaserfting',
                          'homegbaserating', 'h8mebaserating', 'h9mebaserating', 'h0mebaserating', 'h;mebaserating',
                          'h*mebaserating', 'h(mebaserating', 'h)mebaserating', 'ho,ebaserating', 'ho<ebaserating',
                          'hom4baserating', 'hom3baserating', 'hom2baserating', 'hom$baserating', 'hom#baserating',
                          'hom@baserating', 'homebas4rating', 'homebas3rating', 'homebas2rating', 'homebas$rating',
                          'homebas#rating', 'homebas@rating', 'homebase3ating', 'homebase4ating', 'homebase5ating',
                          'homebase#ating', 'homebase$ating', 'homebase%ating', 'homebasera4ing', 'homebasera5ing',
                          'homebasera6ing', 'homebasera$ing', 'homebasera%ing', 'homebasera^ing', 'homebaserat7ng',
                          'homebaserat8ng', 'homebaserat9ng', 'homebaserat&ng', 'homebaserat*ng', 'homebaserat(ng',
                          'homebaserati,g', 'homebaserati<g', 'hbraing', 'hbdating', 'hrbating', 'hbratig', 'hbraitng',
                          'hyrating', 'hbratidg', 'hbratixng', 'hbratinl', 'hbratinm', 'hbating', 'hbratinfg',
                          'qhbrating', 'hbratnig', 'hbratvng', 'fhbrating', 'hbratign', 'bbrating', 'hbratking',
                          'bhrating', 'hbratung', 'hbraning', 'hbratiqng', 'hbruating', 'hbratin', 'hbratng',
                          'hbraiing', 'hbratipng', 'hbratinc', 'hbrhting', 'hbratinj', 'hbarting', 'hbratibg',
                          'hbrating', 'hbrateng', 'hbratinp', 'hbrathing', 'hbxating', 'hhrating', 'hbrateing',
                          'hbwating', 'hbratikg', 'hbrtaing', 'whbrating', 'xhbrating', 'obrating', 'hbratimg',
                          'hbratings', 'hbeating', 'tbrating', 'hbratingl', 'hbratinjg', 'jbrating', 'hbzrating',
                          'htbrating', 'rhbrating', 'hbraaing', 'hbratkng', 'hbratqng', 'hdrating', 'harating',
                          'abrating', 'hbratinq', 'hbrting', 'hbratgng', 'hurating', 'hbbating', 'hbkrating',
                          'hbratizg', 'hrbrating', 'hbrsating', 'hbrazting', 'hbrathng', 'hpbrating', 'hbratlng',
                          'hbrvting', 'hbratino', 'hblrating', 'hbratinng', 'uhbrating', 'hbrasing', 'ihbrating',
                          'hbiating', 'hbpating', 'hbratingc', 'hbratizng', 'hbraeing', 'nhbrating', 'hbratingk',
                          'hbrayting', 'hbgrating', 'hbratoing', 'hnrating', 'hbrationg', 'hbratingg', 'hbjating',
                          'hbqrating', 'hwbrating', 'hbratihg', 'hbraating', 'hlbrating', 'hbratsng', 'hbcating',
                          'hbrativng', 'hirating', 'hbraping', 'hbrlting', 'mbrating', 'hbratwng', 'hbrahting',
                          'hbratinr', 'hfbrating', 'hbratinhg', 'hbraxing', 'hbratingb', 'hbraoing', 'hblating',
                          'hbraying', 'hbrativg', 'bhbrating', 'hbratiwg', 'hbratingz', 'htrating', 'hbrzating',
                          'hbratingm', 'hbratling', 'yhbrating', 'hbrattng', 'hbratine', 'hbratcng', 'hbratiing',
                          'hbrabing', 'hbrwating', 'hbriating', 'hbrnting', 'hmrating', 'hbratinz', 'hbrnating',
                          'hbrawing', 'kbrating', 'hbratding', 'hbrakting', 'hbratingt', 'hbrhating', 'hbratiang',
                          'wbrating', 'hbtrating', 'hboating', 'hlrating', 'hbrdting', 'hbnating', 'hbrafing',
                          'hnbrating', 'hbracing', 'hjrating', 'hbratiung', 'hbratning', 'hbratingu', 'hbrpating',
                          'hbratdng', 'hbrbating', 'hbratihng', 'hbprating', 'rbrating', 'hbralting', 'lbrating',
                          'hbrfating', 'hbratilg', 'hbraeting', 'hbratming', 'hbraging', 'hbreting', 'hbruting',
                          'hbratinwg', 'hbrjting', 'hbratwing', 'hbratingj', 'hbraoting', 'hzrating', 'hbrzting',
                          'hbratingq', 'hbratibng', 'hbraming', 'hbraiting', 'hbkating', 'hcbrating', 'hbratinge',
                          'hburating', 'hbratingy', 'hbrrting', 'hbravting', 'hbratiug', 'hbraving', 'hbrpting',
                          'hbratjng', 'hbratinyg', 'hbraqing', 'hmbrating', 'hbrataing', 'hbreating', 'hbratinlg',
                          'hbratifng', 'hbratink', 'hbratingx', 'hbratinf', 'hbsating', 'hwrating', 'hbrarting',
                          'hbaating', 'hbratisg', 'hbratingh', 'hbratitng', 'hbratitg', 'hbratingw', 'hbrqating',
                          'hbmating', 'hbratinug', 'hbratinv', 'khbrating', 'hqbrating', 'hbryating', 'hbranting',
                          'hbrrating', 'hbrazing', 'hbraxting', 'hbratirg', 'hbrajing', 'hbsrating', 'hbratxing',
                          'hbrading', 'hhbrating', 'hbrabting', 'hbratang', 'hbratmng', 'hbratiog', 'hbrtating',
                          'hbfating', 'hbratinzg', 'ghbrating', 'ehbrating', 'hbtating', 'hbratintg', 'hbratiny',
                          'hbdrating', 'hbrajting', 'hbratieg', 'hbrcting', 'hbratirng', 'hubrating', 'hbratieng',
                          'hbratinn', 'hbratging', 'hbratifg', 'hbratindg', 'dbrating', 'hbratbing', 'hbfrating',
                          'hbvating', 'hbratigg', 'hbrxting', 'hbratiwng', 'hbrlating', 'hbraling', 'hbrauing',
                          'hibrating', 'hbratingp', 'hbratying', 'hbratinog', 'hbnrating', 'hbratpng', 'hbrsting',
                          'hobrating', 'hbroating', 'hbratfng', 'hbrdating', 'hbratbng', 'hbratiqg', 'hbyating',
                          'sbrating', 'hgrating', 'lhbrating', 'ebrating', 'hbratring', 'hbratint', 'fbrating',
                          'chbrating', 'hbratigng', 'xbrating', 'dhbrating', 'hbratixg', 'hbraticng', 'hbratingo',
                          'hybrating', 'hbratiag', 'hbratrng', 'thbrating', 'hjbrating', 'phbrating', 'hbrjating',
                          'hbratfing', 'hbrbting', 'hvrating', 'hbratnng', 'hbraticg', 'hbrwting', 'hbrapting',
                          'hbraking', 'hbratingi', 'hzbrating', 'hbrmating', 'hsrating', 'hbratinh', 'hrrating',
                          'hbratinxg', 'hxrating', 'hbratuing', 'hbrfting', 'hbrvating', 'hbqating', 'hkbrating',
                          'hbratcing', 'hbratilng', 'hbratiig', 'hbratins', 'hbratinw', 'hbratiyg', 'hbrqting',
                          'hbratinb', 'hbroting', 'hbrxating', 'hbxrating', 'hbgating', 'hbratineg', 'hbratzng',
                          'hbratind', 'hkrating', 'hbrawting', 'hbarating', 'hbratincg', 'hbratipg', 'hbratingf',
                          'hbratong', 'hbratinqg', 'hbyrating', 'hbbrating', 'herating', 'hbratinag', 'ybrating',
                          'hbratting', 'hbratikng', 'hebrating', 'hsbrating', 'hbrahing', 'cbrating', 'nbrating',
                          'horating', 'hbhating', 'hbratingr', 'hvbrating', 'hbrasting', 'hbratxng', 'vbrating',
                          'hbratingd', 'shbrating', 'hbratinig', 'hbratisng', 'ohbrating', 'hbratinvg', 'qbrating',
                          'hbhrating', 'hbrgting', 'hqrating', 'hbrkting', 'hbratingv', 'hbracting', 'hbirating',
                          'jhbrating', 'hbratini', 'hbratinbg', 'hbratyng', 'hbratina', 'hbjrating', 'hbraqting',
                          'habrating', 'hxbrating', 'hbvrating', 'pbrating', 'hbrcating', 'hbrauting', 'hbwrating',
                          'mhbrating', 'hbradting', 'hbcrating', 'hgbrating', 'hbrkating', 'hbratiyng', 'hbratinpg',
                          'ahbrating', 'hbrgating', 'hprating', 'hbratijg', 'hfrating', 'hbratinx', 'hbratinmg',
                          'hbratinrg', 'zbrating', 'hdbrating', 'hcrating', 'hbratinsg', 'hbratping', 'hborating',
                          'hbratinga', 'zhbrating', 'hbratsing', 'hbrmting', 'hbratving', 'hbratijng', 'hbragting',
                          'hbratingn', 'vhbrating', 'hbratinkg', 'hbraring', 'hbratinu', 'hbriting', 'hbratqing',
                          'hbratidng', 'hbryting', 'hbratzing', 'hbuating', 'hbratimng', 'hbzating', 'hbrtting',
                          'hbratjing', 'hbramting', 'gbrating', 'hbrafting', 'ibrating', 'ubrating', 'hbmrating',
                          'hberating', 'hb3ating', 'hb4ating', 'hb5ating', 'hb#ating', 'hb$ating', 'hb%ating',
                          'hbra4ing', 'hbra5ing', 'hbra6ing', 'hbra$ing', 'hbra%ing', 'hbra^ing', 'hbrat7ng',
                          'hbrat8ng', 'hbrat9ng', 'hbrat&ng', 'hbrat*ng', 'hbrat(ng', 'hbrati,g', 'hbrati<g', '/pwr',
                          '/pwrlvl', '/rating', '/rank', '/hbrating', 'pewer', 'poker', 'poweru', 'jower', 'powyer',
                          'gower', 'pzower', 'mower', 'powger', 'pmower', 'pomwer', 'xpower', 'epower', 'kower',
                          'powoer', 'cpower', 'pvwer', 'fower', 'apower', 'powvr', 'powmr', 'powenr', 'powxr', 'powew',
                          'powter', 'ptower', 'powor', 'powzer', 'powerz', 'powmer', 'gpower', 'poweq', 'psower',
                          'pouer', 'powez', 'poyer', 'zower', 'pomer', 'pdwer', 'powerv', 'pxower', 'pogwer', 'poweb',
                          'rower', 'pojer', 'powyr', 'bpower', 'powecr', 'poper', 'pywer', 'puower', 'powei', 'peower',
                          'powea', 'poweor', 'pohwer', 'aower', 'powerw', 'powper', 'yower', 'powjer', 'powery',
                          'pozwer', 'rpower', 'powher', 'porwer', 'powgr', 'powerp', 'powerb', 'powekr', 'pcower',
                          'fpower', 'powex', 'poter', 'dpower', 'powhr', 'powern', 'poweu', 'pyower', 'pbower', 'porer',
                          'ipower', 'pxwer', 'powehr', 'hpower', 'powlr', 'poweo', 'jpower', 'powero', 'prwer',
                          'powebr', 'powerc', 'pdower', 'phower', 'powber', 'cower', 'powzr', 'pozer', 'pober',
                          'powcer', 'poweyr', 'powerj', 'powejr', 'wower', 'hower', 'vpower', 'pqwer', 'powek',
                          'powxer', 'powev', 'pvower', 'pofwer', 'spower', 'pfower', 'powera', 'pfwer', 'poner',
                          'powcr', 'poywer', 'pnwer', 'pocer', 'vower', 'powner', 'pgwer', 'powbr', 'powuer', 'poxwer',
                          'ypower', 'powear', 'powem', 'paower', 'poweir', 'powezr', 'pooer', 'powes', 'powerq',
                          'puwer', 'upower', 'pofer', 'powpr', 'dower', 'pwwer', 'mpower', 'powier', 'ponwer', 'iower',
                          'pouwer', 'uower', 'poler', 'powey', 'qower', 'powerx', 'powver', 'poger', 'powelr', 'powers',
                          'pswer', 'pojwer', 'pbwer', 'povwer', 'powerl', 'tower', 'wpower', 'powep', 'powevr',
                          'powerm', 'powkr', 'poier', 'pqower', 'powur', 'poxer', 'powec', 'pocwer', 'powerh', 'nower',
                          'ptwer', 'pnower', 'powir', 'pcwer', 'powemr', 'qpower', 'eower', 'bower', 'poweri', 'pzwer',
                          'powker', 'npower', 'powqr', 'pjwer', 'xower', 'sower', 'powerk', 'powel', 'poweur', 'zpower',
                          'powen', 'powjr', 'powtr', 'phwer', 'powar', 'kpower', 'poher', 'pawer', 'potwer', 'poweqr',
                          'powexr', 'prower', 'pmwer', 'pover', 'powej', 'poweh', 'pwower', 'powler', 'powepr',
                          'pgower', 'pjower', 'tpower', 'pobwer', 'pownr', '9ower', '-ower', '[ower', ']ower', ';ower',
                          '(ower', ')ower', '_ower', '=ower', '+ower', '{ower', '}ower', ':ower', 'p8wer', 'p;wer',
                          'p*wer', 'p(wer', 'p)wer', 'po1er', 'po!er', 'po@er', 'po#er', 'pow2r', 'pow$r', 'pow#r',
                          'pow@r', 'powe3', 'powe#', 'powe$', 'powe%'],
                 extras={'emoji': "power_level", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         "dev": True, "description_keys": ['power.meta.description'], "name_key": "power.slash.name",
                         "experimental": True},
                 brief="power.meta.brief",
                 description="{0}")
    async def power(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the power command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode of the user
            optout: Whether the user has opted out of auth
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.power_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Power(client))

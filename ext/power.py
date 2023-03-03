"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
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
        # TODO: Fix this calculation being slightly off
        # TODO: Fix some stats being missing
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
        await self.power_command(ctx, token, not bool(auth_opt_out))

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
                          'ratintg', 'ratingt', 'ratinyg', 'ratingy', 'ratingh', 'ratingb', 'ratinvg', 'ratingv',
                          'po', 'ppow', 'poow', 'poww', 'opw', 'pwo', 'oow', '0ow', 'low', 'piw', 'p9w', 'p0w', 'ppw',
                          'plw', 'pkw', 'poq', 'po2', 'po3', 'poe', 'pod', 'pos', 'poa', 'opow', '0pow', 'p0ow', 'lpow',
                          'plow', 'piow', 'poiw', 'p9ow', 'po9w', 'po0w', 'popw', 'polw', 'pkow', 'pokw', 'poqw',
                          'powq', 'po2w', 'pow2', 'po3w', 'pow3', 'poew', 'podw', 'powd', 'posw', 'pows', 'poaw',
                          'powa', '/pow', '/level', '/homebaserating', 'homebaserating', '/power', '/powerlevel',
                          'krag', 'мощност', 'ক্ষমতা', 'Napájení', 'strøm', 'εξουσία', 'fuerza', 'võimsus',
                          'قدرت', 'tehoa', 'શક્તિ', 'iko', 'כּוֹחַ', 'शक्ति', 'snaga', 'erő', 'kekuatan', '力', 'galia',
                          'jauda', 'शक्ती', 'kuasa', 'vermogen', 'ਤਾਕਤ', 'putere', 'мощность', 'moc', 'снага', 'effekt',
                          'nguvu', 'சக்தி', 'శక్తి', 'güç', 'потужність', 'طاقت', '力量'],
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

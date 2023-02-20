"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the auth and kill command. handles auth sessions.
"""

import math

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


class Auth(ext.Cog):
    """
    Cog for the auth command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def auth_command(self, ctx, token='', repeated=False):
        """
        The main function of the auth command

        Args:
            ctx (discord.ext.commands.Context): The context of the command
            token: The token to authenticate with
            repeated: Whether or not the command has been repeated

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        white = self.client.colours["auth_white"]
        error_colour = self.client.colours["error_red"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "auth", token, True, True,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        # i am braindead
        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is
        if auth_info[0] is not None and ainfo3 != "logged_in_processing" and auth_info[2] != []:
            await stw.slash_edit_original(ctx, auth_info[0], auth_info[2])
        elif await stw.validate_existing_session(self.client, auth_info[1]["token"]):
            embed = await stw.create_error_embed(self.client, ctx,
                                                 stw.I18n.get('auth.embed.currentauth.title', desired_lang),
                                                 f"{stw.I18n.get('auth.embed.currentauth.description1', desired_lang)}\n"
                                                 f"```{auth_info[1]['account_name']}```\n"
                                                 f"{stw.I18n.get('auth.embed.currentauth.description2', desired_lang, self.emojis['stopwatch_anim'], '<t:{0}:R>'.format(math.floor(auth_info[1]['expiry'])))}",
                                                 prompt_newcode=True, title_emoji="whitekey", thumbnail="keycard",
                                                 colour="auth_white", auth_push_strong=False,
                                                 desired_lang=desired_lang)
            await stw.slash_edit_original(ctx, auth_info[0], embed)
        else:
            embed = await stw.create_error_embed(self.client, ctx,
                                                 description=f"{stw.I18n.get('auth.embed.currentauth.expired.description1', desired_lang)}\n"
                                                             f"```{auth_info[1]['account_name']}```\n"
                                                             f"{stw.I18n.get('auth.embed.currentauth.expired.description2', desired_lang)}\n"
                                                             f"⦾ {stw.I18n.get('auth.embed.currentauth.expired.description3', desired_lang)}\n"
                                                             f"⦾ {stw.I18n.get('auth.embed.currentauth.expired.description4', desired_lang)}",
                                                 desired_lang=desired_lang,
                                                 promptauth_key="util.error.embed.promptauth.strong1.auth")
            await stw.slash_edit_original(ctx, auth_info[0], embed)

    async def kill_command(self, ctx):
        """
        The main function of the kill command

        Args:
            ctx (discord.ext.commands.Context): The context of the command
        """
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)
        white = self.client.colours["auth_white"]
        if await stw.manslaughter_session(self.client, ctx.author.id, "override"):
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, stw.I18n.get('auth.kill.embed.title', desired_lang),
                                                "whitekey"),
                description=f"```{stw.I18n.get('auth.kill.embed.description', desired_lang)}```\n", colour=white)
        else:
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client,
                                                stw.I18n.get('auth.kill.missing.embed.title', desired_lang),
                                                "whitekey"),
                description=f"```{stw.I18n.get('auth.kill.missing.embed.description', desired_lang)}```\n",
                colour=white)

        embed = await stw.set_thumbnail(self.client, embed, "keycard")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        await stw.slash_send_embed(ctx, embed)

    @ext.command(name='auth',
                 aliases=['login', 'authenticate', "uth", "ath", "auh", "aut", "aauth", "auuth", "autth", "authh",
                          "uath", "atuh", "auht", "quth", "wuth", "suth", "xuth", "zuth", "ayth", "a7th", "a8th",
                          "aith", "akth", "ajth", "ahth", "aurh", "au5h", "au6h", "auyh", "auhh", "augh", "aufh",
                          "autg", "auty", "autu", "autj", "autn", "autb", "qauth", "aquth", "wauth", "awuth", "sauth",
                          "asuth", "xauth", "axuth", "zauth", "azuth", "ayuth", "a7uth", "au7th", "a8uth", "au8th",
                          "aiuth", "auith", "akuth", "aukth", "ajuth", "aujth", "ahuth", "auhth", "aurth", "autrh",
                          "au5th", "aut5h", "au6th", "aut6h", "auyth", "autyh", "augth", "aufth", "autfh", "autgh",
                          "authg", "authy", "autuh", "authu", "autjh", "authj", "autnh", "authn", "autbh", "authb",
                          'lgoin', 'authcode', 'gettoken', 'a', '/auth', 'code', 'ode', 'cde', 'coe', 'cod', 'ccode',
                          'coode', 'codde', 'ocde', 'cdoe', 'coed', 'xode', 'dode', 'fode', 'vode', 'cide', 'c9de',
                          'c0de', 'cpde', 'clde', 'ckde', 'cose', 'coee', 'core', 'cofe', 'coce', 'coxe', 'codw',
                          'cod3', 'cod4', 'codr', 'codf', 'codd', 'cods', 'xcode', 'cxode', 'dcode', 'cdode', 'fcode',
                          'cfode', 'vcode', 'cvode', 'ciode', 'coide', 'c9ode', 'co9de', 'c0ode', 'co0de', 'cpode',
                          'copde', 'clode', 'colde', 'ckode', 'cokde', 'cosde', 'codse', 'coede', 'codee', 'corde',
                          'codre', 'cofde', 'codfe', 'cocde', 'codce', 'coxde', 'codxe', 'codwe', 'codew', 'cod3e',
                          'code3', 'cod4e', 'code4', 'coder', 'codef', 'coded', 'codes', 'ogin', 'lgin', 'loin', 'logn',
                          'logi', 'llogin', 'loogin', 'loggin', 'logiin', 'loginn', 'olgin', 'loign', 'logni', 'kogin',
                          'oogin', 'pogin', 'ligin', 'l9gin', 'l0gin', 'lpgin', 'llgin', 'lkgin', 'lofin', 'lotin',
                          'loyin', 'lohin', 'lobin', 'lovin', 'logun', 'log8n', 'log9n', 'logon', 'logln', 'logkn',
                          'logjn', 'logib', 'logih', 'logij', 'logim', 'klogin', 'ologin', 'plogin', 'lpogin', 'liogin',
                          'loigin', 'l9ogin', 'lo9gin', 'l0ogin', 'lo0gin', 'lopgin', 'lolgin', 'lkogin', 'lokgin',
                          'lofgin', 'logfin', 'lotgin', 'logtin', 'loygin', 'logyin', 'lohgin', 'loghin', 'lobgin',
                          'logbin', 'lovgin', 'logvin', 'loguin', 'logiun', 'log8in', 'logi8n', 'log9in', 'logi9n',
                          'logoin', 'logion', 'loglin', 'logiln', 'logkin', 'logikn', 'logjin', 'logijn', 'logibn',
                          'loginb', 'logihn', 'loginh', 'loginj', 'logimn', 'loginm', 'getcode', 'getauth', 'getlogin',
                          'exchange', '/login', '/code', '/a', '/authcode', '/gettoken', '.login', '.code', '.a',
                          '.authcode', '.gettoken'],
                 extras={'emoji': "keycard", 'args': {
                     'generic.meta.args.authcode': ['auth.slash.token', True]},
                         "dev": False, "description_keys": ['auth.meta.description1', 'auth.meta.description2',
                                                            ['auth.meta.description3',
                                                             'https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode'],
                                                            'auth.meta.description4',
                                                            ['auth.meta.description5', '<@mention_me> auth'],
                                                            'auth.meta.description6', 'auth.meta.description7',
                                                            'auth.meta.description8',
                                                            ['auth.meta.description9',
                                                             '<@mention_me> auth a51c1f4d35b1457c8e34a1f6026faa35'],
                                                            ['auth.meta.description10', '💡'],
                                                            ['auth.meta.description11', '<@mention_me> device'],
                                                            'auth.meta.description12'],
                         "name_key": "auth.slash.name"},
                 brief="auth.slash.description",
                 description='{0}\n{1}\n\u200b\n⦾ {2}\n⦾ {3}\n⦾ {4}\n⦾ {5}\n⦾ {6}\n{7}\n\n```json\n{'
                             '"redirectUrl":"https://accounts.epicgames.com/fnauth?code'
                             '=a51c1f4d35b1457c8e34a1f6026faa35","sid":null})```\n{8}\n{9}\n⦾ {10}\n⦾ {11}')
    async def auth(self, ctx, token=''):
        """
        This function is the entry point for the auth command when called traditionally

        Args:
            ctx: The context of the command
            token: The authcode to use for authentication
        """
        await self.auth_command(ctx, token)

    @ext.command(name='kill',
                 aliases=['koll', 'ki9ll', 'imakillyou', 'k8ll', 'kkll', 'mkill', 'kuill', 'end', 'oill', 'kjill',
                          'k8ill', 'k9ill', 'bai', 'keel-over-and-die' 'ill', 'jill', 'kiol', 'klill', 'kil', 'ikll',
                          'kikll', 'kipl', 'kilk', 'okill', 'klll', 'kilkl', 'kilol', 'kipll', 'ikill', 'lkill',
                          'kilpl', 'mill', 'bye', 'kjll', 'koill', 'baibai', 'killk', 'kilo', 'k9ll', 'kkill', 'killl',
                          'killo', 'kll', 'killp', 'kikl', 'kioll', 'iill', 'kull', 'jkill', 'kmill', 'klil', '🔪',
                          'kiull', 'kiill', 'lill', 'kijll', 'kilp', 'ki8ll', 'logout', 'logoff', '/logout', '/logoff',
                          '/kill', 'nd', 'ed', 'en', 'eend', 'ennd', 'endd', 'ned', 'edn', 'wnd', '3nd', '4nd', 'rnd',
                          'fnd', 'dnd', 'snd', 'ebd', 'ehd', 'ejd', 'emd', 'ens', 'ene', 'enr', 'enf', 'enc', 'enx',
                          'wend', 'ewnd', '3end', 'e3nd', '4end', 'e4nd', 'rend', 'ernd', 'fend', 'efnd', 'dend',
                          'ednd', 'send', 'esnd', 'ebnd', 'enbd', 'ehnd', 'enhd', 'ejnd', 'enjd', 'emnd', 'enmd',
                          'ensd', 'ends', 'ened', 'ende', 'enrd', 'endr', 'enfd', 'endf', 'encd', 'endc', 'enxd',
                          'endx', 'ogout', 'lgout', 'loout', 'logut', 'logot', 'logou', 'llogout', 'loogout', 'loggout',
                          'logoout', 'logouut', 'logoutt', 'olgout', 'lgoout', 'loogut', 'loguot', 'logotu', 'kogout',
                          'oogout', 'pogout', 'ligout', 'l9gout', 'l0gout', 'lpgout', 'llgout', 'lkgout', 'lofout',
                          'lotout', 'loyout', 'lohout', 'lobout', 'lovout', 'logiut', 'log9ut', 'log0ut', 'logput',
                          'loglut', 'logkut', 'logoyt', 'logo7t', 'logo8t', 'logoit', 'logokt', 'logojt', 'logoht',
                          'logour', 'logou5', 'logou6', 'logouy', 'logouh', 'logoug', 'logouf', 'klogout', 'lkogout',
                          'ologout', 'plogout', 'lpogout', 'liogout', 'loigout', 'l9ogout', 'lo9gout', 'l0ogout',
                          'lo0gout', 'lopgout', 'lolgout', 'lokgout', 'lofgout', 'logfout', 'lotgout', 'logtout',
                          'loygout', 'logyout', 'lohgout', 'loghout', 'lobgout', 'logbout', 'lovgout', 'logvout',
                          'logiout', 'logoiut', 'log9out', 'logo9ut', 'log0out', 'logo0ut', 'logpout', 'logoput',
                          'loglout', 'logolut', 'logkout', 'logokut', 'logoyut', 'logouyt', 'logo7ut', 'logou7t',
                          'logo8ut', 'logou8t', 'logouit', 'logoukt', 'logojut', 'logoujt', 'logohut', 'logouht',
                          'logourt', 'logoutr', 'logou5t', 'logout5', 'logou6t', 'logout6', 'logouty', 'logouth',
                          'logougt', 'logoutg', 'logouft', 'logoutf', '.logout', '/end', 'welp', 'kys', 'kms'],
                 extras={'emoji': "whitekey", "args": {}, "dev": False,
                         "description_keys": ['auth.kill.meta.description1', 'auth.kill.meta.description2'],
                         "name_key": "auth.kill.slash.name"},
                 brief="auth.kill.slash.description",
                 description="{0}\n{1}")
    async def kill(self, ctx):
        """
        This function is the entry point for the kill command when called traditionally

        Args:
            ctx: The context of the command
        """
        await self.kill_command(ctx)

    @slash_command(name='auth', name_localizations=stw.I18n.construct_slash_dict("auth.slash.name"),
                   description='Login with your Epic Games authcode and start an authentication session',
                   description_localizations=stw.I18n.construct_slash_dict("auth.slash.description"),
                   guild_ids=stw.guild_ids)
    async def slashauth(self, ctx: discord.ApplicationContext,
                        token: Option(
                            description="Your Epic Games authcode. Leave this blank to get one",
                            description_localizations=stw.I18n.construct_slash_dict(
                                "auth.slash.token"),
                            name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                            min_length=32, default="") = ""):
        """
        This function is the entry point for the auth command when called via slash commands
        Args:
            ctx: The context of the command
            token: The authcode to use for authentication
        """
        await self.auth_command(ctx, token)

    @slash_command(name='kill', name_localizations=stw.I18n.construct_slash_dict("auth.kill.slash.name"),
                   description='End your active authentication session',
                   description_localizations=stw.I18n.construct_slash_dict("auth.kill.slash.description"),
                   guild_ids=stw.guild_ids)
    async def slashkill(self, ctx):
        """
        This function is the entry point for the kill command when called via slash commands

        Args:
            ctx: The context of the command
        """
        await self.kill_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Auth(client))

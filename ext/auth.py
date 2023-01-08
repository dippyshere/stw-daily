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
        white = self.client.colours["auth_white"]
        error_colour = self.client.colours["error_red"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "auth", token, True, True)
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
            # TODO: update this to a view + use config["login_links"]["logout_login_fortnite_pc"]
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Currently Authenticated", "whitekey"),
                                  description=(f"\u200b\n"
                                               f"Existing Auth Session Found For:\n"
                                               f"```{auth_info[1]['account_name']}```\n"
                                               f"{self.emojis['stopwatch_anim']} **Your auth session expires** <t:{math.floor(auth_info[1]['expiry'])}:R>\n"
                                               f"\u200b\n"
                                               f"Rerun this command with a new auth code to change accounts, you can get one from:\n"
                                               f"[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)\n"
                                               f"[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n\n"
                                               f"**Need Help? Run**\n"
                                               f"{await stw.mention_string(self.client, 'help auth')}\n"
                                               f"Or [Join the support server]({self.client.config['support_url']})\n"
                                               f"Note: You need a new code __each time you authenticate__\n\u200b\n"),
                                  colour=white)
            embed = await stw.set_thumbnail(self.client, embed, "keycard")
            embed = await stw.add_requested_footer(ctx, embed)
            await stw.slash_edit_original(ctx, auth_info[0], embed)
        else:
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, stw.random_error(self.client), "error"),
                description=(f"\u200b\n"
                             f"Your auth session has expired prematurely for:\n"
                             f"```{auth_info[1]['account_name']}```\n"
                             f"⦾ This can happen if you launch the game after authenticating.\n"
                             f"\u200b\n"
                             f"You'll need to reauthenticate with a new code, you can get one from:\n"
                             f"[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)\n"
                             f"[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n\n"
                             f"**Need Help? Run**\n"
                             f"{await stw.mention_string(self.client, 'help auth')}\n"
                             f"Or [Join the support server]({self.client.config['support_url']})\n"
                             f"Note: You need a new code __each time you authenticate__\n\u200b\n"
                             f"            ")
                , colour=error_colour)
            embed = await stw.set_thumbnail(self.client, embed, "error")
            embed = await stw.add_requested_footer(ctx, embed)
            await stw.slash_edit_original(ctx, auth_info[0], embed)

    async def kill_command(self, ctx):
        """
        The main function of the kill command

        Args:
            ctx (discord.ext.commands.Context): The context of the command
        """
        white = self.client.colours["auth_white"]
        if await stw.manslaughter_session(self.client, ctx.author.id, "override"):
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Killed Auth Session", "whitekey"),
                                  description=f"```Successfully ended authentication session```\n", colour=white)
        else:
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Kill Auth Session", "whitekey"),
                                  description=f"```You have no sessions to kill```\n", colour=white)

        embed = await stw.set_thumbnail(self.client, embed, "keycard")
        embed = await stw.add_requested_footer(ctx, embed)
        await stw.slash_send_embed(ctx, embed)

    @ext.command(name='auth',
                 aliases=['login', 'authenticate', "uth", "ath", "auh", "aut",
                          "aauth", "auuth", "autth", "authh", "uath", "atuh",
                          "auht", "quth", "wuth", "suth", "xuth", "zuth", "ayth",
                          "a7th", "a8th", "aith", "akth", "ajth", "ahth", "aurh",
                          "au5h", "au6h", "auyh", "auhh", "augh", "aufh", "autg",
                          "auty", "autu", "autj", "autn", "autb", "qauth", "aquth",
                          "wauth", "awuth", "sauth", "asuth", "xauth", "axuth", "zauth",
                          "azuth", "ayuth", "a7uth", "au7th", "a8uth", "au8th",
                          "aiuth", "auith", "akuth", "aukth", "ajuth", "aujth", "ahuth",
                          "auhth", "aurth", "autrh", "au5th", "aut5h", "au6th", "aut6h",
                          "auyth", "autyh", "augth", "aufth",
                          "autfh", "autgh", "authg", "authy", "autuh", "authu",
                          "autjh", "authj", "autnh", "authn", "autbh", "authb", 'lgoin',
                          'authcode', 'gettoken', 'a', '/auth',
                          'code', 'ode', 'cde', 'coe', 'cod', 'ccode', 'coode', 'codde', 'ocde', 'cdoe', 'coed', 'xode',
                          'dode', 'fode', 'vode', 'cide', 'c9de', 'c0de', 'cpde', 'clde', 'ckde', 'cose', 'coee',
                          'core', 'cofe', 'coce', 'coxe', 'codw', 'cod3', 'cod4', 'codr', 'codf', 'codd', 'cods',
                          'xcode', 'cxode', 'dcode', 'cdode', 'fcode', 'cfode', 'vcode', 'cvode', 'ciode', 'coide',
                          'c9ode', 'co9de', 'c0ode', 'co0de', 'cpode', 'copde', 'clode', 'colde', 'ckode', 'cokde',
                          'cosde', 'codse', 'coede', 'codee', 'corde', 'codre', 'cofde', 'codfe', 'cocde', 'codce',
                          'coxde', 'codxe', 'codwe', 'codew', 'cod3e', 'code3', 'cod4e', 'code4', 'coder', 'codef',
                          'coded', 'codes', 'ogin', 'lgin', 'loin', 'logn', 'logi', 'llogin', 'loogin', 'loggin',
                          'logiin', 'loginn', 'olgin', 'loign', 'logni', 'kogin', 'oogin', 'pogin', 'ligin', 'l9gin',
                          'l0gin', 'lpgin', 'llgin', 'lkgin', 'lofin', 'lotin', 'loyin', 'lohin', 'lobin', 'lovin',
                          'logun', 'log8n', 'log9n', 'logon', 'logln', 'logkn', 'logjn', 'logib', 'logih', 'logij',
                          'logim', 'klogin', 'ologin', 'plogin', 'lpogin', 'liogin', 'loigin', 'l9ogin', 'lo9gin',
                          'l0ogin', 'lo0gin', 'lopgin', 'lolgin', 'lkogin', 'lokgin', 'lofgin', 'logfin', 'lotgin',
                          'logtin', 'loygin', 'logyin', 'lohgin', 'loghin', 'lobgin', 'logbin', 'lovgin', 'logvin',
                          'loguin', 'logiun', 'log8in', 'logi8n', 'log9in', 'logi9n', 'logoin', 'logion', 'loglin',
                          'logiln', 'logkin', 'logikn', 'logjin', 'logijn', 'logibn', 'loginb', 'logihn', 'loginh',
                          'loginj', 'logimn', 'loginm',
                          'getcode', 'getauth', 'getlogin', 'exchange', '/login', '/code', '/a', '/authcode',
                          '/gettoken'],
                 extras={'emoji': "keycard", 'args': {
                     'token': "Your Epic Games authcode. Leave this blank to get one."},
                         "dev": False},
                 brief="Login with your Epic Games authcode and start an authentication session",
                 description=(  # TODO: update this help message
                         "This command allows you to claim your Fortnite: Save The World rewards including dailies, "
                         "research points and llamas, utilise other utility commands etc, Note that you must get a "
                         "new token __each time you authenticate__. For a guide on how to authenticate\n\u200b\n "
                         "\n[Firstly visit this link by clicking here](https://tinyurl.com/epicauthcode) You'll have "
                         "to sign into your epic account, and then you should see something like:\n "
                         "\n```yaml\n{\"redirectUrl\":\"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b1457c8e34a1f6026faa35\",\"sid\":null})```\n"
                         "Copy only the authentication token part which for our example would be:\n"
                         "```a51c1f4d35b1457c8e34a1f6026faa35```\n"
                         "Your authentication token should be different and this is __NOT__ [the code from the url, "
                         "instead it is the one from the web page.]("
                         "https://cdn.discordapp.com/attachments/757768833946877992/874560824482623568/unknown.png)\n"
                         "\n "
                         "After retrieving this token simply paste it as an argument into the command like:\n\n"
                         "<@mention_me> auth a51c1f4d35b1457c8e34a1f6026faa35\n\n\n"
                         "💡 **Tips:**\n"
                         "⦾ After using the url where you have to login, you can just simply [use this link](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code) instead which will directly give you the authcode without having to sign in\n"
                         "\n⦾ In most browsers, double click on or below the code and it should highlight just the "
                         "code making it easier to copy, you can also just refresh the last page with the authcode\n\n "
                         "⦾ You can claim your daily once every day, check when you can claim it again by checking the bots status.\n\u200b\n\n"
                         "**Important Disclaimer:**\n"
                         "AFAIK, your auth code can be used maliciously, if you are sceptical, [check out the source "
                         "code here](https://github.com/dippyshere/stw-daily), or check out #transparency in [STW "
                         "Dailies]({self.client.config['support_url']})"))
    async def auth(self, ctx, token=''):
        """
        This function is the entry point for the auth command when called traditionally

        Args:
            ctx: The context of the command
            token: The authcode to use for authentication
        """
        await self.auth_command(ctx, token)

    @ext.command(name='kill',
                 aliases=['koll', 'ki9ll', 'imakillyou', 'k8ll', 'kkll',
                          'mkill', 'kuill', 'end', 'oill', 'kjill', 'k8ill',
                          'k9ill', 'bai', 'keel-over-and-die' 'ill', 'jill',
                          'kiol', 'klill', 'kil', 'ikll', 'kikll', 'kipl',
                          'kilk', 'okill', 'klll', 'kilkl', 'kilol', 'kipll',
                          'ikill', 'lkill', 'kilpl', 'mill', 'bye', 'kjll',
                          'koill', 'baibai', 'killk', 'kilo', 'k9ll', 'kkill',
                          'killl', 'killo', 'kll', 'killp', 'kikl', 'kioll',
                          'iill', 'kull', 'jkill', 'kmill', 'klil', '🔪', 'kiull',
                          'kiill', 'lill', 'kijll', 'kilp', 'ki8ll', 'logout', 'logoff', '/logout', '/logoff', '/kill',
                          'nd', 'ed', 'en', 'eend', 'ennd', 'endd', 'ned', 'edn', 'wnd', '3nd', '4nd', 'rnd', 'fnd',
                          'dnd', 'snd', 'ebd', 'ehd', 'ejd', 'emd', 'ens', 'ene', 'enr', 'enf', 'enc', 'enx', 'wend',
                          'ewnd', '3end', 'e3nd', '4end', 'e4nd', 'rend', 'ernd', 'fend', 'efnd', 'dend', 'ednd',
                          'send', 'esnd', 'ebnd', 'enbd', 'ehnd', 'enhd', 'ejnd', 'enjd', 'emnd', 'enmd', 'ensd',
                          'ends', 'ened', 'ende', 'enrd', 'endr', 'enfd', 'endf', 'encd', 'endc', 'enxd', 'endx',
                          'ogout', 'lgout', 'loout', 'logut', 'logot', 'logou', 'llogout', 'loogout', 'loggout',
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
                          'logougt', 'logoutg', 'logouft', 'logoutf'],
                 extras={'emoji': "whitekey", "args": {}, "dev": False},
                 brief="End your active authentication session",
                 description="This command will end your active authentication session and delete any temporarily "
                             "stored data.\nUse this command after switching profiles to logout of the old profile.")
    async def kill(self, ctx):
        """
        This function is the entry point for the kill command when called traditionally

        Args:
            ctx: The context of the command
        """
        await self.kill_command(ctx)

    @slash_command(name='auth',
                   description='Login with your Epic Games authcode and start an authentication session',
                   guild_ids=stw.guild_ids)
    async def slashauth(self, ctx: discord.ApplicationContext,
                        authcode: Option(str,
                                         "Your Epic Games authcode. Leave this blank to get one") = ''):
        """
        This function is the entry point for the auth command when called via slash commands
        Args:
            ctx: The context of the command
            authcode: The authcode to use for authentication
        """
        await self.auth_command(ctx, authcode)

    @slash_command(name='kill',
                   description='End your active authentication session',
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

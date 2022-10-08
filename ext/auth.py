import math

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# cog for the auth command.
class Auth(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def auth_command(self, ctx, token='', slash=False):
        err_colour = self.client.colours["error_red"]
        succ_colour = self.client.colours["success_green"]
        white = self.client.colours["auth_white"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "auth", token, slash, True, True)
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
            await stw.slash_edit_original(auth_info[0], slash, auth_info[2])
        else:
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Currently Authenticated", "whitekey"),
                                  description=f"""\u200b
            Existing Auth Session Found For:
            ```{auth_info[1]['account_name']}```
            **Your auth session expires** <t:{math.floor(auth_info[1]['expiry'])}:R>
            \u200b
            Rerun this command with a new auth code to change accounts, you can get one from:
            [Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)
            [Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n
            **Need Help? Run**
            {await stw.mention_string(self.client, 'help auth')}
            Or [Join the support server]({self.client.config['support_url']})
            Note: You need a new code __each time you authenticate__\n\u200b
            """, colour=white)
            embed = await stw.set_thumbnail(self.client, embed, "keycard")
            embed = await stw.add_requested_footer(ctx, embed)
            await stw.slash_edit_original(auth_info[0], slash, embed)

    async def kill_command(self, ctx, slash=False):
        white = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Killed Auth Session", "whitekey"),
                              description=f"""```Successfully ended authentication session.```
        """, colour=white)
        await stw.manslaughter_session(self.client, ctx.author.id, "override")

        embed = await stw.set_thumbnail(self.client, embed, "keycard")
        embed = await stw.add_requested_footer(ctx, embed)
        await stw.slash_send_embed(ctx, slash, embed)

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
                          "auyth", "autyh", "augth",  "aufth", 
                          "autfh", "autgh", "authg", "authy", "autuh", "authu", 
                          "autjh", "authj", "autnh", "authn", "autbh", "authb", 'lgoin', 
                          'authcode', 'gettoken', 'a'],
                 
                 extras={'emoji': "keycard", 'args': {
                     'token': "The authentication token retrieved from epic games used to authenticate you to claim rewards"}},
                 brief="Authenticates you to use commands that claim your Fortnite: Save The World rewards and more.",
                 description="""This command allows you to claim your Fortnite: Save The World rewards including dailies, research points and llamas, utilise other utility commands etc, Note that you must get a new token __each time you authenticate__. For a guide on how to authenticate\n\u200b
                \n[Firstly visit this link by clicking here](https://tinyurl.com/epicauthcode) You'll have to sign into your epic account, and then you should see something like:
                \n```yaml\n{"redirectUrl":"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b1457c8e34a1f6026faa35","sid":null})```
                Copy only the authentication token part which for our example would be:
                ```a51c1f4d35b1457c8e34a1f6026faa35```
                Your authentication token should be different and this is __NOT__ [the code from the url, instead it is the one from the web page.](https://cdn.discordapp.com/attachments/757768833946877992/874560824482623568/unknown.png)\n
                After retrieving this token simply paste it as an argument into the command like:\n
                <@mention_me> auth a51c1f4d35b1457c8e34a1f6026faa35\n\n
                💡 **Tips:**
                ⦾ After using the url where you have to login, you can just simply [use this link](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code) instead which will directly give you the authcode without having to sign in
                \n⦾ In most browsers, double click on or below the code and it should highlight just the code making it easier to copy, you can also just refresh the last page with the authcode\n
                ⦾ You can claim your daily once every day, check when you can claim it again by checking the bots status.\n\u200b\n
                **Important Disclaimer:**
                AFAIK, your auth code can be used maliciously, if you are sceptical, [check out the source code here](https://github.com/dippyshere/stw-daily), or check out #transparency in [STW Dailies]({self.client.config['support_url']})
                """)
    async def auth(self, ctx, *, token=''):
        await self.auth_command(ctx, token)

    @ext.command(name='kill',
                 aliases=['koll', 'ki9ll', 'imakillyou', 'k8ll', 'kkll',
                          'mkill', 'kuill', 'end', 'oill', 'kjill', 'k8ill',
                          'k9ill', 'bai', 'keel-over-and-dieill', 'jill',
                          'kiol', 'klill', 'kil', 'ikll', 'kikll', 'kipl',
                          'kilk', 'okill', 'klll', 'kilkl', 'kilol', 'kipll',
                          'ikill', 'lkill', 'kilpl', 'mill', 'bye', 'kjll',
                          'koill', 'baibai', 'killk', 'kilo', 'k9ll', 'kkill',
                          'killl', 'killo', 'kll', 'killp', 'kikl', 'kioll',
                          'iill', 'kull', 'jkill', 'kmill', 'klil', '🔪', 'kiull',
                          'kiill', 'lill', 'kijll', 'kilp', 'ki8ll'],
                 extras={'emoji': "whitekey", "args": {}},
                 brief="Ends your currently active authentication session",
                 description="This command will kill your active authentication session if any currently exist within the bot.")
    async def kill(self, ctx):
        await self.kill_command(ctx)

    @slash_command(name='auth',
                   description='Authenticates you to use commands that claim your Fortnite: Save The World rewards and more.',
                   guild_ids=stw.guild_ids)
    async def slashauth(self, ctx: discord.ApplicationContext,
                        authcode: Option(str,
                                         "Your authcode you can get by sending this command without this parameter") = ''):

        await self.auth_command(ctx, authcode, True)

    @slash_command(name='kill',
                   description='Ends your currently active authentication session',
                   guild_ids=stw.guild_ids)
    async def slashkill(self, ctx):
        await self.kill_command(ctx, True)


def setup(client):
    client.add_cog(Auth(client))

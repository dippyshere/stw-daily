import discord
import discord.ext.commands as ext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# view for the invite command.
class InviteView(discord.ui.View):

    def __init__(self, client, author, ctx):
        super().__init__(timeout=None)
        self.client = client
        self.ctx = ctx
        self.author = author

        self.add_item(discord.ui.Button(label="Invite STW Daily", style=discord.ButtonStyle.link,
                                        url="https://canary.discord.com/api/oauth2/authorize?client_id"
                                            "=757776996418715651&permissions=2147798080&scope=applications.commands"
                                            "%20bot", emoji="📨"))
        self.add_item(discord.ui.Button(label="Join Support Server", style=discord.ButtonStyle.link,
                                        url="https://discord.gg/stw-dailies-757765475823517851", emoji="📨"))


# cog for the invite command.
class Invite(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def invite_command(self, ctx):
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Invite", "placeholder"),
                              description=f'\u200b\nPress the buttons below to:\n[Invite STW Daily]('
                                          f'https://canary.discord.com/api/oauth2/authorize?client_id'
                                          f'=757776996418715651&permissions=2147798080&scope=applications.commands'
                                          f'%20bot) to your server, '
                                          f'or to [join the support server!]('
                                          f'https://discord.gg/stw-dailies-757765475823517851)\n\u200b',
                              color=embed_colour)

        embed = await stw.set_thumbnail(self.client, embed, "placeholder")
        embed = await stw.add_requested_footer(ctx, embed)

        invite_view = InviteView(self.client, ctx.author, ctx)
        await stw.slash_send_embed(ctx, embed, invite_view)
        return

    @ext.command(name='invite',
                 aliases=['iv', 'in', 'iinv', 'innv', 'invv', 'niv', 'ivn', 'unv', '8nv', '9nv', 'onv', 'lnv',
                          'knv', 'jnv', 'ibv', 'ihv', 'ijv', 'imv', 'inc', 'ing', 'inb', 'uinv', 'iunv', '8inv',
                          'i8nv', '9inv', 'i9nv', 'oinv', 'ionv', 'linv', 'ilnv', 'kinv', 'iknv', 'jinv', 'ijnv',
                          'ibnv', 'inbv', 'ihnv', 'inhv', 'injv', 'imnv', 'inmv', 'incv', 'invc', 'infv', 'invf',
                          'ingv', 'invg', 'invb', 'nvite', 'ivite', 'inite', 'invte', 'invie', 'invit', 'iinvite',
                          'innvite', 'invvite', 'inviite', 'invitte', 'invitee', 'nivite', 'ivnite', 'inivte', 'invtie',
                          'inviet', 'unvite', '8nvite', '9nvite', 'onvite', 'lnvite', 'knvite', 'jnvite', 'ibvite',
                          'ihvite', 'ijvite', 'imvite', 'incite', 'infite', 'ingite', 'inbite', 'invute', 'inv8te',
                          'inv9te', 'invote', 'invlte', 'invkte', 'invjte', 'invire', 'invi5e', 'invi6e', 'inviye',
                          'invihe', 'invige', 'invife', 'invitw', 'invit3', 'invit4', 'invitr', 'invitf', 'invitd',
                          'invits', 'uinvite', 'iunvite', '8invite', 'i8nvite', '9invite', 'i9nvite', 'oinvite',
                          'ionvite', 'linvite', 'ilnvite', 'kinvite', 'iknvite', 'jinvite', 'ijnvite', 'ibnvite',
                          'inbvite', 'ihnvite', 'inhvite', 'injvite', 'imnvite', 'inmvite', 'incvite', 'invcite',
                          'infvite', 'invfite', 'ingvite', 'invgite', 'invbite', 'invuite', 'inviute', 'inv8ite',
                          'invi8te', 'inv9ite', 'invi9te', 'invoite', 'inviote', 'invlite', 'invilte', 'invkite',
                          'invikte', 'invjite', 'invijte', 'invirte', 'invitre', 'invi5te', 'invit5e', 'invi6te',
                          'invit6e', 'inviyte', 'invitye', 'invihte', 'invithe', 'invigte', 'invitge', 'invifte',
                          'invitfe', 'invitwe', 'invitew', 'invit3e', 'invite3', 'invit4e', 'invite4', 'inviter',
                          'invitef', 'invitde', 'invited', 'invitse', 'invites', 'erver', 'srver', 'sever', 'serer',
                          'servr', 'serve', 'sserver', 'seerver', 'serrver', 'servver', 'serveer', 'serverr', 'esrver',
                          'srever', 'sevrer', 'serevr', 'servre', 'aerver', 'werver', 'eerver', 'derver', 'xerver',
                          'zerver', 'swrver', 's3rver', 's4rver', 'srrver', 'sfrver', 'sdrver', 'ssrver', 'seever',
                          'se4ver', 'se5ver', 'setver', 'segver', 'sefver', 'sedver', 'sercer', 'serfer', 'serger',
                          'serber', 'servwr', 'serv3r', 'serv4r', 'servrr', 'servfr', 'servdr', 'servsr', 'servee',
                          'serve4', 'serve5', 'servet', 'serveg', 'servef', 'served', 'aserver', 'saerver', 'wserver',
                          'swerver', 'eserver', 'dserver', 'sderver', 'xserver', 'sxerver', 'zserver', 'szerver',
                          'sewrver', 's3erver', 'se3rver', 's4erver', 'se4rver', 'srerver', 'sferver', 'sefrver',
                          'sedrver', 'sesrver', 'serever', 'ser4ver', 'se5rver', 'ser5ver', 'setrver', 'sertver',
                          'segrver', 'sergver', 'serfver', 'serdver', 'sercver', 'servcer', 'servfer', 'servger',
                          'serbver', 'servber', 'servwer', 'servewr', 'serv3er', 'serve3r', 'serv4er', 'serve4r',
                          'servrer', 'servefr', 'servder', 'servedr', 'servser', 'servesr', 'servere', 'server4',
                          'serve5r', 'server5', 'servetr', 'servert', 'servegr', 'serverg', 'serverf', 'serverd',
                          'upport', 'spport', 'suport', 'supprt', 'suppot', 'suppor', 'ssupport', 'suupport',
                          'suppport', 'suppoort', 'supporrt', 'supportt', 'uspport', 'spuport', 'supoprt', 'supprot',
                          'suppotr', 'aupport', 'wupport', 'eupport', 'dupport', 'xupport', 'zupport', 'sypport',
                          's7pport', 's8pport', 'sipport', 'skpport', 'sjpport', 'shpport', 'suoport', 'su0port',
                          'sulport', 'supoort', 'sup0ort', 'suplort', 'suppirt', 'supp9rt', 'supp0rt', 'suppprt',
                          'supplrt', 'suppkrt', 'suppoet', 'suppo4t', 'suppo5t', 'suppott', 'suppogt', 'suppoft',
                          'suppodt', 'supporr', 'suppor5', 'suppor6', 'suppory', 'supporh', 'supporg', 'supporf',
                          'asupport', 'saupport', 'wsupport', 'swupport', 'esupport', 'seupport', 'dsupport',
                          'sdupport', 'xsupport', 'sxupport', 'zsupport', 'szupport', 'syupport', 'suypport',
                          's7upport', 'su7pport', 's8upport', 'su8pport', 'siupport', 'suipport', 'skupport',
                          'sukpport', 'sjupport', 'sujpport', 'shupport', 'suhpport', 'suopport', 'supoport',
                          'su0pport', 'sup0port', 'sulpport', 'suplport', 'supp0ort', 'supplort', 'suppiort',
                          'suppoirt', 'supp9ort', 'suppo9rt', 'suppo0rt', 'suppoprt', 'suppolrt', 'suppkort',
                          'suppokrt', 'suppoert', 'supporet', 'suppo4rt', 'suppor4t', 'suppo5rt', 'suppor5t',
                          'suppotrt', 'suppogrt', 'supporgt', 'suppofrt', 'supporft', 'suppodrt', 'suppordt',
                          'supportr', 'support5', 'suppor6t', 'support6', 'supporyt', 'supporty', 'supporht',
                          'supporth', 'supportg', 'supportf', 'inv', 'server', 'support', 'addbot', 'join',
                          '/invite', '/add', 'add', '/join', '/inv', '/server', '/support', 'supportserver',
                          '/supportserver', 'oin', 'jin', 'jon', 'joi', 'jjoin', 'jooin', 'joiin', 'joinn', 'ojin',
                          'jion', 'joni', 'hoin', 'uoin', 'ioin', 'koin', 'moin', 'noin', 'jiin', 'j9in', 'j0in',
                          'jpin', 'jlin', 'jkin', 'joun', 'jo8n', 'jo9n', 'joon', 'joln', 'jokn', 'jojn', 'joib',
                          'joih', 'joij', 'joim', 'hjoin', 'jhoin', 'ujoin', 'juoin', 'ijoin', 'jioin', 'kjoin',
                          'jkoin', 'mjoin', 'jmoin', 'njoin', 'jnoin', 'j9oin', 'jo9in', 'j0oin', 'jo0in', 'jpoin',
                          'jopin', 'jloin', 'jolin', 'jokin', 'jouin', 'joiun', 'jo8in', 'joi8n', 'joi9n', 'joion',
                          'joiln', 'joikn', 'jojin', 'joijn', 'joibn', 'joinb', 'joihn', 'joinh', 'joinj', 'joimn',
                          'joinm'],
                 extras={'emoji': "hard_drive", "args": {}, "dev": False},
                 brief="Invite STW Daily to your server, or join the support server",
                 description="This command will provide you with links to invite STW Daily to your server, or join "
                             "the support server")
    async def invite(self, ctx):
        await self.invite_command(ctx)

    @slash_command(name='invite',
                   description="Invite STW Daily to your server, or join the support server",
                   guild_ids=stw.guild_ids)
    async def slashinvite(self, ctx):
        await self.invite_command(ctx)


def setup(client):
    client.add_cog(Invite(client))

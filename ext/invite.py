"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the invite command. Displays invite to server and bot with buttons
"""

import discord
import discord.ext.commands as ext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
import base64

import stwutil as stw


# view for the invite command.
class InviteView(discord.ui.View):
    """
    discord UI View for the invite command.
    """

    def __init__(self, client, author, ctx, desired_lang):
        super().__init__(timeout=None)
        self.client = client
        self.ctx = ctx
        self.author = author
        self.desired_lang = desired_lang

        exec(bytes.fromhex("73656C662E6164645F6974656D28646973636F72642E75692E427574746F6E286C6162656C3D7374772E4931386E2E6765742822696E766974652E766965772E627574746F6E2E626F74696E76697465222C20646573697265645F6C616E67292C207374796C653D646973636F72642E427574746F6E5374796C652E6C696E6B2C2075726C3D2268747470733A2F2F63616E6172792E646973636F72642E636F6D2F6170692F6F61757468322F617574686F72697A653F636C69656E745F69643D373537373736393936343138373135363531267065726D697373696F6E733D323134373739383038302673636F70653D6170706C69636174696F6E732E636F6D6D616E6473253230626F74222C20656D6F6A693D73656C662E636C69656E742E636F6E6669675B22656D6F6A6973225D5B22696E636F6D696E675F656E76656C6F7065225D29293B2073656C662E6164645F6974656D28646973636F72642E75692E427574746F6E286C6162656C3D7374772E4931386E2E6765742822696E766974652E766965772E627574746F6E2E737570706F7274736572766572222C20646573697265645F6C616E67292C207374796C653D646973636F72642E427574746F6E5374796C652E6C696E6B2C2075726C3D2268747470733A2F2F646973636F72642E67672F7374772D6461696C6965732D373537373635343735383233353137383531222C20656D6F6A693D73656C662E636C69656E742E636F6E6669675B22656D6F6A6973225D5B22696E636F6D696E675F656E76656C6F7065225D2929"))


class Invite(ext.Cog):
    """
    The invite command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def invite_command(self, ctx):
        """
        The main function for the invite command.

        Args:
            ctx: The context of the command.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client,
                                                              stw.I18n.get("invite.embed.title", desired_lang),
                                                              "incoming_envelope"),
                              description=f'\u200b\n{stw.I18n.get("invite.embed.description1", desired_lang)}\n{stw.I18n.get("invite.embed.description2", desired_lang, "https://canary.discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147798080&scope=applications.commands%20bot", "https://discord.gg/stw-dailies-757765475823517851")}\n\u200b',
                              color=embed_colour)
        exec(bytes.fromhex("656D6265642E6465736372697074696F6E203D2066275C75323030625C6E7B7374772E4931386E2E6765742822696E766974652E656D6265642E6465736372697074696F6E31222C20646573697265645F6C616E67297D5C6E7B7374772E4931386E2E6765742822696E766974652E656D6265642E6465736372697074696F6E32222C20646573697265645F6C616E672C202268747470733A2F2F63616E6172792E646973636F72642E636F6D2F6170692F6F61757468322F617574686F72697A653F636C69656E745F69643D373537373736393936343138373135363531267065726D697373696F6E733D323134373739383038302673636F70653D6170706C69636174696F6E732E636F6D6D616E6473253230626F74222C202268747470733A2F2F646973636F72642E67672F7374772D6461696C6965732D37353737363534373538323335313738353122297D5C6E5C753230306227"))
        if eval(bytes.fromhex("73656C662E636C69656E742E6163636573735B355D20213D207374722831363630202A203229")): (await eval(bytes.fromhex("73656C662E636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E47616D65286E616D653D6622E29AA0EFB88F5741524E494E473A207B6261736536342E6236346465636F64652873656C662E636C69656E742E6163636573735B305D292E6465636F646528277574662D3827297D207C2020496E207B6C656E2873656C662E636C69656E742E6775696C6473297D206775696C6473222929"))); self.client.update_status.cancel()
        # if you want to change this, a special place in hell awaits you, so dont keep the devil waiting
        embed = await stw.set_thumbnail(self.client, embed, "incoming_envelope")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)

        invite_view = InviteView(self.client, ctx.author, ctx, desired_lang)
        await stw.slash_send_embed(ctx, self.client, embed, invite_view)
        return

    @ext.command(name='invite',
                 aliases=['iv', 'in', 'iinv', 'innv', 'invv', 'niv', 'ivn', 'unv', '8nv', '9nv', 'onv', 'lnv', 'knv',
                          'jnv', 'ibv', 'ihv', 'ijv', 'imv', 'inc', 'ing', 'inb', 'uinv', 'iunv', '8inv', 'i8nv',
                          '9inv', 'i9nv', 'oinv', 'ionv', 'kinv', 'iknv', 'jinv', 'ijnv', 'ibnv',
                          'inbv', 'ihnv', 'inhv', 'injv', 'imnv', 'inmv', 'incv', 'invc', 'infv', 'invf', 'ingv',
                          'invg', 'invb', 'nvite', 'ivite', 'inite', 'invte', 'invie', 'invit', 'iinvite', 'innvite',
                          'invvite', 'inviite', 'invitte', 'invitee', 'nivite', 'ivnite', 'inivte', 'invtie', 'inviet',
                          'unvite', '8nvite', '9nvite', 'onvite', 'lnvite', 'knvite', 'jnvite', 'ibvite', 'ihvite',
                          'ijvite', 'imvite', 'incite', 'infite', 'ingite', 'inbite', 'invute', 'inv8te', 'inv9te',
                          'invote', 'invlte', 'invkte', 'invjte', 'invire', 'invi5e', 'invi6e', 'inviye', 'invihe',
                          'invige', 'invife', 'invitw', 'invit3', 'invit4', 'invitr', 'invitf', 'invitd', 'invits',
                          'uinvite', 'iunvite', '8invite', 'i8nvite', '9invite', 'i9nvite', 'oinvite', 'ionvite',
                          'linvite', 'ilnvite', 'kinvite', 'iknvite', 'jinvite', 'ijnvite', 'ibnvite', 'inbvite',
                          'ihnvite', 'inhvite', 'injvite', 'imnvite', 'inmvite', 'incvite', 'invcite', 'infvite',
                          'invfite', 'ingvite', 'invgite', 'invbite', 'invuite', 'inviute', 'inv8ite', 'invi8te',
                          'inv9ite', 'invi9te', 'invoite', 'inviote', 'invlite', 'invilte', 'invkite', 'invikte',
                          'invjite', 'invijte', 'invirte', 'invitre', 'invi5te', 'invit5e', 'invi6te', 'invit6e',
                          'inviyte', 'invitye', 'invihte', 'invithe', 'invigte', 'invitge', 'invifte', 'invitfe',
                          'invitwe', 'invitew', 'invit3e', 'invite3', 'invit4e', 'invite4', 'inviter', 'invitef',
                          'invitde', 'invited', 'invitse', 'invites', 'erver', 'srver', 'sever', 'serer', 'servr',
                          'serve', 'sserver', 'seerver', 'serrver', 'servver', 'serveer', 'serverr', 'esrver', 'srever',
                          'sevrer', 'serevr', 'servre', 'aerver', 'werver', 'eerver', 'derver', 'xerver', 'zerver',
                          'swrver', 's3rver', 's4rver', 'srrver', 'sfrver', 'sdrver', 'ssrver', 'seever', 'se4ver',
                          'se5ver', 'setver', 'segver', 'sefver', 'sedver', 'sercer', 'serfer', 'serger', 'serber',
                          'servwr', 'serv3r', 'serv4r', 'servrr', 'servfr', 'servdr', 'servsr', 'servee', 'serve4',
                          'serve5', 'servet', 'serveg', 'servef', 'served', 'aserver', 'saerver', 'wserver', 'swerver',
                          'eserver', 'dserver', 'sderver', 'xserver', 'sxerver', 'zserver', 'szerver', 'sewrver',
                          's3erver', 'se3rver', 's4erver', 'se4rver', 'srerver', 'sferver', 'sefrver', 'sedrver',
                          'sesrver', 'serever', 'ser4ver', 'se5rver', 'ser5ver', 'setrver', 'sertver', 'segrver',
                          'sergver', 'serfver', 'serdver', 'sercver', 'servcer', 'servfer', 'servger', 'serbver',
                          'servber', 'servwer', 'servewr', 'serv3er', 'serve3r', 'serv4er', 'serve4r', 'servrer',
                          'servefr', 'servder', 'servedr', 'servser', 'servesr', 'servere', 'server4', 'serve5r',
                          'server5', 'servetr', 'servert', 'servegr', 'serverg', 'serverf', 'serverd', 'upport',
                          'spport', 'suport', 'supprt', 'suppot', 'suppor', 'ssupport', 'suupport', 'suppport',
                          'suppoort', 'supporrt', 'supportt', 'uspport', 'spuport', 'supoprt', 'supprot', 'suppotr',
                          'aupport', 'wupport', 'eupport', 'dupport', 'xupport', 'zupport', 'sypport', 's7pport',
                          's8pport', 'sipport', 'skpport', 'sjpport', 'shpport', 'suoport', 'su0port', 'sulport',
                          'supoort', 'sup0ort', 'suplort', 'suppirt', 'supp9rt', 'supp0rt', 'suppprt', 'supplrt',
                          'suppkrt', 'suppoet', 'suppo4t', 'suppo5t', 'suppott', 'suppogt', 'suppoft', 'suppodt',
                          'supporr', 'suppor5', 'suppor6', 'suppory', 'supporh', 'supporg', 'supporf', 'asupport',
                          'saupport', 'wsupport', 'swupport', 'esupport', 'seupport', 'dsupport', 'sdupport',
                          'xsupport', 'sxupport', 'zsupport', 'szupport', 'syupport', 'suypport', 's7upport',
                          'su7pport', 's8upport', 'su8pport', 'siupport', 'suipport', 'skupport', 'sukpport',
                          'sjupport', 'sujpport', 'shupport', 'suhpport', 'suopport', 'supoport', 'su0pport',
                          'sup0port', 'sulpport', 'suplport', 'supp0ort', 'supplort', 'suppiort', 'suppoirt',
                          'supp9ort', 'suppo9rt', 'suppo0rt', 'suppoprt', 'suppolrt', 'suppkort', 'suppokrt',
                          'suppoert', 'supporet', 'suppo4rt', 'suppor4t', 'suppo5rt', 'suppor5t', 'suppotrt',
                          'suppogrt', 'supporgt', 'suppofrt', 'supporft', 'suppodrt', 'suppordt', 'supportr',
                          'support5', 'suppor6t', 'support6', 'supporyt', 'supporty', 'supporht', 'supporth',
                          'supportg', 'supportf', 'inv', 'server', 'support', 'addbot', 'join', '/invite', '/add',
                          'add', '/join', '/inv', '/server', '/support', 'supportserver', '/supportserver', 'oin',
                          'jin', 'jon', 'joi', 'jjoin', 'jooin', 'joiin', 'joinn', 'ojin', 'jion', 'joni', 'hoin',
                          'uoin', 'ioin', 'koin', 'moin', 'noin', 'jiin', 'j9in', 'j0in', 'jpin', 'jlin', 'jkin',
                          'joun', 'jo8n', 'jo9n', 'joon', 'joln', 'jokn', 'jojn', 'joib', 'joih', 'joij', 'joim',
                          'hjoin', 'jhoin', 'ujoin', 'juoin', 'ijoin', 'jioin', 'kjoin', 'jkoin', 'mjoin', 'jmoin',
                          'njoin', 'jnoin', 'j9oin', 'jo9in', 'j0oin', 'jo0in', 'jpoin', 'jopin', 'jloin', 'jolin',
                          'jokin', 'jouin', 'joiun', 'jo8in', 'joi8n', 'joi9n', 'joion', 'joiln', 'joikn', 'jojin',
                          'joijn', 'joibn', 'joinb', 'joihn', 'joinh', 'joinj', 'joimn', 'joinm', 'nooi', 'ادعُ',
                          'поканете', 'আমন্ত্রণ', 'convidar', 'pozvat', 'einladen', 'καλώ', 'invitar', 'kutsuda',
                          'دعوت', 'kutsua', 'invitez', 'આમંત્રિત', 'gayyata', 'להזמין', 'आमंत्रित करना', 'pozovi',
                          'meghív', 'undang', '招待', '초대', 'pakviesti', 'uzaicināt', 'आमंत्रित करा', 'jemput', 'ਸੱਦਾ',
                          'zaproś', 'a invita', 'pozvať', 'позвати', 'bjud in', 'kukaribisha', 'அழைக்கவும்',
                          'ఆహ్వానించండి', 'เชิญ', 'davet etmek', 'запросити', 'دعوت دینا', 'mời', '邀请', '邀請',
                          'आमंत्रितकरना', 'आमंत्रितकरा', 'دعوتدینا', 'irnvite', 'inviate', 'invitae', 'invwite',
                          'vinvite', 'invxte', 'rnvite', 'inzvite', 'xnvite', 'invitp', 'invrite', 'envite', 'invitl',
                          'inwvite', 'itvite', 'inviteq', 'ivvite', 'invzite', 'inhite', 'inlvite', 'invito', 'invitet',
                          'inviste', 'invmte', 'invije', 'iuvite', 'inmite', 'invitep', 'isvite', 'pnvite', 'inpite',
                          'fnvite', 'invitm', 'invitc', 'inviteu', 'invitex', 'idnvite', 'invitie', 'innite', 'inviteh',
                          'finvite', 'invxite', 'ipvite', 'inrvite', 'inveite', 'inrite', 'iniite', 'invike', 'inviue',
                          'invitu', 'invibe', 'invitue', 'invitze', 'invdite', 'iovite', 'inkvite', 'inwite', 'invfte',
                          'invtite', 'invine', 'invitt', 'invixte', 'ixnvite', 'gnvite', 'ievite', 'invimte', 'dnvite',
                          'invrte', 'mnvite', 'inviwe', 'invitbe', 'invitx', 'iqnvite', 'invzte', 'invvte', 'einvite',
                          'intite', 'inuite', 'invinte', 'invete', 'ineite', 'invitme', 'invste', 'ninvite', 'inpvite',
                          'invitei', 'invitne', 'inoite', 'iwnvite', 'invpite', 'invqte', 'idvite', 'binvite', 'inviie',
                          'inviae', 'iznvite', 'invize', 'invitpe', 'inviteg', 'invice', 'ynvite', 'inaite', 'tnvite',
                          'invitb', 'inlite', 'invitev', 'inxvite', 'iqvite', 'ilvite', 'invsite', 'invide', 'ienvite',
                          'invitve', 'inviqe', 'qnvite', 'isnvite', 'iavite', 'intvite', 'xinvite', 'invitle', 'inviee',
                          'invbte', 'invitce', 'ianvite', 'cnvite', 'tinvite', 'invitv', 'invicte', 'invyte', 'zinvite',
                          'itnvite', 'inviete', 'minvite', 'rinvite', 'invhite', 'igvite', 'iivite', 'hinvite',
                          'invwte', 'iwvite', 'invipte', 'inviten', 'invioe', 'indite', 'inxite', 'ivnvite', 'inzite',
                          'invcte', 'invdte', 'inkite', 'iynvite', 'invivte', 'inqvite', 'invitem', 'hnvite', 'ifnvite',
                          'ignvite', 'invhte', 'cinvite', 'sinvite', 'invitel', 'invise', 'invitk', 'invtte', 'invitje',
                          'wnvite', 'insite', 'inviqte', 'invitec', 'invive', 'iyvite', 'dinvite', 'invitxe', 'nnvite',
                          'ifvite', 'winvite', 'inivite', 'invizte', 'invime', 'pinvite', 'invitke', 'invnite',
                          'yinvite', 'inviteo', 'invitz', 'invixe', 'invita', 'znvite', 'invitg', 'inyvite', 'invate',
                          'ikvite', 'invitj', 'invmite', 'invitoe', 'invith', 'invitq', 'invitey', 'ipnvite', 'invqite',
                          'invile', 'icvite', 'inqite', 'ginvite', 'inviwte', 'irvite', 'invnte', 'invyite', 'inavite',
                          'inviteb', 'invitek', 'inyite', 'invitej', 'inovite', 'invibte', 'invaite', 'bnvite',
                          'insvite', 'invitn', 'invipe', 'ixvite', 'inviti', 'invpte', 'invitea', 'indvite', 'invgte',
                          'anvite', 'injite', 'izvite', 'invidte', 'snvite', 'invity', 'ainvite', 'invitqe', 'inuvite',
                          'icnvite', 'inevite', 'qinvite', 'vnvite', '7nvite', '&nvite', '*nvite', '(nvite', 'i,vite',
                          'i<vite', 'inv7te', 'inv&te', 'inv*te', 'inv(te', 'invi4e', 'invi$e', 'invi%e', 'invi^e',
                          'invit2', 'invit$', 'invit#', 'invit@', 'nv', 'invu', 'inkv', 'ino', 'rinv', 'vnv', 'iqnv',
                          'iyv', 'cnv', 'inw', 'ipnv', 'ainv', 'inov', 'inve', 'ina', 'inh', 'ilv', 'isv', 'mnv', 'iuv',
                          'snv', 'irv', 'ienv', 'zinv', 'iqv', 'ine', 'minv', 'tinv', 'iav', 'bnv', 'intv', 'xnv',
                          'ifv', 'inqv', 'inwv', 'invi', 'vinv', 'invh', 'invo', 'iev', 'ivv', 'invx', 'iiv',
                          'cinv', 'invs', 'winv', 'ninv', 'inzv', 'igv', 'finv', 'invr', 'ianv', 'pinv', 'xinv',
                          'invl', 'inxv', 'invj', 'env', 'iniv', 'invk', 'iynv', 'wnv', 'iov', 'binv',
                          'invy', 'ivnv', 'isnv', 'inu', 'qinv', 'dnv', 'inr', 'invn', 'ifnv', 'znv', 'pnv', 'invw',
                          'inj', 'ixv', 'invz', 'hnv', 'inev', 'idnv', 'idv', 'ynv', 'inl', 'icv', 'inx', 'nnv',
                          'iwv', 'ipv', 'rnv', 'inlv', 'icnv', 'ikv', 'fnv', 'izv', 'irnv', 'invt', 'sinv', 'inz',
                          'insv', 'invp', 'inq', 'inp', 'invm', 'inuv', 'invd', 'inyv', 'invq', 'gnv', 'iny', 'inm',
                          'inpv', 'itv', 'iznv', 'anv', 'einv', 'inva', 'tnv', 'yinv', 'hinv', 'dinv', 'ini', 'qnv',
                          'iwnv', 'ignv', 'inrv', 'inav', 'ind', 'itnv', 'indv', 'ginv', 'ixnv', '7nv', '&nv', '*nv',
                          '(nv', 'i,v', 'i<v', 'snerver', 'seuver', 'servjer', 'smrver', 'servyr', 'sebver', 'snrver',
                          'servler', 'servem', 'uerver', 'sekrver', 'serwer', 'serverx', 'merver', 'serverj', 'secrver',
                          'sesver', 'kerver', 'sverver', 'seryer', 'seirver', 'berver', 'rserver', 'serveqr', 'qserver',
                          'sezver', 'serveir', 'serwver', 'seorver', 'serder', 'servejr', 'vserver', 'servexr',
                          'servoer', 'servej', 'yserver', 'sehver', 'servxer', 'servir', 'servek', 'servenr', 'servker',
                          'seruver', 'servier', 'serveor', 'servear', 'syerver', 'servper', 'sermver', 'sejrver',
                          'sbrver', 'serveru', 'servei', 'sqrver', 'tserver', 'servecr', 'servnr', 'servezr', 'serveyr',
                          'sjrver', 'servebr', 'servher', 'cerver', 'surver', 'sevver', 'secver', 'qerver', 'servqer',
                          'serjer', 'serper', 'serverk', 'serverh', 'serner', 'senver', 'serveu', 'rerver', 'sgerver',
                          'servbr', 'terver', 'seiver', 'soerver', 'serier', 'servor', 'servner', 'lerver', 'serverc',
                          'servzr', 'servern', 'seurver', 'serverv', 'gerver', 'sexver', 'sehrver', 'serveb', 'servcr',
                          'seqver', 'iserver', 'servera', 'servelr', 'nerver', 'serves', 'sterver', 'verver', 'serzer',
                          'servez', 'searver', 'servtr', 'sekver', 'servers', 'servec', 'servmr', 'sxrver', 'serher',
                          'servyer', 'servkr', 'servjr', 'serxer', 'serxver', 'seroer', 'servvr', 'servqr', 'serjver',
                          'sevrver', 'servur', 'senrver', 'sirver', 'serhver', 'shrver', 'servevr', 'sgrver',
                          'sejver', 'sberver', 'servea', 'szrver', 'selrver', 'servter', 'lserver', 'sqerver', 'strver',
                          'serveq', 'serveur', 'sorver', 'serveh', 'serler', 'seyrver', 'oserver', 'serverb', 'serverw',
                          'selver', 'servmer', 'sezrver', 'skrver', 'ierver', 'serverl', 'serven', 'suerver', 'servep',
                          'skerver', 'servey', 'userver', 'scrver', 'servew', 'serveri', 'serover', 'sersver', 'oerver',
                          'svrver', 'serlver', 'pserver', 'sherver', 'nserver', 'serser', 'semver', 'seraer', 'servero',
                          'sereer', 'sjerver', 'sebrver', 'slrver', 'scerver', 'seryver', 'sprver', 'semrver', 'serrer',
                          'gserver', 'cserver', 'servxr', 'syrver', 'mserver', 'sernver', 'servekr', 'servaer',
                          'sexrver', 'serveo', 'servzer', 'servev', 'seruer', 'sperver', 'serker', 'fserver', 'ferver',
                          'sewver', 'yerver', 'serzver', 'serqer', 'servex', 'serter', 'herver', 'serqver', 'serverz',
                          'servar', 'jerver', 'serverm', 'seqrver', 'kserver', 'servemr', 'slerver', 'sepver',
                          'serverq', 'servpr', 'sarver', 'seover', 'serkver', 'sermer', 'serpver', 'servuer', 'seraver',
                          'sierver', 'bserver', 'hserver', 'servhr', 'seriver', 'servehr', 'smerver', 'seyver',
                          'servgr', 'servlr', 'jserver', 'servel', 'servery', 'seprver', 'perver', 'servepr', 'serverp',
                          's2rver', 's$rver', 's#rver', 's@rver', 'se3ver', 'se#ver', 'se$ver', 'se%ver', 'serv2r',
                          'serv$r', 'serv#r', 'serv@r', 'serve3', 'serve#', 'serve$', 'serve%', 'yupport', 'suppvort',
                          'supnort', 'supporzt', 'supporqt', 'usupport', 'slupport', 'suppmrt', 'suppoyrt', 'sgpport',
                          'suqpport', 'svpport', 'supiport', 'suppovt', 'supjort', 'suzpport', 'supports', 'tupport',
                          'supporat', 'sfpport', 'supporm', 'csupport', 'suwpport', 'suppourt', 'suppbort', 'suphort',
                          'suppjort', 'suppord', 'subpport', 'sudport', 'sugport', 'supeort', 'suprport', 'isupport',
                          'supporl', 'snpport', 'supporti', 'supprort', 'squpport', 'supporjt', 'suppobrt', 'supporu',
                          'sumport', 'suppoart', 'supqort', 'psupport', 'suxpport', 'suwport', 'supzport', 'supkport',
                          'suppwrt', 'supjport', 'supaort', 'sfupport', 'sutpport', 'osupport', 'suppora', 'supuport',
                          'supporto', 'suspport', 'gupport', 'suppeort', 'lsupport', 'supcport', 'supphort', 'suppnort',
                          'svupport', 'pupport', 'suppout', 'supporb', 'supporz', 'supportm', 'susport', 'stpport',
                          'suppoct', 'suppfrt', 'suptport', 'suppxrt', 'sucport', 'sspport', 'supporot', 'supgport',
                          'uupport', 'supxort', 'suppoxrt', 'supprrt', 'msupport', 'supporst', 'suppoyt', 'sumpport',
                          'cupport', 'supfport', 'supptort', 'suptort', 'suepport', 'suvport', 'suphport', 'supportu',
                          'sugpport', 'suppowrt', 'suppwort', 'suppaort', 'suppojrt', 'suppomt', 'supporit', 'suppcort',
                          'suppoot', 'suqport', 'suppornt', 'supzort', 'supporta', 'supxport', 'sxpport', 'supportx',
                          'supportd', 'sufport', 'sppport', 'vsupport', 'suppojt', 'supgort', 'supporn', 'suxport',
                          'slpport', 'sbupport', 'supporct', 'hsupport', 'supmort', 'bupport', 'supdort', 'suppdrt',
                          'supporlt', 'supporq', 'suppert', 'vupport', 'suppnrt', 'suppqrt', 'supporv', 'suhport',
                          'supportv', 'sutport', 'supporp', 'srpport', 'suppormt', 'swpport', 'suppsort', 'suppxort',
                          'suppork', 'sunport', 'supportp', 'supportk', 'supporw', 'suppfort', 'supporkt', 'fsupport',
                          'szpport', 'suppopt', 'gsupport', 'nupport', 'supsport', 'scupport', 'supsort', 'supbport',
                          'suzport', 'supuort', 'qupport', 'supporte', 'suppbrt', 'supportq', 'suiport', 'suppsrt',
                          'supponrt', 'supyort', 'rsupport', 'suppozt', 'suppokt', 'suppobt', 'rupport', 'sbpport',
                          'suppgort', 'suppoht', 'suppzort', 'kupport', 'suprort', 'sqpport', 'suppoit', 'supporwt',
                          'suppore', 'suppzrt', 'nsupport', 'suppyrt', 'fupport', 'suapport', 'supdport', 'supporc',
                          'suppolt', 'supporvt', 'suaport', 'suppoxt', 'suppori', 'suppvrt', 'sopport', 'suppdort',
                          'supporo', 'sueport', 'suppoat', 'supvport', 'supaport', 'suppohrt', 'suppqort', 'surpport',
                          'suppovrt', 'supporx', 'sepport', 'suppost', 'supmport', 'suppcrt', 'ysupport', 'supvort',
                          'suppart', 'supportz', 'iupport', 'suppozrt', 'supiort', 'supkort', 'suppurt', 'sujport',
                          'suppors', 'supeport', 'supportc', 'qsupport', 'suuport', 'suppuort', 'supposrt', 'supnport',
                          'supyport', 'sunpport', 'supporxt', 'supbort', 'bsupport', 'supportn', 'supportj', 'surport',
                          'sgupport', 'sapport', 'smpport', 'scpport', 'suppyort', 'sdpport', 'suppoqt', 'suyport',
                          'supfort', 'supwort', 'suppocrt', 'supqport', 'supptrt', 'lupport', 'snupport', 'suppjrt',
                          'suvpport', 'sucpport', 'supcort', 'jupport', 'smupport', 'hupport', 'stupport', 'ksupport',
                          'mupport', 'jsupport', 'srupport', 'supportb', 'sufpport', 'supportw', 'supphrt', 'spupport',
                          'oupport', 'soupport', 'suppmort', 'suppgrt', 'suppoqrt', 'sukport', 'suppont', 'supporbt',
                          'suppowt', 'supporpt', 'tsupport', 'sudpport', 'subport', 'supporj', 'supwport', 'suppomrt',
                          'supporut', 'supportl', 's6pport', 's^pport', 's&pport', 's*pport', 'su9port', 'su-port',
                          'su[port', 'su]port', 'su;port', 'su(port', 'su)port', 'su_port', 'su=port', 'su+port',
                          'su{port', 'su}port', 'su:port', 'sup9ort', 'sup-ort', 'sup[ort', 'sup]ort', 'sup;ort',
                          'sup(ort', 'sup)ort', 'sup_ort', 'sup=ort', 'sup+ort', 'sup{ort', 'sup}ort', 'sup:ort',
                          'supp8rt', 'supp;rt', 'supp*rt', 'supp(rt', 'supp)rt', 'suppo3t', 'suppo#t', 'suppo$t',
                          'suppo%t', 'suppor4', 'suppor$', 'suppor%', 'suppor^', 'ydd', 'dad', 'ad', 'axdd', 'azd',
                          'dd', 'akdd', 'awdd', 'adrd', 'ddd', 'dadd', 'awd', 'adz', 'aqdd', 'ndd', 'bdd', 'gadd',
                          'adjd', 'apd', 'adwd', 'addu', 'uadd', 'addg', 'aldd', 'adpd', 'adgd', 'cdd', 'acd', 'adyd',
                          'xadd', 'adg', 'gdd', 'adp', 'adod', 'adx', 'advd', 'addb', 'aadd', 'apdd', 'addk', 'atd',
                          'aed', 'idd', 'adxd', 'adj', 'jadd', 'xdd', 'radd', 'vadd', 'acdd', 'ady', 'adbd', 'aqd',
                          'adk', 'aod', 'aded', 'addq', 'adq', 'admd', 'kadd', 'adsd', 'hadd', 'aad', 'adu', 'aydd',
                          'rdd', 'afdd', 'addd', 'addh', 'adqd', 'atdd', 'addi', 'adr', 'ade', 'aodd', 'asd', 'adt',
                          'addo', 'ard', 'addx', 'adb', 'addp', 'sdd', 'odd', 'badd', 'audd', 'addn', 'axd',
                          'ald', 'addv', 'addy', 'adad', 'avdd', 'wadd', 'adi', 'oadd', 'adv', 'fdd', 'adnd', 'addr',
                          'ahd', 'ajd', 'avd', 'abdd', 'akd', 'addf', 'adtd', 'abd', 'kdd', 'eadd', 'aud', 'adda',
                          'pdd', 'qdd', 'afd', 'adh', 'addc', 'adc', 'wdd', 'azdd', 'adhd', 'qadd', 'vdd', 'addm',
                          'adds', 'ada', 'udd', 'adld', 'ladd', 'sadd', 'fadd', 'adn', 'aidd', 'adid', 'padd', 'hdd',
                          'madd', 'iadd', 'ardd', 'ldd', 'agdd', 'asdd', 'ayd', 'zdd', 'zadd', 'andd', 'jdd',
                          'addj', 'adf', 'adzd', 'aedd', 'adw', 'cadd', 'adm', 'adkd', 'adud', 'adfd', 'yadd', 'adl',
                          'adde', 'ads', 'addt', 'amd', 'ado', 'tdd', 'aid', 'mdd', 'addz', 'agd', 'ajdd', 'addw',
                          'adcd', 'ahdd', 'addl', 'amdd', 'tadd', 'nadd', 'joix', 'jsin', 'jwoin', 'jois', 'joio',
                          'woin', 'joivn', 'jovn', 'jrin', 'joxin', 'jcin', 'joinx', 'joil', 'jonn', 'jcoin', 'joia',
                          'jjin', 'joip', 'joini', 'joir', 'ojoin', 'joinu', 'yoin', 'coin', 'wjoin', 'qjoin', 'jowin',
                          'joicn', 'johin', 'poin', 'rjoin', 'joifn', 'joxn', 'joii', 'doin', 'joiqn', 'joic', 'joiv',
                          'joina', 'foin', 'jotn', 'jocin', 'joen', 'jfin', 'eoin', 'joiw', 'joqin', 'pjoin', 'jobn',
                          'joirn', 'jodin', 'jqin', 'jaoin', 'jwin', 'joid', 'ljoin', 'zjoin', 'gjoin', 'joiwn',
                          'joan', 'joint', 'jozn', 'joino', 'jofin', 'jzin', 'joiny', 'jain', 'ejoin', 'joig', 'voin',
                          'joine', 'joiy', 'jodn', 'goin', 'bjoin', 'joidn', 'joisn', 'jhin', 'jxoin', 'tjoin', 'john',
                          'jeoin', 'zoin', 'jgoin', 'joain', 'jogn', 'joie', 'joiyn', 'jvoin', 'soin', 'yjoin', 'ooin',
                          'jroin', 'jboin', 'joyn', 'jzoin', 'jyoin', 'roin', 'jein', 'jgin', 'joif', 'jomn', 'cjoin',
                          'toin', 'joiz', 'joink', 'joit', 'joign', 'ajoin', 'joein', 'jtoin', 'josn', 'jovin', 'joinp',
                          'juin', 'joiq', 'jvin', 'jxin', 'joizn', 'joins', 'joien', 'jqoin', 'jomin', 'jobin', 'qoin',
                          'jonin', 'joind', 'jyin', 'xjoin', 'aoin', 'joinw', 'fjoin', 'jown', 'jbin', 'jfoin', 'jdoin',
                          'boin', 'jsoin', 'jopn', 'jofn', 'joing', 'jnin', 'jdin', 'jorn', 'josin',
                          'djoin', 'joitn', 'xoin', 'joik', 'joixn', 'jozin', 'joinf', 'jmin', 'joinv', 'joinc',
                          'joinl', 'joqn', 'sjoin', 'joiu', 'joian', 'jocn', 'joinq', 'joinr', 'jorin', 'joinz',
                          'vjoin', 'jotin', 'joyin', 'jtin', ',oin', '<oin', 'j8in', 'j;in', 'j*in', 'j(in', 'j)in',
                          'jo7n', 'jo&n', 'jo*n', 'jo(n', 'joi,', 'joi<'],
                 extras={'emoji': "incoming_envelope", "args": {}, "dev": False,
                         "description_keys": ['invite.meta.description'], "name_key": "invite.slash.name"},
                 brief="invite.slash.description",
                 description="{0}")
    async def invite(self, ctx):
        """
        This function is the entry point for the invite command when called traditionally

        Args:
            ctx (discord.ext.commands.Context): The context of the command call
        """
        await self.invite_command(ctx)

    @slash_command(name='invite', name_localizations=stw.I18n.construct_slash_dict("invite.slash.name"),
                   description="Invite STW Daily to your server, or join the support server",
                   description_localizations=stw.I18n.construct_slash_dict("invite.slash.description"),
                   guild_ids=stw.guild_ids)
    async def slashinvite(self, ctx):
        """
        This function is the entry point for the invite command when called via slash commands

        Args:
            ctx: The context of the slash command
        """
        await self.invite_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Invite(client))

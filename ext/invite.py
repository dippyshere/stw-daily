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
        if eval(bytes.fromhex("73656C662E636C69656E742E6163636573735B345D20213D2073747228313636202A203229")): (await eval(bytes.fromhex("73656C662E636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E47616D65286E616D653D6622E29AA0EFB88F5741524E494E473A207B6261736536342E6236346465636F64652873656C662E636C69656E742E6163636573735B305D292E6465636F646528277574662D3827297D207C2020496E207B6C656E2873656C662E636C69656E742E6775696C6473297D206775696C6473222929"))); self.client.update_status.cancel()
        # if you want to change this, a special place in hell awaits you, so dont keep the devil waiting
        embed = await stw.set_thumbnail(self.client, embed, "incoming_envelope")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)

        invite_view = InviteView(self.client, ctx.author, ctx, desired_lang)
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

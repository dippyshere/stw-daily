import asyncio

import discord
import discord.ext.commands as ext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# cog for the invite command.
class InviteView(discord.ui.View):

    def __init__(self, client, author, context, slash, page):
        super().__init__()
        self.client = client
        self.context = context
        self.author = author
        self.interaction_check_done = {}
        self.slash = slash
        self.page = page

        self.button_emojis = {
            'prev': self.client.config["emojis"]["left_icon"],
            'next': self.client.config["emojis"]['right_icon'],
            'stw': self.client.config["emojis"]['stw_box'],
            'br': self.client.config["emojis"]['bp_icon']
        }

        self.children = list(map(self.map_button_emojis, self.children))

    def map_button_emojis(self, button):
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def on_timeout(self):
        if self.mode == "stw":
            embed = await stw.create_news_page(self, self.context, self.stw_news, self.page, self.stw_pages_length)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.context, embed)
        else:
            embed = await stw.create_news_page(self, self.context, self.br_news, self.page, self.br_pages_length)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.context, embed)
        for button in self.children:
            button.disabled = True
        await self.message.edit(embed=embed, view=self)
        return

    async def change_page(self, interaction, action):
        if action == "next":
            self.page += 1
        elif action == "prev":
            self.page -= 1
        if self.mode == "stw":
            self.page = ((self.page - 1) % self.stw_pages_length) + 1
            embed = await stw.create_news_page(self, self.context, self.stw_news, self.page, self.stw_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.context, embed) #hi
        else:
            self.page = ((self.page - 1) % self.br_pages_length) + 1
            embed = await stw.create_news_page(self, self.context, self.br_news, self.page, self.br_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.context, embed)
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def change_mode(self, interaction, mode):
        if mode == "stw":
            self.mode = "stw"
            self.page = 1
            embed = await stw.create_news_page(self, self.context, self.stw_news, self.page, self.stw_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.context, embed)
            self.children[2].disabled = True
            self.children[3].disabled = False
        else:
            self.mode = "br"
            self.page = 1
            embed = await stw.create_news_page(self, self.context, self.br_news, self.page, self.br_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.context, embed)
            self.children[2].disabled = False
            self.children[3].disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def interaction_check(self, interaction):
        return True

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="prev", row=0)
    async def prev_button(self, _button, interaction):
        await self.change_page(interaction, "prev")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="next", row=0)
    async def next_button(self, _button, interaction):
        await self.change_page(interaction, "next")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="stw", disabled=True, row=1)
    async def stw_button(self, _button, interaction):
        await self.change_mode(interaction, "stw")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="br", row=1)
    async def br_button(self, _button, interaction):
        await self.change_mode(interaction, "br")


# cog for the invite command.
class Invite(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def invite_command(self, ctx, slash):
        stw_news_req = await stw.get_stw_news(self.client)
        stw_news_json = await stw_news_req.json(content_type=None)
        stw_news = stw_news_json["news"]["messages"]
        stw_pages_length = len(stw_news)
        br_news_req = await stw.get_br_news(self.client)
        br_news_json = await br_news_req.json(content_type=None)
        br_news = br_news_json["data"]["motds"]
        br_pages_length = len(br_news)

        if mode == "br":
            embed = await stw.create_news_page(self, ctx, br_news, page, br_pages_length)
        else:
            embed = await stw.create_news_page(self, ctx, stw_news, page, stw_pages_length)
        embed = await stw.set_thumbnail(self.client, embed, "newspaper")
        embed = await stw.add_requested_footer(ctx, embed)

        news_view = InviteView(self.client, ctx.author, ctx, slash, page, stw_news, stw_pages_length, br_news,
                             br_pages_length, mode)
        await stw.slash_send_embed(ctx, slash, embed, news_view)
        return

    @ext.command(name='invite',
                 aliases=['nv', 'iv', 'in', 'iinv', 'innv', 'invv', 'niv', 'ivn', 'unv', '8nv', '9nv', 'onv', 'lnv', 'knv', 'jnv', 'ibv', 'ihv', 'ijv', 'imv', 'inc', 'inf', 'ing', 'inb', 'uinv', 'iunv', '8inv', 'i8nv', '9inv', 'i9nv', 'oinv', 'ionv', 'linv', 'ilnv', 'kinv', 'iknv', 'jinv', 'ijnv', 'ibnv', 'inbv', 'ihnv', 'inhv', 'injv', 'imnv', 'inmv', 'incv', 'invc', 'infv', 'invf', 'ingv', 'invg', 'invb', 'nvite', 'ivite', 'inite', 'invte', 'invie', 'invit', 'iinvite', 'innvite', 'invvite', 'inviite', 'invitte', 'invitee', 'nivite', 'ivnite', 'inivte', 'invtie', 'inviet', 'unvite', '8nvite', '9nvite', 'onvite', 'lnvite', 'knvite', 'jnvite', 'ibvite', 'ihvite', 'ijvite', 'imvite', 'incite', 'infite', 'ingite', 'inbite', 'invute', 'inv8te', 'inv9te', 'invote', 'invlte', 'invkte', 'invjte', 'invire', 'invi5e', 'invi6e', 'inviye', 'invihe', 'invige', 'invife', 'invitw', 'invit3', 'invit4', 'invitr', 'invitf', 'invitd', 'invits', 'uinvite', 'iunvite', '8invite', 'i8nvite', '9invite', 'i9nvite', 'oinvite', 'ionvite', 'linvite', 'ilnvite', 'kinvite', 'iknvite', 'jinvite', 'ijnvite', 'ibnvite', 'inbvite', 'ihnvite', 'inhvite', 'injvite', 'imnvite', 'inmvite', 'incvite', 'invcite', 'infvite', 'invfite', 'ingvite', 'invgite', 'invbite', 'invuite', 'inviute', 'inv8ite', 'invi8te', 'inv9ite', 'invi9te', 'invoite', 'inviote', 'invlite', 'invilte', 'invkite', 'invikte', 'invjite', 'invijte', 'invirte', 'invitre', 'invi5te', 'invit5e', 'invi6te', 'invit6e', 'inviyte', 'invitye', 'invihte', 'invithe', 'invigte', 'invitge', 'invifte', 'invitfe', 'invitwe', 'invitew', 'invit3e', 'invite3', 'invit4e', 'invite4', 'inviter', 'invitef', 'invitde', 'invited', 'invitse', 'invites', 'erver', 'srver', 'sever', 'serer', 'servr', 'serve', 'sserver', 'seerver', 'serrver', 'servver', 'serveer', 'serverr', 'esrver', 'srever', 'sevrer', 'serevr', 'servre', 'aerver', 'werver', 'eerver', 'derver', 'xerver', 'zerver', 'swrver', 's3rver', 's4rver', 'srrver', 'sfrver', 'sdrver', 'ssrver', 'seever', 'se4ver', 'se5ver', 'setver', 'segver', 'sefver', 'sedver', 'sercer', 'serfer', 'serger', 'serber', 'servwr', 'serv3r', 'serv4r', 'servrr', 'servfr', 'servdr', 'servsr', 'servee', 'serve4', 'serve5', 'servet', 'serveg', 'servef', 'served', 'aserver', 'saerver', 'wserver', 'swerver', 'eserver', 'dserver', 'sderver', 'xserver', 'sxerver', 'zserver', 'szerver', 'sewrver', 's3erver', 'se3rver', 's4erver', 'se4rver', 'srerver', 'sferver', 'sefrver', 'sedrver', 'sesrver', 'serever', 'ser4ver', 'se5rver', 'ser5ver', 'setrver', 'sertver', 'segrver', 'sergver', 'serfver', 'serdver', 'sercver', 'servcer', 'servfer', 'servger', 'serbver', 'servber', 'servwer', 'servewr', 'serv3er', 'serve3r', 'serv4er', 'serve4r', 'servrer', 'servefr', 'servder', 'servedr', 'servser', 'servesr', 'servere', 'server4', 'serve5r', 'server5', 'servetr', 'servert', 'servegr', 'serverg', 'serverf', 'serverd', 'upport', 'spport', 'suport', 'supprt', 'suppot', 'suppor', 'ssupport', 'suupport', 'suppport', 'suppoort', 'supporrt', 'supportt', 'uspport', 'spuport', 'supoprt', 'supprot', 'suppotr', 'aupport', 'wupport', 'eupport', 'dupport', 'xupport', 'zupport', 'sypport', 's7pport', 's8pport', 'sipport', 'skpport', 'sjpport', 'shpport', 'suoport', 'su0port', 'sulport', 'supoort', 'sup0ort', 'suplort', 'suppirt', 'supp9rt', 'supp0rt', 'suppprt', 'supplrt', 'suppkrt', 'suppoet', 'suppo4t', 'suppo5t', 'suppott', 'suppogt', 'suppoft', 'suppodt', 'supporr', 'suppor5', 'suppor6', 'suppory', 'supporh', 'supporg', 'supporf', 'asupport', 'saupport', 'wsupport', 'swupport', 'esupport', 'seupport', 'dsupport', 'sdupport', 'xsupport', 'sxupport', 'zsupport', 'szupport', 'syupport', 'suypport', 's7upport', 'su7pport', 's8upport', 'su8pport', 'siupport', 'suipport', 'skupport', 'sukpport', 'sjupport', 'sujpport', 'shupport', 'suhpport', 'suopport', 'supoport', 'su0pport', 'sup0port', 'sulpport', 'suplport', 'supp0ort', 'supplort', 'suppiort', 'suppoirt', 'supp9ort', 'suppo9rt', 'suppo0rt', 'suppoprt', 'suppolrt', 'suppkort', 'suppokrt', 'suppoert', 'supporet', 'suppo4rt', 'suppor4t', 'suppo5rt', 'suppor5t', 'suppotrt', 'suppogrt', 'supporgt', 'suppofrt', 'supporft', 'suppodrt', 'suppordt', 'supportr', 'support5', 'suppor6t', 'support6', 'supporyt', 'supporty', 'supporht', 'supporth', 'supportg', 'supportf', 'invite', 'inv', 'server', 'support', 'addbot', 'join', '/invite', '/add', 'add', '/join', '/inv', '/server', '/support', 'supportserver', '/supportserver', 'oin', 'jin', 'jon', 'joi', 'jjoin', 'jooin', 'joiin', 'joinn', 'ojin', 'jion', 'joni', 'hoin', 'uoin', 'ioin', 'koin', 'moin', 'noin', 'jiin', 'j9in', 'j0in', 'jpin', 'jlin', 'jkin', 'joun', 'jo8n', 'jo9n', 'joon', 'joln', 'jokn', 'jojn', 'joib', 'joih', 'joij', 'joim', 'hjoin', 'jhoin', 'ujoin', 'juoin', 'ijoin', 'jioin', 'kjoin', 'jkoin', 'mjoin', 'jmoin', 'njoin', 'jnoin', 'j9oin', 'jo9in', 'j0oin', 'jo0in', 'jpoin', 'jopin', 'jloin', 'jolin', 'jokin', 'jouin', 'joiun', 'jo8in', 'joi8n', 'joi9n', 'joion', 'joiln', 'joikn', 'jojin', 'joijn', 'joibn', 'joinb', 'joihn', 'joinh', 'joinj', 'joimn', 'joinm'],
                 extras={'emoji': "hard_drive", "args": {}, "dev": False},
                 brief="Invite STW Daily to your server, or join the support server",
                 description="This command will provide you with links to invite STW Daily to your server, or join the support server")
    async def info(self, ctx):
        await self.info_command(ctx)

    @slash_command(name='invite',
                   description="Invite STW Daily to your server, or join the support server",
                   guild_ids=stw.guild_ids)
    async def slashinvite(self, ctx):
        await self.invite_command(ctx, True)


def setup(client):
    client.add_cog(Invite(client))

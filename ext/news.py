import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


class NewsView(discord.ui.View):

    def __init__(self, client, author, ctx, slash, page, stw_news, stw_pages_length, br_news, br_pages_length,
                 mode):
        super().__init__()
        self.client = client
        self.ctx = ctx
        self.author = author
        self.interaction_check_done = {}
        self.slash = slash
        self.page = page
        self.mode = mode
        self.stw_news = stw_news
        self.stw_pages_length = stw_pages_length
        self.br_news = br_news
        self.br_pages_length = br_pages_length

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
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.ctx, embed)
        else:
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.ctx, embed)
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
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed) #hi
        else:
            self.page = ((self.page - 1) % self.br_pages_length) + 1
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed)
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def change_mode(self, interaction, mode):
        if mode == "stw":
            self.mode = "stw"
            self.page = 1
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed)
            self.children[2].disabled = True
            self.children[3].disabled = False
        else:
            self.mode = "br"
            self.page = 1
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed)
            self.children[2].disabled = False
            self.children[3].disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def interaction_check(self, interaction):
        return await stw.view_interaction_check(self, interaction, "news")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="prev", row=0, label="Previous Page")
    async def prev_button(self, _button, interaction):
        await self.change_page(interaction, "prev")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="next", row=0, label="Next Page")
    async def next_button(self, _button, interaction):
        await self.change_page(interaction, "next")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="stw", disabled=True, row=1, label="Switch to STW")
    async def stw_button(self, _button, interaction):
        await self.change_mode(interaction, "stw")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="br", row=1, label="Switch to BR") # hi >:3 ?
    async def br_button(self, _button, interaction):
        await self.change_mode(interaction, "br")


# cog for the daily command.
class News(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def news_command(self, ctx, slash, page, mode):
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

        news_view = NewsView(self.client, ctx.author, ctx, slash, page, stw_news, stw_pages_length, br_news,
                             br_pages_length, mode)
        await stw.slash_send_embed(ctx, slash, embed, news_view)
        return

    @ext.slash_command(name='news',
                       description='View the latest in-game news from Fortnite',
                       guild_ids=stw.guild_ids)
    async def slashnews(self, ctx: discord.ApplicationContext,
                        page: Option(int,
                                     "The page number to view") = 1,
                        mode: Option(str, description="Choose a game mode to see news from",
                                     choices=["stw", "br"]) = "stw"):
        await self.news_command(ctx, True, page, mode)

    @ext.command(name='news',
                 aliases=['ew', 'nw', 'ne', 'nnew', 'neew', 'neww', 'enw', 'nwe', 'bew', 'hew', 'jew', 'mew', 'nww',
                          'n3w', 'n4w', 'nrw', 'nfw', 'ndw', 'nsw', 'neq', 'ne2', 'ne3', 'nee', 'nes', 'nea', 'bnew',
                          'nbew', 'hnew', 'nhew', 'jnew', 'njew', 'mnew', 'nmew', 'nwew', 'n3ew', 'ne3w', 'n4ew',
                          'ne4w', 'nrew', 'nerw', 'nfew', 'nefw', 'ndew', 'nedw', 'nsew', 'nesw', 'neqw', 'newq',
                          'ne2w', 'new2', 'new3', 'newe', 'newd', 'neaw', 'newa', 'ews', 'nws', 'new', 'nnews', 'neews',
                          'newws', 'newss', 'enws', 'nwes', 'bews', 'hews', 'jews', 'mews', 'nwws', 'n3ws', 'n4ws',
                          'nrws', 'nfws', 'ndws', 'nsws', 'neqs', 'ne2s', 'ne3s', 'nees', 'neds', 'ness', 'neas',
                          'newx', 'newz', 'bnews', 'nbews', 'hnews', 'nhews', 'jnews', 'njews', 'mnews', 'nmews',
                          'nwews', 'n3ews', 'ne3ws', 'n4ews', 'ne4ws', 'nrews', 'nerws', 'nfews', 'nefws', 'ndews',
                          'nedws', 'nsews', 'nesws', 'neqws', 'newqs', 'ne2ws', 'new2s', 'new3s', 'newes', 'newds',
                          'neaws', 'newas', 'newsa', 'newsw', 'newse', 'newsd', 'newxs', 'newsx', 'newzs', 'newsz', 'n',
                          '/n', '/new', '/news'],
                 extras={'emoji': "bang", "args": {'page': "The page number to view (Optional)",
                                                   "mode": "The game mode to see news from (stw/br) (Optional)"},
                         "dev": False},
                 brief="View the latest in-game news from Fortnite",
                 description="""This command will fetch and display the latest news from the game. You can switch between viewing Save the World or Battle Royale news by pressing the corresponding buttons. Cycle between pages by pressing the left/right arrow buttons.
                \u200b
                """)
    async def news(self, ctx, page=1, mode="stw"):
        await self.news_command(ctx, False, page, mode)


def setup(client):
    client.add_cog(News(client))

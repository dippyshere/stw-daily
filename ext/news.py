import asyncio

import discord
import discord.ext.commands as ext
from discord import Option
import json

import stwutil as stw


class NewsView(discord.ui.View):

    def __init__(self, client, author, context, slash, page, stw_news, stw_pages_length, br_news, br_pages_length,
                 mode):
        super().__init__()
        self.client = client
        self.context = context
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
        if self.author == interaction.user:
            return True
        else:
            try:
                already_notified = self.interaction_check_done[interaction.user.id]
            except:
                already_notified = False
                self.interaction_check_done[interaction.user.id] = True

            if not already_notified:
                support_url = self.client.config["support_url"]
                acc_name = ""
                error_code = "errors.stwdaily.not_author_interaction_response"
                embed = await stw.post_error_possibilities(interaction, self.client, "news", acc_name, error_code,
                                                           support_url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            else:
                return False

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
                       description='Get the latest news from Fortnite.',
                       guild_ids=stw.guild_ids)
    async def slashnews(self, ctx: discord.ApplicationContext,
                        page: int = 1,
                        mode: Option(str, description="Choose a Game Mode to get news from", choices=["stw", "br"]) = "stw"):
        await self.news_command(ctx, True, page, mode)

    @ext.command(name='news',
                 aliases=['n'],
                 extras={'emoji': "bang", "args": {'page': "The page number you want to see (Optional)",
                                                          "mode": "The game mode you want to see news from (stw/br) (Optional)"}},
                 brief="Get the latest news from Fortnite.",
                 description="""This command allows you to see the latest news from Fortnite in both Battle Royale and Save the World.
                \u200b
                """)
    async def news(self, ctx, page=1, mode="stw"):
        await self.news_command(ctx, False, page, mode)


def setup(client):
    client.add_cog(News(client))

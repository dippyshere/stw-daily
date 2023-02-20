"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the news command. It is used to get the latest news from fortnite
"""

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice
import asyncio

import stwutil as stw


class NewsView(discord.ui.View):
    """
    The UI View for the news command
    """

    def __init__(self, client, author, ctx, page, stw_news, stw_pages_length, br_news, br_pages_length, mode, og_msg,
                 desired_lang):
        super().__init__()
        self.client = client
        self.ctx = ctx
        self.author = author
        self.interaction_check_done = {}
        self.page = page
        self.mode = mode
        self.stw_news = stw_news
        self.stw_pages_length = stw_pages_length
        self.br_news = br_news
        self.br_pages_length = br_pages_length
        self.message = og_msg
        self.desired_lang = desired_lang

        self.button_emojis = {
            'prev': self.client.config["emojis"]["left_icon"],
            'next': self.client.config["emojis"]['right_icon'],
            'stw': self.client.config["emojis"]['stw_box'],
            'br': self.client.config["emojis"]['bp_icon']
        }

        self.children = list(map(self.map_button_emojis, self.children))
        self.children[0].label = stw.I18n.get('generic.view.button.previous', self.desired_lang)
        self.children[1].label = stw.I18n.get('generic.view.button.next', self.desired_lang)
        self.children[2].label = stw.I18n.get("news.view.button.stw", self.desired_lang)
        self.children[3].label = stw.I18n.get("news.view.button.br", self.desired_lang)

        if self.mode in ["stw", "Save the World"]:
            self.children[2].disabled = True
            self.children[3].disabled = False
            if self.stw_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True

        if self.mode in ["br", "Battle Royale"]:
            self.children[2].disabled = False
            self.children[3].disabled = True
            if self.br_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True

    def map_button_emojis(self, button):
        """
        Maps the button emojis to the buttons

        Args:
            button: The button to map the emoji to

        Returns:
            The button with the emoji mapped
        """
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def on_timeout(self):
        """
        Called when the view times out

        Returns:
            None
        """
        if self.mode in ["stw", "Save the World"]:
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length,
                                               self.desired_lang)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.ctx, embed, self.desired_lang)
        else:
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length,
                                               self.desired_lang)
            embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            embed = await stw.add_requested_footer(self.ctx, embed, self.desired_lang)
        for button in self.children:
            button.disabled = True
        return await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self)

    async def change_page(self, interaction, action):
        """
        Pagination. Changes the page of the news when requested.

        Args:
            interaction: The interaction that called the function
            action: The action to take. Either "prev" or "next" page

        Returns:
            None
        """
        if action == "next":
            self.page += 1
        elif action == "prev":
            self.page -= 1
        if self.mode in ["stw", "Save the World"]:
            try:
                self.page = ((self.page - 1) % self.stw_pages_length) + 1
            except:
                self.page = 1
            if self.stw_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length,
                                               self.desired_lang)
        else:
            try:
                self.page = ((self.page - 1) % self.br_pages_length) + 1
            except:
                self.page = 1
            if self.br_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length,
                                               self.desired_lang)
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def change_mode(self, interaction, mode):
        """
        Changes the game mode mode of the news command

        Args:
            interaction: The interaction that called the function
            mode: The mode to change to. Either "stw" or "br"

        Returns:
            None
        """
        if mode in ["stw", "Save the World"]:
            self.mode = "stw"
            self.page = 1
            if self.stw_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = await stw.create_news_page(self, self.ctx, self.stw_news, self.page, self.stw_pages_length,
                                               self.desired_lang)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed)
            self.children[2].disabled = True
            self.children[3].disabled = False
        else:
            self.mode = "br"
            self.page = 1
            if self.br_pages_length == 0:
                self.children[0].disabled = True
                self.children[1].disabled = True
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = await stw.create_news_page(self, self.ctx, self.br_news, self.page, self.br_pages_length,
                                               self.desired_lang)
            # embed = await stw.set_thumbnail(self.client, embed, "newspaper")
            # embed = await stw.add_requested_footer(self.ctx, embed)
            self.children[2].disabled = False
            self.children[3].disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        return

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command

        Args:
            interaction: The interaction to check

        Returns:
            True if the interaction is from the author of the command, False otherwise
        """
        return await stw.view_interaction_check(self, interaction, "news")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="prev", row=0, label="Previous Page")
    async def prev_button(self, _button, interaction):
        """
        The previous page button

        Args:
            _button: The button that was pressed
            interaction: The interaction that called the function
        """
        await self.change_page(interaction, "prev")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="next", row=0, label="Next Page")
    async def next_button(self, _button, interaction):
        """
        The next page button

        Args:
            _button: The button that was pressed
            interaction: The interaction that called the function
        """
        await self.change_page(interaction, "next")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="stw", disabled=True, row=1, label="Switch to STW")
    async def stw_button(self, _button, interaction):
        """
        The STW button

        Args:
            _button: The button that was pressed
            interaction: The interaction that called the function
        """
        await self.change_mode(interaction, "stw")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="br", row=1, label="Switch to BR")  # hi >:3 ?
    async def br_button(self, _button, interaction):
        """
        The BR button

        Args:
            _button: The button that was pressed
            interaction: The interaction that called the function
        """
        await self.change_mode(interaction, "br")


class News(ext.Cog):
    """
    Cog for the news command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def news_command(self, ctx, page, mode):
        """
        The main function for the news command

        Args:
            ctx: The context of the command
            page: The page to start on
            mode: The mode to start on

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        load_msg = await stw.slash_send_embed(ctx, await stw.processing_embed(self.client, ctx, desired_lang,
                                                                              stw.I18n.get("news.embed.processing.title", desired_lang)))
        stw_news_req = await stw.get_stw_news(self.client, desired_lang)
        stw_news_json = await stw_news_req.json(content_type=None)
        stw_news = stw_news_json["news"]["messages"]
        stw_pages_length = len(stw_news)
        br_news_req = await stw.get_br_news(self.client, desired_lang)
        br_news_json = await br_news_req.json(content_type=None)
        br_news = br_news_json["data"]["motds"]
        br_pages_length = len(br_news)

        if mode in ["br", "Battle Royale"]:
            embed = await stw.create_news_page(self, ctx, br_news, page, br_pages_length, desired_lang)
        else:
            embed = await stw.create_news_page(self, ctx, stw_news, page, stw_pages_length, desired_lang)
        embed = await stw.set_thumbnail(self.client, embed, "newspaper")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        news_view = NewsView(self.client, ctx.author, ctx, page, stw_news, stw_pages_length, br_news, br_pages_length,
                             mode, load_msg, desired_lang)
        await asyncio.sleep(0.25)
        await stw.slash_edit_original(ctx, load_msg, embed, news_view)
        return

    @ext.slash_command(name='news', name_localizations=stw.I18n.construct_slash_dict("news.slash.name"),
                       description='View the latest in-game news from Fortnite',
                       description_localizations=stw.I18n.construct_slash_dict("news.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashnews(self, ctx: discord.ApplicationContext,
                        page: Option(int, min_value=1, max_value=100, default=1,
                                     name_localizations=stw.I18n.construct_slash_dict("news.meta.args.page"),
                                     description="The page number to view",
                                     description_localizations=stw.I18n.construct_slash_dict("news.meta.args.page.description")) = 1,
                        mode: Option(default="stw",
                                     name_localizations=stw.I18n.construct_slash_dict("news.meta.args.mode"),
                                     description="Choose a game mode to see news from",
                                     description_localizations=stw.I18n.construct_slash_dict("news.slash.mode.description"),
                                     choices=[OptionChoice("Save the World", "stw",
                                                           stw.I18n.construct_slash_dict("generic.stw")),
                                              OptionChoice("Battle Royale", "br",
                                                           stw.I18n.construct_slash_dict("generic.br"))]) = "stw"):
        """
        This function is the entry point for the news command when called via slash

        Args:
            ctx: The context of the command
            page: The page to start on
            mode: The mode to start on
        """
        await self.news_command(ctx, page, mode)

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
                          '/n', '/new', '/news', 'feed'],
                 extras={'emoji': "bang", "args": {'news.meta.args.page': ['news.meta.args.page.description', True],
                                                   "news.meta.args.mode": ['news.meta.args.mode.description', True]},
                         "dev": False, "description_keys": ['news.meta.description'], "name_key": 'news.slash.name'},
                 brief="news.slash.description",
                 description="{0}")
    async def news(self, ctx, page=1, mode="stw"):
        """
        This function is the entry point for the news command when called traditionally

        Args:
            ctx: The context of the command
            page: The page to start on
            mode: The mode to start on
        """
        await self.news_command(ctx, page, mode)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(News(client))

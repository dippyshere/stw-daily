import asyncio

import discord
import discord.ext.commands as ext
from discord import Option
import json

import stwutil as stw


# cog for the daily command.
class News(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def create_news_page(self, ctx, news_json, current, total):
        generic = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "News", "placeholder"),
                              description=f"\u200b\n**News page {current} of {total}:**\u200b\n"
                                          f"**{news_json[current - 1]['title']}**"
                                          f"\n{news_json[current - 1]['body']}",
                              colour=generic)

        embed.description += "\u200b\n\u200b"

        # set embed image
        embed = await stw.set_embed_image(embed, news_json[current - 1]["image"])
        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def news_command(self, ctx, slash, page):
        # With all info extracted, create the output
        stw_news_req = await stw.get_stw_news(self.client)
        stw_news_json = await stw_news_req.json(content_type=None)
        stw_news = stw_news_json["news"]["messages"]
        pages_length = len(stw_news)
        embed = await self.create_news_page(ctx, stw_news, page, pages_length)

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        await stw.slash_send_embed(ctx, slash, embed)
        return

    @ext.slash_command(name='news',
                       description='Get the latest news from the game.',
                       guild_ids=stw.guild_ids)
    async def slashnews(self, ctx: discord.ApplicationContext):
        await self.news_command(ctx, True, page=1)

    @ext.command(name='news',
                 aliases=['n'],
                 extras={'emoji': "placeholder", "args": {}},
                 brief="Get the latest news from the game.",
                 description="""This command allows you to get the latest news from the game.
                \u200b
                """)
    async def news(self, ctx, page=1):
        await self.news_command(ctx, False, page)


def setup(client):
    client.add_cog(News(client))

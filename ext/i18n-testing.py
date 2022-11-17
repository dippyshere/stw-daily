import discord
import discord.ext.commands as ext

import stwutil as stw
from ext.profile.bongodb import get_user_document


# cog for the reloading related commands.
class Internationalisation(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def i18n_command(self, ctx, slash=False):

        user_profile = await get_user_document(self.client, ctx.author.id)
        localisation = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"]["localisation"]

        embed_colour = self.client.colours["auth_white"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "i18n", "experimental"),
                              description=f'\u200b\n',
                              color=embed_colour)
        try:
            embed.description += f'\nYour chosen language: {localisation}\n'
        except Exception as e:
            embed.description += f'\nError getting your chosen language: ```{e}```\n'
        try:
            embed.description += f'\nYour language: {ctx.locale}\n'
        except Exception as e:
            embed.description += f'\nError getting your language: ```{e}```\n'
        try:
            embed.description += f'\nInteraction language: {ctx.interaction.locale}\n'
        except Exception as e:
            embed.description += f'\nError getting interaction language: ```{e}```\n'
        try:
            embed.description += f'\nGuild language: {ctx.guild.preferred_locale}\n'
        except Exception as e:
            embed.description += f'\nError getting guild language: ```{e}```\n'

        embed.description += f'\n\u200b'

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)

        await stw.slash_send_embed(ctx, slash, embed)

    @ext.slash_command(name='i18n',
                       description='Test internationalisation',
                       guild_ids=stw.guild_ids)
    async def slashi18n(self, ctx: discord.ApplicationContext):
        await self.i18n_command(ctx, True)

    @ext.command(name='i18n',
                 aliases=[],
                 extras={'emoji': "experimental", "args": {}, "dev": True},
                 brief="Test internationalisation",
                 description="Test internationalisation (translation) for STW Daily")
    async def i18n(self, ctx):
        await self.i18n_command(ctx)


def setup(client):
    client.add_cog(Internationalisation(client))

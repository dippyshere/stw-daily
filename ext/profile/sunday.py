# it doesnt matter if its sunday

import asyncio
import json
import math
import os
import discord
import discord.ext.commands as ext
from discord import Option, slash_command

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio

from ext.profile.bongodb import get_user_document


async def add_field_to_page_embed(page_embed, setting, client, profile):
    setting_info = client.default_settings[setting]
    setting_type = str(type(setting_info["default"]).__name__)
    page_embed.fields[
        0].value += f"""\n\n# {setting.replace("_", " ").capitalize()}\n> {setting.replace("_", "-")} | {profile["settings"][setting]}\n{setting_info['description']}"""
    return page_embed


async def settings_page(page, client, ctx, pages, settings_per_page, selected_profile, selected_profile_data, settings,
                        embed_colour):
    page_embed = await main_page(page, client, ctx, pages, settings_per_page, selected_profile, selected_profile_data,
                                 settings, embed_colour)
    page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"
    await stw.slash_send_embed(ctx, True, embeds=page_embed)


async def main_page(page_number, client, ctx, pages, settings_per_page, selected_profile, selected_profile_data,
                    settings, embed_colour):
    shift = settings_per_page * page_number
    current_slice = settings[(0 + shift):(settings_per_page + shift)]

    page_embed = discord.Embed(title=await stw.add_emoji_title(client, "Settings", "settings"),
                               description=f"""\u200b
                              **Currently Selected Profile {selected_profile}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b""",
                               color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "settings_cog")
    page_embed = await stw.add_requested_footer(ctx, page_embed)

    page_embed.add_field(name=f"Showing Settings Page {page_number + 1}/{pages}", value="```md", inline=False)
    for setting in current_slice:
        page_embed = await add_field_to_page_embed(page_embed, setting, client, selected_profile_data)

    page_embed.fields[0].value += "```"

    return page_embed


async def settings_command(client, ctx, slash=False, setting=None, profile=None, value=None):
    settings_per_page = 5
    pages = math.ceil(len(client.default_settings) / settings_per_page)
    settings = client.settings_choices

    embed_colour = client.colours["profile_lavendar"]

    user_profile = await get_user_document(client, ctx.author.id)
    selected_profile = user_profile["global"]["selected_profile"]
    selected_profile_data = user_profile["profiles"][str(selected_profile)]

    if setting is None and profile is None and value is None:
        main_page_embed = await main_page(0, client, ctx, pages, settings_per_page, selected_profile,
                                          selected_profile_data, settings, embed_colour)
        main_page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"
        await stw.slash_send_embed(ctx, slash, embeds=main_page_embed)


# cog for the profile related settings & Disclosure - You & Me (Flume Remix)
class ProfileSettings(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def autocomplete_settings(self, actx: discord.AutocompleteContext):
        return self.client.settings_choices

    @ext.slash_command(name='settings',
                       description='Change or view the settings associated with your currently selected profile',
                       guild_ids=stw.guild_ids)
    async def slash_settings(self, ctx: discord.ApplicationContext,
                             setting: Option(str,
                                             "The name of the setting you wish to change",
                                             autocomplete=autocomplete_settings) = None,
                             value: Option(str,
                                           "The value you wish to set this setting to") = None,
                             profile: Option(int,
                                             "Which profile you would wish to execute this setting change on") = None
                             ):
        await settings_command(self.client, ctx, True, setting, profile, value)

    @ext.command(name='settings',
                 aliases=['boy'],
                 extras={'emoji': "pink_link", "args": {
                     'setting': 'The setting you wish to change(PENDING)',
                     'profile': 'The profile which to switch to so these new changes are applied to that profile, else just uses the current selected profile (Optional)(PENDING)',
                     'value': 'The new value for the setting you wish to change(PENDING)',
                 }, "dev": False},
                 brief="Change or view the settings associated with your currently selected profile(PENDING)",
                 description="""
                 This command allows you to change the settings of your profiles, you can either utilise the built in navigation of settings to change them, or change your settings through the utilisation of the commands arguments.(PENDING)
                \u200b
                """)
    async def settings(self, ctx, setting=None, value=None, profile=None):
        await settings_command(self.client, ctx, False, setting, profile, value)


def setup(client):
    client.add_cog(ProfileSettings(client))

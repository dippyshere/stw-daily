"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is whatever github wants it to be.
"""


# stw daily settings pages and menu

async def main_page(page_number, client, ctx, pages, settings_per_page, selected_profile, selected_profile_data,
                    settings,
                    embed_colour):
    page_embed = stw.Embed(title=f"{client.user.name} | Settings | Daily",
                           description=f"**Profile:** {selected_profile}\n\u200b\n**Settings:**\n\u200b\n",
                           colour=embed_colour)

    for i in range(page_number * settings_per_page, (page_number + 1) * settings_per_page):
        if i >= len(settings):
            break

        if settings[i] == "daily":
            page_embed.fields[
                0].value += f"**{settings[i]}:** {selected_profile_data['profiles'][selected_profile][settings[i]]}\n\u200b\n"
        else:
            page_embed.fields[
                0].value += f"**{settings[i]}:** {selected_profile_data['profiles'][selected_profile]['daily'][settings[i]]}\n\u200b\n"

    page_embed.set_footer(text=f"Page {page_number + 1}/{pages}")

    return page_embed


async def main_menu(client, ctx, page_number, pages, settings_per_page, selected_profile, selected_profile_data,
                    settings,
                    embed_colour, slash_command):
    page_embed = await main_page(page_number, client, ctx, pages, settings_per_page, selected_profile,
                                 selected_profile_data, settings, embed_colour)

    page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"

    menu = stw.DropdownMenu()
    menu.add_custom_id("main_menu_first")
    menu.add_custom_id("main_menu_previous")
    menu.add_custom_id("main_menu_next")
    menu.add_custom_id("main_menu_last")
    menu.add_custom_id("main_menu_select")

    menu.add_button("⏮", "main_menu_first")
    menu.add_button("◀", "main_menu_previous")
    menu.add_button("▶", "main_menu_next")
    menu.add_button("⏭", "main_menu_last")
    menu.add_select("main_menu_select",
                    options=[stw.DropdownOption(label=str(i), value=str(i)) for i in range(1, pages + 1)])

    await stw.slash_edit_embed(ctx, embeds=page_embed, components=menu)


async def settings_menu(client, ctx, page_number, pages, settings_per_page, selected_profile, selected_profile_data,
                        settings, embed_colour):
    page_embed = await main_page(page_number, client, ctx, pages, settings_per_page, selected_profile,
                                 selected_profile_data, settings, embed_colour)
    page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"
    await stw.slash_edit_embed(ctx, embeds=page_embed)


async def settings_menu_button(client, ctx, button, page_number, pages, settings_per_page, selected_profile,
                               selected_profile_data, settings, embed_colour):
    if button.custom_id == "settings_menu_first":
        page_number = 0
    elif button.custom_id == "settings_menu_previous":
        page_number -= 1
    elif button.custom_id == "settings_menu_next":
        page_number += 1
    elif button.custom_id == "settings_menu_last":
        page_number = pages - 1

    await settings_menu(client, ctx, page_number, pages, settings_per_page, selected_profile, selected_profile_data,
                        settings, embed_colour)


async def settings_menu_select(client, ctx, select, page_number, pages, settings_per_page, selected_profile,
                               selected_profile_data, settings, embed_colour):
    if select.custom_id == "settings_menu_select":
        page_number = int(select.values[0]) - 1

        await settings_menu(client, ctx, page_number, pages, settings_per_page, selected_profile, selected_profile_data,
                            settings, embed_colour)


async def settings_menu(client, ctx, page_number, pages, settings_per_page, selected_profile, selected_profile_data,
                        settings, embed_colour):
    page_embed = await main_page(page_number, client, ctx, pages, settings_per_page, selected_profile,
                                 selected_profile_data, settings, embed_colour)

    page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"

    menu = stw.DropdownMenu()
    menu.add_custom_id("settings_menu_first")
    menu.add_custom_id("settings_menu_previous")
    menu.add_custom_id("settings_menu_next")
    menu.add_custom_id("settings_menu_last")
    menu.add_custom_id("settings_menu_select")

    menu.add_button("⏮", "settings_menu_first")
    menu.add_button("◀", "settings_menu_previous")
    menu.add_button("▶", "settings_menu_next")
    menu.add_button("⏭", "settings_menu_last")
    menu.add_select("settings_menu_select",
                    options=[stw.DropdownOption(label=str(i), value=str(i)) for i in range(1, pages + 1)])

    await stw.slash_edit_embed(ctx, embeds=page_embed, components=menu)


# you are zoommin :(((   ong ok bye have fun i am having the fun PLEASE WAIT HOST IS WORKING WITH A SETTINGS DIALOG
# Path: ext\profile\settings.py
# Compare this snippet from ext\profile\settings.py:
#
import asyncio
import json
import os
import discord
import discord.ext.commands as ext
from discord import Option, slash_command

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio


async def insert_default_document(client, user_snowflake):
    default_document = client.user_default
    default_document['user_snowflake'] = user_snowflake
    await client.stw_database.insert_one(default_document)

    return default_document


async def replace_user_document(client, document):
    await client.stw_database.replace_one({"user_snowflake": document["user_snowflake"]}, document)


async def check_profile_ver_document(client, document):
    current_profile_ver = client.user_default["global"]["profiles_ver"]
    force_overwrite = client.user_default["global"]["rewrite_older"]
    user_id = document["user_snowflake"]

    try:
        if document["global"]["profiles_ver"] >= current_profile_ver:
            return document

    except KeyError:
        pass

    if force_overwrite is False:
        copied_default = client.user_default.copy()
        new_base = await asyncio.gather(asyncio.to_thread(deep_merge, copied_default, document))
        new_base = new_base[0]
        for profile in list(new_base["profiles"].keys()):
            new_base["profiles"][profile] = await asyncio.gather(
                asyncio.to_thread(deep_merge, copied_default["profiles"]["0"], new_base["profiles"][profile]))
    else:
        new_base = client.user_default
        new_base['user_snowflake'] = user_id

    new_base["global"]["profiles_ver"] = current_profile_ver

    await replace_user_document(client, new_base)
    return new_base


# cog for settings
class SettingsCog(ext.Cog, name="Settings"):
    def __init__(self, client):
        self.client = client

    @slash_command(name="settings", description="Show the settings panel")
    async def settings(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        embed_colour = settings["global"]["embed_colour"]
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]
        settings_per_page = 5

        pages = int(len(selected_profile_data) / settings_per_page)
        if len(selected_profile_data) % settings_per_page != 0:
            pages += 1

        page_number = 0

        page_embed = await main_page(page_number, self.client, ctx, pages, settings_per_page, selected_profile,
                                     selected_profile_data, settings, embed_colour)

        page_embed.fields[0].value += "\u200b\n*Waiting for an action*\n\u200b\n"

        menu = stw.DropdownMenu()
        menu.add_custom_id("settings_menu_first")
        menu.add_custom_id("settings_menu_previous")
        menu.add_custom_id("settings_menu_next")
        menu.add_custom_id("settings_menu_last")
        menu.add_custom_id("settings_menu_select")

        menu.add_button("⏮", "settings_menu_first")
        menu.add_button("◀", "settings_menu_previous")
        menu.add_button("▶", "settings_menu_next")
        menu.add_button("⏭", "settings_menu_last")
        menu.add_select("settings_menu_select",
                        options=[stw.DropdownOption(label=str(i), value=str(i)) for i in range(1, pages + 1)])

        await ctx.respond(embeds=page_embed, components=menu)

        while True:
            button = await self.client.wait_for_component(ctx)
            if button.custom_id == "settings_menu_first":
                page_number = 0
            elif button.custom_id == "settings_menu_previous":
                page_number -= 1
            elif button.custom_id == "settings_menu_next":
                page_number += 1
            elif button.custom_id == "settings_menu_last":
                page_number = pages - 1

            await settings_menu(self.client, ctx, page_number, pages, settings_per_page, selected_profile,
                                selected_profile_data, settings, embed_colour)

    @slash_command(name="set", description="Set a setting")
    async def set(self, ctx: stw.Context,
                  setting: Option(str, "The setting to change", required=True),
                  value: Option(str, "The value to set the setting to", required=True)):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        if setting not in selected_profile_data:
            await ctx.respond("This setting doesn't exist in the profile you have selected")
            return

        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                pass

        selected_profile_data[setting] = value

        await replace_user_document(self.client, settings)
        await ctx.respond(f"Set {setting} to {value}")

    @slash_command(name="select_profile", description="Select a profile")
    async def select_profile(self, ctx: stw.Context,
                             profile: Option(str, "The profile to select", required=True)):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        if profile not in selected_profile_data:
            await ctx.respond("This profile doesn't exist")
            return

        settings["global"]["selected_profile"] = profile

        await replace_user_document(self.client, settings)
        await ctx.respond(f"Selected profile {profile}")

    @slash_command(name="new_profile", description="Create a new profile")
    async def new_profile(self, ctx: stw.Context,
                          profile: Option(str, "The name of the profile to create", required=True)):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        if profile in selected_profile_data:
            await ctx.respond("This profile already exists")
            return

        settings["profiles"][profile] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond(f"Created profile {profile}")

    @slash_command(name="delete_profile", description="Delete a profile")
    async def delete_profile(self, ctx: stw.Context,
                             profile: Option(str, "The name of the profile to delete", required=True)):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        if profile not in selected_profile_data:
            await ctx.respond("This profile doesn't exist")
            return

        del settings["profiles"][profile]

        await replace_user_document(self.client, settings)
        await ctx.respond(f"Deleted profile {profile}")

    @slash_command(name="reset_profile", description="Reset a profile")
    async def reset_profile(self, ctx: stw.Context,
                            profile: Option(str, "The name of the profile to reset", required=True)):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        if profile not in selected_profile_data:
            await ctx.respond("This profile doesn't exist")
            return

        settings["profiles"][profile] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond(f"Reset profile {profile}")

    @slash_command(name="reset_all_profiles", description="Reset all profiles")
    async def reset_all_profiles(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        for profile in selected_profile_data:
            if profile == "0":
                continue
            settings["profiles"][profile] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond("Reset all profiles")

    @slash_command(name="reset_all_settings", description="Reset all settings")
    async def reset_all_settings(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        for profile in selected_profile_data:
            settings["profiles"][profile] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond("Reset all settings")

    @slash_command(name="reset_global_settings", description="Reset global settings")
    async def reset_global_settings(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        settings["global"] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond("Reset global settings")

    @slash_command(name="reset_all", description="Reset all settings and profiles")
    async def reset_all(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        for profile in selected_profile_data:
            settings["profiles"][profile] = settings["profiles"]["0"].copy()

        settings["global"] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond("Reset all settings and profiles")

    @slash_command(name="reset_all_profiles", description="Reset all profiles")
    async def reset_all_profiles(self, ctx: stw.Context):
        settings = await check_profile_ver_document(self.client, ctx.user_data)
        selected_profile = settings["global"]["selected_profile"]
        selected_profile_data = settings["profiles"][selected_profile]

        for profile in selected_profile_data:
            if profile == "0":
                continue
            settings["profiles"][profile] = settings["profiles"]["0"].copy()

        await replace_user_document(self.client, settings)
        await ctx.respond("Reset all profiles")
        # kiss yourself


# stw.context
class Context:
    def __init__(self, client: Client, data: dict):
        self.client = client
        self.data = data
        self._user_data = None

    @property
    def user_data(self) -> dict:
        if self._user_data is None:
            self._user_data = self.client.get_user_data(self.data["user_id"])
        return self._user_data

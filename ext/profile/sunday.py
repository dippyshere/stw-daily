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

from ext.profile.bongodb import *
from ext.profile.settings_checks import *


async def settings_profile_setting_select(view, select, interaction):
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    embed = await sub_setting_page(select.values[0][:-1], view.client, view.ctx, view.user_document)
    embed.fields[0].value += f"\u200b\n*Selected Setting: **{select.values[0][:-1]}***\n\u200b\n"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(select.values[0][:-1], view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  int(select.values[0][-1]), view.message)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def back_to_main_page(view, interaction):
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()
    main_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                            view.message)
    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings)
    embed.fields[0].value += f"\u200b\n*Returned to main menu*\n\u200b\n"
    await interaction.edit_original_response(embed=embed, view=main_view)


async def shift_page(view, interaction, amount):
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.page += amount

    max_pages = math.ceil(len(view.client.default_settings) / view.settings_per_page)
    if view.page < 1:
        view.page = max_pages
    elif view.page > max_pages:
        view.page = 1

    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings)

    embed.fields[0].value += f"\u200b\n*Changed to page **{view.page}***\n\u200b"

    new_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                           view.message)
    await interaction.edit_original_response(embed=embed, view=new_view)


async def shift_page_on_sub_page(view, interaction, amount):
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.page += amount

    max_pages = math.ceil(len(view.client.default_settings) / view.settings_per_page)
    if view.page < 1:
        view.page = max_pages
    elif view.page > max_pages:
        view.page = 1

    current_slice = get_current_settings_slice(view.page, view.settings_per_page, view.settings)

    view.selected_setting = current_slice[max(0, min(int(view.selected_setting_index), len(current_slice) - 1))]

    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document)
    embed.fields[0].value += f"\u200b\n*Changed to page **{view.page}***\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def sub_settings_profile_select_change(view, select, interaction):
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)
    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document)
    embed.fields[0].value += f"\u200b\n*Selected Profile **{new_profile_selected}***\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message)

    del view.client.processing_queue[view.user_document["user_snowflake"]]
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def settings_profile_select_change(view, select, interaction):
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)
    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings)
    embed.fields[0].value += f"\u200b\n*Selected profile **{new_profile_selected}***\n\u200b"
    new_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                           view.message)

    del view.client.processing_queue[view.user_document["user_snowflake"]]
    await interaction.edit_original_response(embed=embed, view=new_view)


async def edit_current_setting(view, interaction):
    selected_setting = view.selected_setting
    setting_information = view.client.default_settings[selected_setting]
    modal = RetrieveSettingChangeModal(setting_information, view.client, view, view.user_document, view.ctx,
                                       view.selected_setting)
    await interaction.response.send_modal(modal)


async def edit_current_setting_bool(view, interaction, set_value):
    selected_setting = view.selected_setting
    setting_information = view.client.default_settings[selected_setting]

    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.user_document["profiles"][view.selected_profile]["settings"][view.selected_setting] = set_value
    await replace_user_document(view.client, view.user_document)

    current_value = view.user_document["profiles"][view.selected_profile]["settings"][view.selected_setting]

    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document)
    embed.fields[0].value += f"\u200b\n*Changed **{view.selected_setting}** to **{current_value}***\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message)

    del view.client.processing_queue[view.user_document["user_snowflake"]]
    await interaction.edit_original_response(embed=embed, view=sub_view)


class RetrieveSettingChangeModal(discord.ui.Modal):
    def __init__(self, setting_information, client, view, user_document, ctx, current_setting):

        self.client = client
        self.view = view
        self.user_document = user_document
        self.ctx = ctx
        self.current_setting_value = user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"][current_setting]

        title = setting_information["modal_title"].format(self.current_setting_value)
        super().__init__(title=title)

        # aliases default description modal_title input_label check_function emoji input_type req_string

        input_style = discord.InputTextStyle.long if setting_information[
                                                         "input_type"] == "long" else discord.InputTextStyle.short
        setting_input = discord.ui.InputText(style=input_style,
                                             label=setting_information["input_label"].format(
                                                 self.current_setting_value),
                                             placeholder=setting_information["input_placeholder"].format(
                                                 self.current_setting_value),
                                             required=True,
                                             min_length=setting_information["min_length"],
                                             max_length=setting_information["max_length"])

        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        value = self.children[0].value
        check_function = globals()[self.client.default_settings[self.view.selected_setting]['check_function']]
        check_result = check_function(self.client, self.ctx, value)

        view = self.view

        if check_result is not False:
            selected_profile = self.user_document["global"]["selected_profile"]
            self.user_document["profiles"][str(selected_profile)]["settings"][self.view.selected_setting] = check_result
            await replace_user_document(view.client, view.user_document)

        embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document)
        sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                      view.client, view.page, view.ctx, view.settings,
                                                                      view.selected_setting_index, view.message)
        if check_result:
            embed.fields[0].value += f"\u200b\n*Changed Setting Value to **{value}***\n\u200b"
        else:
            embed.fields[0].value += f"\u200b\n*Invalid value entered! Try again*\n\u200b"

        del view.client.processing_queue[view.user_document["user_snowflake"]]
        await interaction.edit_original_response(embed=embed, view=sub_view)


async def settings_view_timeout(view):
    for child in view.children:
        child.disabled = True

    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings)
    embed.fields[0].value += f"\u200b\n*Timed out, please reuse command to continue*\n\u200b"
    await view.message.edit(embed=embed, view=view)


class SettingProfileSettingsSettingViewOfSettingSettings(discord.ui.View):
    def __init__(self, selected_setting, user_document, client, page, ctx, settings, selected_setting_index,
                 pass_message=None):
        super().__init__()

        if pass_message != None:
            self.message = pass_message

        settings_per_page = client.config["profile_settings"]["settings_per_page"]
        self.user_document = user_document
        self.client = client
        self.page = page
        self.ctx = ctx
        self.settings_per_page = settings_per_page
        self.settings = settings
        self.interaction_check_done = {}
        self.selected_setting_index = selected_setting_index
        self.selected_setting = selected_setting
        self.selected_profile = str(user_document["global"]["selected_profile"])
        current_slice = get_current_settings_slice(page, settings_per_page, settings)
        settings_options = generate_settings_view_options(client, current_slice)

        self.children[0].options = generate_profile_select_options(client, int(self.selected_profile), user_document)
        self.children[1].options = settings_options

        self.children[2:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[2:]))

        if isinstance(self.client.default_settings[selected_setting]["default"], bool):
            self.children.pop(5)

            if user_document["profiles"][self.selected_profile]["settings"][selected_setting]:
                self.children[5].disabled = True
            else:
                self.children[6].disabled = True

        else:
            self.children = self.children[:-2]

    async def on_timeout(self):
        await settings_view_timeout(self)

    async def interaction_check(self, interaction):
        return await stw.view_interaction_check(self, interaction, "settings")

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        await sub_settings_profile_select_change(self, select, interaction)

    @discord.ui.select(
        placeholder="Select setting to view/change here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def settings_select(self, select, interaction):
        await settings_profile_setting_select(self, select, interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_icon", row=2, label="Previous Page")
    async def previous_page(self, button, interaction):
        await shift_page_on_sub_page(self, interaction, -1)  # hio :3 hyanson

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="right_icon", row=2, label="Next Page")
    async def next_page(self, button, interaction):
        await shift_page_on_sub_page(self, interaction, 1)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_arrow", row=3, label="Main Menu")
    async def exit_back(self, button, interaction):
        await back_to_main_page(self, interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="library_cogs", row=3, label="Change Value")
    async def edit_setting_non_bool(self, button, interaction):
        await edit_current_setting(self, interaction)

    @discord.ui.button(style=discord.ButtonStyle.green, emoji="check_checked", row=3, label="True")
    async def edit_setting_bool_true(self, button, interaction):
        await edit_current_setting_bool(self, interaction, True)

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="check_empty", row=3, label="False")
    async def edit_setting_bool_false(self, button, interaction):
        await edit_current_setting_bool(self, interaction, False)


class MainPageProfileSettingsView(discord.ui.View):
    def __init__(self, user_document, client, page, ctx, settings, pass_message=None):
        super().__init__()

        if pass_message != None:
            self.message = pass_message

        settings_per_page = client.config["profile_settings"]["settings_per_page"]
        self.user_document = user_document
        self.client = client
        self.page = page
        self.ctx = ctx
        self.settings_per_page = settings_per_page
        self.settings = settings
        self.interaction_check_done = {}

        current_slice = get_current_settings_slice(page, settings_per_page, settings)
        settings_options = generate_settings_view_options(client, current_slice)

        selected_profile = user_document["global"]["selected_profile"]

        self.children[0].options = generate_profile_select_options(client, selected_profile, user_document)
        self.children[1].options = settings_options

        self.children[2:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[2:]))

    async def on_timeout(self):
        await settings_view_timeout(self)

    async def interaction_check(self, interaction):
        return await stw.view_interaction_check(self, interaction, "settings")

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        await settings_profile_select_change(self, select, interaction)

    @discord.ui.select(
        placeholder="Select setting to view/change here",
        min_values=1,
        max_values=1,  # i thought you were afk but it was just my theme :3
        options=[],  # :3
    )
    async def settings_select(self, select, interaction):
        await settings_profile_setting_select(self, select, interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_icon", row=2, label="Previous Page")
    async def previous_page(self, button, interaction):
        await shift_page(self, interaction, -1)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="right_icon", row=2, label="Next Page")
    async def next_page(self, button, interaction):
        await shift_page(self, interaction, 1)


async def add_field_to_page_embed(page_embed, setting, client, profile):
    setting_info = client.default_settings[setting]
    setting_type = str(type(setting_info["default"]).__name__)
    page_embed.fields[
        0].value += f"""\n\n# {setting.replace("_", " ").capitalize()}\n> {setting.replace("_", "-")} | {profile["settings"][setting]}\n{setting_info['description']}"""
    return page_embed


def generate_settings_view_options(client, current_slice):
    select_options = []

    for index, setting_option in enumerate(current_slice):
        emoji_key = client.default_settings[setting_option]["emoji"]
        select_options.append(discord.SelectOption(label=setting_option, value=setting_option + str(index),
                                                   emoji=client.config["emojis"][emoji_key]))

    return select_options


def get_current_settings_slice(page_number, settings_per_page, settings):
    shift = settings_per_page * (page_number - 1)
    return settings[(0 + shift):(settings_per_page + shift)]


async def main_page(page_number, client, ctx, user_profile,
                    settings):
    embed_colour = client.colours["profile_lavendar"]

    selected_profile = user_profile["global"]["selected_profile"]
    selected_profile_data = user_profile["profiles"][str(selected_profile)]
    settings_per_page = client.config["profile_settings"]["settings_per_page"]

    pages = math.ceil(len(client.default_settings) / settings_per_page)
    current_slice = get_current_settings_slice(page_number, settings_per_page, settings)

    page_embed = discord.Embed(title=await stw.add_emoji_title(client, "Settings", "settings"),
                               description=f"""\u200b
                              **Currently Selected Profile {selected_profile}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b""",
                               color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "settings_cog")
    page_embed = await stw.add_requested_footer(ctx, page_embed)

    page_embed.add_field(name=f"Showing Settings Page {page_number}/{pages}", value="```md", inline=False)
    for setting in current_slice:
        page_embed = await add_field_to_page_embed(page_embed, setting, client, selected_profile_data)

    page_embed.fields[0].value += "```"

    return page_embed


async def sub_setting_page(setting, client, ctx, user_profile):
    setting_info = client.default_settings[setting]

    embed_colour = client.colours["profile_lavendar"]

    selected_profile = user_profile["global"]["selected_profile"]
    selected_profile_data = user_profile["profiles"][str(selected_profile)]

    page_embed = discord.Embed(title=await stw.add_emoji_title(client, "Settings", "settings"),
                               description=f"""\u200b
                              **Currently Selected Profile {selected_profile}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b""",
                               color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "settings_cog")
    page_embed = await stw.add_requested_footer(ctx, page_embed)

    requirement_string = ""
    if isinstance(setting_info['default'], bool):
        requirement_string = "True or False"
    else:
        requirement_string = setting_info['req_string']

    page_embed.add_field(name=f"{client.config['emojis'][setting_info['emoji']]} Selected Setting: {setting}",
                         value=f"""```asciidoc\n== {setting.replace("_", " ").capitalize()}\n// {setting}\n\nCurrent Value:: {selected_profile_data["settings"][setting]}\n\n{setting_info["description"]}\n\n\n\nType:: {type(setting_info['default']).__name__}\nRequirement:: {requirement_string}```""",
                         inline=False)

    return page_embed


async def map_settings_aliases(client):
    default_settings = client.default_settings
    setting_map = {}

    for setting in default_settings:
        setting_info = default_settings[setting]
        setting_map[setting] = setting

        for alias in setting_info["aliases"]:
            setting_map[alias] = setting

    return setting_map


async def default_page_profile_settings(client, ctx, user_profile, settings, message):
    page = client.config["profile_settings"]["default_settings_page"]
    main_page_embed = await main_page(page, client, ctx, user_profile, settings)
    main_page_embed.fields[0].value += message

    settings_view = MainPageProfileSettingsView(user_profile, client, page, ctx, settings)
    await stw.slash_send_embed(ctx, embeds=main_page_embed, view=settings_view)


async def settings_command(client, ctx, setting=None, profile=None, value=None):
    settings = client.settings_choices

    user_profile = await get_user_document(client, ctx.author.id)
    user_snowflake = user_profile["user_snowflake"]

    if setting is not None or profile is not None or value is not None:
        setting_map = await map_settings_aliases(client)

        happy_message = "\u200b\n*"
        if setting in list(setting_map.keys()):
            settings_per_page = client.config["profile_settings"]["settings_per_page"]
            setting = setting_map[setting]
            happy_message += f"Set Setting **{setting}**"
        else:
            setting = False

        if str(profile) in list(user_profile["profiles"].keys()):
            client.processing_queue[user_snowflake] = True

            new_profile_selected = int(profile)
            user_profile["global"]["selected_profile"] = new_profile_selected
            await replace_user_document(client, user_profile)

            del client.processing_queue[user_snowflake]
            happy_message += f" on profile **{profile}**"
        elif profile is not None:
            profile = False

        if value is not None and value is not False and profile is not None and profile is not False and setting is not None and setting is not False:
            client.processing_queue[user_snowflake] = True

            if isinstance(client.default_settings[setting]['default'], bool):
                check_function = check_bool
            else:
                check_function = globals()[client.default_settings[setting]['check_function']]

            check_result = check_function(client, ctx, value)

            if check_result is not False:
                selected_profile = user_profile["global"]["selected_profile"]

                if isinstance(client.default_settings[setting]['default'], bool):
                    user_profile["profiles"][profile]["settings"][setting] = boolean_string_representation[value]
                else:
                    user_profile["profiles"][profile]["settings"][setting] = check_result

                await replace_user_document(client, user_profile)

            if check_result is not False:
                happy_message += f" to **{value}**"
            else:
                value = False

            del client.processing_queue[user_snowflake]

            if value is not False:
                embed = await sub_setting_page(setting, client, ctx, user_profile)

                selected_setting_index = (settings.index(setting) % settings_per_page) - 1
                page = math.ceil(settings.index(setting) / settings_per_page)

                sub_view = SettingProfileSettingsSettingViewOfSettingSettings(setting, user_profile,
                                                                              client, page, ctx,
                                                                              settings,
                                                                              selected_setting_index)
                embed.fields[0].value += happy_message + "*\n\u200b\n"
                await stw.slash_send_embed(ctx, embeds=embed, view=sub_view)
                return

        elif value is not None:
            value = False

        list_of_potential_nones = [setting, profile, value]
        associated_error = ["Invalid setting passed", "Invalid profile passed", "Invalid value passed"]
        associated_missing = ["Missing setting passed", "Missing profile to apply change to",
                              "Missing value to change to"]
        base_error_message = "\u200b\n*Failed to apply setting change:"

        for index, missing_or_error in enumerate(list_of_potential_nones):

            if missing_or_error == False:
                base_error_message += f" {associated_error[index]}"
            elif missing_or_error == None:
                base_error_message += f" {associated_missing[index]}"
            if not missing_or_error or not missing_or_error:
                if index < len(list_of_potential_nones) - 1:
                    base_error_message += ","

        base_error_message += "*\n\u200b\n"

        if setting is not None and setting is not False:
            embed = await sub_setting_page(setting, client, ctx, user_profile)
            selected_setting_index = (settings.index(setting) % settings_per_page) - 1
            page = math.floor(settings.index(setting) / settings_per_page) + 1

            sub_view = SettingProfileSettingsSettingViewOfSettingSettings(setting, user_profile,
                                                                          client, page, ctx,
                                                                          settings,
                                                                          selected_setting_index)
            embed.fields[0].value += base_error_message
            await stw.slash_send_embed(ctx, embeds=embed, view=sub_view)
            return
        else:
            await default_page_profile_settings(client, ctx, user_profile, settings, base_error_message)
            return

    await default_page_profile_settings(client, ctx, user_profile, settings,
                                        "\u200b\n*Waiting for an action*\n\u200b\n")
    return


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
                             profile: Option(str,
                                             "Which profile you would wish to execute this setting change on") = None,
                             value: Option(str,
                                           "The value you wish to set this setting to") = None
                             ):
        await settings_command(self.client, ctx, setting, profile, value)

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
    async def settings(self, ctx, setting=None, profile=None, value=None):
        await settings_command(self.client, ctx, setting, profile, value)


def setup(client):
    client.add_cog(ProfileSettings(client))

# le guide for ze epic function for le check for le non bool type of le setting
# must be synchronous no async around here
# ok so the name of the function must be unique and must be in this file, the parameters passed to the function are
# bot client, context, value
# where bot client is well the same fucking client as everywhere
# context is either the context from a slash command or a normal command
# value is the inputted value from the user which the function should check if it meets the requirements for this setting
# the return type must be the value that the setting will become, or False if the value inputted is not allowed
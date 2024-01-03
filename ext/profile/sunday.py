"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the settings command. not currently under development.
"""

# it does matter if its sunday

import math
import logging

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw
from ext.profile.bongodb import *
from ext.profile.settings_checks import *

logger = logging.getLogger(__name__)


async def settings_profile_setting_select(view, select, interaction, desired_lang):
    """
    This is the function that is called when the user selects a setting to change.

    Args:
        view: The view that the user is currently on.
        select: The select menu that the user selected.
        interaction: The interaction that the user did.
        desired_lang: The desired language.
    """
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    embed = await sub_setting_page(select.values[0][:-1], view.client, view.ctx, view.user_document, desired_lang)
    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.select', desired_lang, select.values[0][:-1])}\n\u200b\n"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(select.values[0][:-1], view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  int(select.values[0][-1]), view.message,
                                                                  desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, sub_view)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def back_to_main_page(view, interaction, desired_lang):
    """
    This is the function that is called when the user selects the back button on the sub page.

    Args:
        view: The view that the user is currently on.
        interaction: The interaction that the user did.
        desired_lang: The desired language.
    """
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()
    main_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                            view.message, desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, main_view)
    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings, desired_lang)
    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.return', desired_lang)}\n\u200b\n"
    await interaction.edit_original_response(embed=embed, view=main_view)


async def shift_page(view, interaction, amount, desired_lang):
    """
    This is the function that is called when the user selects the back or forward button on the main page.

    Args:
        view: The view that the user is currently on.
        interaction: The interaction that the user did.
        amount: The amount of pages to shift by.
        desired_lang: The desired language.
    """
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

    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings, desired_lang)

    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.pagination.changepage', desired_lang, view.page)}\n\u200b"

    new_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                           view.message, desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, new_view)
    await interaction.edit_original_response(embed=embed, view=new_view)


async def shift_page_on_sub_page(view, interaction, amount, desired_lang):
    """
    This is the function that is called when the user selects the back or forward button on the sub page.

    Args:
        view: The view that the user is currently on.
        interaction: The interaction that the user did.
        amount: The amount of pages to shift by.
        desired_lang: The desired language.
    """
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

    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document, desired_lang)
    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.pagination.changepage', desired_lang, view.page)}\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message,
                                                                  desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, sub_view)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def sub_settings_profile_select_change(view, select, interaction, desired_lang):
    """
    This is the function that is called when the user selects a setting to change on the sub page.

    Args:
        view: The view that the user is currently on.
        select: The select menu that the user selected.
        interaction: The interaction that the user did.
        desired_lang: The desired language.
    """
    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()
    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    await replace_user_document(view.client, view.user_document)
    del view.client.processing_queue[view.user_document["user_snowflake"]]
    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document, desired_lang)
    embed.fields[0].value += f"\u200b\n{stw.I18n.get('profile.embed.select', desired_lang, new_profile_selected)}\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message,
                                                                  desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, sub_view)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def settings_profile_select_change(view, select, interaction, desired_lang):
    """
    This is the function that is called when the user selects a setting to change on the main page.

    Args:
        view: The view that the user is currently on.
        select: The select menu that the user selected.
        interaction: The interaction that the user did.
        desired_lang: The desired language.
    """
    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    await replace_user_document(view.client, view.user_document)
    del view.client.processing_queue[view.user_document["user_snowflake"]]
    embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings, desired_lang)
    embed.fields[0].value += f"\u200b\n{stw.I18n.get('profile.embed.select', desired_lang, new_profile_selected)}\n\u200b"
    new_view = MainPageProfileSettingsView(view.user_document, view.client, view.page, view.ctx, view.settings,
                                           view.message, desired_lang=desired_lang)
    await active_view(view.client, view.ctx.author.id, new_view)
    await interaction.edit_original_response(embed=embed, view=new_view)


async def edit_current_setting(view, interaction, desired_lang):
    """
    This is the function that is called when the user selects the edit button on the sub page.

    Args:
        view: The view that the user is currently on.
        interaction: The interaction that the user did.
        desired_lang: The desired language
    """
    setting_information = view.client.default_settings[view.selected_setting]
    modal = RetrieveSettingChangeModal(setting_information, view.client, view, view.user_document, view.ctx,
                                       view.selected_setting, desired_lang)

    await interaction.response.send_modal(modal)


async def edit_current_setting_select(view, select, interaction, desired_lang):
    """
    This is the function that is called when the user selects the edit button on the sub page.

    Args:
        view: The view that the user is currently on.
        select: The select menu that the user selected.
        interaction: The interaction that the user did.
        desired_lang: The desired language
    """
    selected_setting = view.selected_setting
    setting_information = view.client.default_settings[selected_setting]

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.user_document["profiles"][str(view.selected_profile)]["settings"][view.selected_setting] = select.values[0]
    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    await replace_user_document(view.client, view.user_document)
    del view.client.processing_queue[view.user_document["user_snowflake"]]

    current_value = view.user_document["profiles"][str(view.selected_profile)]["settings"][view.selected_setting]

    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document, desired_lang)

    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.change', desired_lang, view.selected_setting, current_value)}\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message,
                                                                  desired_lang=desired_lang)

    await active_view(view.client, view.ctx.author.id, sub_view)
    await interaction.edit_original_response(embed=embed, view=sub_view)


async def edit_current_setting_bool(view, interaction, set_value, desired_lang):
    """
    This is the function that is called when the user selects the edit button on the sub page.

    Args:
        view: The view that the user is currently on.
        interaction: The interaction that the user did.
        set_value: The value to set the setting to.
        desired_lang: The desired language
    """
    selected_setting = view.selected_setting
    setting_information = view.client.default_settings[selected_setting]

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.user_document["profiles"][str(view.selected_profile)]["settings"][view.selected_setting] = set_value
    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    await replace_user_document(view.client, view.user_document)
    del view.client.processing_queue[view.user_document["user_snowflake"]]

    current_value = view.user_document["profiles"][str(view.selected_profile)]["settings"][view.selected_setting]

    embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document, desired_lang)

    embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.change', desired_lang, view.selected_setting, current_value)}\n\u200b"
    sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                  view.client, view.page, view.ctx, view.settings,
                                                                  view.selected_setting_index, view.message,
                                                                  desired_lang=desired_lang)

    await active_view(view.client, view.ctx.author.id, sub_view)
    await interaction.edit_original_response(embed=embed, view=sub_view)


class RetrieveSettingChangeModal(discord.ui.Modal):
    """
    This is the modal that is used to retrieve the value that the user wants to change the setting to.
    """

    def __init__(self, setting_information, client, view, user_document, ctx, current_setting, desired_lang):

        self.client = client
        self.view = view
        self.user_document = user_document
        self.ctx = ctx
        try:
            self.current_setting_value = user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"][current_setting]
        except:
            self.current_setting_value = ""
        self.default_value = str(setting_information["default"])
        self.desired_lang = desired_lang

        logger.debug(f"Setting information: {setting_information}")
        super().__init__(title=stw.truncate(stw.I18n.get(setting_information["modal_title"], desired_lang), 45),
                         timeout=480.0)

        # aliases default description modal_title input_label check_function emoji input_type req_string

        input_style = discord.InputTextStyle.long if setting_information["input_type"] == "long" else discord.InputTextStyle.short
        setting_input = discord.ui.InputText(style=input_style,
                                             label=stw.truncate(stw.I18n.get(setting_information["input_label"],
                                                                             self.desired_lang), 45),
                                             placeholder=stw.truncate(
                                                 stw.I18n.get(setting_information["input_placeholder"],
                                                              self.desired_lang, self.default_value)),
                                             value=stw.truncate(str(self.current_setting_value), 4000),
                                             min_length=setting_information["min_length"],
                                             max_length=setting_information["max_length"])

        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        """
        This is the function that is called when the user submits the modal.

        Args:
            interaction: The interaction that the user did.
        """

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        value = self.children[0].value
        check_function = globals()[self.client.default_settings[self.view.selected_setting]['check_function']]
        check_result = check_function(self.client, self.ctx, value)

        view = self.view

        if check_result[1] is not False:
            selected_profile = self.user_document["global"]["selected_profile"]
            self.user_document["profiles"][str(selected_profile)]["settings"][self.view.selected_setting] = check_result[0]
            self.client.processing_queue[self.user_document["user_snowflake"]] = True
            await replace_user_document(view.client, view.user_document)
            del view.client.processing_queue[view.user_document["user_snowflake"]]
            if self.view.selected_setting == "language" and stw.I18n.is_lang(check_result[0]):
                self.desired_lang = self.user_document["profiles"][str(selected_profile)]["settings"]["language"]
            if self.view.selected_setting == "language" and check_result[0] == "auto":
                try:
                    interaction_language = self.ctx.interaction.locale
                    if interaction_language.lower() in ["en-us", "en-gb", "en"]:
                        interaction_language = "en"
                    elif interaction_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn",
                                                          "zh-hans-sg"]:
                        interaction_language = "zh-CHS"
                    elif interaction_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                          "zh-hant-hk", "zh-hant-mo"]:
                        interaction_language = "zh-CHT"
                    if not stw.I18n.is_lang(interaction_language):
                        interaction_language = None
                except:
                    interaction_language = None
                try:
                    guild_language = self.ctx.guild.preferred_locale
                    if guild_language.lower() in ["en-us", "en-gb", "en"]:
                        guild_language = "en"
                    elif guild_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn", "zh-hans-sg"]:
                        guild_language = "zh-CHS"
                    elif guild_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                    "zh-hant-hk", "zh-hant-mo"]:
                        guild_language = "zh-CHT"
                    if not stw.I18n.is_lang(guild_language):
                        guild_language = None
                except:
                    guild_language = None
                self.desired_lang = interaction_language or guild_language or "en"

        embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document,
                                       self.desired_lang)
        sub_view = SettingProfileSettingsSettingViewOfSettingSettings(view.selected_setting, view.user_document,
                                                                      view.client, view.page, view.ctx, view.settings,
                                                                      view.selected_setting_index, view.message,
                                                                      desired_lang=self.desired_lang)
        await active_view(view.client, view.ctx.author.id, sub_view)

        if check_result[1] is not False:
            embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.change1', self.desired_lang, str(check_result[0]))}\n\u200b"
        else:
            embed.fields[0].value += f"\u200b\n{stw.I18n.get('settings.change1.invalid', self.desired_lang)}\n\u200b"

        await interaction.edit_original_response(embed=embed, view=sub_view)


async def settings_view_timeout(view, sub=False, desired_lang=None):
    """
    This is the function that is called when the view times out.

    Args:
        view: The view that timed out.
        sub: Whether or not the view is a sub page.
        desired_lang: The desired language.
    """
    for child in view.children:
        child.disabled = True

    if not sub:
        embed = await main_page(view.page, view.client, view.ctx, view.user_document, view.settings, desired_lang)
    else:
        embed = await sub_setting_page(view.selected_setting, view.client, view.ctx, view.user_document, desired_lang)

    embed.fields[0].value += f"\u200b\n{stw.I18n.get('generic.embed.timeout', desired_lang)}\n\u200b"
    # TODO: This has a none type error
    # await view.message.edit(embed=embed, view=view)
    if isinstance(view.message, discord.Interaction):
        method = view.message.edit_original_response
    else:
        try:
            method = view.message.edit
        except:
            method = view.ctx.edit
    try:
        if isinstance(view.ctx, discord.ApplicationContext):
            try:
                return await method(embed=embed, view=view)
            except:
                try:
                    return await view.ctx.edit(embed=embed, view=view)
                except:
                    return await method(embed=embed, view=view)
        else:
            return await method(embed=embed, view=view)
    except:
        if isinstance(view.ctx, discord.ApplicationContext):
            try:
                return await method(view=view)
            except:
                try:
                    return await view.ctx.edit(view=view)
                except:
                    return await method(view=view)
        else:
            return await method(view=view)


def generate_setting_options(client, options, user_document, selected_setting, desired_lang):
    """
    This function generates the options for a setting.

    Args:
        client: The client.
        options: The options to generate.
        user_document: The user document.
        selected_setting: The selected setting.
        desired_lang: The desired language.

    Returns:
        The generated options.
    """
    select_options = []
    print(options)

    try:
        current = user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"][selected_setting]
    except:
        current = client.default_settings[selected_setting]["default"]

    for attr, val in options.items():
        logger.debug(f"Generating select menu for option: {attr}, {val}")
        try:
            description = stw.I18n.get(val['description'], desired_lang)
            description = stw.truncate(description) if '.' not in description else None
        except:
            description = None

            # Add this option to our select options
            select_options.append(discord.SelectOption(label = stw.truncate(stw.I18n.get(val['name'], desired_lang)),
            value = attr,
            emoji = client.config["emojis"][val["emoji"]],
            default = True if current == attr else False))

    return select_options if len(select_options) > 0 else [discord.SelectOption(label="placeholder")]


class SettingProfileSettingsSettingViewOfSettingSettings(discord.ui.View):  # what the hell
    """
    This is the view that is used to display the settings of a setting.
    """

    def __init__(self, selected_setting, user_document, client, page, ctx, settings, selected_setting_index,
                 pass_message=None, desired_lang=None):
        super().__init__(timeout=480.0)

        if pass_message is not None:
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
        self.desired_lang = desired_lang

        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1].placeholder = stw.I18n.get('settings.view.select.setting.placeholder', self.desired_lang)
        self.children[2].label = stw.I18n.get('generic.view.button.previous', self.desired_lang)
        self.children[3].label = stw.I18n.get('generic.view.button.next', self.desired_lang)
        self.children[4].label = stw.I18n.get('generic.view.button.mainmenu', self.desired_lang)
        self.children[5].label = stw.I18n.get('settings.view.button.changevalue', self.desired_lang)
        self.children[6].label = stw.I18n.get('generic.true', self.desired_lang)
        self.children[7].label = stw.I18n.get('generic.false', self.desired_lang)

        current_slice = get_current_settings_slice(page, settings_per_page, settings)
        # print(current_slice)
        settings_options = generate_settings_view_options(self.client, current_slice, self.desired_lang,
                                                          selected_setting)

        self.children[0].options = generate_profile_select_options(self.client, int(self.selected_profile),
                                                                   user_document, desired_lang)
        self.children[1].options = settings_options

        self.children[2:8] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[2:8]))

        # Change which children should be displayed based on the type of the current setting
        setting_type = get_setting_type(selected_setting, client)

        if setting_type == "select":
            # Removes Change Value, True and False buttons.
            del self.children[5:8]

            # Sets the select values
            self.children[5].placeholder = stw.I18n.get(self.client.default_settings[selected_setting]["placeholder"], self.desired_lang)
            self.children[5].options = generate_setting_options(self.client,
                                                                self.client.default_settings[selected_setting]["options"],
                                                                user_document, selected_setting,
                                                                self.desired_lang)

        elif setting_type == "bool":
            # Disable the currently selected boolean button
            current_document = user_document["profiles"][self.selected_profile]

            if current_document["settings"].get(selected_setting, False):
                self.children[6].disabled = True
            else:
                self.children[7].disabled = True

            # Removes the select new setting, and Change value button
            del self.children[5]
            del self.children[7]

        elif setting_type == "modal":
            # Removes the True and False buttons and the select
            del self.children[6:9]
        
        self.timed_out = False

    async def on_timeout(self):
        """
        This is the function that is called when the view times out.
        """
        self.timed_out = True
        await settings_view_timeout(self, True, self.desired_lang)

    async def interaction_check(self, interaction):
        """
        This is the function that is called when the user interacts with the view.

        Args:
            interaction: The interaction that the user did.

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "settings") & await timeout_check_processing(self,
                                                                                                                self.client,
                                                                                                                interaction)

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        """
        This is the function that is called when the user selects a profile.

        Args:
            select: The select that the user selected.
            interaction: The interaction that the user did.
        """
        await sub_settings_profile_select_change(self, select, interaction, self.desired_lang)

    @discord.ui.select(
        placeholder="Select a setting to view/change here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def settings_select(self, select, interaction):
        """
        This is the function that is called when the user selects a setting.

        Args:
            select: The select that the user selected.
            interaction: The interaction that the user did.
        """
        await settings_profile_setting_select(self, select, interaction, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_icon", row=2, label="Previous Page")
    async def previous_page(self, button, interaction):
        """
        This is the function that is called when the user presses the previous page button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await shift_page_on_sub_page(self, interaction, -1, self.desired_lang)  # hio :3 hyanson

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="right_icon", row=2, label="Next Page")
    async def next_page(self, button, interaction):
        """
        This is the function that is called when the user presses the next page button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await shift_page_on_sub_page(self, interaction, 1, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_arrow", row=3, label="Main Menu")
    async def exit_back(self, button, interaction):
        """
        This is the function that is called when the user presses the exit button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await back_to_main_page(self, interaction, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="library_cogs", row=3, label="Change Value")
    async def edit_setting_non_bool(self, button, interaction):
        """
        This is the function that is called when the user presses the edit setting button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await edit_current_setting(self, interaction, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.green, emoji="check_checked", row=3, label="True")
    async def edit_setting_bool_true(self, button, interaction):
        """
        This is the function that is called when the user presses the edit setting button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await edit_current_setting_bool(self, interaction, True, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="check_empty", row=3, label="False")
    async def edit_setting_bool_false(self, button, interaction):
        """
        This is the function that is called when the user presses the edit setting button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await edit_current_setting_bool(self, interaction, False, self.desired_lang)

    @discord.ui.select(placeholder="Choose a new setting", options=[discord.SelectOption(label="placeholder")], row=4)
    async def edit_setting_select(self, select, interaction):
        """
        This is the function that is called when the user selects a setting.

        Args:
            select: The select that the user selected.
            interaction: The interaction that the user did.
        """
        await edit_current_setting_select(self, select, interaction, self.desired_lang)


class MainPageProfileSettingsView(discord.ui.View):
    """
    This is the view for the profile settings page.
    """

    def __init__(self, user_document, client, page, ctx, settings, pass_message=None, desired_lang=None):
        super().__init__(timeout=480.0)

        if pass_message is not None:
            self.message = pass_message

        settings_per_page = client.config["profile_settings"]["settings_per_page"]
        self.user_document = user_document
        self.client = client
        self.page = page
        self.ctx = ctx
        self.settings_per_page = settings_per_page
        self.settings = settings
        self.interaction_check_done = {}
        self.desired_lang = desired_lang

        current_slice = get_current_settings_slice(page, settings_per_page, settings)
        settings_options = generate_settings_view_options(self.client, current_slice, self.desired_lang)

        selected_profile = user_document["global"]["selected_profile"]

        self.children[0].options = generate_profile_select_options(self.client, selected_profile, user_document,
                                                                   desired_lang)
        self.children[1].options = settings_options
        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1].placeholder = stw.I18n.get('settings.view.select.setting.placeholder', self.desired_lang)
        self.children[2].label = stw.I18n.get('generic.view.button.previous', self.desired_lang)
        self.children[3].label = stw.I18n.get('generic.view.button.next', self.desired_lang)

        self.children[2:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[2:]))

        if math.ceil(len(self.client.default_settings) / settings_per_page) == 1:
            self.children[2].disabled = True
            self.children[3].disabled = True
        else:
            self.children[2].disabled = False
            self.children[3].disabled = False
        self.timed_out = False

    async def on_timeout(self):
        """
        This is the function that is called when the view times out.
        """
        self.timed_out = True
        await settings_view_timeout(self, desired_lang=self.desired_lang)

    async def interaction_check(self, interaction):
        """
        This is the function that is called when the user interacts with the view.

        Args:
            interaction: The interaction that the user did.

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "settings") & await timeout_check_processing(self,
                                                                                                                self.client,
                                                                                                                interaction)

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        """
        This is the function that is called when the user selects a profile.

        Args:
            select: The select that the user selected.
            interaction: The interaction that the user did.
        """
        await settings_profile_select_change(self, select, interaction, self.desired_lang)

    @discord.ui.select(
        placeholder="Select a setting to view/change here",
        min_values=1,
        max_values=1,  # i thought you were afk but it was just my theme :3
        options=[],  # :3
    )
    async def settings_select(self, select, interaction):
        """
        This is the function that is called when the user selects a setting.

        Args:
            select: The select that the user selected.
            interaction: The interaction that the user did.
        """
        await settings_profile_setting_select(self, select, interaction, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="left_icon", row=2, label="Previous Page")
    async def previous_page(self, button, interaction):
        """
        This is the function that is called when the user presses the previous page button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await shift_page(self, interaction, -1, self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="right_icon", row=2, label="Next Page")
    async def next_page(self, button, interaction):
        """
        This is the function that is called when the user presses the next page button.

        Args:
            button: The button that the user pressed.
            interaction: The interaction that the user did.
        """
        await shift_page(self, interaction, 1, self.desired_lang)

def get_setting_type(setting, client):
    setting_info = client.default_settings[setting]
    setting_type = str(type(setting_info["default"]).__name__)

    if setting_info.get("options", None) is not None:
        return "select"
    elif setting_type == "bool":
        return "bool"
    else:
        return "modal"

async def add_field_to_page_embed(page_embed, setting, client, profile, desired_lang):
    """
    This function adds a field to the page embed.

    Args:
        page_embed: The embed to add the field to.
        setting: The setting to add to the embed.
        client: The client.
        profile: The profile.
        desired_lang: The desired language.

    Returns:
        discord.Embed: The embed with the field added.
    """
    setting_info = client.default_settings[setting]

    if setting == "language":
        try:
            current_value = f"{profile['settings'][setting]} " \
                            f"- {stw.I18n.get('lang.{0}'.format(profile['settings'][setting]), 'en')} " \
                            f"({client.config['valid_locales'][profile['settings'][setting]][1]})"
        except:
            try:
                current_value = profile['settings'][setting]
            except:
                try:
                    current_value = stw.I18n.get(f'lang.{setting_info["default"]}', desired_lang)
                except:
                    current_value = stw.I18n.get('settings.currentvalue.error', desired_lang)
    elif setting_info.get('options', None) != None:
        try:
            current_value = stw.I18n.get(setting_info['options'][profile['settings'][setting]]['name'], desired_lang)
        except:
            try:
                current_value = stw.I18n.get(setting_info['options'][profile['settings'][setting_info['default']]]['name'], desired_lang)
            except:
                current_value = stw.I18n.get('settings.currentvalue.error', desired_lang)
    else:
        try:
            if profile['settings'][setting] is True:
                current_value = stw.I18n.get('generic.enabled', desired_lang)
            elif profile['settings'][setting] is False:
                current_value = stw.I18n.get('generic.disabled', desired_lang)
            else:
                current_value = profile['settings'][setting]
        except:
            try:
                current_value = setting_info["default"]
            except:
                current_value = stw.I18n.get('settings.currentvalue.error', desired_lang)
    try:
        current_value = stw.I18n.fmt_num(int(current_value), desired_lang)
    except:
        pass
    page_embed.fields[0].value += f"""\n\n# {stw.I18n.get(setting_info['localised_name'], desired_lang)}\n> {current_value}\n{stw.I18n.get(setting_info['short_description'], desired_lang)}"""
    return page_embed


def generate_settings_view_options(client, current_slice, desired_lang, selected_setting=None):
    """
    This function generates the options for the settings select.

    Args:
        client: The client.
        current_slice: The current slice of settings.
        desired_lang: The desired language.
        selected_setting: The selected setting.

    Returns:
        list: The list of options.
    """
    select_options = []

    for index, setting_option in enumerate(current_slice):
        emoji_key = client.default_settings[setting_option]["emoji"]
        logger.debug(f"Current slice: {current_slice}")
        select_options.append(discord.SelectOption(
            label=stw.truncate(stw.I18n.get(client.default_settings[setting_option]["localised_name"], desired_lang)),
            description=stw.truncate(stw.I18n.get(client.default_settings[setting_option]["short_description"], desired_lang)) if '.' not in stw.I18n.get(client.default_settings[setting_option]["short_description"], desired_lang) else None,
            value=setting_option + str(index),
            emoji=client.config["emojis"][emoji_key],
            default=True if selected_setting == setting_option else False))

    return select_options


def get_current_settings_slice(page_number, settings_per_page, settings):
    """
    This function gets the current settings slice.

    Args:
        page_number: The page number.
        settings_per_page: The settings per page.
        settings: The settings.

    Returns:
        list: The current settings slice.
    """
    shift = settings_per_page * max(0, page_number - 1)
    return settings[(0 + shift):(settings_per_page + shift)]


async def main_page(page_number, client, ctx, user_profile, settings, desired_lang):
    """
    This function generates the main page.

    Args:
        page_number: The page number.
        client: The client.
        ctx: The context.
        user_profile: The user profile.
        settings: The settings.
        desired_lang: The desired language.

    Returns:
        discord.Embed: The embed.
    """
    embed_colour = client.colours["profile_lavendar"]

    selected_profile = user_profile["global"]["selected_profile"]

    # https://en.wikipedia.org/wiki/Tim_Sweeney_(game_developer)

    selected_profile_data = user_profile["profiles"][str(selected_profile)]
    settings_per_page = client.config["profile_settings"]["settings_per_page"]

    pages = math.ceil(len(client.default_settings) / settings_per_page)
    current_slice = get_current_settings_slice(page_number, settings_per_page, settings)

    page_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('settings.embed.title', desired_lang), "settings"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, selected_profile)}\n"
                     f"```{selected_profile_data['friendly_name']}```\u200b"),
        color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "settings_cog")
    page_embed = await stw.add_requested_footer(ctx, page_embed, desired_lang)

    page_embed.add_field(name="",
                         value=f"{stw.I18n.get('settings.pagination.showing', desired_lang, page_number, pages)}"
                               f"```md", inline=False)
    for setting in current_slice:
        page_embed = await add_field_to_page_embed(page_embed, setting, client, selected_profile_data, desired_lang)

    page_embed.fields[0].value += "```"

    return page_embed


async def sub_setting_page(setting, client, ctx, user_profile, desired_lang):
    """
    This function generates the sub setting page.

    Args:
        setting: The setting.
        client: The client.
        ctx: The context.
        user_profile: The user profile.
        desired_lang: The desired language.

    Returns:
        discord.Embed: The embed.
    """
    setting_info = client.default_settings[setting]

    embed_colour = client.colours["profile_lavendar"]

    selected_profile = user_profile["global"]["selected_profile"]
    selected_profile_data = user_profile["profiles"][str(selected_profile)]

    page_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('settings.embed.title', desired_lang), "settings"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, selected_profile)}\n"
                     f"```{selected_profile_data['friendly_name']}```\u200b"),
        color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "settings_cog")
    page_embed = await stw.add_requested_footer(ctx, page_embed, desired_lang)

    if setting == "language":
        try:
            current_value = f"{selected_profile_data['settings'][setting]} " \
                            f"- {stw.I18n.get('lang.{0}'.format(selected_profile_data['settings'][setting]), 'en')} " \
                            f"({client.config['valid_locales'][selected_profile_data['settings'][setting]][1]})"
        except:
            current_value = selected_profile_data['settings'][setting]
    elif setting_info.get('options', None) != None:
        try:
            current_value = stw.I18n.get(setting_info['options'][selected_profile_data['settings'][setting]]['name'],
                                         desired_lang)
        except:
            current_value = stw.I18n.get('settings.currentvalue.error', desired_lang)
    else:
        try:
            if selected_profile_data['settings'][setting] is True:
                current_value = stw.I18n.get('generic.enabled', desired_lang)
            elif selected_profile_data['settings'][setting] is False:
                current_value = stw.I18n.get('generic.disabled', desired_lang)
            else:
                current_value = selected_profile_data['settings'][setting]
        except:
            current_value = setting_info['default']
    try:
        current_value = stw.I18n.fmt_num(int(current_value), desired_lang)
    except:
        pass
    try:
        setting_name = f"[{stw.I18n.get(setting_info['localised_name'], desired_lang)}]({setting_info['url']})"
    except:
        setting_name = stw.I18n.get(setting_info['localised_name'], desired_lang)
    if isinstance(setting_info['default'], bool):
        page_embed.add_field(
            name="",
            value=f"**{stw.I18n.get('settings.select1', desired_lang, client.config['emojis'][setting_info['emoji']], setting_name)}**"
                  f"```asciidoc\n== {stw.I18n.get(setting_info['localised_name'], desired_lang)}\n\n{stw.I18n.get('settings.currentvalue', desired_lang)}:: {current_value}\n\n{stw.I18n.get(setting_info['long_description'], desired_lang)}\n\n\n{stw.I18n.get('settings.requirement', desired_lang)}:: {stw.I18n.get('settings.type.bool', desired_lang)}```",
            inline=False)
    else:
        try:
            requirement_string = stw.I18n.get(setting_info['req_string'], desired_lang)
            page_embed.add_field(
                name="",
                value=f"**{stw.I18n.get('settings.select1', desired_lang, client.config['emojis'][setting_info['emoji']], setting_name)}**"
                      f"```asciidoc\n== {stw.I18n.get(setting_info['localised_name'], desired_lang)}\n\n{stw.I18n.get('settings.currentvalue', desired_lang)}:: {current_value}\n\n{stw.I18n.get(setting_info['long_description'], desired_lang)}\n\n\n{stw.I18n.get('settings.type', desired_lang)}:: {stw.I18n.get('settings.type.{}'.format(type(setting_info['default']).__name__), desired_lang)}\n{stw.I18n.get('settings.requirement', desired_lang)}:: {requirement_string}```",
                inline=False)
        except:
            page_embed.add_field(
                name="",
                value=f"**{stw.I18n.get('settings.select1', desired_lang, client.config['emojis'][setting_info['emoji']], setting_name)}**"
                      f"```asciidoc\n== {stw.I18n.get(setting_info['localised_name'], desired_lang)}\n\n{stw.I18n.get('settings.currentvalue', desired_lang)}:: {current_value}\n\n{stw.I18n.get(setting_info['long_description'], desired_lang)}```",
                inline=False)

    return page_embed


async def map_settings_aliases(client):
    """
    This function maps the settings aliases.

    Args:
        client: The client.

    Returns:
        dict: The settings aliases.
    """
    default_settings = client.default_settings
    setting_map = {}

    for setting in default_settings:
        setting_info = default_settings[setting]
        setting_map[setting] = setting

        for alias in setting_info["aliases"]:
            setting_map[alias] = setting

    return setting_map


async def default_page_profile_settings(client, ctx, user_profile, settings, message, desired_lang):
    """
    This function generates the default page for the profile settings.

    Args:
        client: The client.
        ctx: The context.
        user_profile: The user profile.
        settings: The settings.
        message: The message.
        desired_lang: The desired language.
    """
    page = client.config["profile_settings"]["default_settings_page"]
    main_page_embed = await main_page(page, client, ctx, user_profile, settings, desired_lang)
    main_page_embed.fields[0].value += message

    settings_view = MainPageProfileSettingsView(user_profile, client, page, ctx, settings, desired_lang=desired_lang)
    await active_view(client, ctx.author.id, settings_view)
    message = await stw.slash_send_embed(ctx, client, embeds=main_page_embed, view=settings_view)
    settings_view.message = message
    return message


async def no_profiles_page(client, ctx, desired_lang):
    """
    This is the function that is called when the user has no profiles

    Args:
        client: The client
        ctx: The context
        desired_lang: The desired language

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]

    no_profiles_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('settings.embed.title', desired_lang), "settings"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('settings.noprofile1', desired_lang)}\n"
                     f"```{stw.I18n.get('settings.noprofile2', desired_lang)}```\u200b\n"),
        color=embed_colour)
    no_profiles_embed = await stw.set_thumbnail(client, no_profiles_embed, "settings_cog")
    no_profiles_embed = await stw.add_requested_footer(ctx, no_profiles_embed, desired_lang)

    return no_profiles_embed


async def settings_command(client, ctx, setting=None, value=None, profile=None):
    """
    This function is the settings command.

    Args:
        client: The client.
        ctx: The context.
        setting: The setting.
        profile: The profile.
        value: The value.

    Returns:
        discord.Embed: The embed.
    """

    desired_lang = await stw.I18n.get_desired_lang(client, ctx)

    settings = client.settings_choices
    settings_per_page = 5

    user_profile = await get_user_document(ctx, client, ctx.author.id, desired_lang=desired_lang)
    user_snowflake = user_profile["user_snowflake"]

    # Check if user actually has a profile we can get the settings of :)
    try:
        user_profile["profiles"]["0"]
    except:
        embed = await no_profiles_page(client, ctx, desired_lang)
        return await stw.slash_send_embed(ctx, client, embeds=embed)

    if setting is not None or profile is not None or value is not None:
        if profile is None:
            profile = user_profile["global"]["selected_profile"]
        setting_map = await map_settings_aliases(client)

        happy_message = "\u200b\n*"
        if setting in list(setting_map.keys()):
            settings_per_page = client.config["profile_settings"]["settings_per_page"]
            setting = setting_map[setting]
            happy_message += stw.I18n.get('settings.change2', desired_lang, setting.replace('_', ' ').capitalize())
        else:
            setting = False

        if str(profile) in list(user_profile["profiles"].keys()):
            new_profile_selected = int(profile)
            user_profile["global"]["selected_profile"] = new_profile_selected
            client.processing_queue[user_snowflake] = True
            await replace_user_document(client, user_profile)
            del client.processing_queue[user_snowflake]
            happy_message += stw.I18n.get('settings.change2.1', desired_lang, profile)
        elif profile is not None:
            profile = False

        if value is not None and value is not False and profile is not None and profile is not False and setting is not None and setting is not False:
            if isinstance(client.default_settings[setting]['default'], bool):
                check_function = check_bool
            else:
                try:
                    check_function = globals()[client.default_settings[setting]['check_function']]
                except:
                    check_function = globals()['check_default']

            check_result = check_function(client, ctx, value)

            if check_result[1] is not False:
                selected_profile = user_profile["global"]["selected_profile"]

                if isinstance(client.default_settings[setting]['default'], bool):
                    user_profile["profiles"][str(selected_profile)]["settings"][setting] = boolean_string_representation[
                        value.lower()]
                else:
                    user_profile["profiles"][str(selected_profile)]["settings"][setting] = check_result[0]
                    if setting == "language" and stw.I18n.is_lang(user_profile["profiles"][str(selected_profile)]["settings"]["language"]):
                        desired_lang = user_profile["profiles"][str(selected_profile)]["settings"]["language"]
                    if setting == "language" and check_result[0] == "auto":
                        try:
                            interaction_language = ctx.interaction.locale
                            if interaction_language.lower() in ["en-us", "en-gb", "en"]:
                                interaction_language = "en"
                            elif interaction_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn",
                                                                  "zh-hans-sg"]:
                                interaction_language = "zh-CHS"
                            elif interaction_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant",
                                                                  "zh-hant-tw",
                                                                  "zh-hant-hk", "zh-hant-mo"]:
                                interaction_language = "zh-CHT"
                            if not stw.I18n.is_lang(interaction_language):
                                interaction_language = None
                        except:
                            interaction_language = None
                        try:
                            guild_language = ctx.guild.preferred_locale
                            if guild_language.lower() in ["en-us", "en-gb", "en"]:
                                guild_language = "en"
                            elif guild_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn",
                                                            "zh-hans-sg"]:
                                guild_language = "zh-CHS"
                            elif guild_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant",
                                                            "zh-hant-tw",
                                                            "zh-hant-hk", "zh-hant-mo"]:
                                guild_language = "zh-CHT"
                            if not stw.I18n.is_lang(guild_language):
                                guild_language = None
                        except:
                            guild_language = None
                        desired_lang = interaction_language or guild_language or "en"
                client.processing_queue[user_snowflake] = True
                await replace_user_document(client, user_profile)
                del client.processing_queue[user_snowflake]

            if check_result[1] is not False:
                happy_message += stw.I18n.get('settings.change2.2', desired_lang, str(check_result[0]))
            else:
                value = False

            if value is not False:
                embed = await sub_setting_page(setting, client, ctx, user_profile, desired_lang)

                # may be referenced before assignment
                selected_setting_index = (settings.index(setting) % settings_per_page) - 1
                page = math.ceil(settings.index(setting) / settings_per_page)

                sub_view = SettingProfileSettingsSettingViewOfSettingSettings(setting, user_profile,
                                                                              client, page, ctx,
                                                                              settings,
                                                                              selected_setting_index,
                                                                              desired_lang=desired_lang)
                await active_view(client, ctx.author.id, sub_view)

                embed.fields[0].value += happy_message + "*\n\u200b\n"
                message = await stw.slash_send_embed(ctx, client, embeds=embed, view=sub_view)
                sub_view.message = message
                return message

        elif value is not None:
            value = False

        list_of_potential_nones = [setting, profile, value]
        associated_error = [stw.I18n.get('settings.error.invalid.setting', desired_lang),
                            stw.I18n.get('settings.error.invalid.profile', desired_lang),
                            stw.I18n.get('settings.error.invalid.value', desired_lang)]
        associated_missing = [stw.I18n.get('settings.error.missing.setting', desired_lang),
                              stw.I18n.get('settings.error.missing.profile', desired_lang),
                              stw.I18n.get('settings.error.missing.value', desired_lang)]
        base_error_message = f"\u200b\n{stw.I18n.get('settings.error.base', desired_lang)}"

        for index, missing_or_error in enumerate(list_of_potential_nones):

            if missing_or_error is False:
                base_error_message += f" {associated_error[index]}"
            elif missing_or_error is None:
                base_error_message += f" {associated_missing[index]}"
            if not missing_or_error or not missing_or_error:
                if index < len(list_of_potential_nones) - 1:
                    base_error_message += ","

        base_error_message += "*\n\u200b\n"
        base_error_message.replace(":,", ":")
        base_error_message.replace(",,", ",")  # TODO: fix this, perhaps use .join?

        if setting is not None and setting is not False:
            embed = await sub_setting_page(setting, client, ctx, user_profile, desired_lang)
            # may be referenced before assignment
            selected_setting_index = (settings.index(setting) % settings_per_page) - 1
            page = math.floor(settings.index(setting) / settings_per_page) + 1

            sub_view = SettingProfileSettingsSettingViewOfSettingSettings(setting, user_profile,
                                                                          client, page, ctx,
                                                                          settings,
                                                                          selected_setting_index,
                                                                          desired_lang=desired_lang)
            await active_view(client, ctx.author.id, sub_view)

            embed.fields[0].value += base_error_message
            message = await stw.slash_send_embed(ctx, client, embeds=embed, view=sub_view)
            sub_view.message = message
            return message
        else:
            return await default_page_profile_settings(client, ctx, user_profile, settings, base_error_message, desired_lang)

    await default_page_profile_settings(client, ctx, user_profile, settings,
                                        f"\u200b\n*{stw.random_waiting_message(client, desired_lang)}*\n\u200b\n",
                                        desired_lang)
    return


# cog for the profile related settings & Disclosure - You & Me (Flume Remix)
class ProfileSettings(ext.Cog):
    """
    This class is the profile settings cog.
    """

    def __init__(self, client):
        self.client = client

    async def autocomplete_settings(self, actx: discord.AutocompleteContext):
        """
        This function is the autocomplete for the settings command.

        Args:
            actx: The autocomplete context. (unused)

        Returns:
            list: The list of settings.
        """
        return self.client.settings_choices

    @ext.slash_command(name='settings', name_localization=stw.I18n.construct_slash_dict('settings.slash.name'),
                       description='View/Change settings for STW Daily on a per-profile basis',
                       description_localization=stw.I18n.construct_slash_dict('settings.slash.description'),
                       guild_ids=stw.guild_ids)
    async def slash_settings(self, ctx: discord.ApplicationContext,
                             setting: Option(description="The name of the setting to change",
                                             description_localizations=stw.I18n.construct_slash_dict('settings.meta.args.setting.description'),
                                             name_localizations=stw.I18n.construct_slash_dict('settings.meta.args.setting'),
                                             autocomplete=autocomplete_settings) = None,
                             value: Option(description="The value to change this setting to",
                                           description_localizations=stw.I18n.construct_slash_dict('settings.meta.args.value.description'),
                                           name_localizations=stw.I18n.construct_slash_dict('settings.meta.args.value')) = None,  # TODO: autocomplete if possible
                             profile: Option(int, "The profile you want to change this setting on",
                                             description_localizations=stw.I18n.construct_slash_dict('settings.meta.args.profile.description'),
                                             name_localizations=stw.I18n.construct_slash_dict('profile.meta.args.profile')) = None  # TODO: autocomplete / choice this
                             ):
        """
        This function is the slash command for the settings command.

        Args:
            ctx: The context of the slash command.
            setting: The setting to change.
            profile: The profile to change the setting on.
            value: The value to change the setting to.
        """
        await command_counter(self.client, ctx.author.id)
        await settings_command(self.client, ctx, setting, value, profile)

    @ext.command(name='settings',
                 aliases=['ettings', 'sttings', 'setings', 'settngs', 'settigs', 'settins', 'setting', 'ssettings',
                          'seettings', 'setttings', 'settiings', 'settinngs', 'settinggs', 'settingss', 'esttings',
                          'stetings', 'setitngs', 'settnigs', 'settigns', 'settinsg', 'aettings', 'wettings',
                          'eettings', 'dettings', 'xettings', 'zettings', 'swttings', 's3ttings', 's4ttings',
                          'srttings', 'sfttings', 'sdttings', 'ssttings', 'sertings', 'se5tings', 'se6tings',
                          'seytings', 'sehtings', 'segtings', 'seftings', 'setrings', 'set5ings', 'set6ings',
                          'setyings', 'sethings', 'setgings', 'setfings', 'settungs', 'sett8ngs', 'sett9ngs',
                          'settongs', 'settlngs', 'settkngs', 'settjngs', 'settibgs', 'settihgs', 'settijgs',
                          'settimgs', 'settinfs', 'settints', 'settinys', 'settinhs', 'settinbs', 'settinvs',
                          'settinga', 'settingw', 'settinge', 'settingd', 'settingx', 'settingz', 'asettings',
                          'saettings', 'wsettings', 'swettings', 'esettings', 'dsettings', 'sdettings', 'xsettings',
                          'sxettings', 'zsettings', 'szettings', 'sewttings', 's3ettings', 'se3ttings', 's4ettings',
                          'se4ttings', 'srettings', 'serttings', 'sfettings', 'sefttings', 'sedttings', 'sesttings',
                          'setrtings', 'se5ttings', 'set5tings', 'se6ttings', 'set6tings', 'seyttings', 'setytings',
                          'sehttings', 'sethtings', 'segttings', 'setgtings', 'setftings', 'settrings', 'sett5ings',
                          'sett6ings', 'settyings', 'setthings', 'settgings', 'settfings', 'settuings', 'settiungs',
                          'sett8ings', 'setti8ngs', 'sett9ings', 'setti9ngs', 'settoings', 'settiongs', 'settlings',
                          'settilngs', 'settkings', 'settikngs', 'settjings', 'settijngs', 'settibngs', 'settinbgs',
                          'settihngs', 'settinhgs', 'settinjgs', 'settimngs', 'settinmgs', 'settinfgs', 'settingfs',
                          'settintgs', 'settingts', 'settinygs', 'settingys', 'settinghs', 'settingbs', 'settinvgs',
                          'settingvs', 'settingas', 'settingsa', 'settingws', 'settingsw', 'settinges', 'settingse',
                          'settingds', 'settingsd', 'settingxs', 'settingsx', 'settingzs', 'settingsz', 'ptions',
                          'otions', 'opions', 'optons', 'optins', 'optios', 'option', 'ooptions', 'opptions',
                          'opttions', 'optiions', 'optioons', 'optionns', 'optionss', 'potions', 'otpions', 'opitons',
                          'optoins', 'optinos', 'optiosn', 'iptions', '9ptions', '0ptions', 'pptions', 'lptions',
                          'kptions', 'ootions', 'o0tions', 'oltions', 'oprions', 'op5ions', 'op6ions', 'opyions',
                          'ophions', 'opgions', 'opfions', 'optuons', 'opt8ons', 'opt9ons', 'optoons', 'optlons',
                          'optkons', 'optjons', 'optiins', 'opti9ns', 'opti0ns', 'optipns', 'optilns', 'optikns',
                          'optiobs', 'optiohs', 'optiojs', 'optioms', 'optiona', 'optionw', 'optione', 'optiond',
                          'optionx', 'optionz', 'ioptions', 'oiptions', '9options', 'o9ptions', '0options', 'o0ptions',
                          'poptions', 'loptions', 'olptions', 'koptions', 'okptions', 'opotions', 'op0tions',
                          'opltions', 'oprtions', 'optrions', 'op5tions', 'opt5ions', 'op6tions', 'opt6ions',
                          'opytions', 'optyions', 'ophtions', 'opthions', 'opgtions', 'optgions', 'opftions',
                          'optfions', 'optuions', 'optiuons', 'opt8ions', 'opti8ons', 'opt9ions', 'opti9ons',
                          'optoions', 'optlions', 'optilons', 'optkions', 'optikons', 'optjions', 'optijons',
                          'optioins', 'optio9ns', 'opti0ons', 'optio0ns', 'optipons', 'optiopns', 'optiolns',
                          'optiokns', 'optiobns', 'optionbs', 'optiohns', 'optionhs', 'optiojns', 'optionjs',
                          'optiomns', 'optionms', 'optionas', 'optionsa', 'optionws', 'optionsw', 'optiones',
                          'optionse', 'optionds', 'optionsd', 'optionxs', 'optionsx', 'optionzs', 'optionsz',
                          'references', 'peferences', 'prferences', 'preerences', 'prefrences', 'prefeences',
                          'prefernces', 'prefereces', 'preferenes', 'preferencs', 'preference', 'ppreferences',
                          'prreferences', 'preeferences', 'prefferences', 'prefeerences', 'preferrences',
                          'prefereences', 'preferennces', 'preferencces', 'preferencees', 'preferencess', 'rpeferences',
                          'perferences', 'prfeerences', 'preefrences', 'prefreences', 'prefeernces', 'preferneces',
                          'preferecnes', 'preferenecs', 'preferencse', 'oreferences', '0references', 'lreferences',
                          'peeferences', 'p4eferences', 'p5eferences', 'pteferences', 'pgeferences', 'pfeferences',
                          'pdeferences', 'prwferences', 'pr3ferences', 'pr4ferences', 'prrferences', 'prfferences',
                          'prdferences', 'prsferences', 'prederences', 'prererences', 'preterences', 'pregerences',
                          'preverences', 'precerences', 'prefwrences', 'pref3rences', 'pref4rences', 'prefrrences',
                          'preffrences', 'prefdrences', 'prefsrences', 'prefeeences', 'prefe4ences', 'prefe5ences',
                          'prefetences', 'prefegences', 'prefefences', 'prefedences', 'preferwnces', 'prefer3nces',
                          'prefer4nces', 'preferrnces', 'preferfnces', 'preferdnces', 'prefersnces', 'preferebces',
                          'preferehces', 'preferejces', 'preferemces', 'preferenxes', 'preferendes', 'preferenfes',
                          'preferenves', 'preferencws', 'preferenc3s', 'preferenc4s', 'preferencrs', 'preferencfs',
                          'preferencds', 'preferencss', 'preferencea', 'preferencew', 'preferencee', 'preferenced',
                          'preferencex', 'preferencez', 'opreferences', 'poreferences', '0preferences', 'p0references',
                          'lpreferences', 'plreferences', 'pereferences', 'p4references', 'pr4eferences',
                          'p5references', 'pr5eferences', 'ptreferences', 'prteferences', 'pgreferences',
                          'prgeferences', 'pfreferences', 'prfeferences', 'pdreferences', 'prdeferences',
                          'prweferences', 'prewferences', 'pr3eferences', 'pre3ferences', 'pre4ferences',
                          'prerferences', 'predferences', 'prseferences', 'presferences', 'prefderences',
                          'prefrerences', 'pretferences', 'prefterences', 'pregferences', 'prefgerences',
                          'prevferences', 'prefverences', 'precferences', 'prefcerences', 'prefwerences',
                          'prefewrences', 'pref3erences', 'prefe3rences', 'pref4erences', 'prefe4rences',
                          'prefefrences', 'prefedrences', 'prefserences', 'prefesrences', 'prefer4ences',
                          'prefe5rences', 'prefer5ences', 'prefetrences', 'prefertences', 'prefegrences',
                          'prefergences', 'preferfences', 'preferdences', 'preferwences', 'preferewnces',
                          'prefer3ences', 'prefere3nces', 'prefere4nces', 'preferernces', 'preferefnces',
                          'preferednces', 'prefersences', 'preferesnces', 'preferebnces', 'preferenbces',
                          'preferehnces', 'preferenhces', 'preferejnces', 'preferenjces', 'preferemnces',
                          'preferenmces', 'preferenxces', 'preferencxes', 'preferendces', 'preferencdes',
                          'preferenfces', 'preferencfes', 'preferenvces', 'preferencves', 'preferencwes',
                          'preferencews', 'preferenc3es', 'preference3s', 'preferenc4es', 'preference4s',
                          'preferencres', 'preferencers', 'preferencefs', 'preferenceds', 'preferencses',
                          'preferenceas', 'preferencesa', 'preferencesw', 'preferencese', 'preferencesd',
                          'preferencexs', 'preferencesx', 'preferencezs', 'preferencesz', 'etting', 'stting', 'seting',
                          'settng', 'settig', 'settin', 'ssetting', 'seetting', 'settting', 'settiing', 'settinng',
                          'settingg', 'estting', 'steting', 'setitng', 'settnig', 'settign', 'aetting', 'wetting',
                          'eetting', 'detting', 'xetting', 'zetting', 'swtting', 's3tting', 's4tting', 'srtting',
                          'sftting', 'sdtting', 'sstting', 'serting', 'se5ting', 'se6ting', 'seyting', 'sehting',
                          'segting', 'sefting', 'setring', 'set5ing', 'set6ing', 'setying', 'sething', 'setging',
                          'setfing', 'settung', 'sett8ng', 'sett9ng', 'settong', 'settlng', 'settkng', 'settjng',
                          'settibg', 'settihg', 'settijg', 'settimg', 'settinf', 'settint', 'settiny', 'settinh',
                          'settinb', 'settinv', 'asetting', 'saetting', 'wsetting', 'swetting', 'esetting', 'dsetting',
                          'sdetting', 'xsetting', 'sxetting', 'zsetting', 'szetting', 'sewtting', 's3etting',
                          'se3tting', 's4etting', 'se4tting', 'sretting', 'sertting', 'sfetting', 'seftting',
                          'sedtting', 'sestting', 'setrting', 'se5tting', 'set5ting', 'se6tting', 'set6ting',
                          'seytting', 'setyting', 'sehtting', 'sethting', 'segtting', 'setgting', 'setfting',
                          'settring', 'sett5ing', 'sett6ing', 'settying', 'setthing', 'settging', 'settfing',
                          'settuing', 'settiung', 'sett8ing', 'setti8ng', 'sett9ing', 'setti9ng', 'settoing',
                          'settiong', 'settling', 'settilng', 'settking', 'settikng', 'settjing', 'settijng',
                          'settibng', 'settinbg', 'settihng', 'settinhg', 'settinjg', 'settimng', 'settinmg',
                          'settinfg', 'settingf', 'settintg', 'settingt', 'settinyg', 'settingy', 'settingh',
                          'settingb', 'settinvg', 'settingv', 'ption', 'otion', 'opion', 'opton', 'optin', 'optio',
                          'ooption', 'opption', 'opttion', 'optiion', 'optioon', 'optionn', 'potion', 'otpion',
                          'opiton', 'optoin', 'optino', 'iption', '9ption', '0ption', 'pption', 'lption', 'kption',
                          'ootion', 'o0tion', 'oltion', 'oprion', 'op5ion', 'op6ion', 'opyion', 'ophion', 'opgion',
                          'opfion', 'optuon', 'opt8on', 'opt9on', 'optoon', 'optlon', 'optkon', 'optjon', 'optiin',
                          'opti9n', 'opti0n', 'optipn', 'optiln', 'optikn', 'optiob', 'optioh', 'optioj', 'optiom',
                          'ioption', 'oiption', '9option', 'o9ption', '0option', 'o0ption', 'poption', 'loption',
                          'olption', 'koption', 'okption', 'opotion', 'op0tion', 'opltion', 'oprtion', 'optrion',
                          'op5tion', 'opt5ion', 'op6tion', 'opt6ion', 'opytion', 'optyion', 'ophtion', 'opthion',
                          'opgtion', 'optgion', 'opftion', 'optfion', 'optuion', 'optiuon', 'opt8ion', 'opti8on',
                          'opt9ion', 'opti9on', 'optoion', 'optlion', 'optilon', 'optkion', 'optikon', 'optjion',
                          'optijon', 'optioin', 'optio9n', 'opti0on', 'optio0n', 'optipon', 'optiopn', 'optioln',
                          'optiokn', 'optiobn', 'optionb', 'optiohn', 'optionh', 'optiojn', 'optionj', 'optiomn',
                          'optionm', 'reference', 'peference', 'prference', 'preerence', 'prefrence', 'prefeence',
                          'prefernce', 'preferece', 'preferene', 'preferenc', 'ppreference', 'prreference',
                          'preeference', 'prefference', 'prefeerence', 'preferrence', 'prefereence', 'preferennce',
                          'preferencce', 'rpeference', 'perference', 'prfeerence', 'preefrence', 'prefreence',
                          'prefeernce', 'prefernece', 'preferecne', 'preferenec', 'oreference', '0reference',
                          'lreference', 'peeference', 'p4eference', 'p5eference', 'pteference', 'pgeference',
                          'pfeference', 'pdeference', 'prwference', 'pr3ference', 'pr4ference', 'prrference',
                          'prfference', 'prdference', 'prsference', 'prederence', 'prererence', 'preterence',
                          'pregerence', 'preverence', 'precerence', 'prefwrence', 'pref3rence', 'pref4rence',
                          'prefrrence', 'preffrence', 'prefdrence', 'prefsrence', 'prefeeence', 'prefe4ence',
                          'prefe5ence', 'prefetence', 'prefegence', 'prefefence', 'prefedence', 'preferwnce',
                          'prefer3nce', 'prefer4nce', 'preferrnce', 'preferfnce', 'preferdnce', 'prefersnce',
                          'preferebce', 'preferehce', 'preferejce', 'preferemce', 'preferenxe', 'preferende',
                          'preferenfe', 'preferenve', 'preferencw', 'preferenc3', 'preferenc4', 'preferencr',
                          'preferencf', 'preferencd', 'opreference', 'poreference', '0preference', 'p0reference',
                          'lpreference', 'plreference', 'pereference', 'p4reference', 'pr4eference', 'p5reference',
                          'pr5eference', 'ptreference', 'prteference', 'pgreference', 'prgeference', 'pfreference',
                          'prfeference', 'pdreference', 'prdeference', 'prweference', 'prewference', 'pr3eference',
                          'pre3ference', 'pre4ference', 'prerference', 'predference', 'prseference', 'presference',
                          'prefderence', 'prefrerence', 'pretference', 'prefterence', 'pregference', 'prefgerence',
                          'prevference', 'prefverence', 'precference', 'prefcerence', 'prefwerence', 'prefewrence',
                          'pref3erence', 'prefe3rence', 'pref4erence', 'prefe4rence', 'prefefrence', 'prefedrence',
                          'prefserence', 'prefesrence', 'prefer4ence', 'prefe5rence', 'prefer5ence', 'prefetrence',
                          'prefertence', 'prefegrence', 'prefergence', 'preferfence', 'preferdence', 'preferwence',
                          'preferewnce', 'prefer3ence', 'prefere3nce', 'prefere4nce', 'preferernce', 'preferefnce',
                          'preferednce', 'prefersence', 'preferesnce', 'preferebnce', 'preferenbce', 'preferehnce',
                          'preferenhce', 'preferejnce', 'preferenjce', 'preferemnce', 'preferenmce', 'preferenxce',
                          'preferencxe', 'preferendce', 'preferencde', 'preferenfce', 'preferencfe', 'preferenvce',
                          'preferencve', 'preferencwe', 'preferenc3e', 'preference3', 'preferenc4e', 'preference4',
                          'preferencre', 'preferencer', 'preferencef', 'preferences', '/settings', '/options',
                          '/preferences', '/setting', '/option', '/preference', 'set', '/set', 'opt', '/opt', 'pref',
                          '/pref', 'settomgs', '.settings', '.options', '.preferences', '.setting', '.option', 'sett',
                          'setin', 'setti', 'instellings', 'الإعدادات', 'настройки', 'সেটিংস', 'configuracions',
                          'nastavení', 'indstillinger', 'Einstellungen', 'Ρυθμίσεις', 'ajustes', 'seaded', 'تنظیمات',
                          'asetukset', 'paramètres', 'સેટિંગ્સ', 'saituna', 'הגדרות', 'समायोजन', 'postavkama',
                          'beállítások', 'setelan', 'impostazioni', '設定', '설정', 'nustatymus', 'iestatījumi',
                          'सेटिंग्ज', 'tetapan', 'instellingen', 'innstillinger', 'ਸੈਟਿੰਗਾਂ', 'ustawieniami',
                          'configurações', 'setări', 'настройками', 'nastavenie', 'подешавања', 'inställningar',
                          'mipangilio', 'அமைப்புகள்', 'సెట్టింగులు', 'การตั้งค่า', 'ayarlar', 'налаштуваннями',
                          'ترتیبات', 'cài đặt', '设置', '設置', 'keuze', 'settipngs', 'jettings', 'sgettings',
                          'settivgs', 'settinxs', 'usettings', 'settsings', 'hsettings', 'hettings', 'sattings',
                          'settingr', 'settirngs', 'setzings', 'setdtings', 'settiqngs', 'fsettings', 'settzngs',
                          'setjings', 'settingsk', 'settisgs', 'sextings', 'setvings', 'kettings', 'settingsg',
                          'settingcs', 'settinss', 'sentings', 'settiwngs', 'sevtings', 'settinos', 'settingsp',
                          'settpings', 'settinzgs', 'setoings', 'settikgs', 'settingms', 'sxttings', 'settingu',
                          'setktings', 'settvngs', 'settiwgs', 'svettings', 'sektings', 'setticngs', 'settinlgs',
                          'seetings', 'svttings', 'rsettings', 'settisngs', 'settinags', 'skettings', 'settixngs',
                          'settinks', 'sjttings', 'settingps', 'sebtings', 'syttings', 'setxings', 'setztings',
                          'shettings', 'settipgs', 'uettings', 'settnngs', 'settingqs', 'setbtings', 'setutings',
                          'settingsy', 'shttings', 'seqttings', 'settinqgs', 'settsngs', 'vsettings', 'settingus',
                          'setptings', 'senttings', 'stttings', 'setkings', 'settiegs', 'setatings', 'seotings',
                          'bettings', 'setaings', 'settiags', 'settangs', 'settiqgs', 'settinxgs', 'sottings',
                          'psettings', 'settinkgs', 'settingi', 'settinms', 'settincgs', 'settirgs', 'sgttings',
                          'sittings', 'settiigs', 'seteings', 'msettings', 'suettings', 'septings', 'settinjs',
                          'settinps', 'gsettings', 'settinas', 'iettings', 'settdngs', 'sebttings', 'settdings',
                          'seitings', 'settingsl', 'settiangs', 'settinds', 'seattings', 'settingj', 'selttings',
                          'settines', 'settingsh', 'tettings', 'settiygs', 'yettings', 'setxtings', 'settigngs',
                          'osettings', 'setmings', 'sejttings', 'setvtings', 'sectings', 'settidgs', 'setthngs',
                          'settinus', 'septtings', 'spettings', 'settingm', 'settingso', 'setstings', 'settinegs',
                          'seltings', 'settizngs', 'settincs', 'smettings', 'sqettings', 'settitgs', 'setntings',
                          'setitings', 'seuttings', 'settingis', 'settaings', 'slttings', 'settingc', 'qettings',
                          'settingo', 'settiyngs', 'settinsgs', 'settiengs', 'pettings', 'settinns', 'settiogs',
                          'settinrgs', 'setetings', 'settgngs', 'rettings', 'settingl', 'seittings', 'setcings',
                          'settingn', 'jsettings', 'sezttings', 'spttings', 'settbings', 'settingq', 'setticgs',
                          'gettings', 'lsettings', 'settinis', 'snettings', 'szttings', 'sedtings', 'settinrs',
                          'settingsn', 'settwings', 'settingsi', 'settivngs', 'sevttings', 'tsettings', 'skttings',
                          'seqtings', 'settpngs', 'bsettings', 'settxngs', 'setqtings', 'settingk', 'settingjs',
                          'mettings', 'settfngs', 'setotings', 'settingos', 'settingsq', 'seatings', 'sejtings',
                          'setwtings', 'setttngs', 'settinzs', 'setqings', 'settinigs', 'setuings', 'setiings',
                          'settifngs', 'ysettings', 'sekttings', 'sestings', 'syettings', 'nettings', 'settingsm',
                          'settingsc', 'scttings', 'settiugs', 'settvings', 'setctings', 'seottings', 'seutings',
                          'scettings', 'settitngs', 'settilgs', 'suttings', 'settxings', 'ksettings', 'settnings',
                          'settingls', 'lettings', 'settingst', 'settyngs', 'settiggs', 'setltings', 'settcngs',
                          'settzings', 'settingp', 'settengs', 'setwings', 'isettings', 'sbttings', 'setpings',
                          'settwngs', 'vettings', 'setnings', 'settinws', 'secttings', 'sjettings', 'seztings',
                          'settingsu', 'settingsv', 'soettings', 'settinls', 'cettings', 'settingks', 'csettings',
                          'settqngs', 'setsings', 'oettings', 'settrngs', 'settinogs', 'semtings', 'setteings',
                          'setjtings', 'sewtings', 'setbings', 'qsettings', 'sqttings', 'settqings', 'settcings',
                          'siettings', 'settingns', 'settingsb', 'smttings', 'snttings', 'settindgs', 'settinqs',
                          'sexttings', 'slettings', 'settingrs', 'settinpgs', 'settingsf', 'stettings', 'settingsr',
                          'settinwgs', 'setlings', 'semttings', 'setmtings', 'settmngs', 'settidngs', 'settbngs',
                          'settingsj', 'settifgs', 'settinugs', 'sbettings', 'settixgs', 'setdings', 'settmings',
                          'settizgs', 'fettings', 'nsettings', 's2ttings', 's$ttings', 's#ttings', 's@ttings',
                          'se4tings', 'se$tings', 'se%tings', 'se^tings', 'set4ings', 'set$ings', 'set%ings',
                          'set^ings', 'sett7ngs', 'sett&ngs', 'sett*ngs', 'sett(ngs', 'setti,gs', 'setti<gs',
                          'oqptions', 'ostions', 'optiops', 'qptions', 'opztions', 'optimons', 'optivons', 'oetions',
                          'optiorns', 'moptions', 'oputions', 'opvtions', 'opoions', 'optwions', 'optionos', 'optiocns',
                          'zoptions', 'oztions', 'ovptions', 'aoptions', 'optiotns', 'options', 'optivns', 'otptions',
                          'opations', 'optionu', 'oktions', 'optionsn', 'jptions', 'outions', 'optionfs', 'opticns',
                          'optioks', 'optcions', 'optionsp', 'owptions', 'optiogs', 'optirns', 'optioens', 'optionsb',
                          'mptions', 'sptions', 'dptions', 'optionks', 'opntions', 'oftions', 'optieons', 'optionsv',
                          'opvions', 'opmtions', 'optionps', 'boptions', 'ogptions', 'optioqs', 'optizns', 'oations',
                          'optiods', 'optwons', 'hoptions', 'optioxns', 'optionsi', 'bptions', 'joptions', 'optionqs',
                          'coptions', 'optionq', 'omtions', 'optigns', 'optiors', 'ortions', 'oaptions', 'optgons',
                          'optzons', 'optyons', 'optinns', 'ojtions', 'optihons', 'optionl', 'optionsh', 'optionus',
                          'ovtions', 'orptions', 'optiong', 'optionp', 'optioys', 'optiols', 'optiyons', 'goptions',
                          'oxptions', 'optaons', 'optiouns', 'optioss', 'voptions', 'optnons', 'oqtions', 'optiony',
                          'optpons', 'optionc', 'optioyns', 'optionsr', 'optiosns', 'optifns', 'optnions', 'optaions',
                          'optionrs', 'ouptions', 'optiono', 'optirons', 'oxtions', 'omptions', 'optioans', 'optizons',
                          'ogtions', 'ottions', 'opcions', 'opiions', 'optiont', 'optiozns', 'oytions', 'optionvs',
                          'ocptions', 'optisons', 'optiofs', 'optxions', 'oppions', 'rptions', 'optbons', 'optiogns',
                          'opkions', 'opuions', 'optionsy', 'optionsm', 'optionsf', 'opbions', 'optzions', 'oyptions',
                          'opwtions', 'opetions', 'optmions', 'opdions', 'optxons', 'opjtions', 'zptions', 'doptions',
                          'oitions', 'optifons', 'optijns', 'optibns', 'gptions', 'optihns', 'optvions', 'optiots',
                          'eptions', 'opsions', 'optionys', 'yoptions', 'obtions', 'optinons', 'nptions', 'qoptions',
                          'optionv', 'ontions', 'vptions', 'optiwns', 'optidons', 'optcons', 'fptions', 'optiows',
                          'optionls', 'optsons', 'woptions', 'optiyns', 'optisns', 'optidns', 'cptions', 'opjions',
                          'roptions', 'optigons', 'uptions', 'optioqns', 'optioas', 'opctions', 'eoptions', 'opmions',
                          'opstions', 'osptions', 'optitns', 'optiuns', 'optimns', 'opqtions', 'optvons', 'optionts',
                          'opqions', 'ojptions', 'optiofns', 'ofptions', 'optiovs', 'oplions', 'optdions', 'wptions',
                          'opbtions', 'opxions', 'opitions', 'opdtions', 'onptions', 'octions', 'optiodns', 'optionsl',
                          'optqions', 'opaions', 'opthons', 'xptions', 'opwions', 'optiowns', 'optionr', 'uoptions',
                          'obptions', 'optioos', 'optians', 'optiwons', 'optioxs', 'optiozs', 'optionsk', 'optiocs',
                          'optioes', 'optdons', 'optrons', 'foptions', 'optfons', 'optioni', 'opxtions', 'odtions',
                          'opticons', 'optiens', 'optqons', 'optionf', 'optionsg', 'optmons', 'optiois', 'opeions',
                          'opteions', 'oeptions', 'optioncs', 'optibons', 'optionsq', 'xoptions', 'soptions', 'opttons',
                          'optpions', 'opzions', 'opteons', 'aptions', 'optiqons', 'opnions', 'ohtions', 'odptions',
                          'optsions', 'optionst', 'optionsc', 'yptions', 'optixns', 'optionso', 'optiongs', 'optixons',
                          'optiqns', 'optious', 'optionsj', 'owtions', 'ohptions', 'tptions', 'noptions', 'optionk',
                          'opktions', 'hptions', 'optionis', 'optionsu', 'optiaons', 'ozptions', 'optiovns', 'optitons',
                          'optbions', 'toptions', '8ptions', ';ptions', '*ptions', '(ptions', ')ptions', 'o9tions',
                          'o-tions', 'o[tions', 'o]tions', 'o;tions', 'o(tions', 'o)tions', 'o_tions', 'o=tions',
                          'o+tions', 'o{tions', 'o}tions', 'o:tions', 'op4ions', 'op$ions', 'op%ions', 'op^ions',
                          'opt7ons', 'opt&ons', 'opt*ons', 'opt(ons', 'opti8ns', 'opti;ns', 'opti*ns', 'opti(ns',
                          'opti)ns', 'optio,s', 'optio<s', 'stgns', 'stnsg', 'ttngs', 'stggs', 'stngls', 'sntngs',
                          'stngw', 'stjngs', 'ctngs', 'stnrgs', 'lstngs', 'snngs', 'stns', 'ystngs', 'xstngs', 'stlgs',
                          'stgs', 'stngsf', 'stng', 'stngsr', 'stnos', 'stnqs', 'ssngs', 'stngs', 'stugs', 'stsngs',
                          'stngsj', 'tsngs', 'vstngs', 'sngs', 'sptngs', 'sttngs', 'sntgs', 'dstngs', 'stngk', 'sutngs',
                          'tngs', 'setngs', 'stngse', 'stnas', 'stwngs', 'swngs', 'srngs', 'kstngs', 'hstngs', 'stnds',
                          'stngz', 'stngxs', 'stngu', 'stnhs', 'ltngs', 'htngs', 'stnis', 'stnga', 'sotngs', 'syngs',
                          'sytngs', 'sktngs', 'sungs', 'sjtngs', 'stmngs', 'stnhgs', 'satngs', 'stpngs', 'sdtngs',
                          'stngsb', 'stngsz', 'stongs', 'stcgs', 'stndgs', 'slngs', 'sangs', 'stngn', 'stnkgs', 'stnxs',
                          'stngo', 'stbgs', 'stnts', 'stnzgs', 'stnwgs', 'stings', 'stngsw', 'stdngs', 'stngsa',
                          'istngs', 'stnjs', 'stngy', 'svtngs', 'stangs', 'stfngs', 'stbngs', 'stngso', 'stngd',
                          'stygs', 'stngsc', 'stxgs', 'svngs', 'astngs', 'stnbgs', 'stnns', 'stnbs', 'nstngs', 'stnss',
                          'estngs', 'sltngs', 'stnes', 'stnks', 'stnxgs', 'stngrs', 'stnzs', 'stngt', 'utngs', 'ftngs',
                          'ktngs', 'ustngs', 'mstngs', 'stngqs', 'stngsy', 'shngs', 'stncgs', 'shtngs', 'rstngs',
                          'stngsx', 'itngs', 'stngst', 'stngg', 'stngss', 'stnjgs', 'stngts', 'qstngs',
                          'stnvs', 'stngis', 'stqngs', 'szngs', 'qtngs', 'stngj', 'stnigs', 'stvngs', 'stngsu', 'sdngs',
                          'stwgs', 'stncs', 'stnags', 'sbtngs', 'bstngs', 'sjngs', 'stngsk', 'stngps', 'ztngs',
                          'smtngs', 'stngsh', 'sxtngs', 'stqgs', 'stngvs', 'stnps', 'sgtngs', 'stngr', 'stngbs',
                          'sfngs', 'jtngs', 'stnws', 'stcngs', 'stngm', 'sttgs', 'stnggs', 'etngs', 'stngv', 'stnsgs',
                          'stogs', 'wstngs', 'stpgs', 'skngs', 'stngx', 'stngp', 'stngh', 'stnqgs', 'stngsn', 'stngsp',
                          'stvgs', 'sbngs', 'ntngs', 'sstngs', 'stngys', 'stngcs', 'stnms', 'stnys', 'zstngs', 'stkgs',
                          'gstngs', 'sengs', 'stngms', 'scngs', 'stkngs', 'stnugs', 'styngs', 'stnrs', 'ytngs',
                          'stnygs', 'stngns', 'sings', 'stngos', 'smngs', 'stnegs', 'stngi', 'strgs', 'stngc', 'stnus',
                          'stxngs', 'sztngs', 'stlngs', 'stntgs', 'swtngs', 'gtngs', 'stnge', 'mtngs', 'stngsg',
                          'vtngs', 'stzngs', 'stngjs', 'sgngs', 'stngks', 'tstngs', 'stngws', 'wtngs', 'sxngs', 'songs',
                          'sqngs', 'otngs', 'rtngs', 'stngzs', 'pstngs', 'stnfgs', 'stngl', 'stngfs', 'sthngs',
                          'sqtngs', 'stmgs', 'stngus', 'srtngs', 'stngds', 'stnogs', 'stnges', 'stnfs', 'dtngs',
                          'xtngs', 'stsgs', 'stigs', 'stngsl', 'sftngs', 'stngf', 'stngsm', 'sthgs', 'stnngs', 'fstngs',
                          'stungs', 'sctngs', 'jstngs', 'cstngs', 'stngq', 'stngsv', 'stnmgs', 'stngb', 'btngs',
                          'strngs', 'stgngs', 'stngsi', 'stngsd', 'stdgs', 'stnpgs', 'stegs', 'atngs', 'stengs',
                          'stzgs', 'stngsq', 'stnghs', 'spngs', 'stnvgs', 'stngas', 'stfgs', 'stnls', 'ostngs', 'ptngs',
                          'sitngs', 'stjgs', 'stnlgs', 's4ngs', 's5ngs', 's6ngs', 's$ngs', 's%ngs', 's^ngs', 'st,gs',
                          'st<gs', 'otps', 'fopts', 'ots', 'ops', 'opst', 'sopts', 'opths', 'pts', 'oets', 'pots',
                          'opns', 'opus', 'optn', 'oapts', 'oats', 'opxts', 'spts', 'kpts', 'opes', 'opws', 'optsq',
                          'oprts', 'opts', 'opfts', 'opth', 'gopts', 'lopts', 'qopts', 'octs', 'zpts', 'oppts', 'optts',
                          'nopts', 'optr', 'optjs', 'opets', 'oxpts', 'opmts', 'optsd', 'optqs', 'optsj', 'jpts',
                          'hopts', 'obpts', 'ohts', 'opcs', 'obts', 'optsx', 'vopts', 'optv', 'optps', 'optt', 'ogts',
                          'ovpts', 'optns', 'mpts', 'optq', 'npts', 'optsf', 'opty', 'opms', 'oprs', 'popts', 'optsc',
                          'optsi', 'optys', 'oopts', 'optp', 'optgs', 'oypts', 'optds', 'oits', 'outs', 'opis', 'ovts',
                          'optsl', 'hpts', 'opsts', 'oplts', 'opti', 'omts', 'optm', 'optsm', 'uopts', 'opos', 'okts',
                          'zopts', 'opyts', 'oots', 'ompts', 'yopts', 'optsy', 'wpts', 'ozts', 'optc', 'optls', 'opvts',
                          'optxs', 'optf', 'opdts', 'apts', 'ojts', 'upts', 'optss', 'opots', 'opjs', 'aopts', 'kopts',
                          'iopts', 'optsu', 'optg', 'ocpts', 'opys', 'odts', 'opwts', 'opcts', 'opds', 'optsw', 'opte',
                          'ipts', 'owpts', 'ppts', 'okpts', 'otpts', 'ofpts', 'onts', 'qpts', 'xopts', 'optz', 'olts',
                          'opqts', 'opzts', 'optfs', 'oqts', 'jopts', 'opgs', 'opls', 'opvs', 'oqpts', 'xpts', 'optu',
                          'optst', 'oupts', 'optsr', 'optsh', 'optl', 'rpts', 'optsn', 'owts', 'vpts', 'opta', 'opfs',
                          'bpts', 'optvs', 'ypts', 'optms', 'ophs', 'odpts', 'ozpts', 'optx', 'opzs', 'otts', 'oxts',
                          'opjts', 'cpts', 'opbts', 'opqs', 'opnts', 'lpts', 'opks', 'ohpts', 'oyts', 'optse', 'optj',
                          'orts', 'orpts', 'eopts', 'opps', 'opas', 'topts', 'copts', 'ofts', 'ospts', 'optcs', 'onpts',
                          'ogpts', 'optks', 'opits', 'opss', 'fpts', 'optus', 'optsb', 'ophts', 'gpts', 'optis',
                          'optsz', 'wopts', 'optsp', 'osts', 'optk', 'opgts', 'optso', 'opxs', 'dpts', 'optsv', 'epts',
                          'olpts', 'optsk', 'opats', 'mopts', 'bopts', 'optzs', 'optsg', 'dopts', 'optrs', 'oputs',
                          'oepts', 'optes', 'optas', 'ojpts', 'optw', 'oipts', 'opto', 'optd', 'optsa', 'optws',
                          'optbs', 'opkts', 'opbs', 'tpts', 'ropts', 'optb', 'optos', '8pts', '9pts', '0pts', ';pts',
                          '*pts', '(pts', ')pts', 'o9ts', 'o0ts', 'o-ts', 'o[ts', 'o]ts', 'o;ts', 'o(ts', 'o)ts',
                          'o_ts', 'o=ts', 'o+ts', 'o{ts', 'o}ts', 'o:ts', 'op4s', 'op5s', 'op6s', 'op$s', 'op%s',
                          'op^s', 'preferencvs', 'upreferences', 'preferennes', 'preferenyes', 'prefeqences',
                          'preferexnces', 'pzreferences', 'preferenrces', 'preferenceps', 'preoferences',
                          'preferenceus', 'wreferences', 'kpreferences', 'prefereaces', 'prjferences', 'preferencesl',
                          'xreferences', 'preferzences', 'sreferences', 'preeerences', 'preferuences', 'preferencebs',
                          'dreferences', 'prefyerences', 'pzeferences', 'pbreferences', 'preferenoes', 'prefernences',
                          'prefeirences', 'preferencel', 'preferenees', 'preferencesm', 'prefermnces', 'preftrences',
                          'preferencks', 'pweferences', 'ireferences', 'prefesences', 'prefenrences', 'prcferences',
                          'preflrences', 'prefewences', 'prejerences', 'preferenlces', 'preferencesu', 'pareferences',
                          'pcreferences', 'prpferences', 'preferencesf', 'prefeprences', 'premerences', 'preferencegs',
                          'wpreferences', 'preqerences', 'epreferences', 'preferpnces', 'preferencesy', 'prefjrences',
                          'prefecrences', 'preferiences', 'greferences', 'prefarences', 'preferevces', 'prefergnces',
                          'prefereices', 'prefermences', 'preyerences', 'prenerences', 'preferedces', 'prefeaences',
                          'zreferences', 'mpreferences', 'preferjnces', 'preferenhes', 'preuferences', 'prefekences',
                          'treferences', 'kreferences', 'preferxnces', 'prefcrences', 'preferencets', 'preferencesq',
                          'freferences', 'pkreferences', 'pxreferences', 'preferencps', 'prefeqrences', 'preferencles',
                          'prefelences', 'preferencesk', 'preferencem', 'preferyences', 'prefererces', 'ureferences',
                          'qpreferences', 'preqferences', 'prefearences', 'prefertnces', 'preferznces', 'hreferences',
                          'preferenuces', 'prefqerences', 'pneferences', 'preflerences', 'preferevnces', 'npreferences',
                          'preferencyes', 'prefemences', 'prlferences', 'preferencesc', 'xpreferences', 'prefkrences',
                          'preferjences', 'preferenceso', 'prefereqces', 'prefierences', 'prkeferences', 'pieferences',
                          'preferencms', 'rreferences', 'preferenceo', 'preferbences', 'prveferences', 'preferenwces',
                          'preferkences', 'preforences', 'prelerences', 'priferences', 'preferenceks', 'preferenies',
                          'preferencges', 'preferelnces', 'preferenbes', 'prefezences', 'paeferences', 'prefmrences',
                          'prefgrences', 'prefeuences', 'preferenyces', 'pmeferences', 'prefervnces', 'preferezces',
                          'prbeferences', 'preferenches', 'preferencos', 'preferencep', 'preferexces', 'prefzerences',
                          'preaerences', 'prefereqnces', 'prexerences', 'preferencbes', 'ypreferences', 'creferences',
                          'prefperences', 'preferencels', 'preferencesh', 'hpreferences', 'prejferences', 'breferences',
                          'preferepces', 'prefelrences', 'preferenceos', 'preferencev', 'pyeferences', 'prjeferences',
                          'pruferences', 'prnferences', 'preierences', 'preferencmes', 'preferenices', 'prefberences',
                          'prceferences', 'preferencec', 'nreferences', 'preferecces', 'pueferences', 'preberences',
                          'prefzrences', 'preferenkes', 'pwreferences', 'preferenccs', 'preferencey', 'pjeferences',
                          'psreferences', 'preferlences', 'preferecnces', 'preferoences', 'preferekces', 'preferencis',
                          'prefhrences', 'preferencpes', 'preferpences', 'preferencest', 'prefprences', 'preferunces',
                          'prefebrences', 'preferengces', 'preiferences', 'prefyrences', 'preferencqs', 'preferenmes',
                          'prefercnces', 'prgferences', 'prekferences', 'poeferences', 'preferencxs', 'preferencjes',
                          'preferknces', 'preferencies', 'prefeorences', 'prefereyces', 'preferencesn', 'prefereinces',
                          'preferenkces', 'preferhnces', 'preferenchs', 'pnreferences', 'preferepnces', 'prtferences',
                          'preferonces', 'fpreferences', 'proferences', 'preferencesp', 'gpreferences', 'preferencas',
                          'pvreferences', 'prefezrences', 'prefereynces', 'prefekrences', 'prqferences', 'preferencbs',
                          'pqreferences', 'prexferences', 'prefvrences', 'preferenles', 'prefeoences', 'prefbrences',
                          'mreferences', 'vreferences', 'prqeferences', 'prefeiences', 'proeferences', 'prekerences',
                          'pxeferences', 'przeferences', 'preferencnes', 'preferencesg', 'prefxerences', 'preferencqes',
                          'preferenoces', 'prbferences', 'apreferences', 'cpreferences', 'preferentes', 'preferenceh',
                          'preferlnces', 'qreferences', 'ppeferences', 'preferenpes', 'prkferences', 'prefepences',
                          'prneferences', 'preferencecs', 'preferxences', 'preferencen', 'preferenues', 'prefervences',
                          'preferegnces', 'prpeferences', 'preferefces', 'preferenctes', 'pkeferences', 'prefexrences',
                          'prefurences', 'preferencesb', 'preferencek', 'prefernnces', 'prefmerences', 'prefnerences',
                          'prewerences', 'pceferences', 'prefehences', 'prefercences', 'preferenaes', 'preferaences',
                          'prefeurences', 'preferenceb', 'prefehrences', 'pjreferences', 'prleferences', 'preferenses',
                          'prefxrences', 'prefereonces', 'praeferences', 'pheferences', 'phreferences', 'prvferences',
                          'prefaerences', 'bpreferences', 'preferencjs', 'yreferences', 'prefeyences', 'preferances',
                          'preferencems', 'prefnrences', 'prefereneces', 'prezerences', 'preferqences', 'preferenzes',
                          'preferenwes', 'prefemrences', 'preferinces', 'vpreferences', 'preferencgs', 'preferenpces',
                          'prefereeces', 'prefherences', 'prefkerences', 'preferetces', 'preyferences', 'prefenences',
                          'areferences', 'prefereoces', 'prefejences', 'preferenckes', 'prefereuces', 'preferenzces',
                          'preferencns', 'pseferences', 'premferences', 'prefeyrences', 'preferencehs', 'prefecences',
                          'prieferences', 'pryeferences', 'prehferences', 'preferencesr', 'rpreferences',
                          'preferencejs', 'preferesces', 'preferencts', 'preferenaces', 'preperences', 'prefirences',
                          'preferenceq', 'dpreferences', 'preferewces', 'ipreferences', 'preferenjes', 'preferegces',
                          'preferqnces', 'praferences', 'prezferences', 'preferentces', 'preaferences', 'jreferences',
                          'prenferences', 'preferenqces', 'preferencesj', 'preferenczs', 'prefevences', 'preferelces',
                          'prefuerences', 'preferenres', 'preferencei', 'prmferences', 'pveferences', 'tpreferences',
                          'pireferences', 'prefoerences', 'jpreferences', 'pryferences', 'preferenceqs', 'preuerences',
                          'preferencesv', 'prefjerences', 'pyreferences', 'preferenceys', 'preferencues',
                          'zpreferences', 'preferenceis', 'prebferences', 'prefejrences', 'prepferences', 'preferencus',
                          'preherences', 'preferencls', 'prheferences', 'preferetnces', 'preferensces', 'pureferences',
                          'prmeferences', 'prefexences', 'preferenceg', 'preferencys', 'preferynces', 'preferenczes',
                          'spreferences', 'preferencaes', 'ereferences', 'preferhences', 'prxeferences', 'prefereunces',
                          'preferencevs', 'pleferences', 'prhferences', 'prefereznces', 'prefereknces', 'prefebences',
                          'preferencej', 'preferencet', 'preoerences', 'przferences', 'pqeferences', 'preferenqes',
                          'preferenceu', 'preferencens', 'prelferences', 'prefevrences', 'preferencesi', 'preserences',
                          'preferbnces', 'pbeferences', 'preferenges', 'prefereances', 'prxferences', 'prefqrences',
                          'preferencoes', 'pmreferences', 'prueferences', '9references', '-references', '[references',
                          ']references', ';references', '(references', ')references', '_references', '=references',
                          '+references', '{references', '}references', ':references', 'p3eferences', 'p#eferences',
                          'p$eferences', 'p%eferences', 'pr2ferences', 'pr$ferences', 'pr#ferences', 'pr@ferences',
                          'pref2rences', 'pref$rences', 'pref#rences', 'pref@rences', 'prefe3ences', 'prefe#ences',
                          'prefe$ences', 'prefe%ences', 'prefer2nces', 'prefer$nces', 'prefer#nces', 'prefer@nces',
                          'prefere,ces', 'prefere<ces', 'preferenc2s', 'preferenc$s', 'preferenc#s', 'preferenc@s',
                          'prfrncis', 'prfrnsc', 'prfrnlcs', 'prfncs', 'prfrnc', 'prxrncs', 'prfrnpcs', 'rfrncs',
                          'prfrncg', 'pfrrncs', 'prfrcs', 'prrfrncs', 'phrfrncs', 'prfrnco', 'pffrncs', 'prfrhcs',
                          'prfnrcs', 'prfrns', 'pwfrncs', 'prfrncsk', 'prfrqcs', 'pfrncs', 'prfrcns', 'prfrndcs',
                          'prfrnecs', 'prrfncs', 'prrncs', 'prcrncs', 'prffncs', 'prfrnjs', 'pifrncs', 'prfrlcs',
                          'pcrfrncs', 'rpfrncs', 'prsfrncs', 'purfrncs', 'prfrvncs', 'prvfrncs', 'prfrnhcs', 'prfrncs',
                          'prfrncd', 'cprfrncs', 'prsrncs', 'pmfrncs', 'prfhncs', 'prfrncks', 'prfrncl', 'prfrnxs',
                          'pirfrncs', 'prfrnch', 'zprfrncs', 'prfnrncs', 'prfrmcs', 'pkfrncs', 'prprncs', 'prfrqncs',
                          'hrfrncs', 'prtrncs', 'ptrfrncs', 'wprfrncs', 'prfrnas', 'uprfrncs', 'prhrncs', 'prfgncs',
                          'orfrncs', 'rrfrncs', 'pryrncs', 'phfrncs', 'psfrncs', 'prfmncs', 'prfrncu', 'pzfrncs',
                          'prfuncs', 'prfrnhs', 'prlrncs', 'prfrnos', 'pcfrncs', 'prirncs', 'prdfrncs', 'prlfrncs',
                          'pvfrncs', 'prfrnics', 'prfrncsp', 'qprfrncs', 'prflncs', 'prqrncs', 'prfrrcs', 'prfrnczs',
                          'prfrncvs', 'prafrncs', 'prfvncs', 'prfrdcs', 'prfrics', 'prfrncsf', 'prfrnccs', 'nrfrncs',
                          'prfzncs', 'prfrncsw', 'prfrncsq', 'pjrfrncs', 'prfrncsh', 'prfrxcs', 'pxfrncs', 'pdrfrncs',
                          'prfrncx', 'prfruncs', 'prforncs', 'prfrnncs', 'prfrncqs', 'prfarncs', 'prmfrncs', 'frfrncs',
                          'brfrncs', 'prfracs', 'prfrncns', 'prfrnvcs', 'prfrdncs', 'prfkncs', 'prfsncs', 'prfrncrs',
                          'prbfrncs', 'prfxncs', 'jrfrncs', 'prfxrncs', 'prfrncsl', 'oprfrncs', 'prwfrncs', 'prfnncs',
                          'prfrpcs', 'prfrjcs', 'trfrncs', 'prfrgncs', 'prflrncs', 'prfrvcs', 'prftncs', 'prfrnchs',
                          'prfrnqs', 'prfrnzcs', 'prfrnts', 'mprfrncs', 'xprfrncs', 'prfencs', 'prfrncsu', 'arfrncs',
                          'urfrncs', 'prfrnbs', 'prfrxncs', 'prfdncs', 'prfrnvs', 'przrncs', 'prfrnws', 'prfbncs',
                          'prfrgcs', 'prfrncm', 'prfrncps', 'pmrfrncs', 'prfrzncs', 'prfvrncs', 'prfrjncs', 'prfrncn',
                          'prfrrncs', 'plfrncs', 'prfrlncs', 'prfrncsg', 'prfrncsx', 'prarncs', 'prfrnzs', 'prfrncus',
                          'prfsrncs', 'yprfrncs', 'prfrecs', 'prfrncy', 'prfcncs', 'qrfrncs', 'prfrncp', 'prfyrncs',
                          'pbrfrncs', 'prfrnjcs', 'prfrncys', 'nprfrncs', 'prfrnrs', 'prftrncs', 'prfrncsn', 'prqfrncs',
                          'prfrngs', 'lrfrncs', 'prfrnces', 'pkrfrncs', 'prfrnca', 'irfrncs', 'prfrnbcs', 'prfrnmcs',
                          'prfrncgs', 'prfdrncs', 'prfrncsj', 'prfrzcs', 'prfrtncs', 'prfrncz', 'pyrfrncs', 'prfrncxs',
                          'prgrncs', 'prmrncs', 'prfrnps', 'przfrncs', 'prfrncb', 'kprfrncs', 'lprfrncs', 'prfrwcs',
                          'prfrnfcs', 'prfrnce', 'pdfrncs', 'prfrmncs', 'prorncs', 'pvrfrncs', 'prfkrncs', 'prpfrncs',
                          'prfrncsd', 'prfrsncs', 'pprfrncs', 'psrfrncs', 'prfancs', 'prfirncs', 'prfrngcs', 'prjfrncs',
                          'pgfrncs', 'pryfrncs', 'prfrkcs', 'prfrncss', 'prfrncsz', 'prfrncv', 'perfrncs', 'prgfrncs',
                          'zrfrncs', 'erfrncs', 'prfrnss', 'prfryncs', 'prffrncs', 'prfrbcs', 'prfrncas', 'pfrfrncs',
                          'pbfrncs', 'prwrncs', 'prrrncs', 'jprfrncs', 'prfrncf', 'prfurncs', 'ptfrncs', 'prfrncds',
                          'mrfrncs', 'prfrncr', 'prdrncs', 'profrncs', 'prfzrncs', 'prnrncs', 'prvrncs', 'prfrfncs',
                          'prfrncj', 'pqfrncs', 'ppfrncs', 'prfrnns', 'prefrncs', 'prfrncsy', 'porfrncs', 'prifrncs',
                          'bprfrncs', 'prfrkncs', 'pzrfrncs', 'plrfrncs', 'prxfrncs', 'prfrnkcs', 'prfrbncs',
                          'prfprncs', 'pjfrncs', 'prjrncs', 'prfrncq', 'prfrnck', 'prfrnxcs', 'prfrocs', 'pafrncs',
                          'prfrtcs', 'sprfrncs', 'prfrccs', 'aprfrncs', 'prhfrncs', 'grfrncs', 'prfrntcs', 'parfrncs',
                          'prfrncts', 'prkrncs', 'prfrncos', 'prfrnks', 'pyfrncs', 'prfrncms', 'prfrycs', 'prfrpncs',
                          'prfrnus', 'prfrnycs', 'hprfrncs', 'prfrnqcs', 'prfrnci', 'prurncs', 'fprfrncs', 'prfrnct',
                          'prfoncs', 'prfrnys', 'yrfrncs', 'prfrncsi', 'prfwncs', 'pnrfrncs', 'prfpncs', 'prfcrncs',
                          'drfrncs', 'prfrnes', 'dprfrncs', 'prfrncsm', 'prfrncw', 'prfrncse', 'prtfrncs', 'vprfrncs',
                          'prfqncs', 'prfrnucs', 'prkfrncs', 'prfrncjs', 'pnfrncs', 'krfrncs', 'iprfrncs', 'prfrencs',
                          'prfrhncs', 'prfrnrcs', 'prfrincs', 'wrfrncs', 'prfmrncs', 'prfrncsv', 'prnfrncs', 'prfgrncs',
                          'prfrnocs', 'xrfrncs', 'prfrnds', 'pufrncs', 'pwrfrncs', 'prfwrncs', 'pqrfrncs', 'prfincs',
                          'rprfrncs', 'prfrucs', 'prerncs', 'prfrncc', 'prfyncs', 'pofrncs', 'crfrncs', 'prfbrncs',
                          'prcfrncs', 'prfrncsa', 'prfrncso', 'prfrscs', 'prfhrncs', 'prufrncs', 'prfrfcs', 'prfrncsr',
                          'prfroncs', 'gprfrncs', 'srfrncs', 'prfrnms', 'prbrncs', 'pgrfrncs', 'prfrnscs', 'prfrnfs',
                          'prferncs', 'prfrncsc', 'prfrncfs', 'prfrnis', 'tprfrncs', 'prfrwncs', 'eprfrncs', 'prfrncst',
                          'prfrnls', 'prfrnwcs', 'prfrncbs', 'pefrncs', 'prfrnacs', 'prfrancs', 'prfrncws', 'pxrfrncs',
                          'prfrcncs', 'prfqrncs', 'prfrncsb', 'prfjncs', 'vrfrncs', 'prfjrncs', 'prfrncls', '9rfrncs',
                          '0rfrncs', '-rfrncs', '[rfrncs', ']rfrncs', ';rfrncs', '(rfrncs', ')rfrncs', '_rfrncs',
                          '=rfrncs', '+rfrncs', '{rfrncs', '}rfrncs', ':rfrncs', 'p3frncs', 'p4frncs', 'p5frncs',
                          'p#frncs', 'p$frncs', 'p%frncs', 'prf3ncs', 'prf4ncs', 'prf5ncs', 'prf#ncs', 'prf$ncs',
                          'prf%ncs', 'prfr,cs', 'prfr<cs', 'sret', 'swet', 'snet', 'sej', 'ste', 'st', 'se',
                          'seg', 'sext', 'srt', 'est', 'seth', 'setc', 'sev', 'shet', 'sht', 'pet', 'stt',
                          'seot', 'sgt', 'sfet', 'ser', 'seft', 'jet', 'sel', 'zet', 'vet', 'sea', 'yset', 'nset',
                          'sqet', 'soet', 'sot', 'spt', 'det', 'seti', 'bset', 'sjet', 'setq', 'sdet', 'qet', 'het',
                          'wet', 'mset', 'aet', 'sef', 'sxt', 'setk', 'setf', 'setr', 'sen', 'setz', 'zset', 'iset',
                          'seet', 'szet', 'seqt', 'setl', 'scet', 'setw', 'sekt', 'setj', 'szt', 'seu', 'sety', 'sei',
                          'jset', 'setv', 'sejt', 'seta', 'eet', 'yet', 'sept', 'sset', 'setx', 'sft', 'syet',
                          'fet', 'met', 'vset', 'stet', 'bet', 'syt', 'net', 'dset', 'sst', 'sct', 'seut', 'sat', 'sek',
                          'selt', 'sewt', 'smt', 'swt', 'sex', 'skt', 'seh', 'siet', 'see', 'aset', 'sez', 'seht',
                          'seit', 'setp', 'cset', 'sect', 'sete', 'sets', 'sbet', 'sjt', 'sent', 'setb', 'sert', 'slt',
                          'slet', 'lset', 'fset', 'eset', 'seb', 'setu', 'gset', 'hset', 'uet', 'sget', 'setg',
                          'uset', 'snt', 'seo', 'sep', 'qset', 'sem', 'seq', 'oset', 'sey', 'svt', 'tset', 'let', 'sed',
                          'xset', 'segt', 'cet', 'pset', 'ket', 'sew', 'sec', 'sezt', 'seyt', 'kset', 'sest', 'suet',
                          'get', 'iet', 'setd', 'semt', 'sket', 'setn', 'seat', 'rset', 'sdt', 'sit', 'sevt',
                          'setm', 'sbt', 'sedt', 'saet', 'svet', 'sqt', 'sebt', 'spet', 'smet', 'wset', 'seto', 'oet',
                          'xet', 'sxet', 's4t', 's3t', 's2t', 's$t', 's#t', 's@t', 'se4', 'se5', 'se6', 'se$', 'se%',
                          'se^', 'ot', 'otp', 'yopt', 'odt', 'iopt', 'op', 'opj', 'opr', 'out', 'npt', 'dpt',
                          'pt', 'oxt', 'ojt', 'oppt', 'opnt', 'opat', 'uopt', 'lpt', 'opm', 'sopt', 'opgt', 'owpt',
                          'oft', 'obpt', 'opmt', 'oot', 'oplt', 'ost', 'ohpt', 'opbt', 'oprt', 'opb', 'opvt', 'opo',
                          'jopt', 'opg', 'ope', 'oupt', 'opqt', 'omt', 'ojpt', 'ozt', 'upt', 'opx', 'vpt', 'xopt',
                          'qopt', 'oput', 'opi', 'copt', 'popt', 'opzt', 'ipt', 'opz', 'ogt', 'oapt', 'oxpt', 'oph',
                          'opn', 'opu', 'ospt', 'opct', 'ont', 'hpt', 'opf', 'mopt', 'jpt', 'okt', 'ropt', 'onpt',
                          'oct', 'opit', 'cpt', 'opxt', 'ozpt', 'rpt', 'oept', 'wpt', 'opot', 'zopt', 'opd',
                          'fpt', 'owt', 'ocpt', 'qpt', 'opy', 'lopt', 'ypt', 'aopt', 'oqt', 'oht', 'xpt', 'gopt', 'opl',
                          'kpt', 'ept', 'opwt', 'ovt', 'ovpt', 'opft', 'opp', 'bpt', 'vopt', 'mpt', 'kopt', 'oit',
                          'odpt', 'oqpt', 'okpt', 'hopt', 'olpt', 'nopt', 'opdt', 'opa', 'gpt', 'otpt',
                          'opk', 'ppt', 'opet', 'opkt', 'bopt', 'ott', 'oyt', 'apt', 'dopt', 'opjt', 'oopt',
                          'ofpt', 'ompt', 'ogpt', 'oat', 'olt', 'zpt', 'oipt', 'obt', 'eopt', 'opc', 'opv', 'oypt',
                          'topt', 'opyt', 'opht', 'orpt', 'wopt', 'opq', '8pt', '9pt', '0pt', ';pt', '*pt', '(pt',
                          ')pt', 'o9t', 'o0t', 'o-t', 'o[t', 'o]t', 'o;t', 'o(t', 'o)t', 'o_t', 'o=t', 'o+t', 'o{t',
                          'o}t', 'o:t', 'op4', 'op5', 'op6', 'op$', 'op%', 'op^', 'prsef', 'pef', 'prefi', 'preef',
                          'perf', 'ppref', 'prea', 'lref', 'prer', 'preuf',
                          'prei', 'ptref', 'prek', 'prkef', 'hpref', 'preh', 'ppef', 'prief', 'qpref', 'pnref',
                          'prtf', 'pfref', 'prmef', 'prrf', 'pwref', 'prehf', 'prhef', 'tpref', 'qref', 'ptef', 'pzref',
                          'xref', 'pfef', 'wref', 'prxef', 'pcef', 'pre', 'dpref', 'pren', 'pqef', 'prefa', 'preu',
                          'prefc', 'lpref', 'pcref', 'pjef', 'rref', 'aref', 'pqref', 'pmref', 'prewf', 'prefs',
                          'pkref', 'pruef', 'uref', 'pgef', 'zref', 'prif', 'sref', 'prpf', 'pnef', 'prgf', 'prkf',
                          'prsf', 'premf', 'prefz', 'preo', 'prfef', 'preg', 'prem', 'prefk', 'href', 'piref',
                          'cpref', 'prcf', 'prefv', 'preqf', 'peef', 'pyref', 'psref', 'pregf', 'puref', 'prenf',
                          'prdf', 'gpref', 'prbef', 'prjef', 'preq', 'eref', 'prgef', 'prref', 'kref', 'praef', 'mpref',
                          'ypref', 'iref', 'pxef', 'pbref', 'precf', 'epref', 'preff', 'prnf', 'prez', 'xpref', 'pyef',
                          'prjf', 'paef', 'prbf', 'przf', 'apref', 'jpref', 'prxf', 'zpref', 'fpref', 'prefu', 'prefy',
                          'pret', 'prefr', 'predf', 'pzef', 'psef', 'prhf', 'poef', 'prezf', 'prep', 'phef', 'prelf',
                          'pjref', 'upref', 'pief', 'pred', 'prcef', 'prefn', 'prqf', 'prefq', 'prefx', 'preft', 'prey',
                          'prec', 'prev', 'preb', 'vpref', 'praf', 'preyf', 'prefo', 'rpref', 'prerf', 'prefd', 'proef',
                          'prefw', 'prebf', 'yref', 'pryf', 'pruf', 'peref', 'prefb', 'prnef', 'pwef', 'prdef',
                          'pvef', 'pgref', 'prepf', 'pmef', 'prefe', 'pryef', 'cref', 'preif', 'dref', 'pxref', 'prefh',
                          'prejf', 'kpref', 'npref', 'preaf', 'nref', 'wpref', 'pdef', 'prekf', 'fref', 'ipref', 'prmf',
                          'jref', 'pbef', 'prej', 'prwf', 'prefp', 'prefg', 'puef', 'bpref', 'prvf', 'prefm', 'prvef',
                          'bref', 'prex', 'gref', 'pretf', 'phref', 'opref', 'przef', 'prtef', 'prexf', 'prew',
                          'pvref', 'spref', 'mref', 'presf', 'plef', 'pkef', 'oref', 'preof', 'vref',
                          'prqef', 'poref', 'pree', 'plref', 'prwef', 'paref', 'prpef', 'prlef', 'prevf', 'pdref',
                          'prefj', '9ref', '0ref', '-ref', '[ref', ']ref', ';ref', '(ref', ')ref', '_ref', '=ref',
                          '+ref', '{ref', '}ref', ':ref', 'p3ef', 'p4ef', 'p5ef', 'p#ef', 'p$ef', 'p%ef', 'pr4f',
                          'pr3f', 'pr2f', 'pr$f', 'pr#f', 'pr@f', '/stngs', '/opts', '/prfrncs'],
                 extras={'emoji': "settings", "args": {
                     'settings.meta.args.setting': ['settings.meta.args.setting.description', True],
                     'settings.meta.args.value': ['settings.meta.args.value.description', True],
                     'profile.meta.args.profile': ['profile.meta.args.profile.description', True],
                 }, "dev": False, "description_keys": ['settings.meta.description1', 'settings.meta.description2'],
                         "name_key": "settings.slash.name"},
                 brief="settings.slash.description",
                 description="{0}\n{1}")
    async def settings(self, ctx, setting=None, value=None, profile=None):
        """
        This function is the command for the settings command.

        Args:
            ctx: The context of the command.
            setting: The setting to change.
            value: The value to change the setting to.
            profile: The profile to change the setting on.
        """
        await command_counter(self.client, ctx.author.id)
        await settings_command(self.client, ctx, setting, value, profile)


def setup(client):
    """
    This function is the setup function for the profile settings cog.

    Args:
        client: The client of the bot.
    """
    client.add_cog(ProfileSettings(client))


"""
le guide for ze epic function for le check for le non bool type of le setting
must be synchronous no async around here
ok so the name of the function must be unique and must be in this file, the parameters passed to the function are
bot client, context, value
where bot client is well the same fucking client as everywhere
context is either the context from a slash command or a normal command
value is the inputted value from the user which the function should check if it meets the requirements for this setting
the return type must be the value that the setting will become, or False if the value inputted is not allowed
"""

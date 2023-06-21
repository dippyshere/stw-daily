"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the device auth command.
"""

import asyncio
import base64
import os
import time
import logging

import discord
import discord.ext.commands as ext
import orjson
from Crypto.Cipher import AES

import stwutil as stw
from ext.profile.bongodb import get_user_document, replace_user_document, generate_profile_select_options, \
    timeout_check_processing, active_view, command_counter

TOS_VERSION = 31
logger = logging.getLogger(__name__)


async def tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx, desired_lang):
    """
    This is the embed that is sent when the user has not accepted the TOS

    Args:
        user_document: The user document
        client: The client
        currently_selected_profile_id: The currently selected profile id
        ctx: The context
        desired_lang: The desired language

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('devauth.embed.legal.title', desired_lang), "pink_link"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, currently_selected_profile_id)}\n"
                     f"```{selected_profile_data['friendly_name']}```\u200b\n"),
        color=embed_colour)
    embed.description += (
        f"{stw.I18n.get('devauth.embed.legal.description', desired_lang, currently_selected_profile_id)}\n"
        f"```{stw.I18n.get('devauth.embed.legal.agreement1', desired_lang)}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement2', desired_lang)}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement3', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement4', desired_lang, 'https://www.stwdaily.tk/legal-info/terms-of-service')}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement5', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement6', desired_lang)}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement7', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement8', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement9', desired_lang)}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement10', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement11', desired_lang)}\n\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement12', desired_lang)}\n"
        f"{stw.I18n.get('devauth.embed.legal.agreement13', desired_lang, 'https://www.stwdaily.tk/legal-info/privacy-policy')}"
        f"```\n\u200b")

    embed = await stw.set_thumbnail(client, embed, "pink_link")
    embed = await stw.add_requested_footer(ctx, embed, desired_lang)
    return embed


async def add_enslaved_user_accepted_license(view, interaction):
    """
    This is the function that is called when the user accepts the TOS

    Args:
        view: The view
        interaction: The interaction
    """
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"]["tos_accepted"] = True
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_date"] = time.time_ns()  # how to get unix timestamp i forgor time.time is unix
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_version"] = TOS_VERSION

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    await replace_user_document(view.client, view.user_document)
    del view.client.processing_queue[view.user_document["user_snowflake"]]


async def pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction=None,
                                  exchange_auth_session=None, timeout_bypass=False, desired_lang=None):
    """
    This is the function that is called when the user has not device authed yet

    Args:
        user_document: The user document
        client: The client
        currently_selected_profile_id: The currently selected profile id
        ctx: The context
        interaction: The interaction
        exchange_auth_session: The exchange auth session
        timeout_bypass: Whether or not to bypass the timeout
        desired_lang: The desired language

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    page_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('devauth.embed.title', desired_lang), "pink_link"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, currently_selected_profile_id)}\n"
                     f"```{selected_profile_data['friendly_name']}```\u200b"),
        color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "pink_link")
    page_embed = await stw.add_requested_footer(ctx, page_embed, desired_lang)

    if selected_profile_data["authentication"] is None:
        # Not authenticated yet data stuffy ;p

        auth_session = False
        if exchange_auth_session is None and timeout_bypass is False:
            try:
                temp_auth = client.temp_auth[ctx.author.id]
                auth_session = temp_auth

                embed = await stw.processing_embed(client, ctx, desired_lang)

                message = None
                if interaction is None:
                    message = await stw.slash_send_embed(ctx, client, embeds=embed)
                else:
                    await interaction.edit_original_response(embed=embed)

                asyncio.get_event_loop().create_task(
                    attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction, message,
                                                desired_lang=desired_lang))
                return False
            except:
                pass
        elif exchange_auth_session:
            auth_session = True

        auth_session_found_message = f"{stw.I18n.get('devauth.embed.preauth.description.nosession1', desired_lang, client.config['login_links']['logout_login_fortnite_pc'])}\n\u200b\n{stw.I18n.get('devauth.embed.preauth.description.nosession2', desired_lang, client.config['emojis']['locked'])}"
        if auth_session:
            auth_session_found_message = f"{stw.I18n.get('devauth.embed.preauth.description.activesession1', desired_lang, client.config['emojis']['library_input'])}\n\u200b\n{stw.I18n.get('devauth.embed.preauth.description.activesession2', desired_lang, client.config['login_links']['logout_login_fortnite_pc'], client.config['emojis']['locked'])}"

        page_embed.description += f"\n{stw.I18n.get('devauth.embed.preauth.description', desired_lang)}" \
                                  f"\n\u200b\n{auth_session_found_message}\n\u200b"

    return page_embed


async def attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction=None, message=None,
                                      desired_lang=None):
    """
    This function attemps to exchange the auth to an ios token

    Args:
        temp_auth: The temp auth
        user_document: The user document
        client: The client
        ctx: The context
        interaction: The interaction
        message: The message
        desired_lang: The desired lang
    """
    try:
        get_ios_auth = await stw.exchange_games(client, temp_auth["token"], "ios")
        response_json = orjson.loads(await get_ios_auth.read())
        await handle_dev_auth(client, ctx, interaction, user_document, response_json, message,
                              desired_lang=desired_lang)
    except:
        await handle_dev_auth(client, ctx, interaction, user_document, False, message, desired_lang=desired_lang)


async def no_profiles_page(client, ctx, desired_lang):
    """
    This is the function that is called when the user has no profiles

    Args:
        client: The client
        ctx: The context
        desired_lang: The desired lang

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]

    no_profiles_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('devauth.embed.title', desired_lang), "pink_link"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.noprofiles.description1', desired_lang)}\n"
                     f"```{stw.I18n.get('devauth.embed.noprofile.descripton2', desired_lang)}```\u200b\n"),
        color=embed_colour)
    no_profiles_embed = await stw.set_thumbnail(client, no_profiles_embed, "pink_link")
    no_profiles_embed = await stw.add_requested_footer(ctx, no_profiles_embed, desired_lang)

    return no_profiles_embed


async def existing_dev_auth_embed(client, ctx, current_profile, currently_selected_profile_id, desired_lang,
                                  user_document):
    """
    This is the function that is called when the user has device authed

    Args:
        client: The client
        ctx: The context
        current_profile: The current profile
        currently_selected_profile_id: The currently selected profile id
        desired_lang: The desired lang
        user_document: The user document

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]

    try:
        if user_document["auto_claim"]["enabled"]:
            flow_key = 'devauth.embed.existing.description4.disable'
        else:
            flow_key = 'devauth.embed.existing.description4.enable'
    except:
        flow_key = 'devauth.embed.existing.description4.enable'

    try:
        if current_profile["authentication"]["hasExpired"]:
            expired = True
        else:
            expired = False
    except:
        expired = False

    happy_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('devauth.embed.title', desired_lang), "pink_link"),
        description=f"\u200b\n"
                    f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, currently_selected_profile_id)}\n"
                    f"```{current_profile['friendly_name']}```\u200b\n"
                    f"{stw.I18n.get('devauth.embed.existing.description1', desired_lang)}\n\u200b\n "
                    f"{stw.I18n.get('devauth.embed.existing.description2', desired_lang, client.config['emojis']['library_trashcan'])}\n\u200b\n"
                    f"{stw.I18n.get('devauth.embed.existing.description3', desired_lang, client.config['emojis']['library_floppydisc'])}\n\u200b\n"
                    f"{stw.I18n.get(flow_key, desired_lang, client.config['emojis']['library_clock'])}\n\u200b\n",
        color=embed_colour)

    if expired:
        happy_embed.description += f"{stw.I18n.get('devauth.embed.existing.hasexpired.description', desired_lang, client.config['emojis']['warning'])}\n\u200b\n"
    happy_embed.description += f"{stw.I18n.get('devauth.embed.existing.description5', desired_lang)}\n" \
                               f"```{current_profile['authentication']['displayName']}```\u200b"

    sad_embed = await stw.set_thumbnail(client, happy_embed, "pink_link")
    neutral_embed = await stw.add_requested_footer(ctx, sad_embed, desired_lang)

    return neutral_embed


async def handle_dev_auth(client, ctx, interaction=None, user_document=None, exchange_auth_session=None, message=None,
                          desired_lang=None):
    """
    This function handles the device auth

    Args:
        client: The client
        ctx: The context
        interaction: The interaction
        user_document: The user document
        exchange_auth_session: The exchange auth session
        message: The message
        desired_lang: The desired lang

    Returns:
        The embed
    """
    logger.debug(f"handle_dev_auth() called with args: {locals()}")

    current_author_id = ctx.author.id

    if user_document is None:
        user_document = await get_user_document(ctx, client, current_author_id, desired_lang=desired_lang)

    # Get the currently selected profile

    currently_selected_profile_id = user_document["global"]["selected_profile"]

    try:
        current_profile = user_document["profiles"][str(currently_selected_profile_id)]
    except:
        embed = await no_profiles_page(client, ctx, desired_lang)
        return await stw.slash_send_embed(ctx, client, embeds=embed)

    if current_profile["statistics"]["tos_accepted_version"] != TOS_VERSION:
        embed = await tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx, desired_lang)
        button_accept_view = EnslaveUserLicenseAgreementButton(user_document, client, ctx,
                                                               currently_selected_profile_id, interaction, message,
                                                               desired_lang=desired_lang)
        await active_view(client, ctx.author.id, button_accept_view)

        if message is not None:
            return await stw.slash_edit_original(ctx, message, embeds=embed, view=button_accept_view)

        if interaction is None:
            message = await stw.slash_send_embed(ctx, client, embeds=embed, view=button_accept_view)
            button_accept_view.message = message
            return message
        else:
            return await interaction.edit_original_response(embed=embed, view=button_accept_view)

    elif current_profile["authentication"] is None:

        embed = await pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction,
                                              exchange_auth_session, desired_lang=desired_lang)
        if not embed:
            return
        account_stealing_view = EnslaveAndStealUserAccount(user_document, client, ctx, currently_selected_profile_id,
                                                           exchange_auth_session, interaction, message,
                                                           desired_lang=desired_lang)
        await active_view(client, ctx.author.id, account_stealing_view)

        if message is not None:
            return await stw.slash_edit_original(ctx, message, embeds=embed, view=account_stealing_view)

        if interaction is None:
            message = await stw.slash_send_embed(ctx, client, embeds=embed, view=account_stealing_view)
            account_stealing_view.message = message
            return message
        else:
            return await interaction.edit_original_response(embed=embed, view=account_stealing_view)

    elif current_profile["authentication"] is not None:
        embed = await existing_dev_auth_embed(client, ctx, current_profile, currently_selected_profile_id, desired_lang,
                                              user_document)
        stolen_account_view = StolenAccountView(user_document, client, ctx, currently_selected_profile_id, interaction,
                                                embed, message, desired_lang=desired_lang)
        await active_view(client, ctx.author.id, stolen_account_view)

        if message is not None:
            return await stw.slash_edit_original(ctx, message, embeds=embed, view=stolen_account_view)

        if interaction is None:
            message = await stw.slash_send_embed(ctx, client, embeds=embed, view=stolen_account_view)
            stolen_account_view.message = message
            return message
        else:
            return await interaction.edit_original_response(embed=embed, view=stolen_account_view)


class EnslaveAndStealUserAccount(discord.ui.View):
    """
    This class is the view for authing the user
    """

    def __init__(self, user_document, client, ctx, currently_selected_profile_id, response_json, interaction=None,
                 extra_message=None, error_embed=None, desired_lang=None):

        super().__init__(timeout=480.0)
        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}

        if extra_message is not None:
            self.message = extra_message

        self.response_json = response_json
        self.interaction = interaction

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document, desired_lang)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))
        self.timed_out = False
        self.error_embed = error_embed
        self.desired_lang = desired_lang
        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', desired_lang)
        self.children[1].label = stw.I18n.get('devauth.view.button.auth', desired_lang)
        self.children[2].label = stw.I18n.get('devauth.view.button.auth.withsession', desired_lang)
        self.exchanged = False
        if self.response_json is None or self.response_json is False:
            del self.children[2]
        else:
            self.exchanged = True

    async def on_timeout(self, processing_timeout=False):
        """
        This function handles the timeout

        Args:
            processing_timeout: If the timeout is processing

        Returns:
            None
        """

        if self.error_embed is None:
            timeout_embed = await pre_authentication_time(self.user_document, self.client,
                                                          self.currently_selected_profile_id, self.ctx,
                                                          self.interaction,
                                                          self.exchanged, True, desired_lang=self.desired_lang)

            timeout_embed.description += f"{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"
        else:
            self.error_embed.description += f"\n\u200b\n{stw.I18n.get('generic.embed.timeout', self.desired_lang)}"
            timeout_embed = self.error_embed

        for child in self.children:
            child.disabled = True
        self.stop()
        self.timed_out = True

        try:
            if self.interaction is None:
                return await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
            else:
                return await self.interaction.edit_original_response(embed=timeout_embed, view=self)
        except:
            try:
                if isinstance(self.message, discord.Interaction):
                    method = self.message.edit_original_response
                else:
                    try:
                        method = self.message.edit
                    except:
                        method = self.ctx.edit
                if isinstance(self.ctx, discord.ApplicationContext):
                    try:
                        return await method(view=self)
                    except:
                        try:
                            return await self.ctx.edit(view=self)
                        except:
                            return await method(view=self)
                else:
                    return await method(view=self)
            except:
                return await self.ctx.edit(view=self)

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        """
        This function handles the profile select

        Args:
            select: The select
            interaction: The interaction
        """
        await select_change_profile(self, select, interaction, self.desired_lang)

    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "device") & await timeout_check_processing(self,
                                                                                                              self.client,
                                                                                                              interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Authenticate", emoji="locked")
    async def enter_your_account_to_be_stolen_button(self, button, interaction):
        """
        This function handles authentication button

        Args:
            button:
            interaction:
        """
        modal = StealAccountLoginDetailsModal(self, self.user_document, self.client, self.ctx,
                                              self.currently_selected_profile_id, self.desired_lang)
        await interaction.response.send_modal(modal)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Auth With Session", emoji="library_input")
    async def existing_account_that_we_already_stole_button(self, button, interaction):
        """
        This function handles the existing auth button

        Args:
            button: The button
            interaction: The interaction
        """
        """I dont know if you meant to delete this, but heres what was here before:
        modal = StealAccountLoginDetailsModal(self, self.user_document, self.client, self.ctx,
                                              self.currently_selected_profile_id, self.ios_token)
        await interaction.response.send_modal(modal)
        """

        processing_embed = await stw.processing_embed(self.client, self.ctx, self.desired_lang)
        await interaction.response.edit_message(embed=processing_embed, view=None)

        await dont_sue_me_please_im_sorry_forgive_me(self.client, interaction, self.user_document,
                                                     self.currently_selected_profile_id, self.ctx, self.response_json,
                                                     self.desired_lang)


class StolenAccountView(discord.ui.View):
    """
    This class is the view for the EULA
    """

    def __init__(self, user_document, client, ctx, currently_selected_profile_id, interaction=None, embed=None,
                 extra_message=None, desired_lang=None):
        super().__init__(timeout=360.0)

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}
        self.interaction = interaction
        self.embed = embed
        self.desired_lang = desired_lang
        self.current_profile = user_document["profiles"][str(currently_selected_profile_id)]
        if extra_message is not None:
            self.message = extra_message
        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document, self.desired_lang)
        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1].label = stw.I18n.get('devauth.view.button.remove', self.desired_lang)
        self.children[2].label = stw.I18n.get('devauth.view.button.reauthenticate', self.desired_lang)
        self.timed_out = False
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))
        try:
            if self.user_document["auto_claim"]["enabled"]:
                self.children[3].label = stw.I18n.get('devauth.view.button.autoclaim.disable', self.desired_lang)
                self.children[3].style = discord.ButtonStyle.red
            else:
                self.children[3].label = stw.I18n.get('devauth.view.button.autoclaim.enable', self.desired_lang)
                self.children[3].style = discord.ButtonStyle.green
        except:
            self.children[3].label = stw.I18n.get('devauth.view.button.autoclaim.enable', self.desired_lang)
            self.children[3].style = discord.ButtonStyle.green
        self.children[3].disabled = True
        try:
            if self.user_document["profiles"][str(self.currently_selected_profile_id)]["authentication"]["hasExpired"]:
                self.children[2].disabled = True
            else:
                self.children[2].disabled = False
        except:
            self.children[2].disabled = False

    async def on_timeout(self):
        """
        This function handles the timeout

        Returns:
            None
        """
        timeout_embed = await existing_dev_auth_embed(self.client, self.ctx, self.user_document["profiles"][
            str(self.currently_selected_profile_id)], self.currently_selected_profile_id, self.desired_lang,
                                                      self.user_document)

        timeout_embed.description += f"\u200b\n{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        self.stop()
        self.timed_out = True
        try:
            if self.interaction is None:
                return await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
            else:
                return await self.interaction.edit_original_response(embed=timeout_embed, view=self)
        except:
            try:
                if isinstance(self.message, discord.Interaction):
                    method = self.message.edit_original_response
                else:
                    try:
                        method = self.message.edit
                    except:
                        method = self.ctx.edit
                if isinstance(self.ctx, discord.ApplicationContext):
                    try:
                        return await method(view=self)
                    except:
                        try:
                            return await self.ctx.edit(view=self)
                        except:
                            return await method(view=self)
                else:
                    return await method(view=self)
            except:
                return await self.ctx.edit(view=self)

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        """
        This function handles the profile select

        Args:
            select: The select
            interaction: The interaction
        """

        await select_change_profile(self, select, interaction, self.desired_lang)

    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "device") & await timeout_check_processing(self,
                                                                                                              self.client,
                                                                                                              interaction)

    @discord.ui.button(style=discord.ButtonStyle.danger, label="Remove Link", emoji="library_trashcan")
    async def regain_soul_button(self, button, interaction):
        """
        This function handles the delete link button

        Args:
            button: The button
            interaction: The interaction
        """
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        self.currently_selected_profile_id = str(self.currently_selected_profile_id)
        self.user_document["profiles"][self.currently_selected_profile_id]["authentication"] = None

        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]

        await handle_dev_auth(self.client, self.ctx, interaction, self.user_document, desired_lang=self.desired_lang)

    @discord.ui.button(style=discord.ButtonStyle.green, label="Reauthenticate Now", emoji="library_floppydisc")
    async def sell_your_data_button(self, button, interaction):
        """
        This function handles the auth now button

        Args:
            button: The button
            interaction: The interaction
        """
        try:
            user_profile = await get_user_document(self.ctx, self.client, interaction.user.id,
                                                   desired_lang=self.desired_lang)
            ephemeral = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"][
                "ephemeral"]
        except:
            ephemeral = False
        await interaction.response.defer(ephemeral=ephemeral, invisible=False)
        try:
            del self.client.temp_auth[self.ctx.author.id]
        except:
            pass

        # for child in self.children:
        #     child.disabled = True
        # await interaction.response.edit_message(view=self)

        auth_stuff = await stw.get_or_create_auth_session(self.client, self.ctx, "device", "", True, False, True,
                                                          desired_lang=self.desired_lang)
        try:
            if isinstance(auth_stuff[2], list):
                embeds = auth_stuff[2]
            else:
                embeds = [auth_stuff[2]]
            try:
                self.children[2].disabled = False
                self.children[3].disabled = False
            except:
                pass
            return await interaction.edit_original_response(embeds=embeds)
        except:
            if isinstance(auth_stuff[2], list):
                embeds = auth_stuff[2]
            else:
                embeds = [auth_stuff[2]]
            return await interaction.edit_original_response(embeds=embeds)

        # if not self.timed_out:
        #     for child in self.children:
        #         child.disabled = False
        #     await interaction.edit_original_response(view=self)

    @discord.ui.button(style=discord.ButtonStyle.green, label="Enable Auto Claim", emoji="library_clock", disabled=True)
    async def temp_auto_claim_button(self, button, interaction):
        """
        This function handles the temporary auto claim button

        Args:
            button: The button
            interaction: The interaction
        """
        try:
            if self.user_document["auto_claim"]["enabled"]:
                self.user_document["auto_claim"] = None
                button.label = stw.I18n.get('devauth.view.button.autoclaim.enable', self.desired_lang)
                button.style = discord.ButtonStyle.green
                result = "devauth.embed.existing.processed.success.disable", "devauth.embed.existing.description4.enable"
            else:
                self.user_document["auto_claim"] = {
                    "enabled": True,
                }
                button.label = stw.I18n.get('devauth.view.button.autoclaim.disable', self.desired_lang)
                button.style = discord.ButtonStyle.red
                result = "devauth.embed.existing.processed.success.enable", "devauth.embed.existing.description4.disable"
        except:
            self.user_document["auto_claim"] = {
                "enabled": True,
            }
            button.label = stw.I18n.get('devauth.view.button.autoclaim.disable', self.desired_lang)
            button.style = discord.ButtonStyle.red
            result = "devauth.embed.existing.processed.success.enable", "devauth.embed.existing.description4.disable"
        self.client.processing_queue[self.ctx.author.id] = True
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.ctx.author.id]
        self.embed.description = (
            f"\u200b\n"
            f"{stw.I18n.get('profile.embed.currentlyselected', self.desired_lang, self.currently_selected_profile_id)}\n"
            f"```{self.current_profile['friendly_name']}```\u200b\n"
            f"{stw.I18n.get('devauth.embed.existing.description1', self.desired_lang)}\n\u200b\n "
            f"{stw.I18n.get('devauth.embed.existing.description2', self.desired_lang, self.client.config['emojis']['library_trashcan'])}\n\u200b\n"
            f"{stw.I18n.get('devauth.embed.existing.description3', self.desired_lang, self.client.config['emojis']['library_floppydisc'])}\n\u200b\n"
            f"{stw.I18n.get(result[1], self.desired_lang, self.client.config['emojis']['library_clock'])}\n\u200b\n"
            f"{stw.I18n.get('devauth.embed.existing.description5', self.desired_lang)}\n"
            f"```{self.current_profile['authentication']['displayName']}```\u200b\n"
            f"{stw.I18n.get(result[0], self.desired_lang)}\n\u200b"
        )
        await interaction.response.edit_message(view=self, embed=self.embed)


class EnslaveUserLicenseAgreementButton(discord.ui.View):
    """
    This class is the view for the EULA
    """

    def __init__(self, user_document, client, ctx, currently_selected_profile_id, interaction=None,
                 extra_message=None, desired_lang=None):
        super().__init__(timeout=480.0)

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}
        self.interaction = interaction
        self.desired_lang = desired_lang
        self.timed_out = False
        if extra_message is not None:
            self.message = extra_message
        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document, self.desired_lang)
        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1].label = stw.I18n.get('devauth.view.button.agreement', self.desired_lang)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        """
        This function handles the profile select

        Args:
            select: The select
            interaction: The interaction
        """

        await select_change_profile(self, select, interaction, self.desired_lang)

    async def on_timeout(self):
        """
        This function handles the timeout

        Returns:
            None
        """
        timeout_embed = await tos_acceptance_embed(self.user_document, self.client, self.currently_selected_profile_id,
                                                   self.ctx, self.desired_lang)
        timeout_embed.description += f"{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        self.stop()
        self.timed_out = True

        try:
            if self.interaction is None:
                return await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
            else:
                return await self.interaction.edit_original_response(embed=timeout_embed, view=self)
        except:
            try:
                if isinstance(self.message, discord.Interaction):
                    method = self.message.edit_original_response
                else:
                    try:
                        method = self.message.edit
                    except:
                        method = self.ctx.edit
                if isinstance(self.ctx, discord.ApplicationContext):
                    try:
                        return await method(view=self)
                    except:
                        try:
                            return await self.ctx.edit(view=self)
                        except:
                            return await method(view=self)
                else:
                    return await method(view=self)
            except:
                return await self.ctx.edit(view=self)

    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "devauth") & await timeout_check_processing(self,
                                                                                                               self.client,
                                                                                                               interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Accept Agreement", emoji="library_handshake")
    async def soul_selling_button(self, button, interaction):
        """
        This function handles the accept button

        Args:
            button: The button
            interaction: The interaction
        """
        await add_enslaved_user_accepted_license(self, interaction)
        await handle_dev_auth(self.client, self.ctx, interaction, self.user_document, desired_lang=self.desired_lang)


# cog for the device auth login command.
class ProfileAuth(ext.Cog):
    """
    This class is the cog for the device auth login command
    """

    def __init__(self, client):
        self.client = client

    async def devauth_command(self, ctx):
        """
        This function handles the device auth login command

        Args:
            ctx: The context
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        await handle_dev_auth(self.client, ctx, desired_lang=desired_lang)

    @ext.slash_command(name='device', name_localizations=stw.I18n.construct_slash_dict('devauth.slash.name'),
                       description='Create an authentication session that will keep you logged in for a long time',
                       description_localizations=stw.I18n.construct_slash_dict('devauth.slash.description'),
                       guild_ids=stw.guild_ids)
    async def slash_device(self, ctx: discord.ApplicationContext):
        """
        This function handles the device auth login slash command

        Args:
            ctx: The context
        """
        await command_counter(self.client, ctx.author.id)
        await self.devauth_command(ctx)

    @ext.command(name='device',
                 aliases=['devauth', 'dev', 'deviceauth', 'deviceauthcode', 'profileauth', 'proauth', 'evauth',
                          'dvauth', 'deauth', 'devuth', 'devath', 'devauh', 'devaut', 'ddevauth', 'deevauth',
                          'devvauth', 'devaauth', 'devauuth', 'devautth', 'devauthh', 'edvauth', 'dveauth', 'deavuth',
                          'devuath', 'devatuh', 'devauht', 'sevauth', 'eevauth', 'revauth', 'fevauth', 'cevauth',
                          'xevauth', 'dwvauth', 'd3vauth', 'd4vauth', 'drvauth', 'dfvauth', 'ddvauth', 'dsvauth',
                          'decauth', 'defauth', 'degauth', 'debauth', 'devquth', 'devwuth', 'devsuth', 'devxuth',
                          'devzuth', 'devayth', 'deva7th', 'deva8th', 'devaith', 'devakth', 'devajth', 'devahth',
                          'devaurh', 'devau5h', 'devau6h', 'devauyh', 'devauhh', 'devaugh', 'devaufh', 'devautg',
                          'devauty', 'devautu', 'devautj', 'devautn', 'devautb', 'sdevauth', 'dsevauth', 'edevauth',
                          'rdevauth', 'drevauth', 'fdevauth', 'dfevauth', 'cdevauth', 'dcevauth', 'xdevauth',
                          'dxevauth', 'dwevauth', 'dewvauth', 'd3evauth', 'de3vauth', 'd4evauth', 'de4vauth',
                          'dervauth', 'defvauth', 'dedvauth', 'desvauth', 'decvauth', 'devcauth', 'devfauth',
                          'degvauth', 'devgauth', 'debvauth', 'devbauth', 'devqauth', 'devaquth', 'devwauth',
                          'devawuth', 'devsauth', 'devasuth', 'devxauth', 'devaxuth', 'devzauth', 'devazuth',
                          'devayuth', 'devauyth', 'deva7uth', 'devau7th', 'deva8uth', 'devau8th', 'devaiuth',
                          'devauith', 'devakuth', 'devaukth', 'devajuth', 'devaujth', 'devahuth', 'devauhth',
                          'devaurth', 'devautrh', 'devau5th', 'devaut5h', 'devau6th', 'devaut6h', 'devautyh',
                          'devaugth', 'devautgh', 'devaufth', 'devautfh', 'devauthg', 'devauthy', 'devautuh',
                          'devauthu', 'devautjh', 'devauthj', 'devautnh', 'devauthn', 'devautbh', 'devauthb', 'evice',
                          'dvice', 'deice', 'devce', 'devie', 'devic', 'ddevice', 'deevice', 'devvice', 'deviice',
                          'devicce', 'devicee', 'edvice', 'dveice', 'deivce', 'devcie', 'deviec', 'sevice', 'eevice',
                          'revice', 'fevice', 'cevice', 'xevice', 'dwvice', 'd3vice', 'd4vice', 'drvice', 'dfvice',
                          'ddvice', 'dsvice', 'decice', 'defice', 'degice', 'debice', 'devuce', 'dev8ce', 'dev9ce',
                          'devoce', 'devlce', 'devkce', 'devjce', 'devixe', 'devide', 'devife', 'devive', 'devicw',
                          'devic3', 'devic4', 'devicr', 'devicf', 'devicd', 'devics', 'sdevice', 'dsevice', 'edevice',
                          'rdevice', 'drevice', 'fdevice', 'dfevice', 'cdevice', 'dcevice', 'xdevice', 'dxevice',
                          'dwevice', 'dewvice', 'd3evice', 'de3vice', 'd4evice', 'de4vice', 'dervice', 'defvice',
                          'dedvice', 'desvice', 'decvice', 'devcice', 'devfice', 'degvice', 'devgice', 'debvice',
                          'devbice', 'devuice', 'deviuce', 'dev8ice', 'devi8ce', 'dev9ice', 'devi9ce', 'devoice',
                          'devioce', 'devlice', 'devilce', 'devkice', 'devikce', 'devjice', 'devijce', 'devixce',
                          'devicxe', 'devidce', 'devicde', 'devifce', 'devicfe', 'devivce', 'devicve', 'devicwe',
                          'devicew', 'devic3e', 'device3', 'devic4e', 'device4', 'devicre', 'devicer', 'devicef',
                          'deviced', 'devicse', 'devices', 'avelogin', 'svelogin', 'saelogin', 'savlogin', 'saveogin',
                          'savelgin', 'saveloin', 'savelogn', 'savelogi', 'ssavelogin', 'saavelogin', 'savvelogin',
                          'saveelogin', 'savellogin', 'saveloogin', 'saveloggin', 'savelogiin', 'saveloginn',
                          'asvelogin', 'svaelogin', 'saevlogin', 'savleogin', 'saveolgin', 'savelgoin', 'saveloign',
                          'savelogni', 'aavelogin', 'wavelogin', 'eavelogin', 'davelogin', 'xavelogin', 'zavelogin',
                          'sqvelogin', 'swvelogin', 'ssvelogin', 'sxvelogin', 'szvelogin', 'sacelogin', 'safelogin',
                          'sagelogin', 'sabelogin', 'savwlogin', 'sav3login', 'sav4login', 'savrlogin', 'savflogin',
                          'savdlogin', 'savslogin', 'savekogin', 'saveoogin', 'savepogin', 'saveligin', 'savel9gin',
                          'savel0gin', 'savelpgin', 'savellgin', 'savelkgin', 'savelofin', 'savelotin', 'saveloyin',
                          'savelohin', 'savelobin', 'savelovin', 'savelogun', 'savelog8n', 'savelog9n', 'savelogon',
                          'savelogln', 'savelogkn', 'savelogjn', 'savelogib', 'savelogih', 'savelogij', 'savelogim',
                          'asavelogin', 'wsavelogin', 'swavelogin', 'esavelogin', 'seavelogin', 'dsavelogin',
                          'sdavelogin', 'xsavelogin', 'sxavelogin', 'zsavelogin', 'szavelogin', 'sqavelogin',
                          'saqvelogin', 'sawvelogin', 'sasvelogin', 'saxvelogin', 'sazvelogin', 'sacvelogin',
                          'savcelogin', 'safvelogin', 'savfelogin', 'sagvelogin', 'savgelogin', 'sabvelogin',
                          'savbelogin', 'savwelogin', 'savewlogin', 'sav3elogin', 'save3login', 'sav4elogin',
                          'save4login', 'savrelogin', 'saverlogin', 'saveflogin', 'savdelogin', 'savedlogin',
                          'savselogin', 'saveslogin', 'saveklogin', 'savelkogin', 'saveologin', 'saveplogin',
                          'savelpogin', 'saveliogin', 'saveloigin', 'savel9ogin', 'savelo9gin', 'savel0ogin',
                          'savelo0gin', 'savelopgin', 'savelolgin', 'savelokgin', 'savelofgin', 'savelogfin',
                          'savelotgin', 'savelogtin', 'saveloygin', 'savelogyin', 'savelohgin', 'saveloghin',
                          'savelobgin', 'savelogbin', 'savelovgin', 'savelogvin', 'saveloguin', 'savelogiun',
                          'savelog8in', 'savelogi8n', 'savelog9in', 'savelogi9n', 'savelogoin', 'savelogion',
                          'saveloglin', 'savelogiln', 'savelogkin', 'savelogikn', 'savelogjin', 'savelogijn',
                          'savelogibn', 'saveloginb', 'savelogihn', 'saveloginh', 'saveloginj', 'savelogimn',
                          'saveloginm', 'rofileauth', 'pofileauth', 'prfileauth', 'proileauth', 'profleauth',
                          'profieauth', 'profilauth', 'profileuth', 'profileath', 'profileauh', 'profileaut',
                          'pprofileauth', 'prrofileauth', 'proofileauth', 'proffileauth', 'profiileauth',
                          'profilleauth', 'profileeauth', 'profileaauth', 'profileauuth', 'profileautth',
                          'profileauthh', 'rpofileauth', 'porfileauth', 'prfoileauth', 'proifleauth', 'proflieauth',
                          'profielauth', 'profilaeuth', 'profileuath', 'profileatuh', 'profileauht', 'orofileauth',
                          '0rofileauth', 'lrofileauth', 'peofileauth', 'p4ofileauth', 'p5ofileauth', 'ptofileauth',
                          'pgofileauth', 'pfofileauth', 'pdofileauth', 'prifileauth', 'pr9fileauth', 'pr0fileauth',
                          'prpfileauth', 'prlfileauth', 'prkfileauth', 'prodileauth', 'prorileauth', 'protileauth',
                          'progileauth', 'provileauth', 'procileauth', 'profuleauth', 'prof8leauth', 'prof9leauth',
                          'profoleauth', 'proflleauth', 'profkleauth', 'profjleauth', 'profikeauth', 'profioeauth',
                          'profipeauth', 'profilwauth', 'profil3auth', 'profil4auth', 'profilrauth', 'profilfauth',
                          'profildauth', 'profilsauth', 'profilequth', 'profilewuth', 'profilesuth', 'profilexuth',
                          'profilezuth', 'profileayth', 'profilea7th', 'profilea8th', 'profileaith', 'profileakth',
                          'profileajth', 'profileahth', 'profileaurh', 'profileau5h', 'profileau6h', 'profileauyh',
                          'profileauhh', 'profileaugh', 'profileaufh', 'profileautg', 'profileauty', 'profileautu',
                          'profileautj', 'profileautn', 'profileautb', 'oprofileauth', 'porofileauth', '0profileauth',
                          'p0rofileauth', 'lprofileauth', 'plrofileauth', 'perofileauth', 'preofileauth',
                          'p4rofileauth', 'pr4ofileauth', 'p5rofileauth', 'pr5ofileauth', 'ptrofileauth',
                          'prtofileauth', 'pgrofileauth', 'prgofileauth', 'pfrofileauth', 'prfofileauth',
                          'pdrofileauth', 'prdofileauth', 'priofileauth', 'proifileauth', 'pr9ofileauth',
                          'pro9fileauth', 'pr0ofileauth', 'pro0fileauth', 'prpofileauth', 'propfileauth',
                          'prlofileauth', 'prolfileauth', 'prkofileauth', 'prokfileauth', 'prodfileauth',
                          'profdileauth', 'prorfileauth', 'profrileauth', 'protfileauth', 'proftileauth',
                          'progfileauth', 'profgileauth', 'provfileauth', 'profvileauth', 'procfileauth',
                          'profcileauth', 'profuileauth', 'profiuleauth', 'prof8ileauth', 'profi8leauth',
                          'prof9ileauth', 'profi9leauth', 'profoileauth', 'profioleauth', 'proflileauth',
                          'profkileauth', 'profikleauth', 'profjileauth', 'profijleauth', 'profilkeauth',
                          'profiloeauth', 'profipleauth', 'profilpeauth', 'profilweauth', 'profilewauth',
                          'profil3eauth', 'profile3auth', 'profil4eauth', 'profile4auth', 'profilreauth',
                          'profilerauth', 'profilfeauth', 'profilefauth', 'profildeauth', 'profiledauth',
                          'profilseauth', 'profilesauth', 'profileqauth', 'profileaquth', 'profileawuth',
                          'profileasuth', 'profilexauth', 'profileaxuth', 'profilezauth', 'profileazuth',
                          'profileayuth', 'profileauyth', 'profilea7uth', 'profileau7th', 'profilea8uth',
                          'profileau8th', 'profileaiuth', 'profileauith', 'profileakuth', 'profileaukth',
                          'profileajuth', 'profileaujth', 'profileahuth', 'profileauhth', 'profileaurth',
                          'profileautrh', 'profileau5th', 'profileaut5h', 'profileau6th', 'profileaut6h',
                          'profileautyh', 'profileaugth', 'profileautgh', 'profileaufth', 'profileautfh',
                          'profileauthg', 'profileauthy', 'profileautuh', 'profileauthu', 'profileautjh',
                          'profileauthj', 'profileautnh', 'profileauthn', 'profileautbh', 'profileauthb', 'savelogin',
                          '/device', '/deviceauth', '/profileauth', '/savelogin', 'dauth', '/dauth', 'save', '/save',
                          '.save', '.autodaily', '.device', 'toestel', 'الجهاز', 'устройство', 'যন্ত্র', 'dispositiu',
                          'přístroj', 'enhed', 'Gerät', 'συσκευή', 'dispositivo', 'seade', 'دستگاه', 'laite',
                          'appareil', 'ઉપકરણ', 'na\'urar', 'התקן', 'उपकरण', 'uređaj', 'eszköz', 'perangkat', 'デバイス',
                          '기기', 'prietaisas', 'ierīci', 'डिव्हाइस', 'peranti', 'apparaat', 'enhet', 'ਜੰਤਰ',
                          'urządzenie', 'dispozitiv', 'zariadenie', 'уређај', 'kifaa', 'சாதனம்', 'పరికరం', 'อุปกรณ์',
                          'cihaz', 'آلہ', 'thiết bị', '设备', '設備', 'autoclaim', 'auto', '/autoclaim', '/auto',
                          '.auto', 'autodaily', '/autodaily', 'autoclaimdaily', 'thiếtbị', 'devzice', 'devicp',
                          'devicej', 'deuvice', 'devize', 'devyce', 'demice', 'devici', 'odevice', 'devfce', 'divice',
                          'dezvice', 'devnice', 'deviae', 'denice', 'devicev', 'dpvice', 'dewice', 'devisce', 'idevice',
                          'dqvice', 'deivice', 'devicb', 'devimce', 'hdevice', 'dhvice', 'deviace', 'devicne', 'deqice',
                          'nevice', 'bdevice', 'demvice', 'dkvice', 'devicje', 'dexice', 'devise', 'devime', 'devico',
                          'uevice', 'devince', 'devirce', 'devigce', 'deovice', 'devicu', 'devine', 'dehice', 'devxice',
                          'deaice', 'deoice', 'ldevice', 'devrce', 'devpce', 'kdevice', 'devtice', 'dekice', 'devicoe',
                          'devipe', 'dnvice', 'deviee', 'devqce', 'devhice', 'deviwe', 'pevice', 'devmice', 'devicbe',
                          'deviue', 'mdevice', 'deviceg', 'doevice', 'aevice', 'djevice', 'deyice', 'deuice', 'dmevice',
                          'detice', 'deviqce', 'devicke', 'devioe', 'deviyce', 'deviceb', 'dgvice', 'deviece',
                          'devicea', 'zevice', 'devica', 'devicle', 'deeice', 'devece', 'devicue', 'pdevice', 'davice',
                          'deyvice', 'deviceh', 'devihce', 'vdevice', 'devibce', 'devicm', 'devicel', 'devicex',
                          'dlevice', 'jevice', 'delice', 'devicem', 'devwice', 'vevice', 'devije', 'kevice', 'devipce',
                          'desice', 'depvice', 'dezice', 'dehvice', 'tdevice', 'devicv', 'dtvice', 'devicx', 'devcce',
                          'dzevice', 'deviie', 'devtce', 'devicc', 'devnce', 'devqice', 'detvice', 'hevice', 'devicge',
                          'dedice', 'devicn', 'dexvice', 'devicec', 'devike', 'dlvice', 'devvce', 'devibe', 'dxvice',
                          'devyice', 'dejvice', 'devicen', 'devgce', 'devicg', 'devitce', 'deviceu', 'dejice',
                          'devicet', 'delvice', 'devmce', 'devicei', 'gevice', 'oevice', 'qevice', 'devicy', 'devicie',
                          'deqvice', 'devile', 'jdevice', 'devicae', 'devicz', 'dvevice', 'wevice', 'mevice', 'wdevice',
                          'devwce', 'gdevice', 'tevice', 'devicek', 'deavice', 'devicye', 'devrice', 'dbvice',
                          'dtevice', 'devicez', 'duevice', 'dkevice', 'devdice', 'dovice', 'devite', 'udevice',
                          'devicpe', 'adevice', 'ievice', 'dmvice', 'dqevice', 'deviche', 'devhce', 'deiice', 'devicme',
                          'deviqe', 'derice', 'dvvice', 'qdevice', 'dyevice', 'devbce', 'devicqe', 'dcvice', 'deviwce',
                          'dyvice', 'djvice', 'devich', 'dpevice', 'devsce', 'dhevice', 'devpice', 'deviceo', 'devicl',
                          'devicze', 'deveice', 'depice', 'dbevice', 'duvice', 'denvice', 'devace', 'devzce', 'zdevice',
                          'dgevice', 'devizce', 'devicte', 'dievice', 'levice', 'ydevice', 'deviceq', 'yevice',
                          'devicq', 'devdce', 'devict', 'devicj', 'devire', 'bevice', 'dnevice', 'devihe', 'devsice',
                          'devicey', 'devicep', 'deviye', 'devige', 'dzvice', 'dekvice', 'devxce', 'daevice', 'ndevice',
                          'devick', 'devaice', 'd2vice', 'd$vice', 'd#vice', 'd@vice', 'dev7ce', 'dev&ce', 'dev*ce',
                          'dev(ce', 'devic2', 'devic$', 'devic#', 'devic@', 'devautho', 'djevauth', 'devanuth',
                          'devautp', 'demvauth', 'devauqh', 'dhevauth', 'devbuth', 'devatth', 'devautr', 'devluth',
                          'tevauth', 'devaputh', 'dejvauth', 'dkvauth', 'qdevauth', 'yevauth', 'dewauth', 'detauth',
                          'demauth', 'deveuth', 'devouth', 'devarth', 'wevauth', 'devauthe', 'delauth', 'desauth',
                          'devaduth', 'devasth', 'devauthd', 'devauoh', 'depauth', 'devawth', 'devavuth', 'devautm',
                          'deiauth', 'dvvauth', 'devauxh', 'ldevauth', 'devauwth', 'devaumh', 'devguth', 'dlevauth',
                          'zdevauth', 'dyevauth', 'devafth', 'devaueh', 'dzvauth', 'deoauth', 'ydevauth', 'deviuth',
                          'devauthi', 'devauta', 'devtuth', 'duvauth', 'devmuth', 'dgvauth', 'bdevauth', 'devauzth',
                          'kevauth', 'dovauth', 'denauth', 'dnevauth', 'aevauth', 'devaudh', 'mdevauth', 'djvauth',
                          'devauti', 'devaudth', 'devruth', 'devautha', 'deqauth', 'doevauth', 'devauths', 'devaouth',
                          'devautz', 'devaukh', 'devjuth', 'devauvh', 'deivauth', 'dmevauth', 'devhauth', 'devauph',
                          'devauthl', 'duevauth', 'devfuth', 'devacth', 'devauthk', 'mevauth', 'hdevauth', 'dqevauth',
                          'devauthp', 'devautv', 'devanth', 'devaguth', 'devabuth', 'devrauth', 'deveauth', 'detvauth',
                          'devauuh', 'davauth', 'devautvh', 'delvauth', 'daevauth', 'devagth', 'deqvauth', 'devautph',
                          'dejauth', 'dmvauth', 'dehauth', 'devautwh', 'devauthz', 'devlauth', 'dbvauth', 'devamuth',
                          'devcuth', 'uevauth', 'dpevauth', 'deeauth', 'vevauth', 'devauoth', 'devautht', 'devafuth',
                          'divauth', 'devabth', 'kdevauth', 'devautk', 'devautw', 'deovauth', 'dhvauth', 'devaulth',
                          'devauthv', 'devazth', 'devtauth', 'devauto', 'dlvauth', 'devnuth', 'devauthr', 'adevauth',
                          'deyauth', 'devaunh', 'devautmh', 'devduth', 'devautc', 'devaueth', 'devaluth', 'devalth',
                          'devatuth', 'dexauth', 'devkauth', 'pevauth', 'dedauth', 'devapth', 'dexvauth', 'devautzh',
                          'dgevauth', 'devauah', 'devhuth', 'devaucth', 'devuuth', 'devauch', 'qevauth', 'deyvauth',
                          'devaqth', 'dekvauth', 'jevauth', 'devauts', 'devautkh', 'devautsh', 'deviauth', 'dqvauth',
                          'devaujh', 'devmauth', 'devyauth', 'derauth', 'devauxth', 'devaulh', 'devauqth', 'devautdh',
                          'dcvauth', 'devaupth', 'devavth', 'devjauth', 'dekauth', 'devausth', 'dpvauth', 'gevauth',
                          'devuauth', 'devauthf', 'dbevauth', 'devaumth', 'devauteh', 'dvevauth', 'devaubh', 'udevauth',
                          'tdevauth', 'devpauth', 'devauthx', 'devaeuth', 'dyvauth', 'dnvauth', 'deaauth', 'devautch',
                          'devauthm', 'devaeth', 'vdevauth', 'levauth', 'devautf', 'devautih', 'devautq', 'dezvauth',
                          'gdevauth', 'depvauth', 'wdevauth', 'dtvauth', 'dezauth', 'devauvth', 'devvuth', 'nevauth',
                          'devauthc', 'devauzh', 'devadth', 'ievauth', 'bevauth', 'ndevauth', 'devaush', 'dkevauth',
                          'dehvauth', 'devautah', 'devamth', 'deavauth', 'zevauth', 'pdevauth', 'dxvauth', 'devaoth',
                          'jdevauth', 'devautoh', 'odevauth', 'deuvauth', 'devauthw', 'oevauth', 'devaath', 'devacuth',
                          'devautd', 'devauthq', 'dievauth', 'devyuth', 'devoauth', 'devaute', 'devaubth', 'devaruth',
                          'devnauth', 'devaxth', 'deuauth', 'devauwh', 'devautt', 'devautx', 'idevauth', 'devautxh',
                          'devkuth', 'devauath', 'devautl', 'devautqh', 'devautlh', 'denvauth', 'devputh', 'dtevauth',
                          'devauih', 'devdauth', 'hevauth', 'dzevauth', 'devaunth', 'd2vauth', 'd$vauth', 'd#vauth',
                          'd@vauth', 'deva6th', 'deva^th', 'deva&th', 'deva*th', 'devau4h', 'devau$h', 'devau%h',
                          'devau^h', 'svae', 'sanve', 'ssve', 'saev', 'asve', 'savz', 'savse', 'ave', 'sve', 'nsave',
                          'sav', 'savv', 'suave', 'smve', 'savke', 'savx', 'saveo', 'savze', 'saven', 'sajve', 'yave',
                          'savt', 'savey', 'tsave', 'cave', 'uave', 'savqe', 'sgve', 'xsave', 'savve', 'usave', 'saove',
                          'safve', 'sawve', 'savk', 'saye', 'jsave', 'saveg', 'oave', 'mave', 'sae', 'savce', 'sagve',
                          'sale', 'wave', 'sxave', 'sive', 'ssave', 'svve', 'sqve', 'aave', 'savb', 'savm', 'saqve',
                          'wsave', 'skave', 'savxe', 'saveb', 'skve', 'msave', 'savei', 'shave', 'saee', 'scve', 'vave',
                          'rsave', 'sasve', 'eave', 'savo', 'syave', 'sove', 'savj', 'savef', 'sape', 'qsave', 'sahve',
                          'sapve', 'saave', 'savl', 'bave', 'sadve', 'stave', 'sfave', 'sava', 'spve', 'saje', 'savme',
                          'swve', 'savw', 'savpe', 'ysave', 'fsave', 'swave', 'savge', 'qave', 'gave', 'saue', 'sahe',
                          'sdve', 'saves', 'sfve', 'seve', 'savd', 'savex', 'savee', 'sbve', 'sane', 'sace', 'saze',
                          'szve', 'savej', 'csave', 'sase', 'sjave', 'saved', 'saie', 'savne', 'rave', 'savew', 'nave',
                          'sabe', 'satve', 'samve', 'sdave', 'shve', 'saxve', 'srave', 'pave', 'sakve', 'savn', 'saveu',
                          'fave', 'sayve', 'slave', 'savre', 'sabve', 'sake', 'svave', 'sade', 'savg', 'savet', 'savp',
                          'savf', 'hsave', 'saoe', 'savle', 'sawe', 'stve', 'snave', 'savep', 'sare', 'sqave', 'xave',
                          'suve', 'saive', 'savie', 'sacve', 'lsave', 'savc', 'zave', 'sxve', 'dave', 'snve', 'iave',
                          'soave', 'lave', 'jave', 'savde', 'zsave', 'osave', 'savje', 'savev', 'savr', 'savu', 'sgave',
                          'savi', 'sage', 'sauve', 'saxe', 'savoe', 'saae', 'have', 'sjve', 'sarve', 'dsave',
                          'savek', 'saver', 'savs', 'savh', 'saveh', 'srve', 'slve', 'savhe', 'vsave', 'kave', 'sbave',
                          'isave', 'siave', 'savwe', 'savbe', 'savye', 'smave', 'tave', 'gsave', 'safe', 'sate',
                          'psave', 'szave', 'savfe', 'scave', 'saveq', 'savel', 'saqe', 'sazve', 'syve', 'asave',
                          'same', 'savem', 'spave', 'salve', 'savte', 'esave', 'seave', 'savy', 'ksave', 'savue',
                          'savec', 'savez', 'savae', 'saeve', 'savq', 'savea', 'sav4', 'sav3', 'sav2', 'sav$', 'sav#',
                          'sav@', 'svvelogin', 'savelogcn', 'savielogin', 'saovelogin', 'saveloginl', 'savelomin',
                          'sapvelogin', 'savelcogin', 'suvelogin', 'yavelogin', 'savelqgin', 'saveloggn', 'savelygin',
                          'saveloginc', 'savelogiq', 'saveltogin', 'uavelogin', 'savelogizn', 'saveloghn', 'savelogitn',
                          'skvelogin', 'savilogin', 'saveloein', 'savelogip', 'saveloqgin', 'savelogbn', 'savelogzn',
                          'savxlogin', 'savelogqn', 'savelojgin', 'savelogino', 'oavelogin', 'savelxgin', 'saveloginu',
                          'savelogifn', 'savelaogin', 'savelogian', 'savzlogin', 'srvelogin', 'savegogin', 'saveulogin',
                          'savelocin', 'savevogin', 'sarvelogin', 'gavelogin', 'savelojin', 'spavelogin', 'savllogin',
                          'jsavelogin', 'syvelogin', 'savelfogin', 'savenogin', 'stvelogin', 'saoelogin', 'saveloain',
                          'savelogyn', 'sdvelogin', 'scavelogin', 'sahelogin', 'sayelogin', 'savelokin', 'snvelogin',
                          'navelogin', 'savelbogin', 'sbavelogin', 'saveloginf', 'savelvgin', 'saveldogin',
                          'saveloging', 'saveyogin', 'savelooin', 'saselogin', 'sevelogin', 'syavelogin', 'savelwogin',
                          'saveloxgin', 'suavelogin', 'savelogiu', 'saveloginw', 'savelogic', 'lavelogin', 'savelozin',
                          'savelhogin', 'savelogidn', 'savelogind', 'savewogin', 'savelogsn', 'shavelogin', 'savplogin',
                          'savclogin', 'savelomgin', 'savezogin', 'sauvelogin', 'savelognin', 'savologin', 'sravelogin',
                          'saveloginq', 'savblogin', 'savelogpn', 'savefogin', 'saveeogin', 'savelogan', 'scvelogin',
                          'sfvelogin', 'saveilogin', 'savelogsin', 'saveljogin', 'savelouin', 'savelogid', 'psavelogin',
                          'saxelogin', 'saivelogin', 'savelogzin', 'savejogin', 'sajelogin', 'sjvelogin', 'savelogiy',
                          'sarelogin', 'savelogiv', 'spvelogin', 'vsavelogin', 'savelognn', 'slvelogin', 'sjavelogin',
                          'kavelogin', 'savelogqin', 'savelogdn', 'satvelogin', 'saveglogin', 'iavelogin', 'savelagin',
                          'savelosin', 'vavelogin', 'savelfgin', 'savelmogin', 'savelozgin', 'savlelogin', 'savelorin',
                          'savelolin', 'savelogina', 'savejlogin', 'savxelogin', 'savelogxn', 'savelyogin',
                          'savelogain', 'savelogcin', 'saveylogin', 'saveiogin', 'hsavelogin', 'tsavelogin',
                          'havelogin', 'savelcgin', 'savelxogin', 'csavelogin', 'ravelogin', 'savelrgin', 'savelugin',
                          'pavelogin', 'savmlogin', 'savelogit', 'saqelogin', 'favelogin', 'savelggin', 'savexogin',
                          'savelogix', 'savelogint', 'nsavelogin', 'sajvelogin', 'saveloxin', 'sadvelogin',
                          'savelodgin', 'savelogink', 'sanvelogin', 'savexlogin', 'snavelogin', 'saveltgin',
                          'savelzgin', 'savelogie', 'savalogin', 'sakelogin', 'javelogin', 'savelorgin', 'saveuogin',
                          'savelogif', 'savetogin', 'savelosgin', 'lsavelogin', 'siavelogin', 'savehlogin',
                          'savzelogin', 'saveclogin', 'savoelogin', 'savelogine', 'savelogxin', 'saveloginz',
                          'saeelogin', 'sawelogin', 'savelougin', 'sovelogin', 'savhelogin', 'saveblogin', 'saveqogin',
                          'saveljgin', 'savelogig', 'savemlogin', 'savelogdin', 'savelogfn', 'cavelogin', 'svavelogin',
                          'smvelogin', 'saveloginp', 'savelogil', 'savelogia', 'savelongin', 'saveloginv', 'slavelogin',
                          'sahvelogin', 'savelogrin', 'savelogwn', 'savelzogin', 'savelogiw', 'savelogivn',
                          'savelogiyn', 'smavelogin', 'savelogik', 'savelhgin', 'qsavelogin', 'osavelogin',
                          'savkelogin', 'savetlogin', 'savelogrn', 'savezlogin', 'savebogin', 'savelmgin', 'savelogixn',
                          'savelwgin', 'savelqogin', 'saveluogin', 'savelogicn', 'saverogin', 'sauelogin', 'savjlogin',
                          'savelogisn', 'savylogin', 'savelowin', 'mavelogin', 'bsavelogin', 'shvelogin', 'saaelogin',
                          'fsavelogin', 'savelogign', 'savelogen', 'saveloginr', 'savpelogin', 'savvlogin', 'savelogir',
                          'savemogin', 'sbvelogin', 'msavelogin', 'sanelogin', 'savuelogin', 'savulogin', 'savelrogin',
                          'savnelogin', 'savelogis', 'savtlogin', 'salelogin', 'savelsogin', 'savedogin', 'savmelogin',
                          'savealogin', 'savglogin', 'tavelogin', 'sayvelogin', 'saevelogin', 'sazelogin', 'stavelogin',
                          'savelogmn', 'bavelogin', 'savjelogin', 'savelogio', 'rsavelogin', 'savelogiwn', 'savelogien',
                          'skavelogin', 'savelopin', 'sadelogin', 'savelogvn', 'ksavelogin', 'sfavelogin', 'saveldgin',
                          'saveloginy', 'savelogipn', 'saveloiin', 'savesogin', 'satelogin', 'savelogtn', 'savelgogin',
                          'salvelogin', 'savehogin', 'sivelogin', 'savelogmin', 'saveleogin', 'ysavelogin',
                          'isavelogin', 'saveloginx', 'savqelogin', 'savaelogin', 'soavelogin', 'savhlogin',
                          'savelogwin', 'samvelogin', 'sapelogin', 'savelogpin', 'savtelogin', 'savnlogin',
                          'savelogins', 'savevlogin', 'saveqlogin', 'savecogin', 'sgvelogin', 'savelegin', 'saveloagin',
                          'saielogin', 'savelogirn', 'savelonin', 'savelsgin', 'savelowgin', 'savyelogin', 'savenlogin',
                          'savqlogin', 'savelnogin', 'gsavelogin', 'savelvogin', 'sgavelogin', 'savelbgin',
                          'sakvelogin', 'usavelogin', 'saveaogin', 'savelogein', 'qavelogin', 'savklogin', 'savelodin',
                          'savelogiqn', 'savelngin', 'savelogii', 'savelocgin', 'samelogin', 'savelogini', 'saveloqin',
                          'savelogiz', 'saveloegin', 'sav2login', 'sav$login', 'sav#login', 'sav@login', 'save;ogin',
                          'save/ogin', 'save.ogin', 'save,ogin', 'save?ogin', 'save>ogin', 'save<ogin', 'savel8gin',
                          'savel;gin', 'savel*gin', 'savel(gin', 'savel)gin', 'savelog7n', 'savelog&n', 'savelog*n',
                          'savelog(n', 'savelogi,', 'savelogi<', 'profilceauth', 'qprofileauth', 'profilenuth',
                          'pjofileauth', 'profileauph', 'profivleauth', 'profhileauth', 'prbfileauth', 'fprofileauth',
                          'pirofileauth', 'profilieauth', 'nrofileauth', 'profilealuth', 'profilnauth', 'profileauxh',
                          'profilecauth', 'pwofileauth', 'profileaujh', 'profileauthf', 'prwfileauth', 'profileaath',
                          'pruofileauth', 'pkofileauth', 'profinleauth', 'proufileauth', 'profiueauth', 'profileauoh',
                          'profiqeauth', 'profireauth', 'przofileauth', 'probfileauth', 'prsfileauth', 'profiqleauth',
                          'profileautah', 'profileaulth', 'pvofileauth', 'grofileauth', 'pqofileauth', 'profilxauth',
                          'profiljeauth', 'iprofileauth', 'prwofileauth', 'purofileauth', 'piofileauth', 'profileamth',
                          'profilmeauth', 'profilejauth', 'profyileauth', 'prozileauth', 'profrleauth', 'profilefuth',
                          'hprofileauth', 'poofileauth', 'prtfileauth', 'profileauths', 'profileaumh', 'proiileauth',
                          'profileamuth', 'profilevuth', 'profieeauth', 'profileouth', 'prozfileauth', 'profileaupth',
                          'rrofileauth', 'prokileauth', 'profileputh', 'profilehuth', 'paofileauth', 'profnleauth',
                          'promileauth', 'profileduth', 'profileaulh', 'profileabth', 'profilyeauth', 'prohfileauth',
                          'profiveauth', 'profileauzth', 'profileauvh', 'profileaudh', 'crofileauth', 'proqileauth',
                          'drofileauth', 'profbleauth', 'profileauthz', 'prxofileauth', 'profileauoth', 'profillauth',
                          'profileautk', 'proficeauth', 'profiletuth', 'propileauth', 'profileautp', 'profileautdh',
                          'profiweauth', 'profigeauth', 'profileauthl', 'prnofileauth', 'profileacth', 'profileautkh',
                          'profilejuth', 'proffleauth', 'proficleauth', 'prooileauth', 'profqileauth', 'prolileauth',
                          'profialeauth', 'profileauih', 'profileautxh', 'pjrofileauth', 'profiletauth', 'profileautch',
                          'profiteauth', 'zprofileauth', 'ppofileauth', 'profmleauth', 'projfileauth', 'profileauta',
                          'prouileauth', 'psofileauth', 'profileauthr', 'prhofileauth', 'profileauthw', 'profileauch',
                          'phofileauth', 'pronileauth', 'profilpauth', 'profilebuth', 'profqleauth', 'arofileauth',
                          'plofileauth', 'profileautr', 'rprofileauth', 'profileautha', 'profiaeauth', 'prcfileauth',
                          'profileauah', 'profxleauth', 'profileauqh', 'wprofileauth', 'profileyuth', 'profileafth',
                          'trofileauth', 'profileautph', 'profileautc', 'proyileauth', 'profileluth', 'profileauthk',
                          'profileabuth', 'jrofileauth', 'dprofileauth', 'profileauthv', 'profilheauth', 'profileazth',
                          'pcofileauth', 'pxrofileauth', 'prsofileauth', 'profijeauth', 'probileauth', 'profimeauth',
                          'profigleauth', 'pbrofileauth', 'profibeauth', 'profileatth', 'profileapth', 'profibleauth',
                          'profilearth', 'praofileauth', 'profileruth', 'profeleauth', 'prvfileauth', 'profsileauth',
                          'profileaeth', 'profiheauth', 'cprofileauth', 'profmileauth', 'pqrofileauth', 'pronfileauth',
                          'pnofileauth', 'profileauwh', 'profpileauth', 'profilteauth', 'puofileauth', 'pvrofileauth',
                          'profileagth', 'profilyauth', 'profiljauth', 'profileadth', 'profileuauth', 'profizeauth',
                          'profileauvth', 'phrofileauth', 'profilearuth', 'profixleauth', 'profileauteh', 'profileaoth',
                          'profidleauth', 'profizleauth', 'profileaudth', 'prosileauth', 'profileaush', 'urofileauth',
                          'mrofileauth', 'xrofileauth', 'profbileauth', 'profimleauth', 'profileaukh', 'profileoauth',
                          'profirleauth', 'profilekuth', 'profiloauth', 'prosfileauth', 'profiluauth', 'profileauthx',
                          'profilaeauth', 'profileauthi', 'prohileauth', 'projileauth', 'prmofileauth', 'profileauts',
                          'pzofileauth', 'profileautsh', 'profsleauth', 'profilbeauth', 'profileuuth', 'profileaubth',
                          'aprofileauth', 'proqfileauth', 'profileaqth', 'profilmauth', 'prbofileauth', 'profyleauth',
                          'profileaputh', 'profileauthq', 'profileauqth', 'pxofileauth', 'profileautt', 'promfileauth',
                          'profwileauth', 'profileautv', 'profilecuth', 'proeileauth', 'profileautht', 'profileaguth',
                          'pwrofileauth', 'pkrofileauth', 'profileanth', 'qrofileauth', 'prowileauth', 'tprofileauth',
                          'profxileauth', 'prgfileauth', 'uprofileauth', 'sprofileauth', 'profaileauth', 'pmofileauth',
                          'profileauto', 'mprofileauth', 'prnfileauth', 'profiyleauth', 'irofileauth', 'profilaauth',
                          'profileautq', 'pbofileauth', 'prufileauth', 'profileanuth', 'profilemauth', 'proxfileauth',
                          'profileasth', 'profilzauth', 'profileautho', 'profilemuth', 'profiyeauth', 'profgleauth',
                          'pyrofileauth', 'eprofileauth', 'profilneauth', 'proyfileauth', 'erofileauth', 'profilkauth',
                          'profileaueh', 'nprofileauth', 'pryfileauth', 'profileaunth', 'profilxeauth', 'profilegauth',
                          'psrofileauth', 'hrofileauth', 'frofileauth', 'prowfileauth', 'profileavuth', 'profpleauth',
                          'profixeauth', 'profileauti', 'profilbauth', 'prqfileauth', 'profilehauth', 'profilevauth',
                          'profileaumth', 'proftleauth', 'profileautl', 'profilqauth', 'profilhauth', 'profileguth',
                          'profdleauth', 'profileawth', 'proxileauth', 'profileaunh', 'profileaubh', 'zrofileauth',
                          'profifleauth', 'profileauthp', 'profileautf', 'prqofileauth', 'profileiauth', 'profileauthm',
                          'profileauzh', 'profileauwth', 'profilelauth', 'prefileauth', 'profideauth', 'prhfileauth',
                          'profileaute', 'prjfileauth', 'prcofileauth', 'profileafuth', 'profineauth', 'profiseauth',
                          'profileautoh', 'profileaeuth', 'profilueauth', 'profvleauth', 'profeileauth', 'krofileauth',
                          'profileautw', 'profilzeauth', 'profileaucth', 'profileavth', 'profzileauth', 'kprofileauth',
                          'yprofileauth', 'gprofileauth', 'parofileauth', 'profilepauth', 'profileautmh', 'profzleauth',
                          'profileatuth', 'profileeuth', 'vprofileauth', 'profileautzh', 'profilebauth', 'prvofileauth',
                          'profilenauth', 'profileautqh', 'profiwleauth', 'profnileauth', 'pcrofileauth',
                          'profisleauth', 'profileaxth', 'profaleauth', 'srofileauth', 'profieleauth', 'bprofileauth',
                          'profcleauth', 'profileautwh', 'vrofileauth', 'jprofileauth', 'profileiuth', 'profileautd',
                          'proaileauth', 'profilqeauth', 'profitleauth', 'profileauxth', 'proafileauth', 'profileautih',
                          'prdfileauth', 'profilveauth', 'prafileauth', 'profileautx', 'profhleauth', 'prffileauth',
                          'przfileauth', 'pyofileauth', 'profilealth', 'xprofileauth', 'profileaduth', 'profihleauth',
                          'profiltauth', 'profwleauth', 'profileacuth', 'pnrofileauth', 'profileaouth', 'brofileauth',
                          'profilgeauth', 'profiliauth', 'prxfileauth', 'profifeauth', 'profileauthe', 'prmfileauth',
                          'profileausth', 'profileautlh', 'profilcauth', 'profileauthc', 'profileauthd', 'profileautz',
                          'profiieauth', 'pzrofileauth', 'profileauuh', 'profileauath', 'prjofileauth', 'profileautvh',
                          'prrfileauth', 'wrofileauth', 'proefileauth', 'profilgauth', 'profileautm', 'profileaueth',
                          'pmrofileauth', 'yrofileauth', 'pryofileauth', 'profileyauth', 'profilekauth', 'profilvauth',
                          '9rofileauth', '-rofileauth', '[rofileauth', ']rofileauth', ';rofileauth', '(rofileauth',
                          ')rofileauth', '_rofileauth', '=rofileauth', '+rofileauth', '{rofileauth', '}rofileauth',
                          ':rofileauth', 'p3ofileauth', 'p#ofileauth', 'p$ofileauth', 'p%ofileauth', 'pr8fileauth',
                          'pr;fileauth', 'pr*fileauth', 'pr(fileauth', 'pr)fileauth', 'prof7leauth', 'prof&leauth',
                          'prof*leauth', 'prof(leauth', 'profi;eauth', 'profi/eauth', 'profi.eauth', 'profi,eauth',
                          'profi?eauth', 'profi>eauth', 'profi<eauth', 'profil2auth', 'profil$auth', 'profil#auth',
                          'profil@auth', 'profilea6th', 'profilea^th', 'profilea&th', 'profilea*th', 'profileau4h',
                          'profileau$h', 'profileau%h', 'profileau^h', 'deviceauht', 'devgiceauth', 'deivceauth',
                          'dhviceauth', 'deiiceauth', 'hdeviceauth', 'deviceatuh', 'devicerauth', 'devceauth',
                          'deviceahth', 'dleviceauth', 'devcieauth', 'dfviceauth', 'devticeauth', 'devicaeuth',
                          'devieauth', 'deviceauoth', 'deviceuath', 'deviceaudh', 'devitceauth', 'devriceauth',
                          'deviceaut', 'devicxeauth', 'deviceautf', 'dveiceauth', 'deviceaulh', 'deviceavth',
                          'deviceauta', 'devichauth', 'deviceauthm', 'devicetuth', 'dqviceauth', 'devxiceauth',
                          'devicnauth', 'devicqauth', 'deuviceauth', 'deviceuth', 'deviceauvh', 'deviecauth',
                          'deviaeauth', 'deviceajuth', 'devicauth', 'deviceaquth', 'devuceauth', 'deviceautth',
                          'dieviceauth', 'devicjeauth', 'devaceauth', 'dxeviceauth', 'devicearuth', 'deviceautr',
                          'deyviceauth', 'devicedauth', 'devdiceauth', 'deviceauthe', 'devihceauth', 'devsiceauth',
                          'deviceauthz', 'edviceauth', 'deiceauth', 'devficeauth', 'eviceauth', 'devictauth',
                          'leviceauth', 'devicezauth', 'deviceaath', 'desviceauth', 'devicetauth', 'devbceauth',
                          'dviceauth', 'zdeviceauth', 'devicfauth', 'deviceauthk', 'deviceauuth', 'deviczauth',
                          'derviceauth', 'deviceauh', 'devziceauth', 'djeviceauth', 'veviceauth', 'deviceautph',
                          'deviceputh', 'beviceauth', 'deviyceauth', 'devixeauth', 'deviceauah', 'devibeauth',
                          'deviceautx', 'deviceauthw', 'deviceath', 'deviceauts', 'devicepauth', 'deviccauth',
                          'deviyeauth', 'deviceaugth', 'devicdeauth', 'devyiceauth', 'deviheauth', 'devipeauth',
                          'devicezuth', 'devigceauth', 'deviceauxth', 'deviceaumh', 'deviceauhh', 'dezviceauth',
                          'devciceauth', 'deoiceauth', 'deviceautgh', 'deviceauwth', 'devioceauth', 'dlviceauth',
                          'deviceautbh', 'devicjauth', 'devicaeauth', 'deviceautrh', 'deficeauth', 'deviceautlh',
                          'deviceazuth', 'deqviceauth', 'dedviceauth', 'eeviceauth', 'deoviceauth', 'deviceluth',
                          'ydeviceauth', 'dtviceauth', 'deviceaunth', 'deviqeauth', 'dewiceauth', 'daeviceauth',
                          'deviceauvth', 'dneviceauth', 'deviceauqh', 'devicrauth', 'dehiceauth', 'deviceauthn',
                          'dteviceauth', 'deviceauthv', 'devicfeauth', 'mdeviceauth', 'deyiceauth', 'deviceamth',
                          'deeviceauth', 'adeviceauth', 'deviceauteh', 'devigeauth', 'devicejuth', 'deviceiauth',
                          'deviceautah', 'deviceacuth', 'devibceauth', 'deviceaduth', 'deviceoauth', 'devoiceauth',
                          'deviceauxh', 'jdeviceauth', 'ieviceauth', 'devicenauth', 'deviueauth', 'dkviceauth',
                          'devicvauth', 'devicequth', 'deviceeauth', 'delviceauth', 'devicneauth', 'devicebauth',
                          'decviceauth', 'deviceautzh', 'xdeviceauth', 'devhceauth', 'devdceauth', 'ddeviceauth',
                          'reviceauth', 'devicueauth', 'dejviceauth', 'deviceanuth', 'deviceauto', 'sdeviceauth',
                          'tdeviceauth', 'deviceauthd', 'deviceaujh', 'deviceauthi', 'devicegauth', 'deviceauti',
                          'devicgauth', 'deviceacth', 'devineauth', 'deviceauthy', 'deviceayth', 'odeviceauth',
                          'deviceaauth', 'deqiceauth', 'deviceanth', 'devicenuth', 'deviceaoth', 'deviceauoh',
                          'devvceauth', 'deviceduth', 'keviceauth', 'deviceauthq', 'deviceautt', 'deviceasth',
                          'deviceabth', 'deviceajth', 'deviceauthh', 'devicemuth', 'devoceauth', 'dmeviceauth',
                          'deviceaputh', 'deviceautg', 'deviceguth', 'degiceauth', 'oeviceauth', 'devwceauth',
                          'devicealuth', 'devicsauth', 'peviceauth', 'deviceautc', 'devicehuth', 'pdeviceauth',
                          'deviceautm', 'devbiceauth', 'devicekauth', 'devmiceauth', 'devkceauth', 'deviceautw',
                          'devxceauth', 'deviceakth', 'deviuceauth', 'meviceauth', 'ideviceauth', 'devqiceauth',
                          'deaiceauth', 'deviceaukth', 'deviceautyh', 'deviceautmh', 'devicelauth', 'weviceauth',
                          'dseviceauth', 'devinceauth', 'deviceauath', 'deviceauqth', 'doeviceauth', 'deviceauthp',
                          'deviveauth', 'devicexauth', 'deviceeuth', 'deviceautha', 'deviceakuth', 'deviceaiuth',
                          'deviceautfh', 'devicoeauth', 'devicoauth', 'deviceaute', 'devicesauth', 'debviceauth',
                          'deviceauths', 'devicmauth', 'devwiceauth', 'daviceauth', 'devlceauth', 'deveceauth',
                          'devivceauth', 'devyceauth', 'ceviceauth', 'devicefauth', 'dheviceauth', 'dwviceauth',
                          'deviceadth', 'devjceauth', 'deviceauzh', 'feviceauth', 'ueviceauth', 'deviceauthf',
                          'deviceaqth', 'deviceamuth', 'deviceasuth', 'deviceaujth', 'devizeauth', 'deviceautk',
                          'deviceauthu', 'deviceaxth', 'deviceyuth', 'dnviceauth', 'dexiceauth', 'devipceauth',
                          'deviceawuth', 'devicewuth', 'drviceauth', 'detviceauth', 'deviceaueth', 'deviceautoh',
                          'deviceaucth', 'vdeviceauth', 'deviceauih', 'deviceaeth', 'deviceautd', 'deviceyauth',
                          'devicearth', 'deviceautu', 'devaiceauth', 'heviceauth', 'deviiceauth', 'neviceauth',
                          'edeviceauth', 'dekiceauth', 'devijeauth', 'deziceauth', 'dmviceauth', 'devviceauth',
                          'deviceaumth', 'deviceauph', 'demviceauth', 'deviceauthg', 'deviceaunh', 'devifeauth',
                          'dveviceauth', 'deviciauth', 'deviceautuh', 'deviceqauth', 'devsceauth', 'deviceautv',
                          'devicesuth', 'devicejauth', 'devtceauth', 'degviceauth', 'zeviceauth', 'devicweauth',
                          'devqceauth', 'devicexuth', 'devicecauth', 'aeviceauth', 'yeviceauth', 'deviceauith',
                          'deviceauthb', 'devnceauth', 'devfceauth', 'devikeauth', 'devicewauth', 'dehviceauth',
                          'deviceautj', 'deviseauth', 'dbeviceauth', 'deviceruth', 'devzceauth', 'devcceauth',
                          'seviceauth', 'devieceauth', 'devimceauth', 'djviceauth', 'devicecuth', 'devniceauth',
                          'deviceaulth', 'deviceautnh', 'deviceaurth', 'jeviceauth', 'devideauth', 'deviceautkh',
                          'deviceuuth', 'deviceuauth', 'dreviceauth', 'dvviceauth', 'devicehauth', 'deveiceauth',
                          'deviceazth', 'devicyauth', 'deviceaubh', 'devicbauth', 'qdeviceauth', 'deviceauthx',
                          'devicekuth', 'diviceauth', 'devicdauth', 'deviceagth', 'deviceautxh', 'devickeauth',
                          'devickauth', 'defviceauth', 'deviceatuth', 'demiceauth', 'devpceauth', 'devidceauth',
                          'xeviceauth', 'cdeviceauth', 'deviceautb', 'dejiceauth', 'dzviceauth', 'deviceaupth',
                          'devioeauth', 'deviceaouth', 'deviteauth', 'depviceauth', 'devicseauth', 'deviceabuth',
                          'gdeviceauth', 'dyviceauth', 'devireauth', 'deviceaurh', 'devicaauth', 'devmceauth',
                          'devkiceauth', 'deviceautwh', 'deviceaith', 'devicefuth', 'deviceauthc', 'devicteauth',
                          'devicgeauth', 'devhiceauth', 'dpeviceauth', 'ddviceauth', 'devileauth', 'dgeviceauth',
                          'deviceaufth', 'devicqeauth', 'deviceahuth', 'dsviceauth', 'deviceauhth', 'dexviceauth',
                          'deeiceauth', 'dbviceauth', 'deviceautq', 'deviceautz', 'devicreauth', 'deviceauuh',
                          'deviceatth', 'dewviceauth', 'deviceawth', 'wdeviceauth', 'deviceauzth', 'devicevuth',
                          'rdeviceauth', 'bdeviceauth', 'devpiceauth', 'devifceauth', 'deviceayuth', 'deaviceauth',
                          'dekviceauth', 'deviceauyh', 'fdeviceauth', 'deviceautl', 'deviceaush', 'dkeviceauth',
                          'devisceauth', 'devicemauth', 'deviieauth', 'depiceauth', 'deviceouth', 'qeviceauth',
                          'deviceautqh', 'devirceauth', 'dcviceauth', 'udeviceauth', 'desiceauth', 'deviceausth',
                          'devimeauth', 'dgviceauth', 'deviceaxuth', 'devikceauth', 'duviceauth', 'deiviceauth',
                          'teviceauth', 'devicealth', 'devicpauth', 'deviceautvh', 'devliceauth', 'deviceaueh',
                          'deuiceauth', 'deviaceauth', 'devicbeauth', 'devicmeauth', 'dfeviceauth', 'ldeviceauth',
                          'deviceauyth', 'deviceaeuth', 'dpviceauth', 'deviceauty', 'deviqceauth', 'devicxauth',
                          'devjiceauth', 'devicveauth', 'dericeauth', 'deviceafuth', 'devicieauth', 'devicceauth',
                          'devicpeauth', 'geviceauth', 'deviceautn', 'doviceauth', 'deviceaguth', 'devixceauth',
                          'dxviceauth', 'devicleauth', 'devizceauth', 'deviceautdh', 'deviceautp', 'deviceautsh',
                          'dweviceauth', 'deviceaugh', 'deviwceauth', 'devicuauth', 'devrceauth', 'dyeviceauth',
                          'deniceauth', 'deviceauthj', 'deviceauwh', 'debiceauth', 'dediceauth', 'deviceaubth',
                          'devieeauth', 'deviceautjh', 'deviceautih', 'devicyeauth', 'deviceaudth', 'deviceavuth',
                          'denviceauth', 'deviceautho', 'deciceauth', 'devicebuth', 'deviczeauth', 'dueviceauth',
                          'devuiceauth', 'devicheauth', 'deviceaukh', 'deviclauth', 'deviceaufh', 'deviceiuth',
                          'deviceautht', 'devicwauth', 'deliceauth', 'deviceauthl', 'deviceautch', 'devgceauth',
                          'dqeviceauth', 'deviceauthr', 'dzeviceauth', 'deviweauth', 'devicevauth', 'dceviceauth',
                          'deviceapth', 'deticeauth', 'devilceauth', 'deviceafth', 'kdeviceauth', 'ndeviceauth',
                          'deviceauch', 'devijceauth', 'd4viceauth', 'd3viceauth', 'd2viceauth', 'd$viceauth',
                          'd#viceauth', 'd@viceauth', 'dev7ceauth', 'dev8ceauth', 'dev9ceauth', 'dev&ceauth',
                          'dev*ceauth', 'dev(ceauth', 'devic4auth', 'devic3auth', 'devic2auth', 'devic$auth',
                          'devic#auth', 'devic@auth', 'devicea6th', 'devicea7th', 'devicea8th', 'devicea^th',
                          'devicea&th', 'devicea*th', 'deviceau4h', 'deviceau5h', 'deviceau6h', 'deviceau$h',
                          'deviceau%h', 'deviceau^h', 'diauth', 'dauqth', 'daut', 'dkauth', 'daduth', 'duath', 'datuh',
                          'dajth', 'aduth', 'dalth', 'dauh', 'daubh', 'vauth', 'dauthc', 'fauth', 'dautph', 'gdauth',
                          'duth', 'dahth', 'dauht', 'dautv', 'dxuth', 'dath', 'dputh', 'dautj', 'dauthb', 'dnauth',
                          'dautzh', 'dautch', 'dautx', 'dautbh', 'dauti', 'daukh', 'dauzh', 'dauthp', 'wdauth',
                          'zdauth', 'dautn', 'dautf', 'dduth', 'daxuth', 'dautp', 'adauth', 'dautrh', 'daubth', 'dautk',
                          'daunh', 'idauth', 'dauch', 'dayuth', 'sdauth', 'dauuth', 'davuth', 'dauthd', 'dautt',
                          'dtuth', 'kdauth', 'dquth', 'daquth', 'dajuth', 'edauth', 'odauth', 'dautnh', 'dautb',
                          'daute', 'daujh', 'druth', 'dyuth', 'dauoth', 'pauth', 'dauvh', 'dakuth', 'dausth', 'dakth',
                          'wauth', 'dbauth', 'dauah', 'daruth', 'dauqh', 'dafth', 'dbuth', 'dauths', 'dawth', 'dautl',
                          'daueh', 'dabuth', 'dauyh', 'dauxth', 'danth', 'djauth', 'daguth', 'daeuth', 'dautfh',
                          'cdauth', 'djuth', 'dcuth', 'dazuth', 'daoth', 'dauthj', 'dauwh', 'dvuth', 'davth', 'dautu',
                          'dautsh', 'dautr', 'daeth', 'dauxh', 'daurth', 'tdauth', 'daulh', 'udauth', 'dauthm', 'qauth',
                          'mdauth', 'dautht', 'damth', 'fdauth', 'gauth', 'dagth', 'dauthq', 'dawuth', 'diuth', 'daurh',
                          'dautih', 'dauthf', 'eauth', 'datuth', 'dauts', 'dtauth', 'bdauth', 'dauthe', 'ddauth',
                          'dautg', 'dautxh', 'dautyh', 'daluth', 'daudth', 'dauuh', 'dadth', 'douth', 'dautc', 'dauith',
                          'dasth', 'jdauth', 'dlauth', 'dauthz', 'dautvh', 'dautth', 'dautm', 'dautha', 'dauthu',
                          'daupth', 'dmauth', 'daxth', 'dauta', 'daouth', 'dautho', 'dqauth', 'lauth', 'dautjh',
                          'dauthr', 'dfauth', 'dautmh', 'dauwth', 'daauth', 'dhauth', 'dauthh', 'dautlh', 'dauhh',
                          'dasuth', 'dmuth', 'dauih', 'dauteh', 'daufh', 'dauzth', 'dautqh', 'dautd', 'dahuth', 'daush',
                          'dauoh', 'daucth', 'dzuth', 'dwauth', 'dauty', 'daukth', 'pdauth', 'daqth', 'deuth', 'dautoh',
                          'duuth', 'dabth', 'dkuth', 'dautq', 'dautkh', 'dauvth', 'daumh', 'qdauth', 'dayth', 'darth',
                          'dzauth', 'dsauth', 'danuth', 'daulth', 'dauph', 'dhuth', 'dautah', 'dsuth', 'dyauth',
                          'dfuth', 'dauto', 'dauyth', 'ndauth', 'dauthn', 'dnuth', 'rauth', 'daueth', 'dluth', 'ldauth',
                          'xdauth', 'damuth', 'dauthi', 'dcauth', 'dauhth', 'dautz', 'dxauth', 'ydauth', 'daufth',
                          'dauthv', 'duauth', 'cauth', 'jauth', 'daiuth', 'dauthx', 'dpauth', 'daugth', 'dgauth',
                          'daujth', 'daith', 'daumth', 'dazth', 'dafuth', 'dauthg', 'datth', 'dacuth', 'dapth', 'daugh',
                          'dautwh', 'dguth', 'hauth', 'dautw', 'rdauth', 'daunth', 'dautgh', 'dauthk', 'dauath',
                          'dauthy', 'drauth', 'dautdh', 'vdauth', 'dauthl', 'dacth', 'doauth', 'daudh', 'dauthw',
                          'dwuth', 'hdauth', 'dautuh', 'daputh', 'daath', 'da6th', 'da7th', 'da8th', 'da^th', 'da&th',
                          'da*th', 'dau4h', 'dau5h', 'dau6h', 'dau$h', 'dau%h', 'dau^h', 'uatodaily', 'autodialy',
                          'autodaioy', 'autodail', 'autodaiyl', 'utodaily', 'atodaily', 'autodaly', 'autodiaily',
                          'automaily', 'autodailyt', 'akutodaily', 'autodadily', 'auotdaily', 'autoqaily', 'autodaiy',
                          'awutodaily', 'autodaidly', 'autodaliy', 'iautodaily', 'aoutodaily', 'autodily', 'autodnaily',
                          'autoadily', 'autodaimy', 'autkdaily', 'autodailyb', 'oautodaily', 'autkodaily', 'autodaiwy',
                          'autjodaily', 'atutodaily', 'autodxily', 'attodaily', 'autodailjy', 'autodailay', 'autodarly',
                          'antodaily', 'autdaily', 'auqtodaily', 'aufodaily', 'auodaily', 'autodairy', 'autodkaily',
                          'avutodaily', 'autodazly', 'autodailn', 'autodatily', 'autadaily', 'aitodaily', 'ajutodaily',
                          'autodafly', 'autdoaily', 'auvtodaily', 'auhodaily', 'autodaiply', 'autoaily', 'autoxaily',
                          'autodailly', 'autpdaily', 'autodzaily', 'sautodaily', 'autodailyy', 'autodaigy', 'gutodaily',
                          'autodarily', 'autmodaily', 'autodailya', 'ayutodaily', 'qutodaily', 'autodailny',
                          'auvodaily', 'autodaity', 'ahutodaily', 'autrodaily', 'autoeaily', 'altodaily', 'autodailh',
                          'autodeaily', 'atuodaily', 'vutodaily', 'autaodaily', 'aeutodaily', 'autodailr', 'abtodaily',
                          'tautodaily', 'autobaily', 'autodaipy', 'autodailm', 'autogdaily', 'autodailyg', 'autodaqly',
                          'aatodaily', 'autodailzy', 'autowaily', 'autopdaily', 'autodaaily', 'auzodaily', 'autodaioly',
                          'autodailys', 'autoduaily', 'autodaidy', 'autoodaily', 'autiodaily', 'autvdaily',
                          'autodsaily', 'autodailyv', 'amutodaily', 'auqodaily', 'autodasily', 'autosaily',
                          'autoidaily', 'autoyaily', 'wautodaily', 'autodpily', 'autotaily', 'autodyaily', 'autodaiky',
                          'auitodaily', 'autodhaily', 'wutodaily', 'autodailgy', 'auttodaily', 'autodaiyy',
                          'autodaiqly', 'auntodaily', 'autodcily', 'iutodaily', 'autodaify', 'autordaily', 'autodaizy',
                          'auktodaily', 'aujtodaily', 'autzdaily', 'lutodaily', 'nautodaily', 'zautodaily', 'aueodaily',
                          'autodailyr', 'autodailyp', 'eutodaily', 'autodaiqy', 'autodaikly', 'aumtodaily', 'autodaisy',
                          'austodaily', 'awtodaily', 'authdaily', 'autodaizly', 'autovaily', 'autodailyn', 'aautodaily',
                          'aunodaily', 'autojaily', 'autodcaily', 'adutodaily', 'autodmily', 'autodyily', 'autidaily',
                          'autodagily', 'autodailty', 'autodailk', 'autoiaily', 'autpodaily', 'autodaiuy', 'xautodaily',
                          'autodailoy', 'autodailw', 'autodailym', 'rautodaily', 'aultodaily', 'autodailey',
                          'autodailky', 'kutodaily', 'autodqily', 'autodzily', 'autodbily', 'autodaili', 'auetodaily',
                          'auuodaily', 'autodailxy', 'autodaaly', 'auytodaily', 'autodacily', 'autolaily', 'autodailv',
                          'auftodaily', 'aurodaily', 'auwtodaily', 'autodails', 'autodaila', 'gautodaily', 'autobdaily',
                          'autodaijly', 'autodavily', 'autodailhy', 'autodailu', 'autodaiuly', 'autodailyh',
                          'auaodaily', 'autooaily', 'uutodaily', 'pautodaily', 'jutodaily', 'autoadaily', 'vautodaily',
                          'autfdaily', 'autodlaily', 'autudaily', 'autcodaily', 'autodailry', 'cutodaily', 'autodailyl',
                          'autodaiily', 'autofaily', 'autodaxily', 'aqtodaily', 'autodailyk', 'eautodaily', 'aotodaily',
                          'autodajly', 'autodaifly', 'autodailx', 'autodagly', 'abutodaily', 'autodadly', 'nutodaily',
                          'autwdaily', 'autodbaily', 'autbodaily', 'autodaiyly', 'autodraily', 'autodamily',
                          'autodahly', 'autokaily', 'autodjily', 'autosdaily', 'autodailqy', 'autodailq', 'autyodaily',
                          'autodairly', 'autodhily', 'azutodaily', 'autodacly', 'autodaihy', 'amtodaily', 'zutodaily',
                          'autodwaily', 'autogaily', 'bautodaily', 'aukodaily', 'autodailwy', 'autodailcy', 'autodably',
                          'autoedaily', 'autxdaily', 'autodailby', 'autodxaily', 'autodaiey', 'aztodaily', 'autuodaily',
                          'aftodaily', 'autodaxly', 'autodafily', 'autodailfy', 'autoxdaily', 'hautodaily',
                          'autodailyf', 'axutodaily', 'autodaiby', 'auutodaily', 'autodnily', 'autodaigly', 'autodailc',
                          'autondaily', 'autodamly', 'auteodaily', 'autohdaily', 'autodailf', 'autodawly', 'augtodaily',
                          'autodailye', 'autodaile', 'autodazily', 'artodaily', 'autodailyz', 'agtodaily', 'avtodaily',
                          'autodainy', 'autodailyc', 'autodfaily', 'autodaihly', 'agutodaily', 'autodaiay',
                          'autofdaily', 'autoduily', 'autodoily', 'aqutodaily', 'acutodaily', 'autcdaily', 'arutodaily',
                          'auptodaily', 'autrdaily', 'autodaely', 'autfodaily', 'autodwily', 'aujodaily', 'autvodaily',
                          'ajtodaily', 'autodmaily', 'autodainly', 'autodailb', 'autodaibly', 'autqodaily',
                          'aubtodaily', 'autodailg', 'autodailiy', 'autodaiely', 'aubodaily', 'butodaily', 'autoddaily',
                          'auoodaily', 'autodiily', 'autgodaily', 'augodaily', 'autodailz', 'autoraily', 'autodeily',
                          'autodanily', 'autodaicly', 'autodaply', 'autodaivy', 'autodajily', 'autodtily', 'hutodaily',
                          'cautodaily', 'futodaily', 'lautodaily', 'autodlily', 'autodaicy', 'autodrily', 'autodaoily',
                          'autodaiiy', 'autozdaily', 'autovdaily', 'autqdaily', 'dutodaily', 'aucodaily', 'autodaijy',
                          'autwodaily', 'autodailyd', 'aytodaily', 'autocdaily', 'autoaaily', 'autsodaily',
                          'autdodaily', 'autodfily', 'autodakily', 'autgdaily', 'auatodaily', 'axtodaily', 'autlodaily',
                          'autxodaily', 'auyodaily', 'autodailyj', 'autoddily', 'sutodaily', 'yautodaily', 'autodally',
                          'autocaily', 'autodaild', 'autodaimly', 'outodaily', 'autouaily', 'autodasly', 'autodailyx',
                          'autodgaily', 'autonaily', 'autedaily', 'autodaill', 'auiodaily', 'autodaitly', 'audodaily',
                          'putodaily', 'adtodaily', 'kautodaily', 'autodalily', 'autodailp', 'autodaildy', 'autodapily',
                          'jautodaily', 'autydaily', 'autodailt', 'autodkily', 'autnodaily', 'autodakly', 'autodgily',
                          'autodailmy', 'autodailj', 'ahtodaily', 'autodaeily', 'autmdaily', 'mautodaily', 'autldaily',
                          'aumodaily', 'aptodaily', 'autoydaily', 'autopaily', 'autodatly', 'autodabily', 'aiutodaily',
                          'autjdaily', 'autodoaily', 'autodawily', 'aetodaily', 'autodaoly', 'autohaily', 'auwodaily',
                          'autoqdaily', 'auhtodaily', 'autbdaily', 'autodailyw', 'autodayily', 'auotodaily',
                          'autzodaily', 'auxodaily', 'afutodaily', 'autodaixly', 'autodailsy', 'autotdaily',
                          'anutodaily', 'automdaily', 'autodailuy', 'asutodaily', 'autodanly', 'autozaily', 'autndaily',
                          'actodaily', 'autodauly', 'autodayly', 'aupodaily', 'ausodaily', 'autodaqily', 'aputodaily',
                          'autodauily', 'qautodaily', 'audtodaily', 'xutodaily', 'autodaialy', 'autojdaily',
                          'auxtodaily', 'fautodaily', 'aurtodaily', 'alutodaily', 'mutodaily', 'autodailpy',
                          'autodpaily', 'autodaixy', 'autodaisly', 'aulodaily', 'auttdaily', 'autodsily', 'autowdaily',
                          'autodqaily', 'auztodaily', 'autodjaily', 'autodailyq', 'auctodaily', 'uautodaily',
                          'autodahily', 'autodaiwly', 'autodailyi', 'dautodaily', 'aktodaily', 'autddaily',
                          'authodaily', 'autodvily', 'autoudaily', 'autodtaily', 'yutodaily', 'autodailvy', 'autsdaily',
                          'tutodaily', 'autokdaily', 'autodailyo', 'autodailo', 'astodaily', 'autodavly', 'rutodaily',
                          'autodailyu', 'autodaivly', 'autodvaily', 'autoldaily', 'a6todaily', 'a7todaily', 'a8todaily',
                          'a^todaily', 'a&todaily', 'a*todaily', 'au4odaily', 'au5odaily', 'au6odaily', 'au$odaily',
                          'au%odaily', 'au^odaily', 'aut8daily', 'aut9daily', 'aut0daily', 'aut;daily', 'aut*daily',
                          'aut(daily', 'aut)daily', 'autoda7ly', 'autoda8ly', 'autoda9ly', 'autoda&ly', 'autoda*ly',
                          'autoda(ly', 'autodai;y', 'autodai/y', 'autodai.y', 'autodai,y', 'autodai?y', 'autodai>y',
                          'autodai<y', 'autodail5', 'autodail6', 'autodail7', 'autodail%', 'autodail^', 'autodail&',
                          'autoclaikm', 'autocliam', 'utoclaim', 'dautoclaim', 'autocyaim', 'adtoclaim', 'autoclaimy',
                          'autoclxim', 'autolcaim', 'autoclaimm', 'autocuaim', 'autocaim', 'autoclami', 'atoclaim',
                          'autolaim', 'autocalim', 'autcolaim', 'aftoclaim', 'mautoclaim', 'autoclpim', 'autoclalm',
                          'autclaim', 'autobclaim', 'rutoclaim', 'auttoclaim', 'autoceaim', 'autovlaim', 'uatoclaim',
                          'autoclfim', 'agutoclaim', 'autoclai', 'autmoclaim', 'autokclaim', 'autocloaim', 'zautoclaim',
                          'autoalaim', 'xutoclaim', 'autoclagim', 'qautoclaim', 'pautoclaim', 'lutoclaim', 'autoclajm',
                          'atuoclaim', 'autoflaim', 'autoclaitm', 'autoclayim', 'autocoaim', 'eautoclaim', 'auoclaim',
                          'autoclaimc', 'autoclavim', 'auotclaim', 'autocllaim', 'autoclaimv', 'auutoclaim',
                          'autoclakm', 'autoclim', 'autocltaim', 'autoclaijm', 'mutoclaim', 'autoclaib', 'autoclam',
                          'aufoclaim', 'actoclaim', 'autoclaij', 'autoclaix', 'artoclaim', 'autoclaiy', 'autnoclaim',
                          'autoclkim', 'autoclaqim', 'autoylaim', 'autoclakim', 'autoclaeim', 'aitoclaim', 'autoclaaim',
                          'uautoclaim', 'uutoclaim', 'autoclaims', 'antoclaim', 'autocljaim', 'autocklaim',
                          'autgoclaim', 'autwoclaim', 'autocluim', 'autonlaim', 'autoclaxm', 'autoctlaim', 'autoclafim',
                          'autochlaim', 'autoclaimx', 'autocleim', 'autoclalim', 'auuoclaim', 'ausoclaim', 'aupoclaim',
                          'autfoclaim', 'autioclaim', 'autoclbim', 'autoclaihm', 'amutoclaim', 'auftoclaim',
                          'automlaim', 'jutoclaim', 'autovclaim', 'autoclaiim', 'adutoclaim', 'avutoclaim',
                          'autocplaim', 'autocladm', 'autocslaim', 'autsclaim', 'axtoclaim', 'auooclaim', 'autoclaia',
                          'autoslaim', 'autoclcim', 'autoclasm', 'aucoclaim', 'autcclaim', 'auitoclaim', 'autocloim',
                          'auvtoclaim', 'aktoclaim', 'kutoclaim', 'autoclafm', 'tutoclaim', 'autoclatm', 'autoyclaim',
                          'autoclaxim', 'autocnaim', 'putoclaim', 'autoclair', 'autoclaiam', 'autoclwim', 'aqutoclaim',
                          'autoclanim', 'autotclaim', 'autoclnim', 'iutoclaim', 'autyclaim', 'autoaclaim', 'aultoclaim',
                          'aetoclaim', 'autoclawim', 'autocmaim', 'fautoclaim', 'hautoclaim', 'autnclaim', 'autoclaih',
                          'autofclaim', 'autoclmaim', 'oautoclaim', 'autoclabim', 'aukoclaim', 'autoclaig',
                          'autocvlaim', 'autozlaim', 'autocrlaim', 'autocldim', 'autoclatim', 'autoclaimi', 'autoclrim',
                          'autoclaimh', 'autrclaim', 'autjoclaim', 'autochaim', 'aputoclaim', 'autoclmim', 'autoclaiv',
                          'autoclapm', 'authclaim', 'autoczlaim', 'autoclaiu', 'autoclaiqm', 'akutoclaim', 'aoutoclaim',
                          'abutoclaim', 'autoclauim', 'anutoclaim', 'autoczaim', 'arutoclaim', 'autoclanm',
                          'auhtoclaim', 'auyoclaim', 'autocflaim', 'autoclyaim', 'autozclaim', 'autboclaim',
                          'autocdlaim', 'autocelaim', 'auloclaim', 'autxoclaim', 'autocjaim', 'autoblaim', 'autoclaiz',
                          'autdclaim', 'autqoclaim', 'autoclaoim', 'autoclaimw', 'autojlaim', 'ahtoclaim', 'aqtoclaim',
                          'autocluaim', 'autwclaim', 'autoclzim', 'aytoclaim', 'outoclaim', 'autoclaip', 'autkoclaim',
                          'autoccaim', 'autoclaimq', 'autvclaim', 'qutoclaim', 'autorlaim', 'autoclahm', 'autoulaim',
                          'agtoclaim', 'aptoclaim', 'autocylaim', 'altoclaim', 'autoclaism', 'autocnlaim', 'autoclazim',
                          'autoclaibm', 'autoclvim', 'autoclahim', 'autooclaim', 'atutoclaim', 'autoclaiem',
                          'autoclazm', 'aiutoclaim', 'autowclaim', 'autoclamm', 'autoplaim', 'alutoclaim', 'autoclabm',
                          'autotlaim', 'autbclaim', 'autoilaim', 'augoclaim', 'auaoclaim', 'autoclaiq', 'butoclaim',
                          'autocgaim', 'autocwaim', 'autocclaim', 'autocfaim', 'autocpaim', 'auwoclaim', 'autoclaimr',
                          'autoiclaim', 'auticlaim', 'augtoclaim', 'autuoclaim', 'tautoclaim', 'autoclain', 'auqoclaim',
                          'autoglaim', 'autoclawm', 'auteclaim', 'axutoclaim', 'autoolaim', 'attoclaim', 'autxclaim',
                          'auwtoclaim', 'autdoclaim', 'auytoclaim', 'autoclaik', 'autoclvaim', 'autohlaim', 'autoxlaim',
                          'autpclaim', 'asutoclaim', 'sautoclaim', 'autzoclaim', 'afutoclaim', 'autfclaim',
                          'autoclaimz', 'autocljim', 'autocliaim', 'autoclait', 'auxoclaim', 'autoclaimk', 'aautoclaim',
                          'autuclaim', 'aujtoclaim', 'lautoclaim', 'auttclaim', 'autoculaim', 'futoclaim', 'auteoclaim',
                          'autoclais', 'autoclaidm', 'autaclaim', 'autoclaam', 'autocltim', 'auktoclaim', 'autocbaim',
                          'autocwlaim', 'automclaim', 'auqtoclaim', 'autocllim', 'aujoclaim', 'autocsaim', 'autoclaigm',
                          'autoclcaim', 'astoclaim', 'autodclaim', 'autoclaem', 'autoclhim', 'autoclajim', 'audoclaim',
                          'autoclgaim', 'autohclaim', 'xautoclaim', 'autoxclaim', 'auctoclaim', 'autpoclaim',
                          'austoclaim', 'autroclaim', 'bautoclaim', 'audtoclaim', 'aumoclaim', 'ahutoclaim',
                          'autoclaid', 'jautoclaim', 'autocjlaim', 'auboclaim', 'abtoclaim', 'dutoclaim', 'autoclaimn',
                          'azutoclaim', 'autlclaim', 'autoclaimb', 'autocqlaim', 'autocraim', 'autoclqaim', 'autocliim',
                          'autoclacim', 'autkclaim', 'autyoclaim', 'autzclaim', 'autocalaim', 'autollaim', 'autoctaim',
                          'autqclaim', 'auhoclaim', 'autoclaimp', 'autocblaim', 'awutoclaim', 'autoclairm', 'autoclaum',
                          'ajtoclaim', 'autoclaimu', 'zutoclaim', 'auxtoclaim', 'autoclaima', 'autocdaim', 'autojclaim',
                          'autowlaim', 'autoclaiym', 'auioclaim', 'awtoclaim', 'autoqclaim', 'autoclfaim', 'avtoclaim',
                          'cutoclaim', 'autocglaim', 'autoclpaim', 'autoclavm', 'autoclaipm', 'aeutoclaim', 'autoclagm',
                          'nutoclaim', 'autoclaif', 'aztoclaim', 'yutoclaim', 'autaoclaim', 'authoclaim', 'rautoclaim',
                          'autoclkaim', 'acutoclaim', 'auroclaim', 'autoclaie', 'autoclaimg', 'aubtoclaim', 'autoklaim',
                          'autoclgim', 'autoclapim', 'autoclaiml', 'aotoclaim', 'vutoclaim', 'autcoclaim', 'autocmlaim',
                          'auvoclaim', 'autopclaim', 'autoclaii', 'autoclaivm', 'aunoclaim', 'autoelaim', 'vautoclaim',
                          'ajutoclaim', 'autoclaifm', 'autoclasim', 'auetoclaim', 'auntoclaim', 'wutoclaim',
                          'autoclaicm', 'autoclaimd', 'autoclsaim', 'autoclaiwm', 'autmclaim', 'autocladim',
                          'autocilaim', 'autoclacm', 'autoclxaim', 'autgclaim', 'autocolaim', 'autoclaizm',
                          'aumtoclaim', 'autoclaom', 'autocvaim', 'amtoclaim', 'auotoclaim', 'autoclaio', 'autocaaim',
                          'autosclaim', 'autoclhaim', 'autoclaium', 'autoclaqm', 'yautoclaim', 'autocqaim',
                          'autoclnaim', 'autoclaimj', 'kautoclaim', 'sutoclaim', 'autoqlaim', 'autoclaimo',
                          'autoclaimt', 'iautoclaim', 'cautoclaim', 'auztoclaim', 'autoclailm', 'autockaim',
                          'autoclamim', 'autoclaime', 'autocxaim', 'auatoclaim', 'autocxlaim', 'autoeclaim',
                          'autoclzaim', 'gutoclaim', 'autjclaim', 'autodlaim', 'autorclaim', 'autvoclaim', 'wautoclaim',
                          'eutoclaim', 'autoclaiom', 'autoclbaim', 'autoclaiw', 'autoclyim', 'autoclqim', 'autolclaim',
                          'autocldaim', 'aatoclaim', 'autogclaim', 'autoclarm', 'autoclraim', 'autoclaic', 'gautoclaim',
                          'autonclaim', 'autloclaim', 'auptoclaim', 'autoclaym', 'aurtoclaim', 'autoclarim',
                          'auzoclaim', 'aueoclaim', 'autoclainm', 'autoclwaim', 'autociaim', 'autouclaim', 'autoclail',
                          'nautoclaim', 'hutoclaim', 'autoclsim', 'autoclaixm', 'autsoclaim', 'ayutoclaim',
                          'autoclaimf', 'autocleaim', 'a6toclaim', 'a7toclaim', 'a8toclaim', 'a^toclaim', 'a&toclaim',
                          'a*toclaim', 'au4oclaim', 'au5oclaim', 'au6oclaim', 'au$oclaim', 'au%oclaim', 'au^oclaim',
                          'aut8claim', 'aut9claim', 'aut0claim', 'aut;claim', 'aut*claim', 'aut(claim', 'aut)claim',
                          'autoc;aim', 'autoc/aim', 'autoc.aim', 'autoc,aim', 'autoc?aim', 'autoc>aim', 'autoc<aim',
                          'autocla7m', 'autocla8m', 'autocla9m', 'autocla&m', 'autocla*m', 'autocla(m', 'autoclai,',
                          'autoclai<', 'uato', 'augto', 'auko', 'aquto', 'atuo', 'yuto', 'agto', 'aeto', 'auo', 'auot',
                          'ato', 'autoq', 'nuto', 'auato', 'autop', 'auuto', 'oauto', 'aurto', 'aputo', 'eauto',
                          'autoo', 'muto', 'aluto', 'ajto', 'aumo', 'aupto', 'ajuto', 'autgo', 'amto', 'uto', 'jauto',
                          'autos', 'auhto', 'auqto', 'aulto', 'auho', 'auco', 'auyo', 'ahto', 'aeuto', 'aupo', 'autoa',
                          'aulo', 'auxo', 'buto', 'autov', 'yauto', 'hauto', 'auvto', 'pauto', 'kuto', 'auno', 'auro',
                          'adto', 'autob', 'autro', 'aujto', 'axto', 'asuto', 'avuto', 'autd', 'aute', 'autj', 'autio',
                          'asto', 'auoo', 'auxto', 'wauto', 'auso', 'suto', 'auton', 'autoj', 'auwo', 'auti',
                          'aruto', 'autb', 'aiuto', 'audto', 'azuto', 'acto', 'aoto', 'autbo', 'quto', 'wuto', 'xuto',
                          'arto', 'audo', 'autm', 'autw', 'autto', 'qauto', 'autco', 'aubto', 'abuto', 'acuto', 'aqto',
                          'axuto', 'akuto', 'autwo', 'auwto', 'guto', 'anto', 'autv', 'autfo', 'auzo', 'autoh', 'autc',
                          'fauto', 'autvo', 'aubo', 'autoy', 'aito', 'autdo', 'luto', 'autoz', 'vauto', 'autho', 'iuto',
                          'autao', 'huto', 'vuto', 'auito', 'akto', 'auteo', 'autl', 'aouto', 'autod', 'abto', 'tauto',
                          'iauto', 'autor', 'autko', 'autom', 'autjo', 'autzo', 'autf', 'lauto', 'euto', 'autp',
                          'sauto', 'auyto', 'autso', 'atto', 'autox', 'azto', 'aufto', 'auuo', 'mauto', 'aduto', 'autz',
                          'ahuto', 'futo', 'ruto', 'austo', 'autoc', 'autxo', 'anuto', 'autol', 'autok', 'bauto',
                          'autuo', 'autyo', 'alto', 'ayto', 'rauto', 'aueo', 'autow', 'juto', 'auzto', 'zauto', 'autq',
                          'autg', 'aato', 'puto', 'uuto', 'aunto', 'autoe', 'cuto', 'autk', 'awto', 'autqo', 'auqo',
                          'uauto', 'aauto', 'aucto', 'autot', 'nauto', 'autoi', 'auts', 'auvo', 'auty', 'auio', 'aukto',
                          'auoto', 'autt', 'autou', 'auao', 'autpo', 'autu', 'duto', 'gauto', 'amuto', 'aguto', 'autmo',
                          'autog', 'ayuto', 'avto', 'afuto', 'autno', 'autr', 'aujo', 'augo', 'autof', 'autlo', 'zuto',
                          'outo', 'kauto', 'apto', 'aumto', 'xauto', 'afto', 'cauto', 'aueto', 'autx', 'atuto', 'aufo',
                          'awuto', 'a6to', 'a7to', 'a8to', 'a^to', 'a&to', 'a*to', 'au4o', 'au5o', 'au6o', 'au$o',
                          'au%o', 'au^o', 'aut8', 'aut9', 'aut0', 'aut;', 'aut*', 'aut(', 'aut)', 'agtoclaimer',
                          'autocalimer', 'tautoclaimer', 'ausoclaimer', 'autoclaimez', 'autoclaimber', 'autcolaimer',
                          'autoclaimre', 'autoclamier', 'autoclawmer', 'autoclwimer', 'atoclaimer', 'autokclaimer',
                          'autodclaimer', 'autoclaiymer', 'auetoclaimer', 'autclaimer', 'autoclaier', 'autoclaiimer',
                          'autoclaimet', 'uatoclaimer', 'mautoclaimer', 'auotoclaimer', 'autoclaiemr', 'azutoclaimer',
                          'autocilaimer', 'altoclaimer', 'autoclacmer', 'arutoclaimer', 'autoclaiber', 'autolcaimer',
                          'afutoclaimer', 'autolclaimer', 'autoclaimeg', 'autoclaimerv', 'autoclaoimer', 'vautoclaimer',
                          'auitoclaimer', 'autoflaimer', 'autyclaimer', 'autoulaimer', 'autoclaiqmer', 'autwoclaimer',
                          'autocladmer', 'autoclaimek', 'autoclamer', 'atuoclaimer', 'autoclaiier', 'autsoclaimer',
                          'autoclimer', 'aujtoclaimer', 'auloclaimer', 'autocllaimer', 'yautoclaimer', 'autoclauimer',
                          'agutoclaimer', 'autoclaimerm', 'autoclawimer', 'autocliamer', 'autocliimer', 'auotclaimer',
                          'autoclaimsr', 'auatoclaimer', 'autoclaidmer', 'aetoclaimer', 'autocdaimer', 'autocxaimer',
                          'autoclaimery', 'autoclasmer', 'autoclaimeur', 'automclaimer', 'auoclaimer', 'autoclatimer',
                          'autocaimer', 'auboclaimer', 'autoclaimer', 'autoclarimer', 'aumoclaimer', 'autoclaimler',
                          'kautoclaimer', 'atutoclaimer', 'autoclaimepr', 'autoclanimer', 'akutoclaimer',
                          'autoclamimer', 'autonlaimer', 'autoclaitmer', 'autoclsaimer', 'autoclaimrr', 'autocflaimer',
                          'autoclaymer', 'autohlaimer', 'autoclaiker', 'auxoclaimer', 'autocliaimer', 'aufoclaimer',
                          'autocklaimer', 'autochaimer', 'auzoclaimer', 'autohclaimer', 'autoaclaimer', 'autoclaijmer',
                          'autolaimer', 'autlclaimer', 'autoclhaimer', 'autochlaimer', 'autoclaiemer', 'autoclgimer',
                          'autoklaimer', 'autoclaimex', 'xutoclaimer', 'autoclaaimer', 'aumtoclaimer', 'autojclaimer',
                          'autoclaiper', 'autgoclaimer', 'autoclaimerr', 'anutoclaimer', 'autoclaimier', 'autoclaimecr',
                          'autocelaimer', 'autoclaiser', 'autoclaimaer', 'autoclaumer', 'autocnlaimer', 'utoclaimer',
                          'rutoclaimer', 'auttoclaimer', 'autoclaimlr', 'nautoclaimer', 'autoceaimer', 'autoclaimeri',
                          'acutoclaimer', 'autoclaivmer', 'cautoclaimer', 'autoclaimera', 'autoilaimer', 'putoclaimer',
                          'autoqlaimer', 'autoclpaimer', 'autoclaimedr', 'autoclaimfer', 'autoclaimder', 'autoclaimejr',
                          'autoclaimqer', 'adtoclaimer', 'autoclaimep', 'autoclqimer', 'autocmlaimer', 'autoclaimea',
                          'autoclaimexr', 'auyoclaimer', 'autocmaimer', 'xautoclaimer', 'autoclvaimer', 'autoclaeimer',
                          'autocblaimer', 'autoclaximer', 'auwoclaimer', 'autoclaiwer', 'autocltaimer', 'authoclaimer',
                          'autocpaimer', 'aitoclaimer', 'autbclaimer', 'autoclaimver', 'autoclaimeer', 'attoclaimer',
                          'autoclajmer', 'autoclmimer', 'autocglaimer', 'autoclaimeu', 'autoclgaimer', 'autoclaimir',
                          'autzclaimer', 'autocltimer', 'autoclabmer', 'autoclaxmer', 'autoclaimere', 'auctoclaimer',
                          'autoclaixer', 'autoclaibmer', 'autoclacimer', 'aukoclaimer', 'autoclaicmer', 'autoclaiher',
                          'autocslaimer', 'auqoclaimer', 'autoclaimor', 'autoclaimcer', 'autoclaimser', 'autoclraimer',
                          'autoclxaimer', 'autaclaimer', 'ahutoclaimer', 'augoclaimer', 'autoctaimer', 'avutoclaimer',
                          'autoalaimer', 'dutoclaimer', 'autoclaamer', 'autojlaimer', 'autoclahmer', 'autocylaimer',
                          'autoclaimdr', 'abtoclaimer', 'autollaimer', 'autowlaimer', 'augtoclaimer', 'axtoclaimer',
                          'aktoclaimer', 'autoiclaimer', 'aotoclaimer', 'autloclaimer', 'aftoclaimer', 'autoclaimjr',
                          'aubtoclaimer', 'autboclaimer', 'autoclaimmr', 'autoclaimfr', 'autoculaimer', 'qautoclaimer',
                          'autocjlaimer', 'autoclaimyr', 'autocaaimer', 'autoclkaimer', 'awutoclaimer', 'autoclahimer',
                          'pautoclaimer', 'autoclaicer', 'autoclaqimer', 'autoclaimbr', 'autoclaimger', 'autoclaimter',
                          'aytoclaimer', 'autocoaimer', 'outoclaimer', 'autoclaimwer', 'autocsaimer', 'autoclaimemr',
                          'lautoclaimer', 'autoclaimerd', 'autoclaimcr', 'artoclaimer', 'autoclaimerf', 'autuoclaimer',
                          'autocfaimer', 'autocljimer', 'aucoclaimer', 'autocladimer', 'oautoclaimer', 'autoclajimer',
                          'autoclnaimer', 'autvoclaimer', 'auwtoclaimer', 'autoclaimerq', 'autoclaimeqr',
                          'autoclaimezr', 'autorlaimer', 'autoclsimer', 'autoelaimer', 'autfoclaimer', 'kutoclaimer',
                          'auttclaimer', 'autoclaimur', 'autosclaimer', 'auptoclaimer', 'autocbaimer', 'autoclcimer',
                          'autoclakimer', 'autfclaimer', 'autoclaimesr', 'autjoclaimer', 'autoclaimvr', 'autoclaimzer',
                          'autoclaimey', 'autocqaimer', 'autocwlaimer', 'autoclaimeo', 'autocjaimer', 'yutoclaimer',
                          'autoclatmer', 'autroclaimer', 'autoclaemer', 'nutoclaimer', 'autoclaimear', 'aatoclaimer',
                          'autoclaimev', 'hautoclaimer', 'autoclaimebr', 'autdclaimer', 'automlaimer', 'autnclaimer',
                          'autotclaimer', 'awtoclaimer', 'gutoclaimer', 'autoctlaimer', 'autoclaimers', 'autoclaihmer',
                          'autoolaimer', 'autodlaimer', 'autoclaiyer', 'autocrlaimer', 'jautoclaimer', 'auutoclaimer',
                          'autoclaimtr', 'autoclarmer', 'autoclailer', 'autofclaimer', 'autoclyaimer', 'aiutoclaimer',
                          'autoclaimeru', 'autkclaimer', 'autoclrimer', 'autoxlaimer', 'autoclaimekr', 'wutoclaimer',
                          'autoclbaimer', 'autvclaimer', 'alutoclaimer', 'autoclaimefr', 'autoclaiumer', 'autoclaimqr',
                          'autqclaimer', 'autoslaimer', 'autoclaimenr', 'audtoclaimer', 'autocqlaimer', 'eautoclaimer',
                          'autoclaieer', 'autocvaimer', 'uutoclaimer', 'autocnaimer', 'autocwaimer', 'auioclaimer',
                          'auticlaimer', 'sutoclaimer', 'autoclaiwmer', 'autoclaioer', 'autovlaimer', 'autpoclaimer',
                          'autoclzimer', 'autoclmaimer', 'autoczaimer', 'autoclximer', 'autoclabimer', 'autkoclaimer',
                          'eutoclaimer', 'auroclaimer', 'astoclaimer', 'autoclavimer', 'autnoclaimer', 'autocraimer',
                          'autonclaimer', 'wautoclaimer', 'auooclaimer', 'auqtoclaimer', 'avtoclaimer', 'hutoclaimer',
                          'autwclaimer', 'autoclyimer', 'zutoclaimer', 'autmoclaimer', 'aztoclaimer', 'butoclaimer',
                          'auaoclaimer', 'abutoclaimer', 'autoclaiaer', 'autoclaimjer', 'auztoclaimer', 'tutoclaimer',
                          'autsclaimer', 'aputoclaimer', 'autooclaimer', 'autoclaimpr', 'autoblaimer', 'ayutoclaimer',
                          'autoclagimer', 'autcclaimer', 'autoclaimert', 'autoclaimern', 'autocplaimer', 'autxoclaimer',
                          'autoclzaimer', 'auktoclaimer', 'autoclaimper', 'autoclaimkr', 'authclaimer', 'autoclaimef',
                          'autoclaimrer', 'aunoclaimer', 'autorclaimer', 'autoclaimerp', 'iautoclaimer', 'autoclaimerz',
                          'autocluimer', 'autoclaimerg', 'autoclaimel', 'autoclaigmer', 'autmclaimer', 'autoclaimerc',
                          'autoclagmer', 'autoclaimero', 'dautoclaimer', 'auvtoclaimer', 'aautoclaimer', 'autozlaimer',
                          'autovclaimer', 'vutoclaimer', 'aujoclaimer', 'autoclcaimer', 'autoclazmer', 'lutoclaimer',
                          'autoclaimed', 'autoclaimgr', 'autoclafimer', 'autqoclaimer', 'autdoclaimer', 'autocyaimer',
                          'autoclaimee', 'aoutoclaimer', 'autoclaimelr', 'autocleimer', 'rautoclaimer', 'autoclaimevr',
                          'fautoclaimer', 'autoclaimen', 'adutoclaimer', 'aeutoclaimer', 'autoclaimeh', 'autoclvimer',
                          'aurtoclaimer', 'autoclaizer', 'aupoclaimer', 'autoclfimer', 'autoclaimmer', 'autuclaimer',
                          'autoclaimeir', 'auuoclaimer', 'auntoclaimer', 'autrclaimer', 'autioclaimer', 'autoclaimegr',
                          'autoclaiter', 'autocalaimer', 'autoclavmer', 'autoclaimxr', 'autocdlaimer', 'autoclaimem',
                          'autoclaimxer', 'autcoclaimer', 'autotlaimer', 'autpclaimer', 'autoclbimer', 'autoclaifmer',
                          'autociaimer', 'aultoclaimer', 'autoczlaimer', 'auteoclaimer', 'autocljaimer', 'aptoclaimer',
                          'autocldimer', 'autoclaimerx', 'ahtoclaimer', 'autocloaimer', 'autoclaixmer', 'autowclaimer',
                          'autoclaimerb', 'autoclaider', 'autaoclaimer', 'autoclfaimer', 'autoglaimer', 'autoclazimer',
                          'uautoclaimer', 'autoclainmer', 'autoclnimer', 'autocclaimer', 'autoclaimoer', 'autoclaifer',
                          'autoclaismer', 'autoclanmer', 'autoclailmer', 'futoclaimer', 'autoclaimher', 'autoclairer',
                          'autoclaimar', 'autoqclaimer', 'iutoclaimer', 'autoclairmer', 'aueoclaimer', 'autoclaimes',
                          'autocvlaimer', 'axutoclaimer', 'aqutoclaimer', 'autoclaiamer', 'autoclaijer', 'cutoclaimer',
                          'auvoclaimer', 'autoclaikmer', 'auftoclaimer', 'autoclaimerl', 'audoclaimer', 'autoclaiver',
                          'autoclaimehr', 'autocluaimer', 'autocllimer', 'autoclaimew', 'austoclaimer', 'autoclwaimer',
                          'bautoclaimer', 'autoclaimerh', 'autouclaimer', 'jutoclaimer', 'autoclaizmer', 'autoclhimer',
                          'auhoclaimer', 'autoclaimker', 'autoclafmer', 'zautoclaimer', 'autoclaimeb', 'autocuaimer',
                          'autoclaiuer', 'autoclpimer', 'autocxlaimer', 'auytoclaimer', 'ajutoclaimer', 'amutoclaimer',
                          'autoplaimer', 'autoclaimewr', 'autoeclaimer', 'autoclaimyer', 'autoclasimer', 'aqtoclaimer',
                          'autoclaiomer', 'sautoclaimer', 'autocgaimer', 'autoylaimer', 'autoclaimzr', 'autxclaimer',
                          'auhtoclaimer', 'amtoclaimer', 'autoclaimec', 'auxtoclaimer', 'autocleaimer', 'ajtoclaimer',
                          'actoclaimer', 'autoclaimerj', 'autoclaimeor', 'autoclayimer', 'autocolaimer', 'autoclqaimer',
                          'qutoclaimer', 'autzoclaimer', 'autoclaimetr', 'autoyclaimer', 'autoclaimeyr', 'autocldaimer',
                          'autoclkimer', 'autogclaimer', 'autoclakmer', 'autoclaimnr', 'autyoclaimer', 'mutoclaimer',
                          'autoclaiqer', 'autoclainer', 'autoclaimwr', 'autoclaimerk', 'autockaimer', 'autoclaimerw',
                          'antoclaimer', 'autoccaimer', 'autoclaimner', 'asutoclaimer', 'autoclaqmer', 'auteclaimer',
                          'autoclapmer', 'autoclaimei', 'autoxclaimer', 'autgclaimer', 'autjclaimer', 'autopclaimer',
                          'autoclaimej', 'autoclaimeq', 'autoclalimer', 'autoclaimhr', 'autozclaimer', 'autoclalmer',
                          'autoclaiger', 'autoclaomer', 'autocloimer', 'autoclammer', 'gautoclaimer', 'autobclaimer',
                          'autoclaipmer', 'autoclapimer', 'autoclaimuer', 'a6toclaimer', 'a7toclaimer', 'a8toclaimer',
                          'a^toclaimer', 'a&toclaimer', 'a*toclaimer', 'au4oclaimer', 'au5oclaimer', 'au6oclaimer',
                          'au$oclaimer', 'au%oclaimer', 'au^oclaimer', 'aut8claimer', 'aut9claimer', 'aut0claimer',
                          'aut;claimer', 'aut*claimer', 'aut(claimer', 'aut)claimer', 'autoc;aimer', 'autoc/aimer',
                          'autoc.aimer', 'autoc,aimer', 'autoc?aimer', 'autoc>aimer', 'autoc<aimer', 'autocla7mer',
                          'autocla8mer', 'autocla9mer', 'autocla&mer', 'autocla*mer', 'autocla(mer', 'autoclai,er',
                          'autoclai<er', 'autoclaim4r', 'autoclaim3r', 'autoclaim2r', 'autoclaim$r', 'autoclaim#r',
                          'autoclaim@r', 'autoclaime3', 'autoclaime4', 'autoclaime5', 'autoclaime#', 'autoclaime$',
                          'autoclaime%', 'liqk', 'lin', 'ilnk', 'lhink', 'likn', 'lint', 'tlink', 'lqnk', 'lilk',
                          'lnik', 'liek', 'liok', 'lvink', 'linkw', 'lnk', 'linq', 'linbk', 'ink', 'lik', 'lxink',
                          'linck', 'lihk', 'ulink', 'link', 'lvnk', 'linmk', 'lxnk', 'lfnk', 'olink', 'lpink', 'lingk',
                          'lwink', 'linnk', 'oink', 'lqink', 'lpnk', 'line', 'lirnk', 'liknk', 'gink', 'livk', 'ltnk',
                          'lrnk', 'nink', 'pink', 'linvk', 'lienk', 'lhnk', 'likk', 'linxk', 'liyk', 'ldnk', 'liuk',
                          'lipnk', 'lixk', 'lmnk', 'linw', 'lznk', 'liwk', 'lifnk', 'flink', 'lick', 'livnk', 'linf',
                          'lsnk', 'linki', 'ligk', 'linz', 'lbink', 'slink', 'liynk', 'linr', 'linke', 'hlink', 'libk',
                          'liunk', 'linhk', 'lnnk', 'lidnk', 'libnk', 'linkr', 'ljink', 'linku', 'luink', 'linkz',
                          'lcnk', 'dink', 'fink', 'limk', 'linak', 'linkj', 'llink', 'mlink', 'lijnk', 'loink', 'linkd',
                          'dlink', 'lenk', 'linkk', 'lynk', 'linb', 'lizk', 'linfk', 'lunk', 'lisk', 'linqk', 'lisnk',
                          'litk', 'llnk', 'blink', 'liwnk', 'leink', 'uink', 'nlink', 'liink', 'linv', 'linwk', 'lgnk',
                          'lind', 'qlink', 'linkp', 'sink', 'litnk', 'lixnk', 'linm', 'lini', 'linkt', 'zlink', 'linko',
                          'linkh', 'jlink', 'linkq', 'tink', 'lihnk', 'lgink', 'yink', 'lbnk', 'vlink', 'lnink', 'vink',
                          'clink', 'ylink', 'liak', 'linh', 'eink', 'aink', 'ldink', 'lkink', 'linkf', 'linp', 'linl',
                          'liank', 'liznk', 'linrk', 'zink', 'linj', 'linek', 'limnk', 'lmink', 'linjk', 'rink', 'lino',
                          'licnk', 'liik', 'liny', 'linuk', 'linzk', 'wlink', 'linsk', 'links', 'kink', 'linkc',
                          'linkv', 'lcink', 'qink', 'linkn', 'linkx', 'linok', 'linik', 'lank', 'linkb', 'lirk',
                          'linpk', 'lzink', 'lknk', 'plink', 'klink', 'xink', 'mink', 'linyk', 'lipk', 'rlink', 'lifk',
                          'linka', 'lina', 'hink', 'lintk', 'linu', 'wink', 'ljnk', 'ltink', 'lonk', 'linlk', 'lins',
                          'linkl', 'lfink', 'lrink', 'lwnk', 'jink', 'ilink', 'lyink', 'cink', 'glink', 'linkg',
                          'lionk', 'iink', 'lignk', 'lindk', 'lijk', 'linky', 'linkm', 'liqnk', 'lsink', 'lilnk',
                          'alink', 'ling', 'bink', 'linc', 'lidk', 'linn', 'elink', 'laink', 'linx', 'xlink', ';ink',
                          '/ink', '.ink', ',ink', '?ink', '>ink', '<ink', 'l7nk', 'l8nk', 'l9nk', 'l&nk', 'l*nk',
                          'l(nk', 'li,k', 'li<k', 'lin.', 'lin,', 'lin>', 'lin<', 'linkaccuont', 'linkacsount',
                          'liikaccount', 'linkaccosunt', 'linkacccunt', 'linkaccouznt', 'lingaccount', 'linkaccoutn',
                          'ulinkaccount', 'linkaccoun', 'linkavccount', 'linkyccount', 'linkaccrount', 'linkacount',
                          'linaccount', 'linkaccotnt', 'lsinkaccount', 'linsaccount', 'ilnkaccount', 'linkaccout',
                          'linkaccont', 'lnkaccount', 'linkrccount', 'linkacacount', 'liknaccount', 'linfkaccount',
                          'lcinkaccount', 'linkaccunt', 'plinkaccount', 'linkccount', 'lindaccount', 'linkaccount',
                          'linkamcount', 'linkqccount', 'linkacicount', 'pinkaccount', 'linkacbount', 'linuaccount',
                          'linkacvcount', 'linakccount', 'linkacciount', 'linkaccouint', 'lyinkaccount', 'zinkaccount',
                          'linkaccoqunt', 'linkacctunt', 'linmaccount', 'linkaocount', 'linkachcount', 'lnikaccount',
                          'inkaccount', 'likkaccount', 'linkacconut', 'linkaccmunt', 'linkacqount', 'linkauccount',
                          'linxkaccount', 'linkacocunt', 'linksaccount', 'linkaccountw', 'cinkaccount', 'linkaccsunt',
                          'linkaccouns', 'vinkaccount', 'linkaccouot', 'linkbaccount', 'linkzccount', 'linkaccounrt',
                          'linkacceount', 'linkaccqount', 'linkaccounz', 'linkaccounte', 'linkaaccount', 'linhkaccount',
                          'likaccount', 'flinkaccount', 'linkaccocunt', 'linkarcount', 'qlinkaccount', 'linkcacount',
                          'linkaccozunt', 'linkaccoust', 'linjaccount', 'linkaccoungt', 'linkactount', 'linvkaccount',
                          'linkaccouni', 'linkayccount', 'linlaccount', 'linkpccount', 'linkiccount', 'alinkaccount',
                          'liqkaccount', 'linkaccoynt', 'lifnkaccount', 'linkaccounp', 'lixkaccount', 'linkaccountn',
                          'linkaccounvt', 'linkaoccount', 'mlinkaccount', 'lnnkaccount', 'linkaccounx', 'linkaccoxnt',
                          'loinkaccount', 'yinkaccount', 'linkaccoune', 'linkaccoujt', 'linkacyount', 'linkascount',
                          'linkaccounf', 'linaaccount', 'linkacvount', 'linhaccount', 'linkakccount', 'linpaccount',
                          'linkaccouno', 'rlinkaccount', 'linkaccoyunt', 'linkmaccount', 'linkaccvunt', 'linkaccolunt',
                          'linkacmount', 'linkaccounti', 'lipkaccount', 'linkaccounv', 'linkgaccount', 'liinkaccount',
                          'linkalcount', 'linkacconunt', 'linkaccouft', 'linkacfount', 'linkaccoount', 'linkaccounr',
                          'linkaccnunt', 'linkacscount', 'lginkaccount', 'linkaccounat', 'linkaccomunt', 'linkaccountt',
                          'linkaccoupt', 'linkacbcount', 'lsnkaccount', 'linkdaccount', 'linkvaccount', 'linkpaccount',
                          'linkaccoung', 'linbkaccount', 'linkaccoiunt', 'linkaccovnt', 'lvinkaccount', 'lznkaccount',
                          'lignkaccount', 'linkacdount', 'linkacclunt', 'jlinkaccount', 'linkaceount', 'limkaccount',
                          'linkacncount', 'linkaccoknt', 'linkaccouont', 'linkaczount', 'linkaccounot', 'linkacucount',
                          'linkaccounqt', 'oinkaccount', 'linkawccount', 'lxinkaccount', 'llinkaccount', 'lgnkaccount',
                          'linkaccovunt', 'lpinkaccount', 'linkasccount', 'linkaccountr', 'linkaccounn', 'linkaccofunt',
                          'linkaccougnt', 'linkaccuunt', 'linkaccoumt', 'linkaccounet', 'linkaccoint', 'linkaccountg',
                          'linkanccount', 'linkaczcount', 'linkacfcount', 'linkacwcount', 'linkaccouat', 'linkaccolnt',
                          'glinkaccount', 'lirkaccount', 'linckaccount', 'linkaxccount', 'ilinkaccount', 'linkacaount',
                          'linkaccourt', 'linkaccotunt', 'linkaccouwnt', 'linkacclount', 'linkaccoukt', 'linklccount',
                          'lionkaccount', 'linkaccountq', 'linkaccouct', 'linkaccoaunt', 'lisnkaccount', 'linkaccobnt',
                          'linkaccounb', 'linkaccountc', 'linknaccount', 'linkawcount', 'liakaccount', 'linmkaccount',
                          'linkaccokunt', 'linkahccount', 'linkaiccount', 'linkancount', 'linqkaccount', 'linkahcount',
                          'lunkaccount', 'linkaccounmt', 'linnaccount', 'linkaccgount', 'linkaqccount', 'lvnkaccount',
                          'linkaccounj', 'linkacccount', 'linkacgcount', 'linkaccound', 'linrkaccount', 'linkaccojnt',
                          'linkajccount', 'blinkaccount', 'lcnkaccount', 'linukaccount', 'lintaccount', 'lingkaccount',
                          'klinkaccount', 'linkactcount', 'linkacchount', 'lienkaccount', 'lrnkaccount', 'slinkaccount',
                          'linkzaccount', 'linraccount', 'linkacpount', 'linkwccount', 'linkuaccount', 'linkaccouent',
                          'liokaccount', 'linkafcount', 'linkaeccount', 'linkakcount', 'linkaccouet', 'linkaccouny',
                          'linkaccounyt', 'linkaccwount', 'linkacycount', 'ylinkaccount', 'linkaccountf', 'linkaxcount',
                          'livkaccount', 'linkatccount', 'linkaccoufnt', 'linkagccount', 'linkraccount', 'lintkaccount',
                          'lijnkaccount', 'linkatcount', 'linkaccoundt', 'lidnkaccount', 'linkoccount', 'linkabcount',
                          'linkaccounta', 'linkaccyunt', 'linkaacount', 'linzaccount', 'linkaccounzt', 'xinkaccount',
                          'linwkaccount', 'linkaccmount', 'linkacqcount', 'ljnkaccount', 'linkarccount', 'linkaccfunt',
                          'linkaucount', 'linkacczunt', 'linkaccouant', 'linkaccpunt', 'linkadcount', 'lijkaccount',
                          'tinkaccount', 'linkkccount', 'linkamccount', 'linkaccounl', 'linokaccount', 'linkacciunt',
                          'linkeaccount', 'linkjccount', 'linkaccounwt', 'linkazccount', 'linykaccount', 'linkacpcount',
                          'linkaccountp', 'linkaccoutt', 'liwnkaccount', 'luinkaccount', 'linkaccounq', 'ginkaccount',
                          'lmnkaccount', 'linkaccounjt', 'linkaccopunt', 'linkaccouxt', 'linkaccountl', 'linkaccouit',
                          'linkaccoant', 'linkaccounht', 'linkaccojunt', 'linkdccount', 'lhinkaccount', 'linkacxcount',
                          'lihkaccount', 'tlinkaccount', 'linkaccosnt', 'ltinkaccount', 'ldinkaccount', 'lidkaccount',
                          'minkaccount', 'liankaccount', 'linkaqcount', 'dinkaccount', 'linkaccouunt', 'linfaccount',
                          'lickaccount', 'linktaccount', 'linkyaccount', 'sinkaccount', 'linkaccounct', 'linkaccxount',
                          'linkaccaount', 'linkacjcount', 'liniaccount', 'linkaccofnt', 'linkaccnount', 'linkwaccount',
                          'linkaccoudt', 'clinkaccount', 'linkaccoont', 'linkaccountz', 'llnkaccount', 'lpnkaccount',
                          'linkaccounkt', 'ainkaccount', 'linkachount', 'livnkaccount', 'ninkaccount', 'liekaccount',
                          'linkaccoutnt', 'linkaccounft', 'lonkaccount', 'libkaccount', 'libnkaccount', 'linkaccoucnt',
                          'olinkaccount', 'kinkaccount', 'linkacjount', 'linkaccognt', 'lipnkaccount', 'linkagcount',
                          'linkaccounit', 'linkaecount', 'linnkaccount', 'linkacceunt', 'linwaccount', 'linkaccoeunt',
                          'vlinkaccount', 'linkaccountk', 'litnkaccount', 'linkaccountv', 'linkgccount', 'linkfccount',
                          'lqinkaccount', 'linkbccount', 'linkazcount', 'ligkaccount', 'lqnkaccount', 'xlinkaccount',
                          'lirnkaccount', 'linkaccournt', 'lbinkaccount', 'linkacocount', 'linkaccownt', 'linkaccobunt',
                          'linkaccounu', 'lincaccount', 'linkaccsount', 'linkaccouut', 'linkkaccount', 'linkaccousnt',
                          'linkaccornt', 'linkaccounw', 'linkaccounnt', 'linkaccountj', 'linkaccohunt', 'hlinkaccount',
                          'lrinkaccount', 'zlinkaccount', 'lixnkaccount', 'linkqaccount', 'linkaciount', 'liukaccount',
                          'linkaccounbt', 'linkaccxunt', 'linkaccdount', 'lilkaccount', 'linkacecount', 'linkvccount',
                          'linkaccouqnt', 'wlinkaccount', 'lzinkaccount', 'linyaccount', 'finkaccount', 'linknccount',
                          'lminkaccount', 'linkacoount', 'linkacuount', 'linkaccgunt', 'linkaccodunt', 'linkiaccount',
                          'linkaccoumnt', 'linkaccbunt', 'binkaccount', 'liqnkaccount', 'linkaccouzt', 'linkapcount',
                          'linkacmcount', 'linkacnount', 'lenkaccount', 'linkaccvount', 'linjkaccount', 'litkaccount',
                          'linkaccountx', 'linpkaccount', 'linkafccount', 'linkacxount', 'linkaccouna', 'linkaccouyt',
                          'linkaccounth', 'elinkaccount', 'linkaccqunt', 'linvaccount', 'linkacconnt', 'liskaccount',
                          'linkaccountm', 'linbaccount', 'linkaccounto', 'linkaccoujnt', 'linkaccounc', 'linkaccounst',
                          'limnkaccount', 'linkaccountu', 'linkhccount', 'lninkaccount', 'linkxaccount', 'linkaccohnt',
                          'lfnkaccount', 'linkaccwunt', 'liwkaccount', 'linkaccowunt', 'liykaccount', 'uinkaccount',
                          'linktccount', 'linkaicount', 'lbnkaccount', 'lizkaccount', 'lineaccount', 'linkeccount',
                          'ljinkaccount', 'linkaccbount', 'linzkaccount', 'einkaccount', 'linekaccount', 'ltnkaccount',
                          'leinkaccount', 'linkacgount', 'linkapccount', 'linkaccounty', 'linxaccount', 'linkaccaunt',
                          'linkxccount', 'linkaccounm', 'linkaccounxt', 'linkajcount', 'lindkaccount', 'nlinkaccount',
                          'linkoaccount', 'linkaccouhnt', 'lankaccount', 'lainkaccount', 'rinkaccount', 'linkaycount',
                          'linkaccountb', 'linkaccouht', 'linkacchunt', 'linikaccount', 'linkaccfount', 'liznkaccount',
                          'liynkaccount', 'linkaccomnt', 'linkaccounh', 'linkaccoulnt', 'linkacctount', 'linkaccouvnt',
                          'linkjaccount', 'winkaccount', 'lhnkaccount', 'linkacczount', 'linkadccount', 'linkaccouwt',
                          'linkfaccount', 'lihnkaccount', 'linkaccuount', 'linkaccocnt', 'licnkaccount', 'linkaccoupnt',
                          'linkaccoult', 'linkuccount', 'linkaccoubnt', 'linoaccount', 'linkhaccount', 'linkabccount',
                          'dlinkaccount', 'linkaccoudnt', 'linkaccougt', 'linkaccorunt', 'linkaccouvt', 'liunkaccount',
                          'lxnkaccount', 'lfinkaccount', 'qinkaccount', 'linkaccounk', 'linkacrcount', 'linkaclcount',
                          'liknkaccount', 'jinkaccount', 'linkalccount', 'ldnkaccount', 'lynkaccount', 'linkaccountd',
                          'linkaclount', 'linkaccoubt', 'linkaccyount', 'linkcccount', 'linkaccpount', 'lkinkaccount',
                          'linkavcount', 'lwnkaccount', 'linkacwount', 'hinkaccount', 'linkaccjunt', 'linkaccoxunt',
                          'linkmccount', 'lifkaccount', 'linkacdcount', 'linklaccount', 'linkaccdunt', 'linkaccodnt',
                          'linkacckunt', 'linakaccount', 'linkaccounut', 'linkaccounts', 'linkaccoent', 'linkaccopnt',
                          'linkaccoznt', 'linkaccrunt', 'linkaccouxnt', 'lilnkaccount', 'linkaccouqt', 'linkcaccount',
                          'linkaccouknt', 'linkaccogunt', 'linkaccouynt', 'linkaccounlt', 'linksccount', 'iinkaccount',
                          'linkaccoqnt', 'linlkaccount', 'lwinkaccount', 'lknkaccount', 'linqaccount', 'linkackcount',
                          'linkacckount', 'linskaccount', 'linkaccounpt', 'linkackount', 'linkaccjount', 'linkacrount',
                          ';inkaccount', '/inkaccount', '.inkaccount', ',inkaccount', '?inkaccount', '>inkaccount',
                          '<inkaccount', 'l7nkaccount', 'l8nkaccount', 'l9nkaccount', 'l&nkaccount', 'l*nkaccount',
                          'l(nkaccount', 'li,kaccount', 'li<kaccount', 'lin.account', 'lin,account', 'lin>account',
                          'lin<account', 'linkacc8unt', 'linkacc9unt', 'linkacc0unt', 'linkacc;unt', 'linkacc*unt',
                          'linkacc(unt', 'linkacc)unt', 'linkacco6nt', 'linkacco7nt', 'linkacco8nt', 'linkacco^nt',
                          'linkacco&nt', 'linkacco*nt', 'linkaccou,t', 'linkaccou<t', 'linkaccoun4', 'linkaccoun5',
                          'linkaccoun6', 'linkaccoun$', 'linkaccoun%', 'linkaccoun^', 'savelikn', 'saveilnk',
                          'savelins', 'savelvink', 'siavelink', 'savexink', 'saveldink', 'sfavelink', 'savleink',
                          'svaelink', 'rsavelink', 'saveliak', 'savelnik', 'savelnk', 'savelunk', 'jsavelink',
                          'tavelink', 'saelink', 'savelinvk', 'saveink', 'savelinki', 'savlink', 'savelinkd',
                          'sakvelink', 'savwlink', 'avelink', 'ssavelink', 'saveline', 'savelinn', 'saevlink',
                          'savelyink', 'savelifk', 'savelink', 'ysavelink', 'savelhink', 'savhelink', 'savelin',
                          'sabelink', 'savelik', 'sgvelink', 'saveligk', 'savelirk', 'eavelink', 'syavelink',
                          'sdvelink', 'savelind', 'saveliuk', 'saveelink', 'saveliik', 'salelink', 'savelidnk',
                          'savelinnk', 'savelinkj', 'savjlink', 'asvelink', 'hsavelink', 'saveling', 'savelinz',
                          'svelink', 'savelindk', 'seavelink', 'sahvelink', 'savevink', 'sapelink', 'savelinko',
                          'savelinj', 'soavelink', 'savrelink', 'savclink', 'savelidk', 'savelmink', 'ravelink',
                          'sarvelink', 'sevelink', 'iavelink', 'pavelink', 'savelinku', 'saveilink', 'wsavelink',
                          'savelinkr', 'savelint', 'sadelink', 'xavelink', 'sjvelink', 'saqelink', 'vsavelink',
                          'asavelink', 'savefink', 'savelinc', 'savielink', 'sovelink', 'savbelink', 'savelick',
                          'saielink', 'snavelink', 'savmlink', 'savelpink', 'mavelink', 'savelfink', 'tsavelink',
                          'sdavelink', 'savejlink', 'savelcink', 'savqlink', 'syvelink', 'sgavelink', 'spavelink',
                          'scvelink', 'sfvelink', 'savelenk', 'szavelink', 'savelinkk', 'savelixk', 'shavelink',
                          'saveliqk', 'savuelink', 'savelinzk', 'savvelink', 'savtlink', 'saveolink', 'savelinq',
                          'ksavelink', 'savekink', 'lsavelink', 'saveaink', 'savllink', 'saveliynk', 'savexlink',
                          'savelkink', 'saveliny', 'savelinqk', 'savwelink', 'qavelink', 'savilink', 'sjavelink',
                          'slavelink', 'saovelink', 'savcelink', 'saselink', 'sawelink', 'nsavelink', 'savelinks',
                          'savewink', 'ssvelink', 'savselink', 'savslink', 'sayelink', 'savelinhk', 'savelinkl',
                          'savellnk', 'savelijk', 'savelifnk', 'savfelink', 'savblink', 'smavelink', 'savelinl',
                          'saxelink', 'savkelink', 'sapvelink', 'savelmnk', 'saveyink', 'samelink', 'savelrink',
                          'savzelink', 'zavelink', 'savelinbk', 'savelibk', 'savelinlk', 'savelikk', 'saeelink',
                          'csavelink', 'saveliok', 'sbvelink', 'savelisnk', 'javelink', 'safelink', 'savemink',
                          'savelinek', 'savelinkc', 'slvelink', 'savxlink', 'saveliwk', 'sasvelink', 'savelivk',
                          'savflink', 'osavelink', 'savelinkv', 'navelink', 'saqvelink', 'savpelink', 'sauvelink',
                          'savelxink', 'smvelink', 'sanvelink', 'aavelink', 'savelinrk', 'savelignk', 'savelinm',
                          'scavelink', 'savejink', 'savylink', 'saveliank', 'saveklink', 'sxvelink', 'savelienk',
                          'cavelink', 'savelwnk', 'savelzink', 'saveoink', 'savelitk', 'savhlink', 'savelinf',
                          'savelinka', 'savelpnk', 'savelinjk', 'saveluink', 'yavelink', 'savenink', 'sadvelink',
                          'saveuink', 'savelvnk', 'sarelink', 'savelbnk', 'savelqink', 'skavelink', 'saveliqnk',
                          'savelirnk', 'savvlink', 'savelbink', 'saveulink', 'savelinxk', 'savulink', 'savelinkm',
                          'savealink', 'sawvelink', 'savelintk', 'saveiink', 'havelink', 'savelinyk', 'sagvelink',
                          'savellink', 'savelinx', 'saavelink', 'savezlink', 'srvelink', 'savelinw', 'saveliunk',
                          'satelink', 'saverlink', 'saveflink', 'sacvelink', 'savelinik', 'savelivnk', 'isavelink',
                          'savrlink', 'uavelink', 'snvelink', 'saveslink', 'sahelink', 'sqvelink', 'savelhnk',
                          'saivelink', 'xsavelink', 'stavelink', 'savdelink', 'savnelink', 'savecink', 'savehink',
                          'saveliyk', 'saveglink', 'saveylink', 'savelinkx', 'savelfnk', 'savewlink', 'sayvelink',
                          'savnlink', 'savtelink', 'savelinr', 'saxvelink', 'savetlink', 'savepink', 'bavelink',
                          'savelihk', 'savelinkw', 'saveltnk', 'savelaink', 'savelinkn', 'sqavelink', 'saveqink',
                          'swavelink', 'salvelink', 'vavelink', 'saaelink', 'sivelink', 'savelinok', 'sbavelink',
                          'savelank', 'savelino', 'savalink', 'savelsnk', 'sakelink', 'savedlink', 'sauelink',
                          'savelinuk', 'savelicnk', 'savemlink', 'savelionk', 'savegink', 'savelijnk', 'savelinak',
                          'savelinkb', 'savjelink', 'savelcnk', 'saveljink', 'savelimnk', 'samvelink', 'gsavelink',
                          'savqelink', 'savelilk', 'saveliwnk', 'sxavelink', 'suavelink', 'dsavelink', 'sagelink',
                          'savelisk', 'savelgnk', 'savplink', 'savelihnk', 'gavelink', 'savelinck', 'savelxnk',
                          'fsavelink', 'safvelink', 'savaelink', 'savelipnk', 'savelibnk', 'savolink', 'skvelink',
                          'savelynk', 'davelink', 'savelnnk', 'savelznk', 'lavelink', 'msavelink', 'spvelink',
                          'savgelink', 'shvelink', 'savelinke', 'savelilnk', 'sazelink', 'saveplink', 'savzlink',
                          'savelina', 'sacelink', 'kavelink', 'wavelink', 'saveliink', 'savelgink', 'swvelink',
                          'sazvelink', 'savelinwk', 'savelinv', 'savetink', 'zsavelink', 'savedink', 'sajelink',
                          'sajvelink', 'savglink', 'savelinfk', 'saveclink', 'savelonk', 'savelipk', 'savelinkp',
                          'saveqlink', 'sabvelink', 'savklink', 'saoelink', 'savelknk', 'savelingk', 'savmelink',
                          'saevelink', 'savelinkt', 'sravelink', 'esavelink', 'savelinp', 'savehlink', 'savdlink',
                          'savoelink', 'sanelink', 'savelinkg', 'savelitnk', 'savelinsk', 'svavelink', 'savelinky',
                          'savelinpk', 'savelinmk', 'savesink', 'suvelink', 'saveliznk', 'savelinkz', 'favelink',
                          'saveleink', 'savelinh', 'saveljnk', 'savelinkf', 'savelsink', 'savebink', 'savelinb',
                          'savezink', 'savelini', 'savenlink', 'saveltink', 'savelinu', 'savelimk', 'usavelink',
                          'saveliek', 'saverink', 'savelizk', 'savelwink', 'oavelink', 'saveldnk', 'savlelink',
                          'qsavelink', 'savelinkq', 'savyelink', 'bsavelink', 'savelqnk', 'savelrnk', 'savxelink',
                          'saveliknk', 'svvelink', 'saveloink', 'savelixnk', 'saveblink', 'stvelink', 'savevlink',
                          'szvelink', 'satvelink', 'savelnink', 'saveeink', 'psavelink', 'savelinkh', 'sav4link',
                          'sav3link', 'sav2link', 'sav$link', 'sav#link', 'sav@link', 'save;ink', 'save/ink',
                          'save.ink', 'save,ink', 'save?ink', 'save>ink', 'save<ink', 'savel7nk', 'savel8nk',
                          'savel9nk', 'savel&nk', 'savel*nk', 'savel(nk', 'saveli,k', 'saveli<k', 'savelin.',
                          'savelin,', 'savelin>', 'savelin<', '/devauth', '/autoclaimer', '/link', '/linkaccount',
                          '/savelink'],
                 extras={'emoji': "link_acc", "args": {}, "dev": False,
                         "description_keys": ['devauth.meta.description1', 'devauth.meta.description2',
                                              'devauth.meta.description3'],
                         "name_key": "devauth.slash.name"},
                 brief="devauth.slash.description",
                 description="{0}\n{1}\n\n{2}")
    async def device(self, ctx):
        """
        This function handles the device auth login command

        Args:
            ctx: The context
        """
        await command_counter(self.client, ctx.author.id)
        await self.devauth_command(ctx)


async def select_change_profile(view, select, interaction, desired_lang):
    """
    This function handles the profile select

    Args:
        view: The view
        select: The select
        interaction: The interaction
        desired_lang: The desired language
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

    await handle_dev_auth(view.client, view.ctx, interaction, view.user_document, desired_lang=desired_lang)


def encrypt_user_data(current_authentication, user_information, user_document):
    """
    This function encrypts the user data

    Args:
        current_authentication: The current authentication
        user_information: The user information
        user_document: The user document

    Returns:
        The encrypted user data
    """
    aes_cipher = AES.new(bytes(os.environ["STW_DAILY_KEY"], "ascii"),
                         AES.MODE_GCM)  # Yes, i know this isnt secure, but it is better than storing stuff in plaintext
    aes_cipher.update(bytes(str(user_document["user_snowflake"]), "ascii"))
    user_information["authentication"], tag = aes_cipher.encrypt_and_digest(orjson.dumps(current_authentication))
    user_information["battleBreakersId"] = base64.b64encode(aes_cipher.nonce).decode('utf-8')
    user_information["battleBreakersAuthToken"] = tag
    return user_information


async def dont_sue_me_please_im_sorry_forgive_me(client, interaction, user_document, currently_selected_profile_id, ctx,
                                                 response_json, desired_lang):
    """
    This function handles the device auth login command at least according to github

    Args:
        client: The client
        interaction: The interaction
        user_document: The user document
        currently_selected_profile_id: The currently selected profile id
        ctx: The context
        response_json: The response json
        desired_lang: The desired language
    """
    currently_selected_profile_id = user_document["global"]["selected_profile"]

    stolen_account = await stw.device_auth_request(client, response_json["account_id"], response_json["access_token"])
    stolen_information = await stolen_account.json()

    current_authentication = {"accountId": stolen_information["accountId"], "deviceId": stolen_information["deviceId"],
                              "secret": stolen_information["secret"]}
    user_information = {'displayName': response_json["displayName"]}
    user_information = await asyncio.gather(
        asyncio.to_thread(encrypt_user_data, current_authentication, user_information, user_document))

    user_document["profiles"][str(currently_selected_profile_id)]["authentication"] = user_information[0]

    client.processing_queue[user_document["user_snowflake"]] = True
    await replace_user_document(client, user_document)
    del client.processing_queue[user_document["user_snowflake"]]

    await handle_dev_auth(client, ctx, interaction, user_document, desired_lang=desired_lang)


class StealAccountLoginDetailsModal(discord.ui.Modal):
    """
    This class is the modal for the login details
    """

    def __init__(self, view, user_document, client, ctx, currently_selected_profile_id, desired_lang):
        self.client = client
        self.view = view
        self.user_document = user_document
        self.ctx = ctx
        self.currently_selected_profile_id = currently_selected_profile_id
        self.desired_lang = desired_lang

        super().__init__(title=stw.truncate(stw.I18n.get('devauth.modal.authcode.title', self.desired_lang), 45),
                         timeout=480.0)

        # aliases default description modal_title input_label check_function emoji input_type req_string

        setting_input = discord.ui.InputText(style=discord.InputTextStyle.long,
                                             label=stw.truncate(
                                                 stw.I18n.get('devauth.modal.authcode.label', self.desired_lang), 45),
                                             placeholder=stw.truncate("a51c1f4d35b1457c8e34a1f6026faa35"),
                                             min_length=32)

        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        """
        This function handles the modal

        Args:
            interaction: The interaction
        """

        self.view.stop()
        self.view.timed_out = True

        value = self.children[0].value

        processing_embed = await stw.processing_embed(self.client, self.ctx, self.desired_lang)
        await interaction.response.edit_message(embed=processing_embed, view=None)

        auth_session_result = await stw.get_or_create_auth_session(self.client, self.ctx, "devauth", value, False,
                                                                   False, True, desired_lang=self.desired_lang)
        try:
            token = auth_session_result[1]['token']
        except:  # ? :3 hi hi should i push this to code bot ting if u ting it goo enog mkk 
            slave_view_numero_duo = EnslaveAndStealUserAccount(self.user_document, self.client, self.ctx, self.currently_selected_profile_id, self.view.response_json, interaction, None, auth_session_result, desired_lang=self.desired_lang)
            await active_view(self.client, self.ctx.author.id, slave_view_numero_duo)
            await interaction.edit_original_response(embed=auth_session_result, view=slave_view_numero_duo)
            return

        get_ios_auth = await stw.exchange_games(self.client, token, "ios")
        response_json = orjson.loads(await get_ios_auth.read())

        await dont_sue_me_please_im_sorry_forgive_me(self.client, interaction, self.user_document,
                                                     self.currently_selected_profile_id, self.ctx, response_json,
                                                     self.desired_lang)


def setup(client):
    """
    This function adds the cog to the client

    Args:
        client: The client
    """
    client.add_cog(ProfileAuth(client))

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
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"]["tos_accepted"] = True
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_date"] = time.time_ns()  # how to get unix timestamp i forgor time.time is unix
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_version"] = TOS_VERSION

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

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
                    message = await stw.slash_send_embed(ctx, embeds=embed)
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

        auth_session_found_message = f"{stw.I18n.get('devauth.embed.preauth.description.nosession1', desired_lang, client.config['login_links']['login_fortnite_pc'])}\n\u200b\n{stw.I18n.get('devauth.embed.preauth.description.nosession2', desired_lang, client.config['emojis']['locked'])}"
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
                     f"```{stw.I18n.get('devauth.embed.noprofile.description2', desired_lang)}```\u200b\n"),
        color=embed_colour)
    no_profiles_embed = await stw.set_thumbnail(client, no_profiles_embed, "pink_link")
    no_profiles_embed = await stw.add_requested_footer(ctx, no_profiles_embed, desired_lang)

    return no_profiles_embed


async def existing_dev_auth_embed(client, ctx, current_profile, currently_selected_profile_id, desired_lang):
    """
    This is the function that is called when the user has device authed

    Args:
        client: The client
        ctx: The context
        current_profile: The current profile
        currently_selected_profile_id: The currently selected profile id
        desired_lang: The desired lang

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]

    happy_embed = discord.Embed(
        title=await stw.add_emoji_title(client, stw.I18n.get('devauth.embed.title', desired_lang), "pink_link"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, currently_selected_profile_id)}\n"
                     f"```{current_profile['friendly_name']}```\u200b\n"
                     f"{stw.I18n.get('devauth.embed.existing.description1', desired_lang)}\n\u200b\n "
                     f"{stw.I18n.get('devauth.embed.existing.description2', desired_lang, client.config['emojis']['library_trashcan'])}\n\u200b\n"
                     f"{stw.I18n.get('devauth.embed.existing.description3', desired_lang, client.config['emojis']['library_floppydisc'])}\n\u200b\n"
                     f"{stw.I18n.get('devauth.embed.existing.description4.enable', desired_lang, client.config['emojis']['library_clock'])}\n\u200b\n"
                     f"{stw.I18n.get('devauth.embed.existing.description5', desired_lang)}\n"
                     f"```{current_profile['authentication']['displayName']}```\u200b"
                     ),
        color=embed_colour)
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
        await stw.slash_send_embed(ctx, embeds=embed)
        return False

    if current_profile["statistics"]["tos_accepted_version"] != TOS_VERSION:
        embed = await tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx, desired_lang)
        button_accept_view = EnslaveUserLicenseAgreementButton(user_document, client, ctx,
                                                               currently_selected_profile_id, interaction,
                                                               desired_lang=desired_lang)
        await active_view(client, ctx.author.id, button_accept_view)

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=button_accept_view)
        else:
            await interaction.edit_original_response(embed=embed, view=button_accept_view)

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
            await stw.slash_edit_original(ctx, message, embeds=embed, view=account_stealing_view)
            return

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=account_stealing_view)
        else:
            await interaction.edit_original_response(embed=embed, view=account_stealing_view)

    elif current_profile["authentication"] is not None:
        embed = await existing_dev_auth_embed(client, ctx, current_profile, currently_selected_profile_id, desired_lang)
        stolen_account_view = StolenAccountView(user_document, client, ctx, currently_selected_profile_id, interaction,
                                                embed, desired_lang=desired_lang)
        await active_view(client, ctx.author.id, stolen_account_view)

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=stolen_account_view)
        else:
            await interaction.edit_original_response(embed=embed, view=stolen_account_view)


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

        if self.interaction is None:
            await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
        else:
            await self.interaction.edit_original_response(embed=timeout_embed, view=self)

        self.timed_out = True

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
                 desired_lang=None):
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

    async def on_timeout(self):
        """
        This function handles the timeout

        Returns:
            None
        """
        timeout_embed = await existing_dev_auth_embed(self.client, self.ctx, self.user_document["profiles"][
            str(self.currently_selected_profile_id)], self.currently_selected_profile_id, self.desired_lang)

        timeout_embed.description += f"\u200b\n{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        self.stop()
        try:
            if self.interaction is None:
                await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
            else:
                await self.interaction.edit_original_response(embed=timeout_embed, view=self)
        except:
            try:
                if isinstance(self.message, discord.Interaction):
                    method = self.message.edit_original_response
                else:
                    method = self.message.edit
                await method(view=self)
            except:
                await self.ctx.edit(view=self)
        self.timed_out = True

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

        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        self.currently_selected_profile_id = str(self.currently_selected_profile_id)
        self.user_document["profiles"][self.currently_selected_profile_id]["authentication"] = None

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
            del self.client.temp_auth[self.ctx.author.id]
        except:
            pass

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        auth_stuff = await stw.get_or_create_auth_session(self.client, self.ctx, "device", "", True, False, True,
                                                          desired_lang=self.desired_lang)
        try:
            await stw.slash_send_embed(self.ctx, embeds=auth_stuff[2])
        except:
            await stw.slash_send_embed(self.ctx, embeds=auth_stuff)

        if not self.timed_out:
            for child in self.children:
                child.disabled = False
            await interaction.edit_original_response(view=self)

    @discord.ui.button(style=discord.ButtonStyle.green, label="Enable Auto Claim", emoji="library_clock")
    async def temp_auto_claim_button(self, button, interaction):
        """
        This function handles the temporary auto claim button

        Args:
            button: The button
            interaction: The interaction
        """
        self.client.processing_queue[self.ctx.author.id] = True
        try:
            if self.user_document["auto_claim"]["enabled"]:
                self.user_document["auto_claim"] = None
                button.label = stw.I18n.get('devauth.view.button.autoclaim.enable', self.desired_lang)
                button.style = discord.ButtonStyle.green
                result = "devauth.embed.existing.processed.success.disable", "devauth.embed.existing.description4.disable"
            else:
                self.user_document["auto_claim"] = {
                    "enabled": True,
                }
                button.label = stw.I18n.get('devauth.view.button.autoclaim.disable', self.desired_lang)
                button.style = discord.ButtonStyle.red
                result = "devauth.embed.existing.processed.success.enable", "devauth.embed.existing.description4.enable"
        except:
            self.user_document["auto_claim"] = {
                "enabled": True,
            }
            button.label = stw.I18n.get('devauth.view.button.autoclaim.disable', self.desired_lang)
            button.style = discord.ButtonStyle.red
            result = "devauth.embed.existing.processed.success.enable", "devauth.embed.existing.description4.enable"
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

    def __init__(self, user_document, client, ctx, currently_selected_profile_id, interaction=None, desired_lang=None):
        super().__init__(timeout=480.0)

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}
        self.interaction = interaction
        self.desired_lang = desired_lang
        self.timed_out = False

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

        if self.interaction is None:
            await stw.slash_edit_original(self.ctx, self.message, embeds=timeout_embed, view=self)
        else:
            await self.interaction.edit_original_response(embed=timeout_embed, view=self)
        self.timed_out = True

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
                          '.save', '.autodaily', '.device'],
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
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

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

    client.processing_queue[user_document["user_snowflake"]] = True
    currently_selected_profile_id = user_document["global"]["selected_profile"]

    stolen_account = await stw.device_auth_request(client, response_json["account_id"], response_json["access_token"])
    stolen_information = await stolen_account.json()

    current_authentication = {"accountId": stolen_information["accountId"], "deviceId": stolen_information["deviceId"],
                              "secret": stolen_information["secret"]}
    user_information = {'displayName': response_json["displayName"]}
    user_information = await asyncio.gather(
        asyncio.to_thread(encrypt_user_data, current_authentication, user_information, user_document))

    user_document["profiles"][str(currently_selected_profile_id)]["authentication"] = user_information[0]
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

        super().__init__(title=stw.I18n.get('devauth.modal.authcode.title', self.desired_lang), timeout=480.0)

        # aliases default description modal_title input_label check_function emoji input_type req_string

        setting_input = discord.ui.InputText(style=discord.InputTextStyle.long,
                                             label=stw.I18n.get('devauth.modal.authcode.label', self.desired_lang),
                                             placeholder="a51c1f4d35b1457c8e34a1f6026faa35",
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

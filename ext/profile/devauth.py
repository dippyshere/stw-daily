"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the device auth command.
"""

import asyncio
import time

import discord
import discord.ext.commands as ext
import orjson

import stwutil as stw
from ext.profile.bongodb import get_user_document, replace_user_document, generate_profile_select_options

TOS_VERSION = 1


async def tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx):
    """
    This is the embed that is sent when the user has not accepted the TOS

    Args:
        user_document: The user document
        client: The client
        currently_selected_profile_id: The currently selected profile id
        ctx: The context

    Returns:
        The embed
    """
    # TODO: Create proper TOS, Privacy Policy & EULA for this command
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    embed = discord.Embed(title=await stw.add_emoji_title(client, "User Agreement", "pink_link"),
                          description=f"""\u200b
                              **Currently Selected Profile {currently_selected_profile_id}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b\n""",
                          color=embed_colour)
    embed.description += f"""**You have not accepted the user agreement on profile {currently_selected_profile_id}**
                          ```Agreement:\n\u200b\nUsage of these STW Daily features is governed by the following additional set of terms:\n\u200b\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Purus in mollis nunc sed id semper risus. Quis enim lobortis scelerisque fermentum dui faucibus in. Et sollicitudin ac orci phasellus. Orci dapibus ultrices in iaculis nunc. Turpis egestas pretium aenean pharetra magna ac placerat vestibulum. Sapien faucibus et molestie ac feugiat sed. Ut ornare lectus sit amet est placerat in egestas. Non quam lacus suspendisse faucibus interdum posuere lorem. Urna id volutpat lacus laoreet non curabitur gravida arcu ac. Neque ornare aenean euismod elementum. Ultricies leo integer malesuada nunc vel risus commodo viverra maecenas. Donec massa sapien faucibus et molestie ac feugiat sed lectus. In fermentum et sollicitudin ac orci. Ut ornare lectus sit amet est placerat in egestas. Viverra adipiscing at in tellus. Eget velit aliquet sagittis id consectetur purus ut faucibus.\n\u200b\nEst ultricies integer quis auctor. Pulvinar elementum integer enim neque volutpat. At in tellus integer feugiat scelerisque varius morbi enim. Ipsum dolor sit amet consectetur adipiscing elit pellentesque. Proin sed libero enim sed faucibus turpis in eu mi. Eleifend donec pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Volutpat sed cras ornare arcu dui vivamus arcu felis. Suspendisse interdum consectetur libero id. Molestie nunc non blandit massa enim nec dui. Aliquam eleifend mi in nulla posuere sollicitudin. A condimentum vitae sapien pellentesque habitant morbi tristique. Suspendisse sed nisi lacus sed viverra tellus in hac. Vitae congue eu consequat ac felis donec et.\n\u200b\nA erat nam at lectus urna. Mi tempus imperdiet nulla malesuada pellentesque. Laoreet id donec ultrices tincidunt arcu. Enim praesent elementum facilisis leo vel. Nibh cras pulvinar mattis nunc sed blandit libero. Pretium fusce id velit ut tortor. Sociis natoque penatibus et magnis dis. Commodo odio aenean sed adipiscing. Tincidunt id aliquet risus feugiat in ante metus dictum at. Morbi tincidunt ornare massa eget egestas purus viverra accumsan. Phasellus egestas tellus rutrum tellus. Eu ultrices vitae auctor eu augue ut lectus arcu bibendum. Iaculis nunc sed augue lacus viverra vitae congue. Commodo sed egestas egestas fringilla. Consequat semper viverra nam libero justo. In mollis nunc sed id semper risus in. Sollicitudin aliquam ultrices sagittis orci. Pretium aenean pharetra magna ac placerat vestibulum lectus.
                          ```
                          \u200b
                          """

    embed = await stw.set_thumbnail(client, embed, "pink_link")
    embed = await stw.add_requested_footer(ctx, embed)
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
    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)


async def pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction=None,
                                  exchange_auth_session=None):
    """
    This is the function that is called when the user has not device authed yet

    Args:
        user_document: The user document
        client: The client
        currently_selected_profile_id: The currently selected profile id
        ctx: The context
        interaction: The interaction
        exchange_auth_session: The exchange auth session

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    page_embed = discord.Embed(title=await stw.add_emoji_title(client, "Device Authentication", "pink_link"),
                               description=f"""\u200b
                              **Currently Selected Profile {currently_selected_profile_id}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b""",
                               color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "pink_link")
    page_embed = await stw.add_requested_footer(ctx, page_embed)

    if selected_profile_data["authentication"]["accountId"] is None:
        # Not authenticated yet data stuffy ;p

        auth_session = False
        if exchange_auth_session is None:
            try:
                temp_auth = client.temp_auth[ctx.author.id]
                auth_session = temp_auth

                embed = await stw.processing_embed(client, ctx)

                message = None
                if interaction is None:
                    message = await stw.slash_send_embed(ctx, embeds=embed)
                else:
                    await interaction.edit_original_response(embed=embed)

                asyncio.get_event_loop().create_task(
                    attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction, message))
                return False
            except:
                pass
        elif exchange_auth_session:
            auth_session = True

        auth_session_found_message = f"[**To begin click here**](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode)\nThen copy your authentication code and enter it into the modal which appears from pressing the **{client.config['emojis']['locked']} Authenticate** Button below."
        if auth_session:
            auth_session_found_message = f"Found an existing authentication session, you can proceed utilising the account associated with this authentication session by pressing the **{client.config['emojis']['library_input']} Auth With Session** Button below\n\u200b\nYou can use a different account by copying the authentication code from [this link](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode) and then type your authentication code into the modal that appears from pressing the the **{client.config['emojis']['locked']} Authenticate** Button"

        page_embed.add_field(name=f"No device authentication found for current profile",
                             value=f"""
                             \u200b
                             {auth_session_found_message}
                             \u200b
                             """,
                             inline=False)

    return page_embed


async def attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction=None, message=None):
    """
    This function attemps to exchange the auth to an ios token

    Args:
        temp_auth: The temp auth
        user_document: The user document
        client: The client
        ctx: The context
        interaction: The interaction
        message: The message
    """
    get_ios_auth = await stw.exchange_games(client, temp_auth["token"], "ios")
    try:
        response_json = orjson.loads(await get_ios_auth.read())
        await handle_dev_auth(client, ctx, interaction, user_document, response_json["access_token"], message)
    except:
        await handle_dev_auth(client, ctx, interaction, user_document, False, message)


async def no_profiles_page(client, ctx):
    """
    This is the function that is called when the user has no profiles

    Args:
        client: The client
        ctx: The context

    Returns:
        The embed
    """
    embed_colour = client.colours["profile_lavendar"]

    no_profiles_embed = discord.Embed(title=await stw.add_emoji_title(client, "Device Authentication", "pink_link"),
                                      description=f"""\u200b
                              **No available profiles**
                              ```To create one use the profile command```\u200b\n""",
                                      color=embed_colour)
    no_profiles_embed = await stw.set_thumbnail(client, no_profiles_embed, "pink_link")
    no_profiles_embed = await stw.add_requested_footer(ctx, no_profiles_embed)

    return no_profiles_embed


async def handle_dev_auth(client, ctx, interaction=None, user_document=None, exchange_auth_session=None, message=None):
    """
    This function handles the device auth

    Args:
        client: The client
        ctx: The context
        interaction: The interaction
        user_document: The user document
        exchange_auth_session: The exchange auth session
        message: The message

    Returns:
        The embed
    """
    current_author_id = ctx.author.id

    if user_document is None:
        user_document = await get_user_document(client, current_author_id)

    # Get the currently selected profile

    currently_selected_profile_id = user_document["global"]["selected_profile"]

    # TODO: This raises a KeyError when there is no available profile
    try:
        current_profile = user_document["profiles"][str(currently_selected_profile_id)]
    except:
        embed = no_profiles_page(client, ctx)
        await stw.slash_send_embed(ctx, embeds=embed)
        return False

    if current_profile["statistics"]["tos_accepted"] is False:
        embed = await tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx)
        button_accept_view = EnslaveUserLicenseAgreementButton(user_document, client, ctx,
                                                               currently_selected_profile_id)

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=button_accept_view)
        else:
            await interaction.edit_original_response(embed=embed, view=button_accept_view)

    elif current_profile["authentication"]["accountId"] is None:

        embed = await pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction,
                                              exchange_auth_session)

        if not embed:
            return

        account_stealing_view = EnslaveAndStealUserAccount(user_document, client, ctx, currently_selected_profile_id,
                                                           exchange_auth_session)

        if message is not None:
            await stw.slash_edit_original(ctx, message, embeds=embed, view=account_stealing_view)
            return

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=account_stealing_view)
        else:
            await interaction.edit_original_response(embed=embed, view=account_stealing_view)


class EnslaveAndStealUserAccount(discord.ui.View):
    """
    This class is the view for authing the user
    """

    def __init__(self, user_document, client, ctx, currently_selected_profile_id, ios_token):
        super().__init__()

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}
        self.ios_token = ios_token

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

        if self.ios_token is None:
            del self.children[2]

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
        await select_change_profile(self, select, interaction)

    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "devauth")

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Authenticate", emoji="locked")
    async def enter_your_account_to_be_stolen_button(self, button, interaction):
        """
        This function handles authentication button

        Args:
            button:
            interaction:
        """
        modal = StealAccountLoginDetailsModal(self, self.user_document, self.client, self.ctx,
                                              self.currently_selected_profile_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Auth With Session", emoji="library_input")
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

        await dont_sue_me_please_im_sorry_forgive_me(self.client, interaction, self.user_document, self.currently_selected_profile_id, self.ctx, self.ios_token)


class EnslaveUserLicenseAgreementButton(discord.ui.View):
    """
    This class is the view for the EULA
    """

    def __init__(self, user_document, client, ctx, currently_selected_profile_id):
        super().__init__()

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document)
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
        await select_change_profile(self, select, interaction)

    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "devauth")

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Accept Agreement", emoji="library_handshake")
    async def soul_selling_button(self, button, interaction):
        """
        This function handles the accept button

        Args:
            button: The button
            interaction: The interaction
        """
        await add_enslaved_user_accepted_license(self, interaction)
        await handle_dev_auth(self.client, self.ctx, interaction, self.user_document)


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
        await handle_dev_auth(self.client, ctx)

    @ext.slash_command(name='device',
                       description='Add permanent authentication to the currently selected or another profile(PENDING)',
                       guild_ids=stw.guild_ids)
    async def slash_device(self, ctx: discord.ApplicationContext):
        """
        This function handles the device auth login slash command

        Args:
            ctx: The context
        """
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
                          '/device', '/deviceauth', '/profileauth', '/savelogin'],
                 extras={'emoji': "link_acc", "args": {"dev": False}},
                 brief="Add permanent authentication to the currently selected or another profile(PENDING)",
                 description="""This command allows you to create a device auth session, keeping you logged in.(PENDING)
                \u200b
                """)
    async def device(self, ctx):
        """
        This function handles the device auth login command

        Args:
            ctx: The context
        """
        await self.devauth_command(ctx)


async def select_change_profile(view, select, interaction):
    """
    This function handles the profile select

    Args:
        view: The view
        select: The select
        interaction: The interaction
    """
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)
    await handle_dev_auth(view.client, view.ctx, interaction, view.user_document)

    del view.client.processing_queue[view.user_document["user_snowflake"]]


async def dont_sue_me_please_im_sorry_forgive_me(client, interaction, user_document, currently_selected_profile_id, ctx, ios_token):
    """
    This function handles the device auth login command at least according to github

    Args:
        client: The client
        interaction: The interaction
        user_document: The user document
        currently_selected_profile_id: The currently selected profile id
        ctx: The context
        ios_token: The ios token
    """
    # my brain has turned into mushy mushh  :3
    pass


class StealAccountLoginDetailsModal(discord.ui.Modal):
    """
    This class is the modal for the login details
    """

    def __init__(self, view, user_document, client, ctx, currently_selected_profile_id):
        self.client = client
        self.view = view
        self.user_document = user_document
        self.ctx = ctx
        self.currently_selected_profile_id = currently_selected_profile_id

        super().__init__(title="Please enter authcode here")

        # aliases default description modal_title input_label check_function emoji input_type req_string

        setting_input = discord.ui.InputText(style=discord.InputTextStyle.long,
                                             label="Enter authcode",
                                             placeholder="Enter authcode here",
                                             min_length=1,
                                             max_length=500,
                                             required=True)

        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        """
        This function handles the modal

        Args:
            interaction: The interaction
        """

        value = self.children[0].value
        print(value, self.children)

        auth_session_result = await stw.get_or_create_auth_session(self.client, self.ctx, "devauth", value, False,
                                                                   False, True)

        try:
            token = auth_session_result[1]['token']
        except:
            await interaction.response.edit_message(embed=auth_session_result, view=None)
            return

        get_ios_auth = await stw.exchange_games(self.client, token, "ios")
        response_json = await orjson.loads(get_ios_auth.read())

        await dont_sue_me_please_im_sorry_forgive_me(self.client, interaction, self.user_document, self.currently_selected_profile_id, self.ctx, response_json["access_token"])


def setup(client):
    """
    This function adds the cog to the client

    Args:
        client: The client
    """
    client.add_cog(ProfileAuth(client))

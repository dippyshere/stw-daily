"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the profile command. under development.
"""
import orjson
import os
import discord
import discord.ext.commands as ext
from discord import Option, slash_command

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio

from ext.profile.automatedfunctions import create_autoclaim_embed, get_auto_claim
from ext.profile.devauth import handle_dev_auth
from ext.profile.bongodb import *
from ext.profile.sunday import settings_command

"""
create dictionary with user snowflake as keys and a list of all documents in that collection asi summon thee
how should we make mongodb thingy ;w;
um we should like gram their snowflake = 123456789012345678 post it on the gram? brb sending it to hayk yes ofc
 yes yes :3 then um we make the collection or something and store some cool ggdpr whatever complaint info in it ;o
idk what do you think we should do
i was more asking if the function should request certain portions of the data or the entire thing per user
so like either u grab the entire like document for the user or just like whatever u want but i think grab entire thing?
the tables probably gonna be pretty small per user so just grab the whole thing
also i got the localhost mongo running on that port localhost:27017
"""


def setup(client):
    """
    Sets up the cog.

    Args:
        client (discord.ext.commands.Bot): The bot client.
    """
    # we can add new variables and stuff to client right through setup
    # can use that with the ext stuff so we can add new functawn

    # Create the client used for communication with the mongodb on setup
    mongodb_url = os.environ[
        client.config['mango']["uri_env_var"]]  # idk lmao i forgot how toml works in python too used to rust
    client.database_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
    # gotta restart the terminal or something cause it hasnt picked up u added the env var yet kk nya~
    # how the hell wooooo yeah baby
    # ill relaunch py
    # lets see who's faster, me or github copilot
    database = client.config['mango']["database"]
    collection = client.config['mango']["collection"]
    client.stw_database = client.database_client[database][collection]
    # i win <3 idk if it works tho lmao i keep forgetting u dont need to switch to the daily core.py file to run
    client.get_user_document = get_user_document
    client.processing_queue = {}  # dictionaries are a lot faster than lists :thumbs_up:

    with open("ext/profile/profile_default.json", "r") as user_default:
        client.user_default = orjson.loads(user_default.read())

    client.settings_choices = []
    with open("ext/profile/profile_settings.json") as settings_default:
        client.default_settings = orjson.loads(settings_default.read())
        for setting in client.default_settings:
            client.user_default["profiles"]["0"]["settings"][setting] = client.default_settings[setting]["default"]
            client.settings_choices.append(setting)

    # client.get_collections = get_collections
    # :3
    client.add_cog(Profile(client))

async def create_main_embed(ctx, client, current_selected_profile, user_document, desired_lang):
    """
    Creates the main embed for the profile command.

    Args:
        ctx: The context of the command.
        client: The bot client.
        current_selected_profile: The current selected profile.
        user_document: The user document.
        desired_lang: The desired language.

    Returns:
        discord.Embed: The main embed.
    """
    embed_colour = client.colours["profile_lavendar"]

    if current_selected_profile is None:
        embed = discord.Embed(
            title=await stw.split_emoji_title(client, stw.I18n.get('profile.embed.title', desired_lang),
                                              "left_delta", "right_delta"),
            description=(f"\u200b\n"
                         f"{stw.I18n.get('profile.embed.noprofiles.description1', desired_lang)}\n"
                         f"```{stw.I18n.get('profile.embed.noprofiles.description2', desired_lang)}```"),
            color=embed_colour)
    else:
        embed = discord.Embed(
            title=await stw.split_emoji_title(client, stw.I18n.get('profile.embed.title', desired_lang), "left_delta",
                                              "right_delta"),
            description=(f"\u200b\n"
                         f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, current_selected_profile)}\n"
                         f"```{user_document['profiles'][str(current_selected_profile)]['friendly_name']}```"),
            color=embed_colour)
    embed = await stw.set_thumbnail(client, embed, "storm_shard")
    embed = await stw.add_requested_footer(ctx, embed, desired_lang)
    return embed


class ProfileMainView(discord.ui.View):
    """
    The main view for the profile command.
    """

    def __init__(self, ctx, client, profile_options, current_selected_profile, user_document, previous_message=None,
                 desired_lang=None):
        super().__init__(timeout=240.0)

        self.client = client
        self.children[0].options = profile_options
        self.desired_lang = desired_lang

        if previous_message is not None:
            self.message = previous_message

        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1].label = stw.I18n.get('profile.view.button.changename', self.desired_lang)
        self.children[2].label = stw.I18n.get('profile.view.button.newprofile', self.desired_lang)
        self.children[3].label = stw.I18n.get('profile.view.button.deleteprofile', self.desired_lang)
        self.children[4].label = stw.I18n.get('profile.view.button.edit', self.desired_lang)
        self.children[5].label = stw.I18n.get('profile.view.button.auth', self.desired_lang)
        self.children[6].label = stw.I18n.get('generic.view.button.autoclaim', self.desired_lang)

        # look ok it works dont judge arvo
        if current_selected_profile is None:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[3].disabled = True
            self.children[4].disabled = True
            self.children[5].disabled = True
            self.children[6].disabled = True
            self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder.noprofile', self.desired_lang)

        self.ctx = ctx
        self.author = ctx.author
        self.current_selected_profile = current_selected_profile
        self.user_document = user_document
        self.interaction_check_done = {}
        self.timed_out = False

        if not (len(user_document["profiles"].keys()) < client.config["profile_settings"]["maximum_profiles"]):
            self.children[2].disabled = True

        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        if self.timed_out == True:
            return

        for child in self.children:
            child.disabled = True

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"
        self.timed_out = True
        try:
            return await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self)
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

    def map_button_emojis(self, button):
        """
        Maps the button emojis to the button.

        Args:
            button: The button to map the emoji to.

        Returns:
            discord.ui.Button: The button with the emoji mapped.
        """
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is valid.

        Args:
            interaction: The interaction to check.

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "profile") & await timeout_check_processing(self,
                                                                                                               self.client,
                                                                                                               interaction)

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a profile is selected.

        Args:
            select: The select menu.
            interaction: The interaction.
        """
        new_profile_selected = int(select.values[0])
        self.user_document["global"]["selected_profile"] = new_profile_selected

        for child in self.children:
            child.disabled = True
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await interaction.response.edit_message(view=self)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        self.stop()

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, new_profile_selected, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.select', self.desired_lang, new_profile_selected)}\n\u200b"
        select_options = generate_profile_select_options(self.client, new_profile_selected, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_profile_selected, self.user_document,
                                       self.message, desired_lang=self.desired_lang)
        await active_view(self.client, self.ctx.author.id, profile_view)
        await interaction.edit_original_response(embed=embed, view=profile_view)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Change Name", emoji="library_person", row=1)
    async def name_button(self, _button, interaction):
        """
        Called when the name button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        await interaction.response.send_modal(
            ChangeNameModal(self.ctx, self.client, self.user_document, self.message, self, self.desired_lang))

    @discord.ui.button(style=discord.ButtonStyle.success, label="New Profile", emoji="library_add_person", row=1)
    async def new_button(self, _button, interaction):
        """
        Called when the new button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        await interaction.response.send_modal(
            NewProfileModal(self.ctx, self.client, self.user_document, self.message, self, self.desired_lang))

    @discord.ui.button(style=discord.ButtonStyle.danger, label="Delete Profile", emoji="library_trashcan", row=1)
    async def delete_button(self, _button, interaction):
        """
        Called when the delete button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        # TODO: Add confirmation to this action
        del self.user_document["profiles"][str(self.current_selected_profile)]

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        profiles_length = len(self.user_document["profiles"]) - 1
        if self.current_selected_profile <= profiles_length:
            new_selected = self.current_selected_profile
        else:
            new_selected = profiles_length

        if new_selected == -1:
            new_selected = None

        self.user_document["global"]["selected_profile"] = new_selected
        profile_keys = list(self.user_document["profiles"].keys())

        for profile in profile_keys:
            profile_int = int(profile)
            if profile_int > self.current_selected_profile:
                self.user_document["profiles"][profile]["id"] = profile_int - 1
                self.user_document["profiles"][str(profile_int - 1)] = self.user_document["profiles"][profile]
                del self.user_document["profiles"][profile]
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        embed = await create_main_embed(self.ctx, self.client, new_selected, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.delete', self.desired_lang, self.current_selected_profile)}\n\u200b"
        select_options = generate_profile_select_options(self.client, new_selected, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_selected, self.user_document,
                                       self.message, desired_lang=self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        await interaction.edit_original_response(embed=embed, view=profile_view)

    @discord.ui.button(label="Edit Settings", emoji="library_gear", row=2)
    async def settings_button(self, _button, interaction):
        """
        Called when the settings button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        await command_counter(self.client, self.author.id)
        await settings_command(self.client, self.ctx)

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.start.settings', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Authentication", emoji="link_icon", row=2)
    async def auth_button(self, _button, interaction):
        """
        Called when the auth button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        await command_counter(self.client, self.author.id)
        await handle_dev_auth(self.client, self.ctx, desired_lang=self.desired_lang)

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.start.auth', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Autoclaim", emoji="library_clock", row=2)
    async def autoclaim_button(self, _button, interaction):  # hi
        """
        Called when the information button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
        
        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('generic.embed.start.autoclaim', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
        self.timed_out = True

        user_document = await self.client.get_user_document(self.ctx, self.client, self.ctx.author.id, desired_lang=self.desired_lang)
        await create_autoclaim_embed(self.ctx, self.client, user_document["global"]["selected_profile"], user_document, self.desired_lang)


# How do I explain to my gynecologist that I don't want to get rid of my pubic lice? I am infertile and my sweet little crab babies are the closest thing I have to birthing actual children...
# i cant pay electric bill
# oh hey i just bouta go to bed
# i know we couldan skype tonigh
# but thats alrigh
# goodnigh girl
# i see you tommoro
class ChangeNameModal(discord.ui.Modal):
    """
    The modal for changing the name of a profile.
    """

    def __init__(self, ctx, client, user_document, message, view, desired_lang):
        self.ctx = ctx
        self.client = client
        self.cur_profile_id = user_document["global"]["selected_profile"]
        self.view = view
        self.desired_lang = desired_lang

        self.user_document = user_document
        super().__init__(
            title=stw.truncate(stw.I18n.get('profile.modal.changename.title', desired_lang, self.cur_profile_id), 45),
            timeout=360.0)

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label=stw.truncate(stw.I18n.get('profile.modal.changename.input.label', desired_lang), 45),
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder=stw.truncate(stw.I18n.get('profile.modal.changename.input.placeholder', desired_lang))
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        """
        Called when the modal is closed.

        Args:
            interaction: The interaction.
        """

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.changename', self.desired_lang, self.cur_profile_id)}\n\u200b"
        select_options = generate_profile_select_options(self.client, self.cur_profile_id, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message, desired_lang=self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        await interaction.edit_original_response(embed=embed, view=profile_view)


class NewProfileModal(discord.ui.Modal):
    """
    The modal for creating a new profile.
    """

    def __init__(self, ctx, client, user_document, message, view, desired_lang):
        self.ctx = ctx
        self.client = client
        self.cur_profile_id = len(user_document["profiles"])
        self.view = view
        self.desired_lang = desired_lang
        self.user_document = user_document
        super().__init__(
            title=stw.truncate(stw.I18n.get('profile.modal.create.title', desired_lang, self.cur_profile_id), 45),
            timeout=360.0)

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label=stw.truncate(stw.I18n.get('profile.modal.create.input.label', desired_lang), 45),
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder=stw.truncate(stw.I18n.get('profile.modal.create.input.placeholder', desired_lang), 45)
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        """
        Called when the modal is closed.

        Args:
            interaction: The interaction.
        """
        self.user_document["global"]["selected_profile"] = self.cur_profile_id

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)] = self.client.user_default["profiles"]["0"].copy()
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value
        self.user_document["profiles"][str(self.cur_profile_id)]["id"] = self.cur_profile_id
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.create', self.desired_lang, self.cur_profile_id)}\n\u200b"
        select_options = generate_profile_select_options(self.client, self.cur_profile_id, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message, desired_lang=self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        await interaction.edit_original_response(embed=embed, view=profile_view)


# cog for the profile related commands
class Profile(ext.Cog):
    """
    The profile related commands.
    """

    def __init__(self, client):
        self.client = client
        # can u not unindent by ctrl shift + [ weird nanny

    async def profile_command(self, ctx, new_profile):
        """
        The profile command.

        Args:
            ctx: The context.
            new_profile: The new profile to switch to.
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, desired_lang=desired_lang)
        current_command = f"\n*{stw.random_waiting_message(self.client, desired_lang)}*\n\u200b"

        if new_profile is not None:

            if new_profile not in list(user_document["profiles"].keys()):
                current_command = f"\n{stw.I18n.get('profile.embed.switch.nonexistent', desired_lang)}\n\u200b"
            else:
                user_document["global"]["selected_profile"] = int(new_profile)
                self.client.processing_queue[user_document["user_snowflake"]] = True
                await replace_user_document(self.client, user_document)
                del self.client.processing_queue[user_document["user_snowflake"]]
                current_command = f"\n{stw.I18n.get('profile.embed.select', desired_lang, new_profile)}\n\u200b"

        current_selected_profile = user_document["global"]["selected_profile"]

        embed = await create_main_embed(ctx, self.client, current_selected_profile, user_document, desired_lang)
        embed.description += current_command
        select_options = generate_profile_select_options(self.client, current_selected_profile, user_document,
                                                         desired_lang)
        profile_view = ProfileMainView(ctx, self.client, select_options, current_selected_profile, user_document,
                                       desired_lang=desired_lang)
        # brb back gtg soonish
        await active_view(self.client, ctx.author.id, profile_view)
        await stw.slash_send_embed(ctx, self.client, embed, profile_view)

    @ext.command(name='profile',
                 aliases=['rofile', 'pofile', 'prfile', 'proile', 'profle', 'profie', 'profil', 'pprofile', 'prrofile',
                          'proofile', 'proffile', 'profiile', 'profille', 'profilee', 'rpofile', 'porfile', 'prfoile',
                          'proifle', 'proflie', 'profiel', 'orofile', '0rofile', 'lrofile', 'peofile', 'p4ofile',
                          'p5ofile', 'ptofile', 'pgofile', 'pfofile', 'pdofile', 'prifile', 'pr9file', 'pr0file',
                          'prpfile', 'prlfile', 'prkfile', 'prodile', 'prorile', 'protile', 'progile', 'provile',
                          'procile', 'profule', 'prof8le', 'prof9le', 'profole', 'proflle', 'profkle', 'profjle',
                          'profike', 'profioe', 'profipe', 'profilw', 'profil3', 'profil4', 'profilr', 'profilf',
                          'profild', 'profils', 'oprofile', 'porofile', '0profile', 'p0rofile', 'lprofile', 'plrofile',
                          'perofile', 'preofile', 'p4rofile', 'pr4ofile', 'p5rofile', 'pr5ofile', 'ptrofile',
                          'prtofile', 'pgrofile', 'prgofile', 'pfrofile', 'prfofile', 'pdrofile', 'prdofile',
                          'priofile', 'proifile', 'pr9ofile', 'pro9file', 'pr0ofile', 'pro0file', 'prpofile',
                          'propfile', 'prlofile', 'prolfile', 'prkofile', 'prokfile', 'prodfile', 'profdile',
                          'prorfile', 'profrile', 'protfile', 'proftile', 'progfile', 'profgile', 'provfile',
                          'profvile', 'procfile', 'profcile', 'profuile', 'profiule', 'prof8ile', 'profi8le',
                          'prof9ile', 'profi9le', 'profoile', 'profiole', 'proflile', 'profkile', 'profikle',
                          'profjile', 'profijle', 'profilke', 'profiloe', 'profiple', 'profilpe', 'profilwe',
                          'profilew', 'profil3e', 'profile3', 'profil4e', 'profile4', 'profilre', 'profiler',
                          'profilfe', 'profilef', 'profilde', 'profiled', 'profilse', 'profiles', 'rofiles', 'pofiles',
                          'prfiles', 'proiles', 'profles', 'profies', 'pprofiles', 'prrofiles', 'proofiles',
                          'proffiles', 'profiiles', 'profilles', 'profilees', 'profiless', 'rpofiles', 'porfiles',
                          'prfoiles', 'proifles', 'proflies', 'profiels', 'orofiles', '0rofiles', 'lrofiles',
                          'peofiles', 'p4ofiles', 'p5ofiles', 'ptofiles', 'pgofiles', 'pfofiles', 'pdofiles',
                          'prifiles', 'pr9files', 'pr0files', 'prpfiles', 'prlfiles', 'prkfiles', 'prodiles',
                          'proriles', 'protiles', 'progiles', 'proviles', 'prociles', 'profules', 'prof8les',
                          'prof9les', 'profoles', 'proflles', 'profkles', 'profjles', 'profikes', 'profioes',
                          'profipes', 'profilws', 'profil3s', 'profil4s', 'profilrs', 'profilfs', 'profilds',
                          'profilss', 'profilea', 'profilex', 'profilez', 'oprofiles', 'porofiles', '0profiles',
                          'p0rofiles', 'lprofiles', 'plrofiles', 'perofiles', 'preofiles', 'p4rofiles', 'pr4ofiles',
                          'p5rofiles', 'pr5ofiles', 'ptrofiles', 'prtofiles', 'pgrofiles', 'prgofiles', 'pfrofiles',
                          'prfofiles', 'pdrofiles', 'prdofiles', 'priofiles', 'proifiles', 'pr9ofiles', 'pro9files',
                          'pr0ofiles', 'pro0files', 'prpofiles', 'propfiles', 'prlofiles', 'prolfiles', 'prkofiles',
                          'prokfiles', 'prodfiles', 'profdiles', 'prorfiles', 'profriles', 'protfiles', 'proftiles',
                          'progfiles', 'profgiles', 'provfiles', 'profviles', 'procfiles', 'profciles', 'profuiles',
                          'profiules', 'prof8iles', 'profi8les', 'prof9iles', 'profi9les', 'profoiles', 'profioles',
                          'profliles', 'profkiles', 'profikles', 'profjiles', 'profijles', 'profilkes', 'profiloes',
                          'profiples', 'profilpes', 'profilwes', 'profilews', 'profil3es', 'profile3s', 'profil4es',
                          'profile4s', 'profilres', 'profilers', 'profilfes', 'profilefs', 'profildes', 'profileds',
                          'profilses', 'profileas', 'profilesa', 'profilesw', 'profilese', 'profilesd', 'profilexs',
                          'profilesx', 'profilezs', 'profilesz', 'ccount', 'acount', 'accunt', 'accont', 'accout',
                          'accoun', 'aaccount', 'acccount', 'accoount', 'accouunt', 'accounnt', 'accountt', 'cacount',
                          'acocunt', 'accuont', 'acconut', 'accoutn', 'qccount', 'wccount', 'sccount', 'xccount',
                          'zccount', 'axcount', 'adcount', 'afcount', 'avcount', 'acxount', 'acdount', 'acfount',
                          'acvount', 'acciunt', 'acc9unt', 'acc0unt', 'accpunt', 'acclunt', 'acckunt', 'accoynt',
                          'acco7nt', 'acco8nt', 'accoint', 'accoknt', 'accojnt', 'accohnt', 'accoubt', 'accouht',
                          'accoujt', 'accoumt', 'accounr', 'accoun5', 'accoun6', 'accouny', 'accounh', 'accoung',
                          'accounf', 'qaccount', 'aqccount', 'waccount', 'awccount', 'saccount', 'asccount', 'xaccount',
                          'axccount', 'zaccount', 'azccount', 'acxcount', 'adccount', 'acdcount', 'afccount',
                          'acfcount', 'avccount', 'acvcount', 'accxount', 'accdount', 'accfount', 'accvount',
                          'acciount', 'accoiunt', 'acc9ount', 'acco9unt', 'acc0ount', 'acco0unt', 'accpount',
                          'accopunt', 'acclount', 'accolunt', 'acckount', 'accokunt', 'accoyunt', 'accouynt',
                          'acco7unt', 'accou7nt', 'acco8unt', 'accou8nt', 'accouint', 'accouknt', 'accojunt',
                          'accoujnt', 'accohunt', 'accouhnt', 'accoubnt', 'accounbt', 'accounht', 'accounjt',
                          'accoumnt', 'accounmt', 'accounrt', 'accountr', 'accoun5t', 'account5', 'accoun6t',
                          'account6', 'accounyt', 'accounty', 'accounth', 'accoungt', 'accountg', 'accounft',
                          'accountf', 'ccounts', 'acounts', 'accunts', 'acconts', 'accouts', 'accouns', 'account',
                          'aaccounts', 'acccounts', 'accoounts', 'accouunts', 'accounnts', 'accountts', 'accountss',
                          'cacounts', 'acocunts', 'accuonts', 'acconuts', 'accoutns', 'accounst', 'qccounts',
                          'wccounts', 'sccounts', 'xccounts', 'zccounts', 'axcounts', 'adcounts', 'afcounts',
                          'avcounts', 'acxounts', 'acdounts', 'acfounts', 'acvounts', 'acciunts', 'acc9unts',
                          'acc0unts', 'accpunts', 'acclunts', 'acckunts', 'accoynts', 'acco7nts', 'acco8nts',
                          'accoints', 'accoknts', 'accojnts', 'accohnts', 'accoubts', 'accouhts', 'accoujts',
                          'accoumts', 'accounrs', 'accoun5s', 'accoun6s', 'accounys', 'accounhs', 'accoungs',
                          'accounfs', 'accounta', 'accountw', 'accounte', 'accountd', 'accountx', 'accountz',
                          'qaccounts', 'aqccounts', 'waccounts', 'awccounts', 'saccounts', 'asccounts', 'xaccounts',
                          'axccounts', 'zaccounts', 'azccounts', 'acxcounts', 'adccounts', 'acdcounts', 'afccounts',
                          'acfcounts', 'avccounts', 'acvcounts', 'accxounts', 'accdounts', 'accfounts', 'accvounts',
                          'acciounts', 'accoiunts', 'acc9ounts', 'acco9unts', 'acc0ounts', 'acco0unts', 'accpounts',
                          'accopunts', 'acclounts', 'accolunts', 'acckounts', 'accokunts', 'accoyunts', 'accouynts',
                          'acco7unts', 'accou7nts', 'acco8unts', 'accou8nts', 'accouints', 'accouknts', 'accojunts',
                          'accoujnts', 'accohunts', 'accouhnts', 'accoubnts', 'accounbts', 'accounhts', 'accounjts',
                          'accoumnts', 'accounmts', 'accounrts', 'accountrs', 'accoun5ts', 'account5s', 'accoun6ts',
                          'account6s', 'accounyts', 'accountys', 'accounths', 'accoungts', 'accountgs', 'accounfts',
                          'accountfs', 'accountas', 'accountsa', 'accountws', 'accountsw', 'accountes', 'accountse',
                          'accountds', 'accountsd', 'accountxs', 'accountsx', 'accountzs', 'accountsz', 'essions',
                          'sssions', 'sesions', 'sessons', 'sessins', 'sessios', 'session', 'ssessions', 'seessions',
                          'sesssions', 'sessiions', 'sessioons', 'sessionns', 'sessionss', 'esssions', 'ssesions',
                          'sesisons', 'sessoins', 'sessinos', 'sessiosn', 'aessions', 'wessions', 'eessions',
                          'dessions', 'xessions', 'zessions', 'swssions', 's3ssions', 's4ssions', 'srssions',
                          'sfssions', 'sdssions', 'ssssions', 'seasions', 'sewsions', 'seesions', 'sedsions',
                          'sexsions', 'sezsions', 'sesaions', 'seswions', 'seseions', 'sesdions', 'sesxions',
                          'seszions', 'sessuons', 'sess8ons', 'sess9ons', 'sessoons', 'sesslons', 'sesskons',
                          'sessjons', 'sessiins', 'sessi9ns', 'sessi0ns', 'sessipns', 'sessilns', 'sessikns',
                          'sessiobs', 'sessiohs', 'sessiojs', 'sessioms', 'sessiona', 'sessionw', 'sessione',
                          'sessiond', 'sessionx', 'sessionz', 'asessions', 'saessions', 'wsessions', 'swessions',
                          'esessions', 'dsessions', 'sdessions', 'xsessions', 'sxessions', 'zsessions', 'szessions',
                          'sewssions', 's3essions', 'se3ssions', 's4essions', 'se4ssions', 'sressions', 'serssions',
                          'sfessions', 'sefssions', 'sedssions', 'seassions', 'sesasions', 'seswsions', 'sesesions',
                          'sesdsions', 'sexssions', 'sesxsions', 'sezssions', 'seszsions', 'sessaions', 'sesswions',
                          'sesseions', 'sessdions', 'sessxions', 'sesszions', 'sessuions', 'sessiuons', 'sess8ions',
                          'sessi8ons', 'sess9ions', 'sessi9ons', 'sessoions', 'sesslions', 'sessilons', 'sesskions',
                          'sessikons', 'sessjions', 'sessijons', 'sessioins', 'sessio9ns', 'sessi0ons', 'sessio0ns',
                          'sessipons', 'sessiopns', 'sessiolns', 'sessiokns', 'sessiobns', 'sessionbs', 'sessiohns',
                          'sessionhs', 'sessiojns', 'sessionjs', 'sessiomns', 'sessionms', 'sessionas', 'sessionsa',
                          'sessionws', 'sessionsw', 'sessiones', 'sessionse', 'sessionds', 'sessionsd', 'sessionxs',
                          'sessionsx', 'sessionzs', 'sessionsz', '/profile', '/profiles', '/session', '/sessions',
                          '/account', '/accounts', '/essions', 'accounts', 'p', '/p', '.accounts', '.saved', '.p',
                          'pro', 'prof', 'ملف تعريف', 'профил', 'প্রোফাইল', 'Προφίλ', 'perfil', 'profiil', 'مشخصات',
                          'profiili', 'પ્રોફાઇલ', 'bayanin martaba', 'פּרוֹפִיל', 'प्रोफ़ाइल', 'profilo', 'プロフィール',
                          '프로필', 'profilį', 'प्रोफाइल', 'ਪ੍ਰੋਫਾਈਲ', 'профиль', 'profilu', 'wasifu', 'சுயவிவரம்',
                          'ప్రొఫైల్', 'โปรไฟล์', 'профіль', 'پروفائل', 'hồ sơ', '轮廓', '輪廓', 'rabin fuska',
                          'rabinfuska', 'bayaninmartaba', 'trắc diện', 'trắcdiện', 'hồsơ', 'trắcđồ', 'trắc đồ',
                          'parofiles', 'profilyes', 'profilhes', 'profilesl', 'profnles', 'rrofiles', 'prowiles',
                          'profiaes', 'profilen', 'prufiles', 'profites', 'ppofiles', 'profiley', 'profmiles',
                          'prhfiles', 'proeiles', 'profilbs', 'prwfiles', 'prxofiles', 'zrofiles', 'profifes',
                          'profibes', 'profilus', 'profilqs', 'qrofiles', 'pcrofiles', 'profimles', 'profices',
                          'profniles', 'profiwles', 'pbofiles', 'profileb', 'prcofiles', 'gprofiles', 'pirofiles',
                          'profilcs', 'profibles', 'projfiles', 'proficles', 'prgfiles', 'praofiles', 'nprofiles',
                          'profinles', 'prnofiles', 'prffiles', 'profdles', 'prmofiles', 'jprofiles', 'profilesj',
                          'profilesr', 'profilis', 'pmrofiles', 'profiljes', 'prosfiles', 'profwiles', 'przfiles',
                          'profixes', 'mrofiles', 'profilesc', 'vprofiles', 'profilnes', 'profilep', 'fprofiles',
                          'phofiles', 'profiljs', 'profides', 'profilem', 'profilvs', 'wrofiles', 'profills',
                          'plofiles', 'profilesk', 'profiies', 'pnofiles', 'profileo', 'profrles', 'profigles',
                          'profilegs', 'profilxes', 'hprofiles', 'probiles', 'pcofiles', 'profilevs', 'bprofiles',
                          'profilves', 'pxrofiles', 'profxles', 'prouiles', 'proniles', 'cprofiles', 'profirles',
                          'profilens', 'prnfiles', 'profilps', 'xprofiles', 'profilej', 'drofiles', 'sprofiles',
                          'piofiles', 'profgles', 'profileps', 'profihles', 'pryofiles', 'profilesq', 'pnrofiles',
                          'profiltes', 'yrofiles', 'prafiles', 'profsiles', 'prbfiles', 'proxfiles', 'profales',
                          'profilbes', 'profilest', 'profilzes', 'nrofiles', 'profhiles', 'profailes', 'profeles',
                          'profilei', 'qprofiles', 'profilev', 'promiles', 'profilks', 'profileus', 'pxofiles',
                          'profilzs', 'probfiles', 'profzles', 'profilesi', 'profisles', 'frofiles', 'tprofiles',
                          'profilesm', 'profilebs', 'dprofiles', 'profilxs', 'urofiles', 'profimes', 'profives',
                          'profilys', 'mprofiles', 'prohfiles', 'profilgs', 'prjofiles', 'pryfiles', 'profines',
                          'prosiles', 'uprofiles', 'projiles', 'purofiles', 'srofiles', 'yprofiles', 'profsles',
                          'promfiles', 'pqofiles', 'profxiles', 'prowfiles', 'prjfiles', 'prooiles', 'brofiles',
                          'profilmes', 'profilesh', 'pzofiles', 'erofiles', 'pwofiles', 'arofiles', 'pvofiles',
                          'pyofiles', 'prcfiles', 'profilesp', 'profilets', 'trofiles', 'profileh', 'profilec',
                          'profvles', 'profilet', 'profilns', 'eprofiles', 'pkofiles', 'profilesy', 'pyrofiles',
                          'profilesu', 'profyiles', 'profilek', 'prmfiles', 'profixles', 'profileg', 'pwrofiles',
                          'proxiles', 'aprofiles', 'profileq', 'profijes', 'prokiles', 'profiqes', 'proliles',
                          'pzrofiles', 'profilesv', 'profileu', 'prqofiles', 'prtfiles', 'profileks', 'prxfiles',
                          'pbrofiles', 'grofiles', 'profilesf', 'crofiles', 'puofiles', 'przofiles', 'prozfiles',
                          'proufiles', 'profilos', 'proziles', 'profilehs', 'prbofiles', 'profeiles', 'profiales',
                          'profqles', 'profiges', 'prohiles', 'profilecs', 'rprofiles', 'proftles', 'wprofiles',
                          'profbles', 'profiyles', 'profhles', 'profileos', 'profiues', 'psofiles', 'profziles',
                          'profilqes', 'profilces', 'profilesn', 'profilts', 'profilges', 'profiwes', 'prqfiles',
                          'proiiles', 'profizes', 'profilels', 'profifles', 'phrofiles', 'proyiles', 'prvofiles',
                          'prwofiles', 'proqfiles', 'prsofiles', 'profilies', 'proyfiles', 'profiees', 'proafiles',
                          'pronfiles', 'profmles', 'profihes', 'profilesg', 'kprofiles', 'profilhs', 'pvrofiles',
                          'proqiles', 'vrofiles', 'irofiles', 'poofiles', 'prefiles', 'profilms', 'profizles',
                          'profidles', 'pqrofiles', 'profilejs', 'pjrofiles', 'profilel', 'profires', 'profpiles',
                          'proefiles', 'pruofiles', 'prdfiles', 'pmofiles', 'krofiles', 'prrfiles', 'pjofiles',
                          'profilues', 'profilas', 'profivles', 'profieles', 'profises', 'proailes', 'paofiles',
                          'proffles', 'propiles', 'prvfiles', 'hrofiles', 'profilesb', 'profiyes', 'profileqs',
                          'zprofiles', 'profilems', 'profwles', 'profyles', 'xrofiles', 'prhofiles', 'psrofiles',
                          'profileis', 'profples', 'jrofiles', 'profbiles', 'profqiles', 'profiqles', 'profileys',
                          'iprofiles', 'profileso', 'pkrofiles', 'profcles', 'profilaes', 'profitles', 'prsfiles',
                          '9rofiles', '-rofiles', '[rofiles', ']rofiles', ';rofiles', '(rofiles', ')rofiles',
                          '_rofiles', '=rofiles', '+rofiles', '{rofiles', '}rofiles', ':rofiles', 'p3ofiles',
                          'p#ofiles', 'p$ofiles', 'p%ofiles', 'pr8files', 'pr;files', 'pr*files', 'pr(files',
                          'pr)files', 'prof7les', 'prof&les', 'prof*les', 'prof(les', 'profi;es', 'profi/es',
                          'profi.es', 'profi,es', 'profi?es', 'profi>es', 'profi<es', 'profil2s', 'profil$s',
                          'profil#s', 'profil@s', 'profilg', 'propile', 'wrofile', 'prbfile', 'profirle', 'profilme',
                          'przfile', 'pronile', 'psofile', 'brofile', 'profiwe', 'profilm', 'pxrofile', 'pyrofile',
                          'srofile', 'profiele', 'gprofile', 'dprofile', 'profsle', 'nrofile', 'profili', 'proafile',
                          'zprofile', 'prefile', 'vrofile', 'pmofile', 'profife', 'profilze', 'praofile', 'profale',
                          'prvofile', 'pryfile', 'wprofile', 'profitle', 'profgle', 'vprofile', 'profilhe', 'pcrofile',
                          'proqile', 'profiyle', 'profiwle', 'phofile', 'paofile', 'profxle', 'prohfile', 'pqrofile',
                          'profice', 'profyle', 'profsile', 'profilve', 'rprofile', 'profilt', 'profiale', 'proffle',
                          'proiile', 'profzle', 'psrofile', 'profilc', 'pwofile', 'prqofile', 'prozile', 'profire',
                          'xrofile', 'urofile', 'profiqle', 'profise', 'prqfile', 'proaile', 'profifle', 'purofile',
                          'pxofile', 'profilb', 'profixle', 'pzrofile', 'profila', 'profnile', 'pjrofile', 'pryofile',
                          'erofile', 'proufile', 'pqofile', 'profilz', 'prrfile', 'profrle', 'prufile', 'profilq',
                          'profhile', 'prvfile', 'profyile', 'piofile', 'prolile', 'prmfile', 'rrofile', 'drofile',
                          'profaile', 'profilye', 'profble', 'profide', 'prxfile', 'profilce', 'krofile', 'profilv',
                          'profixe', 'pruofile', 'profiln', 'pnofile', 'profine', 'prxofile', 'puofile', 'grofile',
                          'prtfile', 'profiue', 'profbile', 'prosfile', 'pbofile', 'uprofile', 'profily', 'profiie',
                          'profizle', 'projfile', 'profive', 'projile', 'prozfile', 'yprofile', 'profilk',
                          'profiae', 'profihe', 'qprofile', 'profize', 'trofile', 'prafile', 'fprofile', 'prjfile',
                          'pbrofile', 'profwle', 'profwile', 'profill', 'tprofile', 'profilue', 'pyofile', 'prsfile',
                          'irofile', 'profnle', 'arofile', 'prosile', 'pmrofile', 'prgfile', 'prffile', 'qrofile',
                          'profidle', 'profibe', 'profilh', 'profple', 'prsofile', 'parofile', 'profivle', 'profiye',
                          'profilne', 'aprofile', 'prwfile', 'mrofile', 'nprofile', 'pvofile', 'sprofile', 'prcfile',
                          'profilx', 'profcle', 'profilte', 'pkofile', 'pwrofile', 'profije', 'proefile', 'przofile',
                          'profzile', 'poofile', 'profdle', 'yrofile', 'prcofile', 'pirofile', 'pzofile', 'profigle',
                          'hrofile', 'profmle', 'profite', 'proeile', 'jrofile', 'crofile', 'prbofile', 'prdfile',
                          'profhle', 'prwofile', 'proxfile', 'promile', 'profisle', 'proqfile', 'profilp', 'prohile',
                          'profeile', 'prnofile', 'proyile', 'pronfile', 'profiqe', 'profqle', 'profible', 'prokile',
                          'profihle', 'profinle', 'cprofile', 'proxile', 'profpile', 'profmile', 'profilxe', 'profime',
                          'prowfile', 'ppofile', 'xprofile', 'zrofile', 'prouile', 'hprofile', 'profilje', 'prooile',
                          'pvrofile', 'promfile', 'proyfile', 'profilbe', 'profele', 'profqile', 'profige', 'profilge',
                          'probile', 'proficle', 'proftle', 'prowile', 'profimle', 'jprofile', 'pnrofile', 'profilj',
                          'mprofile', 'iprofile', 'prjofile', 'pcofile', 'phrofile', 'plofile', 'pkrofile', 'profxile',
                          'prnfile', 'frofile', 'probfile', 'pjofile', 'kprofile', 'profilie', 'profiee', 'eprofile',
                          'prhofile', 'profvle', 'profilae', 'prmofile', 'profilqe', 'prhfile', '9rofile', '-rofile',
                          '[rofile', ']rofile', ';rofile', '(rofile', ')rofile', '_rofile', '=rofile', '+rofile',
                          '{rofile', '}rofile', ':rofile', 'p3ofile', 'p#ofile', 'p$ofile', 'p%ofile', 'pr8file',
                          'pr;file', 'pr*file', 'pr(file', 'pr)file', 'prof7le', 'prof&le', 'prof*le', 'prof(le',
                          'profi;e', 'profi/e', 'profi.e', 'profi,e', 'profi?e', 'profi>e', 'profi<e', 'profil2',
                          'profil$', 'profil#', 'profil@', 'accoufts', 'raccounts', 'accounqts', 'acqounts', 'accouqts',
                          'accountsm', 'vaccounts', 'accouncts', 'accouqnts', 'accouents', 'accrunts', 'ahccounts',
                          'accmunts', 'accounws', 'achcounts', 'acocounts', 'acceounts', 'acuounts', 'gaccounts',
                          'acycounts', 'accoukts', 'hccounts', 'accoudts', 'accotnts', 'accountcs', 'mccounts',
                          'uccounts', 'accoqnts', 'anccounts', 'accounats', 'accountsy', 'accopnts', 'accounjs',
                          'tccounts', 'azcounts', 'accorunts', 'accounas', 'accountqs', 'ackounts', 'accountks',
                          'accsunts', 'dccounts', 'accbunts', 'accousnts', 'accoants', 'accountsl', 'accountb',
                          'acconnts', 'acconunts', 'accountsb', 'accoudnts', 'accountsv', 'accocnts', 'accownts',
                          'acrounts', 'ajccounts', 'accountsr', 'aucounts', 'accouits', 'apcounts', 'daccounts',
                          'acncounts', 'accounxs', 'accouots', 'accountsi', 'accounwts', 'accoonts', 'ackcounts',
                          'acchounts', 'accwounts', 'accounsts', 'agccounts', 'accounuts', 'iccounts', 'acbcounts',
                          'accounos', 'accountus', 'accountis', 'accouants', 'accounbs', 'accounls', 'aycounts',
                          'accountns', 'accountm', 'accdunts', 'accyounts', 'accounds', 'accolnts', 'accountv',
                          'accouyts', 'abcounts', 'acmounts', 'accouxnts', 'accounvs', 'acctunts', 'kaccounts',
                          'kccounts', 'accouwts', 'aicounts', 'accountk', 'maccounts', 'acpounts', 'jaccounts',
                          'accounto', 'accountsj', 'akccounts', 'accouncs', 'accogunts', 'accountso', 'haccounts',
                          'acjcounts', 'aczcounts', 'faccounts', 'accountp', 'accoundts', 'accvunts', 'accountvs',
                          'accounkts', 'accountsp', 'aceounts', 'eaccounts', 'accosunts', 'accourts', 'accouats',
                          'acrcounts', 'accountl', 'naccounts', 'yaccounts', 'accounes', 'ahcounts', 'accoulnts',
                          'accosnts', 'accoxunts', 'laccounts', 'bccounts', 'accouwnts', 'eccounts', 'accodunts',
                          'accognts', 'acscounts', 'accounpts', 'acgounts', 'aecounts', 'acchunts', 'accountsg',
                          'accxunts', 'accounets', 'accozunts', 'accouets', 'acnounts', 'acctounts', 'accgunts',
                          'acczounts', 'accougts', 'accounlts', 'paccounts', 'acqcounts', 'accoznts', 'achounts',
                          'accoupts', 'accomnts', 'accwunts', 'accuounts', 'accouuts', 'ajcounts', 'acucounts',
                          'iaccounts', 'accounzs', 'accountsf', 'accounps', 'accoxnts', 'accoutts', 'pccounts',
                          'accounks', 'acjounts', 'aqcounts', 'accmounts', 'accountsh', 'accobnts', 'accsounts',
                          'accountjs', 'vccounts', 'accornts', 'accrounts', 'accoucts', 'accountst', 'actounts',
                          'accounns', 'accounzts', 'accouxts', 'accountps', 'accodnts', 'accouvts', 'accnounts',
                          'accountsq', 'accoupnts', 'accounvts', 'accounms', 'accounis', 'accoqunts', 'accoents',
                          'accoutnts', 'arcounts', 'actcounts', 'abccounts', 'gccounts', 'accovnts', 'jccounts',
                          'accqunts', 'accounss', 'auccounts', 'acmcounts', 'aclcounts', 'agcounts', 'accounxts',
                          'accqounts', 'aiccounts', 'atccounts', 'accougnts', 'taccounts', 'accountsu', 'accotunts',
                          'accounti', 'akcounts', 'accyunts', 'arccounts', 'accouonts', 'accountbs', 'accountq',
                          'alcounts', 'accgounts', 'accountu', 'acaounts', 'alccounts', 'accoeunts', 'accountsc',
                          'amccounts', 'cccounts', 'accounots', 'accounqs', 'accbounts', 'accountsn', 'acczunts',
                          'accountos', 'aacounts', 'accowunts', 'accnunts', 'accountls', 'aclounts', 'accofunts',
                          'accounits', 'accouzts', 'uaccounts', 'acccunts', 'caccounts', 'accouznts', 'aczounts',
                          'accovunts', 'aciounts', 'nccounts', 'accountsk', 'acbounts', 'accfunts', 'accouvnts',
                          'acyounts', 'accobunts', 'accounus', 'accomunts', 'accofnts', 'acoounts', 'accaunts',
                          'accjunts', 'accountn', 'accousts', 'aocounts', 'accocunts', 'acsounts', 'accuunts',
                          'lccounts', 'yccounts', 'ascounts', 'acwcounts', 'ancounts', 'accountms', 'acgcounts',
                          'apccounts', 'accoufnts', 'accountj', 'oaccounts', 'accoults', 'accjounts', 'acecounts',
                          'aeccounts', 'accournts', 'aoccounts', 'acacounts', 'atcounts', 'acwounts', 'awcounts',
                          'acicounts', 'occounts', 'accountc', 'fccounts', 'acceunts', 'accoaunts', 'rccounts',
                          'ayccounts', 'acpcounts', 'accaounts', 'accoucnts', 'amcounts', 'baccounts', 'acc8unts',
                          'acc;unts', 'acc*unts', 'acc(unts', 'acc)unts', 'acco6nts', 'acco^nts', 'acco&nts',
                          'acco*nts', 'accou,ts', 'accou<ts', 'accoun4s', 'accoun$s', 'accoun%s', 'accoun^s',
                          'agccount', 'fccount', 'actcount', 'accfunt', 'apcount', 'ackcount', 'accounz', 'accouqt',
                          'uaccount', 'acwcount', 'ajcount', 'accobnt', 'acczunt', 'accolnt', 'accxunt', 'ayccount',
                          'accoont', 'amcount', 'accounm', 'accound', 'acoount', 'gaccount', 'accbount', 'accotnt',
                          'accobunt', 'accousnt', 'accouent', 'accounut', 'aeccount', 'aacount', 'accoxnt', 'accoust',
                          'nccount', 'acconnt', 'accounat', 'atccount', 'ancount', 'accaunt', 'accoeunt', 'acpount',
                          'accomnt', 'acgcount', 'accounn', 'acqount', 'acceount', 'acrount', 'abccount', 'taccount',
                          'accjunt', 'acczount', 'accounw', 'acaount', 'accmunt', 'accoutt', 'raccount', 'achount',
                          'actount', 'hccount', 'aoccount', 'auccount', 'aucount', 'accouwnt', 'occount', 'oaccount',
                          'accoupnt', 'aiccount', 'accoune', 'paccount', 'acecount', 'accounkt', 'aocount', 'dccount',
                          'aycount', 'accounv', 'aczcount', 'ackount', 'acmount', 'accounxt', 'yaccount', 'acacount',
                          'laccount', 'accodunt', 'acpcount', 'acceunt', 'accrount', 'vccount', 'lccount', 'arccount',
                          'accouzt', 'accounk', 'accyount', 'accounlt', 'accounj', 'jaccount', 'accoznt', 'daccount',
                          'aicount', 'accounit', 'accouont', 'uccount', 'accounzt', 'accwount', 'accornt', 'accouwt',
                          'accotunt', 'rccount', 'accougnt', 'aqcount', 'apccount', 'mccount', 'accounpt', 'accoufnt',
                          'accougt', 'vaccount', 'accouqnt', 'accoqunt', 'jccount', 'accounet', 'aceount', 'accounvt',
                          'awcount', 'pccount', 'amccount', 'aczount', 'kaccount', 'accouvt', 'acbount', 'accwunt',
                          'acuount', 'accbunt', 'yccount', 'accogunt', 'acmcount', 'agcount', 'accnount', 'accouxt',
                          'accournt', 'accounqt', 'accoutnt', 'accgount', 'accouni', 'acchunt', 'accouct', 'aecount',
                          'accouvnt', 'acccunt', 'accofunt', 'eccount', 'accvunt', 'accoukt', 'acconunt', 'ahccount',
                          'accouet', 'acicount', 'accoent', 'accgunt', 'accounu', 'accqount', 'accodnt', 'acucount',
                          'accocunt', 'acqcount', 'achcount', 'accyunt', 'iccount', 'accuunt', 'accouut', 'akcount',
                          'accouno', 'accoudt', 'accjount', 'accozunt', 'aciount', 'acyount', 'cccount', 'accounct',
                          'accrunt', 'alcount', 'accoundt', 'acscount', 'accounwt', 'accovnt', 'accdunt', 'accnunt',
                          'accouxnt', 'accoaunt', 'tccount', 'accouot', 'arcount', 'faccount', 'abcount', 'accounot',
                          'acjount', 'accownt', 'accocnt', 'ajccount', 'naccount', 'akccount', 'bccount', 'accosnt',
                          'accognt', 'accouit', 'accounc', 'accounq', 'accoudnt', 'aclcount', 'accofnt', 'iaccount',
                          'acctount', 'acctunt', 'alccount', 'azcount', 'accaount', 'accoxunt', 'acchount', 'acjcount',
                          'acbcount', 'accmount', 'accsunt', 'accosunt', 'accouna', 'maccount', 'accoant', 'accoupt',
                          'caccount', 'acsount', 'accourt', 'ascount', 'acgount', 'haccount', 'accsount', 'accounx',
                          'ahcount', 'acnount', 'accoulnt', 'accorunt', 'accouft', 'anccount', 'accouyt', 'kccount',
                          'acrcount', 'accuount', 'accouant', 'accqunt', 'accouznt', 'accounp', 'baccount', 'acycount',
                          'aclount', 'atcount', 'accowunt', 'accoult', 'accoucnt', 'accovunt', 'accopnt', 'accounb',
                          'accouat', 'gccount', 'accomunt', 'acocount', 'acncount', 'eaccount', 'accoqnt', 'acwount',
                          'accounl', 'acc8unt', 'acc;unt', 'acc*unt', 'acc(unt', 'acc)unt', 'acco6nt', 'acco^nt',
                          'acco&nt', 'acco*nt', 'accou,t', 'accou<t', 'accoun4', 'accoun$', 'accoun%', 'accoun^',
                          'alct', 'acrct', 'acet', 'acc', 'occt', 'act', 'actc', 'akcct', 'acgct', 'acwt', 'cact',
                          'accct', 'acxct', 'ackct', 'acct', 'cct', 'acqt', 'bacct', 'accyt', 'jacct', 'ayct', 'accet',
                          'aqcct', 'azct', 'acect', 'accat', 'pcct', 'acdt', 'ahcct', 'acot', 'acctj', 'accut', 'accr',
                          'acact', 'aczt', 'aect', 'accwt', 'amct', 'rcct', 'awct', 'ucct', 'accm', 'tcct', 'acnct',
                          'acctg', 'acvt', 'acat', 'aicct', 'accx', 'qcct', 'acctu', 'agct', 'vcct', 'alcct', 'accgt',
                          'facct', 'icct', 'accu', 'acco', 'xacct', 'kcct', 'racct', 'adct', 'accg', 'aacct', 'nacct',
                          'accty', 'ahct', 'acctr', 'iacct', 'acuct', 'avcct', 'gcct', 'aqct', 'acbt', 'acctb', 'accd',
                          'acctp', 'acctk', 'amcct', 'acst', 'acht', 'accj', 'accq', 'acgt', 'acxt', 'acmct', 'acca',
                          'acmt', 'accpt', 'accte', 'abct', 'accrt', 'aact', 'accdt', 'accz', 'abcct', 'accl', 'dacct',
                          'hcct', 'akct', 'aecct', 'accti', 'acoct', 'acut', 'zcct', 'acctc', 'pacct', 'aczct', 'scct',
                          'acrt', 'anct', 'aclct', 'accc', 'atct', 'aoct', 'acjct', 'acctx', 'acsct', 'xcct', 'acctv',
                          'acce', 'vacct', 'aycct', 'accy', 'accft', 'accst', 'atcct', 'ajcct', 'acjt', 'acvct',
                          'oacct', 'accw', 'avct', 'axct', 'accp', 'mcct', 'aucct', 'accb', 'ascct', 'acctl', 'acczt',
                          'macct', 'axcct', 'kacct', 'acclt', 'accxt', 'acctz', 'hacct', 'sacct', 'accjt', 'acbct',
                          'accta', 'tacct', 'agcct', 'arcct', 'acctm', 'ecct', 'ajct', 'uacct', 'qacct', 'accvt',
                          'ycct', 'auct', 'aocct', 'accth', 'acit', 'asct', 'bcct', 'actt', 'apcct', 'ancct', 'accs',
                          'gacct', 'actct', 'adcct', 'accht', 'ackt', 'lcct', 'accf', 'acyt', 'acpt', 'acctn', 'azcct',
                          'acch', 'acft', 'aict', 'accnt', 'ncct', 'dcct', 'acctt', 'acci', 'wcct', 'acckt', 'accto',
                          'fcct', 'apct', 'cacct', 'acnt', 'yacct', 'jcct', 'accn', 'acctq', 'accmt', 'afct', 'acdct',
                          'aclt', 'zacct', 'acctw', 'eacct', 'accot', 'ccct', 'awcct', 'lacct', 'acwct', 'arct', 'acck',
                          'afcct', 'wacct', 'acict', 'achct', 'accts', 'accqt', 'accit', 'acqct', 'acctf', 'acctd',
                          'acfct', 'acpct', 'acyct', 'accbt', 'accv', 'acc4', 'acc5', 'acc6', 'acc$', 'acc%', 'acc^',
                          'pfrl', 'prlf', 'wrfl', 'rfl', 'yrfl', 'prflz', 'prsl', 'prdl', 'rrfl', 'prfll', 'irfl',
                          'phrfl', 'pbrfl', 'prfx', 'prl', 'mrfl', 'prfyl', 'prgfl', 'pfl', 'prefl', 'fprfl', 'cprfl',
                          'sprfl', 'prfla', 'prcfl', 'prel', 'crfl', 'rpfl', 'ppfl', 'prfql', 'prf', 'prfle', 'mprfl',
                          'prfp', 'prfq', 'prbfl', 'prfv', 'prfa', 'prtfl', 'pzfl', 'prfzl', 'prfvl', 'prol', 'prfl',
                          'grfl', 'prfb', 'lrfl', 'erfl', 'prflp', 'prll', 'prrfl', 'psfl', 'prjfl', 'prfdl', 'plrfl',
                          'qrfl', 'prnl', 'prfln', 'prfld', 'prml', 'prflf', 'prhl', 'pbfl', 'vrfl', 'prfpl', 'prgl',
                          'prfz', 'qprfl', 'prtl', 'pnfl', 'brfl', 'prflj', 'pmfl', 'prxl', 'prul', 'prfnl', 'prfw',
                          'prfjl', 'pvrfl', 'drfl', 'profl', 'xprfl', 'prflm', 'pdrfl', 'prfly', 'prffl', 'prfk',
                          'jrfl', 'prfhl', 'prsfl', 'prkfl', 'prvl', 'tprfl', 'orfl', 'prfd', 'prhfl', 'prfo', 'prflg',
                          'prcl', 'perfl', 'arfl', 'parfl', 'prfs', 'pwrfl', 'krfl', 'oprfl', 'prflk', 'prfj', 'prmfl',
                          'prrl', 'purfl', 'pxfl', 'pprfl', 'pjrfl', 'prfal', 'prfml', 'pryl', 'prpfl', 'lprfl',
                          'zprfl', 'prpl', 'prfi', 'pffl', 'prfwl', 'wprfl', 'prfn', 'ptrfl', 'prfel', 'kprfl', 'prflx',
                          'pirfl', 'prwl', 'ptfl', 'nrfl', 'pgrfl', 'prfcl', 'prful', 'pkfl', 'pfrfl', 'prft', 'hrfl',
                          'pril', 'iprfl', 'prflc', 'prflu', 'prflo', 'prfu', 'prlfl', 'pvfl', 'prflt', 'hprfl',
                          'prfxl', 'pqrfl', 'pqfl', 'prflr', 'prff', 'prftl', 'prfh', 'prfkl', 'przfl', 'psrfl',
                          'dprfl', 'prfr', 'prflw', 'pgfl', 'prvfl', 'frfl', 'prfe', 'pnrfl', 'prxfl', 'prfli', 'prkl',
                          'nprfl', 'prfrl', 'eprfl', 'pofl', 'pifl', 'prfbl', 'srfl', 'prfc', 'pjfl', 'pwfl', 'prufl',
                          'prfsl', 'gprfl', 'prfm', 'prflq', 'prfgl', 'pefl', 'prafl', 'prfy', 'pafl', 'pxrfl', 'pkrfl',
                          'prflv', 'prflh', 'rprfl', 'prjl', 'przl', 'trfl', 'jprfl', 'uprfl', 'pzrfl', 'prfg', 'prwfl',
                          'xrfl', 'pmrfl', 'bprfl', 'plfl', 'zrfl', 'urfl', 'pcrfl', 'prifl', 'pryfl', 'pral', 'porfl',
                          'aprfl', 'prbl', 'phfl', 'vprfl', 'pcfl', 'pdfl', 'prqfl', 'pyrfl', 'yprfl', 'prfol', 'prdfl',
                          'prfil', 'prnfl', 'prflb', 'prql', 'pufl', 'prfls', 'pyfl', '9rfl', '0rfl', '-rfl', '[rfl',
                          ']rfl', ';rfl', '(rfl', ')rfl', '_rfl', '=rfl', '+rfl', '{rfl', '}rfl', ':rfl', 'p3fl',
                          'p4fl', 'p5fl', 'p#fl', 'p$fl', 'p%fl', 'prf;', 'prf/', 'prf.', 'prf,', 'prf?', 'prf>',
                          'prf<', 'sessiony', 'qessions', 'pessions', 'sessionm', 'sesswons', 'sessions', 'sessizons',
                          'sessionis', 'sesstons', 'sessivns', 'sesscions', 'seshions', 'sessionv', 'sessicons',
                          'sefsions', 'sessinns', 'seyssions', 'uessions', 'sessiois', 'sessimns', 'svssions',
                          'sessiongs', 'isessions', 'sesyions', 'nsessions', 'sesvions', 'slessions', 'semssions',
                          'sessiont', 'soessions', 'sebsions', 'sesoions', 'sessirns', 'sessiops', 'sessiofns',
                          'sessionsc', 'sessiocs', 'sesksions', 'sebssions', 'sessionsp', 'sessionso', 'sessiozs',
                          'qsessions', 'sessicns', 'sessnons', 'sessiqns', 'sessionls', 'sessitons', 'oessions',
                          'sessionq', 'sessimons', 'sessmions', 'hsessions', 'sessioxns', 'sesfions', 'seslsions',
                          'sessijns', 'sessionp', 'skssions', 'sessionfs', 'sesrions', 'sessiols', 'seqsions',
                          'sbssions', 'sessionn', 'sessizns', 'sesrsions', 'sessvions', 'sesmions', 'sessionf',
                          'nessions', 'msessions', 'seksions', 'seisions', 'smessions', 'messions', 'sxssions',
                          'sevssions', 'sessiocns', 'iessions', 'sesqions', 'sessixons', 'sepssions', 'sessionys',
                          'sesspions', 'sessionus', 'seossions', 'sessbions', 'sessiwns', 'sessiors', 'sussions',
                          'sessionsb', 'sessitns', 'seussions', 'sqessions', 'sessqons', 'selssions', 'sessionr',
                          'sessiows', 'sessiogs', 'sekssions', 'senssions', 'sestsions', 'usessions', 'sesgsions',
                          'sessaons', 'sehsions', 'csessions', 'sesiions', 'sessioni', 'setssions', 'sessiozns',
                          'sesjsions', 'suessions', 'shssions', 'sessidons', 'sessbons', 'sessgions', 'sissions',
                          'sessigns', 'sessigons', 'sessiodns', 'sessionos', 'syessions', 'sjssions', 'selsions',
                          'seosions', 'sessionsl', 'sesmsions', 'syssions', 'sepsions', 'sessioqns', 'sesszons',
                          'sessiods', 'ysessions', 'sessiyns', 'sessinons', 'sersions', 'sessifons', 'sessioqs',
                          'sessfons', 'jsessions', 'sessibns', 'sessyions', 'sessionk', 'jessions', 'sessxons',
                          'seslions', 'sessionts', 'siessions', 'seusions', 'sesshions', 'sessihns', 'sessiowns',
                          'sehssions', 'hessions', 'sessyons', 'gessions', 'sessiots', 'sesbsions', 'setsions',
                          'sqssions', 'sgssions', 'scessions', 'sessiong', 'sessidns', 'spssions', 'lessions',
                          'sessiotns', 'segssions', 'snessions', 'sessionqs', 'sessionvs', 'shessions', 'sescions',
                          'sessivons', 'sesscons', 'sessionsu', 'sessiosns', 'sessionsm', 'seskions', 'secssions',
                          'sesssons', 'stessions', 'sessionps', 'fsessions', 'kessions', 'secsions', 'sessgons',
                          'sessiens', 'sessieons', 'sessionj', 'ksessions', 'sessionsr', 'sessionl', 'sessiyons',
                          'sessiovs', 'sejsions', 'skessions', 'sessdons', 'sessionb', 'sesgions', 'yessions',
                          'sessqions', 'sensions', 'seissions', 'sessionu', 'sestions', 'sessians', 'sessiaons',
                          'sessiuns', 'fessions', 'sesnsions', 'sesisions', 'sesusions', 'sessvons', 'sessfions',
                          'lsessions', 'smssions', 'tsessions', 'bessions', 'sessionsq', 'sesstions', 'sessionh',
                          'sessisns', 'sejssions', 'sessionrs', 'sessionst', 'snssions', 'slssions', 'sesspons',
                          'stssions', 'sessionks', 'segsions', 'sessionsk', 'sessioks', 'sesjions', 'sessioys',
                          'ressions', 'sessrons', 'sessioxs', 'sessionc', 'sessiwons', 'sesqsions', 'sesshons',
                          'sessnions', 'sessionsv', 'rsessions', 'sessiouns', 'sessirons', 'sesuions', 'cessions',
                          'sessrions', 'sessionsh', 'sessiovns', 'scssions', 'sessious', 'sessiono', 'sespions',
                          'seysions', 'sessmons', 'sesnions', 'sevsions', 'vsessions', 'szssions', 'bsessions',
                          'sessiogns', 'sessixns', 'sessionsi', 'sessioss', 'sessiofs', 'sesosions', 'sessibons',
                          'svessions', 'sessionsj', 'sbessions', 'sessionsf', 'sessioncs', 'psessions', 'sessihons',
                          'sessioas', 'sesbions', 'sescsions', 'sessioens', 'sessionsn', 'sessiorns', 'semsions',
                          'sessioos', 'sesysions', 'sessifns', 'sesvsions', 'vessions', 'gsessions', 'sessionsg',
                          'sesseons', 'sassions', 'sessisons', 'sessiqons', 'sossions', 'tessions', 'sessioyns',
                          'sesfsions', 'seqssions', 'sespsions', 'sessionsy', 'sessioes', 'seshsions', 'osessions',
                          'spessions', 'sgessions', 'sjessions', 'sessioans', 's2ssions', 's$ssions', 's#ssions',
                          's@ssions', 'sess7ons', 'sess&ons', 'sess*ons', 'sess(ons', 'sessi8ns', 'sessi;ns',
                          'sessi*ns', 'sessi(ns', 'sessi)ns', 'sessio,s', 'sessio<s', '/acct', '/prfl'],
                 extras={'emoji': "stormshard", "args": {
                     'profile.meta.args.profile': ['profile.meta.args.profile.description', True]},
                         "dev": False,
                         "description_keys": ['profile.meta.description1', ['profile.meta.description1', '`kill`']],
                         "name_key": "profile.slash.name"},
                 brief="profile.slash.description",
                 description="{0}\n{1}")
    async def profile(self, ctx, profile=None):
        """
        entry point for profile command when called traditionally

        Args:
            ctx: the context of the command
            profile: the profile to change to
        """
        await command_counter(self.client, ctx.author.id)
        await self.profile_command(ctx, profile)

    @slash_command(name='profile', name_localization=stw.I18n.construct_slash_dict('profile.slash.name'),
                   description="Manage your different STW Daily profiles",
                   description_localization=stw.I18n.construct_slash_dict('profile.slash.description'),
                   guild_ids=stw.guild_ids)
    async def slashprofile(self, ctx: discord.ApplicationContext,
                           profile: Option(int, name_localizations=stw.I18n.construct_slash_dict('profile.meta.args.profile'),
                                           description_localizations=stw.I18n.construct_slash_dict('profile.meta.args.profile.description'),
                                           description="The ID of the profile to switch to (e.g. 0)",
                                           default=None) = None):  # TODO: Autocomplete this with the user's profiles
        """
        The profile command.

        Args:
            ctx: The context.
            profile: The profile to switch to.
        """
        if not isinstance(profile, int):
            profile = None
        await command_counter(self.client, ctx.author.id)
        await self.profile_command(ctx, profile)

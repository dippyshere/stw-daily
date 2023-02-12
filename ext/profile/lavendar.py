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

from ext.profile.automatedfunctions import get_auto_claim
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
        super().__init__()

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
        self.children[6].label = stw.I18n.get('profile.view.button.info', self.desired_lang)

        # look ok it works dont judge arvo
        if current_selected_profile is None:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[3].disabled = True
            self.children[4].disabled = True
            self.children[5].disabled = True
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
        for child in self.children:
            child.disabled = True

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b"
        self.timed_out = True
        return await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self)

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
        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        new_profile_selected = int(select.values[0])
        self.user_document["global"]["selected_profile"] = new_profile_selected

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, new_profile_selected, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.select', self.desired_lang, new_profile_selected)}\n\u200b"
        select_options = generate_profile_select_options(self.client, new_profile_selected, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_profile_selected, self.user_document,
                                       self.message, self.desired_lang)
        await active_view(self.client, self.ctx.author.id, profile_view)

        del self.client.processing_queue[self.user_document["user_snowflake"]]
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
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
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

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, new_selected, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.delete', self.desired_lang, self.current_selected_profile)}\n\u200b"
        select_options = generate_profile_select_options(self.client, new_selected, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_selected, self.user_document,
                                       self.message, self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        await interaction.edit_original_response(embed=embed, view=profile_view)

    @discord.ui.button(label="Edit Settings", emoji="library_gear", row=2)
    async def settings_button(self, _button, interaction):
        """
        Called when the settings button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """
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
        await handle_dev_auth(self.client, self.ctx, desired_lang=self.desired_lang)

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.start.auth', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Information", emoji="experimental", row=2, disabled=True)
    async def information_button(self, _button, interaction):  # hi
        """
        Called when the information button is pressed.

        Args:
            _button: The button.
            interaction: The interaction.
        """

        self.client.temp_auth[interaction.user.id]["token"] = "💀"
        #await interaction.response.send_message(content=stw.truncate(str(self.user_document), 2000))


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
        super().__init__(title=stw.I18n.get('profile.modal.changename.title', desired_lang, self.cur_profile_id))

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label=stw.I18n.get('profile.modal.changename.input.label', desired_lang),
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder=stw.I18n.get('profile.modal.changename.input.placeholder', desired_lang)
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        """
        Called when the modal is closed.

        Args:
            interaction: The interaction.
        """
        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.changename', self.desired_lang, self.cur_profile_id)}\n\u200b"
        select_options = generate_profile_select_options(self.client, self.cur_profile_id, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message, self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
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
        super().__init__(title=stw.I18n.get('profile.modal.create.title', desired_lang, self.cur_profile_id))

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label=stw.I18n.get('profile.modal.create.input.label', desired_lang),
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder=stw.I18n.get('profile.modal.create.input.placeholder', desired_lang)
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        """
        Called when the modal is closed.

        Args:
            interaction: The interaction.
        """
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        self.user_document["global"]["selected_profile"] = self.cur_profile_id

        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)] = self.client.user_default["profiles"]["0"].copy()
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value
        self.user_document["profiles"][str(self.cur_profile_id)]["id"] = self.cur_profile_id

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document,
                                        self.desired_lang)
        embed.description += f"\n{stw.I18n.get('profile.embed.create', self.desired_lang, self.cur_profile_id)}\n\u200b"
        select_options = generate_profile_select_options(self.client, self.cur_profile_id, self.user_document,
                                                         self.desired_lang)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message, self.desired_lang)

        await active_view(self.client, self.ctx.author.id, profile_view)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
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
                self.client.processing_queue[user_document["user_snowflake"]] = True

                user_document["global"]["selected_profile"] = int(new_profile)
                await replace_user_document(self.client, user_document)
                current_command = f"\n{stw.I18n.get('profile.embed.select', desired_lang, new_profile)}\n\u200b"
                del self.client.processing_queue[user_document["user_snowflake"]]

        current_selected_profile = user_document["global"]["selected_profile"]

        embed = await create_main_embed(ctx, self.client, current_selected_profile, user_document, desired_lang)
        embed.description += current_command
        select_options = generate_profile_select_options(self.client, current_selected_profile, user_document,
                                                         desired_lang)
        profile_view = ProfileMainView(ctx, self.client, select_options, current_selected_profile, user_document,
                                       desired_lang)
        # brb back gtg soonish
        await active_view(self.client, ctx.author.id, profile_view)
        await stw.slash_send_embed(ctx, embed, profile_view)

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
                          'pro', 'prof'],
                 extras={'emoji': "stormshard", "args": {
                     'profile': 'The ID of the profile to switch to (e.g. 0)(Optional)'},
                         "dev": False},
                 brief="Manage your different STW Daily profiles",
                 description="This command allows you to manage your different STW Daily profiles. Each profile will "
                             "have it's own settings and authentication information.\nWhen switching profiles, remember"
                             "to run the `kill` command, so that next time you authenticate, it will use the selected"
                             "profile's authentication information.")
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
                                           default=0) = None):  # TODO: Autocomplete this with the user's profiles
        """
        The profile command.

        Args:
            ctx: The context.
            profile: The profile to switch to.
        """
        await command_counter(self.client, ctx.author.id)
        await self.profile_command(ctx, profile)

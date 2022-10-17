# mongo interaction

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

    try:
        if document["global"]["profiles_ver"] >= current_profile_ver:
            return document

    except KeyError:
        pass

    copied_default = client.user_default.copy()
    new_base = await asyncio.gather(asyncio.to_thread(deep_merge, copied_default, document))
    new_base = new_base[0]
    for profile in list(new_base["profiles"].keys()):
        new_base["profiles"][profile] = await asyncio.gather(
            asyncio.to_thread(deep_merge, copied_default["profiles"]["0"], new_base["profiles"][profile]))

    new_base["global"]["profiles_ver"] = current_profile_ver

    await replace_user_document(client, new_base)
    return new_base


# you are zoommin :(((   ong ok bye have fun i am having the fun PLEASE WAIT HOST IS WORKING WITH A SETTINGS DIALOG
def deep_merge(dict1, dict2):
    def _val(value_1, value_2):
        if isinstance(value_1, dict) and isinstance(value_2, dict):
            return deep_merge(value_1, value_2)
        return value_2 or value_1

    return {key: _val(dict1.get(key), dict2.get(key)) for key in dict1.keys() | dict2.keys()}


# define function to read mongodb database and return a list of all the collections in the database
async def get_user_document(client, user_snowflake):
    # which one lol
    # what do u want to call the database and collection? actually we can just slap this into config too :) sure
    document = await client.stw_database.find_one({'user_snowflake': user_snowflake})

    if document is None:
        document = await insert_default_document(client, user_snowflake)

    document = await check_profile_ver_document(client, document)
    return document


# create dictionary with user snowflake as keys and a list of all documents in that collection asi summon thee
# how should we make mongodb thingy ;w;
# um we should like gram their snowflake = 123456789012345678 post it on the gram? brb sending it to hayk yes ofc
#  yes yes :3 then um we make the collection or something and store some cool ggdpr whatever complaint info in it ;o
# idk what do you think we should do
# i was more asking if the function should request certain portions of the data or the entire thing per user
# so like either u grab the entire like document for the user or just like whatever u want but i think grab entire thing?
# the tables probably gonna be pretty small per user so just grab the whole thing
# also i got the localhost mongo running on that port localhost:27017

def setup(client):
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
    client.processing_queue = {}  # dictionaries are alot faster than lists :thumbs_up:

    with open("profile_default.json", "r") as user_default:
        client.user_default = json.load(user_default)

    # client.get_collections = get_collections
    # :3
    client.add_cog(Profile(client))


async def create_main_embed(ctx, client, current_selected_profile, user_document):
    embed_colour = client.colours["profile_lavendar"]

    if current_selected_profile is None:
        embed = discord.Embed(title=await stw.split_emoji_title(client, "Profile", "left_delta", "right_delta"),
                              description=f"""\u200b
                              **No Available Profiles**
                              ```Create a new profile using the "New Profile" Button!```""",
                              color=embed_colour)
    else:
        embed = discord.Embed(title=await stw.split_emoji_title(client, "Profile", "left_delta", "right_delta"),
                              description=f"""\u200b
                              **Currently Selected Profile {current_selected_profile}**
                              ```{user_document["profiles"][str(current_selected_profile)]["friendly_name"]}```""",
                              color=embed_colour)
    embed = await stw.set_thumbnail(client, embed, "storm_shard")
    embed = await stw.add_requested_footer(ctx, embed)
    return embed


class ProfileMainView(discord.ui.View):
    def __init__(self, ctx, client, profile_options, current_selected_profile, user_document, previous_message=None):
        super().__init__()
        self.client = client
        self.children[0].options = profile_options

        if previous_message is not None:
            self.message = previous_message

        # look ok it works dont judge arvo
        if current_selected_profile is None:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[3].disabled = True
            self.children[0].placeholder = "No available profiles"

        self.ctx = ctx
        self.author = ctx.author
        self.current_selected_profile = current_selected_profile
        self.user_document = user_document
        self.interaction_check_done = {}

        self.button_emojis = {
            'meleegeneric': self.client.config["emojis"]["meleegeneric"],
            'leadsurvivor': self.client.config["emojis"]['leadsurvivor'],
            'cross': self.client.config["emojis"]['cross'],
        }

        if not (len(user_document["profiles"].keys()) < client.config["profile_settings"]["maximum_profiles"]):
            self.children[2].disabled = True

        self.children[1:] = list(map(self.map_button_emojis, self.children[1:]))

    async def on_timeout(self):

        for child in self.children:
            child.disabled = True

        embed = await create_main_embed(self.ctx, self.client, self.current_selected_profile, self.user_document)
        embed.description += "\n*Timed out, please reuse command to continue*\n\u200b"
        await self.message.edit(embed=embed, view=self)

    def map_button_emojis(self, button):
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def interaction_check(self, interaction):
        if self.author == interaction.user:
            return True
        else:
            try:
                already_notified = self.interaction_check_done[interaction.user.id]
            except:
                already_notified = False
                self.interaction_check_done[interaction.user.id] = True

            if not already_notified:
                support_url = self.client.config["support_url"]
                acc_name = ""
                error_code = "errors.stwdaily.not_author_interaction_response"
                embed = await stw.post_error_possibilities(interaction, self.client, "help", acc_name, error_code,
                                                           support_url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            else:
                return False

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def selected_option(self, select, interaction):
        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        new_profile_selected = int(select.values[0])
        self.user_document["global"]["selected_profile"] = new_profile_selected

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, new_profile_selected, self.user_document)
        embed.description += f"\n*Selected profile **{new_profile_selected}***\n\u200b"
        select_options = generate_select_options(self.client, new_profile_selected, self.user_document)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_profile_selected, self.user_document,
                                       self.message)

        del self.client.processing_queue[self.user_document["user_snowflake"]]
        await interaction.edit_original_response(embed=embed, view=profile_view)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Change Name", emoji="meleegeneric")
    async def name_button(self, _button, interaction):
        await interaction.response.send_modal(ChangeNameModal(self.ctx, self.client, self.user_document, self.message))

        for child in self.children:
            child.disabled = True

        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.grey, label="New Profile", emoji="leadsurvivor")
    async def new_button(self, _button, interaction):
        await interaction.response.send_modal(NewProfileModal(self.ctx, self.client, self.user_document, self.message))

        for child in self.children:
            child.disabled = True

        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Delete Profile", emoji="cross")
    async def delete_button(self, _button, interaction):

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
        embed = await create_main_embed(self.ctx, self.client, new_selected, self.user_document)
        embed.description += f"\n*Deleted Profile **{self.current_selected_profile}***\n\u200b"
        select_options = generate_select_options(self.client, new_selected, self.user_document)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, new_selected, self.user_document,
                                       self.message)

        del self.client.processing_queue[self.user_document["user_snowflake"]]
        await interaction.edit_original_response(embed=embed, view=profile_view)


class ChangeNameModal(discord.ui.Modal):
    def __init__(self, ctx, client, user_document, message):
        self.ctx = ctx
        self.client = client
        self.cur_profile_id = user_document["global"]["selected_profile"]

        self.user_document = user_document
        super().__init__(title=f"Change name of profile {self.cur_profile_id}")

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label="Enter a new name to identify this profile",
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder="Enter new name"
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        self.client.processing_queue[self.user_document["user_snowflake"]] = True

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document)
        embed.description += f"\n*Changed name of profile **{self.cur_profile_id}***\n\u200b"
        select_options = generate_select_options(self.client, self.cur_profile_id, self.user_document)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message)

        del self.client.processing_queue[self.user_document["user_snowflake"]]
        await interaction.response.edit_message(embed=embed, view=profile_view)


class NewProfileModal(discord.ui.Modal):
    def __init__(self, ctx, client, user_document, message):
        self.ctx = ctx
        self.client = client
        self.cur_profile_id = len(user_document["profiles"])

        self.user_document = user_document
        super().__init__(title=f"Create profile {self.cur_profile_id}")

        # Add the required items into this modal for entering

        profile_settings = client.config["profile_settings"]

        # The profile friendly name
        input_profile_name = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label="Enter a name to identify this profile",
            min_length=profile_settings["min_friendly_name_length"],
            max_length=profile_settings["max_friendly_name_length"],
            placeholder="Friendly Name"
        )
        self.message = message
        self.add_item(input_profile_name)

    async def callback(self, interaction: discord.Interaction):
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        self.user_document["global"]["selected_profile"] = self.cur_profile_id

        # there is probably a better way to do this
        self.user_document["profiles"][str(self.cur_profile_id)] = self.client.user_default["profiles"]["0"].copy()
        self.user_document["profiles"][str(self.cur_profile_id)]["friendly_name"] = self.children[0].value
        self.user_document["profiles"][str(self.cur_profile_id)]["id"] = self.cur_profile_id

        await replace_user_document(self.client, self.user_document)
        embed = await create_main_embed(self.ctx, self.client, self.cur_profile_id, self.user_document)
        embed.description += f"\n*Created profile **{self.cur_profile_id}***\n\u200b"
        select_options = generate_select_options(self.client, self.cur_profile_id, self.user_document)
        profile_view = ProfileMainView(self.ctx, self.client, select_options, self.cur_profile_id, self.user_document,
                                       self.message)

        del self.client.processing_queue[self.user_document["user_snowflake"]]
        await interaction.response.edit_message(embed=embed, view=profile_view)


def generate_select_options(client, current_selected_profile, user_document):
    select_options = []

    if current_selected_profile is None:
        select_options.append(discord.SelectOption(
            label="No Available Profiles!",
            value="None",
            default=False,
            emoji=client.config["emojis"]["error"]
        ))

    for profile in user_document["profiles"]:

        profile = user_document["profiles"][profile]

        selected = False
        profile_id = profile["id"]
        if profile_id == current_selected_profile:
            selected = True

        profile_id = str(profile_id)
        select_options.append(discord.SelectOption(
            label=profile["friendly_name"],
            value=profile_id,
            default=False,
            emoji=client.config["emojis"][profile_id]
        ))

    return select_options


# cog for the profile related commands
class Profile(ext.Cog):

    def __init__(self, client):
        self.client = client
        # can u not unindent by ctrl shift + [ weird nanny

    async def profile_command(self, ctx, new_profile, slash=False):
        user_document = await self.client.get_user_document(self.client, ctx.author.id)
        current_command = "\n*Waiting for command*\n\u200b"

        if new_profile is not None:

            if new_profile not in list(user_document["profiles"].keys()):
                current_command = "\n*Attempted to switch to non-existent profile*\n\u200b"
            else:
                self.client.processing_queue[user_document["user_snowflake"]] = True

                user_document["global"]["selected_profile"] = int(new_profile)
                await replace_user_document(self.client, user_document)
                current_command = f"\n*Selected profile **{new_profile}***\n\u200b"
                del self.client.processing_queue[user_document["user_snowflake"]]

        user_document = await self.client.get_user_document(self.client, ctx.author.id)
        current_selected_profile = user_document["global"]["selected_profile"]

        embed = await create_main_embed(ctx, self.client, current_selected_profile, user_document)
        embed.description += current_command
        select_options = generate_select_options(self.client, current_selected_profile, user_document)
        profile_view = ProfileMainView(ctx, self.client, select_options, current_selected_profile, user_document)
        # brb back gtg soonish
        await stw.slash_send_embed(ctx, slash, embed, profile_view)

    @ext.command(name='profile',
                 extras={'emoji': "stormshard", "args": {'profile': 'Which profile you wish to change to, leave this empty if you dont know about profiles or if you wish to utilise the view (Optional)'}},
                 brief="Allows you to create, change the name of, select, & delete profiles",
                 description="A command which allows you to interact with a view to switch between profiles, create new profiles utilising a modal, delete existing profiles and edit the name of existing profiles")
    async def profile(self, ctx, profile=None):
        await self.profile_command(ctx, profile)

    @slash_command(name='profile',
                   description="Allows you to create, change the name of, select, & delete profiles",
                   guild_ids=stw.guild_ids)
    async def slashprofile(self, ctx: discord.ApplicationContext,
                            profile: Option(int,
                                          "Which profile you wish to switch to (Leave empty if you wish to utilise the View)") = None):
        await self.profile_command(ctx, profile, True)

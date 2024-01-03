"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for automatic functions :3
"""
import asyncio
import datetime
import random
import logging

import discord
import discord.ext.commands as ext
from discord.ext import tasks
from orjson import orjson
from ext.profile.sunday import settings_command

import stwutil as stw
from ext.profile.bongodb import active_view, command_counter, generate_profile_select_options, get_all_users_cursor, replace_user_document, timeout_check_processing

claimed_account_ids = []
logger = logging.getLogger(__name__)


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
        title=await stw.add_emoji_title(client, stw.I18n.get('autoclaim.embed.title', desired_lang), "Dark5"),
        description=(f"\u200b\n"
                     f"{stw.I18n.get('profile.embed.noprofiles.description1', desired_lang)}\n"
                     f"```{stw.I18n.get('devauth.embed.noprofile.descripton2', desired_lang)}```\u200b\n"),
        color=embed_colour)
    no_profiles_embed = await stw.set_thumbnail(client, no_profiles_embed, "storm_shard")
    no_profiles_embed = await stw.add_requested_footer(ctx, no_profiles_embed, desired_lang)

    return no_profiles_embed

async def create_autoclaim_embed(ctx, client,  currently_selected_profile_id, user_document, desired_lang, dont_send=False):
    """
    Creates the sub-embed for autoclaim for the profile command
    
    Args:
        ctx: The context of the command.
        client: The bot client.
        user_document: The user document.
        desired_lang: The desired language.

    Returns:
        discord.Embed: The sub embed.
    """
    embed_colour = client.colours["profile_lavendar"]

    try:
        current_selected_profile = user_document["profiles"][str(currently_selected_profile_id)]
    except:
        embed = await no_profiles_page(client, ctx, desired_lang)
        return await stw.slash_send_embed(ctx, client, embeds=embed)
    
    try:
        method = current_selected_profile["settings"]["autoresmethod"]
    except:
        method = "method_disabled"

    devauth = current_selected_profile["authentication"] is not None

    # Message dictating profile level autoclaim state
    autoclaim = stw.I18n.get("autoclaim.toggle.enabled", desired_lang) if current_selected_profile.get("auto_claim", None) is not None else stw.I18n.get("autoclaim.toggle.disabled", desired_lang)

    embed = discord.Embed(
    title=await stw.add_emoji_title(client, stw.I18n.get('autoclaim.embed.title', desired_lang), "Dark5"),
    description=(f"\u200b\n"
                    f"{stw.I18n.get('profile.embed.currentlyselected', desired_lang, currently_selected_profile_id)}\n"
                    f"```{user_document['profiles'][str(currently_selected_profile_id)]['friendly_name']}```\u200b\n"
                    f"{stw.I18n.get('autoclaim.embed.nodevauth', desired_lang) if not devauth else ''}"
                    f"{stw.I18n.get('autoclaim.embed.description2', desired_lang, client.config['emojis']['experimental'])}\u200b\n"
                    f"```asciidoc\n"
                    f"{stw.I18n.get('autoclaim.embed.toggle', desired_lang, autoclaim)}\n\n"
                    f"{stw.I18n.get('autoclaim.embed.autores', desired_lang, stw.I18n.get(f'settings.config.autoresmethod.{method}', desired_lang))}"
                    f"```\u200b"),    
    
    color=embed_colour)

    embed = await stw.set_thumbnail(client, embed, "storm_shard")
    embed = await stw.add_requested_footer(ctx, embed, desired_lang)

    if dont_send:
        return embed
    
    highlight_view = AutoclaimHighlightView(ctx, client, currently_selected_profile_id, user_document, desired_lang)
    await command_counter(client, ctx.author.id)
    await active_view(client, ctx.author.id, highlight_view)
    await stw.slash_send_embed(ctx, client, embed, view=highlight_view)

class AutoclaimHighlightView(discord.ui.View):
    def __init__(self, ctx, client,  currently_selected_profile_id, user_document, desired_lang=None):
        super().__init__(timeout=240)

        self.client = client
        self.desired_lang = desired_lang
        self.ctx = ctx
        self.author = ctx.author
        self.currently_selected_profile_id = currently_selected_profile_id
        self.user_document = user_document
        self.interaction_check_done = {}
        self.timed_out = False

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                            user_document, desired_lang)
        self.children[0].placeholder = stw.I18n.get('profile.view.options.placeholder', self.desired_lang)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

        current_selected_profile = user_document["profiles"][str(currently_selected_profile_id)]

        # Message dictating profile level autoclaim state for the button
        autoclaim_state = current_selected_profile.get("auto_claim", None) is not None
        autoclaim = stw.I18n.get("autoclaim.toggle.to.disabled", desired_lang) if autoclaim_state else stw.I18n.get("autoclaim.toggle.to.enabled", desired_lang)

        self.children[2].label = autoclaim

        if autoclaim_state:
            self.children[2].style = discord.ButtonStyle.red
        else:
            self.children[2].style = discord.ButtonStyle.green
    
    async def interaction_check(self, interaction):
        """
        This function checks the interaction

        Args:
            interaction: The interaction

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "device") & await timeout_check_processing(self, self.client, interaction)                              

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        if self.timed_out == True:
            return

        for child in self.children:
            child.disabled = True

        embed = await create_autoclaim_embed(self.ctx, self.client, self.currently_selected_profile_id, self.user_document,
                                        self.desired_lang, True)
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
        new_profile_selected = int(select.values[0])
        self.user_document["global"]["selected_profile"] = new_profile_selected

        for child in self.children:
            child.disabled = True
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await interaction.response.edit_message(view=self)
        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        self.stop()


        embed = await create_autoclaim_embed(self.ctx, self.client,  new_profile_selected, self.user_document,
                                        self.desired_lang, True)
        embed.description += f"\n{stw.I18n.get('profile.embed.select', self.desired_lang, new_profile_selected)}\n\u200b"
        autoclaim_view = AutoclaimHighlightView(self.ctx, self.client,  new_profile_selected, self.user_document, self.desired_lang)
        await active_view(self.client, self.ctx.author.id, autoclaim_view)
        await interaction.edit_original_response(embed=embed, view=autoclaim_view)

    @discord.ui.button(label="Auto-Research", emoji="experimental")
    async def autoresearch_button(self, button, interaction):
        """
        This function handles the auto-research button

        Args:
            button: The button
            interaction: The interaction
        """
        embed = await create_autoclaim_embed(self.ctx, self.client, self.currently_selected_profile_id, self.user_document,
                                        self.desired_lang, True)
        embed.description += f"\n{stw.I18n.get('autoclaim.embed.start.autoresearch', self.desired_lang)}\n\u200b"

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
        self.timed_out = True

        await command_counter(self.client, self.ctx.author.id)
        await settings_command(self.client, self.ctx, "res")

    @discord.ui.button(label="Toggle Claiming", emoji="library_clock")
    async def claim_toggle_button(self, button, interaction):
        
        current_selected_profile = self.user_document["profiles"][str(self.currently_selected_profile_id)]

        for child in self.children:
            child.disabled = True
        self.client.processing_queue[self.user_document["user_snowflake"]] = True
        await interaction.response.edit_message(view=self)

        # toggle switch
        current_autoclaim = current_selected_profile.get("auto_claim",  None)
        if current_autoclaim is None:
            current_selected_profile["auto_claim"] = True
        else:
            current_selected_profile["auto_claim"] = None

        # set autoclaim tag to true so we get it on auto claiminator (keeps all modern post daily removal users ig)
        self.user_document["auto_claim"] = True

        await replace_user_document(self.client, self.user_document)
        del self.client.processing_queue[self.user_document["user_snowflake"]]
        self.stop()

        embed = await create_autoclaim_embed(self.ctx, self.client,  self.currently_selected_profile_id, self.user_document,
                                        self.desired_lang, True)
        embed.description += f"\n{stw.I18n.get('autoclaim.embed.toggle.claim', self.desired_lang)}\n\u200b"
        autoclaim_view = AutoclaimHighlightView(self.ctx, self.client, self.currently_selected_profile_id, self.user_document, self.desired_lang)
        await active_view(self.client, self.ctx.author.id, autoclaim_view)
        await interaction.edit_original_response(embed=embed, view=autoclaim_view)

# a function to autoclaim daily rewards on epic games accounts
async def auto_authenticate(client, auth_entry):
    """
    A function called per account to claim the daily reward using provided auth info i guess

    Args:
        client: The client
        auth_entry: The auth entry

    Returns:
        True if successful, False if not
    """
    # TODO: with time, we can optimise / add more features to this function
    snowflake = auth_entry['user_snowflake']
    current_selected_profile = auth_entry["global"]["selected_profile"]

    for profile in auth_entry["profiles"]:
        current_profile = auth_entry["profiles"][profile]

        if current_profile["authentication"] is not None:
            auth_entry["global"]["selected_profile"] = profile

            if current_profile.get("auto_claim", None) is None:
                continue

            try:
                if auth_entry["profiles"][profile]["authentication"]["hasExpired"]:
                    continue
            except:
                pass


            auth_info_thread = await asyncio.gather(
                asyncio.to_thread(stw.decrypt_user_data, snowflake, current_profile["authentication"]))
            dev_auth_info = auth_info_thread[0]

            account_id = dev_auth_info["accountId"]
            claimed_account_ids = []
            if account_id not in claimed_account_ids:
                logger.info(f"Auto authenticating for: {snowflake}")
                
                claimed_account_ids.append(account_id)
                await asyncio.sleep(random.randint(2, 10))
                logger.info(f"Display name: {current_profile['authentication']['displayName']}")
                token_req = await stw.get_token_devauth(client, auth_entry, game="ios",
                                                        auth_info_thread=auth_info_thread)
                response = orjson.loads(await token_req.read())

                try:
                    access_token = response["access_token"]
                    # Simulate temp entry so we can do profile request stuff i guess lol
                    entry = {   
                        "token": access_token,
                        "account_id": account_id,
                        "vbucks": True,
                        "account_name": "",
                        'expiry': "",
                        "day": None,
                        "bb_token": "",
                        "bb_day": None,
                        "games": "",
                    }
                    # await asyncio.sleep(random.randint(2, 10))

                    # Auto-Research
                    if  auth_entry["profiles"][profile]["settings"].get("autoresmethod", "method_disabled") != "method_disabled":
                        await auto_research_claim(client, auth_entry, profile, entry)
                
                except Exception as E:
                    try:
                        if response["errorCode"] == "errors.com.epicgames.account.invalid_account_credentials":
                            auth_entry["profiles"][profile]["authentication"]["hasExpired"] = True
                            auth_entry["global"]["selected_profile"] = current_selected_profile
                            await replace_user_document(client, auth_entry)
                            logger.warning(f"Auto-Claim authentication expired for profile {profile}")
                    except:
                        pass
                    logger.warning(f"Failed to authenticate for profile {profile}: Epic: {response} | Python: {E}")

async def auto_research_claim(client, auth_entry, profile, temp_entry):
    # Debug info var
    snowflake = auth_entry['user_snowflake']

    # Get current fort stats
    current_research_statistics_request = await stw.profile_request(client, "query", temp_entry)
    json_response = orjson.loads(await current_research_statistics_request.read())

    current_levels = json_response['profileChanges'][0]['profile']['stats']['attributes']['research_levels']
    
    # Calculate next action based on current levels
    proc_max = False
    try:
        if current_levels["offense"] + current_levels["fortitude"] + current_levels["resistance"] + current_levels[
            "technology"] >= 480:
            proc_max = True
            pass
    except:
        for stat in ["offense", "fortitude", "resistance", "technology"]:
            if stat not in current_levels:
                current_levels[stat] = 0

    # Flag that dictates whether or not to update the setting based on current stat levels
    update_profile = True
    method = auth_entry["profiles"][profile]["settings"].get("autoresmethod", "method_disabled")

    # If we're at max research then disable research
    if proc_max:
        logger.warning(f"User: {snowflake} Has reached max research points on profile {profile}, Disabling auto-research.")
        auth_entry["profiles"][profile]["settings"]["autoresmethod"] = "method_disabled"
    
    # If we're at max for anything with  that method, switch back
    elif method == "method_fortitude"   and current_levels["fortitude"] >= 120 or \
         method == "method_offense"     and current_levels["offense"] >= 120 or \
         method == "method_resistance"  and current_levels["resistance"] >= 120 or \
         method == "method_technology"  and current_levels["technology"] >= 120:
        
        logger.warning(f"User: {snowflake} Has reached max research points for a stat on profile {profile}, Switching to Method: Distribute.")
        auth_entry["profiles"][profile]["settings"]["autoresmethod"] = "method_distribute"

    else:
        update_profile = False

    # Update user document from changes to autosresmethod
    if update_profile:
        client.processing_queue[snowflake] = True
        await replace_user_document(client, auth_entry)
        del client.processing_queue[snowflake]
    
    # Reget method post method changing
    method = auth_entry["profiles"][profile]["settings"].get("autoresmethod", "method_disabled")

    # If our method is disabled, then dont claim as we shouldn't
    if method == "method_disabled":
        return
    
    # get the next "stat" to upgrade
    upgrade_stat = "fortitude"

    # call me yandere dev
    if method == "method_fortitude":
        upgrade_stat = "fortitude"

    elif method == "method_offense":
        upgrade_stat = "offense"

    elif method == "method_resistance":
        upgrade_stat = "resistance"
    
    elif method == "method_technology":
        upgrade_stat = "technology"
    
    else:
        # Find the minimum of all the stats
        upgrade_stat = min(current_levels, key=current_levels.get)

    logger.debug(f"Attempting to upgrade stat {upgrade_stat} due to method {method} for user: {snowflake}")

   # try:
    # Find research guid
    research_cog = client.cogs['Research']
    research_guid_temp = await asyncio.gather(asyncio.to_thread(research_cog.check_for_research_guid_key, json_response))
    research_guid = research_guid_temp[0]

    # Claim research point resources
    current_research_statistics_request = await stw.profile_request(client, "resources", temp_entry, json={"collectorsToClaim": [research_guid]})
    json_response = orjson.loads(await current_research_statistics_request.read())

    # Get total points the user currently has
    token_points = await asyncio.gather(asyncio.to_thread(research_cog.check_for_research_points_item, json_response))
    total_points, rp_token_guid = token_points[0][0], token_points[0][1]

    # Cannot afford stat so prematurely return
    if current_levels[upgrade_stat] >= 120 or total_points['quantity'] < stw.research_stat_cost(upgrade_stat, current_levels[upgrade_stat]):
        logger.warning(f"User: {snowflake} Cannot afford stat {upgrade_stat}, Ignoring")
        return

    await stw.profile_request(client, "purchase_research", temp_entry,
                                            json={'statId': upgrade_stat})

async def get_auto_claim(client):
    """
    A function to get the auto claim cursor

    Args:
        client: The client
    """
    user_cursor = await get_all_users_cursor(client)

    async for user in user_cursor:
        await auto_authenticate(client, user)

    await user_cursor.close()


class AutoFunction(ext.Cog):
    """
    Cog for the Reminder task and the Autoclaim command
    """

    @ext.slash_command(name='autoclaim', name_localization=stw.I18n.construct_slash_dict("autoclaim.slash.name"),
                       description='Autoclaim information related to the current profile',
                       description_localization=stw.I18n.construct_slash_dict("autoclaim.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slash_autoclaim(self, ctx: discord.ApplicationContext,):
        """
        This function is the slash command for the settings command.

        Args:
            ctx: The context of the slash command.
            setting: The setting to change.
            profile: The profile to change the setting on.
            value: The value to change the setting to.
        """
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, desired_lang=desired_lang)
        await create_autoclaim_embed(ctx, self.client, user_document["global"]["selected_profile"], user_document, desired_lang)

    @ext.command(name='autoclaim', aliases=[],                  
                  extras={'emoji': "library_clock", "args": {}, 
                "dev": False, "description_keys": ["autoclaim.meta.description1"],
                         "name_key": "autoclaim.slash.name"},
                 brief="autoclaim.slash.description",
                 description="{0}")
    async def autoclaim(self, ctx):
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, desired_lang=desired_lang)
        await create_autoclaim_embed(ctx, self.client, user_document["global"]["selected_profile"], user_document, desired_lang)
    
    def __init__(self, client):
        self.client = client
        # self.autoclaim_task.start()  # hi

    @tasks.loop(time=datetime.time(0, 0, random.randint(11, 39), tzinfo=datetime.timezone.utc))
    async def autoclaim_task(self):
        """
        The autoclaim task
        """
        await get_auto_claim(self.client)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(AutoFunction(client))

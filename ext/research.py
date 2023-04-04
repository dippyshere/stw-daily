"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the research command. collect and spend research points
"""

import asyncio
import logging

import orjson
import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from cache import AsyncLRU

import stwutil as stw

logger = logging.getLogger(__name__)


@AsyncLRU(maxsize=16)
async def add_fort_fields(client, embed, current_levels, desired_lang, extra_white_space=False):
    """
    Add the fields to the embed for the fort stats.

    Args:
        client: The client object.
        embed: The embed to add the fields to.
        current_levels: The dictionary of current levels of the stats.
        desired_lang: The language to use for the embed.
        extra_white_space: Whether to add extra white space to the embed.

    Returns:
        The embed with the fields added.
    """
    # print("current levels: ", current_levels)
    fortitude = current_levels["fortitude"]
    offense = current_levels["offense"]
    resistance = current_levels["resistance"]
    technology = current_levels["technology"]

    embed.add_field(name="\u200B", value="\u200B", inline=True)
    embed.add_field(name=stw.I18n.get("research.stat.fortitude", desired_lang, client.config["emojis"]["fortitude"]),
                    value=f'```{fortitude} (+{int((await stw.research_stat_rating("fortitude", fortitude))[0])}%)```\u200b',
                    inline=True)
    embed.add_field(name=stw.I18n.get("research.stat.offense", desired_lang, client.config["emojis"]["offense"]),
                    value=f'```{offense} (+{int((await stw.research_stat_rating("offense", offense))[0])}%)```\u200b',
                    inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=True)
    embed.add_field(name=stw.I18n.get("research.stat.resistance", desired_lang, client.config["emojis"]["resistance"]),
                    value=f'```{resistance} (+{int((await stw.research_stat_rating("resistance", resistance))[0])}%)```\u200b',
                    inline=True)

    extra_white_space = "\u200b\n\u200b\n\u200b" if extra_white_space is True else ""
    embed.add_field(name=stw.I18n.get("research.stat.tech", desired_lang, client.config["emojis"]["technology"]),
                    value=f'```{technology} (+{int((await stw.research_stat_rating("technology", technology))[0])}%)```{extra_white_space}',
                    inline=True)
    return embed


class ResearchView(discord.ui.View):
    """
    The UI View for the research command
    """

    def disable_button_when_poor(self, button, index):
        """
        Disable the button if the user cannot afford the stat.

        Args:
            button: The button to disable.
            index: The index of the button.

        Returns:
            The button with the disabled attribute set.
        """
        button_map = ['fortitude', 'offense', 'resistance', 'technology']  # woah ur alive yes
        if self.current_levels[button_map[index]] >= 120:
            button.disabled = True
            button.label = stw.I18n.get('research.button.max', self.desired_lang)
            return button
        button.disabled = not self.check_stat_affordability(button_map[index])
        button.label = f"{int(stw.research_stat_cost(button_map[index], self.current_levels[button_map[index]])):,}"
        return button

    def check_stat_affordability(self, stat):
        """
        Check if the stat can be afforded.

        Args:
            stat: The stat to check.

        Returns:
            bool: True if the stat can be afforded, False if not.
        """
        if self.current_levels[stat] >= 120:
            return False
        return self.total_points['quantity'] >= stw.research_stat_cost(stat, self.current_levels[stat])

    def map_button_emojis(self, button):
        """
        Map the button emojis to the buttons.

        Args:
            button: The button to map the emoji to.

        Returns:
            The button with the emoji mapped.
        """
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def on_timeout(self):
        """
        Called when the view times out.

        Returns:
            None
        """
        res_green = self.client.colours["research_green"]
        crown_yellow = self.client.colours["crown_yellow"]

        for child in self.children:
            child.disabled = True
        total_points = self.total_points
        current_levels = self.current_levels
        proc_max = False
        try:
            if current_levels["offense"] + current_levels["fortitude"] + current_levels["resistance"] + current_levels["technology"] == 480:
                proc_max = True
        except:
            pass
        max_fort_string = f"{stw.I18n.get('research.embed.maximumstats', self.desired_lang)}\n"
        total_points_quantity = total_points["quantity"]
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('research.embed.title', self.desired_lang),
                                            "crown" if proc_max else "research_point"),
            description=(f'\u200b\n{max_fort_string if proc_max else ""}'
                         f'{stw.I18n.get("research.embed.description.singular", self.desired_lang, f"{total_points_quantity:,}") if total_points["quantity"] == 1 else stw.I18n.get("research.embed.description.plural", self.desired_lang, f"{total_points_quantity:,}")}\n\u200b\n\u200b'),
            colour=crown_yellow if proc_max else res_green
        )

        embed = await stw.set_thumbnail(self.client, embed, "crown" if proc_max else "research")
        embed = await stw.add_requested_footer(self.ctx, embed, self.desired_lang)
        embed = await add_fort_fields(self.client, embed, current_levels, self.desired_lang)
        embed.add_field(name=f"\u200b", value=f"{stw.I18n.get('generic.embed.timeout', self.desired_lang)}\n\u200b")
        return await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self)

    async def universal_stat_process(self, interaction, stat):
        """
        Process the stat button press for any stat.

        Args:
            interaction: The interaction object.
            stat: The stat to process.

        Returns:
            None
        """
        res_green = self.client.colours["research_green"]
        crown_yellow = self.client.colours["crown_yellow"]

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        stat_purchase = await stw.profile_request(self.client, "purchase_research", self.auth_info[1],
                                                  json={'statId': stat})
        purchased_json = orjson.loads(await stat_purchase.read())

        total_points = self.total_points
        current_levels = self.current_levels

        for child in self.children:
            child.disabled = False

        try:
            if purchased_json['errorCode'] == 'errors.com.epicgames.fortnite.item_consumption_failed':
                total_points_quantity = total_points["quantity"]
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client,
                                                    stw.I18n.get('research.embed.title', self.desired_lang),
                                                    "research_point"),
                    description=(f'\u200b\n'
                                 f'{stw.I18n.get("research.embed.description.singular", self.desired_lang, f"{total_points_quantity:,}") if total_points["quantity"] == 1 else stw.I18n.get("research.embed.description.plural", self.desired_lang, f"{total_points_quantity:,}")}\n\u200b\n\u200b'),
                    colour=res_green
                )

                embed = await stw.set_thumbnail(self.client, embed, "research")
                embed = await stw.add_requested_footer(interaction, embed, self.desired_lang)
                embed = await add_fort_fields(self.client, embed, current_levels, self.desired_lang)
                embed.add_field(name=f"\u200b",
                                value=f'{stw.I18n.get("research.embed.insufficient", self.desired_lang, stw.I18n.get("research.button.{0}".format(stat), self.desired_lang))}\n\u200b')
                await interaction.edit_original_response(embed=embed, view=self)
                return
        except:
            pass

        current_research_statistics_request = await stw.profile_request(self.client, "query", self.auth_info[1])
        json_response = orjson.loads(await current_research_statistics_request.read())
        current_levels, proc_max = await research_query(interaction, self.client, self.auth_info, [], json_response,
                                                        self.desired_lang)

        self.current_levels = current_levels

        # What I believe happens is that epic games removes the research points item if you use it all... not to sure if they change the research token guid
        try:
            research_points_item = purchased_json['profileChanges'][0]['profile']['items'][self.research_token_guid]
        except Exception as e:
            # this can be entered if there is an error during purchase
            try:
                error_code = json_response["errorCode"]
                logger.warning(f"Error during purchase: {e} | {stw.truncate(str(purchased_json))}")
                acc_name = self.auth_info[1]["account_name"]
                embed = await stw.post_error_possibilities(self.ctx, self.client, "research", acc_name, error_code,
                                                           verbiage_action="resitem",
                                                           desired_lang=self.desired_lang)
                await interaction.edit_original_response(embed=embed, view=self)
                return
            except:
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client,
                                                    stw.I18n.get('research.embed.title', self.desired_lang),
                                                    "research_point"),
                    description=(f"\u200b\n"
                                 f"{stw.I18n.get('research.error.zeroplaceholder', self.desired_lang)}\n\u200b\n\u200b"),
                    colour=res_green
                )

                embed = await add_fort_fields(self.client, embed, current_levels, self.desired_lang)
                embed.add_field(name=f"\u200b",
                                value=f"{stw.I18n.get('research.embed.expendedpoints', self.desired_lang)}\n\u200b")
                embed = await stw.set_thumbnail(self.client, embed, "research")
                embed = await stw.add_requested_footer(interaction, embed, self.desired_lang)
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=embed, view=self)
                return

        spent_points = self.total_points['quantity'] - research_points_item['quantity']
        max_fort_string = f"{stw.I18n.get('research.embed.maximumstats', self.desired_lang)}\n"
        total_points_quantity = research_points_item['quantity']
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('research.embed.title', self.desired_lang),
                                            "crown" if proc_max else "research_point"),
            description=(f'\u200b\n{max_fort_string if proc_max else ""}'
                         f'{stw.I18n.get("research.embed.description.singular", self.desired_lang, f"{total_points_quantity:,}") if total_points["quantity"] == 1 else stw.I18n.get("research.embed.description.plural", self.desired_lang, f"{total_points_quantity:,}")}\n\u200b\n\u200b'),
            colour=crown_yellow if proc_max else res_green
        )

        embed = await add_fort_fields(self.client, embed, current_levels, self.desired_lang)
        embed.add_field(name=f"\u200b",
                        value=f"{stw.I18n.get('research.embed.purchasestat', self.desired_lang, f'{spent_points:,}', stw.I18n.get('research.button.{0}'.format(stat), self.desired_lang))}\n\u200b")
        embed = await stw.set_thumbnail(self.client, embed, "crown" if proc_max else "research")
        embed = await stw.add_requested_footer(interaction, embed, self.desired_lang)
        self.total_points = research_points_item

        for i, child in enumerate(self.children):
            self.disable_button_when_poor(child, i)

        await interaction.edit_original_response(embed=embed, view=self)

    # creo kinda fire though ngl
    def __init__(self, client, ctx, auth_info, author, total_points, current_levels, research_token_guid, og_msg,
                 desired_lang):
        super().__init__(timeout=360.0)
        self.client = client
        self.ctx = ctx
        self.auth_info = auth_info
        self.author = author
        self.interaction_check_done = {}
        self.total_points = total_points
        self.current_levels = current_levels
        self.research_token_guid = research_token_guid
        self.message = og_msg
        self.desired_lang = desired_lang

        self.button_emojis = {
            'fortitude': self.client.config["emojis"]["fortitude"],
            'offense': self.client.config["emojis"]['offense'],
            'resistance': self.client.config["emojis"]['resistance'],
            'technology': self.client.config["emojis"]['technology']
        }

        self.children = list(map(self.map_button_emojis, self.children))

        for i, child in enumerate(self.children):
            self.disable_button_when_poor(child, i)
            # hmm github copilot ;o maybe i should use it instead of writing everything :( it DOESNT work on the remote client :p it doesnt work well on the remote clientif it works

    async def interaction_check(self, interaction):
        """
        Check if the interaction is performed by the author

        Args:
            interaction: The interaction object.

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "research")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="fortitude")
    async def fortitude_button(self, _button, interaction):
        """
        Process the fortitude button press.

        Args:
            _button: The button object.
            interaction: The interaction object.
        """
        await self.universal_stat_process(interaction, "fortitude")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="offense")
    async def offense_button(self, _button, interaction):
        """
        Process the offense button press.

        Args:
            _button: The button object.
            interaction: The interaction object.
        """
        await self.universal_stat_process(interaction, "offense")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="resistance")
    async def resistance_button(self, _button, interaction):
        """
        Process the resistance button press.

        Args:
            _button: The button object.
            interaction: The interaction object.
        """
        await self.universal_stat_process(interaction, "resistance")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="technology")
    async def technology_button(self, _button, interaction):
        """
        Process the technology button press.

        Args:
            _button: The button object.
            interaction: The interaction object.
        """
        await self.universal_stat_process(interaction, "technology")


async def research_query(ctx, client, auth_info, final_embeds, json_response, desired_lang):
    """
    Query the research endpoint for the current research levels.

    Args:
        ctx: The context object.
        client: The client object.
        auth_info: The auth info object.
        final_embeds: The final embeds object.
        json_response: The json response object.
        desired_lang: The desired language.

    Returns:
        tuple: The current research levels dict, and a bool if the max research level has been reached.
    """
    acc_name = auth_info[1]["account_name"]

    try:
        error_code = json_response["errorCode"]
        embed = await stw.post_error_possibilities(ctx, client, "research", acc_name, error_code,
                                                   verbiage_action="research", desired_lang=desired_lang)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return None, None
    except:
        pass

    try:
        current_levels = json_response['profileChanges'][0]['profile']['stats']['attributes']['research_levels']
    except Exception as e:
        # account may not have stw
        try:
            # check if account has daily reward stats, if not, then account doesn't have stw
            check_stw = json_response['profileChanges'][0]['profile']['stats']['attributes']['daily_rewards']
            try:
                logger.warning(f"Error: {e} | no research stat, but daily reward; assuming zero research stats. | {stw.truncate(json_response['profileChanges'][0]['profile']['stats']['attributes'])}")
            except:
                logger.warning(f"Error: {e} | no research stat, but daily reward; assuming zero research stats. | {stw.truncate(json_response)}")
            # assume all stats are at 0 because idk it cant be max surely not, the stats are here for max so...
            # dippy note here - after some investigation, this condition is entered when the stats are missing (due to being level 0 / not unlocked yet)
            # it should be when all stats are missing, but this is entered when 1 stat is missing, we should check which stats are missing and assign to level 0
            # TODO: This condition may be entered when research is not unlocked yet
            current_levels = {'fortitude': 0, 'offense': 0, 'resistance': 0, 'technology': 0}
            pass
        except:
            # account doesn't have stw
            error_code = "errors.com.epicgames.fortnite.check_access_failed"
            embed = await stw.post_error_possibilities(ctx, client, "research", acc_name, error_code,
                                                       verbiage_action="res", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return None, None

    # I'm not too sure what happens here but if current_levels doesn't exist im assuming its at maximum.
    # I'll assume it's minimum
    proc_max = False
    try:
        if current_levels["offense"] + current_levels["fortitude"] + current_levels["resistance"] + current_levels[
            "technology"] == 480:
            proc_max = True
    except:
        for stat in ["offense", "fortitude", "resistance", "technology"]:
            if stat not in current_levels:
                current_levels[stat] = 0

        pass  # yeah same i pass

    return current_levels, proc_max


class Research(ext.Cog):
    """
    Cog for the research related commands.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        self.token_guid_research = "Token_collectionresource_nodegatetoken01"
        self.item_templateid_research = "Token:collectionresource_nodegatetoken01"

    def check_for_research_points_item(self, query_json):
        """
        Check if the research points item is in the inventory.

        Args:
            query_json: The query json object.

        Returns:
            tuple: the research points item and key, otherwise None
        """
        # Yes you can use the itemGuid from the notifications response from the claimcollectedresources response
        # but, you do not get notifications when you are at maximum research points!
        items = query_json['profileChanges'][0]['profile']['items']

        for key, item in items.items():
            try:
                if item['templateId'] == f"{self.item_templateid_research}":
                    return item, key
            except:
                pass

        return None

    def check_for_research_guid_key(self, query_json):
        """
        Check if the research points item is in the inventory.

        Args:
            query_json: The query json object.

        Returns:
            tuple: the research points key, otherwise None
        """
        items = query_json['profileChanges'][0]['profile']['items']
        for key, item in items.items():
            try:
                if item['templateId'] == f"CollectedResource:{self.token_guid_research}":
                    return key
            except:
                pass

        return None

    async def research_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the research command.

        Args:
            ctx: The context object.
            authcode: The authcode object.
            auth_opt_out: The auth_opt_out object.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        res_green = self.client.colours["research_green"]
        crown_yellow = self.client.colours["crown_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "research", authcode, auth_opt_out, True,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        current_research_statistics_request = await stw.profile_request(self.client, "query", auth_info[1])
        json_response = orjson.loads(await current_research_statistics_request.read())
        current_levels, proc_max = await research_query(ctx, self.client, auth_info, final_embeds, json_response,
                                                        desired_lang)
        # TODO: handle proc_max properly i.e. skip redundant steps, hide buttons, etc.
        if current_levels is None:
            return
        # if proc_max:
        #     crown_yellow = self.client.colours["crown_yellow"]
        #     embed = discord.Embed(
        #         title=await stw.add_emoji_title(self.client, "Max", "crown"),
        #         description=("\u200b\n"
        #                      "Congratulations, you have **maximum** FORT stats.\n\u200b\n\u200b"),
        #         colour=crown_yellow
        #     )
        #
        #     await add_fort_fields(self.client, embed, current_levels, True)
        #     embed = await stw.set_thumbnail(self.client, embed, "crown")
        #     embed = await stw.add_requested_footer(ctx, embed)
        #     final_embeds.append(embed)
        #     await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        #     return

        # assign variables for error embeds
        support_url = self.client.config["support_url"]
        acc_name = auth_info[1]["account_name"]

        # Find research guid to post to required for ClaimCollectedResources json
        research_guid_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_guid_key, json_response))
        # print("research guid: ", research_guid_check)
        if research_guid_check[0] is None:
            logger.warning("errors.stwdaily.failed_guid_research encountered:", stw.truncate(json_response))
            error_code = "errors.stwdaily.failed_guid_research"
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                       verbiage_action="res", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        research_guid = research_guid_check[0]
        pass

        current_research_statistics_request = await stw.profile_request(self.client, "resources", auth_info[1],
                                                                        json={"collectorsToClaim": [research_guid]})
        json_response = orjson.loads(await current_research_statistics_request.read())
        # print("current research stats: ", stw.truncate(json_response))

        try:
            error_code = json_response["errorCode"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                       verbiage_action="res", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        except:
            pass

        # Get total points
        total_points_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_points_item, json_response))
        if total_points_check[0] is None:
            logger.warning("errors.stwdaily.failed_total_points encountered:", stw.truncate(json_response))
            error_code = "errors.stwdaily.failed_total_points"
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                       verbiage_action="res", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

        total_points, rp_token_guid = total_points_check[0][0], total_points_check[0][1]

        # I do believe that after some testing if you are at le maximum research points
        # you do not receive notifications so this must be wrapped in a try statement
        # assume that research points generated is none since it is at max!
        # the above statement is false, this has now been fixed :)
        research_points_claimed = None
        try:
            research_feedback, check = json_response["notifications"], False
            for notification in research_feedback:
                if notification["type"] == "collectedResourceResult":
                    research_feedback, check = notification, True
                    break

            if not check:
                error_code = "errors.stwdaily.failed_get_collected_resource_type"
                embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                           verbiage_action="res", desired_lang=desired_lang)
                final_embeds.append(embed)
                await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
                return

            available_research_items, check = research_feedback["loot"]["items"], False
            for research_item in available_research_items:
                try:
                    if research_item["itemType"] == self.item_templateid_research:
                        research_item, check = research_item, True
                        break
                except:
                    pass

            if not check:
                error_code = "errors.stwdaily.failed_get_collected_resource_item"
                embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                           verbiage_action="res", desired_lang=desired_lang)
                final_embeds.append(embed)
                await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
                return
            # this variable might be referenced before assignment hmm
            research_points_claimed = research_item['quantity']
        except Exception as e:
            if 'notifications' in str(e):
                logger.debug("No notifications found in json_response")
            else:
                logger.info("Error in research_points_claimed: ", str(e))

        # Create the embed for displaying nyaa~

        if research_points_claimed is not None:
            if research_points_claimed == 1:
                claimed_text = f"{stw.I18n.get('research.embed.claim.claimed.singular', desired_lang, f'{research_points_claimed:,}')}\n\u200b"
            else:
                claimed_text = f"{stw.I18n.get('research.embed.claim.claimed.plural', desired_lang, f'{research_points_claimed:,}')}\n\u200b"
        else:
            # TODO: add info about player's research storage limit / regen time (wallet)
            claimed_text = f"{stw.I18n.get('research.embed.claim.romania', desired_lang)}\n\u200b"
        max_fort_string = f"{stw.I18n.get('research.embed.maximumstats', desired_lang)}\n"
        total_points_quantity = total_points["quantity"]
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get('research.embed.title', desired_lang),
                                            "crown" if proc_max else "research_point"),
            description=(f'\u200b\n{max_fort_string if proc_max else ""}'
                         f'{stw.I18n.get("research.embed.description.singular", desired_lang, f"{total_points_quantity:,}") if total_points["quantity"] == 1 else stw.I18n.get("research.embed.description.plural", desired_lang, f"{total_points_quantity:,}")}\n\u200b\n\u200b'),
            colour=crown_yellow if proc_max else res_green
        )

        embed = await add_fort_fields(self.client, embed, current_levels, desired_lang)
        embed.add_field(name=f"\u200b", value=claimed_text)
        embed = await stw.set_thumbnail(self.client, embed, "crown" if proc_max else "research")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)

        final_embeds.append(embed)
        research_view = ResearchView(self.client, ctx, auth_info, ctx.author, total_points, current_levels,
                                     rp_token_guid,
                                     embed, desired_lang)
        research_view.message = await stw.slash_edit_original(ctx, auth_info[0], final_embeds, view=research_view)

    @ext.command(name='research',
                 aliases=['rse', 'des', 'rgesearch', 'r4es', 'reas', 'resd', 'resa', 're', 're4s', 'researtch',
                          're3search', 'rexearch', 'resw', 'rfesearch', 'researhc', 'rea', 'rers', 'reswarch',
                          'resdarch', 'resarch', 'redearch', 'researchh', 'researfh', 'reseach', 'reseatrch',
                          'rsesearch', 'r3s', 'rews', 'reseadrch', 'ers', 'rewearch', 'rese3arch', 'rssearch',
                          'gesearch', 'esearch', 'resezrch', 're3s', 'reseearch', 'reasearch', 'rew', 'reds', 'rses',
                          'researcyh', 'researdh', 'res4arch', 'ressearch', '5esearch', 'rezearch', 'reseatch',
                          'researcfh', 'rrsearch', 'ees', 'researcgh', 'rseearch', 'reesarch', 'resaearch', 'resear4ch',
                          'rds', 'rewsearch', 'tresearch', 'resefarch', 'reseaarch', 'researcxh', '4res', 'resx',
                          'resesrch', 'resexarch', 'r4search', 'r4esearch', '4es', 'rresearch', 'resrearch', 'rs',
                          'resea4ch', 'fes', 'gresearch', 'reseagch', 'es', 'r5es', 'rsearch', 'researvh', 'r3esearch',
                          'res4earch', 'researcjh', 'researech', 'researchn', 'resesarch', 'researcy', 'researrch',
                          'resfearch', 'researcj', 'reseasrch', 'resear5ch', 'rez', 'r3es', 'r3search', 'researc',
                          'res', 'researchj', 'refsearch', 'dres', 'rex', 'researchg', 'rrs', 'researchu', 'redsearch',
                          'rersearch', 'reseafch', 'reesearch', 'researcvh', 'eesearch', 'resezarch', '5research',
                          'res3earch', 'resewarch', 'fesearch', 'reearch', 'resxearch', 'rwes', 'rees', 'reswearch',
                          'reseaxrch', 'researcuh', 'refs', 'reseaqrch', 'resea4rch', 'rfs', 'fres', 'researgch',
                          'gres', 'reeearch', 'resea5ch', 'rtes', 'resexrch', 'rws', 'tres', 'researchy', 'researcnh',
                          'rdesearch', 'researcch', 'rexs', 'rges', 'reserch', 'resaerch', 'rese4arch', 'reserarch',
                          'researcu', 'researcbh', 'fresearch', 'rdes', 'rwesearch', 'rexsearch', 'desearch',
                          'reseqarch', 'dresearch', 'rezsearch', 'researchb', 'reseaech', 'eresearch', 'researxch',
                          'researdch', 'r4s', 'rfsearch', 'rres', 'reseagrch', 'reseaerch', 'ress', 'resaesaer',
                          'reseqrch', 'rfes', '4esearch', 'rwsearch', 'resea5rch', 'rtesearch', 'researfch', '5res',
                          'researcdh', 'eres', 'ressarch', 'resfarch', 'reseadch', 'rss', 'reszearch', 'reserach',
                          'reach', 'ersearch', 'reseazrch', 'rdsearch', 'ges', 'researcn', 'researcg', '4research',
                          'researcb', 'ree', 'resz', 'reseacrh', 'red', 'resdearch', 'reseawrch', '5es', 'rese',
                          'reseafrch', 'reaearch', 'researh', 'tesearch', 'researxh', 'r5esearch', 'resrarch',
                          'researvch', 'res3arch', 'resewrch', 'rezs', 're4search', 'tes', 'resedarch', '/res', '/r',
                          '/research', 'resea', 'resear', 'lab', 'fortitude', 'fort', 'upgrade', 'tree',
                          'navorsing', 'بحث', 'изследвания', 'গবেষণা', 'recerca', 'výzkum', 'forskning', 'Forschung',
                          'έρευνα', 'investigación', 'uurimine', 'پژوهش', 'tutkimusta', 'recherche', 'સંશોધન',
                          'bincike', 'מחקר', 'शोध करना', 'istraživanje', 'kutatás', 'penelitian', 'ricerca', 'リサーチ',
                          '연구', 'tyrimai', 'pētījumiem', 'संशोधन', 'penyelidikan', 'onderzoek', 'ਖੋਜ', 'badania',
                          'pesquisa', 'cercetare', 'исследование', 'výskumu', 'истраживања', 'utafiti', 'ஆராய்ச்சி',
                          'పరిశోధన', 'วิจัย', 'araştırma', 'дослідження', 'تحقیق', 'nghiên cứu', '研究', 'ries', 'kres',
                          'qres', 'sres', 'rec', 'resj', 'mres', 'resy', 'rev', 'resr', 'bes', 'vres', 'req', 'les',
                          'rks', 'resn', 'reh', 'rcs', 'rgs', 'rjs', 'ret', 'ires', 'ves', 'raes', 'rej',
                          'resp', 'rejs', 'roes', 'bres', 'ies', 'wes', 'ref', 'pes', 'rqes', 'resq', 'reb', 'rus',
                          'ren', 'jes', 'xres', 'aes', 'rms', 'ces', 'oes', 'resc', 'rjes', 'ores', 'reis', 'yes',
                          'reus', 'rems', 'reu', 'resl', 'resb', 'ues', 'rxes', 'ryes', 'rues', 'regs', 'ses', 'zes',
                          'resv', 'reo', 'resg', 'rhes', 'rbes', 'reos', 'reys', 'rehs', 'kes', 'wres', 'rys',
                          'rkes', 'rei', 'ris', 'reso', 'resf', 'ros', 'lres', 'resu', 'mes', 'ras', 'rek', 'hes',
                          'rnes', 'rps', 'resk', 'rns', 'revs', 'rels', 'rts', 'ares', 'cres', 'resi', 'resm', 'yres',
                          'nres', 'rvs', 'rets', 'rebs', 'xes', 'jres', 'qes', 'rmes', 'hres', 'rer', 'rles', 'rep',
                          'rxs', 'resh', 'reps', 'rel', 'rzs', 'reks', 'reg', 'rest', 'rces', 'rves', 'rzes', 'reqs',
                          'zres', 'rens', 'pres', 'rbs', 'recs', 'rey', 'rqs', 'rpes', 'ures', 'rhs', '3es', '#es',
                          '$es', '%es', 'r2s', 'r$s', 'r#s', 'r@s', 'reseacrch', 'cesearch', 'reseaprch', 'pesearch',
                          'sresearch', 'resjarch', 'rhesearch', 'researcph', 'regearch', 'reseaych', 'reseabrch',
                          'researich', 'relearch', 'reseaqch', 'reseerch', 'reuearch', 'reseakrch', 'rtsearch',
                          'researmch', 'researco', 'rmsearch', 'resnearch', 'researcz', 'resehrch', 'rxesearch',
                          'researsh', 'yresearch', 'rzsearch', 'resjearch', 'resbarch', 'rekearch', 'resyarch',
                          'vesearch', 'resegrch', 'reseparch', 'researchc', 'resqearch', 'qesearch', 'reseiarch',
                          'rosearch', 'researah', 'reseasch', 'researcf', 'vresearch', 'researhch', 'resealch',
                          'reselarch', 'researuch', 'hresearch', 'reslearch', 'researpch', 'resetrch', 'rzesearch',
                          'jesearch', 'researceh', 'ruesearch', 'rkesearch', 'researph', 'resmarch', 'reseabch',
                          'rvsearch', 'resnarch', 'rxsearch', 'reseamch', 'researyh', 'iesearch', 'retearch',
                          'resuearch', 'reseajch', 'resecrch', 'researnh', 'researcw', 'rehsearch',
                          'reseapch', 'resparch', 'sesearch', 'researbch', 'resegarch', 'reseaxch', 'reseavch',
                          'reisearch', 'aesearch', 'rebearch', 'resxarch', 'researych', 'researmh', 'resiearch',
                          'reseoarch', 'researcr', 'researuh', 'hesearch', 'reseaich', 'researqh', 'lresearch',
                          'reseuarch', 'reseavrch', 'researchz', 'resgearch', 'kesearch', 'reseanrch', 'researkch',
                          'aresearch', 'risearch', 'reseanch', 'researjh', 'remsearch', 'mresearch', 'resyearch',
                          'nesearch', 'xesearch', 'mesearch', 'resefrch', 'researchr', 'reseajrch', 'researcx',
                          'reseaach', 'recearch', 'rbesearch', 'researhh', 'researcp', 'rnesearch', 'respearch',
                          'researcd', 'researchk', 'reosearch', 'resekrch', 'revearch', 'restarch', 'rmesearch',
                          'roesearch', 'researcrh', 'researcth', 'uresearch', 'rlsearch', 'researrh', 'researci',
                          'resedrch', 'researlch', 'researchm', 'researchv', 'revsearch', 'researlh', 'reiearch',
                          'resebrch', 'researcq', 'researzh', 'repsearch', 'qresearch', 'rpesearch', 'oresearch',
                          'rusearch', 'researchp', 'lesearch', 'researcah', 'iresearch', 'cresearch', 'resenrch',
                          'researcha', 'restearch', 'regsearch', 'researct', 'resenarch', 'reseahrch', 'rescearch',
                          'reseaurch', 'researck', 'researca', 'researchx', 'oesearch', 'rysearch', 'rhsearch',
                          'rqesearch', 'repearch', 'wresearch', 'resuarch', 'raesearch', 'reyearch', 'reseyarch',
                          'reseharch', 'reserrch', 'reseawch', 'researcmh', 'researeh', 'uesearch', 'researchf',
                          'rebsearch', 'resejrch', 'reseazch', 'reqearch', 'rpsearch', 'reqsearch', 'besearch',
                          'researchs', 'reseakch', 'researczh', 'rejsearch', 'ryesearch', 'retsearch', 'researih',
                          'reseayrch', 'rensearch', 'rejearch', 'renearch', 'resoearch', 'reseahch', 'researchw',
                          'researcl', 'researcho', 'presearch', 'jresearch', 'nresearch', 'researcoh', 'reseauch',
                          'rehearch', 'researwch', 'resecarch', 'resmearch', 'rvesearch', 'reseaoch', 'reseprch',
                          'researwh', 'rqsearch', 'researcih', 'resevrch', 'researjch', 'rgsearch', 'relsearch',
                          'reusearch', 'reseorch', 'resebarch', 'researcm', 'researnch', 'reoearch', 'resoarch',
                          'researoch', 'researcv', 'reseaorch', 'researkh', 'xresearch', 'resqarch', 'yesearch',
                          'rerearch', 'researzch', 'researcs', 'rasearch', 'bresearch', 'researcht', 'researach',
                          'reseacch', 'remearch', 'resejarch', 'researqch', 'refearch', 'rescarch', 'resaarch',
                          'researchd', 'reskarch', 'researcsh', 'researche', 'kresearch', 'zresearch', 'reseurch',
                          'reseamrch', 'recsearch', 'reslarch', 'researth', 'researgh', 'resbearch', 'resvarch',
                          'researsch', 'rbsearch', 'rcesearch', 'researce', 'resemarch', 'rnsearch', 'reseairch',
                          'researchi', 'reszarch', 'researchq', 'reskearch', 'riesearch', 'rjsearch', 'rjesearch',
                          'resvearch', 'resemrch', 'reseyrch', 'researcqh', 'researclh', 'resharch', 'researcc',
                          'rksearch', 'reysearch', 'zesearch', 'researbh', 'researckh', 'wesearch', 'reseirch',
                          'resealrch', 'reshearch', 'resiarch', 'resekarch', 'reselrch', 'rcsearch', 'resetarch',
                          'researoh', 'reksearch', 'resgarch', 'resevarch', 'researcwh', 'researchl', 'rlesearch',
                          '3esearch', '#esearch', '$esearch', '%esearch', 'r2search', 'r$search', 'r#search',
                          'r@search', 'res2arch', 'res$arch', 'res#arch', 'res@arch', 'resea3ch', 'resea#ch',
                          'resea$ch', 'resea%ch', 'rscrh', 'rjsrch', 'rsrcfh', 'gsrch', 'rsrhc', 'srrch', 'rsch',
                          'esrch', 'wsrch', 'rsjrch', 'rrch', 'rrsch', 'rurch', 'rosrch', 'rsrh', 'rskrch', 'csrch',
                          'rskch', 'rsrmch', 'rsach', 'rsxch', 'srch', 'rsrcc', 'rsrdch', 'rbsrch', 'rsrc', 'rsrca',
                          'rsmrch', 'rsroh', 'rsrcb', 'vrsrch', 'rsrcbh', 'rsrct', 'rsrchi', 'rslrch', 'rsrchf',
                          'rsrchh', 'ysrch', 'rsreh', 'rsrcv', 'rsrclh', 'fsrch', 'rnsrch', 'rsrjh', 'rfsrch', 'rsrcth',
                          'rsrcq', 'osrch', 'rsvrch', 'rsrcph', 'rsrzh', 'ursrch', 'rsrcch', 'dsrch', 'rsrchg', 'rsrmh',
                          'rsruch', 'rsirch', 'rksrch', 'rwrch', 'rsrcj', 'rsrcp', 'rzsrch', 'rsrbch', 'jrsrch',
                          'rsrsch', 'rfrch', 'brsrch', 'rsdrch', 'rsrsh', 'rsrvh', 'rsjch', 'rvsrch', 'irsrch', 'rsrch',
                          'rsrach', 'rswch', 'rsrcvh', 'rsrqch', 'rsrchp', 'rsrdh', 'psrch', 'rsrcrh', 'rsrwh',
                          'rsrgch', 'rsrcu', 'rkrch', 'rqrch', 'rtrch', 'rsrxh', 'rsrcha', 'rsuch', 'rsdch', 'rsrcf',
                          'rsrckh', 'rsrnh', 'rprch', 'rsrcs', 'rsrchv', 'rhrch', 'rsrbh', 'drsrch', 'rrrch', 'ssrch',
                          'krsrch', 'rsych', 'rsrcl', 'rsrchy', 'rserch', 'rirch', 'rstch', 'rsrxch', 'rsrpch', 'rsoch',
                          'rsrchu', 'rqsrch', 'rsfch', 'hrsrch', 'tsrch', 'rcsrch', 'rsrchc', 'rsrcm', 'nsrch', 'usrch',
                          'lsrch', 'rsrcoh', 'ersrch', 'rdsrch', 'rsruh', 'rstrch', 'arsrch', 'hsrch', 'rsrfh',
                          'rsorch', 'rsrcgh', 'rsrech', 'rorch', 'rsxrch', 'rsrwch', 'rszch', 'rrsrch', 'rsrcyh',
                          'lrsrch', 'rsnch', 'rsryh', 'rsrchq', 'rbrch', 'rsrqh', 'rsrrch', 'wrsrch', 'rsrcht',
                          'rsroch', 'rsrchb', 'rsrcsh', 'rsrcmh', 'rsmch', 'rsrcqh', 'rsrchs', 'rnrch', 'rsrkch',
                          'rlsrch', 'rsvch', 'rgrch', 'rwsrch', 'rsrcxh', 'resrch', 'rsich', 'risrch', 'rpsrch',
                          'rsnrch', 'rdrch', 'rsyrch', 'rsrtch', 'frsrch', 'rsrcr', 'crsrch', 'isrch', 'vsrch',
                          'rmsrch', 'rspch', 'rsrchx', 'rszrch', 'rtsrch', 'rsrjch', 'rsrcz', 'trsrch', 'rsbch',
                          'rsrlch', 'rsrcn', 'rsrcah', 'rsrah', 'yrsrch', 'srsrch', 'rsrgh', 'rsrvch', 'rsrcy', 'rsech',
                          'rsrcwh', 'rusrch', 'rsrchr', 'zsrch', 'rshch', 'rsrhh', 'rsrcih', 'rsrcnh', 'rsfrch',
                          'rsrcg', 'rsrce', 'rmrch', 'nrsrch', 'xrsrch', 'rsrph', 'rsrcho', 'msrch', 'rsrcjh', 'rsrci',
                          'ryrch', 'rslch', 'rsrth', 'rsqrch', 'rsrceh', 'rjrch', 'rswrch', 'prsrch', 'rvrch', 'jsrch',
                          'rscrch', 'rsrchw', 'rsrich', 'rsrchl', 'xsrch', 'rzrch', 'rsgch', 'rssrch', 'rshrch',
                          'rsrchz', 'rsrzch', 'rasrch', 'bsrch', 'rysrch', 'rsrih', 'orsrch', 'rsrcd', 'rxrch', 'rsrck',
                          'rxsrch', 'qrsrch', 'rcrch', 'rarch', 'rlrch', 'rerch', 'rsrcx', 'rgsrch', 'grsrch', 'rsrcw',
                          'qsrch', 'rhsrch', 'rsrcuh', 'rsrnch', 'rscch', 'rsarch', 'ksrch', 'rsrkh', 'rssch', 'rsurch',
                          'rsrchj', 'rsrco', 'rsrczh', 'rsrrh', 'rsbrch', 'rsrfch', 'rsrcdh', 'rsrchk', 'rsrchn',
                          'rsrlh', 'rsgrch', 'zrsrch', 'rsqch', 'rsrchd', 'rsrche', 'rsrych', 'asrch', 'rsrchm',
                          'mrsrch', 'rsrhch', 'rsprch', '3srch', '4srch', '5srch', '#srch', '$srch', '%srch', 'rs3ch',
                          'rs4ch', 'rs5ch', 'rs#ch', 'rs$ch', 'rs%ch', 'alb', 'lb', 'loab', 'labw', 'lau', 'la', 'lba',
                          'lhb', 'lib', 'labx', 'blab', 'yab', 'fab', 'xab', 'lxb', 'lao', 'jab', 'lhab', 'laz', 'lan',
                          'alab', 'lag', 'aab', 'cab', 'zab', 'ab', 'lgab', 'iab', 'lvb', 'lbb', 'laa', 'labo',
                          'kab', 'laeb', 'lvab', 'gab', 'lpb', 'laj', 'klab', 'laib', 'labs', 'pab', 'lakb',
                          'lnb', 'laf', 'lar', 'lqb', 'ldb', 'lap', 'wlab', 'lac', 'lwb', 'nab', 'law', 'lah', 'llab',
                          'larb', 'lkb', 'labf', 'labk', 'mlab', 'lcab', 'glab', 'ldab', 'labi', 'lal', 'lxab',
                          'lkab', 'lzb', 'qab', 'ulab', 'labq', 'wab', 'lapb', 'lrab', 'lai', 'tlab', 'lqab', 'lsb',
                          'mab', 'ylab', 'labv', 'vlab', 'elab', 'labb', 'sab', 'lyb', 'tab', 'dlab', 'lajb', 'uab',
                          'lagb', 'ilab', 'ljab', 'dab', 'lafb', 'bab', 'lad', 'lamb', 'laab', 'lay', 'lacb', 'labd',
                          'lrb', 'slab', 'labt', 'vab', 'laub', 'hab', 'lanb', 'laqb', 'lfb', 'oab', 'lcb', 'lbab',
                          'lak', 'olab', 'labn', 'liab', 'labm', 'lat', 'labr', 'lae', 'nlab', 'lgb', 'lnab',
                          'labh', 'ltab', 'lwab', 'lav', 'ltb', 'labu', 'lob', 'lfab', 'lalb', 'laba', 'lzab', 'luab',
                          'lawb', 'ljb', 'hlab', 'leab', 'lmb', 'llb', 'eab', 'lavb', 'lsab', 'labz', 'lazb', 'laq',
                          'lasb', 'latb', 'zlab', 'lub', 'labp', 'jlab', 'clab', 'laob', 'laxb', 'labc', 'lahb', 'flab',
                          'layb', 'labj', 'qlab', 'leb', 'lyab', 'plab', 'laby', 'lax', 'rlab', 'labe', 'labg', 'ladb',
                          'labl', 'lpab', 'xlab', ';ab', '/ab', '.ab', ',ab', '?ab', '>ab', '<ab', 'ofrtitude',
                          'fortitdue', 'forvtitude', 'foratitude', 'fortiude', 'fortitudve', 'forittude', 'forttude',
                          'fortzitude', 'fortitufe', 'fotitude', 'fortwtude', 'foritude', 'fortitubde', 'fortitudb',
                          'fortituee', 'fortitud', 'forttiude', 'forztitude', 'ortitude', 'fortjtude', 'fortitdude',
                          'fortidude', 'gortitude', 'fortinude', 'fortituze', 'fortitudem', 'frotitude', 'fortttude',
                          'fortieude', 'forstitude', 'fortitue', 'forfitude', 'fortitudet', 'fortitade', 'portitude',
                          'fortetude', 'frtitude', 'fotritude', 'fortitusde', 'fortptude', 'fortitxde', 'fortitsde',
                          'fortiitude', 'fortitudue', 'fortituqe', 'fortxtude', 'afortitude', 'fortitjde', 'fortitde',
                          'fortitudz', 'fovtitude', 'fokrtitude', 'fortituke', 'foraitude', 'fortitudd', 'fortiutde',
                          'wfortitude', 'fortitued', 'fortitudef', 'fortibude', 'fortibtude', 'forbitude', 'fortitmde',
                          'forteitude', 'fortitudse', 'forhitude', 'fortidtude', 'fortiotude', 'fnrtitude',
                          'fortituqde', 'fortitudes', 'foqtitude', 'fortituhde', 'fortktude', 'fortaitude',
                          'fortitxude', 'fortitudej', 'fortiltude', 'forftitude', 'fofrtitude', 'foztitude',
                          'foktitude', 'fortvtude', 'fortitudep', 'xfortitude', 'bfortitude', 'fortikude', 'fortiwude',
                          'fortiutude', 'fortitudye', 'fortitide', 'fortituue', 'ftortitude', 'fortitudoe',
                          'fortitudel', 'fortiture', 'fornitude', 'fortiteude', 'fobtitude', 'folrtitude', 'fortitukde',
                          'fottitude', 'uortitude', 'forjitude', 'fortitbude', 'fortitudw', 'fortistude', 'fortitmude',
                          'fortijtude', 'fortbitude', 'ofortitude', 'fortitzude', 'fortitvde', 'fmrtitude',
                          'kfortitude', 'fortitudze', 'fortqitude', 'fqortitude', 'fortitnude', 'fortipude',
                          'fyortitude', 'foroitude', 'foatitude', 'fortityde', 'fortiuude', 'fortijude', 'fortiqude',
                          'fodrtitude', 'fortitudn', 'fortituxe', 'fortimude', 'nfortitude', 'bortitude', 'fortitqde',
                          'foirtitude', 'fkrtitude', 'fortituae', 'fnortitude', 'fowrtitude', 'forxtitude',
                          'forthitude', 'fortitpude', 'fortitfde', 'fortituxde', 'fortitudj', 'fvrtitude', 'fortitudu',
                          'foetitude', 'fortituye', 'forqitude', 'cortitude', 'formtitude', 'forkitude', 'fortrtude',
                          'kortitude', 'fortitdde', 'fortituide', 'fortotude', 'fortitudde', 'fortnitude', 'fortlitude',
                          'forritude', 'fortgitude', 'fortitgde', 'fortitugde', 'dfortitude', 'foxtitude', 'fortitudfe',
                          'footitude', 'ftrtitude', 'fortittde', 'fortitudhe', 'fortitudxe', 'forzitude', 'feortitude',
                          'fozrtitude', 'sfortitude', 'fortytude', 'fortirtude', 'fortmtude', 'fbortitude', 'fortitcde',
                          'fsrtitude', 'fortiiude', 'fjortitude', 'nortitude', 'fortitudeq', 'fortitudeb', 'fwortitude',
                          'fortitudee', 'fhortitude', 'dortitude', 'forvitude', 'forbtitude', 'fortitucde',
                          'fortitudpe', 'fortltude', 'foutitude', 'fowtitude', 'fortitudc', 'fortitlde', 'fortctude',
                          'fortitudek', 'fortituvde', 'fortitrde', 'fortitudeu', 'mfortitude', 'fortpitude',
                          'fortitupde', 'fortitumde', 'mortitude', 'fortjitude', 'fhrtitude', 'foititude', 'zortitude',
                          'aortitude', 'fortatude', 'fortitudle', 'fortiytude', 'fortituhe', 'fortditude', 'fortitudev',
                          'fomrtitude', 'forltitude', 'fortitgude', 'foartitude', 'fzortitude', 'fojrtitude',
                          'fortiwtude', 'fortituse', 'lfortitude', 'foxrtitude', 'fortitfude', 'fortfitude',
                          'fortituie', 'fortitulde', 'fortitkude', 'fortioude', 'fortitujde', 'forrtitude',
                          'flortitude', 'forititude', 'ufortitude', 'fortitoude', 'fortwitude', 'fortilude',
                          'fortitudei', 'foqrtitude', 'fortitkde', 'forwtitude', 'fortietude', 'fortiyude',
                          'forqtitude', 'vfortitude', 'fohtitude', 'fyrtitude', 'fortitunde', 'fortitpde', 'fortitutde',
                          'fontitude', 'fvortitude', 'fortitwude', 'fojtitude', 'forktitude', 'jfortitude', 'foctitude',
                          'fortitudge', 'yfortitude', 'foortitude', 'fortituder', 'fohrtitude', 'foptitude',
                          'fortitudce', 'fortqtude', 'forytitude', 'fxortitude', 'fsortitude', 'fortyitude',
                          'fortitudi', 'fortitnde', 'fortdtude', 'fortitupe', 'fortitudv', 'fortictude', 'fortmitude',
                          'forticude', 'formitude', 'fortitudp', 'fortitudx', 'fgrtitude', 'yortitude', 'fortitede',
                          'fortituode', 'fortituje', 'fortizude', 'focrtitude', 'foftitude', 'fortitudl', 'forpitude',
                          'fqrtitude', 'fortkitude', 'fortituude', 'fortitudm', 'fartitude', 'forgitude', 'forlitude',
                          'fortitute', 'fortritude', 'fotrtitude', 'fortitudte', 'vortitude', 'fortityude',
                          'fortituden', 'fortiaude', 'foryitude', 'fortituge', 'rfortitude', 'forsitude', 'oortitude',
                          'fortithude', 'flrtitude', 'fortitudk', 'fportitude', 'fortitudea', 'fostitude', 'fortitudre',
                          'fomtitude', 'ifortitude', 'fortitqude', 'fdortitude', 'fortitsude', 'eortitude',
                          'fortitudwe', 'fortitudke', 'fortitudo', 'fortitaude', 'zfortitude', 'fprtitude',
                          'fortiztude', 'sortitude', 'foriitude', 'fortituoe', 'fortitudae', 'fortitiude', 'fortithde',
                          'foruitude', 'fortitudt', 'tfortitude', 'fortoitude', 'jortitude', 'fortitrude', 'forotitude',
                          'lortitude', 'fortitudq', 'fodtitude', 'fortituwe', 'fortsitude', 'fortitune', 'forthtude',
                          'forutitude', 'fkortitude', 'fortitudeg', 'fortitudex', 'fuortitude', 'fortirude',
                          'foretitude', 'fortittude', 'ffortitude', 'fortuitude', 'fortitjude', 'hortitude',
                          'fortitcude', 'fortitudme', 'fortifude', 'fortituede', 'foltitude', 'fortitudey',
                          'fourtitude', 'fwrtitude', 'fcortitude', 'fovrtitude', 'fortituce', 'fortiftude',
                          'forjtitude', 'fortitudeh', 'fortbtude', 'forctitude', 'fortitube', 'fortutude', 'fortitudje',
                          'fortitudf', 'frortitude', 'fortitudqe', 'fortntude', 'foyrtitude', 'fortituda', 'fortituyde',
                          'fortituade', 'furtitude', 'fortvitude', 'foprtitude', 'frrtitude', 'fortitufde', 'fortitudg',
                          'forptitude', 'fosrtitude', 'foreitude', 'fortitudew', 'fortisude', 'forttitude',
                          'hfortitude', 'fortftude', 'fortiatude', 'qortitude', 'fortgtude', 'fortztude', 'fortituwde',
                          'forwitude', 'forcitude', 'wortitude', 'fxrtitude', 'forntitude', 'rortitude', 'fortituded',
                          'fortivtude', 'fortigude', 'fortitume', 'cfortitude', 'fortintude', 'fortihude', 'forxitude',
                          'fdrtitude', 'xortitude', 'fgortitude', 'fortxitude', 'forditude', 'fortivude', 'fortiqtude',
                          'fortitvude', 'fortitwde', 'fortitudne', 'fortitudr', 'fortitudy', 'fortitule', 'firtitude',
                          'fobrtitude', 'fortituve', 'fortihtude', 'fbrtitude', 'qfortitude', 'foytitude', 'fortcitude',
                          'gfortitude', 'fortituds', 'fortituzde', 'fertitude', 'fortitudez', 'fordtitude',
                          'faortitude', 'fortitode', 'forgtitude', 'fzrtitude', 'fortiktude', 'fjrtitude', 'fortigtude',
                          'fortimtude', 'fcrtitude', 'fortitudeo', 'fortitlude', 'tortitude', 'foertitude',
                          'fortiturde', 'fmortitude', 'fortitudec', 'fortstude', 'fortitbde', 'pfortitude',
                          'forhtitude', 'fogrtitude', 'fiortitude', 'fortitudbe', 'fortixtude', 'efortitude',
                          'fonrtitude', 'fortixude', 'iortitude', 'fogtitude', 'fortiptude', 'ffrtitude', 'fortitudie',
                          'fortitzde', 'fortitudh', 'f8rtitude', 'f9rtitude', 'f0rtitude', 'f;rtitude', 'f*rtitude',
                          'f(rtitude', 'f)rtitude', 'fo3titude', 'fo4titude', 'fo5titude', 'fo#titude', 'fo$titude',
                          'fo%titude', 'for4itude', 'for5itude', 'for6itude', 'for$itude', 'for%itude', 'for^itude',
                          'fort7tude', 'fort8tude', 'fort9tude', 'fort&tude', 'fort*tude', 'fort(tude', 'forti4ude',
                          'forti5ude', 'forti6ude', 'forti$ude', 'forti%ude', 'forti^ude', 'fortit6de', 'fortit7de',
                          'fortit8de', 'fortit^de', 'fortit&de', 'fortit*de', 'fortitud4', 'fortitud3', 'fortitud2',
                          'fortitud$', 'fortitud#', 'fortitud@', 'ort', 'wfort', 'fopt', 'tfort', 'ofrt', 'forvt',
                          'for', 'fozrt', 'fotr', 'fot', 'fqort', 'forot', 'fmort', 'fortm', 'feort', 'foart', 'frt',
                          'foht', 'ifort', 'formt', 'frot', 'fwort', 'ftort', 'fomt', 'forct', 'fortv', 'forte', 'fodt',
                          'fwrt', 'xfort', 'mfort', 'fortw', 'fart', 'nort', 'fortu', 'fport', 'foqrt', 'forq', 'hort',
                          'fortn', 'forut', 'fyort', 'form', 'vort', 'fortb', 'sfort', 'fork', 'forrt', 'sort', 'fxrt',
                          'forw', 'foro', 'forlt', 'fokt', 'foxt', 'rort', 'forn', 'fohrt', 'fore', 'aort', 'fora',
                          'foort', 'fordt', 'cfort', 'fzrt', 'fosrt', 'fortk', 'focrt', 'forit', 'forl', 'fozt', 'fout',
                          'kort', 'fodrt', 'hfort', 'forh', 'lfort', 'cort', 'foat', 'lort', 'fors', 'foct', 'fert',
                          'forv', 'kfort', 'fzort', 'uort', 'forkt', 'fortf', 'fowrt', 'fortq', 'fhrt', 'fkrt', 'fprt',
                          'fuort', 'fovrt', 'folt', 'foot', 'ufort', 'fgort', 'fortd', 'fxort', 'forz', 'jfort',
                          'fomrt', 'forb', 'mort', 'forx', 'fogt', 'foft', 'dort', 'port', 'jort', 'wort', 'gfort',
                          'foqt', 'forgt', 'qfort', 'fortl', 'flrt', 'zort', 'flort', 'foert', 'forbt', 'fogrt',
                          'fojrt', 'fortj', 'fbrt', 'vfort', 'fyrt', 'foirt', 'fhort', 'fotrt', 'frort', 'fortp',
                          'fortx', 'forth', 'forg', 'fdrt', 'foprt', 'fortz', 'yort', 'ford', 'fiort', 'fortg', 'fortt',
                          'foryt', 'bfort', 'fcort', 'forf', 'faort', 'firt', 'ffrt', 'fgrt', 'qort', 'ffort', 'tort',
                          'forst', 'fmrt', 'oort', 'fost', 'ftrt', 'ofort', 'font', 'dfort', 'forr', 'fonrt', 'fortr',
                          'fofrt', 'yfort', 'afort', 'foyt', 'forc', 'foyrt', 'forwt', 'fvort', 'fovt', 'fory', 'forht',
                          'zfort', 'fnrt', 'fobt', 'pfort', 'xort', 'foru', 'foxrt', 'rfort', 'forpt', 'fnort', 'efort',
                          'forj', 'fott', 'frrt', 'fqrt', 'fvrt', 'iort', 'foret', 'fojt', 'fokrt', 'forty', 'bort',
                          'fornt', 'foit', 'eort', 'forqt', 'fjort', 'forti', 'fbort', 'gort', 'forxt', 'forzt', 'fjrt',
                          'nfort', 'furt', 'forp', 'fowt', 'fortc', 'folrt', 'fcrt', 'forts', 'fdort', 'fsrt', 'forto',
                          'foet', 'fobrt', 'fori', 'forjt', 'fourt', 'forft', 'fsort', 'fkort', 'forat', 'forta',
                          'f8rt', 'f9rt', 'f0rt', 'f;rt', 'f*rt', 'f(rt', 'f)rt', 'fo3t', 'fo4t', 'fo5t', 'fo#t',
                          'fo$t', 'fo%t', 'for4', 'for5', 'for6', 'for$', 'for%', 'for^', 'pgrade', 'ugrade', 'uprade',
                          'uprgade', 'upgade', 'upgkrade', 'upgrde', 'upgryade', 'ukgrade', 'upgradve', 'upgrae',
                          'upgrfade', 'pugrade', 'spgrade', 'uphgrade', 'upgraed', 'upgrad', 'wpgrade', 'upgradez',
                          'upgrdae', 'uopgrade', 'uypgrade', 'upgrwade', 'uporade', 'npgrade', 'upghrade', 'upgrrde',
                          'upgarde', 'upgdade', 'upgradle', 'upgrades', 'upgmrade', 'bupgrade', 'upgprade', 'ugprade',
                          'upograde', 'upgmade', 'upgrmde', 'zpgrade', 'upgradm', 'mupgrade', 'uxgrade', 'upgratde',
                          'upgradeo', 'unpgrade', 'upgradeu', 'upgradee', 'upgrabe', 'upgradd', 'upgradv', 'upgradu',
                          'upgorade', 'upgrahde', 'upgruade', 'upgvade', 'upgkade', 'upgraxe', 'upgraye', 'upgcrade',
                          'upgyade', 'uprgrade', 'upgrace', 'upgrede', 'upgrdde', 'upgrady', 'upgrjade', 'upbrade',
                          'upgradpe', 'upgrzade', 'upgradhe', 'upgradqe', 'upgradue', 'upgrsade', 'upgradje', 'upgradc',
                          'upgbade', 'upgralde', 'upgrawe', 'ubgrade', 'ypgrade', 'upgrale', 'upgraie', 'upgrxde',
                          'upgrqade', 'upgradfe', 'upgqade', 'upgraade', 'upgrude', 'upgrawde', 'upgrare', 'apgrade',
                          'upgrvde', 'rpgrade', 'uvpgrade', 'upgradbe', 'uepgrade', 'ufgrade', 'upgrode', 'lupgrade',
                          'upgwade', 'upgrbade', 'upgrlde', 'upgradeq', 'uperade', 'upgrafde', 'upgtade', 'upgarade',
                          'upgirade', 'upgyrade', 'ufpgrade', 'upgradre', 'eupgrade', 'upgvrade', 'upgrayde', 'upgraze',
                          'pupgrade', 'uhgrade', 'ungrade', 'upgrcde', 'upgrqde', 'upgtrade', 'upgradn', 'upgrabde',
                          'upgradf', 'upfrade', 'uparade', 'upygrade', 'ukpgrade', 'upgrads', 'opgrade', 'upgaade',
                          'umgrade', 'upgryde', 'upgradte', 'upgraqde', 'uzpgrade', 'upgradeh', 'upzrade', 'upgbrade',
                          'upgraqe', 'vpgrade', 'upgraae', 'ujgrade', 'upgeade', 'uapgrade', 'gupgrade', 'upgradeb',
                          'upgxrade', 'mpgrade', 'uqpgrade', 'upgrave', 'upzgrade', 'upjrade', 'upgradeg', 'upgnade',
                          'upgrazde', 'upjgrade', 'uqgrade', 'upgrvade', 'upgzrade', 'upirade', 'upgrase', 'upcrade',
                          'ujpgrade', 'upgrada', 'upigrade', 'upgrajde', 'upgdrade', 'usgrade', 'upgraode', 'fpgrade',
                          'upgraee', 'umpgrade', 'upwgrade', 'upgradke', 'upgradx', 'upurade', 'upgrcade', 'upgrader',
                          'upugrade', 'upgrhde', 'upgradne', 'upbgrade', 'jpgrade', 'upgrjde', 'upgjade', 'uugrade',
                          'upgride', 'upgradae', 'upggrade', 'ulgrade', 'upggade', 'ucpgrade', 'uspgrade', 'uprrade',
                          'upgrnde', 'upgradex', 'upgrate', 'tpgrade', 'upgradde', 'cpgrade', 'upgradye', 'ulpgrade',
                          'upnrade', 'upgrzde', 'upgrfde', 'upgrhade', 'ppgrade', 'upgrgade', 'upgradi', 'upgradh',
                          'urgrade', 'upgradep', 'upsrade', 'upguade', 'tupgrade', 'upgradek', 'upgrmade', 'upgradem',
                          'supgrade', 'uigrade', 'updrade', 'urpgrade', 'upgraded', 'uxpgrade', 'uplrade', 'upgjrade',
                          'upgroade', 'upqrade', 'upgrapde', 'updgrade', 'uptrade', 'fupgrade', 'upgradge', 'upmgrade',
                          'jupgrade', 'upprade', 'upgradk', 'upgradze', 'utgrade', 'upgrado', 'upgfrade', 'uptgrade',
                          'upkrade', 'ucgrade', 'upgraue', 'zupgrade', 'upgreade', 'upgrdade', 'upgradie', 'upgrnade',
                          'upxrade', 'upgrpde', 'upmrade', 'kupgrade', 'ugpgrade', 'uwgrade', 'nupgrade', 'upgrrade',
                          'upgpade', 'upgrame', 'upgrake', 'upgradec', 'upgradxe', 'gpgrade', 'upgrlade', 'iupgrade',
                          'upgradew', 'upgragde', 'upsgrade', 'upfgrade', 'upngrade', 'upgrakde', 'uupgrade', 'upgrtde',
                          'upghade', 'upglade', 'upvrade', 'bpgrade', 'upgradj', 'upgrwde', 'upglrade', 'upwrade',
                          'upgerade', 'upgradce', 'upcgrade', 'vupgrade', 'upgrkde', 'qpgrade', 'uygrade', 'upgwrade',
                          'utpgrade', 'uplgrade', 'lpgrade', 'uphrade', 'upgradse', 'uograde', 'upgrarde', 'upgxade',
                          'uppgrade', 'upgoade', 'upkgrade', 'upgraxde', 'upgrande', 'upgrpade', 'upgrafe', 'qupgrade',
                          'upgradz', 'dupgrade', 'upgraide', 'kpgrade', 'upgradg', 'upgradei', 'oupgrade', 'uhpgrade',
                          'udpgrade', 'upgrane', 'upgrxade', 'upgurade', 'uipgrade', 'upgradme', 'upgraoe', 'ubpgrade',
                          'upgrape', 'upgrasde', 'uagrade', 'upgrage', 'upgradoe', 'upgradb', 'uggrade', 'upgradw',
                          'udgrade', 'upgradwe', 'wupgrade', 'upgraje', 'uvgrade', 'upgramde', 'upgiade', 'upgradej',
                          'ipgrade', 'upgravde', 'upgradey', 'upgracde', 'hupgrade', 'dpgrade', 'upqgrade', 'upgradev',
                          'uzgrade', 'upgcade', 'cupgrade', 'upgraede', 'upgnrade', 'upgradel', 'upgradef', 'upvgrade',
                          'upgrkade', 'upagrade', 'upgriade', 'upgraden', 'epgrade', 'upgradq', 'upgrbde', 'upgradea',
                          'upgsade', 'upgrgde', 'upgradr', 'uwpgrade', 'upegrade', 'upgfade', 'upgsrade', 'rupgrade',
                          'upgrtade', 'upgrsde', 'upgradp', 'uegrade', 'aupgrade', 'hpgrade', 'upgraude', 'upgrahe',
                          'xpgrade', 'yupgrade', 'upgzade', 'upgradl', 'xupgrade', 'upxgrade', 'upgradet', 'upgqrade',
                          'upgradt', 'upyrade', '6pgrade', '7pgrade', '8pgrade', '^pgrade', '&pgrade', '*pgrade',
                          'u9grade', 'u0grade', 'u-grade', 'u[grade', 'u]grade', 'u;grade', 'u(grade', 'u)grade',
                          'u_grade', 'u=grade', 'u+grade', 'u{grade', 'u}grade', 'u:grade', 'upg3ade', 'upg4ade',
                          'upg5ade', 'upg#ade', 'upg$ade', 'upg%ade', 'upgrad4', 'upgrad3', 'upgrad2', 'upgrad$',
                          'upgrad#', 'upgrad@', 'skixl', 'sikll', 'skipl', 'sxkill', 'skiil', 'slkill',
                          'skil', 'shkill', 'skilgl', 'sklill', 'skihl', 'skll', 'skeill', 'skile', 'skilb', 'skitll',
                          'skillr', 'skilla', 'skillz', 'swill', 'skitl', 'skills', 'skpll', 'skipll', 's.ill',
                          's,ill', 's>ill', 's<ill', 'sk7ll', 'sk8ll', 'sk9ll', 'sk&ll', 'sk*ll', 'sk(ll', 'ski;l',
                          'ski/l', 'ski.l', 'ski,l', 'ski?l', 'ski>l', 'ski<l', 'skil;', 'skil/', 'skil.', 'skil,',
                          'skil?', 'skil>', 'skil<', 'tere', 'rtee', 'tee', 'trei', 'tre', 'bree', 'treb',
                          'tuee', 'tsree', 'ttree', 'jree', 'trwee', 'trnee', 'trece', 'tdee', 'xtree', 'traee', 'nree',
                          'treeo', 'teee', 'oree', 'trye', 'treej', 'turee', 'trem', 'sree', 'trqee', 'trke', 'tzee',
                          'trexe', 'tlree', 'treee', 'trje', 'vree', 'ltree', 'tkee', 'atree', 'htree', 'gree', 'trlee',
                          'trre', 'treqe', 'mree', 'tnee', 'trhe', 'trel', 'truee', 'trpee', 'treei', 'trek', 'trere',
                          'trete', 'triee', 'treel', 'zree', 'ttee', 'gtree', 'tgee', 'txee', 'trev', 'utree', 'trxee',
                          'treh', 'trce', 'tyree', 'tsee', 'true', 'dtree', 'treer', 'hree', 'tfee', 'treje', 'ktree',
                          'ctree', 'treg', 'trele', 'treen', 'wtree', 'xree', 'tren', 'tzree', 'ytree', 'treey',
                          'tkree', 'three', 'trde', 'tvee', 'tqee', 'tred', 'txree', 'dree', 'trme', 'treeb', 'trej',
                          'lree', 'cree', 'itree', 'thee', 'trez', 'trfee', 'aree', 'tpee', 'trey', 'trehe', 'trve',
                          'trjee', 'treae', 'taree', 'trree', 'uree', 'treme', 'trege', 'trvee', 'jtree', 'trmee',
                          'free', 'tret', 'trer', 'treed', 'trep', 'tlee', 'trex', 'trtee', 'treet', 'toree', 'vtree',
                          'trdee', 'treev', 'wree', 'trewe', 'trxe', 'ntree', 'treve', 'treep', 'tjee', 'treeg',
                          'trkee', 'tcree', 'tjree', 'treo', 'ptree', 'trew', 'trqe', 'troee', 'trsee', 'trhee', 'troe',
                          'trae', 'tyee', 'trcee', 'tfree', 'tgree', 'trbee', 'tmree', 'teree', 'treze', 'otree',
                          'treue', 'iree', 'trgee', 'trle', 'btree', 'trbe', 'treea', 'qree', 'taee', 'treeu', 'rtree',
                          'trzee', 'ftree', 'treem', 'trese', 'treez', 'yree', 'tiree', 'trene', 'toee', 'treew',
                          'trze', 'tmee', 'treeh', 'stree', 'trfe', 'trepe', 'treec', 'tvree', 'treoe', 'tpree',
                          'qtree', 'treef', 'treie', 'tcee', 'treke', 'treu', 'trse', 'tnree', 'rree', 'treq', 'trees',
                          'tryee', 'tbee', 'twee', 'treye', 'trpe', 'eree', 'trefe', 'trwe', 'ztree', 'treex', 'tdree',
                          'treeq', 'trne', 'treek', 'trge', 'trec', 'trea', 'etree', 'trebe', 'tqree', 'tref', 'mtree',
                          'trie', 'trede', 'tbree', 'trte', 'tiee', 'twree', 'kree', '4ree', '5ree', '6ree', '$ree',
                          '%ree', '^ree', 't3ee', 't4ee', 't5ee', 't#ee', 't$ee', 't%ee', 'tr4e', 'tr3e', 'tr2e',
                          'tr$e', 'tr#e', 'tr@e', 'tre4', 'tre3', 'tre2', 'tre$', 'tre#', 'tre@', '/rsrch', '/lab',
                          '/fortitude', '/fort', '/upgrade', '/skill', '/tree', 'r'],
                 extras={'emoji': "research_point", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.slash.optout', True]
                 }, "dev": False, "description_keys": ["research.meta.description"], "name_key": "research.slash.name"},
                 brief="research.meta.brief",
                 description="{0}")
    async def research(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the research command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode of the user
            optout: Whether or not the user wants to opt out of starting a session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.research_command(ctx, authcode, not optout)

    @slash_command(name='research', name_localizations=stw.I18n.construct_slash_dict("research.slash.name"),
                   description="Claim and spend your research points",
                   description_localizations=stw.I18n.construct_slash_dict("research.slash.description"),
                   guild_ids=stw.guild_ids)
    async def slashresearch(self, ctx: discord.ApplicationContext,
                            token: Option(description="Your Epic Games authcode. Required unless you have an active "
                                                      "session.",
                                          description_localizations=stw.I18n.construct_slash_dict(
                                              "generic.slash.token"),
                                          name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                                          min_length=32) = "",
                            auth_opt_out: Option(default="False",
                                                 description="Opt out of starting an authentication session",
                                                 description_localizations=stw.I18n.construct_slash_dict(
                                                     "generic.slash.optout"),
                                                 name_localizations=stw.I18n.construct_slash_dict(
                                                     "generic.meta.args.optout"),
                                                 choices=[OptionChoice("Do not start an authentication session", "True",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.true")),
                                                          OptionChoice("Start an authentication session (Default)",
                                                                       "False",
                                                                       stw.I18n.construct_slash_dict(
                                                                           "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the research command when called via slash command

        Args:
            ctx: The context of the command
            token: The authcode of the user
            auth_opt_out: Whether or not the user wants to opt out of starting a session
        """
        await self.research_command(ctx, token, not eval(auth_opt_out))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Research(client))

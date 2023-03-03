"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the research command. collect and spend research points
"""

import asyncio
import orjson

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


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
            print(e, "\nError during purchase:\n", stw.truncate(purchased_json))
            try:
                error_code = json_response["errorCode"]
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
            print(e, "\nno research stat, but daily reward; must have zero research stats.\n",
                  stw.truncate(json_response))
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
            print("errors.stwdaily.failed_guid_research encountered:", stw.truncate(json_response))
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
            print("errors.stwdaily.failed_total_points encountered:", stw.truncate(json_response))
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
            print(e)

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
                          '/research', 'resea', 'resear', 'lab', 'fortitude', 'fort', 'upgrade', 'skill', 'tree',
                          'navorsing', 'بحث', 'изследвания', 'গবেষণা', 'recerca', 'výzkum', 'forskning', 'Forschung',
                          'έρευνα', 'investigación', 'uurimine', 'پژوهش', 'tutkimusta', 'recherche', 'સંશોધન',
                          'bincike', 'מחקר', 'शोध करना', 'istraživanje', 'kutatás', 'penelitian', 'ricerca', 'リサーチ',
                          '연구', 'tyrimai', 'pētījumiem', 'संशोधन', 'penyelidikan', 'onderzoek', 'ਖੋਜ', 'badania',
                          'pesquisa', 'cercetare', 'исследование', 'výskumu', 'истраживања', 'utafiti', 'ஆராய்ச்சி',
                          'పరిశోధన', 'วิจัย', 'araştırma', 'дослідження', 'تحقیق', 'nghiên cứu', '研究'],
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
        await self.research_command(ctx, token, not bool(auth_opt_out))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Research(client))

"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily quests command to view + reroll quests.
"""
import asyncio
import logging

import aiofiles
import discord
import discord.ext.commands as ext
from discord import Option, SelectOption, OptionChoice
import orjson

import stwutil as stw

logger = logging.getLogger(__name__)


class QuestsView(discord.ui.View):
    """
    The view for the quests command.
    """

    def __init__(self, ctx, client, message, author, quests, quest_options, auth_info, quest_rerolls, desired_lang):
        super().__init__(timeout=360.0)
        self.dailyquests = None
        self.questsview = None
        self.ctx = ctx
        self.client = client
        self.message = message
        self.author = author
        self.quests = quests
        self.quest_rerolls = quest_rerolls
        self.interaction_check_done = {}
        self.children[0].options = quest_options
        self.children[0].placeholder = stw.I18n.get("dailyquests.view.option.placeholder", desired_lang)
        self.auth_info = auth_info
        self.desired_lang = desired_lang

    async def quest_reroll_embed(self, ctx, guid, select=True):
        """
        Creates an embed for the daily quest reroll command confirmation.

        Args:
            ctx: The context of the command.
            guid: The guid of the quest to reroll.
            select: Whether the embed is for the select menu.

        Returns:
            The embed with the daily quest details.
        """
        if select:
            if guid == "back":
                self.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                        desired_lang=self.desired_lang)
                self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                                   desired_lang=self.desired_lang)
                return await self.dailyquests.dailyquests_embed(ctx, self.desired_lang, self.quests, self.auth_info)
            else:
                self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                        desired_lang=self.desired_lang,
                                                                                        selected_guid=guid)
                self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                                   desired_lang=self.desired_lang,
                                                                                                   selected_guid=guid)
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("dailyquests.embed.title", self.desired_lang),
                                            "library_list"),
            description=f"",
            colour=self.client.colours["generic_blue"])
        if not self.quests:
            embed.description = f"\u200b\n{stw.I18n.get('dailyquests.embed.description.nodailyquests', self.desired_lang, self.client.config['emojis']['checkmark'])}\u200b\n\u200b"
        else:
            for quest in self.quests:
                if quest["guid"] == guid:
                    for file_name in stw.daily_quest_files:
                        if quest["templateId"].lower().split("quest:")[1] == file_name.split(".")[0].lower():
                            async with aiofiles.open(f"ext/DataTables/DailyQuests/{file_name}", "r",
                                                     encoding="utf-8") as f:
                                quest_data = orjson.loads(await f.read())
                                embed.description += await self.dailyquests.dailyquests_entry(quest, quest_data,
                                                                                              self.auth_info["vbucks"],
                                                                                              self.desired_lang)
                                embed.description += f"\n*{quest_data[0]['Properties']['Objectives'][0]['Description']['SourceString']}*\n"
                                break
                    else:
                        continue
        embed.description += f"\u200b\n"
        embed.description = stw.truncate(embed.description, 3999)
        embed = await stw.set_thumbnail(self.client, embed, "challenge_book_s19")
        embed = await stw.add_requested_footer(ctx, embed, self.desired_lang)
        return embed

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command.

        Args:
            interaction: The interaction to check.

        Returns:
            True if the interaction is from the author of the command, False otherwise.
        """
        return await stw.view_interaction_check(self, interaction, "dailyquests")

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        # if isinstance(self.ctx, discord.ApplicationContext):
        #     try:
        #         return await self.message.edit_original_response(view=self)
        #     except:
        #         return await self.ctx.edit(view=self)
        # else:
        #     return await self.message.edit(view=self)

        return await stw.slash_edit_original(self.ctx, self.message, embeds=None, view=self)

    @discord.ui.select(
        placeholder="Choose a daily quest to re-roll",
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a quest is selected.

        Args:
            select: The select menu that was used.
            interaction: The interaction that was used.
        """
        embed = await self.quest_reroll_embed(self.ctx, select.values[0])
        if self.questsview is None:
            view = QuestRerollView(self.ctx, self.client, self.message, self.author, self.quests,
                                   self.children[0].options, select.values[0], self.auth_info, self.quest_rerolls, self.desired_lang)
            self.questsview = view
        else:
            view = self.questsview
        view.dailyquests = self.dailyquests
        view.questsview = self
        if select.values[0] == "back":
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                    desired_lang=self.desired_lang)
            self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                               desired_lang=self.desired_lang)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                    desired_lang=self.desired_lang,
                                                                                    selected_guid=select.values[0])
            self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                               desired_lang=self.desired_lang,
                                                                                               selected_guid=
                                                                                               select.values[0])
            await interaction.response.edit_message(embed=embed, view=self.questsview)


class QuestRerollView(discord.ui.View):
    """
    The view for the quest reroll purchase command.
    """

    def __init__(self, ctx, client, message, author, quests, quest_options, guid, auth_info, quest_rerolls, desired_lang):
        super().__init__(timeout=360.0)
        self.dailyquests = None
        self.questsview = None
        self.ctx = ctx
        self.client = client
        self.message = message
        self.author = author
        self.quests = quests
        self.guid = guid
        self.auth_info = auth_info
        self.quest_rerolls = quest_rerolls
        self.interaction_check_done = {}
        self.desired_lang = desired_lang

        self.children[0].placeholder = stw.I18n.get("dailyquests.view.option.placeholder", desired_lang)

        self.children[0].options = quest_options
        self.children[1].label = stw.I18n.get("dailyquests.confirmation.button.reroll", self.desired_lang)
        self.children[1].emoji = self.client.config["emojis"]["slot_icon_shuffle"]
        if self.quest_rerolls <= 0:
            self.children[1].disabled = True
        # self.children[2].label = stw.I18n.get("generic.view.button.cancel", self.desired_lang)

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        # if isinstance(self.ctx, discord.ApplicationContext):
        #     try:
        #         return await self.message.edit_original_response(view=self)
        #     except:
        #         return await self.ctx.edit(view=self)
        # else:
        #     return await self.message.edit(view=self)

        return await stw.slash_edit_original(self.ctx, self.message, embeds=None, view=self)

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command.

        Args:
            interaction: The interaction to check.

        Returns:
            True if the interaction is from the author of the command, False otherwise.
        """
        return await stw.view_interaction_check(self, interaction, "dailyquests")

    @discord.ui.select(
        placeholder="Choose a daily quest to re-roll",
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a quest is selected.

        Args:
            select: The select menu that was used.
            interaction: The interaction that was used.
        """
        embed = await self.questsview.quest_reroll_embed(self.ctx, select.values[0])
        self.guid = select.values[0]
        if self.guid == "back":
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                    desired_lang=self.desired_lang)
            self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                               desired_lang=self.desired_lang)
            await interaction.response.edit_message(embed=embed, view=self.questsview)
        else:
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                    desired_lang=self.desired_lang,
                                                                                    selected_guid=self.guid)
            self.questsview.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                               desired_lang=self.desired_lang,
                                                                                               selected_guid=self.guid)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Re-roll Quest", style=discord.ButtonStyle.primary)
    async def reroll_quest_button(self, button, interaction):
        """
        Called when the reroll quest button is pressed.

        Args:
            button: The button that was pressed.
            interaction: The interaction that was used.
        """
        stw_request = await stw.profile_request(self.client, "quest_refresh", self.auth_info,
                                                json={"questId": self.guid})
        stw_json_response = orjson.loads(await stw_request.read())
        try:
            error_code = stw_json_response["errorCode"]
            acc_name = self.auth_info["account_name"]
            embed = await stw.post_error_possibilities(self.ctx, self.client, "dailyquests", acc_name, error_code,
                                                       verbiage_action="rerollquest", desired_lang=self.desired_lang)
            logger.info(f"User {self.ctx.author.id} could not reroll quest. | {stw_json_response}")
            await interaction.response.edit_message(embed=embed, view=None)
            if error_code in ["errors.com.epicgames.modules.quests.quest_reroll_error",
                              "errors.com.epicgames.modules.quests.quest_not_found"]:
                await asyncio.sleep(5.8)
                embed = await self.questsview.quest_reroll_embed(self.ctx, "back")
                await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self.questsview)
            return
        except:
            daily_quests = []
            for attribute, value in stw_json_response["profileChanges"][0]["profile"]["items"].items():
                if value["templateId"].startswith("Quest:daily_") and value["attributes"]["quest_state"] == "Active":
                    daily_quests.append(value)
                    daily_quests[-1]["guid"] = attribute
            daily_quests.sort(key=lambda x: x["attributes"]["creation_time"])
            self.quest_rerolls = stw_json_response["profileChanges"][0]["profile"]["stats"]["attributes"].get("quest_manager", 0).get("dailyQuestRerolls", 0)
            self.questsview.quest_rerolls = self.quest_rerolls
            # profile_notifications = stw_json_response.get("notifications", [{}])[0].get("newQuestId")
            self.quests = daily_quests
            self.questsview.quests = daily_quests
            embed = await self.questsview.quest_reroll_embed(self.ctx, "back")
            await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self.questsview)


class DailyQuests(ext.Cog):
    """
    Cog for the daily quests command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, desired_lang):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.
            desired_lang: The desired language for the embeds.

        Returns:
            True if an error is found, False otherwise.
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "dailyquests", acc_name, error_code,
                                                       verbiage_action="rerollquest", desired_lang=desired_lang)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def select_options_quests(self, quests, return_visible=False, desired_lang="en", selected_guid=None):
        """
        Creates the options for the select menu for the daily quests command.

        Args:
            quests: The quests to be displayed.
            return_visible: Whether the return value should be the visible options or the hidden options.
            desired_lang: The language to use for the command.
            selected_guid: The guid of the selected quest.

        Returns:
            The options for the select menu.
        """
        options = []
        if return_visible:
            options.append(SelectOption(label=stw.I18n.get("llamas.view.option.return.name", desired_lang),
                                        value="back", emoji=self.emojis["left_arrow"],
                                        description=stw.I18n.get("dailyquests.view.option.return.description",
                                                                 desired_lang)))
        for quest in quests:
            for file_name in stw.daily_quest_files:
                if quest["templateId"].lower().split("quest:")[1] == file_name.split(".")[0].lower():
                    async with aiofiles.open(f"ext/DataTables/DailyQuests/{file_name}", "r", encoding="utf-8") as f:
                        quest_data = orjson.loads(await f.read())
                        match quest_data[0]["Properties"]["LargePreviewImage"]["AssetPathName"].split(".")[-1]:
                            case "T-Icon-Exterminate-128":
                                quest_icon_emoji = self.client.config["emojis"]["exterminate"]
                            case "T-Icon-Safe-128":
                                quest_icon_emoji = self.client.config["emojis"]["safe"]
                            case "T-Icon-Collect-World-Explorer-128":
                                quest_icon_emoji = self.client.config["emojis"]["world_explorer"]
                            case "T-Icon-Daily-128":
                                quest_icon_emoji = self.client.config["emojis"]["daily_quest"]
                            case "T-Icon-Hero-Soldier-128":
                                quest_icon_emoji = self.client.config["emojis"]["hid_soldier"]
                            case "T-Icon-Hero-Outlander-128":
                                quest_icon_emoji = self.client.config["emojis"]["hid_outlander"]
                            case "T-Icon-Hero-Ninja-128":
                                quest_icon_emoji = self.client.config["emojis"]["hid_ninja"]
                            case "T-Icon-Hero-Constructor-128":
                                quest_icon_emoji = self.client.config["emojis"]["hid_constructor"]
                            case "Icon-Mission-RadarTower-128":
                                quest_icon_emoji = self.client.config["emojis"]["radar_tower"]
                            case _:
                                quest_icon_emoji = self.client.config["emojis"]["daily_quest"]
                        options.append(
                            discord.SelectOption(
                                label=stw.truncate(quest_data[0]['Properties']['DisplayName']['SourceString']),
                                value=quest["guid"],
                                description=stw.truncate(
                                    quest_data[0]['Properties']['Objectives'][0]['Description'][
                                        'SourceString']),
                                emoji=quest_icon_emoji))
                        if selected_guid is not None and selected_guid == quest["guid"]:
                            options[-1].default = True
                        break
            else:
                continue
        return options

    async def dailyquests_entry(self, quest, quest_data, vbucks, desired_lang='en'):
        """
        Creates an embed entry string for a single daily quest entry.

        Args:
            quest: The quest data.
            quest_data: The quest data from the datatable.
            vbucks: If the account is founders
            desired_lang: The language to use for the embed.

        Returns:
            The embed entry string.
        """
        match quest_data[0]["Properties"]["LargePreviewImage"]["AssetPathName"].split(".")[-1]:
            case "T-Icon-Exterminate-128":
                quest_icon_emoji = self.client.config["emojis"]["exterminate"]
            case "T-Icon-Safe-128":
                quest_icon_emoji = self.client.config["emojis"]["safe"]
            case "T-Icon-Collect-World-Explorer-128":
                quest_icon_emoji = self.client.config["emojis"]["world_explorer"]
            case "T-Icon-Daily-128":
                quest_icon_emoji = self.client.config["emojis"]["daily_quest"]
            case "T-Icon-Hero-Soldier-128":
                quest_icon_emoji = self.client.config["emojis"]["hid_soldier"]
            case "T-Icon-Hero-Outlander-128":
                quest_icon_emoji = self.client.config["emojis"]["hid_outlander"]
            case "T-Icon-Hero-Ninja-128":
                quest_icon_emoji = self.client.config["emojis"]["hid_ninja"]
            case "T-Icon-Hero-Constructor-128":
                quest_icon_emoji = self.client.config["emojis"]["hid_constructor"]
            case "Icon-Mission-RadarTower-128":
                quest_icon_emoji = self.client.config["emojis"]["radar_tower"]
            case _:
                quest_icon_emoji = self.client.config["emojis"]["daily_quest"]
        entry_string = f"\u200b\n{quest_icon_emoji}{self.client.config['emojis']['bang'] if not quest['attributes'].get('item_seen', False) else ''} **{quest_data[0]['Properties']['DisplayName']['SourceString']}**"
        if quest["attributes"].get(
                f"completion_{quest_data[0]['Properties']['Objectives'][0]['ObjectiveStatHandle']['RowName']}") is not None:
            entry_string += f" [{quest['attributes']['completion_{0}'.format(quest_data[0]['Properties']['Objectives'][0]['ObjectiveStatHandle']['RowName'])]}/{quest_data[0]['Properties']['Objectives'][0]['Count']}]"
        else:
            entry_string += f" [0/{quest_data[0]['Properties']['Objectives'][0]['Count']}]"
        gold_quantity = stw.quest_rewards[0]["Rows"][f"{quest_data[0]['Name']}_001"]["Quantity"]
        mtx_quantity = stw.quest_rewards[0]["Rows"][f"{quest_data[0]['Name']}_002"]["Quantity"]
        rewards_string = f"{self.client.config['emojis']['gold']}x{gold_quantity} {self.client.config['emojis']['xray']}x{mtx_quantity}"
        if vbucks:
            rewards_string += f" {self.client.config['emojis']['vbucks']}x{mtx_quantity}"
        rewards_string += f" {self.client.config['emojis']['xp_everywhere']}x{stw.I18n.fmt_num(23000, desired_lang)}"
        entry_string += f"\n{stw.I18n.get('dailyquests.embed.rewards', desired_lang, rewards_string)}\n"
        return entry_string

    async def dailyquests_embed(self, ctx, desired_lang, quests, auth_info):
        """
        Creates the embed for the daily quests command.

        Args:
            ctx: The context of the command.
            desired_lang: The language to use for the embed.
            quests: The quests to be displayed.
            auth_info: The auth_info tuple from get_or_create_auth_session.

        Returns:
            The embed.
        """
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("dailyquests.embed.title", desired_lang),
                                            "library_list"),
            description=f"\u200b\n{stw.I18n.get('dailyquests.embed.description.nodailyquests', desired_lang, self.client.config['emojis']['checkmark'])}\u200b\n\u200b",
            colour=self.client.colours["generic_blue"])
        if not quests:
            embed.description = f"\u200b\n{stw.I18n.get('dailyquests.embed.description.nodailyquests', desired_lang, self.client.config['emojis']['checkmark'])}\u200b\n\u200b"
        else:
            if len(quests) == 1:
                embed.description = f"\u200b\n{stw.I18n.get('dailyquests.embed.description.singular', desired_lang)}\u200b\n\u200b"
            else:
                embed.description = f"\u200b\n{stw.I18n.get('dailyquests.embed.description.plural', desired_lang)}\u200b\n\u200b"
            for quest in quests:
                for file_name in stw.daily_quest_files:
                    if quest["templateId"].lower().split("quest:")[1] == file_name.split(".")[0].lower():
                        async with aiofiles.open(f"ext/DataTables/DailyQuests/{file_name}", "r", encoding="utf-8") as f:
                            quest_data = orjson.loads(await f.read())
                            embed.description += await self.dailyquests_entry(quest, quest_data, auth_info["vbucks"],
                                                                              desired_lang)
                            break
                else:
                    continue
        embed.description += f"\u200b\n"
        embed.description = stw.truncate(embed.description, 3999)
        embed = await stw.set_thumbnail(self.client, embed, "challenge_book_s19")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        return embed

    async def daily_quests_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the daily quests command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the account.
            auth_opt_out: Whether the user has opted out of auth.

        Returns:
            None
        """

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "dailyquests", authcode, auth_opt_out, True,
                                                         desired_lang=desired_lang)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except IndexError:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        stw_request = await stw.profile_request(self.client, "quest_login", auth_info[1])
        stw_json_response = orjson.loads(await stw_request.read())
        # stw_file = io.BytesIO()
        # stw_file.write(orjson.dumps(stw_json_response, option=orjson.OPT_INDENT_2))
        # stw_file.seek(0)
        # json_file2 = discord.File(stw_file,
        #                           filename=f"{auth_info[1]['account_name']}-campaign-"
        #                                    f"{datetime.datetime.now().strftime('%D-%M-%Y_%H-%M-%S')}.json")

        # check for le error code
        if await self.check_errors(ctx, stw_json_response, auth_info, final_embeds, desired_lang):
            return

        daily_quests = []
        for attribute, value in stw_json_response["profileChanges"][0]["profile"]["items"].items():
            if value["templateId"].startswith("Quest:daily_") and value["attributes"]["quest_state"] == "Active":
                daily_quests.append(value)
                daily_quests[-1]["guid"] = attribute
        daily_quests.sort(key=lambda x: x["attributes"]["creation_time"])
        daily_quest_rerolls = stw_json_response["profileChanges"][0]["profile"]["stats"]["attributes"].get("quest_manager", 0).get("dailyQuestRerolls", 0)

        embed = await self.dailyquests_embed(ctx, desired_lang, daily_quests, auth_info[1])

        final_embeds.append(embed)

        quests_view_options = await self.select_options_quests(daily_quests, desired_lang=desired_lang)
        quests_view = QuestsView(ctx, self.client, auth_info[0], ctx.author, daily_quests, quests_view_options,
                                 auth_info[1], daily_quest_rerolls, desired_lang)
        quests_view.dailyquests = self
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, quests_view)
        return

    @ext.slash_command(name='dailyquests', name_localizations=stw.I18n.construct_slash_dict("dailyquests.slash.name"),
                       description='View and manage your daily STW quests',
                       description_localizations=stw.I18n.construct_slash_dict("dailyquests.meta.brief"),
                       guild_ids=stw.guild_ids)
    async def slashdailyquests(self, ctx: discord.ApplicationContext,
                               token: Option(description="Your Epic Games authcode. Required unless you have an active "
                                                         "session.",
                                             description_localizations=stw.I18n.construct_slash_dict(
                                                 "generic.slash.token"),
                                             name_localizations=stw.I18n.construct_slash_dict(
                                                 "generic.meta.args.token"),
                                             min_length=32) = "",
                               auth_opt_out: Option(default="False",
                                                    description="Opt out of starting an authentication session",
                                                    description_localizations=stw.I18n.construct_slash_dict(
                                                        "generic.slash.optout"),
                                                    name_localizations=stw.I18n.construct_slash_dict(
                                                        "generic.meta.args.optout"),
                                                    choices=[
                                                        OptionChoice("Do not start an authentication session", "True",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.true")),
                                                        OptionChoice("Start an authentication session (Default)",
                                                                     "False",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the daily quests command when called via slash

        Args:
            ctx (discord.ApplicationContext): The context of the slash command
            token: Your Epic Games authcode. Required unless you have an active session.
            auth_opt_out: Opt out of starting an authentication session
        """
        await self.daily_quests_command(ctx, token, not eval(auth_opt_out))

    @ext.command(name='dailyquests',
                 aliases=['dailyquest', 'dailyuqest', 'daillyquest', 'dailfyquest', 'dailyqest', 'dsilyquest',
                          'davilyquest', 'daiylquest', 'dailyquesbt', 'dialyquest', 'ailyquest', 'uailyquest',
                          'dailquest', 'dailyqueslt', 'dailyquestj', 'dailyqust', 'zdailyquest', 'dailyquet',
                          'dailyquesa', 'dailyquets', 'dailyqiuest', 'dailyqeust', 'dailryquest', 'daliyquest',
                          'damlyquest', 'dailyquesz', 'dailqyuest', 'dailyqouest', 'dalilyquest', 'dailyquezst',
                          'dailyqueest', 'dalyquest', 'dailyques', 'dailyquesst', 'dailyuest', 'dailyquext',
                          'dailyqeest', 'daiilyquest', 'dahlyquest', 'dailyquset', 'daivyquest', 'dainyquest',
                          'dailyquestn', 'daplyquest', 'dailyquoest', 'dawilyquest', 'dailyqbest', 'dailywuest',
                          'dailyquess', 'dailybquest', 'dqailyquest', 'dailyquesct', 'dailyqusst', 'adilyquest',
                          'dilyquest', 'dailyqguest', 'dailyluest', 'daiyyquest', 'dailyquesk', 'daimyquest',
                          'dailywquest', 'dailyqeuest', 'dailyquesw', 'dailyquesl', 'daiyquest', 'dailyqulest',
                          'dailyuquest', 'dqilyquest', 'dailyquesty', 'daihyquest', 'dailyqumest', 'dapilyquest',
                          'dailyquist', 'dailaquest', 'dailyquuest', 'dailiquest', 'dailyeuest', 'datilyquest',
                          'dailyquect', 'dailyquesr', 'dailyquesmt', 'dailyxuest', 'dailyquestc', 'dailyquiest',
                          'daiwlyquest', 'dailyquenst', 'dsailyquest', 'dailyquebst', 'daihlyquest', 'dailyqrest',
                          'dailyqueist', 'dailyquesdt', 'dailvyquest', 'qailyquest', 'daoilyquest', 'dailyquesv',
                          'failyquest', 'dailyqiest', 'dailyquesu', 'daizyquest', 'dailyquesnt', 'daiwyquest',
                          'dallyquest', 'dailyyquest', 'dailtyquest', 'dailyqueost', 'dadlyquest', 'dailyqwest',
                          'hdailyquest', 'dailyquesht', 'dvailyquest', 'daizlyquest', 'dailyqueit', 'dailayquest',
                          'dailyquqest', 'dailyqurst', 'pdailyquest', 'dailyqzuest', 'dailyqueat', 'dailyquesgt',
                          'daildyquest', 'duailyquest', 'dailkquest', 'ddilyquest', 'dailyquelst', 'dailyqueste',
                          'nailyquest', 'dailyqurest', 'daiylyquest', 'dailyqtuest', 'dlilyquest', 'daiayquest',
                          'dailyquesat', 'dailqyquest', 'dailyquept', 'dailyquestb', 'drailyquest', 'daiblyquest',
                          'dailyqusest', 'dgailyquest', 'danilyquest', 'dcilyquest', 'dailequest', 'dailyquefst',
                          'dailyquyest', 'dailyqubest', 'dailyqukest', 'dailysuest', 'dailyquert', 'dailyqutest',
                          'dailyquxest', 'daislyquest', 'eailyquest', 'dasilyquest', 'dailcyquest', 'dtilyquest',
                          'dailyquesx', 'ldailyquest', 'dailyquestp', 'dailyquewt', 'dailyquestg', 'aailyquest',
                          'dailyqquest', 'dmilyquest', 'dailylquest', 'dcailyquest', 'duilyquest', 'dailyquemt',
                          'dailyauest', 'dailyqlest', 'dailyquesn', 'dailyquzst', 'drilyquest', 'dailyquexst',
                          'dailyqtest', 'deailyquest', 'darlyquest', 'dailykuest', 'dailjyquest', 'dailyqjest',
                          'daigyquest', 'dailpyquest', 'dpailyquest', 'dailyqauest', 'dailyquedt', 'dailyqucest',
                          'daixyquest', 'dailyqufest', 'wailyquest', 'dailyfquest', 'dailuyquest', 'dailnyquest',
                          'dailyqduest', 'edailyquest', 'dailyqufst', 'dailyquesth', 'dailyqaest', 'dailyqumst',
                          'dailyquetst', 'diilyquest', 'dailyquxst', 'dailyqueskt', 'dailyqwuest', 'dailkyquest',
                          'dailyquestv', 'dailyqueft', 'dailyouest', 'daqlyquest', 'railyquest', 'dailyqnest',
                          'daxlyquest', 'dazilyquest', 'daivlyquest', 'dailynuest', 'dailyqueut', 'dailyqfuest',
                          'dailiyquest', 'gailyquest', 'dailyqdest', 'dailyqunst', 'dailytuest', 'daiuyquest',
                          'dailmyquest', 'dagilyquest', 'daisyquest', 'oailyquest', 'dailyjquest', 'dailycuest',
                          'daelyquest', 'dailyhuest', 'dailyquesi', 'dailyquepst', 'dailyuuest', 'dailyquespt',
                          'daiplyquest', 'dailynquest', 'dailuquest', 'dailyquejst', 'dailyrquest', 'dailfquest',
                          'daflyquest', 'daialyquest', 'daibyquest', 'dailyqupst', 'dadilyquest',
                          'dmailyquest', 'dailyqudst', 'dailyduest', 'dailyquestq', 'dailyquesc', 'dailyquesg',
                          'daielyquest', 'daildquest', 'dailyquecst', 'mailyquest', 'iailyquest', 'dailyquejt',
                          'dailyqulst', 'dailcquest', 'dailyquett', 'dairyquest', 'dailyquegt', 'dailyquevst',
                          'vailyquest', 'daklyquest', 'dailyquerst', 'dailnquest', 'dailrquest', 'dailyquesp',
                          'dailyqzest', 'dailyqfest', 'dailyquesut', 'dailyqsuest', 'dailyquhst', 'dailyquegst',
                          'dailyqvest', 'qdailyquest', 'dailyquesf', 'daiglyquest', 'dailyquesrt', 'dailyquestr',
                          'dailxquest', 'dailyqugst', 'dairlyquest', 'dailydquest', 'dailyquzest', 'dailbyquest',
                          'daiqyquest', 'dailyquqst', 'darilyquest', 'daeilyquest', 'daidlyquest', 'dailymquest',
                          'dailyquesvt', 'daityquest', 'adailyquest', 'dailyquost', 'dailyquehst', 'dyailyquest',
                          'dailyqueszt', 'ddailyquest', 'dxilyquest', 'dailtquest', 'dailyquestf', 'kailyquest',
                          'dailvquest', 'dailhyquest', 'dailyquesyt', 'dfailyquest', 'daicyquest', 'dailyqgest',
                          'dailyquesj', 'dailyqyest', 'jailyquest', 'dailyqueyt', 'dailyquestx', 'dkilyquest',
                          'daifyquest', 'dvilyquest', 'dailyqueqt', 'bailyquest', 'cdailyquest', 'dailyquesit',
                          'dailyqcuest', 'dfilyquest', 'dainlyquest', 'dakilyquest', 'dawlyquest', 'dauilyquest',
                          'dailyoquest', 'dailyquestw', 'dtailyquest', 'dailxyquest', 'dailyqpest', 'dailyiquest',
                          'daitlyquest', 'odailyquest', 'dailyqueyst', 'daipyquest', 'dailyqunest', 'daalyquest',
                          'daioyquest', 'dzailyquest', 'zailyquest', 'tailyquest', 'dailyquust', 'dajilyquest',
                          'dailyqueset', 'deilyquest', 'dailyquevt', 'dailyquekt', 'dailyquestk', 'damilyquest',
                          'dailyqmest', 'dailpquest', 'dabilyquest', 'datlyquest', 'dailyfuest', 'dailyquesti',
                          'daslyquest', 'dzilyquest', 'dailyquese', 'dailyqukst', 'dailyqkuest', 'dailyqxest',
                          'djailyquest', 'dailhquest', 'dxailyquest', 'dailyqueso', 'dailyquesft', 'dailyquesd',
                          'davlyquest', 'dwilyquest', 'dailygquest', 'dailyqsest', 'dailyquestt', 'dyilyquest',
                          'ydailyquest', 'dailyquast', 'lailyquest', 'dailyqueht', 'dailyqmuest', 'dailyquesta',
                          'dailyvuest', 'daillquest', 'dailyquestd', 'dhailyquest', 'fdailyquest', 'dailyquwst',
                          'dailyqucst', 'daieyquest', 'dailyqueswt', 'dailyquemst', 'dailyqugest', 'dailwquest',
                          'dailyxquest', 'dailyquelt', 'daolyquest', 'vdailyquest', 'dailyquestz', 'dailyqueqst',
                          'dailyhquest', 'daglyquest', 'danlyquest', 'dailyquesy', 'dailyaquest', 'dailyqudest',
                          'dailyquesq', 'mdailyquest', 'dailyvquest', 'udailyquest', 'daileyquest', 'dailyquestm',
                          'dailyyuest', 'dlailyquest', 'dailycquest', 'dailyquaest', 'dailyqueet', 'dayilyquest',
                          'dailyqluest', 'xdailyquest', 'dailyqhuest', 'dailytquest', 'dailyruest', 'doailyquest',
                          'daimlyquest', 'diailyquest', 'dailypuest', 'dailqquest', 'dailybuest', 'bdailyquest',
                          'sdailyquest', 'daclyquest', 'dailyquyst', 'dahilyquest', 'ndailyquest', 'daailyquest',
                          'dafilyquest', 'rdailyquest', 'dailyqutst', 'dailyjuest', 'dailyqujst', 'xailyquest',
                          'daijlyquest', 'dailyqjuest', 'daiiyquest', 'dailgquest', 'dkailyquest', 'dailoyquest',
                          'daiolyquest', 'djilyquest', 'dailyqxuest', 'daixlyquest', 'dailyquesjt', 'dailyqubst',
                          'dailyquestu', 'kdailyquest', 'wdailyquest', 'dailzyquest', 'dablyquest', 'dailyquent',
                          'dailyquezt', 'dailyquekst', 'dailyquestl', 'dailyquesqt', 'daiclyquest', 'dailysquest',
                          'dailyquesxt', 'daiqlyquest', 'sailyquest', 'dailyqueast', 'dailyequest', 'dailyqnuest',
                          'dailymuest', 'dailyzuest', 'dailyqkest', 'dailyqbuest', 'dailyiuest', 'dailyqueot',
                          'dbilyquest', 'dailyqoest', 'dbailyquest', 'dailoquest', 'dailyqpuest', 'dpilyquest',
                          'dailsquest', 'dhilyquest', 'cailyquest', 'hailyquest', 'daqilyquest', 'dailyqcest',
                          'dailyquhest', 'dwailyquest', 'dnailyquest', 'dailyqqest', 'dailwyquest', 'gdailyquest',
                          'yailyquest', 'dailyquedst', 'dailyquvst', 'dailyqujest', 'dacilyquest', 'dailsyquest',
                          'dailykquest', 'daylyquest', 'daiklyquest', 'dailyguest', 'dgilyquest', 'daiulyquest',
                          'dailyquesh', 'dailjquest', 'daiflyquest', 'dailyquesot', 'doilyquest', 'pailyquest',
                          'daidyquest', 'dailyquesm', 'dailyqueust', 'dailyqruest', 'dailyquwest', 'dailyqupest',
                          'idailyquest', 'dailyzquest', 'daikyquest', 'dailyqyuest', 'jdailyquest', 'dailyquesto',
                          'dailbquest', 'dailyquebt', 'daxilyquest', 'dailzquest', 'dailyquewst', 'dajlyquest',
                          'dailyquesb', 'dailyqvuest', 'dazlyquest', 'dailmquest', 'dailyquvest', 'dnilyquest',
                          'dailgyquest', 'daulyquest', 'dailyqhest', 'dailypquest', 'tdailyquest', 'daijyquest',
                          'da7lyquest', 'da8lyquest', 'da9lyquest', 'da&lyquest', 'da*lyquest', 'da(lyquest',
                          'dai;yquest', 'dai/yquest', 'dai.yquest', 'dai,yquest', 'dai?yquest', 'dai>yquest',
                          'dai<yquest', 'dail5quest', 'dail6quest', 'dail7quest', 'dail%quest', 'dail^quest',
                          'dail&quest', 'daily`uest', 'daily1uest', 'daily2uest', 'daily~uest', 'daily!uest',
                          'daily@uest', 'dailyq6est', 'dailyq7est', 'dailyq8est', 'dailyq^est', 'dailyq&est',
                          'dailyq*est', 'dailyqu4st', 'dailyqu3st', 'dailyqu2st', 'dailyqu$st', 'dailyqu#st',
                          'dailyqu@st', 'dailyques4', 'dailyques5', 'dailyques6', 'dailyques$', 'dailyques%',
                          'dailyques^', 'tdq', 'db', 'dhq', 'dy', 'qd', 'dq', 'zdq', 'aq', 'sq', 'tq',
                          'dv', 'dfq', 'dqe', 'q', 'wq', 'qdq', 'uq', 'dqy', 'di', 'dt', 'dz', 'zq', 'oq',
                          'mdq', 'dqi', 'gq', 'dqa', 'cq', 'dqj', 'dgq', 'du', 'drq', 'dqh', 'dd', 'gdq', 'dcq', 'hq',
                          'ydq', 'df', 'eq', 'fdq', 'dr', 'wdq', 'dqb', 'dw', 'mq', 'ds', 'dxq', 'dbq', 'dg', 'dqk',
                          'dqw', 'dpq', 'odq', 'nq', 'dyq', 'dsq', 'yq', 'djq', 'duq', 'daq', 'dqu', 'kq', 'edq',
                          'pdq', 'rq', 'bq', 'dqs', 'kdq', 'dqg', 'dqn', 'dvq', 'dql', 'dqm', 'dqq', 'xdq', 'qq', 'dh',
                          'dtq', 'doq', 'dwq', 'dnq', 'dqt', 'dl', 'ndq', 'dqv', 'sdq', 'dlq', 'xq', 'diq', 'lq', 'rdq',
                          'dqx', 'ddq', 'dj', 'dqr', 'pq', 'dm', 'iq', 'dqd', 'dqo', 'bdq', 'dk', 'fq', 'hdq',
                          'jq', 'de', 'dqc', 'dqz', 'dkq', 'udq', 'dqf', 'idq', 'vq', 'jdq', 'deq', 'do', 'dzq', 'dmq',
                          'ldq', 'cdq', 'dn', 'vdq', 'd`', 'd1', 'd2', 'd~', 'd!', 'd@', 'zuests', 'euests', 'qluests',
                          'qjuests', 'qusets', 'quetss', 'uqests', 'qests', 'xquests', 'questsi', 'qulsts', 'quysts',
                          'auests', 'quets', 'quesds', 'tquests', 'quzsts', 'quesst', 'questy', 'quess', 'uests',
                          'qzuests', 'qeusts', 'qusts', 'suests', 'qhuests', 'questj', 'qunests', 'quest', 'questt',
                          'quegsts', 'queusts', 'qulests', 'quesys', 'questss', 'qrests', 'quesjs', 'qumests',
                          'quwests', 'kquests', 'quesgts', 'nquests', 'questsg', 'queshts', 'qubsts', 'qhests',
                          'queslts', 'questo', 'quensts', 'questps', 'questq', 'questsq', 'qucsts', 'queshs', 'quehsts',
                          'qcests', 'quesats', 'qkuests', 'questus', 'hquests', 'questu', 'qtuests', 'queksts',
                          'queasts', 'vuests', 'qsuests', 'questx', 'qzests', 'wuests', 'qsests', 'qukests', 'juests',
                          'queste', 'questsv', 'quists', 'quesrts', 'fquests', 'quedts', 'quxsts', 'uuests', 'quasts',
                          'qbests', 'quesuts', 'kuests', 'questxs', 'qqests', 'quksts', 'questts', 'questgs', 'huests',
                          'quqsts', 'gquests', 'queosts', 'quesms', 'qudests', 'quests', 'qnuests', 'quesits', 'queqts',
                          'qouests', 'qdests', 'quexts', 'qujests', 'questv', 'questsl', 'questso', 'zquests',
                          'quesths', 'qeests', 'qquests', 'qmests', 'quesfs', 'quebsts', 'quetsts', 'quepsts', 'quwsts',
                          'quuests', 'quesets', 'questsn', 'quesis', 'quesjts', 'questm', 'quesos', 'queots', 'qbuests',
                          'quects', 'tuests', 'quefts', 'questi', 'qursts', 'bquests', 'questk', 'questms', 'qnests',
                          'quesbs', 'qussts', 'quewts', 'questsh', 'guests', 'queswts', 'questb', 'queests', 'quaests',
                          'quevsts', 'cuests', 'queists', 'questsx', 'quvsts', 'qwuests', 'questds', 'quesxts',
                          'queets', 'quemts', 'quejsts', 'qguests', 'fuests', 'questsy', 'qyests', 'quesgs', 'qmuests',
                          'questsp', 'queyts', 'yuests', 'qujsts', 'quegts', 'questc', 'quesxs', 'qufests', 'squests',
                          'questws', 'questl', 'questsc', 'queskts', 'quevts', 'quesss', 'quesvts', 'iquests',
                          'quoests', 'queysts', 'qupsts', 'questjs', 'questqs', 'oquests', 'quesps', 'quesas',
                          'quewsts', 'qubests', 'questf', 'qwests', 'questys', 'questp', 'quecsts', 'buests', 'ouests',
                          'questes', 'quzests', 'qvuests', 'quyests', 'qcuests', 'qduests', 'quessts', 'questsz',
                          'dquests', 'quesus', 'quusts', 'questn', 'qfests', 'quesyts', 'quesws', 'pquests', 'quezsts',
                          'questls', 'aquests', 'queszs', 'questz', 'qkests', 'quefsts', 'queuts', 'quesqs', 'equests',
                          'quelsts', 'qlests', 'quelts', 'uquests', 'quebts', 'luests', 'questcs', 'quesks', 'questas',
                          'questa', 'quescs', 'questg', 'quezts', 'questbs', 'qugests', 'qaests', 'qurests', 'qupests',
                          'quesns', 'quespts', 'questns', 'questst', 'quetts', 'quekts', 'quesvs', 'quents', 'qauests',
                          'querts', 'questd', 'quexsts', 'qusests', 'qiests', 'duests', 'questsk', 'quesnts', 'quesqts',
                          'questsd', 'quhsts', 'qumsts', 'questw', 'qutests', 'quvests', 'questsu', 'ruests', 'qpests',
                          'questrs', 'qeuests', 'iuests', 'quesfts', 'queats', 'quepts', 'nuests', 'qvests', 'qruests',
                          'quosts', 'queqsts', 'quiests', 'questh', 'jquests', 'rquests', 'quqests', 'queses',
                          'questks', 'qtests', 'qfuests', 'qugsts', 'qucests', 'questsm', 'questsf', 'cquests',
                          'questfs', 'qutsts', 'questzs', 'quesrs', 'qudsts', 'quesots', 'qoests', 'quejts', 'questsr',
                          'qpuests', 'quxests', 'qxuests', 'qiuests', 'quhests', 'puests', 'quesbts', 'qyuests',
                          'vquests', 'mquests', 'muests', 'queszts', 'questse', 'qunsts', 'questis', 'qgests',
                          'questsw', 'xuests', 'quesdts', 'queits', 'questsa', 'quehts', 'wquests', 'questos', 'qjests',
                          'questr', 'yquests', 'qxests', 'qufsts', 'quesmts', 'lquests', 'questsj', 'questvs',
                          'questsb', 'quersts', 'quescts', 'quesls', 'quemsts', 'quedsts', '`uests', '1uests', '2uests',
                          '~uests', '!uests', '@uests', 'q6ests', 'q7ests', 'q8ests', 'q^ests', 'q&ests', 'q*ests',
                          'qu4sts', 'qu3sts', 'qu2sts', 'qu$sts', 'qu#sts', 'qu@sts', 'ques4s', 'ques5s', 'ques6s',
                          'ques$s', 'ques%s', 'ques^s', 'dailquests', 'daildquests', 'dailyqusets', 'dauilyquests',
                          'dlilyquests', 'udailyquests', 'dailyqusts', 'dailgquests', 'dailqyuests', 'dailyqouests',
                          'dailyquesmts', 'dailyquespts', 'dailywquests', 'qdailyquests', 'daiyquests', 'daiclyquests',
                          'dailyoquests', 'dacilyquests', 'dalyquests', 'dhailyquests', 'dailyquestsx', 'daolyquests',
                          'dailyqursts', 'daqlyquests', 'jdailyquests', 'dailyqueits', 'dailayquests', 'daidyquests',
                          'dailyquestsl', 'dailyquetss', 'dailyqeusts', 'dailvyquests', 'dailyquuests', 'dailyyquests',
                          'daillyquests', 'dailyqduests', 'dailyuqests', 'dailyqueosts', 'dialyquests', 'deailyquests',
                          'daivlyquests', 'dailyquesots', 'daiylquests', 'dailqquests', 'dailyqtuests', 'dailyqests',
                          'dailyquehts', 'dailrquests', 'ailyquests', 'dailyqiuests', 'daylyquests', 'dailyquewsts',
                          'daiwyquests', 'daillquests', 'dilyquests', 'dailyquedsts', 'dailyuests', 'dailyquysts',
                          'damlyquests', 'dailyqueswts', 'dailiyquests', 'dailyquesdts', 'adilyquests', 'daiwlyquests',
                          'daliyquests', 'dailxquests', 'daipyquests', 'adailyquests', 'tailyquests', 'dbailyquests',
                          'dailyzuests', 'damilyquests', 'dailyquefsts', 'dailydquests', 'dailyquestsd', 'dailyquesss',
                          'oailyquests', 'dailyqueets', 'dailyquaests', 'dailyqvuests', 'daityquests', 'dailyquestys',
                          'doailyquests', 'dailyquestws', 'daoilyquests', 'dailyqueests', 'dailyqurests', 'dailyqtests',
                          'dailyquesbs', 'dailyqutests', 'dailyquelsts', 'dawilyquests', 'iailyquests', 'daidlyquests',
                          'eailyquests', 'dailyqgests', 'dailyxquests', 'dailyquestas', 'daitlyquests', 'dailyquehsts',
                          'dlailyquests', 'kailyquests', 'duilyquests', 'dapilyquests', 'dailbquests', 'dailynquests',
                          'dailjyquests', 'dailyqueats', 'dailyquiests', 'daileyquests', 'dailyquesws', 'dailymuests',
                          'dxailyquests', 'dailymquests', 'dailyquejsts', 'dailyxuests', 'dailyjuests', 'dailyquestzs',
                          'dailyquestsq', 'dailyqusests', 'dailyhquests', 'dailyqhests', 'dailyquesvts', 'dailyqauests',
                          'dailyquestsi', 'dailyquestgs', 'dailyquesas', 'dailynuests', 'djailyquests', 'daimyquests',
                          'dhilyquests', 'dailyqucests', 'dailyqqests', 'dailjquests', 'dailyduests', 'dailyqueses',
                          'daihyquests', 'daisyquests', 'dailyaquests', 'tdailyquests', 'dailyquusts', 'dailyqdests',
                          'bdailyquests', 'dadlyquests', 'dailyquestsa', 'dailyqueuts', 'dailyqluests', 'xailyquests',
                          'dzailyquests', 'daiyyquests', 'pailyquests', 'dailyqaests', 'dailyqnuests', 'dailyqmuests',
                          'dailsyquests', 'dailmyquests', 'dailyfuests', 'dtilyquests', 'ddailyquests', 'dailycuests',
                          'dailyjquests', 'dailyquesvs', 'dailyqwests', 'dairyquests', 'dsilyquests', 'dailyiquests',
                          'dailyquestsf', 'dailyquestsj', 'dailyfquests', 'daclyquests', 'dailyquelts', 'dailtquests',
                          'daiayquests', 'dailequests', 'dailyquestsg', 'dailykuests', 'daklyquests', 'dailyquegsts',
                          'daiylyquests', 'daizyquests', 'dailyquesgts', 'doilyquests', 'dailyqueslts', 'dailyquestis',
                          'daulyquests', 'dailyuquests', 'rdailyquests', 'dailsquests', 'dabilyquests', 'dailyquexts',
                          'dadilyquests', 'dailcquests', 'dailyqsuests', 'dailyquestus', 'dajilyquests', 'dailnquests',
                          'dailyquzsts', 'daiplyquests', 'daalyquests', 'dailiquests', 'dailyquessts', 'dailyauests',
                          'dailyquestsk', 'dailyvquests', 'dailyqkests', 'dailyquesgs', 'daislyquests', 'daijlyquests',
                          'dailyqueszts', 'daifyquests', 'darlyquests', 'dailnyquests', 'daixlyquests', 'dgailyquests',
                          'dailyquhests', 'hdailyquests', 'bailyquests', 'failyquests', 'ddilyquests', 'dailyquepsts',
                          'jailyquests', 'dailyquesuts', 'dailyqufsts', 'dahilyquests', 'dailyqueqts', 'daiolyquests',
                          'hailyquests', 'dailwquests', 'dailyqfuests', 'dailyvuests', 'dailyqubests', 'dvailyquests',
                          'dailyqueshs', 'dallyquests', 'daimlyquests', 'dailyquestfs', 'dailyquestsn', 'dailyqbests',
                          'dailyquesfs', 'dailyquepts', 'xdailyquests', 'dailyguests', 'daiulyquests', 'dailtyquests',
                          'dailyquesxts', 'ndailyquests', 'daihlyquests', 'daialyquests', 'diilyquests', 'davlyquests',
                          'daixyquests', 'daieyquests', 'dailyqcuests', 'dailyquesis', 'dailyqbuests', 'dailyquestsc',
                          'dailyquestts', 'dailyqquests', 'dailyquexsts', 'dmailyquests', 'daicyquests', 'dailytuests',
                          'dailyquefts', 'dailyquestsz', 'dailyquestsy', 'dailyquensts', 'dailyquesls', 'dailyqvests',
                          'dailqyquests', 'dailyouests', 'dailyquasts', 'cailyquests', 'dailyquescts', 'dayilyquests',
                          'dzilyquests', 'dailyquestss', 'daeilyquests', 'dailyqupsts', 'dkilyquests', 'dailyquebts',
                          'dtailyquests', 'dailyqucsts', 'dailyluests', 'dailyquesbts', 'daielyquests', 'dailyqueists',
                          'dailytquests', 'dailyqeuests', 'dailyqueshts', 'dasilyquests', 'dailyquekts', 'dailyqiests',
                          'dailyquists', 'dsailyquests', 'dailyqujsts', 'wdailyquests', 'dailyquxests', 'mdailyquests',
                          'railyquests', 'dailaquests', 'daailyquests', 'dwilyquests', 'daikyquests', 'dailyquestxs',
                          'zailyquests', 'daflyquests', 'vdailyquests', 'drilyquests', 'daizlyquests', 'dailyquwests',
                          'dailyquemsts', 'dailysquests', 'dailyquevsts', 'dailyquetsts', 'dailyqudsts', 'djilyquests',
                          'dmilyquests', 'daivyquests', 'dailfquests', 'dfilyquests', 'dailyqumests', 'dailyquewts',
                          'dailyquesjs', 'dailyuuests', 'dailyquksts', 'dailyquesos', 'dailyqulests', 'dailyquejts',
                          'dailyquesits', 'dailyzquests', 'daplyquests', 'dailyquezsts', 'dailyquzests', 'dazilyquests',
                          'dailyquqests', 'dailyquesns', 'daiflyquests', 'dailyquestqs', 'drailyquests', 'daiqyquests',
                          'dailybuests', 'dailyqrests', 'dailyeuests', 'dailyqulsts', 'dailyquesrs', 'dailpyquests',
                          'gdailyquests', 'daelyquests', 'dailyquvests', 'wailyquests', 'dailyqukests', 'dailylquests',
                          'dgilyquests', 'daiilyquests', 'dablyquests', 'lailyquests', 'dailyqsests', 'dailoquests',
                          'dailyyuests', 'daiklyquests', 'dailyqunsts', 'dailyqueszs', 'dailyquesps', 'dailyquestos',
                          'dainyquests', 'dailyqhuests', 'edailyquests', 'dailyruests', 'aailyquests', 'uailyquests',
                          'dailypuests', 'dailyqoests', 'dailyquestsu', 'qailyquests', 'dailcyquests', 'dailyquedts',
                          'dailyquesus', 'dailyquyests', 'sdailyquests', 'dailyqjests', 'dailuyquests', 'dailyquestls',
                          'dailyquestsh', 'dailyquwsts', 'nailyquests', 'sailyquests', 'daxlyquests', 'dailyquecsts',
                          'dwailyquests', 'dailyqyests', 'dailyqubsts', 'ldailyquests', 'dailyquesys', 'daglyquests',
                          'dailuquests', 'dailyqunests', 'dailyqkuests', 'dailyquents', 'dainlyquests', 'yailyquests',
                          'dailvquests', 'dailyqzuests', 'dpailyquests', 'dailyquesrts', 'dailyrquests', 'odailyquests',
                          'dailypquests', 'dailyquestsv', 'daiuyquests', 'dailyqueskts', 'deilyquests', 'dqailyquests',
                          'dailgyquests', 'dailyqugests', 'dailxyquests', 'dyilyquests', 'dailyqueyts', 'dailyquvsts',
                          'dailyqueqsts', 'daildyquests', 'dailyquesxs', 'dailyqxuests', 'dafilyquests', 'dailysuests',
                          'dailyquesks', 'daqilyquests', 'dailyquosts', 'dailybquests', 'dailyqyuests', 'dailyqussts',
                          'dailyquevts', 'dailyquestps', 'dailyquesyts', 'dailyquescs', 'daiblyquests', 'dailyquemts',
                          'fdailyquests', 'dailyqeests', 'dailmquests', 'dailfyquests', 'davilyquests', 'dazlyquests',
                          'dailyqueasts', 'dailyquestns', 'dailyqumsts', 'dailyquestes', 'dailyqmests', 'pdailyquests',
                          'dailyqpests', 'idailyquests', 'dailzquests', 'daslyquests', 'dpilyquests', 'dakilyquests',
                          'dailryquests', 'dcilyquests', 'dailzyquests', 'dxilyquests', 'dawlyquests', 'dailyquesds',
                          'dailyquesfts', 'dailyqpuests', 'dailyqueusts', 'dailyquestsw', 'daigyquests', 'dailyqfests',
                          'dailyquestsp', 'dailyquects', 'dailyquesnts', 'dailyqruests', 'daibyquests', 'dailkquests',
                          'mailyquests', 'zdailyquests', 'dailyquestjs', 'dailyquestvs', 'dailyquxsts', 'danilyquests',
                          'dailyquestms', 'diailyquests', 'dailyqlests', 'cdailyquests', 'dailyquhsts', 'darilyquests',
                          'dailyquetts', 'dailyquesets', 'dailhyquests', 'dailyqudests', 'dailyqxests', 'dailyqutsts',
                          'dalilyquests', 'dailyequests', 'dailyqjuests', 'dailyquestsr', 'dailyqwuests',
                          'dailygquests', 'dailyquersts', 'dailpquests', 'kdailyquests', 'dailhquests', 'dailyquesths',
                          'duailyquests', 'dnailyquests', 'dailyquesjts', 'dailyquqsts', 'dailyquestst', 'dailbyquests',
                          'vailyquests', 'dyailyquests', 'dailyqguests', 'dailyqueksts', 'daijyquests', 'dcailyquests',
                          'dkailyquests', 'dailyqueysts', 'dfailyquests', 'dailyqugsts', 'dailyquestsb', 'dailyquoests',
                          'dailyqupests', 'dailwyquests', 'dajlyquests', 'dailyquesqs', 'dailycquests', 'datlyquests',
                          'daiiyquests', 'dailkyquests', 'dnilyquests', 'dailyquestse', 'dailyiuests', 'dailyquestds',
                          'dailykquests', 'dailyqufests', 'dailyqnests', 'dailyquesms', 'dailyquegts', 'dqilyquests',
                          'gailyquests', 'dailyquestks', 'dailyquestbs', 'dailywuests', 'dailyquestso', 'dailyqujests',
                          'dagilyquests', 'daiqlyquests', 'dbilyquests', 'daioyquests', 'dailyquerts', 'dailyquesats',
                          'datilyquests', 'dailyquestcs', 'dailyquestrs', 'dvilyquests', 'dairlyquests', 'dailyqcests',
                          'daxilyquests', 'danlyquests', 'dailyhuests', 'dailoyquests', 'dailyqzests', 'dailyquesqts',
                          'dahlyquests', 'ydailyquests', 'dailyquestsm', 'dailyquebsts', 'dailyqueots', 'dailyquezts',
                          'daiglyquests', 'da7lyquests', 'da8lyquests', 'da9lyquests', 'da&lyquests', 'da*lyquests',
                          'da(lyquests', 'dai;yquests', 'dai/yquests', 'dai.yquests', 'dai,yquests', 'dai?yquests',
                          'dai>yquests', 'dai<yquests', 'dail5quests', 'dail6quests', 'dail7quests', 'dail%quests',
                          'dail^quests', 'dail&quests', 'daily`uests', 'daily1uests', 'daily2uests', 'daily~uests',
                          'daily!uests', 'daily@uests', 'dailyq6ests', 'dailyq7ests', 'dailyq8ests', 'dailyq^ests',
                          'dailyq&ests', 'dailyq*ests', 'dailyqu4sts', 'dailyqu3sts', 'dailyqu2sts', 'dailyqu$sts',
                          'dailyqu#sts', 'dailyqu@sts', 'dailyques4s', 'dailyques5s', 'dailyques6s', 'dailyques$s',
                          'dailyques%s', 'dailyques^s', 'xdqs', 'fqs', 'dqss', 'qs', 'dzs', 'dqsi', 'dqsd', 'dds',
                          'dqqs', 'daqs', 'jdqs', 'kqs', 'dss', 'qds', 'dqcs', 'dqse', 'dpqs', 'zdqs', 'dqbs', 'dqns',
                          'yqs', 'djs', 'dqsg', 'dqsw', 'mdqs', 'dqas', 'tqs', 'dqes', 'idqs', 'dks', 'dvs', 'dqsu',
                          'djqs', 'edqs', 'qdqs', 'pdqs', 'dqds', 'dbs', 'dgs', 'xqs', 'wqs', 'dgqs',
                          'duqs', 'jqs', 'dqsk', 'adqs', 'dhs', 'dbqs', 'dps', 'dqsb', 'dhqs', 'dis', 'dqsr', 'tdqs',
                          'dqsa', 'dqms', 'vqs', 'dqvs', 'zqs', 'cdqs', 'dqus', 'dqts', 'aqs', 'dys', 'drs', 'dws',
                          'dqsj', 'dqys', 'dcqs', 'fdqs', 'mqs', 'bqs', 'dfs', 'dqsl', 'dsqs', 'dqsx', 'dyqs', 'rdqs',
                          'sqs', 'dzqs', 'nqs', 'dnqs', 'uqs', 'dqls', 'hqs', 'pqs', 'lqs', 'doqs', 'qqs',
                          'dqjs', 'drqs', 'wdqs', 'ydqs', 'dms', 'vdqs', 'dfqs', 'dns', 'dqis', 'dqsc', 'dmqs', 'dtqs',
                          'dqst', 'dqos', 'dts', 'dqsv', 'dqso', 'bdqs', 'dqsq', 'dos', 'dqsm', 'dqxs', 'dqsf', 'udqs',
                          'dus', 'dvqs', 'hdqs', 'dqgs', 'sdqs', 'iqs', 'deqs', 'diqs', 'ddqs', 'gqs', 'dcs', 'das',
                          'oqs', 'dqps', 'dqsp', 'kdqs', 'eqs', 'dqzs', 'dqsh', 'dlqs', 'dls', 'dqsz', 'dqks', 'dqhs',
                          'ldqs', 'cqs', 'gdqs', 'ndqs', 'dqws', 'dkqs', 'dqsy', 'dqrs', 'dqsn', 'dqfs', 'odqs', 'dwqs',
                          'dxqs', 'd`s', 'd1s', 'd2s', 'd~s', 'd!s', 'd@s', 'dquset', 'dqutest', 'dqeust', 'dquet',
                          'qduest', 'dquert', 'adquest', 'duqest', 'jquest', 'dques', 'dkuest', 'dquaest', 'dquets',
                          'pquest', 'dquent', 'dsuest', 'dqucest', 'ydquest', 'dquepst', 'dquerst', 'dqnest', 'dqust',
                          'dqxest', 'dquvest', 'dquecst', 'qdquest', 'dquvst', 'dqiest', 'zquest', 'dquept', 'dqudst',
                          'dqueast', 'dquesy', 'dzuest', 'duquest', 'dquelt', 'dquestj', 'dgquest', 'dqpest', 'duest',
                          'dqusst', 'dqbuest', 'dquesz', 'dqmest', 'dwuest', 'dqeuest', 'dquesj', 'bquest', 'dqusest',
                          'dyuest', 'dquest', 'dqest', 'dquesht', 'ndquest', 'dquezst', 'xdquest', 'rquest', 'dquespt',
                          'dquefst', 'dqiuest', 'dqfuest', 'dquesto', 'dqjest', 'dqxuest', 'dquesty', 'dquestb',
                          'gdquest', 'dquesmt', 'dyquest', 'dquestt', 'ldquest', 'dqguest', 'dqueyst', 'dqueso',
                          'dqueust', 'dquesu', 'dqubst', 'dquelst', 'dqbest', 'dquegt', 'dqeest', 'dquestl', 'dqgest',
                          'dqunst', 'iquest', 'dqueht', 'dqueet', 'dquist', 'dqujst', 'dquesth', 'dpuest', 'dquestp',
                          'dquwest', 'dquesdt', 'douest', 'dqujest', 'dqueost', 'dqhest', 'dmquest', 'dquesa',
                          'daquest', 'dquehst', 'dqutst', 'dbquest', 'dqurest', 'dqueqst', 'dquestd', 'mquest',
                          'dqueist', 'dquqst', 'dqucst', 'dqcuest', 'dqquest', 'jdquest', 'dhuest', 'dqueyt', 'dquesi',
                          'dquesjt', 'dquesxt', 'dtuest', 'dquekt', 'dquesnt', 'lquest', 'dquesut', 'dqnuest',
                          'dqauest', 'dquhest', 'dquesst', 'dqufest', 'dqugst', 'dquesk', 'drquest', 'dqueset',
                          'dquesd', 'duuest', 'dquesm', 'cquest', 'dqvest', 'dquejt', 'dquewst', 'dquekst', 'dlquest',
                          'tdquest', 'dquexst', 'doquest', 'dquestn', 'dnquest', 'dmuest', 'cdquest', 'dqueit',
                          'nquest', 'sdquest', 'dquesti', 'idquest', 'hquest', 'dquesg', 'dqufst', 'dduest', 'diquest',
                          'dquemt', 'dquedst', 'udquest', 'dqcest', 'dquesvt', 'xquest', 'fdquest', 'dquast', 'dquyest',
                          'dqduest', 'aquest', 'dquyst', 'dguest', 'dquevt', 'dquoest', 'dquesb', 'dqueqt', 'dquesqt',
                          'dbuest', 'dquust', 'dqzuest', 'dqueut', 'dquestz', 'dquestf', 'dqjuest', 'dqsuest',
                          'zdquest', 'dqurst', 'dqueat', 'dquost', 'dquext', 'djuest', 'oquest', 'wquest', 'edquest',
                          'dqupest', 'dqsest', 'dqhuest', 'dxuest', 'dquestq', 'mdquest', 'dquestv', 'dqumest',
                          'odquest', 'gquest', 'diuest', 'dquewt', 'dqzest', 'dqupst', 'tquest', 'dqlest', 'dquxest',
                          'ddquest', 'dquesw', 'vdquest', 'dqvuest', 'dqouest', 'rdquest', 'dqubest', 'dquesit',
                          'dpquest', 'dqkest', 'dfuest', 'squest', 'dqueot', 'dquestg', 'pdquest', 'dquegst', 'dcuest',
                          'dquesta', 'dquezt', 'dquesgt', 'dwquest', 'deuest', 'dquesl', 'dquese', 'dquqest', 'dqulst',
                          'dquestr', 'dqudest', 'dquesot', 'dqukst', 'dnuest', 'dquesx', 'dquesrt', 'dquesat',
                          'dquevst', 'dqwuest', 'dfquest', 'dquesq', 'dqaest', 'dqoest', 'dquejst', 'dquesc', 'dquesv',
                          'dquemst', 'dquxst', 'dqueszt', 'dquett', 'dqruest', 'dquesn', 'uquest', 'dqwest', 'dqpuest',
                          'dquesp', 'dquuest', 'dqrest', 'dqueest', 'dqumst', 'dquestm', 'dquestx', 'dquiest',
                          'dquestw', 'wdquest', 'dquebst', 'dqueswt', 'dquect', 'dvquest', 'hdquest', 'dvuest',
                          'dquetst', 'dquzest', 'dquhst', 'dqluest', 'dqtuest', 'vquest', 'dqyest', 'dqtest', 'dquenst',
                          'dquwst', 'dqfest', 'dqueste', 'kquest', 'dequest', 'dqyuest', 'druest', 'dqueskt', 'dquestc',
                          'dquesbt', 'dquess', 'dqunest', 'dquzst', 'dqqest', 'dquestu', 'dqugest', 'dauest', 'dqueslt',
                          'dquesct', 'dsquest', 'dqueft', 'dquesf', 'dcquest', 'equest', 'dqkuest', 'dqulest', 'dqdest',
                          'dquesyt', 'dqmuest', 'dquesh', 'dquedt', 'qquest', 'dquesr', 'dkquest', 'dzquest', 'yquest',
                          'dhquest', 'djquest', 'kdquest', 'dquebt', 'dquestk', 'dtquest', 'bdquest', 'dxquest',
                          'dquesft', 'dluest', 'fquest', 'dqukest', 'd`uest', 'd1uest', 'd2uest', 'd~uest', 'd!uest',
                          'd@uest', 'dq6est', 'dq7est', 'dq8est', 'dq^est', 'dq&est', 'dq*est', 'dqu4st', 'dqu3st',
                          'dqu2st', 'dqu$st', 'dqu#st', 'dqu@st', 'dques4', 'dques5', 'dques6', 'dques$', 'dques%',
                          'dques^', 'dqeusts', 'duqests', 'dquesas', 'dqguests', 'dquestzs', 'dquestns', 'dqusts',
                          'hdquests', 'dqueests', 'dqaests', 'dqpests', 'dqdests', 'dqests', 'dqquests', 'dqusets',
                          'dquesgts', 'dqueqts', 'dquestos', 'dquetss', 'dquaests', 'jdquests', 'dgquests', 'dquewts',
                          'dquestsh', 'dquestsg', 'dcuests', 'dqueits', 'dqursts', 'dquestus', 'dqueists', 'dqsests',
                          'ddquests', 'dqnests', 'dquestxs', 'dquuests', 'dqbuests', 'dquwsts', 'dqunests', 'dqfests',
                          'dquestcs', 'dqueats', 'dqudests', 'dqmests', 'vdquests', 'dquestks', 'dquesyts', 'douests',
                          'dquesdts', 'dqunsts', 'dqudsts', 'djquests', 'dyquests', 'dquwests', 'dquezts', 'dquestsk',
                          'dquevsts', 'dnquests', 'dquestsb', 'idquests', 'cdquests', 'dquesths', 'dqubests',
                          'dqueosts', 'dqyuests', 'dquezsts', 'dquestsj', 'dquersts', 'dqzests', 'dquestsm', 'dquedsts',
                          'dquehts', 'dqueshts', 'dquesms', 'dxuests', 'dvquests', 'dquesuts', 'dquosts', 'dquessts',
                          'dqueasts', 'dquejts', 'dquesgs', 'dquesits', 'dqxuests', 'dqumests', 'dfuests', 'dquescts',
                          'dquestds', 'dqluests', 'deuests', 'dquesys', 'dquists', 'dquestsz', 'dquexsts', 'dquebts',
                          'dquestts', 'dquefsts', 'xdquests', 'dbquests', 'dquesets', 'pdquests', 'dquiests',
                          'dquestsc', 'dquestss', 'dqueksts', 'dquestsa', 'zdquests', 'dqrests', 'dquestws', 'dqueusts',
                          'dqulests', 'dqnuests', 'dquesss', 'dquefts', 'dtquests', 'dqueets', 'dquesvs', 'dqulsts',
                          'dqueszs', 'dquesbs', 'dquestsi', 'dqcests', 'dduests', 'dqumsts', 'duquests', 'dqucests',
                          'dqueuts', 'dwuests', 'dqlests', 'dqvests', 'dquqests', 'dquesws', 'dqjuests', 'dsquests',
                          'dqubsts', 'dqupests', 'dquects', 'dquesps', 'dquescs', 'dqutsts', 'dqiests', 'dquesnts',
                          'dquemts', 'dqkuests', 'dquesrs', 'dquestsu', 'dquestvs', 'dpquests', 'dquedts', 'dquestst',
                          'gdquests', 'dqueslts', 'dquesfs', 'dxquests', 'dqugsts', 'dlquests', 'dvuests', 'dbuests',
                          'dqueskts', 'dquestgs', 'dquusts', 'duuests', 'edquests', 'dqueszts', 'dqiuests', 'drquests',
                          'dtuests', 'diquests', 'dqtuests', 'dquestjs', 'dquesbts', 'dqoests', 'dauests', 'dquhests',
                          'dyuests', 'dkquests', 'dquesats', 'dqwests', 'dzquests', 'dquesvts', 'dzuests', 'dqjests',
                          'dpuests', 'dquestys', 'dqpuests', 'dquxsts', 'dquesls', 'dkuests', 'dquerts', 'dguests',
                          'dquesqs', 'sdquests', 'dqueysts', 'dqueswts', 'dqueots', 'dquyests', 'adquests', 'dquzests',
                          'dquents', 'dqhuests', 'diuests', 'dquestsx', 'dquesis', 'dquestfs', 'dqueses', 'dquzsts',
                          'dquestsr', 'dquepts', 'dquesus', 'dqtests', 'dquesos', 'dquestas', 'dquesfts', 'dqxests',
                          'dquesns', 'dquetsts', 'dqfuests', 'dqeests', 'dquxests', 'dquesqts', 'dquelts', 'dquvsts',
                          'dqujsts', 'kdquests', 'dqufests', 'qdquests', 'dquvests', 'dquestls', 'dquestbs', 'dqeuests',
                          'dquestps', 'dquesks', 'dquoests', 'ndquests', 'odquests', 'dqbests', 'dquestsf', 'dqgests',
                          'dhquests', 'dqukests', 'dmuests', 'dquestsq', 'druests', 'dquespts', 'dquebsts', 'dquysts',
                          'dquegts', 'dquksts', 'dqucsts', 'mdquests', 'dquestrs', 'dquegsts', 'dquekts', 'dequests',
                          'dqcuests', 'dqueshs', 'dqauests', 'dqyests', 'wdquests', 'dquestsd', 'dqussts', 'dquestsv',
                          'dmquests', 'dqhests', 'dqueyts', 'dqupsts', 'dquesots', 'dqouests', 'doquests', 'dqueqsts',
                          'daquests', 'dquestms', 'dhuests', 'dqufsts', 'dqqests', 'dquesxts', 'dquepsts', 'dqugests',
                          'udquests', 'dquesjts', 'dqduests', 'dquecsts', 'dqkests', 'dquetts', 'dquevts', 'dqusests',
                          'dquemsts', 'dqzuests', 'rdquests', 'djuests', 'dquestsp', 'dquesds', 'dquejsts', 'dquestsy',
                          'dwquests', 'dquasts', 'dquestso', 'dnuests', 'ydquests', 'dqruests', 'dquehsts', 'dquestsl',
                          'dquestes', 'fdquests', 'dqutests', 'dquexts', 'dquhsts', 'tdquests', 'dquesrts', 'dquestsw',
                          'dluests', 'ldquests', 'dqurests', 'dqujests', 'dquestsn', 'dqmuests', 'dquestse', 'dquesmts',
                          'dcquests', 'dquensts', 'dquestqs', 'dquesxs', 'dquqsts', 'dquewsts', 'dqvuests', 'dqsuests',
                          'dquesjs', 'bdquests', 'dquestis', 'dsuests', 'dfquests', 'dqwuests', 'dquelsts', 'd`uests',
                          'd1uests', 'd2uests', 'd~uests', 'd!uests', 'd@uests', 'dq6ests', 'dq7ests', 'dq8ests',
                          'dq^ests', 'dq&ests', 'dq*ests', 'dqu4sts', 'dqu3sts', 'dqu2sts', 'dqu$sts', 'dqu#sts',
                          'dqu@sts', 'dques4s', 'dques5s', 'dques6s', 'dques$s', 'dques%s', 'dques^s', 'daiklyq',
                          'daiylq', 'dilyq', 'ydailyq', 'dailyqn', 'daclyq', 'daiyq', 'dailbq', 'udailyq', 'daidlyq',
                          'dailyyq', 'bailyq', 'dainlyq', 'dailq', 'dailyqz', 'dazilyq', 'dalyq', 'dhilyq',
                          'dailwyq', 'dailyqv', 'dailyqy', 'dailqy', 'ailyq', 'dialyq', 'dahilyq', 'daliyq', 'dkilyq',
                          'dailcyq', 'daklyq', 'dailyc', 'zdailyq', 'dailyfq', 'idailyq', 'dailyd', 'daileyq',
                          'vdailyq', 'daijlyq', 'daihyq', 'dcailyq', 'dasilyq', 'adilyq', 'daixlyq', 'pailyq', 'dailyf',
                          'dailyjq', 'daoilyq', 'dailymq', 'dzailyq', 'tailyq', 'dailyr', 'davlyq', 'dailyq',
                          'dailyqa', 'dailyv', 'dgailyq', 'dailbyq', 'dxailyq', 'qailyq', 'dzilyq', 'daityq', 'dailyt',
                          'mailyq', 'xailyq', 'daildyq', 'djilyq', 'dailyqe', 'dailyqb', 'daqlyq', 'doailyq', 'dailmq',
                          'dailsq', 'dadlyq', 'dazlyq', 'dauilyq', 'dailya', 'aailyq', 'daialyq', 'dagilyq', 'dailyw',
                          'dailtyq', 'daiilyq', 'daimyq', 'dailzq', 'dhailyq', 'dakilyq', 'dafilyq', 'failyq', 'dlilyq',
                          'dailyqm', 'dailyqw', 'daplyq', 'dailyzq', 'dajlyq', 'dawlyq', 'daelyq', 'dailiyq', 'railyq',
                          'daioyq', 'daiflyq', 'diilyq', 'dailryq', 'dailyqh', 'dailywq', 'dailrq', 'duilyq', 'cdailyq',
                          'dailoq', 'dyilyq', 'dabilyq', 'dailiq', 'dailyqt', 'fdailyq', 'ddailyq', 'ndailyq', 'dailvq',
                          'dailyqi', 'dacilyq', 'dailyqg', 'daiulyq', 'dailuq', 'daifyq', 'daiuyq', 'dxilyq', 'dailyk',
                          'daailyq', 'dailycq', 'dailhyq', 'jailyq', 'dyailyq', 'dailyqq', 'damlyq',
                          'dvailyq', 'dailjyq', 'dajilyq', 'dailyi', 'dailqq', 'daitlyq', 'dnilyq', 'gdailyq', 'daiyyq',
                          'daylyq', 'dailyj', 'daqilyq', 'diailyq', 'dalilyq', 'dailyqr', 'daisyq', 'daiqlyq', 'daivyq',
                          'daislyq', 'nailyq', 'dmilyq', 'dailnq', 'yailyq', 'dailwq', 'daimlyq', 'dailoyq', 'dailayq',
                          'dailyqf', 'dailqyq', 'daulyq', 'dgilyq', 'dailuyq', 'uailyq', 'dsilyq', 'dsailyq', 'dailaq',
                          'dpailyq', 'dailyqd', 'dailyqc', 'darilyq', 'sailyq', 'dfailyq', 'dailxq', 'dailym', 'doilyq',
                          'dailjq', 'daalyq', 'mdailyq', 'dqailyq', 'dailydq', 'daigyq', 'daileq', 'dairyq', 'daicyq',
                          'dallyq', 'drilyq', 'daillyq', 'dailynq', 'adailyq', 'vailyq', 'daivlyq', 'daiblyq',
                          'dailpyq', 'daieyq', 'dailfq', 'dailmyq', 'dailysq', 'dailxyq', 'daolyq', 'dailyvq',
                          'dailyeq', 'daiolyq', 'daipyq', 'dailyuq', 'daizlyq', 'danilyq', 'dnailyq', 'dablyq',
                          'dairlyq', 'wailyq', 'deailyq', 'dailybq', 'daijyq', 'daiwyq', 'dailypq', 'dvilyq', 'xdailyq',
                          'oailyq', 'dawilyq', 'dailygq', 'daillq', 'dtailyq', 'dailykq', 'dainyq', 'daglyq', 'hdailyq',
                          'gailyq', 'dailkyq', 'daiplyq', 'dailye', 'dailyhq', 'daiayq', 'iailyq', 'dailyqj', 'dbilyq',
                          'dbailyq', 'dtilyq', 'dahlyq', 'daielyq', 'davilyq', 'daizyq', 'hailyq', 'deilyq', 'dailyn',
                          'dwilyq', 'daikyq', 'dailkq', 'zailyq', 'dailsyq', 'daxlyq', 'dcilyq', 'dailyaq', 'odailyq',
                          'cailyq', 'daidyq', 'dailzyq', 'daibyq', 'daiwlyq', 'dailyqs', 'dailyqx', 'dailyoq',
                          'rdailyq', 'daiylyq', 'danlyq', 'dailyb', 'sdailyq', 'dailnyq', 'dwailyq', 'datilyq',
                          'dapilyq', 'duailyq', 'dailgq', 'daixyq', 'darlyq', 'ddilyq', 'dailpq', 'dfilyq', 'dailgyq',
                          'lailyq', 'daiclyq', 'dmailyq', 'eailyq', 'dailyqp', 'dailys', 'dailyu', 'dqilyq', 'dayilyq',
                          'daihlyq', 'dpilyq', 'daeilyq', 'daiiyq', 'edailyq', 'dlailyq', 'dailyy', 'dailyqo',
                          'dailyrq', 'dailyo', 'datlyq', 'dailtq', 'tdailyq', 'daslyq', 'dailyz', 'dailhq', 'kdailyq',
                          'dailytq', 'damilyq', 'daiglyq', 'jdailyq', 'dailyh', 'dailfyq', 'dailyqk',
                          'daildq', 'dailylq', 'daiqyq', 'wdailyq', 'dailyiq', 'dailyl', 'djailyq', 'dailyg', 'dailyql',
                          'kailyq', 'dkailyq', 'bdailyq', 'pdailyq', 'dailvyq', 'dailcq', 'ldailyq', 'daxilyq',
                          'dadilyq', 'qdailyq', 'drailyq', 'daflyq', 'dailyqu', 'da7lyq', 'da8lyq', 'da9lyq', 'da&lyq',
                          'da*lyq', 'da(lyq', 'dai;yq', 'dai/yq', 'dai.yq', 'dai,yq', 'dai?yq', 'dai>yq', 'dai<yq',
                          'dail5q', 'dail6q', 'dail7q', 'dail%q', 'dail^q', 'dail&q', 'daily`', 'daily1', 'daily2',
                          'daily~', 'daily!', 'daily@', 'daialyqs', 'ailyqs', 'dailqs', 'daiylqs', 'pdailyqs', 'dilyqs',
                          'daiyqs', 'dailytqs', 'hdailyqs', 'daixlyqs', 'davilyqs', 'dailyqbs', 'daildqs', 'dailyas',
                          'udailyqs', 'dailqys', 'daliyqs', 'adilyqs', 'dtailyqs', 'dialyqs', 'dcailyqs', 'daipyqs',
                          'daihlyqs', 'dqailyqs', 'dairlyqs', 'dmilyqs', 'dailaqs', 'dqilyqs', 'dahlyqs', 'sailyqs',
                          'dailoyqs', 'dailyqss', 'adailyqs', 'dailylqs', 'dailyis', 'dailyqso', 'dailcqs', 'daiylyqs',
                          'dalyqs', 'dailyjs', 'drailyqs', 'daijyqs', 'dailyqsz', 'dailyls', 'dailjyqs', 'dailzyqs',
                          'daizyqs', 'dailyqsh', 'dailyqsd', 'daimyqs', 'daiiyqs', 'dacilyqs', 'yailyqs', 'zdailyqs',
                          'dailyqsw', 'dailyns', 'dailyys', 'idailyqs', 'dfilyqs', 'railyqs', 'wdailyqs', 'dalilyqs',
                          'dailyrqs', 'dallyqs', 'bdailyqs', 'dailyqns', 'duailyqs', 'dagilyqs', 'dailybs', 'dailvqs',
                          'dailyfqs', 'dajlyqs', 'dafilyqs', 'dailyqjs', 'dailkqs', 'dailoqs', 'dailiqs', 'dailwqs',
                          'uailyqs', 'dailwyqs', 'zailyqs', 'ddailyqs', 'daiklyqs', 'daeilyqs', 'daiplyqs', 'dailhyqs',
                          'pailyqs', 'dailtqs', 'dhailyqs', 'nailyqs', 'damlyqs', 'djailyqs', 'daslyqs', 'dailyqsy',
                          'daidlyqs', 'dawilyqs', 'deilyqs', 'dailyqse', 'dailyks', 'dzailyqs', 'dailyqzs', 'qdailyqs',
                          'daiwlyqs', 'hailyqs', 'dxilyqs', 'dailyws', 'dailypqs', 'dailyqas', 'dailyhqs',
                          'dailhqs', 'daityqs', 'dazilyqs', 'dailykqs', 'dailsqs', 'daplyqs', 'daailyqs', 'datilyqs',
                          'dailyxqs', 'dmailyqs', 'dadilyqs', 'gailyqs', 'dailyqgs', 'dailuqs', 'daileyqs', 'dhilyqs',
                          'dailyqsa', 'dsailyqs', 'dairyqs', 'dnailyqs', 'daelyqs', 'daisyqs', 'dailyzqs', 'dailymqs',
                          'dailyqrs', 'dailyss', 'dailyqfs', 'dailydqs', 'dazlyqs', 'dailyqls', 'daigyqs', 'duilyqs',
                          'daxlyqs', 'dcilyqs', 'daifyqs', 'kdailyqs', 'dailbqs', 'aailyqs', 'dailyqsn', 'dlailyqs',
                          'daclyqs', 'dailyqqs', 'daidyqs', 'daileqs', 'daflyqs', 'tailyqs', 'dkailyqs', 'dailyqks',
                          'dailyyqs', 'dailyiqs', 'daicyqs', 'dayilyqs', 'darlyqs', 'dailyqsk', 'dailnqs', 'dvilyqs',
                          'darilyqs', 'daiwyqs', 'dailyqms', 'xdailyqs', 'daiqyqs', 'sdailyqs', 'daislyqs', 'dailjqs',
                          'daivlyqs', 'djilyqs', 'daiayqs', 'dailyes', 'dailzqs', 'dailyjqs', 'daieyqs', 'dnilyqs',
                          'dailyqsp', 'dailyqsf', 'oailyqs', 'dailmqs', 'daqlyqs', 'jdailyqs', 'dailyqsx', 'eailyqs',
                          'dzilyqs', 'mdailyqs', 'odailyqs', 'dakilyqs', 'dailyqds', 'dwailyqs', 'dailyoqs', 'dailsyqs',
                          'dailyuqs', 'dailyqhs', 'dailyqsv', 'dailgqs', 'dailyqsr', 'ndailyqs', 'dgailyqs', 'dawlyqs',
                          'mailyqs', 'diailyqs', 'dtilyqs', 'dailyhs', 'dailyms', 'dailyqws', 'ddilyqs', 'dpailyqs',
                          'dailpyqs', 'dailyqcs', 'ldailyqs', 'daiuyqs', 'dsilyqs', 'kailyqs', 'dailyqsc', 'dailywqs',
                          'dainyqs', 'dyilyqs', 'dailyvs', 'dailtyqs', 'doailyqs', 'dgilyqs', 'cailyqs', 'daillqs',
                          'dasilyqs', 'dailyqis', 'danilyqs', 'datlyqs', 'daulyqs', 'dailxqs', 'dvailyqs', 'dailqyqs',
                          'dailyos', 'deailyqs', 'daijlyqs', 'dablyqs', 'dailyqsb', 'daolyqs', 'dailyqsm', 'dainlyqs',
                          'daqilyqs', 'daihyqs', 'dkilyqs', 'daalyqs', 'dailyqst', 'daillyqs', 'dailycs', 'dailyps',
                          'dailygs', 'dailuyqs', 'dailrqs', 'daiblyqs', 'dabilyqs', 'dpilyqs', 'dailyqes', 'bailyqs',
                          'doilyqs', 'dailynqs', 'dailqqs', 'davlyqs', 'dailyqsu', 'dailyqsq', 'dailyds', 'jailyqs',
                          'dailyqsj', 'dailysqs', 'dbailyqs', 'dailcyqs', 'daivyqs', 'lailyqs', 'daiolyqs', 'dailyqxs',
                          'dailnyqs', 'xailyqs', 'dailyqsg', 'vailyqs', 'dailxyqs', 'daiglyqs', 'danlyqs', 'daiyyqs',
                          'daiilyqs', 'dailyvqs', 'dailyqps', 'dbilyqs', 'diilyqs', 'dailayqs', 'daikyqs', 'daixyqs',
                          'dwilyqs', 'dailmyqs', 'dailyzs', 'dailiyqs', 'dailyrs', 'daioyqs', 'dailyqys', 'dailybqs',
                          'daxilyqs', 'dailfyqs', 'dapilyqs', 'daibyqs', 'daglyqs', 'dailfqs', 'daylyqs', 'daildyqs',
                          'daiclyqs', 'rdailyqs', 'dailyts', 'dailycqs', 'dailyeqs', 'dailyqsl', 'dlilyqs', 'daiqlyqs',
                          'dailyqts', 'fdailyqs', 'edailyqs', 'dailvyqs', 'drilyqs', 'dailgyqs', 'dadlyqs', 'dailyqvs',
                          'daklyqs', 'daitlyqs', 'dailyus', 'daoilyqs', 'iailyqs', 'daimlyqs', 'dyailyqs', 'dailryqs',
                          'dailkyqs', 'damilyqs', 'dailyqos', 'dailbyqs', 'daielyqs', 'dailyqsi', 'tdailyqs',
                          'vdailyqs', 'dxailyqs', 'cdailyqs', 'qailyqs', 'daiflyqs', 'daiulyqs', 'dailpqs', 'gdailyqs',
                          'ydailyqs', 'daizlyqs', 'failyqs', 'dailyqus', 'dauilyqs', 'dailygqs', 'dfailyqs', 'dailyfs',
                          'wailyqs', 'dailyaqs', 'dajilyqs', 'dahilyqs', 'da7lyqs', 'da8lyqs', 'da9lyqs', 'da&lyqs',
                          'da*lyqs', 'da(lyqs', 'dai;yqs', 'dai/yqs', 'dai.yqs', 'dai,yqs', 'dai?yqs', 'dai>yqs',
                          'dai<yqs', 'dail5qs', 'dail6qs', 'dail7qs', 'dail%qs', 'dail^qs', 'dail&qs', 'daily`s',
                          'daily1s', 'daily2s', 'daily~s', 'daily!s', 'daily@s', 'reorll', 'reoll', 'reryll', 'rerooll',
                          'rerol', 'rroll', 'rerollc', 'resoll', 'reroll', 'rreoll', 'rqeroll', 'reyroll', 'sreroll',
                          'rerhll', 'rnroll', 'rerll', 'rvroll', 'rerlol', 'rerolnl', 'rtroll', 'rerill', 'rerohll',
                          'erroll', 'rezroll', 'rercll', 'rerolyl', 'eroll', 'reromll', 'rerolwl', 'jreroll', 'reuoll',
                          'rerqll', 'riroll', 'rexoll', 'roroll', 'zeroll', 'rerull', 'rerwll', 'rerotl', 'reroxll',
                          'rerolc', 'rerold', 'rerollr', 'rerolb', 'rerioll', 'rneroll', 'rceroll', 'reroltl', 'refoll',
                          'retroll', 'rferoll', 'reroyl', 'rerolt', 'rerollx', 'rervoll', 'seroll', 'rerolln', 'jeroll',
                          'rerkoll', 'vreroll', 'rerocll', 'renoll', 'rertll', 'rekoll', 'ceroll', 'rewroll', 'rermoll',
                          'reroell', 'reroill', 'rjroll', 'rejroll', 'rerolel', 'reproll', 'redoll', 'rerolul',
                          'preroll', 'rerodll', 'rerollt', 'rerollq', 'rergll', 'rreroll', 'rerollj', 'treroll',
                          'rerolh', 'rerollm', 'rseroll', 'rerollp', 'kreroll', 'rereoll', 'teroll', 'ryroll', 'rermll',
                          'rerokll', 'reaoll', 'rerolx', 'rerkll', 'rerolll', 'rerollo', 'rerolbl', 'rerzoll', 'rerojl',
                          'rerloll', 'rerolp', 'rerobl', 'reruoll', 'rerotll', 'reoroll', 'rcroll', 'rerolm', 'rerovll',
                          'rfroll', 'reronll', 'reroil', 'rueroll', 'rerolcl', 'rxroll', 'rerolly', 'peroll', 'rekroll',
                          'rerolsl', 'rerollz', 'rerollg', 'rerpll', 'rerofl', 'rervll', 'rerolj', 'weroll', 'rerolz',
                          'rqroll', 'reroljl', 'rerovl', 'creroll', 'rwroll', 'reropll', 'rerozll', 'reroldl',
                          'rerollu', 'rxeroll', 'rerolle', 'rerolgl', 'rerolg', 'rerollk', 'rmeroll', 'reropl',
                          'rerolr', 'rerolpl', 'repoll', 'rerolq', 'rerholl', 'rerollw', 'oeroll', 'rerolo', 'veroll',
                          'rersoll', 'renroll', 'rerobll', 'rerolzl', 'keroll', 'xreroll', 'rerolw', 'reooll',
                          'rergoll', 'reqroll', 'rehroll', 'rerolv', 'rerlll', 'rerolli', 'rgroll', 'reuroll',
                          'regroll', 'rerolvl', 'deroll', 'rerokl', 'raroll', 'roeroll', 'reroln', 'rerolf', 'rerolil',
                          'neroll', 'reholl', 'rerfoll', 'ueroll', 'rerjoll', 'reroqll', 'xeroll', 'rerool', 'reroly',
                          'freroll', 'reroull', 'rerollb', 'rebroll', 'rerolol', 'rveroll', 'rerolu', 'rkroll',
                          'rerboll', 'rerolhl', 'ruroll', 'rerowl', 'recroll', 'meroll', 'rerolkl', 'rerqoll',
                          'qreroll', 'rerocl', 'reroal', 'rerogll', 'rerowll', 'reeroll', 'rerxll', 'reryoll', 'rrroll',
                          'mreroll', 'rleroll', 'breroll', 'rerolql', 'revoll', 'qeroll', 'areroll', 'rerolfl',
                          'dreroll', 'aeroll', 'rerosl', 'rerohl', 'rewoll', 'rerolxl', 'reroel', 'rerolal', 'beroll',
                          'reroul', 'rerolld', 'nreroll', 'reroql', 'eeroll', 'reroall', 'rerolla', 'rerojll', 'rerall',
                          'reioll', 'reyoll', 'rerfll', 'rerolrl', 'rerozl', 'rerole', 'heroll', 'rercoll', 'relroll',
                          'rzroll', 'rerols', 'rerollh', 'ieroll', 'rernoll', 'rerwoll', 'rweroll', 'rerjll', 'rersll',
                          'reroml', 'reloll', 'reqoll', 'rgeroll', 'rproll', 'ureroll', 'rjeroll', 'rexroll', 'rerogl',
                          'rearoll', 'rerell', 'reroyll', 'rertoll', 'reraoll', 'remoll', 'rezoll', 'greroll',
                          'rperoll', 'rerodl', 'ireroll', 'ereroll', 'revroll', 'rieroll', 'rteroll', 'reronl',
                          'rerdll', 'rerollf', 'recoll', 'rsroll', 'lreroll', 'rderoll', 'rernll', 'rerdoll', 'reiroll',
                          'yeroll', 'rejoll', 'rmroll', 'rerola', 'rerbll', 'retoll', 'rerrll', 'refroll', 'regoll',
                          'yreroll', 'geroll', 'rbroll', 'wreroll', 'rkeroll', 'rerolk', 'reboll', 'rheroll', 'rerpoll',
                          'leroll', 'zreroll', 'rerzll', 'rerolml', 'rerroll', 'raeroll', 'remroll', 'rerorl',
                          'rerofll', 'rerorll', 'rdroll', 'reroxl', 'feroll', 'rerosll', 'reroli', 'rhroll', 'rlroll',
                          'rberoll', 'rerollv', 'reeoll', 'redroll', 'rerxoll', 'hreroll', 'rerolls', 'oreroll',
                          'resroll', 'ryeroll', 'rzeroll', '3eroll', '4eroll', '5eroll', '#eroll', '$eroll', '%eroll',
                          'r4roll', 'r3roll', 'r2roll', 'r$roll', 'r#roll', 'r@roll', 're3oll', 're4oll', 're5oll',
                          're#oll', 're$oll', 're%oll', 'rer8ll', 'rer9ll', 'rer0ll', 'rer;ll', 'rer*ll', 'rer(ll',
                          'rer)ll', 'rero;l', 'rero/l', 'rero.l', 'rero,l', 'rero?l', 'rero>l', 'rero<l', 'rerol;',
                          'rerol/', 'rerol.', 'rerol,', 'rerol?', 'rerol>', 'rerol<', 'reroclquests', 'rerollqueqts',
                          'rerollqests', 'rerollqueits', 'rerollqeusts', 'rerollquetss', 'refrollquests',
                          'rerollquevsts', 'rerolluqests', 'erollquests', 'rerollquests', 'rreollquests',
                          'rercllquests', 'rerlolquests', 'rerollquest', 'rerollquespts', 'rerollquestsh',
                          'errollquests', 'rerollqumests', 'reorllquests', 'rerollqueste', 'rerollqueszts',
                          'rerollqusets', 'rerolluests', 'rerollequests', 'rerollqusts', 'rerollquyests', 'reollquests',
                          'oerollquests', 'rerollquesxts', 'rerollquesds', 'rerollquescs', 'rerollqufsts',
                          'rerolbquests', 'rerllquests', 'rerollqyests', 'rerollquets', 'rerolglquests', 'rerollquess',
                          'rerolqluests', 'rsrollquests', 'rerowlquests', 'rerollqzuests', 'rerolquests',
                          'rerbollquests', 'rmerollquests', 'rerollqueists', 'rejrollquests', 'reiollquests',
                          'rersllquests', 'reroolquests', 'rrollquests', 'revrollquests', 'grerollquests',
                          'rerollquesns', 'rerollqudests', 'rerolrlquests', 'rzrollquests', 'rerollwuests',
                          'reroldlquests', 'rerollquestm', 'rerollquestsb', 'krerollquests', 'rerolleuests',
                          'rerollbuests', 'rermollquests', 'rerzllquests', 'rerollquelsts', 'rerollquekts',
                          'rerollqutests', 'rerollquwsts', 'reuollquests', 'reroplquests', 'rerollquesths',
                          'rerlllquests', 'reprollquests', 'rerollqueksts', 'rergollquests', 'resollquests',
                          'reroullquests', 'rerollqucests', 'rewrollquests', 'rerollyuests', 'ierollquests',
                          'rerolxlquests', 'rerollquessts', 'rerolequests', 'rerollquefts', 'rperollquests',
                          'reyollquests', 'rerollqmuests', 'rejollquests', 'rerolljquests', 'rerollzuests',
                          'rerollquestss', 'reqrollquests', 'relrollquests', 'rerrllquests', 'rerollquesrs',
                          'rerfllquests', 'rberollquests', 'rebollquests', 'rerzollquests', 'rerollqwuests',
                          'rerolslquests', 'rerofllquests', 'rerollqueots', 'rekollquests', 'rerollquestg',
                          'lerollquests', 'rzerollquests', 'rerallquests', 'terollquests', 'qerollquests',
                          'rerollqfuests', 'rerollquestsj', 'rerolclquests', 'rerololquests', 'reroljlquests',
                          'urerollquests', 'rerollquestrs', 'rerollqkuests', 'rerollquesst', 'reroklquests',
                          'rerollquusts', 'rerollquestls', 'rekrollquests', 'resrollquests', 'rerdollquests',
                          'rerollquerts', 'rerollquestsx', 'reroslquests', 'rerollqujsts', 'rerolluuests',
                          'rqrollquests', 'verollquests', 'rerollqursts', 'rerollquestsk', 'rearollquests',
                          'rerolnquests', 'rerrollquests', 'rerollquexts', 'rerollquosts', 'rerolltquests',
                          'rerollquysts', 'qrerollquests', 'rerollqudsts', 'rerorlquests', 'reqollquests',
                          'renrollquests', 'reroollquests', 'rerollqusests', 'rerollquzests', 'rerollquestsl',
                          'yerollquests', 'rerolltuests', 'reoollquests', 'rerolllquests', 'rerollquesfts',
                          'rerollquesbs', 'jerollquests', 'rerhollquests', 'reroillquests', 'reryollquests',
                          'rewollquests', 'rerollquestj', 'rerollqueslts', 'rerollqukests', 'rerollqgests',
                          'cerollquests', 'rerollquesto', 'rerellquests', 'rerwollquests', 'rerollqubests',
                          'rerpllquests', 'rerollquesls', 'rerollaquests', 'rerollbquests', 'rerollquestts',
                          'rerollquesqs', 'zerollquests', 'rerollqueswts', 'rerollauests', 'reroblquests',
                          'rerollquestys', 'rermllquests', 'rerollquvsts', 'rerkollquests', 'perollquests',
                          'rerollquesits', 'rlrollquests', 'rerollqtuests', 'rerollqueasts', 'repollquests',
                          'rerollquesth', 'rerollquqsts', 'rerollquoests', 'rerollquesti', 'reroelquests',
                          'rferollquests', 'rernllquests', 'rerollquestsa', 'prerollquests', 'regollquests',
                          'rerwllquests', 'rerocllquests', 'rerojllquests', 'rerollquqests', 'rerollqiuests',
                          'rerollqupsts', 'rhrollquests', 'rerollquestk', 'rerollqnuests', 'nrerollquests',
                          'reerollquests', 'rerollquestsz', 'rerollquepts', 'rerollqtests', 'rerollquestsc',
                          'rerollquestn', 'rerolkquests', 'rezollquests', 'rerollqurests', 'rerollqhuests',
                          'redrollquests', 'rerolfquests', 'rerollquedsts', 'rerohlquests', 'rerovlquests',
                          'rerollqcests', 'rerollquwests', 'rwrollquests', 'rerolqquests', 'rprollquests',
                          'rerollquebsts', 'rerollquesjs', 'rerollquensts', 'rerollnuests', 'rerjllquests',
                          'rerollquesots', 'rerollqlests', 'rerollquhests', 'rerollquists', 'rerollqyuests',
                          'rerollxuests', 'rerollquescts', 'rerollqzests', 'eerollquests', 'rerolhlquests',
                          'rerodlquests', 'rerollqoests', 'rerollquemsts', 'rerollpquests', 'rerollquestu',
                          'rerollquetts', 'rerollmquests', 'rerolldquests', 'rrrollquests', 'rerjollquests',
                          'rerollxquests', 'rerollquezts', 'rerollquhsts', 'rerollquesps', 'rerollquegts',
                          'rerollquestc', 'rerollquesos', 'rerollvquests', 'rerollquects', 'rerollquesus',
                          'regrollquests', 'rerolliuests', 'rarollquests', 'kerollquests', 'rkrollquests',
                          'rurollquests', 'rerqollquests', 'rerollquiests', 'rerollquestsg', 'rerollqujests',
                          'rerollquevts', 'rerollquesnts', 'rerollquesqts', 'renollquests', 'rxrollquests',
                          'rerollquents', 'rerollquecsts', 'rerollquemts', 'trerollquests', 'rxerollquests',
                          'rerollqeuests', 'recollquests', 'relollquests', 'rerbllquests', 'rerillquests',
                          'reronllquests', 'rerollqhests', 'irerollquests', 'zrerollquests', 'aerollquests',
                          'rerollquesms', 'revollquests', 'rerollpuests', 'rerollquesta', 'rerollqguests',
                          'arerollquests', 'rerollquuests', 'rexollquests', 'gerollquests', 'rehollquests',
                          'rerollqunsts', 'rerobllquests', 'rerollquestsp', 'rerollqulsts', 'rervollquests',
                          'rerollquestns', 'rerollqwests', 'rerolelquests', 'rerollquesgts', 'rerolmlquests',
                          'rerollquestso', 'rerollquesis', 'reroylquests', 'rerolgquests', 'rerollquxsts',
                          'rerollqsests', 'rerollquesgs', 'reryllquests', 'rcerollquests', 'rerollquehsts',
                          'rerollqueshts', 'rerollquesdts', 'rerollqueqsts', 'rerollqueskts', 'rerollquestxs',
                          'rtrollquests', 'rerollouests', 'rerohllquests', 'retrollquests', 'rerollqqests',
                          'rerollkuests', 'rierollquests', 'rnerollquests', 'rerollqpests', 'rerollqueests',
                          'rerollqpuests', 'rerollqfests', 'reroalquests', 'reriollquests', 'rerollquesks',
                          'rerolluquests', 'rerullquests', 'reroallquests', 'hrerollquests', 'rerollquestzs',
                          'rerollwquests', 'rerolljuests', 'rerollqquests', 'rerollquasts', 'rerollquegsts',
                          'ferollquests', 'rlerollquests', 'rerollquesyts', 'rjrollquests', 'rerollquestbs',
                          'rerollquersts', 'rerollquestas', 'rerollqufests', 'rezrollquests', 'reroloquests',
                          'rerollqupests', 'rerollqdests', 'rerollfuests', 'yrerollquests', 'rerolplquests',
                          'rerolliquests', 'rerollqueszs', 'rerollquestse', 'rerollqueuts', 'nerollquests',
                          'rerollcuests', 'rerollquestp', 'rorollquests', 'rerollqbuests', 'ryrollquests',
                          'xrerollquests', 'reroilquests', 'reroljquests', 'rerollqueshs', 'berollquests',
                          'uerollquests', 'rerollquestr', 'rerolzlquests', 'rmrollquests', 'rereollquests',
                          'rerollquesvts', 'rerollquestsi', 'rerollquestw', 'rerollquesats', 'rwerollquests',
                          'rerojlquests', 'rerotlquests', 'rerollqeests', 'reroldquests', 'rerollqunests',
                          'rerollqubsts', 'rerollqmests', 'rerollquepsts', 'rerollhuests', 'rerollqueats',
                          'rgerollquests', 'rerollqxuests', 'rerovllquests', 'reroliquests', 'rerhllquests',
                          'rerollqxests', 'recrollquests', 'rerollquesrts', 'rerollquestvs', 'rerolloquests',
                          'rerollquestt', 'reirollquests', 'rerolflquests', 'rerollquksts', 'rerollqluests',
                          'ryerollquests', 'rerollquedts', 'rerollquestsd', 'rerollqouests', 'derollquests',
                          'rerolyquests', 'rerollqueses', 'rerollqkests', 'rerollquestsf', 'reroflquests',
                          'reroqllquests', 'rerollquestsm', 'reroltquests', 'rerfollquests', 'rbrollquests',
                          'rerozlquests', 'reromlquests', 'rserollquests', 'rerollquestqs', 'rerodllquests',
                          'reroluquests', 'rerollrquests', 'rerollqvests', 'rerollqueusts', 'rerollquzsts',
                          'rerollquesuts', 'rerolsquests', 'rerollquejts', 'rerollruests', 'rerollquesets',
                          'rerogllquests', 'rerolvlquests', 'mrerollquests', 'rerollquestf', 'rerollquesbts',
                          'rerollqjuests', 'rerollquxests', 'rerollqnests', 'rerollqueets', 'rerollquetsts',
                          'rerollqueyts', 'retollquests', 'rerollquestps', 'reroyllquests', 'rerollqucsts',
                          'rerowllquests', 'rerolzquests', 'reroltlquests', 'rerollluests', 'reroqlquests',
                          'rerolqlquests', 'brerollquests', 'rerollquestsq', 'rerxllquests', 'rehrollquests',
                          'rernollquests', 'redollquests', 'rerollquestz', 'rerollquestsv', 'rerolklquests',
                          'rerollquestes', 'rerollmuests', 'rkerollquests', 'rerollqumsts', 'reeollquests',
                          'rerollquewsts', 'vrerollquests', 'reropllquests', 'rerollduests', 'rerollqsuests',
                          'rerollquestv', 'rerqllquests', 'rerollqugests', 'rerollquestjs', 'rfrollquests',
                          'rerollqduests', 'rerollquestst', 'rerolwlquests', 'rerollquvests', 'rerollquestcs',
                          'rerolhquests', 'rerolrquests', 'reraollquests', 'rergllquests', 'rerollquestos',
                          'rerollquebts', 'raerollquests', 'jrerollquests', 'rercollquests', 'rerdllquests',
                          'rerorllquests', 'rerollquestsr', 'rerosllquests', 'rerollquestx', 'rersollquests',
                          'rerollquesys', 'rerollquexsts', 'crerollquests', 'merollquests', 'rerotllquests',
                          'rerollyquests', 'rrerollquests', 'rerolblquests', 'reroellquests', 'rerollzquests',
                          'refollquests', 'rerollqcuests', 'rerollquesvs', 'reroxlquests', 'rerolnlquests',
                          'rerollquestds', 'rerolaquests', 'reyrollquests', 'reaollquests', 'lrerollquests',
                          'rerollquewts', 'rdrollquests', 'rerollqulests', 'rerollvuests', 'reroglquests',
                          'rerollquesas', 'rerollquestks', 'rerollsuests', 'rerollquestl', 'ruerollquests',
                          'rerolylquests', 'rerollqvuests', 'rerxollquests', 'reurollquests', 'rerollquaests',
                          'rerolilquests', 'rerollquezsts', 'srerollquests', 'rebrollquests', 'rerollqussts',
                          'rerolulquests', 'rnrollquests', 'rerollquestq', 'reruollquests', 'reromllquests',
                          'rerollqauests', 'werollquests', 'rqerollquests', 'drerollquests', 'rerokllquests',
                          'rerollquesss', 'rherollquests', 'rerollquehts', 'rerollqruests', 'reroxllquests',
                          'rgrollquests', 'wrerollquests', 'rerolcquests', 'xerollquests', 'rerollquestis',
                          'rerollgquests', 'rerollfquests', 'rerpollquests', 'rexrollquests', 'ererollquests',
                          'rerollquesxs', 'rerollguests', 'rerollqueosts', 'rerollqaests', 'rerollqbests',
                          'rerolalquests', 'rertollquests', 'rverollquests', 'rervllquests', 'reronlquests',
                          'rerollhquests', 'rerolwquests', 'rerollquesws', 'rerollquejsts', 'reorollquests',
                          'rerollsquests', 'frerollquests', 'rerolmquests', 'rerollquestd', 'rerollqiests',
                          'rerollquestms', 'rerollquestus', 'rerkllquests', 'remollquests', 'rjerollquests',
                          'rerlollquests', 'rerollquestb', 'rertllquests', 'rcrollquests', 'rerollquesmts',
                          'rerolpquests', 'rerollquestsn', 'rerollquelts', 'rerollquesty', 'rerozllquests',
                          'rvrollquests', 'rerollquestsy', 'rirollquests', 'rerolvquests', 'rerollquesjts',
                          'orerollquests', 'rerollquestfs', 'herollquests', 'rerollkquests', 'rerollquestsw',
                          'rerollqrests', 'rerollquefsts', 'rerollquestgs', 'reroulquests', 'rerollqueysts',
                          'serollquests', 'remrollquests', 'rerollqjests', 'rerollquesfs', 'rerollquestws',
                          'rerollcquests', 'rerollqutsts', 'rerollquestsu', 'rerollqugsts', 'rterollquests',
                          'rerollnquests', 'rerolxquests', 'rderollquests', 'roerollquests', '3erollquests',
                          '4erollquests', '5erollquests', '#erollquests', '$erollquests', '%erollquests',
                          'r4rollquests', 'r3rollquests', 'r2rollquests', 'r$rollquests', 'r#rollquests',
                          'r@rollquests', 're3ollquests', 're4ollquests', 're5ollquests', 're#ollquests',
                          're$ollquests', 're%ollquests', 'rer8llquests', 'rer9llquests', 'rer0llquests',
                          'rer;llquests', 'rer*llquests', 'rer(llquests', 'rer)llquests', 'rero;lquests',
                          'rero/lquests', 'rero.lquests', 'rero,lquests', 'rero?lquests', 'rero>lquests',
                          'rero<lquests', 'rerol;quests', 'rerol/quests', 'rerol.quests', 'rerol,quests',
                          'rerol?quests', 'rerol>quests', 'rerol<quests', 'reroll`uests', 'reroll1uests',
                          'reroll2uests', 'reroll~uests', 'reroll!uests', 'reroll@uests', 'rerollq6ests',
                          'rerollq7ests', 'rerollq8ests', 'rerollq^ests', 'rerollq&ests', 'rerollq*ests',
                          'rerollqu4sts', 'rerollqu3sts', 'rerollqu2sts', 'rerollqu$sts', 'rerollqu#sts',
                          'rerollqu@sts', 'rerollques4s', 'rerollques5s', 'rerollques6s', 'rerollques$s',
                          'rerollques%s', 'rerollques^s', '/dailyquest', '/dq', '/quests', '/dailyquests', '/dqs',
                          '/dquest', '/dquests', '/dailyq', '/dailyqs', '/reroll', '/rerollquests'],
                 extras={'emoji': "library_list", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         'dev': False, "description_keys": ['dailyquests.meta.description'],
                         "name_key": "dailyquests.slash.name",
                         "experimental": True},
                 brief="dailyquests.meta.brief",
                 description="{0}")
    async def dailyquests(self, ctx, authcode='', optout=None):
        """
        This is the entry point for the daily quests command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode for the account
            optout: Any text given will opt out of starting an auth session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.daily_quests_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(DailyQuests(client))

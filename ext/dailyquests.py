"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily quests command to view + reroll quests.
"""
import asyncio
import datetime
import io
import time
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

    def __init__(self, ctx, client, message, author, quests, quest_options, auth_info, desired_lang):
        super().__init__(timeout=360.0)
        self.dailyquests = None
        self.questsview = None
        self.ctx = ctx
        self.client = client
        self.message = message
        self.author = author
        self.quests = quests
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
            options: The options for the select menu.

        Returns:
            The embed with the daily quest details.
        """
        if select:
            if guid == "back":
                self.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                        desired_lang=self.desired_lang)
                return await self.dailyquests.dailyquests_embed(ctx, self.desired_lang, self.quests, self.auth_info)
            else:
                self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
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
                            async with aiofiles.open(f"ext/DataTables/DailyQuests/{file_name}", "r", encoding="utf-8") as f:
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
            view = QuestRerollView(self.ctx, self.client, self.message, self.author, self.quests, self.children[0].options,
                                   select.values[0], self.auth_info, self.desired_lang)
            self.questsview = view
        else:
            view = self.questsview
        view.dailyquests = self.dailyquests
        view.questsview = self
        if select.values[0] == "back":
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests,
                                                                                    desired_lang=self.desired_lang)
        else:
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
                                                                                    desired_lang=self.desired_lang,
                                                                                    selected_guid=select.values[0])
        await interaction.response.edit_message(embed=embed, view=self.questsview)


class QuestRerollView(discord.ui.View):
    """
    The view for the quest reroll purchase command.
    """

    def __init__(self, ctx, client, message, author, quests, quest_options, guid, auth_info, desired_lang):
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
        self.interaction_check_done = {}
        self.desired_lang = desired_lang

        self.children[0].placeholder = stw.I18n.get("dailyquests.view.option.placeholder", desired_lang)

        self.children[0].options = quest_options
        self.children[1].label = stw.I18n.get("dailyquests.confirmation.button.reroll", self.desired_lang)
        self.children[1].emoji = self.client.config["emojis"]["slot_icon_shuffle"]
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
        else:
            self.children[0].options = await self.dailyquests.select_options_quests(self.quests, True,
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
        stw_request = await stw.profile_request(self.client, "quest_refresh", self.auth_info)
        stw_json_response = orjson.loads(await stw_request.read())
        try:
            error_code = stw_json_response["errorCode"]
            acc_name = self.auth_info["account_name"]
            embed = await stw.post_error_possibilities(self.ctx, self.client, "dailyquests", acc_name, error_code,
                                                       verbiage_action="rerollquest", desired_lang=self.desired_lang)
            logger.info(f"User {self.ctx.author.id} could not reroll quest. | {stw_json_response}")
            await interaction.response.edit_message(embed=embed, view=None)
            if error_code == "errors.com.epicgames.modules.quests.quest_reroll_error":
                await asyncio.sleep(5.8)
                await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self.llamaview)
            return
        except:
            daily_quests = []
            for attribute, value in stw_json_response["profileChanges"][0]["profile"]["items"].items():
                if value["templateId"].startswith("Quest:daily_") and value["attributes"]["quest_state"] == "Active":
                    daily_quests.append(value)
                    daily_quests[-1]["guid"] = attribute
            daily_quests.sort(key=lambda x: x["attributes"]["creation_time"])
            profile_notifications = stw_json_response.get("notifications", [{}])[0].get("newQuestId")
            print(profile_notifications)
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
            embed = await stw.post_error_possibilities(ctx, self.client, "llamas", acc_name, error_code,
                                                       verbiage_action="getllama", desired_lang=desired_lang)
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
            desired_lang: The language to use for the llama names.
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
                            discord.SelectOption(label=quest_data[0]['Properties']['DisplayName']['SourceString'],
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

        embed = await self.dailyquests_embed(ctx, desired_lang, daily_quests, auth_info[1])

        final_embeds.append(embed)

        quests_view_options = await self.select_options_quests(daily_quests, desired_lang=desired_lang)
        quests_view = QuestsView(ctx, self.client, auth_info[0], ctx.author, daily_quests, quests_view_options,
                                 auth_info[1], desired_lang)
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
                 aliases=['quests', 'dq', 'quest', 'dquest', 'dquests'],
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

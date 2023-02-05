"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily command. claims fortnite stw daily reward
"""

import orjson

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw


class Daily(ext.Cog):
    """
    Cog for the daily command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def daily_command(self, ctx, authcode, auth_opt_out):
        """
        The main function of the daily command

        Args:
            ctx: The context of the command
            authcode: The authcode of the user
            auth_opt_out: Whether the user wants to opt out of auth

        Returns:
            None
        """
        succ_colour = self.client.colours["success_green"]
        yellow = self.client.colours["warning_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "daily", authcode, auth_opt_out, True)
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

        # ok now we have the authcode information stuff, so it's time to attempt to claim daily
        request = await stw.profile_request(self.client, "daily", auth_info[1])
        json_response = orjson.loads(await request.read())
        vbucks = auth_info[1]["vbucks"]

        # check for le error code
        try:
            error_code = json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "daily", acc_name, error_code,
                                                       verbiage_action="claim daily")
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        except:
            daily_feedback = json_response["notifications"]

            for notification in daily_feedback:
                if notification["type"] == "daily_rewards":
                    daily_feedback = notification
                    break

            day = daily_feedback["daysLoggedIn"]

            try:
                self.client.temp_auth[ctx.author.id]["day"] = day
            except:
                pass

            try:
                user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, True)
                currently_selected_profile = str(user_document["global"]["selected_profile"])
                limit = user_document["profiles"][currently_selected_profile]["settings"]["upcoming_display_days"] + 1
            except:
                limit = 8

            items = daily_feedback["items"]
            if ctx.channel.id not in [762864224334381077, 996329452453769226, 1048251904913846272, 997924614548226078]:
                # Empty items means that daily was already claimed
                if len(items) == 0:
                    reward = stw.get_reward(self.client, day, vbucks)
                    rewards = ''
                    max_rewards_reached = False
                    if limit >= 2:
                        if limit > 100:
                            limit = 100
                        for i in range(1, limit):
                            if len(rewards) > 1000:
                                rewards = stw.truncate(rewards, 1000)
                                limit = i
                                max_rewards_reached = True
                                break
                            rewards += stw.get_reward(self.client, int(day) + i, vbucks)[0]
                            if not (i + 1 == limit):
                                rewards += ', '
                            else:
                                rewards += '.'
                            if i % 7 == 0:
                                rewards += '\n\n'

                    calendar = self.client.config["emojis"]["calendar"]

                    embed = discord.Embed(
                        title=await stw.add_emoji_title(self.client, stw.random_error(self.client), "warning"),
                        description=
                        (f"\u200b\n"
                         f"You have already claimed your reward for day **{day}**.\n"
                         f"\u200b\n"
                         f"**{reward[1]} Today's reward was:**\n"
                         f"```{reward[0]}```\n"), colour=yellow)
                    if limit == 2:
                        embed.description += (f"**{calendar} Tomorrow\'s reward:**\n"
                                              f"```{rewards[:-1]}```\n"
                                              f"You can claim tomorrow's reward "
                                              f"<t:{stw.get_tomorrow_midnight_epoch()}:R>\n\u200b\n")
                    elif limit > 2:
                        embed.description += (
                            f"**{calendar} Rewards for the next {'~' if max_rewards_reached else ''}{limit - 1} days"
                            f":**\n ```{rewards}```\n"
                            f"You can claim tomorrow's reward <t:{stw.get_tomorrow_midnight_epoch()}:R>\n"
                            f"\u200b\n")
                    else:
                        embed.description += (f"You can claim tomorrow's reward "
                                              f"<t:{stw.get_tomorrow_midnight_epoch()}:R>\n\u200b\n")
                    embed = await stw.set_thumbnail(self.client, embed, "warn")
                    embed = await stw.add_requested_footer(ctx, embed)
                    final_embeds.append(embed)
                    await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
                    return

                # Initialise the claimed embed
                embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                                      description="\u200b",
                                      colour=succ_colour)

                # First item is the default daily reward, add it using the get_reward method
                reward = stw.get_reward(self.client, day, vbucks)

                # Add any excess items + the default daily reward
                for item in items[2:]:
                    try:
                        amount = item["quantity"]
                        itemtype = item["itemType"]
                        reward[0] += f", {amount} {itemtype}"
                    except:
                        pass

                embed.add_field(name=f'{reward[1]} On day **{day}**, you received:', value=f"```{reward[0]}```",
                                inline=True)

                # Second item is founders reward
                try:
                    founders = items[1]
                    amount = founders["quantity"]
                    itemtype = founders["itemType"]

                    if itemtype == 'CardPack:cardpack_event_founders':
                        display_itemtype = "Founder's Llama"
                    elif itemtype == 'CardPack:cardpack_bronze':
                        display_itemtype = "Upgrade Llama"
                    else:
                        display_itemtype = itemtype

                    embed.add_field(name=f'{self.client.config["emojis"]["founders"]} Founders rewards:',
                                    value=f"```{amount} {display_itemtype}```",
                                    inline=True)
                except:
                    pass
            else:
                if len(items) > 1:
                    plural = "rewards"
                else:
                    plural = "reward"
                embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                                      description=f"\u200b\n<:Check:812201301843902474> "
                                                  f"Successfully claimed daily {plural}"
                                                  f"\n\u200b\n{self.emojis['check_mark']} **Please claim in "
                                                  f"<#757768833946877992> for more detail** "
                                                  f"\n\u200b",
                                      colour=succ_colour)

            if ctx.channel.id not in [762864224334381077, 996329452453769226, 1048251904913846272, 997924614548226078]:
                if limit >= 2:
                    rewards = ''
                    max_rewards_reached = False
                    if limit > 100:
                        limit = 100
                    for i in range(1, limit):
                        if len(rewards) > 1000:
                            rewards = stw.truncate(rewards, 1000)
                            limit = i
                            max_rewards_reached = True
                            break
                        rewards += str(stw.get_reward(self.client, int(day) + i, vbucks)[0])
                        if not (i + 1 == limit):
                            rewards += ', '
                        else:
                            rewards += '.'
                        if i % 7 == 0:
                            rewards += '\n\n'

                    calendar = self.client.config["emojis"]["calendar"]
                    if limit == 2:
                        embed.add_field(name=f'\u200b\n{calendar} Tomorrow\'s reward:',
                                        value=f'```{rewards[:-1]}```\u200b',
                                        inline=False)
                    elif limit > 2:
                        embed.add_field(name=f'\u200b\n{calendar} Rewards for the next '
                                             f'{"~" if max_rewards_reached else ""}'
                                             f'{limit - 1} days:',
                                        value=f'```{rewards}```\u200b',
                                        inline=False)
            embed = await stw.set_thumbnail(self.client, embed, "check")
            embed = await stw.add_requested_footer(ctx, embed)
            if ctx.channel.id not in [762864224334381077, 996329452453769226, 1048251904913846272, 997924614548226078]:
                final_embeds.append(embed)
            else:
                final_embeds = embed
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return

    @ext.slash_command(name='daily', name_localizations=stw.I18n.construct_slash_dict("daily.slash.name"),
                       description='Claim your Save The World daily reward',
                       description_localizations=stw.I18n.construct_slash_dict("daily.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashdaily(self, ctx: discord.ApplicationContext,
                         token: Option(
                             description="Your Epic Games authcode. Required unless you have an active session.",
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
        This function is the entry point for the daily command when called via slash

        Args:
            ctx: The context of the slash command
            token: The authcode of the user
            auth_opt_out: Whether the user wants to opt out of starting an authentication session
        """
        await self.daily_command(ctx, token, not bool(auth_opt_out))

    @ext.command(name='daily',
                 aliases=['daxily', 'clllect', 'deaily', 'clailm', 'c9llect', 'claimm', 'dai9ly', 'claiom', 'collfct',
                          'dsily', 'colaim', 'dawily', 'claqim', 'c9ollect', 'claxim', 'dajily', 'dxily', 'da8ily',
                          'claiim', 'cla9m', 'cla9im', 'clakim', 'cvollect', 'clollect', 'collectf', 'clasim', 'dauly',
                          'daoly', 'daiily', 'daiply', 'dailpy', 'clai8m', 'day', 'dwaily', 'coollect', 'collext',
                          'dailky', 'dailoy', 'clsim', 'clalm', 'coloect', 'colklect', 'collec5t', 'claij', 'colelct',
                          'da9ily', 'daly', 'dakly', 'raily', 'collcet', 'laim', 'daioly', 'coll4ct', 'collecxt',
                          'ckaim', 'dly', 'collecdt', 'dqily', 'dalily', 'vollect', 'caily', 'collecg', 'collsect',
                          'cfollect', 'daqily', 'cpllect', 'calim', 'cillect', 'collec5', 'colle3ct', 'collecvt',
                          'colldct', 'sdaily', 'claoim', 'ciollect', 'dzaily', 'draily', 'colledt', 'collrect',
                          'clazim', 'ckollect', 'cokllect', 'dqaily', 'clainm', 'xaily', 'dcollect', 'dailt', 'daiky',
                          'colletc', 'dakily', 'clakm', 'co9llect', 'dsaily', 'clain', 'clqim', 'coll4ect', 'collesct',
                          'dfaily', 'dailgy', 'xclaim', 'claim', 'collexct', 'daily6', 'aily', 'cloaim', 'cplaim',
                          'dailly', 'saily', 'claium', 'coplect', 'daliy', 'colkect', 'vlaim', 'dailg', 'flaim',
                          'cla8m', 'colleft', 'dailyg', 'clqaim', 'cdaily', 'collecgt', 'clpaim', 'clauim', 'claimn',
                          'collwct', 'colle4ct', 'collet', 'cdlaim', 'daiyl', 'adily', 'dailty', 'dzily', 'dail6',
                          'fclaim', 'collerct', 'coll3ct', 'cxollect', 'dail', 'dclaim', 'dasily', 'dail7', 'xcollect',
                          'dajly', 'clami', 'collec6', 'cdollect', 'daiuly', 'collsct', 'xdaily', 'coaim', 'daioy',
                          'clwim', 'dwily', 'coolect', 'collevct', 'clajim', 'collecy', 'cpaim', 'daily7', 'collect5',
                          'dailyh', 'collect', 'dally', 'ccollect', 'collecyt', 'cliam', 'dlaim', 'eaily', 'claom',
                          'daiy', 'collech', 'fcollect', 'dollect', 'clai9m', 'clzaim', 'collectt', 'ddaily', 'da8ly',
                          'dailyt', 'cxlaim', 'ocllect', 'collec', 'colplect', 'collecr', 'xlaim', 'collecct',
                          'collewct', 'dazily', 'ollect', 'cvlaim', 'ckllect', 'collct', 'dieforyou', 'claimj',
                          'dcaily', 'colect', 'd', 'dailyu', 'collevt', 'cllect', 'collecf', 'dailuy', 'vcollect',
                          'collpect', 'clajm', 'clalim', 'dialy', 'dailhy', 'colpect', 'collfect', 'collecth',
                          'collec6t', 'daikly', 'clxim', 'vclaim', 'cololect', 'claik', 'deez', 'da9ly', 'rdaily',
                          'dailyy', 'follect', 'dailjy', 'dailyj', 'clzim', 'colllect', 'collect6', 'claijm',
                          'colldect', 'cflaim', 'claimk', 'clai', 'cclaim', 'clolect', 'caim', 'clam', 'colloect',
                          'dailu', 'daijly', 'dai8ly', 'deeznuts', 'xollect', 'collectg', 'claum', 'clim', 'coklect',
                          'cla8im', 'clawim', 'clxaim', 'dily', 'dailj', 'colleect', 'cpollect', 'daoily', 'clwaim',
                          'collecrt', 'collecft', 'collefct', 'lcaim', 'claikm', 'collecty', 'dxaily', 'clkaim', 'da',
                          'collecht', 'coll3ect', 'fdaily', 'collrct', 'daaily', 'c0ollect', 'clsaim', 'collwect',
                          'dailh', 'c0llect', 'collkect', 'cklaim', 'co0llect', 'copllect', 'colledct', 'edaily',
                          'dail7y', 'dauily', 'cllaim', 'collectr', 'claaim', 'faily', 'daipy', 'coillect', 'dail6y',
                          '/claim', '/daily', '/d', '/collect', '.daily', '.d', '.claim'],
                 extras={'emoji': "vbucks", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         'dev': False},
                 brief="Claim your Save The World daily reward (authentication requried)",
                 description=(
                         f"This command will instantly claim your daily reward, if available. To use this command, "
                         f"you'll need Fortnite: Save the World on the account you will claim with. You must be "
                         f"authenticated to use this command.\n "
                         f"\u200b\n"
                         f"⦾ This command only runs once, be sure to come back"
                         f" <t:{stw.get_tomorrow_midnight_epoch()}:R>\n"
                         f"⦾ Looking for autoclaim? Check out the `deviceauth` command to opt-in to the auto-claim "
                         f"trial period!\n"
                         f"⦾ Looking for help on authcodes? Check out help for the `auth` command, or try the `how2`"
                         f" command."))
    async def daily(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the daily command when called traditionally

        Args:
            ctx (discord.ext.commands.Context): The context of the command
            authcode: The authcode to use for authentication
            optout: Any text given will opt out of starting an authentication session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.daily_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Daily(client))

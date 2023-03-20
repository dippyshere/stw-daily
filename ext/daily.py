"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the daily command. claims fortnite stw daily reward
"""
import asyncio
import logging

import orjson

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw
from ext.profile.bongodb import get_user_document


logger = logging.getLogger(__name__)


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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        succ_colour = self.client.colours["success_green"]
        yellow = self.client.colours["warning_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "daily", authcode, auth_opt_out, True,
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

        # ok now we have the authcode information stuff, so it's time to attempt to claim daily
        request = await stw.profile_request(self.client, "daily", auth_info[1])
        json_response = orjson.loads(await request.read())
        vbucks = auth_info[1]["vbucks"]

        # check for le error code
        try:
            error_code = json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "daily", acc_name, error_code,
                                                       verbiage_action="daily", desired_lang=desired_lang)
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
                user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, True, desired_lang)
                currently_selected_profile = str(user_document["global"]["selected_profile"])
                limit = user_document["profiles"][currently_selected_profile]["settings"]["upcoming_display_days"] + 1
            except:
                limit = 8

            items = daily_feedback["items"]
            if ctx.channel.id not in [762864224334381077, 996329452453769226, 1048251904913846272, 997924614548226078]:
                # Empty items means that daily was already claimed
                if len(items) == 0:
                    reward = stw.get_reward(self.client, day, vbucks, desired_lang)
                    reward_quantity = f"{reward[-1]:,} " if reward[-1] != 1 else ""
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
                            data = stw.get_reward(self.client, i + int(day), vbucks, desired_lang)
                            data_quantity = f"{data[-1]:,} " if data[-1] != 1 else ""
                            rewards += f"{data_quantity}{data[0]}"
                            if not (i + 1 == limit):
                                rewards += ', '
                            else:
                                rewards += '.'
                            if i % 7 == 0:
                                rewards += '\n\n'

                    calendar = self.client.config["emojis"]["calendar"]

                    embed = discord.Embed(
                        title=await stw.add_emoji_title(self.client, stw.random_error(self.client, desired_lang), "warning"),
                        description=
                        (f"\u200b\n"
                         f"{stw.I18n.get('daily.embed.alreadyclaimed.description1', desired_lang, f'{day:,}')}\n"
                         f"\u200b\n"
                         f"{stw.I18n.get('daily.embed.alreadyclaimed.description2', desired_lang, reward[1])}\n"
                         f"```{reward_quantity}{reward[0]}```\n"), colour=yellow)
                    if limit == 2:
                        embed.description += (
                            f"{stw.I18n.get('reward.embed.field3', desired_lang, calendar)}\n"
                            f"```{rewards[:-1]}```\n"
                            f"{stw.I18n.get('daily.embed.alreadyclaimed.description3', desired_lang, f'<t:{stw.get_tomorrow_midnight_epoch()}:R>')}\n\u200b\n")
                    elif limit > 2:
                        approx = '~' if max_rewards_reached else ''
                        embed.description += (
                            f"**{stw.I18n.get('reward.embed.field4', desired_lang, calendar, f'{approx}{limit - 1:,}').replace('**', '')}**"
                            f"\n ```{rewards}```\n"
                            f"{stw.I18n.get('daily.embed.alreadyclaimed.description3', desired_lang, f'<t:{stw.get_tomorrow_midnight_epoch()}:R>')}\n\u200b\n")
                    else:
                        embed.description += f"{stw.I18n.get('daily.embed.alreadyclaimed.description3', desired_lang, f'<t:{stw.get_tomorrow_midnight_epoch()}:R>')}\n\u200b\n"
                    embed = await stw.set_thumbnail(self.client, embed, "warn")
                    embed = await stw.add_requested_footer(ctx, embed, desired_lang)
                    final_embeds.append(embed)
                    try:
                        user_document = await get_user_document(ctx, self.client, ctx.author.id)
                        try:
                            goal = \
                                user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"][
                                    "mtxgoal"]
                        except:
                            goal = 0
                    except:
                        goal = 0
                    logger.debug(f"mtxgoal: {goal}")
                    if goal > 0:
                        core_request = await stw.profile_request(self.client, "query", auth_info[1],
                                                                 profile_id="common_core")
                        vbucks_item = await asyncio.gather(
                            asyncio.to_thread(stw.extract_profile_item,
                                              profile_json=orjson.loads(await core_request.read()),
                                              item_string="Currency:Mtx"))
                        vbucks_total = await stw.calculate_vbucks(vbucks_item)
                        logger.debug(f"vbucks_total: {vbucks_total}")
                        if goal == "" or not str(goal).isnumeric():
                            embed = await stw.vbucks_goal_embed(self.client, ctx, desired_lang=desired_lang, goal=True)
                        elif int(goal) <= vbucks_total:
                            embed = await stw.vbucks_goal_embed(self.client, ctx, current_total=vbucks_total,
                                                                desired_lang=desired_lang, goal=True)
                        else:
                            total, days = \
                                (await asyncio.gather(asyncio.to_thread(stw.calculate_vbuck_goals, vbucks_total,
                                                                        0 if auth_info[1]['day'] is None else
                                                                        auth_info[1]['day'], int(goal))))[0]
                            logger.debug(f"total: {total}, days: {days}")
                            embed = await stw.vbucks_goal_embed(self.client, ctx, total, days, True, vbucks_total,
                                                                auth_info[1]['vbucks'], goal, desired_lang, True)
                        final_embeds.append(embed)
                    await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
                    return

                # Initialise the claimed embed
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, stw.I18n.get('generic.success', desired_lang),
                                                    "checkmark"),
                    description="\u200b",
                    colour=succ_colour)

                # First item is the default daily reward, add it using the get_reward method
                reward = stw.get_reward(self.client, day, vbucks, desired_lang)
                reward_quantity = f"{reward[-1]:,} " if reward[-1] != 1 else ""

                # Add any excess items + the default daily reward
                for item in items[2:]:
                    try:
                        amount = item["quantity"]
                        itemtype = item["itemType"]
                        reward[0] += f", {amount} {itemtype}"
                    except:
                        pass

                embed.add_field(name=stw.I18n.get('daily.embed.claimed.field.name', desired_lang, reward[1], day),
                                value=f"```{reward_quantity}{reward[0]}```",
                                inline=True)

                # Second item is founders reward
                try:
                    founders = items[1]
                    amount = founders["quantity"]
                    itemtype = founders["itemType"]

                    if itemtype == 'CardPack:cardpack_event_founders':
                        display_itemtype = stw.I18n.get('stw.item.CardPack_Event_Founders.name', desired_lang)
                    elif itemtype == 'CardPack:cardpack_bronze':
                        display_itemtype = stw.I18n.get('stw.item.CardPack_Bronze.name.singular', desired_lang)
                    else:
                        display_itemtype = itemtype

                    embed.add_field(name=stw.I18n.get('daily.embed.claimed.founders.field.name', desired_lang,
                                                      self.client.config["emojis"]["founders"]),
                                    value=f"```{amount + ' ' if int(amount) != 1 else ''}{display_itemtype}```",
                                    inline=True)
                except:
                    pass
            else:
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, stw.I18n.get('generic.success', desired_lang), "checkmark"),
                    description=f"\u200b\n{stw.I18n.get('daily.embed.claimed.umpcoming.channelalert1.plural' if len(items) > 1 else 'daily.embed.claimed.umpcoming.channelalert1.singular', desired_lang, '<:Check:812201301843902474>')}"
                                f"\n\u200b\n{self.emojis['check_mark']} {stw.I18n.get('daily.embed.claimed.umpcoming.channelalert2', desired_lang, '<#757768833946877992>')}\n\u200b",
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
                        data = stw.get_reward(self.client, i + int(day), vbucks, desired_lang)
                        data_quantity = f"{data[-1]:,} " if data[-1] != 1 else ""
                        rewards += f"{data_quantity}{data[0]}"
                        if not (i + 1 == limit):
                            rewards += ', '
                        else:
                            rewards += '.'
                        if i % 7 == 0:
                            rewards += '\n\n'

                    calendar = self.client.config["emojis"]["calendar"]
                    if limit == 2:
                        embed.add_field(name=f'\u200b\n{stw.I18n.get("reward.embed.field3", desired_lang, calendar)}',
                                        value=f'```{rewards[:-1]}```\u200b',
                                        inline=False)
                    elif limit > 2:
                        approx = '~' if max_rewards_reached else ''
                        embed.add_field(
                            name=f'\u200b\n{stw.I18n.get("reward.embed.field4", desired_lang, calendar, f"{approx}{limit - 1:,}")}',
                            value=f'```{rewards}```\u200b',
                            inline=False)
            embed = await stw.set_thumbnail(self.client, embed, "check")
            embed = await stw.add_requested_footer(ctx, embed, desired_lang)
            if ctx.channel.id not in [762864224334381077, 996329452453769226, 1048251904913846272, 997924614548226078]:
                final_embeds.append(embed)
                try:
                    user_document = await get_user_document(ctx, self.client, ctx.author.id)
                    try:
                        goal = user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"][
                            "mtxgoal"]
                    except:
                        goal = 0
                except:
                    goal = 0
                logger.debug(f"mtxgoal: {goal}")
                if goal > 0:
                    core_request = await stw.profile_request(self.client, "query", auth_info[1],
                                                             profile_id="common_core")
                    vbucks_item = await asyncio.gather(
                        asyncio.to_thread(stw.extract_profile_item,
                                          profile_json=orjson.loads(await core_request.read()),
                                          item_string="Currency:Mtx"))
                    vbucks_total = await stw.calculate_vbucks(vbucks_item)
                    logger.debug(f"vbucks_total: {vbucks_total}")
                    if goal == "" or not str(goal).isnumeric():
                        embed = await stw.vbucks_goal_embed(self.client, ctx, desired_lang=desired_lang, goal=True)
                    elif int(goal) <= vbucks_total:
                        embed = await stw.vbucks_goal_embed(self.client, ctx, current_total=vbucks_total,
                                                            desired_lang=desired_lang, goal=True, assert_value=False,
                                                            target=goal)
                    else:
                        total, days = (await asyncio.gather(asyncio.to_thread(stw.calculate_vbuck_goals, vbucks_total,
                                                                              0 if auth_info[1]['day'] is None else
                                                                              auth_info[1]['day'], int(goal))))[0]
                        logger.debug(f"total: {total}, days: {days}")
                        embed = await stw.vbucks_goal_embed(self.client, ctx, total, days, True, vbucks_total,
                                                            auth_info[1]['vbucks'], goal, desired_lang, True)
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
        await self.daily_command(ctx, token, not eval(auth_opt_out))

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
                          '/claim', '/daily', '/d', '/collect', '.daily', '.d', '.claim', 'dc', 'daagliks', 'يوميًا',
                          'ежедневно', 'দৈনিক', 'diàriament', 'denně', 'daglig', 'täglich', 'καθημερινά', 'a diario',
                          'iga päev', 'روزانه', 'päivittäin', 'tous les jours', 'દૈનિક', 'kullum', 'יום יומי', 'दैनिक',
                          'dnevno', 'napi', 'setiap hari', 'giornalmente', '毎日', '매일', 'kasdien', 'katru dienu',
                          'दररोज', 'dagelijks', 'ਰੋਜ਼ਾਨਾ', 'codziennie', 'diariamente', 'zilnic', 'denne', 'дневно',
                          'dagligen', 'kila siku', 'தினசரி', 'రోజువారీ', 'ทุกวัน', 'günlük', 'щодня', 'روزانہ',
                          'hàng ngày', '日常的', 'adiario', 'diario', 'igapäev', 'quotidien', 'touslesjours', 'יוםיומי',
                          'setiaphari', 'katrudienu', 'hàngngày', 'dails', 'daixy', 'dairly', 'dainly',
                          'deily', 'ydaily', 'daiwly', 'dailiy', 'daizly', 'dailb', 'mdaily', 'baily', 'dawly', 'dnily',
                          'dably', 'daxly', 'dhily', 'dmily', 'dailys', 'davily', 'yaily', 'duily', 'daisly', 'dailyv',
                          'dailn', 'daiby', 'dailay', 'diaily', 'daqly', 'dailye', 'daidy', 'daimy', 'dailsy', 'dahly',
                          'dapily', 'damily', 'daiyly', 'daaly', 'dailvy', 'djily', 'waily', 'dacily', 'dailx',
                          'dailyf', 'daify', 'dmaily', 'daiyy', 'daile', 'dailya', 'dasly', 'jdaily', 'daili', 'dafily',
                          'dacly', 'dlily', 'dyily', 'djaily', 'daigy', 'daicy', 'naily', 'daicly', 'iaily', 'vdaily',
                          'daity', 'dhaily', 'dlaily', 'dtily', 'dgaily', 'dailfy', 'paily', 'doaily', 'daiqy',
                          'dtaily', 'dailm', 'dgily', 'daivy', 'dailyq', 'dagily', 'doily', 'dailwy', 'dailny', 'dbily',
                          'dailz', 'dailc', 'daitly', 'dahily', 'dairy', 'dailyn', 'dyaily', 'dailcy', 'dailyw',
                          'dailk', 'daiqly', 'dailr', 'zdaily', 'dailo', 'datily', 'dainy', 'daiey', 'dkily', 'ddily',
                          'ndaily', 'danily', 'darly', 'dailyo', 'datly', 'daply', 'dafly', 'adaily',
                          'duaily', 'dvily', 'dailmy', 'zaily', 'dailey', 'daifly', 'drily', 'dailzy', 'dailyk',
                          'daiiy', 'dfily', 'dailq', 'daila', 'dailyz', 'gaily', 'kdaily', 'dailqy', 'dpily', 'dkaily',
                          'daiay', 'daibly', 'tdaily', 'davly', 'wdaily', 'aaily', 'dnaily', 'dailyd', 'daigly',
                          'daiwy', 'daild', 'dabily', 'dadily', 'daijy', 'dailym', 'dayly', 'daizy', 'dailw', 'jaily',
                          'dvaily', 'kaily', 'daill', 'dayily', 'dbaily', 'daely', 'dcily', 'taily', 'qaily', 'damly',
                          'oaily', 'idaily', 'daiuy', 'daihly', 'dailyl', 'danly', 'dailyc', 'daihy', 'diily', 'daisy',
                          'gdaily', 'laily', 'darily', 'daiely', 'daimly', 'daialy', 'uaily', 'qdaily',
                          'daivly', 'dailby', 'ldaily', 'dailyi', 'hdaily', 'daixly', 'haily', 'dailf', 'dailry',
                          'udaily', 'vaily', 'daildy', 'dailv', 'dagly', 'daidly', 'dazly', 'pdaily', 'dailxy',
                          'daeily', 'dadly', 'dailyb', 'maily', 'odaily', 'dailp', 'dpaily', 'dailyr', 'da7ly', 'da&ly',
                          'da*ly', 'da(ly', 'dai;y', 'dai/y', 'dai.y', 'dai,y', 'dai?y', 'dai>y', 'dai<y', 'dail5',
                          'dail%', 'dail^', 'dail&', 'claitm', 'sclaim', 'cleim', 'claym', 'claicm', 'claip', 'iclaim',
                          'cwaim', 'cilaim', 'cloim', 'cbaim', 'cnlaim', 'clrim', 'clayim', 'claims', 'claizm',
                          'clyaim', 'claiv', 'qclaim', 'claie', 'clair', 'llaim', 'caaim', 'hclaim', 'claiw', 'pclaim',
                          'cuaim', 'clmim', 'mclaim', 'claih', 'ceaim', 'kclaim', 'claimx', 'claix', 'clyim', 'clacm',
                          'cldim', 'clnim', 'klaim', 'claxm', 'crlaim', 'aclaim', 'clais', 'cmaim', 'claihm', 'claiy',
                          'cllim', 'clahm', 'mlaim', 'wclaim', 'claimr', 'uclaim', 'cldaim', 'lclaim', 'cblaim',
                          'cgaim', 'claiem', 'cladm', 'claimq', 'claic', 'clatim', 'claam', 'jclaim', 'claib', 'claimt',
                          'claimi', 'clahim', 'zclaim', 'chaim', 'clgim', 'oclaim', 'claimy', 'tlaim', 'slaim',
                          'tclaim', 'zlaim', 'cxaim', 'clapim', 'ctaim', 'claidm', 'clairm', 'cltaim',
                          'cltim', 'eclaim', 'clail', 'cladim', 'cwlaim', 'clbaim', 'claism', 'glaim', 'claii', 'czaim',
                          'clarim', 'claimv', 'rlaim', 'cliaim', 'claqm', 'ulaim', 'cmlaim', 'clafim', 'cluaim',
                          'cyaim', 'claimh', 'claimu', 'clkim', 'clabm', 'cluim', 'claiz', 'cliim', 'claimb', 'claem',
                          'elaim', 'claifm', 'czlaim', 'clvim', 'cnaim', 'claimp', 'qlaim', 'clcim', 'celaim', 'cvaim',
                          'claia', 'ccaim', 'chlaim', 'clvaim', 'cjlaim', 'clait', 'cfaim', 'claiu', 'gclaim', 'cjaim',
                          'cglaim', 'clavim', 'clatm', 'clamim', 'cqaim', 'plaim', 'claiym', 'blaim', 'clnaim',
                          'claimo', 'claig', 'jlaim', 'clmaim', 'clfaim', 'alaim', 'claiq', 'clabim', 'claime',
                          'cylaim', 'claimc', 'olaim', 'claiam', 'cljaim', 'claiqm', 'clamm', 'claimg', 'claiwm',
                          'cslaim', 'claibm', 'cljim', 'claid', 'culaim', 'nlaim', 'claif', 'clarm', 'clazm', 'yclaim',
                          'clavm', 'clfim', 'clagim', 'calaim', 'clanm', 'clhim', 'clapm', 'claimd', 'clpim', 'claima',
                          'nclaim', 'clanim', 'clcaim', 'claiml', 'craim', 'ctlaim', 'ilaim', 'cdaim', 'cqlaim',
                          'clagm', 'wlaim', 'clacim', 'clhaim', 'clawm', 'clbim', 'claixm', 'clgaim', 'hlaim', 'clasm',
                          'claimz', 'claivm', 'clafm', 'cleaim', 'claeim', 'ciaim', 'ylaim', 'rclaim', 'claio',
                          'claipm', 'claimf', 'clraim', 'claimw', 'csaim', 'claigm', 'c;aim', 'c/aim', 'c.aim', 'c,aim',
                          'c?aim', 'c>aim', 'c<aim', 'cla7m', 'cla&m', 'cla*m', 'cla(m', 'clai,', 'clai<', 'claimfer',
                          'laimer', 'claimyer', 'lcaimer', 'cvaimer', 'climer', 'claimemr', 'slaimer', 'cliamer',
                          'claiper', 'clbimer', 'claimeu', 'claimew', 'clcimer', 'czaimer', 'cclaimer', 'claier',
                          'clamier', 'claiemr', 'clamer', 'claimere', 'clwimer', 'fclaimer', 'cjaimer', 'gclaimer',
                          'cllimer', 'cslaimer', 'claimjer', 'claimer', 'claimtr', 'claipmer', 'cjlaimer', 'claimkr',
                          'cliaimer', 'claimre', 'mclaimer', 'calimer', 'clailmer', 'claimerx', 'ceaimer', 'caimer',
                          'claimur', 'claimea', 'nclaimer', 'iclaimer', 'claimegr', 'clarimer', 'claimev', 'clatmer',
                          'colaimer', 'clajimer', 'clqimer', 'claimetr', 'claimezr', 'tlaimer', 'nlaimer', 'clyimer',
                          'clailer', 'clawimer', 'ylaimer', 'dclaimer', 'claimber', 'claimcer', 'claizmer', 'claimqer',
                          'cluimer', 'claiwmer', 'cglaimer', 'hclaimer', 'claxmer', 'claimers', 'clgaimer', 'claimenr',
                          'claimei', 'cladimer', 'cllaimer', 'claimej', 'clanimer', 'claimes', 'cwlaimer', 'claimaer',
                          'claixmer', 'cnaimer', 'clhimer', 'xclaimer', 'claikmer', 'claymer', 'claimpr', 'claimor',
                          'claimler', 'claimfr', 'cwaimer', 'claomer', 'clpimer', 'claizer', 'claimebr', 'cvlaimer',
                          'claiher', 'clfimer', 'clagimer', 'claimmr', 'claimejr', 'claoimer', 'clabimer', 'clazmer',
                          'clhaimer', 'cylaimer', 'claimerf', 'jclaimer', 'claimeru', 'cyaimer', 'clammer', 'clavmer',
                          'claimerd', 'claimevr', 'clahmer', 'claimwer', 'claimerb', 'clacmer', 'kclaimer', 'culaimer',
                          'claimen', 'blaimer', 'ilaimer', 'claimerr', 'claimdr', 'claimeqr', 'claximer', 'claitmer',
                          'claider', 'claiqer', 'claiymer', 'tclaimer', 'claimeb', 'clapimer', 'clqaimer', 'ccaimer',
                          'claimvr', 'cmaimer', 'clafmer', 'clmaimer', 'claimert', 'claimwr', 'claimser', 'claimeyr',
                          'chaimer', 'claimerw', 'cuaimer', 'cljimer', 'clsimer', 'cdlaimer', 'ulaimer', 'claioer',
                          'claimeh', 'rclaimer', 'claimar', 'claimear', 'clanmer', 'clainer', 'ckaimer', 'lclaimer',
                          'claqimer', 'claiumer', 'cdaimer', 'claimepr', 'claimqr', 'clmimer', 'clagmer', 'claimefr',
                          'clakimer', 'claimee', 'claimsr', 'claiser', 'qlaimer', 'czlaimer', 'cleimer', 'claimier',
                          'claimeo', 'cxlaimer', 'ciaimer', 'claimex', 'claimef', 'claimexr', 'clnimer', 'uclaimer',
                          'claimxer', 'claimgr', 'claimzer', 'clahimer', 'claimesr', 'claieer', 'cpaimer', 'clafimer',
                          'claimeur', 'cladmer', 'caaimer', 'claicmer', 'claimehr', 'claimel', 'clayimer', 'claimek',
                          'clalimer', 'claimekr', 'cklaimer', 'claaimer', 'alaimer', 'rlaimer', 'claimerz', 'chlaimer',
                          'clabmer', 'claimzr', 'claimver', 'claimerg', 'claimed', 'claimey', 'claimcr', 'claumer',
                          'clpaimer', 'clasmer', 'claimez', 'claeimer', 'ctaimer', 'csaimer', 'vclaimer', 'claimeir',
                          'claimir', 'claifmer', 'claimhr', 'llaimer', 'cilaimer', 'clairer', 'oclaimer', 'clnaimer',
                          'yclaimer', 'clarmer', 'cluaimer', 'calaimer', 'claimrer', 'qclaimer', 'claiimer', 'claimerc',
                          'claidmer', 'claimlr', 'claimuer', 'claimker', 'olaimer', 'jlaimer', 'dlaimer', 'claimet',
                          'clamimer', 'clatimer', 'claimep', 'cliimer', 'cqlaimer', 'cfaimer', 'cloaimer', 'claimeq',
                          'claimbr', 'plaimer', 'celaimer', 'eclaimer', 'claimeg', 'claimder', 'claiaer', 'cgaimer',
                          'claimjr', 'claiomer', 'klaimer', 'aclaimer', 'clxaimer', 'cplaimer', 'clkimer', 'claamer',
                          'sclaimer', 'clvaimer', 'clgimer', 'wlaimer', 'claiber', 'clzaimer', 'zclaimer', 'claixer',
                          'claimeer', 'claimnr', 'claimmer', 'clbaimer', 'claiqmer', 'cmlaimer', 'clasimer', 'flaimer',
                          'claimger', 'cleaimer', 'clwaimer', 'wclaimer', 'cljaimer', 'clajmer', 'claimeri', 'cloimer',
                          'cblaimer', 'clapmer', 'ctlaimer', 'claimeor', 'clainmer', 'claimero', 'claimerm', 'claiier',
                          'claimery', 'clyaimer', 'claimera', 'clvimer', 'claimerq', 'clsaimer', 'claijmer', 'claimern',
                          'claismer', 'claiker', 'claiamer', 'clairmer', 'clraimer', 'crlaimer', 'cxaimer', 'clximer',
                          'claimedr', 'claihmer', 'clzimer', 'claimerp', 'clauimer', 'vlaimer', 'claimper', 'claimecr',
                          'pclaimer', 'claimerj', 'mlaimer', 'claimem', 'clacimer', 'claiger', 'cnlaimer', 'claqmer',
                          'claiyer', 'claiwer', 'claifer', 'glaimer', 'bclaimer', 'claimter', 'clakmer', 'claigmer',
                          'zlaimer', 'cltimer', 'elaimer', 'claivmer', 'clavimer', 'claiter', 'claimxr', 'claimyr',
                          'claimerv', 'craimer', 'claimoer', 'clrimer', 'claiemer', 'claimerl', 'clazimer', 'cldimer',
                          'hlaimer', 'cqaimer', 'clcaimer', 'claimner', 'claicer', 'claimerh', 'cltaimer', 'claijer',
                          'claiuer', 'claimewr', 'clkaimer', 'claimerk', 'cldaimer', 'xlaimer', 'claimrr', 'clalmer',
                          'claemer', 'clfaimer', 'cflaimer', 'claibmer', 'cbaimer', 'claiver', 'claimec', 'clawmer',
                          'coaimer', 'claimelr', 'claimher', 'c;aimer', 'c/aimer', 'c.aimer', 'c,aimer', 'c?aimer',
                          'c>aimer', 'c<aimer', 'cla7mer', 'cla8mer', 'cla9mer', 'cla&mer', 'cla*mer', 'cla(mer',
                          'clai,er', 'clai<er', 'claim4r', 'claim3r', 'claim2r', 'claim$r', 'claim#r', 'claim@r',
                          'claime3', 'claime4', 'claime5', 'claime#', 'claime$', 'claime%', 'collecst', 'collict',
                          'collecjt', 'ccllect', 'collekt', 'colleca', 'colgect', 'collqect', 'coliect', 'collemt',
                          'cwllect', 'colflect', 'jollect', 'collecs', 'czollect', 'qollect', 'colqect', 'coullect',
                          'colblect', 'collgect', 'colhect', 'colxlect', 'collegct', 'collvct', 'cohlect', 'lcollect',
                          'coblect', 'collectd', 'collcect', 'collhct', 'colllct', 'collezct', 'colleot', 'colvlect',
                          'colleci', 'ycollect', 'collecq', 'collxct', 'collbect', 'ncollect', 'colject', 'coylect',
                          'colvect', 'coallect', 'cdllect', 'colclect', 'aollect', 'colrect', 'collqct', 'coalect',
                          'cotllect', 'iollect', 'colliect', 'corllect', 'coxllect', 'coldect', 'qcollect', 'collyct',
                          'collecu', 'collejct', 'colhlect', 'tcollect', 'ctollect', 'colleit', 'colcect', 'mollect',
                          'collelct', 'collaect', 'colljct', 'collebct', 'coelect', 'collecz', 'collett', 'colleqt',
                          'cgllect', 'colilect', 'eollect', 'nollect', 'colleut', 'colxect', 'collecb', 'coclect',
                          'collecm', 'colleco', 'colulect', 'cqollect', 'collecn', 'collecqt', 'colleczt', 'cwollect',
                          'callect', 'colfect', 'cowllect', 'collcct', 'colalect', 'cxllect', 'collept', 'colwlect',
                          'cowlect', 'collxect', 'colleact', 'codllect', 'colrlect', 'wcollect', 'colleict', 'collecta',
                          'coljlect', 'colleat', 'colslect', 'colluect', 'conlect', 'coflect', 'collkct', 'collecpt',
                          'colleyct', 'csllect', 'cyllect', 'collecat', 'coslect', 'coluect', 'cogllect', 'collpct',
                          'collecto', 'covllect', 'chollect', 'collectn', 'cuollect', 'acollect', 'coleect', 'collecmt',
                          'collezt', 'coltect', 'ucollect', 'colluct', 'wollect', 'collectx', 'colletct', 'collecbt',
                          'cvllect', 'colltect', 'colleckt', 'covlect', 'colnlect', 'collebt', 'colleet', 'collnct',
                          'collects', 'bcollect', 'cjllect', 'cullect', 'collecc', 'colzect', 'kollect', 'collhect',
                          'collectj', 'pcollect', 'colleck', 'colloct', 'colltct', 'collectw', 'collectm', 'collelt',
                          'collegt', 'zcollect', 'collehct', 'collectu', 'scollect', 'ecollect', 'colleyt', 'oollect',
                          'collectq', 'collecet', 'coxlect', 'collejt', 'hcollect', 'coilect', 'cmllect', 'cozllect',
                          'cyollect', 'cbollect', 'comllect', 'caollect', 'collject', 'coldlect', 'collemct',
                          'cjollect', 'colbect', 'lollect', 'colleht', 'pollect', 'codlect', 'collzct', 'collecd',
                          'collent', 'coqllect', 'zollect', 'coglect', 'cnllect', 'cosllect', 'collecot', 'coyllect',
                          'cmollect', 'collmect', 'collectc', 'collecwt', 'collenct', 'gollect', 'csollect', 'ocollect',
                          'cocllect', 'collectv', 'cozlect', 'colleoct', 'colqlect', 'coqlect', 'cnollect', 'chllect',
                          'collecnt', 'colleuct', 'collectz', 'jcollect', 'cotlect', 'czllect', 'collepct', 'collecit',
                          'collece', 'collecti', 'colwect', 'colaect', 'collekct', 'collectb', 'collecw', 'colsect',
                          'colmect', 'sollect', 'collectk', 'icollect', 'conllect', 'collecp', 'colleqct', 'uollect',
                          'cfllect', 'cojlect', 'colleclt', 'collact', 'bollect', 'comlect', 'collecj', 'cobllect',
                          'crollect', 'gcollect', 'rollect', 'colylect', 'collmct', 'collnect', 'cojllect', 'collest',
                          'collert', 'collecut', 'collbct', 'collvect', 'collecv', 'hollect', 'kcollect', 'colyect',
                          'collzect', 'collecl', 'colzlect', 'collgct', 'yollect', 'cgollect', 'ctllect', 'collecx',
                          'colnect', 'cqllect', 'coltlect', 'cohllect', 'rcollect', 'colglect', 'colelect', 'colmlect',
                          'collewt', 'mcollect', 'corlect', 'collectp', 'collecte', 'cbllect', 'collectl', 'crllect',
                          'collyect', 'tollect', 'cellect', 'coellect', 'coulect', 'ceollect', 'cofllect', 'c8llect',
                          'c;llect', 'c*llect', 'c(llect', 'c)llect', 'co;lect', 'co/lect', 'co.lect', 'co,lect',
                          'co?lect', 'co>lect', 'co<lect', 'col;ect', 'col/ect', 'col.ect', 'col,ect', 'col?ect',
                          'col>ect', 'col<ect', 'coll2ct', 'coll$ct', 'coll#ct', 'coll@ct', 'collec4', 'collec$',
                          'collec%', 'collec^', '/claimer', 'dao;y'],
                 extras={'emoji': "vbucks", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.meta.args.optout.description', True]},
                         'dev': False, "description_keys": ['daily.meta.description.main',
                                                            ['daily.meta.description.list.item1',
                                                             f'<t:{stw.get_tomorrow_midnight_epoch()}:R>'],
                                                            ['daily.meta.description.list.item2', '`device`'],
                                                            ['daily.meta.description.list.item3', '`auth`', '`how2`']],
                         "name_key": "daily.slash.name"},
                 brief="daily.meta.brief",
                 description="{0}\n\u200b\n⦾ {1}\n⦾ {2}\n⦾ {3}")
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

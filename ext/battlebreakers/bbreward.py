"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the battle breakers version of the reward command
"""

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


class BBReward(ext.Cog):
    """
    Cog for the battle breakers reward command
    """

    def __init__(self, client):
        self.client = client

    async def bbreward_command(self, ctx, day, limit=7):
        """
        The main function of the battle breakers reward command

        Args:
            ctx: The context of the command
            day: The day of the week to get the rewards for
            limit: The number of days to get rewards for

        Returns:
            None
        """
        # try:
        #     temp_auth = self.client.temp_auth[ctx.author.id]
        #     if day == 'hi readers of the bot':
        #         daye = temp_auth["bb_day"]
        #         if daye is not None:
        #             day = daye
        # except:
        #     pass

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        embed_colour = self.client.colours["reward_magenta"]

        if limit is None:
            user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, True, desired_lang)
            try:
                currently_selected_profile = str(user_document["global"]["selected_profile"])
                limit = user_document["profiles"][currently_selected_profile]["settings"]["upcoming_display_days"]
            except:
                limit = 7

        if day is None:
            embed = await stw.create_error_embed(self.client, ctx,
                                                 description=f"{stw.I18n.get('reward.error.noday1', desired_lang)}\n"
                                                             f"⦾ {stw.I18n.get('reward.error.noday2', desired_lang)}\n"
                                                             f"⦾ {stw.I18n.get('reward.error.noday3', desired_lang, await stw.mention_string(self.client, 'bbreward 336'))}",
                                                 error_level=0, command="bbreward", prompt_help=True,
                                                 prompt_authcode=False, desired_lang=desired_lang)
            await stw.slash_send_embed(ctx, self.client, embed)
            return

        else:
            try:
                day = int(day)
            except ValueError:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description=f"{stw.I18n.get('reward.error.invalidday1', desired_lang)}\n"
                                                                 f"⦾ {stw.I18n.get('reward.error.invalidday2', desired_lang)}",
                                                     error_level=0, prompt_help=True, prompt_authcode=False,
                                                     command="bbreward", desired_lang=desired_lang)
                await stw.slash_send_embed(ctx, self.client, embed)
                return
            try:
                limit = int(limit)
            except ValueError:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description=f"{stw.I18n.get('reward.error.invalidday1', desired_lang)}\n"
                                                                 f"⦾ {stw.I18n.get('reward.error.invalidlimit2', desired_lang)}",
                                                     error_level=0, prompt_help=True, prompt_authcode=False,
                                                     command="bbreward", desired_lang=desired_lang)
                await stw.slash_send_embed(ctx, self.client, embed)
                return
            if limit < 0:
                limit = 7
            if day <= 0:
                day = 1

            if limit >= 1:
                if limit == 1:
                    embed = discord.Embed(
                        title=await stw.add_emoji_title(self.client, stw.I18n.get("bbreward.embed.title", desired_lang),
                                                        "Shared2"),
                        description=f'\u200b\n{stw.I18n.get("reward.embed.description1.singular", desired_lang, f"{day:,}", f"{limit:,}")}\n\u200b',
                        color=embed_colour)
                else:
                    embed = discord.Embed(
                        title=await stw.add_emoji_title(self.client, stw.I18n.get("bbreward.embed.title", desired_lang),
                                                        "Shared2"),
                        description=f'\u200b\n{stw.I18n.get("reward.embed.description1.plural", desired_lang, f"{day:,}", f"{limit:,}")}\n\u200b',
                        color=embed_colour)
            else:
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, stw.I18n.get("bbreward.embed.title", desired_lang),
                                                    "Shared2"),
                    description=f'\u200b\n{stw.I18n.get("reward.embed.description1.skull", desired_lang, f"{day:,}", f"{limit:,}")}\n\u200b',
                    color=embed_colour)

            try:
                # day, name, emoji_text, description, quantity
                reward = stw.get_bb_reward_data(self.client, pre_calc_day=day, desired_lang=desired_lang)
            except Exception as e:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description=f"{stw.I18n.get('reward.error.general1', desired_lang, day)}\n"
                                                                 f"⦾ {stw.I18n.get('reward.error.general2', desired_lang)}",
                                                     prompt_help=True, prompt_authcode=False, command="bbreward",
                                                     desired_lang=desired_lang)
                await stw.slash_send_embed(ctx, self.client, embed)
                print(f"Error when getting bbreward for day {day} - {e}")
                return
            reward_quantity = f"{reward[4]:,} " if reward[4] != 1 else ""
            embed.add_field(name=stw.I18n.get("reward.embed.field1", desired_lang, reward[2]),
                            value=f'```{reward_quantity}{reward[1]}```\u200b')
            for row in stw.bbLoginRewards[0]['Rows']:
                if 'MtxGiveaway' in stw.bbLoginRewards[0]['Rows'][row]['ItemDefinition']['AssetPathName']:
                    if int(day) % 1800 < int(row):
                        if int(row) - int(day) % 1800 == 1:
                            embed.add_field(
                                name=stw.I18n.get("bbreward.embed.mtx.field.name", desired_lang,
                                                  self.client.config["emojis"]["T_MTX_Gem_Icon"]),  # hello
                                value=f'```{stw.I18n.get("reward.embed.field2.mtxupcoming.singular", desired_lang, f"{stw.get_bb_reward_data(self.client, pre_calc_day=int(row), desired_lang=desired_lang)[-1]:,} {stw.get_bb_reward_data(self.client, pre_calc_day=int(row), desired_lang=desired_lang)[1]}", int(row) - int(day) % 1800)}'
                                      f'```\u200b', inline=False)
                        else:
                            embed.add_field(
                                name=stw.I18n.get("bbreward.embed.mtx.field.name", desired_lang,
                                                  self.client.config["emojis"]["T_MTX_Gem_Icon"]),  # hello
                                value=f'```{stw.I18n.get("reward.embed.field2.mtxupcoming.plural", desired_lang, f"{stw.get_bb_reward_data(self.client, pre_calc_day=int(row), desired_lang=desired_lang)[-1]:,} {stw.get_bb_reward_data(self.client, pre_calc_day=int(row), desired_lang=desired_lang)[1]}", int(row) - int(day) % 1800)}'
                                      f'```\u200b', inline=False)
                        break  # hello alexander hanson
            if limit >= 1:
                rewards = ''
                max_rewards_reached = False
                if limit > 100:
                    limit = 100
                for i in range(1, limit + 1):
                    if len(rewards) > 1000:
                        rewards = stw.truncate(rewards, 1000)
                        limit = i
                        max_rewards_reached = True
                        break
                    data = stw.get_bb_reward_data(self.client, pre_calc_day=day + i, desired_lang=desired_lang)
                    data_quantity = f"{data[4]:,} " if data[4] != 1 else ""
                    rewards += f"{data_quantity}{data[1]}"
                    if not (i + 1 == limit + 1):
                        rewards += ', '
                    else:
                        rewards += '.'
                    if i % 7 == 0:
                        rewards += '\n\n'
                if limit == 1:
                    reward = stw.get_bb_reward_data(self.client, pre_calc_day=day + 1, desired_lang=desired_lang)

                    embed.add_field(name=stw.I18n.get("reward.embed.field3", desired_lang, reward[2]),
                                    value=f'```{reward[4]:,} {reward[1]}```\u200b',
                                    inline=False)
                else:
                    embed.add_field(
                        name=stw.I18n.get("reward.embed.field4", desired_lang, self.client.config["emojis"]["calendar"], f"{'~' if max_rewards_reached else ''}{limit:,}"),
                        value=f'```{rewards}```\u200b', inline=False)
                    if max_rewards_reached:
                        if limit == 1:  # this will never happen
                            embed.description = f'\u200b\n{stw.I18n.get("reward.embed.description1.singular", desired_lang, f"{day:,}", f"~{limit:,}")}\n\u200b'
                        else:
                            embed.description = f'\u200b\n{stw.I18n.get("reward.embed.description1.plural", desired_lang, f"{day:,}", f"~{limit:,}")}\n\u200b'
            embed = await stw.set_thumbnail(self.client, embed, "Shared2")
            embed = await stw.add_requested_footer(ctx, embed, desired_lang)

            await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='bbreward',
                 aliases=['bbr', 'bbrwrd', 'battlebreakersreward', 'breward', 'bbeward', 'bbrward', 'bbreard',
                          'bbrewrd', 'bbrewad', 'bbrewar', 'bbbreward', 'bbrreward', 'bbreeward', 'bbrewward',
                          'bbrewaard', 'bbrewarrd', 'bbrewardd', 'brbeward', 'bberward', 'bbrweard', 'bbreawrd',
                          'bbrewrad', 'bbrewadr', 'vbreward', 'gbreward', 'hbreward', 'nbreward', 'bvreward',
                          'bgreward', 'bhreward', 'bnreward', 'bbeeward', 'bb4eward', 'bb5eward', 'bbteward',
                          'bbgeward', 'bbfeward', 'bbdeward', 'bbrwward', 'bbr3ward', 'bbr4ward', 'bbrrward',
                          'bbrfward', 'bbrdward', 'bbrsward', 'bbreqard', 'bbre2ard', 'bbre3ard', 'bbreeard',
                          'bbredard', 'bbresard', 'bbreaard', 'bbrewqrd', 'bbrewwrd', 'bbrewsrd', 'bbrewxrd',
                          'bbrewzrd', 'bbrewaed', 'bbrewa4d', 'bbrewa5d', 'bbrewatd', 'bbrewagd', 'bbrewafd',
                          'bbrewadd', 'bbrewars', 'bbreware', 'bbrewarr', 'bbrewarf', 'bbrewarc', 'bbrewarx',
                          'vbbreward', 'bvbreward', 'gbbreward', 'bgbreward', 'hbbreward', 'bhbreward', 'nbbreward',
                          'bnbreward', 'bbvreward', 'bbgreward', 'bbhreward', 'bbnreward', 'bbereward', 'bb4reward',
                          'bbr4eward', 'bb5reward', 'bbr5eward', 'bbtreward', 'bbrteward', 'bbrgeward', 'bbfreward',
                          'bbrfeward', 'bbdreward', 'bbrdeward', 'bbrweward', 'bbr3eward', 'bbre3ward', 'bbre4ward',
                          'bbrerward', 'bbrefward', 'bbredward', 'bbrseward', 'bbresward', 'bbreqward', 'bbrewqard',
                          'bbre2ward', 'bbrew2ard', 'bbrew3ard', 'bbreweard', 'bbrewdard', 'bbrewsard', 'bbreaward',
                          'bbrewaqrd', 'bbrewawrd', 'bbrewasrd', 'bbrewxard', 'bbrewaxrd', 'bbrewzard', 'bbrewazrd',
                          'bbrewaerd', 'bbrewared', 'bbrewa4rd', 'bbrewar4d', 'bbrewa5rd', 'bbrewar5d', 'bbrewatrd',
                          'bbrewartd', 'bbrewagrd', 'bbrewargd', 'bbrewafrd', 'bbrewarfd', 'bbrewadrd', 'bbrewarsd',
                          'bbrewards', 'bbrewarde', 'bbrewardr', 'bbrewardf', 'bbrewarcd', 'bbrewardc', 'bbrewarxd',
                          'bbrewardx', 'brwrd', 'bbwrd', 'bbrrd', 'bbrwd', 'bbrwr', 'bbbrwrd', 'bbrrwrd', 'bbrwwrd',
                          'bbrwrrd', 'bbrwrdd', 'brbwrd', 'bbwrrd', 'bbrrwd', 'bbrwdr', 'vbrwrd', 'gbrwrd', 'hbrwrd',
                          'nbrwrd', 'bvrwrd', 'bgrwrd', 'bhrwrd', 'bnrwrd', 'bbewrd', 'bb4wrd', 'bb5wrd', 'bbtwrd',
                          'bbgwrd', 'bbfwrd', 'bbdwrd', 'bbrqrd', 'bbr2rd', 'bbr3rd', 'bbrerd', 'bbrdrd', 'bbrsrd',
                          'bbrard', 'bbrwed', 'bbrw4d', 'bbrw5d', 'bbrwtd', 'bbrwgd', 'bbrwfd', 'bbrwdd', 'bbrwrs',
                          'bbrwre', 'bbrwrr', 'bbrwrf', 'bbrwrc', 'bbrwrx', 'vbbrwrd', 'bvbrwrd', 'gbbrwrd', 'bgbrwrd',
                          'hbbrwrd', 'bhbrwrd', 'nbbrwrd', 'bnbrwrd', 'bbvrwrd', 'bbgrwrd', 'bbhrwrd', 'bbnrwrd',
                          'bberwrd', 'bb4rwrd', 'bbr4wrd', 'bb5rwrd', 'bbr5wrd', 'bbtrwrd', 'bbrtwrd', 'bbrgwrd',
                          'bbfrwrd', 'bbrfwrd', 'bbdrwrd', 'bbrdwrd', 'bbrqwrd', 'bbrwqrd', 'bbr2wrd', 'bbrw2rd',
                          'bbr3wrd', 'bbrw3rd', 'bbrwerd', 'bbrwdrd', 'bbrswrd', 'bbrwsrd', 'bbrawrd', 'bbrwred',
                          'bbrw4rd', 'bbrwr4d', 'bbrw5rd', 'bbrwr5d', 'bbrwtrd', 'bbrwrtd', 'bbrwgrd', 'bbrwrgd',
                          'bbrwfrd', 'bbrwrfd', 'bbrwrsd', 'bbrwrds', 'bbrwrde', 'bbrwrdr', 'bbrwrdf', 'bbrwrcd',
                          'bbrwrdc', 'bbrwrxd', 'bbrwrdx', '/bbr', '/bbrwrd', '/bbreward', '/battlebreakersrewards',
                          'battlebreakersrewards', 'bbitem', '/bbitem'],
                 extras={'emoji': "Shared2", "args": {'reward.meta.args.day': ['reward.meta.args.day.description',
                                                                               False],
                                                      'reward.meta.args.limit': ['reward.meta.args.limit.description',
                                                                                 True]},
                         "dev": False, "description_keys": ['bbreward.meta.description'],
                         "name_key": "bbreward.slash.name",
                         "battle_broken": True},
                 brief="bbreward.slash.description",
                 description="{0}")
    async def bbreward(self, ctx, day=None, limit=None):
        """
        This command lets you view the rewards of any specific day, and any number of rewards that follow.

        Args:
            ctx: The context of the command
            day: The day to get the rewards of. Not required if you are authenticated
            limit: The number of upcoming days to see (Optional)
        """
        await self.bbreward_command(ctx, day, limit)

    @slash_command(name="bbreward", name_localization=stw.I18n.construct_slash_dict("bbreward.slash.name"),
                   description="View info about a specific day's reward, and the rewards that follow in Battle Breakers",
                   description_localization=stw.I18n.construct_slash_dict("bbreward.slash.description"),
                   guild_ids=stw.guild_ids)
    async def bbslashreward(self, ctx: discord.ApplicationContext,
                            day: Option(int,
                                        "The day to get the rewards of. Not required if you are authenticated",
                                        description_localizations=stw.I18n.construct_slash_dict(
                                            "reward.meta.args.day.description"),
                                        name_localizations=stw.I18n.construct_slash_dict("reward.meta.args.day"),
                                        min_value=1) = None,
                            limit: Option(int, "The number of upcoming days to see",
                                          description_localizations=stw.I18n.construct_slash_dict(
                                              "reward.meta.args.limit.description"),
                                          name_localizations=stw.I18n.construct_slash_dict("reward.meta.args.limit"),
                                          min_value=0, max_value=60, default=7) = None):
        """
        This command lets you view the rewards of any specific day, and any number of rewards that follow.

        Args:
            ctx: The context of the command
            day: The day to get the rewards of. Not required if you are authenticated
            limit: The number of upcoming days to see (Optional)
        """
        await self.bbreward_command(ctx, day, limit)


def setup(client):
    """
    This function is called when the cog is loaded.

    Args:
        client: The client that is loading the cog
    """
    client.add_cog(BBReward(client))

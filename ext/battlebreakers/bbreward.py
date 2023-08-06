"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the battle breakers version of the reward command
"""

import logging

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw

logger = logging.getLogger(__name__)

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
                        description=f'\u200b\n{stw.I18n.get("reward.embed.description1.singular", desired_lang, day, limit)}\n\u200b',
                        color=embed_colour)
                else:
                    embed = discord.Embed(
                        title=await stw.add_emoji_title(self.client, stw.I18n.get("bbreward.embed.title", desired_lang),
                                                        "Shared2"),
                        description=f'\u200b\n{stw.I18n.get("reward.embed.description1.plural", desired_lang, day, limit)}\n\u200b',
                        color=embed_colour)
            else:
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, stw.I18n.get("bbreward.embed.title", desired_lang),
                                                    "Shared2"),
                    description=f'\u200b\n{stw.I18n.get("reward.embed.description1.skull", desired_lang, day, limit)}\n\u200b',
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
                logger.error(f"Error when getting bbreward for day {day}: {e}")
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
                            embed.description = f'\u200b\n{stw.I18n.get("reward.embed.description1.singular", desired_lang, day, f"~{limit:,}")}\n\u200b'
                        else:
                            embed.description = f'\u200b\n{stw.I18n.get("reward.embed.description1.plural", desired_lang, day, f"~{limit:,}")}\n\u200b'
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
                          'battlebreakersrewards', 'bbitem', '/bbitem', 'μπρούμυτα', 'دمدمی مزاج', 'ברכה', 'ブレワード',
                          'ббревард', 'சுருக்கமான', 'బ్రేవార్డ్', '布雷沃德', 'xbbrwrd', 'bbrowrd', 'tbrwrd', 'abbrwrd',
                          'bcrwrd', 'bbrwry', 'bbrwrdv', 'bbyrwrd', 'bbrrrd', 'bbrwvd', 'rbbrwrd', 'bbrwrpd', 'bbrwrb',
                          'bbrwjd', 'bbrpwrd', 'bbryrd', 'bbwwrd', 'brbrwrd', 'sbrwrd', 'bbrwnrd', 'qbrwrd', 'bbrwkrd',
                          'bbmwrd', 'bfrwrd', 'bbrwzrd', 'bbrlrd', 'bmbrwrd', 'ibbrwrd', 'bbrwrm', 'bbrwnd', 'mbrwrd',
                          'bsbrwrd', 'bbrword', 'bbrvrd', 'bbrwrdz', 'bbhwrd', 'cbbrwrd', 'bbrwrdb', 'bbrwzd',
                          'bbqrwrd', 'bbrwrh', 'bzrwrd', 'bbiwrd', 'bbywrd', 'bbrwrdw', 'bkbrwrd', 'brrwrd', 'obbrwrd',
                          'bbrzrd', 'bubrwrd', 'bbrwrdk', 'bbqwrd', 'bbrwra', 'bbuwrd', 'bbrxrd', 'bbrwrmd', 'mbbrwrd',
                          'bbrlwrd', 'bbrgrd', 'bbrwqd', 'bbrwprd', 'bbarwrd', 'qbbrwrd', 'bbrwrl', 'bbrwhrd',
                          'bbrkwrd', 'byrwrd', 'dbrwrd', 'fbrwrd', 'bbrwrhd', 'bmrwrd', 'bbrwrt', 'bbxwrd', 'bsrwrd',
                          'bbrwri', 'rbrwrd', 'bbrwrdn', 'cbrwrd', 'bbrwrld', 'bbrwyd', 'bbrwmrd', 'bbcrwrd', 'bbrord',
                          'bbrwrv', 'bxrwrd', 'sbbrwrd', 'birwrd', 'bbrwrn', 'bbrwrj', 'bblrwrd', 'lbrwrd', 'bbmrwrd',
                          'bbrywrd', 'bbrwird', 'bbprwrd', 'bbawrd', 'bbswrd', 'bqrwrd', 'dbbrwrd', 'bwrwrd', 'bbrwbrd',
                          'bbrjwrd', 'bbrwryd', 'bbrwrod', 'tbbrwrd', 'bbrwcd', 'bbrwxrd', 'bbrwrdq', 'lbbrwrd',
                          'abrwrd', 'bbrvwrd', 'bbzwrd', 'bbvwrd', 'btrwrd', 'bqbrwrd', 'bbrbrd', 'bjrwrd', 'bbnwrd',
                          'bbrcrd', 'bbrwrdh', 'bkrwrd', 'bbirwrd', 'bbrwld', 'bebrwrd', 'bbrwrvd', 'bbrprd', 'bbrwrdi',
                          'bbrwrda', 'bbrwvrd', 'bbcwrd', 'bbrwrdg', 'bbrwod', 'bbowrd', 'bbrwsd', 'bbrbwrd', 'bbrwpd',
                          'bbrnrd', 'ubrwrd', 'bbrwrg', 'wbrwrd', 'bbkwrd', 'bbrwrk', 'bbruwrd', 'bbrmwrd', 'bobrwrd',
                          'obrwrd', 'bbsrwrd', 'bjbrwrd', 'bblwrd', 'bbrwhd', 'barwrd', 'bbrwrzd', 'bbrwrid', 'btbrwrd',
                          'bfbrwrd', 'bbrwrud', 'bprwrd', 'bbrhwrd', 'bborwrd', 'berwrd', 'ybrwrd', 'bbkrwrd', 'bbrwru',
                          'bbrhrd', 'zbbrwrd', 'bcbrwrd', 'ubbrwrd', 'ybbrwrd', 'bbrwrdo', 'bbrwro', 'burwrd',
                          'bbrwlrd', 'bburwrd', 'bbrwjrd', 'xbrwrd', 'bbriwrd', 'bbrwbd', 'bbrird', 'bbrnwrd', 'bbrwrq',
                          'bbrwrwd', 'bbjwrd', 'bbrwmd', 'bbzrwrd', 'kbbrwrd', 'bbrwrdu', 'bbrwrz', 'bbrwrbd', 'ibrwrd',
                          'pbrwrd', 'bbrwrad', 'bbrxwrd', 'bbrwwd', 'bbrwrdt', 'bbrzwrd', 'ebbrwrd', 'bbrtrd',
                          'bpbrwrd', 'blrwrd', 'bbrwrdl', 'bbrwrdy', 'bbrwid', 'bbrwrnd', 'bbrwud', 'bbjrwrd', 'bbbwrd',
                          'bbrwyrd', 'bbrmrd', 'pbbrwrd', 'bbrwrp', 'jbrwrd', 'bbxrwrd', 'wbbrwrd', 'bdrwrd', 'bbrwrqd',
                          'kbrwrd', 'bbpwrd', 'bzbrwrd', 'bbrcwrd', 'bbrwrkd', 'bwbrwrd', 'bbrjrd', 'bdbrwrd',
                          'bbwrwrd', 'bbrurd', 'bxbrwrd', 'bbrkrd', 'bbrfrd', 'bibrwrd', 'bbrwkd', 'bybrwrd', 'bbrwcrd',
                          'jbbrwrd', 'zbrwrd', 'bbrwrdm', 'ebrwrd', 'bbrwurd', 'bbrwrdj', 'bbrwrdp', 'bbrwrjd',
                          'borwrd', 'bbrwrw', 'blbrwrd', 'fbbrwrd', 'bbrwad', 'babrwrd', 'bbrwxd', 'bb3wrd', 'bb#wrd',
                          'bb$wrd', 'bb%wrd', 'bbr1rd', 'bbr!rd', 'bbr@rd', 'bbr#rd', 'bbrw3d', 'bbrw#d', 'bbrw$d',
                          'bbrw%d', 'bbrzward', 'bbrebward', 'bareward', 'bbrewasd', 'bpreward', 'bbrewahrd',
                          'bbleward', 'tbreward', 'bbrexard', 'qbreward', 'bbrewacd', 'bbreyard', 'bbqeward',
                          'bpbreward', 'bkreward', 'bbrewkrd', 'bbreword', 'bbrewarud', 'bbceward', 'bireward',
                          'bbrewrard', 'bbrewardh', 'bbrewoard', 'bbweward', 'bbrecward', 'bbruward', 'bbrewmard',
                          'rbbreward', 'bbrewarda', 'bbremard', 'bboeward', 'bbrepard', 'lbbreward', 'bbrewari',
                          'bbrewarw', 'obreward', 'bbrewarnd', 'bbrewarn', 'bbrewlrd', 'bsbreward', 'bbrewardk',
                          'bbrelward', 'bbrewayrd', 'bbrewarbd', 'bbrefard', 'bbrpeward', 'bbjeward', 'ibreward',
                          'bbrewawd', 'bbzreward', 'bbrceward', 'bbrewara', 'bobreward', 'bbrezward', 'blreward',
                          'bbrewardp', 'bbrewcard', 'sbbreward', 'bbrewarm', 'bbrewajrd', 'bbareward', 'bbrjward',
                          'bbrgward', 'bbrewaud', 'bbbeward', 'bbrewapd', 'bbrewayd', 'bbrewrrd', 'bbrewardg',
                          'bbrewarjd', 'bbrqward', 'bbrjeward', 'bbrenward', 'bbaeward', 'bbrewavrd', 'bbrewakd',
                          'bbrecard', 'ubreward', 'bbueward', 'bbretward', 'bureward', 'bjbreward', 'bwbreward',
                          'bbrzeward', 'bbrtward', 'rbreward', 'bbrewarl', 'bbrevward', 'bereward', 'bbrewarj',
                          'bbcreward', 'bbrewprd', 'bbrheward', 'wbreward', 'bbxreward', 'bbrenard', 'bmreward',
                          'fbbreward', 'bbrewardl', 'babreward', 'bbrewgrd', 'bbrewajd', 'bbyreward', 'bbrewardm',
                          'mbbreward', 'bbrewaord', 'bbrexward', 'bbremward', 'bbrueward', 'bbrqeward', 'bbrewabd',
                          'bjreward', 'bbrewdrd', 'bbrewarmd', 'bbrewbrd', 'bbwreward', 'bbrewarid', 'bbrewiard',
                          'abbreward', 'bubreward', 'bbrcward', 'ebreward', 'bbraeward', 'bbrewarpd', 'bbreiard',
                          'bbreiward', 'bbrveward', 'bbrewamrd', 'bbrewark', 'bdreward', 'dbreward', 'blbreward',
                          'bbrbward', 'bbrneward', 'bbrewaad', 'bbrewardj', 'bbrewmrd', 'bdbreward', 'bbrewarwd',
                          'bbrewlard', 'bbrewary', 'bbrewvard', 'bfreward', 'wbbreward', 'bsreward', 'bbrewanrd',
                          'bblreward', 'bbrelard', 'bbpreward', 'bbrewhrd', 'bbzeward', 'xbreward', 'bbrewaod',
                          'ybreward', 'bfbreward', 'bbureward', 'bqreward', 'bbieward', 'bbrewarh', 'bbrewalrd',
                          'bbrewaprd', 'bbrewtrd', 'bbkeward', 'bbsreward', 'bbrepward', 'bbrewaxd', 'boreward',
                          'bbrewacrd', 'bbrewaid', 'bbrewurd', 'bbrewnard', 'sbreward', 'bbrewarzd', 'tbbreward',
                          'bbmreward', 'bbrewjard', 'bbrewardu', 'bbireward', 'bmbreward', 'bbrewardt', 'bbrewardw',
                          'bbrewarz', 'bbrewyrd', 'zbbreward', 'bbheward', 'bbveward', 'cbbreward', 'bkbreward',
                          'bbrewardv', 'bbregward', 'bbjreward', 'bwreward', 'bbrebard', 'bbrewpard', 'bbrlward',
                          'bzreward', 'bbrewahd', 'bbraward', 'bbrewarb', 'bbrhward', 'bbrewaryd', 'xbbreward',
                          'bbrvward', 'bbrewardb', 'bbreoward', 'obbreward', 'bbrewjrd', 'bbrewarv', 'bbreyward',
                          'jbreward', 'fbreward', 'bbrevard', 'bbrehward', 'bbrewart', 'bbrkward', 'bbrewvrd',
                          'bbretard', 'ebbreward', 'bbrewarld', 'bbrewkard', 'cbreward', 'kbbreward', 'bbrewaro',
                          'bbyeward', 'bbryward', 'bbrewakrd', 'bbrpward', 'bbneward', 'bbrmeward', 'bbrieward',
                          'kbreward', 'bbrewird', 'bbrewarad', 'bbrewfrd', 'bqbreward', 'bbrxward', 'bbrewnrd',
                          'bbrewarod', 'bbrewardy', 'ibbreward', 'bbrezard', 'bbrewhard', 'bbrewald', 'bbrewarg',
                          'btbreward', 'bbrewarp', 'bbrewarq', 'ybbreward', 'bbreuard', 'zbreward', 'bbrewaqd',
                          'brbreward', 'bbrewazd', 'bbrehard', 'bxreward', 'bbrewfard', 'abreward', 'bbroward',
                          'bbrleward', 'bbrewaurd', 'pbbreward', 'bboreward', 'bbrejward', 'byreward', 'bbrewarvd',
                          'bbxeward', 'bbreuward', 'dbbreward', 'bbkreward', 'bibreward', 'bcreward', 'bbrewarhd',
                          'bbrewtard', 'bbrewyard', 'bbrewavd', 'bbrewarkd', 'bbseward', 'bbrewaru', 'lbreward',
                          'bbrewabrd', 'brreward', 'bxbreward', 'bbriward', 'bebreward', 'bbrewcrd', 'mbreward',
                          'bbpeward', 'pbreward', 'bbregard', 'bbrewaird', 'bbrewbard', 'bbrewamd', 'bbrbeward',
                          'qbbreward', 'bbrxeward', 'bbrewardo', 'btreward', 'jbbreward', 'ubbreward', 'bbrewerd',
                          'bzbreward', 'bbrnward', 'bbrewarqd', 'bbrewardn', 'bbmeward', 'bbrewand', 'bbryeward',
                          'bbrewardq', 'bbrerard', 'bbreoard', 'bbrewgard', 'bbrewardz', 'bbrekward', 'bbrekard',
                          'bbrkeward', 'bbqreward', 'bbrejard', 'bbroeward', 'bbrmward', 'bybreward', 'bbrewardi',
                          'bcbreward', 'bbrewuard', 'bb3eward', 'bb#eward', 'bb$eward', 'bb%eward', 'bbr2ward',
                          'bbr$ward', 'bbr#ward', 'bbr@ward', 'bbre1ard', 'bbre!ard', 'bbre@ard', 'bbre#ard',
                          'bbrewa3d', 'bbrewa#d', 'bbrewa$d', 'bbrewa%d', 'beakersreward', 'breakersrewad',
                          'breakerseward', 'breakersveward', 'breakkersreward', 'breakersrewhrd', 'baeakersreward',
                          'breakersreyard', 'breakresreward', 'breakersreard', 'breakersrewadr', 'breakersreawrd',
                          'breaekrsreward', 'breaakersreward', 'bkreakersreward', 'breaketrsreward', 'bbreakersreward',
                          'breakegsreward', 'braekersreward', 'breakersrewaard', 'breakzersreward', 'breakersrewarwd',
                          'brekaersreward', 'breakersrecard', 'breakersrward', 'breakersrewardp', 'breakersereward',
                          'ereakersreward', 'xbreakersreward', 'breakersrewar', 'breakersrewarmd', 'breakersrekward',
                          'breakesreward', 'breakernsreward', 'breakersjreward', 'breakersrweard', 'bfreakersreward',
                          'breakersreware', 'breakersneward', 'brakersreward', 'breakersieward', 'breamkersreward',
                          'bcreakersreward', 'breakersrewarm', 'ybreakersreward', 'breakerreward', 'brrakersreward',
                          'breakersretard', 'breakersrewrd', 'breakersrewarrd', 'breaksrsreward', 'breakersrewfard',
                          'berakersreward', 'breakerserward', 'breakesrreward', 'breakersrewvrd', 'breakersrbeward',
                          'breakersreward', 'bwreakersreward', 'rbreakersreward', 'breakersrewarz', 'brekersreward',
                          'breakerskeward', 'bireakersreward', 'breakeosreward', 'breatersreward', 'breakersrewaxd',
                          'breakerereward', 'breakerosreward', 'breakersrjward', 'reakersreward', 'breakvrsreward',
                          'breakersrewrad', 'breakersrmeward', 'breakersreoward', 'breakersrefard', 'brceakersreward',
                          'btreakersreward', 'breakersrejward', 'breakersrewarkd', 'breakefsreward', 'breakrsreward',
                          'breakersrweward', 'brmeakersreward', 'breakedrsreward', 'breagersreward', 'breakersrvward',
                          'breakerkreward', 'breakersrqeward', 'breakersrenward', 'breakversreward', 'brjeakersreward',
                          'kbreakersreward', 'breakersreweard', 'breakersrewakd', 'breakevsreward', 'breaqkersreward',
                          'breakoersreward', 'brreakersreward', 'breakerbsreward', 'breakersrzward', 'breakersrewrrd',
                          'breakxrsreward', 'breakersfeward', 'breakersrezard', 'byeakersreward', 'breakersrewayrd',
                          'breakejrsreward', 'bpeakersreward', 'breakersrewarde', 'breakersrewardd', 'breakewsreward',
                          'breakersrewabrd', 'breakersrewird', 'breakersrlward', 'breakersrezward', 'breakerskreward',
                          'breakerrseward', 'breagkersreward', 'breakersrewahrd', 'ebreakersreward', 'breakersrmward',
                          'breakersrewuard', 'breakersrewkard', 'breaersreward', 'breakersrenard', 'breakzrsreward',
                          'breakersrjeward', 'jreakersreward', 'breabkersreward', 'breakersrceward', 'breyakersreward',
                          'breakersrekard', 'breakersrewvard', 'breakersryward', 'ureakersreward', 'breajkersreward',
                          'briakersreward', 'breakersrewfrd', 'breaxkersreward', 'breakersresard', 'brebakersreward',
                          'rbeakersreward', 'brexkersreward', 'brfeakersreward', 'breakersrewward', 'breakerpreward',
                          'breakersrexward', 'breaktrsreward', 'breakersrehard', 'breakersrefward', 'breakersreeard',
                          'breakerscreward', 'bgreakersreward', 'breakerxsreward', 'breakersrfeward', 'breakersireward',
                          'breakersreaard', 'breakersrhward', 'bveakersreward', 'breakermreward', 'breakfersreward',
                          'breakerxreward', 'breakhersreward', 'breakerjreward', 'rreakersreward', 'breakersrewahd',
                          'breakersrewurd', 'breakersgreward', 'brdakersreward', 'breakersrewalrd', 'breakerspreward',
                          'breakersyreward', 'brezakersreward', 'breakersrewara', 'breakersrewanrd', 'bhreakersreward',
                          'breakersureward', 'breakerysreward', 'creakersreward', 'breakrersreward', 'breakersrewsard',
                          'bteakersreward', 'breaiersreward', 'breakersreword', 'breakergreward', 'brhakersreward',
                          'breakemrsreward', 'breakewrsreward', 'breakersreiard', 'brebkersreward', 'breakersrewardf',
                          'beeakersreward', 'breakersrewardb', 'breacersreward', 'breakersrepard', 'breakerstreward',
                          'breakersrewzrd', 'dreakersreward', 'breakersraward', 'bgeakersreward', 'breakersrewapd',
                          'breakbersreward', 'breakersrebward', 'breakerswreward', 'breakerjsreward', 'qreakersreward',
                          'breakersrewnrd', 'breakersremward', 'bresakersreward', 'breakerlsreward', 'breakersmreward',
                          'bretkersreward', 'breakersjeward', 'breawersreward', 'brveakersreward', 'bryeakersreward',
                          'breikersreward', 'breakersrewjard', 'breakerwsreward', 'breakehsreward', 'breakerssreward',
                          'pbreakersreward', 'breavkersreward', 'breakersreaward', 'gbreakersreward', 'brwakersreward',
                          'breakezrsreward', 'breajersreward', 'breakcrsreward', 'breakersrewarfd', 'breakersrewafd',
                          'breakkrsreward', 'breekersreward', 'fbreakersreward', 'breakekrsreward', 'xreakersreward',
                          'breakersrewards', 'breakersrzeward', 'breakersrewwrd', 'breakersrewcard', 'breakersrewarj',
                          'brbakersreward', 'breakerlreward', 'breakersrreward', 'brtakersreward', 'breakersrewaru',
                          'dbreakersreward', 'breakmersreward', 'breakersheward', 'breakersrewarud', 'breakecrsreward',
                          'breakersceward', 'breapkersreward', 'breakersrsward', 'breakersrqward', 'wreakersreward',
                          'breabersreward', 'breakersrewtrd', 'bxeakersreward', 'breakersdreward', 'brenkersreward',
                          'breakersrelard', 'breawkersreward', 'breakersrueward', 'breakehrsreward', 'breakersrewyrd',
                          'breakersrewald', 'breakersrewarcd', 'breakyersreward', 'breakersrebard', 'kreakersreward',
                          'breakelsreward', 'breakersrewardt', 'breakersrewtard', 'brejkersreward', 'breakertreward',
                          'brsakersreward', 'breakhrsreward', 'breakerrreward', 'breaokersreward', 'breakprsreward',
                          'breakersrepward', 'breauersreward', 'breakerpsreward', 'breakersresward', 'breakersrewarjd',
                          'bsreakersreward', 'breakorsreward', 'breakersweward', 'bregkersreward', 'breakersxeward',
                          'sbreakersreward', 'breakearsreward', 'brdeakersreward', 'breakersrewawd', 'brqakersreward',
                          'breakerszreward', 'breackersreward', 'breakersqeward', 'breakersrewarc', 'breakersrewhard',
                          'breakersreqward', 'breakerhreward', 'breakersrewawrd', 'breakersrewdard', 'breakezsreward',
                          'breakersreqard', 'breakersrewcrd', 'breakersrewarvd', 'breakerdsreward', 'breakersredard',
                          'breakersrewamrd', 'breakesrsreward', 'brieakersreward', 'breakersrewnard', 'breakersrewarg',
                          'breakeorsreward', 'breaykersreward', 'breakersrehward', 'breakfrsreward', 'breakersrewiard',
                          'breakersrewark', 'breakeresreward', 'breakerasreward', 'breskersreward', 'bretakersreward',
                          'breakersrveward', 'breokersreward', 'bneakersreward', 'breakersrewarld', 'bdreakersreward',
                          'breakersroward', 'breakersregward', 'brgakersreward', 'breakersrewarad', 'breakersrewarl',
                          'brevakersreward', 'breakersrewqard', 'brxakersreward', 'breakersrewarpd', 'brlakersreward',
                          'breakersrewafrd', 'breakersbeward', 'breakersregard', 'breakersrecward', 'bareakersreward',
                          'breakersrewkrd', 'breakersrkward', 'breakersrewari', 'breakersrneward', 'breakgrsreward',
                          'brueakersreward', 'bjeakersreward', 'breakcersreward', 'vreakersreward', 'breakersrewacrd',
                          'breakersrewardk', 'breaksersreward', 'breakeprsreward', 'breatkersreward', 'hbreakersreward',
                          'brerkersreward', 'breakersreiward', 'breakersrewardh', 'breakersgeward', 'breakersrewarnd',
                          'breakeroreward', 'breazkersreward', 'bredakersreward', 'bleakersreward', 'breakersretward',
                          'brbeakersreward', 'bmeakersreward', 'braakersreward', 'brvakersreward', 'breakeirsreward',
                          'breakersroeward', 'breakersrewaad', 'lbreakersreward', 'breakersrewgrd', 'breakersrewarsd',
                          'breakersrewardo', 'breakertsreward', 'breakersreuward', 'bqreakersreward', 'breakjrsreward',
                          'breakersrrward', 'breakersrewand', 'bjreakersreward', 'mreakersreward', 'breakersrbward',
                          'breakersfreward', 'breakersrewardu', 'blreakersreward', 'breakersreyward', 'breykersreward',
                          'breakersoeward', 'breakersrdeward', 'breakerzsreward', 'breakersrewagd', 'breakeksreward',
                          'brerakersreward', 'breakarsreward', 'lreakersreward', 'breapersreward', 'breakerureward',
                          'breakersrewayd', 'breakersrewaryd', 'bheakersreward', 'breakecsreward', 'brekkersreward',
                          'brweakersreward', 'breanersreward', 'breakersrewaqrd', 'breakeysreward', 'breakepsreward',
                          'breoakersreward', 'breakersrewoard', 'breaklrsreward', 'brevkersreward', 'breakersrerard',
                          'breakersrewartd', 'breakersrewardv', 'breakeqsreward', 'breaekersreward', 'bceakersreward',
                          'breakersdeward', 'brzakersreward', 'breakersrdward', 'breakersrxward', 'breakersrewaod',
                          'bseakersreward', 'breakersrleward', 'breakersrexard', 'brefakersreward', 'breuakersreward',
                          'breakersrewarp', 'breakercreward', 'breakersrevard', 'breakerbreward', 'breakebsreward',
                          'breaknersreward', 'breaeersreward', 'breakersrkeward', 'breakejsreward', 'breakersrewaurd',
                          'breakeyrsreward', 'breqkersreward', 'brewakersreward', 'brehkersreward', 'breakersrewagrd',
                          'breakerqsreward', 'breakersrewadd', 'breakersvreward', 'breakersrewarid', 'breaskersreward',
                          'breakersrerward', 'breakersrewarqd', 'brearkersreward', 'breakersueward', 'breakersrewbard',
                          'breakersrpeward', 'breakersrewarn', 'broeakersreward', 'breakerfreward', 'breadkersreward',
                          'breakerslreward', 'breiakersreward', 'breakersrewarv', 'brmakersreward', 'brteakersreward',
                          'breakaersreward', 'broakersreward', 'breakessreward', 'tbreakersreward', 'breakersrseward',
                          'bnreakersreward', 'breakersrewarbd', 'breakersrewacd', 'breakgersreward', 'breakeqrsreward',
                          'qbreakersreward', 'freakersreward', 'breakerfsreward', 'breakersrcward', 'breakqrsreward',
                          'breakursreward', 'breakersrewpard', 'breaikersreward', 'breakersrewardr', 'breakersrewamd',
                          'breaaersreward', 'braeakersreward', 'breakyrsreward', 'breazersreward', 'breakersrewdrd',
                          'treakersreward', 'breaketsreward', 'breakersredward', 'breakersrgeward', 'breakersrewared',
                          'breahkersreward', 'bkeakersreward', 'breakerszeward', 'breakersrewaord', 'breakenrsreward',
                          'breakersrewarod', 'breakersrewazd', 'breakersrewlrd', 'breakeersreward', 'breakersmeward',
                          'breakersrewadrd', 'brewkersreward', 'breakersrieward', 'breakersrewyard', 'breakersrewmrd',
                          'breakeryreward', 'breakersrewaprd', 'breakermsreward', 'cbreakersreward', 'breakersrewardq',
                          'breakersrewasd', 'breakersrewarb', 'breakersrewardn', 'breakersrejard', 'breakersrewprd',
                          'brealersreward', 'breakeusreward', 'breakersrewrard', 'breakersryeward', 'breakeisreward',
                          'breukersreward', 'breakersriward', 'nreakersreward', 'breakersrelward', 'breakersrewabd',
                          'breakersrewaxrd', 'breakersruward', 'breakersrewarr', 'breakersrgward', 'breakersrewaerd',
                          'breakersrewatd', 'breakersreoard', 'breakevrsreward', 'breakeursreward', 'breaversreward',
                          'breakersrewmard', 'breakemsreward', 'breafersreward', 'brheakersreward', 'breakersrewardg',
                          'bruakersreward', 'brkakersreward', 'breakersrewajd', 'bbeakersreward', 'breaukersreward',
                          'brxeakersreward', 'brnakersreward', 'breakersrewardm', 'breakersrxeward', 'obreakersreward',
                          'breakersrewardl', 'bdeakersreward', 'breakersremard', 'breakeasreward', 'breakirsreward',
                          'ibreakersreward', 'breadersreward', 'bureakersreward', 'vbreakersreward', 'breakrrsreward',
                          'breakqersreward', 'breakervsreward', 'breakersrfward', 'breakersrewargd', 'bweakersreward',
                          'mbreakersreward', 'brearersreward', 'breakersrewxrd', 'breakersrewardy', 'breakersrewgard',
                          'bieakersreward', 'brepkersreward', 'breaqersreward', 'breakersrewaid', 'breaoersreward',
                          'breakersrewardj', 'ireakersreward', 'breakwersreward', 'breakersteward', 'breakersrheward',
                          'breakersrewerd', 'brpakersreward', 'brekakersreward', 'breaklersreward', 'bereakersreward',
                          'breakersaeward', 'breakersrwward', 'brcakersreward', 'brefkersreward', 'breakersreeward',
                          'nbreakersreward', 'bremkersreward', 'breakerspeward', 'breakerhsreward', 'bregakersreward',
                          'breakefrsreward', 'brelakersreward', 'breakersrewardz', 'bredkersreward', 'breakerireward',
                          'breakersrewardx', 'breasersreward', 'breakersrewsrd', 'breakersrewaird', 'bqeakersreward',
                          'breakergsreward', 'breakmrsreward', 'breafkersreward', 'breakersrewavrd', 'breakersrewarxd',
                          'breakpersreward', 'breakersoreward', 'brqeakersreward', 'breakdersreward', 'jbreakersreward',
                          'ubreakersreward', 'breakdrsreward', 'breakersrewaud', 'breakersareward', 'breaknrsreward',
                          'breakersrewarda', 'breakercsreward', 'bxreakersreward', 'breakernreward', 'wbreakersreward',
                          'breakersrewajrd', 'breakersrewavd', 'breckersreward', 'brepakersreward', 'breakervreward',
                          'breakersxreward', 'breakersrewarw', 'breakerusreward', 'breakersrnward', 'bryakersreward',
                          'brjakersreward', 'breakersrewaro', 'breakersrewarh', 'boeakersreward', 'breakersrewxard',
                          'greakersreward', 'breakersrewarx', 'breqakersreward', 'brecakersreward', 'breakensreward',
                          'brzeakersreward', 'breakersleward', 'oreakersreward', 'breamersreward', 'sreakersreward',
                          'breaktersreward', 'brgeakersreward', 'brseakersreward', 'breakersrewasrd', 'breakersqreward',
                          'brleakersreward', 'breakersrevward', 'breakersrteward', 'breakerseeward', 'yreakersreward',
                          'areakersreward', 'breakxersreward', 'breankersreward', 'breakerdreward', 'breakersrewaqd',
                          'breakershreward', 'breakersrewlard', 'breakersseward', 'breakerisreward', 'breakersyeward',
                          'breakelrsreward', 'breakedsreward', 'zreakersreward', 'breakersrewarzd', 'breakbrsreward',
                          'breakerareward', 'bmreakersreward', 'breakersrewarhd', 'breakerrsreward', 'bzeakersreward',
                          'bremakersreward', 'brneakersreward', 'breakjersreward', 'breakegrsreward', 'breakersrewzard',
                          'breakersbreward', 'breakersrtward', 'brehakersreward', 'breakwrsreward', 'breakersrewardi',
                          'preakersreward', 'brexakersreward', 'bpreakersreward', 'breakersrpward', 'hreakersreward',
                          'byreakersreward', 'breakersrewardw', 'breakerzreward', 'breakexsreward', 'brpeakersreward',
                          'breakuersreward', 'breakerwreward', 'bvreakersreward', 'brfakersreward', 'breakerksreward',
                          'abreakersreward', 'breakersraeward', 'breakersrewarq', 'breakersrewjrd', 'breaxersreward',
                          'brenakersreward', 'boreakersreward', 'breeakersreward', 'breakiersreward', 'brealkersreward',
                          'brkeakersreward', 'breakersreuard', 'breakersrewaed', 'bzreakersreward', 'breakexrsreward',
                          'breakerqreward', 'breakersrewatrd', 'breakersrewqrd', 'breakersrewary', 'zbreakersreward',
                          'breakersrewakrd', 'brelkersreward', 'breakersrewardc', 'bfeakersreward', 'breahersreward',
                          'breakersrewart', 'breakeesreward', 'breakersrewbrd', 'bueakersreward', 'breakebrsreward',
                          'brezkersreward', 'brejakersreward', 'breakersrewazrd', 'breakersnreward', 'breayersreward',
                          'breakersrewars', 'breakersrewarf', 'b3eakersreward', 'b4eakersreward', 'b5eakersreward',
                          'b#eakersreward', 'b$eakersreward', 'b%eakersreward', 'br4akersreward', 'br3akersreward',
                          'br2akersreward', 'br$akersreward', 'br#akersreward', 'br@akersreward', 'brea.ersreward',
                          'brea,ersreward', 'brea>ersreward', 'brea<ersreward', 'break4rsreward', 'break3rsreward',
                          'break2rsreward', 'break$rsreward', 'break#rsreward', 'break@rsreward', 'breake3sreward',
                          'breake4sreward', 'breake5sreward', 'breake#sreward', 'breake$sreward', 'breake%sreward',
                          'breakers3eward', 'breakers4eward', 'breakers5eward', 'breakers#eward', 'breakers$eward',
                          'breakers%eward', 'breakersr4ward', 'breakersr3ward', 'breakersr2ward', 'breakersr$ward',
                          'breakersr#ward', 'breakersr@ward', 'breakersre1ard', 'breakersre2ard', 'breakersre3ard',
                          'breakersre!ard', 'breakersre@ard', 'breakersre#ard', 'breakersrewa3d', 'breakersrewa4d',
                          'breakersrewa5d', 'breakersrewa#d', 'breakersrewa$d', 'breakersrewa%d', 'bsitems', 'bbiteos',
                          'bbiems', 'bbixems', 'bbietms', 'bbiotems', 'bbivtems', 'jbitems', 'bbitcems', 'bbiiems',
                          'fbitems', 'bitems', 'bbitems', 'bbitesm', 'bbtems', 'bbiteme', 'bbitemss', 'nbbitems',
                          'bbfitems', 'ebbitems', 'bbtiems', 'bbites', 'bbitehs', 'bbitemsd', 'bgbitems', 'bbiutems',
                          'bibtems', 'gbitems', 'bbltems', 'bbitels', 'bbiltems', 'bbitemk', 'bbitemsv', 'bbitemas',
                          'wbbitems', 'bbitemr', 'bbitecms', 'bbieems', 'bbdtems', 'bbitmes', 'bbitms', 'bbitpms',
                          'bbbitems', 'bbityems', 'tbbitems', 'bbifems', 'bbatems', 'bbitemj', 'bbiters', 'bbitexms',
                          'bbctems', 'btitems', 'bbiitems', 'bbimems', 'bvitems', 'bbitees', 'bbitemfs', 'bbitemsc',
                          'bbitemso', 'bwitems', 'bzbitems', 'bbritems', 'bbiteqs', 'bbitzms', 'bbittems', 'bbiteis',
                          'bbitets', 'ybitems', 'bqitems', 'qbbitems', 'bbiteml', 'hbbitems', 'bbjtems', 'bbpitems',
                          'hbitems', 'bbitemsz', 'bbiktems', 'bbitemz', 'bbrtems', 'bbitmms', 'bbitcms', 'bbotems',
                          'bbiyems', 'bbitegms', 'abbitems', 'bfbitems', 'bbitxms', 'bbhitems', 'bbditems', 'bbitesms',
                          'bbiteds', 'bbitemds', 'bbiytems', 'bbioems', 'bubitems', 'bbitemls', 'sbbitems', 'bbitzems',
                          'bbizems', 'bnitems', 'bbihems', 'bbitemc', 'pbitems', 'bbwtems', 'bbiterms', 'bbiteas',
                          'bbitemsg', 'bbitlms', 'bbibtems', 'bbitemq', 'bbitema', 'bbibems', 'bbetems', 'bbitvms',
                          'bbitemsx', 'bbwitems', 'bbisems', 'babitems', 'bbitemy', 'bbitemks', 'abitems', 'bbitaems',
                          'bbuitems', 'bkitems', 'bdbitems', 'bbirems', 'bbitlems', 'bbitews', 'britems', 'bbitemd',
                          'bbiaems', 'nbitems', 'ibitems', 'rbitems', 'bbirtems', 'bbitens', 'bbqtems', 'bfitems',
                          'bbitevms', 'bbbtems', 'bbitemsq', 'bbsitems', 'bbitemis', 'bbitemys', 'bbitemo', 'bbitemv',
                          'bbitrms', 'bmbitems', 'pbbitems', 'bboitems', 'xbitems', 'bbiteps', 'bmitems', 'baitems',
                          'bbiqems', 'bbiztems', 'bbitezs', 'bbitemsk', 'bbaitems', 'bbityms', 'bbeitems', 'bbitemsf',
                          'bbitexs', 'bbijems', 'bvbitems', 'bbitqems', 'bbitwms', 'bbitsms', 'bbitpems', 'bbftems',
                          'bbitjems', 'bbitecs', 'bbipems', 'ebitems', 'bebitems', 'bbitemws', 'bbitemb', 'boitems',
                          'bbxtems', 'bbitemhs', 'bbictems', 'bbitemsb', 'bblitems', 'bgitems', 'bbitwems', 'bibitems',
                          'bbitelms', 'bbitemsy', 'bbitemsa', 'bbitgms', 'bbiatems', 'bbptems', 'bbitegs', 'buitems',
                          'bbiwems', 'bhitems', 'tbitems', 'bbqitems', 'bbitenms', 'bbitemms', 'byitems', 'bbxitems',
                          'bbitemjs', 'bbttems', 'jbbitems', 'bbittms', 'bbiteqms', 'bbitemn', 'bbitemsn', 'bbidtems',
                          'bbitemsu', 'bbitemsw', 'bkbitems', 'zbitems', 'bbztems', 'bbitemst', 'bbitfems', 'bbiqtems',
                          'bsbitems', 'bbntems', 'obbitems', 'bbitjms', 'bbitemse', 'bbitnms', 'bzitems', 'bbitemcs',
                          'bbitemqs', 'sbitems', 'bbitefms', 'bbitbms', 'bbivems', 'bbkitems', 'bbinems', 'bbitemrs',
                          'bbzitems', 'vbbitems', 'bbitoems', 'bbiteums', 'bwbitems', 'bbitewms', 'bbiptems',
                          'bbitemsj', 'bbitemg', 'bbitums', 'bbistems', 'bbitemvs', 'bpitems', 'bbitezms', 'bbitgems',
                          'bbitkms', 'bbitemp', 'bbitemsh', 'bbitemps', 'bjitems', 'bbitemsm', 'bbitemf', 'bbitiems',
                          'bbitemns', 'bbitemsp', 'vbitems', 'bbitbems', 'bxbitems', 'bbitdems', 'bbitqms', 'bbitemw',
                          'bbvitems', 'bcitems', 'bjbitems', 'bbiwtems', 'bbikems', 'bbytems', 'ibbitems', 'bbithms',
                          'bbitnems', 'bbiteks', 'bbitims', 'bbitejms', 'bxitems', 'gbbitems', 'bbitemsl', 'dbbitems',
                          'ybbitems', 'bbitevs', 'bobitems', 'kbbitems', 'bbmtems', 'bbitemxs', 'bbiteys', 'bbigtems',
                          'bbithems', 'bbktems', 'bbitoms', 'bbitemes', 'bbitemh', 'zbbitems', 'bbyitems', 'beitems',
                          'blitems', 'bbitsems', 'bbitrems', 'bbiteims', 'bbitemt', 'bbitemgs', 'bbitkems', 'bbtitems',
                          'bbitxems', 'bbitebms', 'bybitems', 'rbbitems', 'bcbitems', 'bbiteems', 'bbitemm', 'brbitems',
                          'bbutems', 'bbitetms', 'cbitems', 'bbiteyms', 'bbitemx', 'bbihtems', 'bbgitems', 'bbitfms',
                          'bbimtems', 'bbiteams', 'bbmitems', 'bbnitems', 'wbitems', 'bbilems', 'bbigems', 'bbitekms',
                          'bbintems', 'bbitdms', 'bbiuems', 'bbicems', 'fbbitems', 'bbvtems', 'btbitems', 'bbitebs',
                          'bbixtems', 'bbitedms', 'bbitemi', 'kbitems', 'bbitemus', 'bnbitems', 'bbitefs', 'cbbitems',
                          'bhbitems', 'bbitehms', 'bbiteoms', 'bbitejs', 'bbiftems', 'bbitembs', 'xbbitems', 'bbcitems',
                          'blbitems', 'bbitemts', 'bbstems', 'mbitems', 'bbhtems', 'bbitemsi', 'bbgtems', 'bbijtems',
                          'lbitems', 'bditems', 'bpbitems', 'bbitemsr', 'dbitems', 'bbiteus', 'bbitams', 'bbitemos',
                          'bbitvems', 'bbitess', 'biitems', 'bbitemzs', 'bqbitems', 'qbitems', 'bbjitems', 'bbidems',
                          'bbietems', 'bbitmems', 'mbbitems', 'ubbitems', 'bbitemu', 'obitems', 'lbbitems', 'bbitepms',
                          'ubitems', 'bbituems', 'bb7tems', 'bb8tems', 'bb9tems', 'bb&tems', 'bb*tems', 'bb(tems',
                          'bbi4ems', 'bbi5ems', 'bbi6ems', 'bbi$ems', 'bbi%ems', 'bbi^ems', 'bbit4ms', 'bbit3ms',
                          'bbit2ms', 'bbit$ms', 'bbit#ms', 'bbit@ms', 'bbite,s', 'bbite<s', '/breakersreward',
                          '/bbitems'],
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

"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the reward command. Displays specified reward + upcoming rewards.
"""

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import items
import stwutil as stw


class Reward(ext.Cog):
    """
    Cog for the vbucks command.
    """

    def __init__(self, client):
        self.client = client

    async def reward_command(self, ctx, day, limit=None):
        """
        The main function for the reward command.

        Args:
            ctx: The context of the command.
            day: The day to get the reward for.
            limit: The number of rewards to get.

        Returns:
            None
        """

        if limit is None:
            user_document = await self.client.get_user_document(ctx, self.client, ctx.author.id, True)
            try:
                currently_selected_profile = str(user_document["global"]["selected_profile"])
                limit = user_document["profiles"][currently_selected_profile]["settings"]["upcoming_display_days"]
            except:
                limit = 7

        # quick check to see if ctx author can get vbucks
        vbucks = True
        try:
            temp_auth = self.client.temp_auth[ctx.author.id]
            vbucks = temp_auth["vbucks"]

            if day == 'hi readers of the bot':
                try:
                    daye = temp_auth["day"]
                    if daye is not None:
                        day = daye
                except KeyError:
                    pass

        except KeyError:
            pass

        embed_colour = self.client.colours["reward_magenta"]
        if day == 'hi readers of the bot':
            embed = await stw.create_error_embed(self.client, ctx,
                                                 description=f"**No day specified**\n"
                                                             f"⦾ You need to specify a day to get the reward for\n"
                                                             f"⦾ For example, "
                                                             f"{await stw.mention_string(self.client, 'reward 336')}",
                                                 error_level=0, command="reward", prompt_help=True,
                                                 prompt_authcode=False)
            await stw.slash_send_embed(ctx, embed)
            return

        else:
            try:
                day = int(day)
            except ValueError:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description="**Invalid number**\n"
                                                                 "⦾ The given day must be a number",
                                                     error_level=0, prompt_help=True, prompt_authcode=False,
                                                     command="reward")
                await stw.slash_send_embed(ctx, embed)
                return
            try:
                limit = int(limit)
            except ValueError:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description="**Invalid number**\n"
                                                                 "⦾ The limit must be a number",
                                                     error_level=0, prompt_help=True, prompt_authcode=False,
                                                     command="reward")
                await stw.slash_send_embed(ctx, embed)
                return
            if limit < 0:
                limit = 7
            if day <= 0:
                day = 1

            limit_str = f" and **{limit:,}** days after" if limit >= 1 else ""
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Reward", "stormeye"),
                                  description=f'\u200b\nDisplaying rewards for day **{day:,}**{limit_str}\n\u200b',
                                  color=embed_colour)

            try:
                reward = stw.get_reward(self.client, day, vbucks)
            except:
                embed = await stw.create_error_embed(self.client, ctx,
                                                     description=f"**An error occured when fetching day {day}**\n"
                                                                 f"⦾ Please let us know on the support server :D",
                                                     prompt_help=True, prompt_authcode=False, command="reward")
                await stw.slash_send_embed(ctx, embed)
                print(f"Error when getting reward for day {day}")
                return

            embed.add_field(name=f'**{reward[1]} Item: **', value=f'```{reward[0]}```\u200b')
            for day1 in items.ItemDictionary:
                if 'V-Bucks & X-Ray Tickets' in items.ItemDictionary[day1][0]:
                    if int(day) % 336 < int(day1):
                        if int(day1) - int(day) % 336 == 1:
                            day_string = "day"
                        else:
                            day_string = "days"

                        if vbucks is True:
                            embed.add_field(
                                name=f'**{self.client.config["emojis"]["vbucks"]}{self.client.config["emojis"]["xray"]}'
                                     f' Next V-Bucks & X-Ray Tickets reward:**',
                                value=f'```{stw.get_reward(self.client, day1)[0]} in {int(day1) - int(day) % 336} '
                                      f'{day_string}```\u200b', inline=False)
                        else:
                            embed.add_field(
                                name=f'**{self.client.config["emojis"]["xray"]} Next X-Ray Tickets reward:**',
                                value=f'```{stw.get_reward(self.client, day1, False)[0]} in '
                                      f'{int(day1) - int(day) % 336} {day_string}```\u200b', inline=False)
                        break
            if limit >= 1:
                rewards = ''
                max_rewards_reached = False
                if limit > 100:
                    limit = 100
                for day2 in range(1, limit + 1):
                    if len(rewards) > 1000:
                        rewards = stw.truncate(rewards, 1000)
                        limit = day2
                        max_rewards_reached = True
                        break
                    rewards += stw.get_reward(self.client, day2 + int(day), vbucks)[0]
                    if not (day2 + 1 == limit + 1):
                        rewards += ', '
                    else:
                        rewards += '.'
                    if day2 % 7 == 0:
                        rewards += '\n\n'
                if limit == 1:
                    reward = stw.get_reward(self.client, int(day) + 1, vbucks)

                    embed.add_field(name=f'**{reward[1]} Tomorrow\'s reward:**', value=f'```{reward[0]}```\u200b',
                                    inline=False)
                else:
                    embed.add_field(
                        name=f'{self.client.config["emojis"]["calendar"]} Rewards for the next '
                             f'**{"~" if max_rewards_reached else ""}{limit}** days:',
                        value=f'```{rewards}```\u200b', inline=False)
                    if max_rewards_reached:
                        embed.description = f'\u200b\nDisplaying rewards for day **{day:,}** ' \
                                            f'and **~{limit:,}** days after\n\u200b'

            embed = await stw.set_thumbnail(self.client, embed, "stormbottle")
            embed = await stw.add_requested_footer(ctx, embed)

            await stw.slash_send_embed(ctx, embed)

    @ext.command(name='reward',
                 aliases=['reqward',
                          'it4ms', 'i6tems',
                          'geward', 'rewarrd', 'rewwrd',
                          'rewared', 'feward', 'iteems', 'itfms',
                          'iutems', 'reaard', 'ite4ms', 'litems', 'itrms',
                          'itsms', 'rewardc', 'rewaard', 'rewa4d', 'r5eward', 'rewarr',
                          'ittems', 'iytems', 'treward', 'deward', 'itemx', 'reard', 're2ward',
                          'itemsx', 'rewafrd', 'reware', 'itemms', '4reward', 'rwrd', 'rewrerd', 'itemns',
                          'rwward', 'rewa5rd', 'uitems', 'rfward', 'itejs', 'itemds', 'itens', 'resward', 'rgeward',
                          'iftems', 'iotems', 'greward', 'teward', 'ereward', 'itemsa', 'itemsd', 'itemws', 'rewa4rd',
                          'erward', 'rewar', 'rew3ard', 'rewawrd', 'rewatrd', 'irtems', 'oitems', 'ltems', 'itenms',
                          'rewar5d',
                          'rewsard', 'iitems', '9items', 'itdems', 'itedms', 'resard', 'itsems', 'rewardx', 'rerward',
                          'jitems', 'itemzs',
                          'rewqard', 'eeward', 'iems', 'ktems', 'itwems', 'rewar4d', 'rewarde', 'rewrad', 'it5ems',
                          'rewadr', 'otems', 'tems',
                          'itemsw', 'r3eward', 'rrward', 'refward', 'itemz', 'rew2ard', 'itemes', 'itemd', 'rewagd',
                          'rewaqrd', 'rewazrd', 'igems',
                          'rewafd', 'itesm', 'itemas', 'itemjs', 're4ward', 'rewrd', 'itemw', 're3ward', 'reqard',
                          'rward', 'ietms', '5reward', 'rewsrd',
                          'rreward', 'dreward', 'rweward', 'reaward', 'itwms', 'rewadd', 'itms', 'rewward', 'rdeward',
                          'reawrd', 'itgems', 'ifems', 'it3ems',
                          'freward', 'itemse', 'rweard', '4eward', 'rewaxrd', 'rewars', 'rewadrd', 'iteme', 'itema',
                          'rewardd', 'rewdard', 'itemsz', 'rewarsd',
                          'reweard', 'ihtems', 'rewzard', 'itekms', 'item', 'itemxs', '8items', 'eward', 'rewa5d',
                          'iterms', 'rewarc', 'tiems', 'iktems', 're3ard',
                          'itfems', 'rfeward', 'utems', 'rewxrd', 'rewzrd', 'ijtems', 'rsward', 'r3ward', 'r4eward',
                          'ites', 'rewarfd', '9tems', 'rewards', 'rseward',
                          'jtems', 'rewardf', 'itemks', 'i5tems', 'ite3ms', 'reeward', 'rewasrd', 'rewargd', 'i9tems',
                          'rewartd', 'rewatd', 'items', 'redward', 'rewarcd',
                          'rteward', 'kitems', 'itmes', 'it6ems', 'itesms', 'rewad', 'rewaerd', '8tems', 'itewms',
                          'reeard', 'ityems', 'rewxard', 'rdw', 'itdms', 'rewardr',
                          'igtems', 'rewarxd', 'rdward', 're2ard', 'irems', 'i5ems', 'r4ward', 'iyems', 'iltems',
                          'ithems', '5eward', 'itrems', 'rewarf', 'redard', 'ihems',
                          'i6ems', 'rewarx', 'i8tems', 'itefms', 'rwd', 'itejms', 'it4ems', 'itemss', 'iteks', 'it3ms',
                          'rewaed', 'rewqrd', 'rewagrd', '/reward', '/items', '/rwrd',
                          '/itm', 'wrd', 'rrd', 'rwr', 'rrwrd', 'rwwrd', 'rwrrd', 'rwrdd', 'wrrd', 'rrwd', 'rwdr',
                          'ewrd', '4wrd', '5wrd', 'twrd', 'gwrd', 'fwrd', 'dwrd', 'rqrd', 'r2rd', 'r3rd', 'rerd',
                          'rdrd', 'rsrd', 'rard', 'rwed', 'rw4d',
                          'rw5d', 'rwtd', 'rwgd', 'rwfd', 'rwdd', 'rwrs', 'rwre', 'rwrr', 'rwrf', 'rwrc', 'rwrx',
                          'erwrd', '4rwrd', 'r4wrd', '5rwrd', 'r5wrd', 'trwrd', 'rtwrd', 'grwrd', 'rgwrd', 'frwrd',
                          'rfwrd', 'drwrd', 'rdwrd', 'rqwrd', 'rwqrd', 'r2wrd', 'rw2rd', 'r3wrd', 'rw3rd', 'rwerd',
                          'rwdrd', 'rswrd', 'rwsrd', 'rawrd', 'rwred', 'rw4rd', 'rwr4d', 'rw5rd', 'rwr5d', 'rwtrd',
                          'rwrtd', 'rwgrd', 'rwrgd', 'rwfrd', 'rwrfd', 'rwrsd', 'rwrds', 'rwrde', 'rwrdr', 'rwrdf',
                          'rwrcd', 'rwrdc', 'rwrxd', 'rwrdx', 'tm', 'im', 'it', 'iitm', 'ittm', 'itmm', 'tim', 'imt',
                          'utm', '8tm', '9tm', 'otm', 'ltm', 'ktm', 'jtm', 'irm', 'i5m', 'i6m', 'iym', 'ihm', 'igm',
                          'ifm', 'itn', 'itj', 'itk', 'uitm', 'iutm', '8itm', 'i8tm', '9itm', 'i9tm', 'oitm', 'iotm',
                          'litm', 'iltm', 'kitm', 'iktm', 'jitm', 'ijtm', 'irtm', 'itrm', 'i5tm', 'it5m', 'i6tm',
                          'it6m', 'iytm', 'itym', 'ihtm', 'ithm', 'igtm', 'itgm', 'iftm', 'itfm', 'itnm', 'itmn',
                          'itjm', 'itmj', 'itkm', 'itmk'],
                 extras={'emoji': "stormeye", "args": {'day': 'The day to get the rewards of. Not required if you are '
                                                              'authenticated',
                                                       'limit': 'The number of upcoming days to see (Optional)'},
                         "dev": False},
                 brief="View info about a specific day\'s reward, and the rewards that follow",
                 description="This command lets you view the rewards of any specific day, and any number of rewards "
                             "that follow")
    async def reward(self, ctx, day='hi readers of the bot', limit=None):
        """
        This function is the entry point for the vbucks command when called traditionally

        Args:
            ctx: The context of the command
            day: The day to get the rewards of. Not required if you are authenticated
            limit: The number of upcoming days to see (Optional)
        """
        await self.reward_command(ctx, day, limit)

    @slash_command(name='reward',
                   description='View info about a specific day\'s reward, and the rewards that follow',
                   guild_ids=stw.guild_ids)
    async def slashreward(self, ctx: discord.ApplicationContext,
                          day: Option(int,
                                      "The day to get the rewards of. Not required if you are authenticated") = 'hi readers of the bot',
                          limit: Option(int, "The number of upcoming days to see") = None):
        """
        This function is the entry point for the reward command when called via slash

        Args:
            ctx: The context of the slash command
            day: The day to get the rewards of. Not required if you are authenticated
            limit: The number of upcoming days to see
        """
        await self.reward_command(ctx, day, limit)


def setup(client):
    """
        This function is called when the cog is loaded via load_extension

        Args:
            client: The bot client
        """
    client.add_cog(Reward(client))

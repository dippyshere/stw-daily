import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# cog for the reward command.
class BBReward(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def bbreward_command(self, ctx, day, limit=7, slash=False):

        try:
            temp_auth = self.client.temp_auth[ctx.author.id]
            if day == 'hi readers of the bot':
                daye = temp_auth["bb_day"]
                if daye is not None:
                    day = daye
        except:
            pass

        embed_colour = self.client.colours["reward_magenta"]
        err_colour = self.client.colours["error_red"]
        if day == 'hi readers of the bot':

            embed = discord.Embed(colour=err_colour,
                                  title=await stw.add_emoji_title(self.client, "Missing Day", "error"),
                                  description="```Please specify the day (number) of which you would like to see```")
            embed = await stw.add_requested_footer(ctx, embed)
            embed = await stw.set_thumbnail(self.client, embed, "error")
            await stw.slash_send_embed(ctx, slash, embed)

        else:
            try:
                day = int(day)
                limit = int(limit)

                if limit < 1:
                    limit = 7

            except:
                embed = discord.Embed(colour=err_colour,
                                      title=await stw.add_emoji_title(self.client, "Non Numeric Day or Limit", "error"),
                                      description="```The inputted day or limit must be a valid integer, please try again```")
                embed = await stw.add_requested_footer(ctx, embed)
                embed = await stw.set_thumbnail(self.client, embed, "error")
                await stw.slash_send_embed(ctx, slash, embed)
                return

            if int(limit) > 100:
                embed = discord.Embed(colour=err_colour,
                                      title=await stw.add_emoji_title(self.client, "Too Long", "error"),
                                      description="```You attempted to retrieve too many days after! Try a lower value```")
                embed = await stw.add_requested_footer(ctx, embed)
                embed = await stw.set_thumbnail(self.client, embed, "error")
                await stw.slash_send_embed(ctx, slash, embed)
                return

            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Reward", "placeholder"),
                                  description=f'\u200b\nDisplaying rewards for day **{day}** and **{limit}** days after\n\u200b',
                                  color=embed_colour)

            try:
                # day, name, emoji_text, description, quantity
                reward = stw.get_bb_reward_data(self.client, pre_calc_day=day)
            except:
                embed = discord.Embed(colour=err_colour,
                                      title=await stw.add_emoji_title(self.client, "Invalid Day", "error"),
                                      description="```Please retry with a valid integer.```")
                embed = await stw.add_requested_footer(ctx, embed)
                embed = await stw.set_thumbnail(self.client, embed, "error")
                await stw.slash_send_embed(ctx, slash, embed)
                return

            embed.add_field(name=f'**{reward[2]} Item: **', value=f'```{reward[4]} {reward[1]}```\u200b')
            for row in stw.LoginRewards[0]['Rows']:
                if 'MtxGiveaway' in stw.LoginRewards[0]['Rows'][row]['ItemDefinition']['AssetPathName']:
                    if int(day) % 1800 < int(row):
                        if int(row) - int(day) % 1800 == 1:
                            day_string = "day."
                        else:
                            day_string = "days."
                        embed.add_field(
                            name=f'**{self.client.config["emojis"]["T_MTX_Gem_Icon"]} Next Gem reward in: **',
                            value=f'```{int(row) - int(day) % 1800} {day_string}```\u200b', inline=False)
                        break

            rewards = ''
            for i in range(1, limit + 1):
                data = stw.get_bb_reward_data(self.client, pre_calc_day=day + i)
                rewards += str(data[4]) + " " + str(data[1])
                if not (i + 1 == limit + 1):
                    rewards += ', '
                else:
                    rewards += '.'
            if limit == 1:
                reward = stw.get_bb_reward_data(self.client, pre_calc_day=day + 1)

                embed.add_field(name=f'**{reward[2]} Tomorrow\'s reward:**',
                                value=f'```{reward[4]} {reward[1]}```\u200b',
                                inline=False)
            else:
                embed.add_field(
                    name=f'{self.client.config["emojis"]["calendar"]} Rewards for the next **{limit}** days:',
                    value=f'```{rewards}```\u200b', inline=False)

            embed = await stw.set_thumbnail(self.client, embed, "placeholder")
            embed = await stw.add_requested_footer(ctx, embed)

            try:
                await stw.slash_send_embed(ctx, slash, embed)
            except discord.errors.HTTPException:
                embed = discord.Embed(colour=err_colour,
                                      title=await stw.add_emoji_title(self.client, "Too Long", "error"),
                                      description="```You attempted to retrieve too many days after! Try a lower value```")
                embed = await stw.add_requested_footer(ctx, embed)
                embed = await stw.set_thumbnail(self.client, embed, "error")
                await stw.slash_send_embed(ctx, slash, embed)

    @ext.command(name='bbreward',
                 aliases=['bbr', 'bbrwrd', 'battlebreakersreward'],
                 extras={'emoji': "placeholder", "args": {'day': 'The day to view the reward for',
                                                          'limit': 'The amount of days after the specified days that rewards will be given for (Optional)'}},
                 brief="View daily rewards from a certain day for a certain amount of days after",
                 description="Allows you to utilise the built in library for items to view Battle Breakers rewards starting from a certain day and for a certain amount of days afterwards")
    async def bbreward(self, ctx, day='hi readers of the bot', limit='7'):
        await self.bbreward_command(ctx, day, int(limit))

    @slash_command(name='bbreward',
                   description='View daily rewards from a certain day for a certain amount of days after.',
                   guild_ids=stw.guild_ids)
    async def bbslashreward(self, ctx: discord.ApplicationContext,
                            day: Option(int, "The day you would like to view rewards for") = 'hi readers of the bot',
                            limit: Option(int, "The amount of days you would like to view rewards for after") = 7):
        await self.bbreward_command(ctx, day, limit, True)


def setup(client):
    client.add_cog(BBReward(client))

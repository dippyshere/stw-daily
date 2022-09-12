import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import items
import stwutil as stw


# cog for the reward command.
class Reward(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def reward_command(self, ctx, day, limit=7, slash=False):

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
                except:
                    pass

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

            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Reward", "stormeye"),
                                  description=f'\u200b\nDisplaying rewards for day **{day}** and **{limit}** days after\n\u200b',
                                  color=embed_colour)

            try:
                reward = stw.get_reward(self.client, day, vbucks)
            except:
                embed = discord.Embed(colour=err_colour,
                                      title=await stw.add_emoji_title(self.client, "Invalid Day", "error"),
                                      description="```Please retry with a valid integer.```")
                embed = await stw.add_requested_footer(ctx, embed)
                embed = await stw.set_thumbnail(self.client, embed, "error")
                await stw.slash_send_embed(ctx, slash, embed)
                return

            embed.add_field(name=f'**{reward[1]} Item: **', value=f'```{reward[0]}```\u200b')
            for day1 in items.ItemDictionary:
                if 'V-Bucks & X-Ray Tickets' in items.ItemDictionary[day1][0]:
                    if int(day) % 336 < int(day1):
                        if int(day1) - int(day) % 336 == 1:
                            day_string = "day."
                        else:
                            day_string = "days."

                        if vbucks is True:
                            embed.add_field(
                                name=f'**{self.client.config["emojis"]["vbucks"]}{self.client.config["emojis"]["xray"]} Next V-Bucks & X-Ray Tickets reward in: **',
                                value=f'```{int(day1) - int(day) % 336} {day_string}```\u200b', inline=False)
                        else:
                            embed.add_field(
                                name=f'**{self.client.config["emojis"]["xray"]} Next X-Ray Tickets reward in: **',
                                value=f'```{int(day1) - int(day) % 336} {day_string}```\u200b', inline=False)
                        break

            rewards = ''
            for day2 in range(1, limit + 1):
                rewards += stw.get_reward(self.client, day2 + int(day), vbucks)[0]
                if not (day2 + 1 == limit + 1):
                    rewards += ', '
                else:
                    rewards += '.'
            if limit == 1:
                reward = stw.get_reward(self.client, int(day) + 1, vbucks)

                embed.add_field(name=f'**{reward[1]} Tomorrow\'s reward:**', value=f'```{reward[0]}```\u200b',
                                inline=False)
            else:
                embed.add_field(
                    name=f'{self.client.config["emojis"]["calendar"]} Rewards for the next **{limit}** days:',
                    value=f'```{rewards}```\u200b', inline=False)

            embed = await stw.set_thumbnail(self.client, embed, "stormbottle")
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

    @ext.command(name='reward',
                 aliases=['rwd', 'rwrd', 'rdw', 'rewrerd', 'rewar', 'items', 'rewards'],
                 extras={'emoji': "stormeye", "args": {'day': 'The day to view the reward for',
                                                       'limit': 'The amount of days after the specified days that rewards will be given for (Optional)'}},
                 brief="View daily rewards from a certain day for a certain amount of days after",
                 description="Allows you to utilise the built in library for items to view your Save The World rewards starting from a certain day and for a certain amount of days afterwards")
    async def reward(self, ctx, day='hi readers of the bot', limit='7'):
        await self.reward_command(ctx, day, limit)

    @slash_command(name='reward',
                   description='View daily rewards from a certain day for a certain amount of days after.',
                   guild_ids=stw.guild_ids)
    async def slashreward(self, ctx: discord.ApplicationContext,
                        day: Option(int, "The day you would like to view rewards for")='hi readers of the bot',
                        limit: Option(int, "The amount of days you would like to view rewards for after") = 7):
        await self.reward_command(ctx, day, limit, True)


def setup(client):
    client.add_cog(Reward(client))

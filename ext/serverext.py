"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the server extensions. Currently: reminder + trading nag
"""

import datetime

import discord
import discord.ext.commands as ext
from discord.ext import tasks

import stwutil as stw


class Reminder(ext.Cog):
    """
    Cog for the Reminder task
    """

    def __init__(self, client):
        self.client = client
        self.dailyreminder.start()

    @tasks.loop(time=datetime.time(tzinfo=datetime.timezone.utc))
    async def dailyreminder(self):
        """
        Sends a reminder to the stw dailies reminder channel

        Returns:
            None
        """
        await self.client.wait_until_ready()
        # TODO: change channel back to 956006055282896976
        channel = self.client.get_channel(956006055282896976)

        def is_me(m):
            """
            Checks if the message is from the bot

            Args:
                m: the message to check

            Returns:
                bool: True if from bot, False if not
            """
            return m.author == self.client.user

        await channel.purge(limit=2, check=is_me)
        # TODO: add something about free llamas here
        # skuby was here
        embed = discord.Embed(title='Daily reminder:',
                              description=f'You can now claim today\'s daily reward. \n '
                                          f'Next daily reminder <t:{stw.get_tomorrow_midnight_epoch()}:R>.',
                              colour=discord.Colour.blue())
        embed.add_field(name='Item shop:', value='[fnbr.co/shop](https://fnbr.co/shop)', inline=True)
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='Mission alerts:', value='[seebot.dev/missions.php](https://seebot.dev/missions.php)',
                        inline=True)
        embed.add_field(name='Auth code link:',
                        value='[epicgames.com/id/api/redirect...]('
                              'https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6'
                              '&responseType=code)',
                        inline=True)
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='Claiming channel:', value='<#757768833946877992>', inline=True)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/748078936424185877/924999902612815892/infostwdaily.png')
        embed.set_footer(text=f"This is an automated daily reminder from {self.client.user.name}",
                         icon_url=self.client.user.avatar.url)
        await channel.send("<@&956005357346488341>", embed=embed)
        # skuby left here


class TradingNag(ext.Cog):
    """
    Cog for the trading nag task
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        self.tradingnag.start()

    @tasks.loop(time=datetime.time(7, tzinfo=datetime.timezone.utc))
    async def tradingnag(self):
        """
        Sends a trading nag to the stw dailies trading channel everyday at 7am UTC (6pm aest)

        Returns:
            None
        """
        await self.client.wait_until_ready()
        # TODO: change channel back to 997924614548226078
        channel = self.client.get_channel(997924614548226078)
        succ_colour = self.client.colours["success_green"]

        def is_me(m):
            """
            Checks if the message is from the bot

            Args:
                m: the message to check

            Returns:
                bool: True if from bot, False if not
            """
            return m.author == self.client.user

        async for message in channel.history(limit=6):
            if message.author == self.client.user:
                return                              #         🥺
        await channel.purge(limit=50, check=is_me)  # is me? 👉👈
        # hi
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Welcome to the trading channel!",
                                            "library_chat"),
            description=f"\u200b\n"
                        f"{self.emojis['library_clipboard']} **Some rules:**\n"
                        f"```diff\n"
                        f"- Scam = Clowned\n"
                        f"- If scammed, DM mods with proof + Discord ID"
                        f"```\u200b",
            colour=succ_colour)
        embed.set_footer(text=f"\nTrading nag for STW Dailies", icon_url=self.client.user.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        embed = await stw.set_thumbnail(self.client, embed, "fleming")
        await channel.send(embed=embed)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Reminder(client))
    client.add_cog(TradingNag(client))

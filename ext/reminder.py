import datetime

import discord
import discord.ext.commands as ext
from discord.ext import tasks


# cog for the reminder task
class Reminder(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        self.dailyreminder.start()

    # simple task to send reminder to stw dailies reminder channel everyday
    @tasks.loop(time=datetime.time(0, 0, tzinfo=datetime.timezone.utc))
    async def dailyreminder(self):
        await self.client.wait_until_ready()
        # TODO: change channel back to 956006055282896976
        channel = self.client.get_channel(956006055282896976)

        def is_me(m):
            return m.author == self.client.user

        await channel.purge(limit=2, check=is_me)
        # skuby was here
        embed = discord.Embed(title='Daily reminder:',
                              description=f'You can now claim today\'s daily reward. \n '
                                          f'Next daily reminder <t:{int(datetime.datetime.combine(datetime.datetime.utcnow() + datetime.timedelta(days=1), datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).timestamp())}:R>.',
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


def setup(client):
    client.add_cog(Reminder(client))

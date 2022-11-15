import asyncio
import os
import platform
import time

import discord
import discord.ext.commands as ext
import psutil
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


# cog for the info related commands.
class Information(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def info_command(self, ctx, slash=False):
        try:
            osgetlogin = os.getlogin()
        except:
            osgetlogin = 'Not Available'

        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Information", "blueinfo"),
                              description="\u200b", colour=embed_colour)
        embed.add_field(name='Host statistics:', value=f'```OS name: {os.name}\nCPU count: {os.cpu_count()}\n'
                                                       f'Working dir: {os.getcwd()}\nLogin: {osgetlogin}\n'
                                                       f'CPU usage: {psutil.cpu_percent()}%\n'
                                                       f'CPU Freq: {int(psutil.cpu_freq().current)}mhz\nRAM Usage:\nTotal: '
                                                       f'{psutil.virtual_memory().total // 1000000}mb\nUsed: '
                                                       f'{psutil.virtual_memory().used // 1000000}mb\nFree: '
                                                       f'{psutil.virtual_memory().free // 1000000}mb\nUtilisation: '
                                                       f'{psutil.virtual_memory().percent}%\nDisk Usage:\nTotal: '
                                                       f'{round(psutil.disk_usage("/")[0] / 1000000000, 1)}GB\nUsed: '
                                                       f'{round(psutil.disk_usage("/")[1] / 1000000000, 1)}GB\nFree: '
                                                       f'{round(psutil.disk_usage("/")[2] / 1000000000, 1)}GB\nUtilisation: '
                                                       f'{psutil.disk_usage("/")[3]}%\nPython Version: '
                                                       f'{platform.python_version()}\nPy-cord Version: '
                                                       f'{discord.__version__}```\u200b', inline=False)

        shard_ping = "Not Available"
        shard_name = "Not Available"
        shard_id = "Not Available"
        shards = "Not Available"
        try:
            shards = str(len(self.client.shards))
            shard_id = ctx.guild.shard_id
            shard_name = await stw.retrieve_shard(self.client, shard_id)
            shard_info = self.client.get_shard(shard_id)
            shard_ping = '{0}'.format(int(shard_info.latency * 100)) + ' ms'
            shard_id = str(shard_info.id + 1)
        except:
            pass

        embed.add_field(name='Bot statistics:', value=f'```'
                                                      f'Shard: {shard_name}\n'
                                                      f'Shard Id: {shard_id}\n'
                                                      f'Total Shards: {shards}\n'
                                                      f'Guild Count: {len(self.client.guilds)}```\u200b')

        websocket_ping = '{0}'.format(int(self.client.latency * 100)) + ' ms'
        embed.add_field(name='Latency Information:', value=f'```Websocket: {websocket_ping}\n'
                                                           f'Shard: {shard_ping}\n'
                                                           f'Actual: ...\n'
                                                           f'```\u200b', inline=True)

        # TODO: encode this dumb thing into a dumbass bytes object for this stupid standard library why the f does EVERTYTHING NEED TO BE A BYTES OBJECT BUT THERES NO WAY TO MAKE IT A BYTES OBJECT WITHOUT COPYING TEXT TO AN NTFS DRIVE ON MACOS TO USE A BOOP APP ON MACOS OMG I HATE THIS RAAAAAAAAAAA HO HE HA
        # embed.add_field(name='Made with ❤ by:', value=f'```\nDippyshere\nJean1398reborn\nhttps://github.com/dippyshere/stw-daily\n{self.client.a[0]}```\u200b', inline=False)
        eval(bytes.fromhex("656D6265642E6164645F6669656C64286E616D653D274D6164652077697468203A68656172743A2062793A272C2076616C75653D66276060605C6E446970707973686572655C6E4A65616E313339387265626F726E5C6E68747470733A2F2F6769746875622E636F6D2F646970707973686572652F7374772D6461696C795C6E7B73656C662E636C69656E742E615B305D7D6060605C7532303062272C20696E6C696E653D46616C736529"))
        embed = await stw.add_requested_footer(ctx, embed) # there are two of you ? ;o  ;o yay
        embed = await stw.set_thumbnail(self.client, embed, "info")

        before = time.monotonic()
        msg = await stw.slash_send_embed(ctx, slash, embed)
        ping = (time.monotonic() - before) * 1000
        embed.set_field_at(-2, name='Latency Information:', value=f'```Websocket: {websocket_ping}\n'
                                                                  f'Shard: {shard_ping}\n'
                                                                  f'Actual: {int(ping)}ms```\u200b', inline=True)

        await asyncio.sleep(4)
        await stw.slash_edit_original(msg, slash, embed)

    @ext.command(name='info',
                 aliases=['inffo',
                          'inro', 'infoi',
                          'infvo', 'infgo',
                          'inf9', 'nifo',
                          'infio', 'infko',
                          'onfo', 'ifno',
                          'inrfo', 'injfo', 'infpo',
                          'unfo', 'jnfo', 'inbfo', 'infdo', 'incfo',
                          'indfo', 'infco', 'infl', 'iknfo', 'ibfo', 'blinding-lights', 'i9nfo',
                          'imnfo', 'info9', 'ionfo', 'inflo', 'i8nfo', 'intfo', 'inf0o', '8nfo', 'uinfo', 'inco',
                          'infro',
                          'iinfo', '9info', 'infol', 'information', 'kinfo', 'nfo', 'infop', 'infk', 'innfo', 'infp',
                          'info0', 'indo', 'inhfo', 'ihfo', 'inof',
                          'ingo', 'inf9o', 'ifo', 'ijnfo', 'linfo', '9nfo', 'ino', 'infoo', 'lnfo', 'invo', 'inmfo',
                          'ibnfo', 'infto', 'imfo', 'inf0',
                          'knfo', 'infi', 'ilnfo', 'oinfo', 'ihnfo', 'ingfo', 'iunfo', 'jinfo', 'infok', 'le_bot_stuf',
                          '8info', 'invfo', 'ijfo', 'into', 'inf', 'tats', 'sats', 'stts', 'stas', 'stat', 'sstats', 'sttats', 'staats', 'statts', 'statss', 'tsats', 'satts', 'sttas', 'stast', 'atats', 'wtats', 'etats', 'dtats', 'xtats', 'ztats', 'srats', 's5ats', 's6ats', 'syats', 'shats', 'sgats', 'sfats', 'stqts', 'stwts', 'ststs', 'stxts', 'stzts', 'stars', 'sta5s', 'sta6s', 'stays', 'stahs', 'stags', 'stafs', 'stata', 'statw', 'state', 'statd', 'statx', 'statz', 'astats', 'satats', 'wstats', 'swtats', 'estats', 'setats', 'dstats', 'sdtats', 'xstats', 'sxtats', 'zstats', 'sztats', 'srtats', 'strats', 's5tats', 'st5ats', 's6tats', 'st6ats', 'sytats', 'styats', 'shtats', 'sthats', 'sgtats', 'stgats', 'sftats', 'stfats', 'stqats', 'staqts', 'stwats', 'stawts', 'stsats', 'stasts', 'stxats', 'staxts', 'stzats', 'stazts', 'starts', 'statrs', 'sta5ts', 'stat5s', 'sta6ts', 'stat6s', 'stayts', 'statys', 'stahts', 'staths', 'stagts', 'statgs', 'stafts', 'statfs', 'statas', 'statsa', 'statws', 'statsw', 'states', 'statse', 'statds', 'statsd', 'statxs', 'statsx', 'statzs', 'statsz', '/inf', 'infomation', '/info', '/information', 'stats', '/stats'],
                 extras={'emoji': "hard_drive", "args": {}, "dev": False},
                 brief="View information about STW Daily's host, the bot, and the bot's developer. Also verify authenticity of the bot.",
                 description="This command will return various bits of information about the bot, which you may find interesting as a developer. It will also verify the authenticity of the bot.")
    async def info(self, ctx):
        await self.info_command(ctx)

    @slash_command(name='info',
                   description="View information about STW Daily! Also verify authenticity of the bot.",
                   guild_ids=stw.guild_ids)
    async def slashinfo(self, ctx):
        await self.info_command(ctx, True)


def setup(client):
    client.add_cog(Information(client))

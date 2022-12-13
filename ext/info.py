"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the info command. displays bot / host info + verification status.
"""

import asyncio
import os
import platform
import time
import base64
import cpuinfo
import re

import discord
import discord.ext.commands as ext
import psutil
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


class Information(ext.Cog):
    """
    The info command. displays bot / host info + verification status.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def info_command(self, ctx):
        """
        The main function for the info command.

        Args:
            ctx: The context of the command.
        """

        load_msg = await stw.slash_send_embed(ctx, await stw.processing_embed(self.client, ctx,
                                                                              title="Crunching the numbers"))

        embed_colour = self.client.colours["generic_blue"]
        cpu_model_filtered = re.sub(r"\(.\)|\(..\)| CPU |@ ....GHz", "", cpuinfo.get_cpu_info()["brand_raw"])
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
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Information", "blueinfo"),
                              description="\u200b", colour=embed_colour)
        embed.add_field(name='Host statistics:', value=f'```yaml\nOS: {re.sub(r"-", " ", platform.platform(aliased=True))} '
                              f'{platform.win32_edition() if platform.system() == "Windows" else ""}\n'
                              f'Working dir: {os.getcwd()}\n'
                              f'Python Version: {platform.python_version()}\n'
                              f'Py-cord Version: {discord.__version__}```\u200b', inline=False)

        embed.add_field(name='CPU:', value=f'```yaml\n{cpu_model_filtered}\n'
                                           f'Usage: {psutil.cpu_percent()}%\n'
                                           f'Freq: {round(cpuinfo.get_cpu_info()["hz_actual"][0] // 1000000000, 2)}GHz\n'
                                           f'Cores: {os.cpu_count()}```\u200b')
        embed.add_field(name='RAM:', value=f'```yaml\nFree: {round(psutil.virtual_memory().free // 1000000000, 1)}GB\n'
                                           f'Used: {round(psutil.virtual_memory().used // 1000000000, 1)}GB\n'
                                           f'Total: {round(psutil.virtual_memory().total // 1000000000, 1)}GB\n'
                                           f'Usage: {psutil.virtual_memory().percent}%```\u200b')
        embed.add_field(name='Disk:', value=f'```yaml\nFree: {round(psutil.disk_usage("/")[2] / 1000000000, 1)}GB\n'
                                            f'Used: {round(psutil.disk_usage("/")[1] / 1000000000, 1)}GB\n'
                                            f'Total: {round(psutil.disk_usage("/")[0] / 1000000000, 1)}GB\n'
                                            f'Usage: {psutil.disk_usage("/")[3]}%```\u200b')

        embed.add_field(name='Bot statistics:', value=f'```yaml\n'
                                                      f'Shard: {shard_name}\n'
                                                      f'Shard Id: {shard_id}\n'
                                                      f'Total Shards: {shards}\n'
                                                      f'Guild Count: {len(self.client.guilds)}```\u200b')

        websocket_ping = '{0}'.format(int(self.client.latency * 100)) + ' ms'
        embed.add_field(name='Latency Information:', value=f'```yaml\nWebsocket: {websocket_ping}\n'
                                                           f'Shard: {shard_ping}\n'
                                                           f'Actual: ...\n'
                                                           f'```\u200b', inline=True)
        eval(bytes.fromhex("656D6265642E6164645F6669656C64286E616D653D274D616465207769746820E29DA4EFB88F2062793A272C2076616C75653D662760606079616D6C5C6E446970707973686572655C6E4A65616E313339385265626F726E5C6E68747470733A2F2F6769746875622E636F6D2F646970707973686572652F7374772D6461696C795C6E7B6261736536342E6236346465636F64652873656C662E636C69656E742E6163636573735B305D292E6465636F646528227574662D3822297D20287B73656C662E636C69656E742E6163636573735B345D7D296060605C7532303062272C20696E6C696E653D46616C736529"))
        embed = await stw.add_requested_footer(ctx, embed)  # there are two of you ? ;o  ;o yay
        embed = await stw.set_thumbnail(self.client, embed, "info")
        await asyncio.sleep(0.25)
        before = time.monotonic()
        msg = await stw.slash_edit_original(ctx, load_msg, embed)
        ping = (time.monotonic() - before) * 1000
        embed.set_field_at(-2, name='Latency Information:', value=f'```yaml\nWebsocket: {websocket_ping}\n'
                                                                  f'Shard: {shard_ping}\n'
                                                                  f'Actual: {int(ping)}ms```\u200b', inline=True)

        await asyncio.sleep(2)
        await stw.slash_edit_original(ctx, msg, embed)

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
                          '8info', 'invfo', 'ijfo', 'into', 'inf', 'tats', 'sats', 'stts', 'stas', 'stat', 'sstats',
                          'sttats', 'staats', 'statts', 'statss', 'tsats', 'satts', 'sttas', 'stast', 'atats', 'wtats',
                          'etats', 'dtats', 'xtats', 'ztats', 'srats', 's5ats', 's6ats', 'syats', 'shats', 'sgats',
                          'sfats', 'stqts', 'stwts', 'ststs', 'stxts', 'stzts', 'stars', 'sta5s', 'sta6s', 'stays',
                          'stahs', 'stags', 'stafs', 'stata', 'statw', 'state', 'statd', 'statx', 'statz', 'astats',
                          'satats', 'wstats', 'swtats', 'estats', 'setats', 'dstats', 'sdtats', 'xstats', 'sxtats',
                          'zstats', 'sztats', 'srtats', 'strats', 's5tats', 'st5ats', 's6tats', 'st6ats', 'sytats',
                          'styats', 'shtats', 'sthats', 'sgtats', 'stgats', 'sftats', 'stfats', 'stqats', 'staqts',
                          'stwats', 'stawts', 'stsats', 'stasts', 'stxats', 'staxts', 'stzats', 'stazts', 'starts',
                          'statrs', 'sta5ts', 'stat5s', 'sta6ts', 'stat6s', 'stayts', 'statys', 'stahts', 'staths',
                          'stagts', 'statgs', 'stafts', 'statfs', 'statas', 'statsa', 'statws', 'statsw', 'states',
                          'statse', 'statds', 'statsd', 'statxs', 'statsx', 'statzs', 'statsz', '/inf', 'infomation',
                          '/info', '/information', 'stats', '/stats'],
                 extras={'emoji': "hard_drive", "args": {}, "dev": False},
                 brief="View information about STW Daily's host, the bot, and the bot's developer. Also verify authenticity.",
                 description="This command will return various bits of information about the bot, which you may find interesting as a developer. It will also verify the authenticity of the bot.")
    async def info(self, ctx):
        """
        This function is the entry point for the info command when called traditionally

        Args:
            ctx: The context of the command
        """
        await self.info_command(ctx)

    @slash_command(name='info',
                   description="View information about STW Daily! Also verify authenticity of the bot.",
                   guild_ids=stw.guild_ids)
    async def slashinfo(self, ctx):
        """
        This function is the entry point for the info command when called via slash command

        Args:
            ctx: The context of the command
        """
        await self.info_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Information(client))

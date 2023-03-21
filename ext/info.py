"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        load_msg = await stw.slash_send_embed(ctx, self.client,
                                              await stw.processing_embed(self.client, ctx, desired_lang,
                                                                         stw.I18n.get(
                                                                             "info.processing.title",
                                                                             desired_lang)))
        shard_ping = shard_name = shard_id = shards = stw.I18n.get("info.entry.notavailable", desired_lang)
        try:
            shards = str(len(self.client.shards))
            shard_id = ctx.guild.shard_id
            shard_name = await stw.retrieve_shard(self.client, shard_id)
            shard_info = self.client.get_shard(shard_id)
            shard_ping = int(shard_info.latency * 100)
            shard_id = str(shard_info.id + 1)
        except:
            pass
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("info.embed.title", desired_lang), "blueinfo"),
            description="\u200b", colour=self.client.colours["generic_blue"])
        embed, websocket_ping = (await asyncio.gather(asyncio.to_thread(self.info_embed, embed, shard_ping, shard_name,
                                                                        shard_id, shards, desired_lang)))[0]
        eval(bytes.fromhex("656D6265642E6164645F6669656C64286E616D653D7374772E4931386E2E6765742822696E666F2E656D6265642E6D6164656279222C20646573697265645F6C616E67292C2076616C75653D662760606079616D6C5C6E446970707973686572655C6E4A65616E313339387265626F726E5C6E68747470733A2F2F6769746875622E636F6D2F646970707973686572652F7374772D6461696C795C6E7B6261736536342E6236346465636F64652873656C662E636C69656E742E6163636573735B305D292E6465636F646528227574662D3822297D20287B73656C662E636C69656E742E6163636573735B355D7D296060605C7532303062272C20696E6C696E653D46616C736529"))
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)  # there are two of you ? ;o  ;o yay
        embed = await stw.set_thumbnail(self.client, embed, "info")
        await asyncio.sleep(0.25)
        before = time.monotonic()
        msg = await stw.slash_edit_original(ctx, load_msg, embed)
        ping = (time.monotonic() - before) * 1000
        embed.set_field_at(-2, name=stw.I18n.get("info.embed.entry.latency", desired_lang),
                           value=f'```yaml\n{stw.I18n.get("info.embed.entry.latency.websocket", desired_lang, f"{websocket_ping:,}")}\n'
                                 f'{stw.I18n.get("info.embed.entry.latency.shard", desired_lang, f"{shard_ping:,}")}\n'
                                 f'{stw.I18n.get("info.embed.entry.latency.actual", desired_lang, f"{int(ping):,}")}```\u200b',
                           inline=True)
        await asyncio.sleep(1.5)
        await stw.slash_edit_original(ctx, msg, embed)

    def info_embed(self, embed, shard_ping, shard_name, shard_id, shards, desired_lang):
        """
        Creates the embed for the info command.

        Args:
            embed: The embed to add the fields to.
            shard_ping: The ping of the shard.
            shard_name: The name of the shard.
            shard_id: The id of the shard.
            shards: The number of shards.
            desired_lang: The desired language.

        Returns:
            The embed for the info command, the shard ping, and the websocket ping.
        """
        cpu_model_filtered = re.sub(r"\(.\)|\(..\)| CPU |@ ....GHz", "", cpuinfo.get_cpu_info()["brand_raw"])

        embed.add_field(name=stw.I18n.get("info.embed.entry.host", desired_lang),
                        value=f'```yaml\n{stw.I18n.get("info.embed.entry.host.os", desired_lang, re.sub(r"-", " ", platform.platform(aliased=True)))} '
                              f'{platform.win32_edition() if platform.system() == "Windows" else ""}\n'
                              f'{stw.I18n.get("info.embed.entry.host.wd", desired_lang, os.getcwd())}\n'
                              f'{stw.I18n.get("info.embed.entry.host.pyv", desired_lang, platform.python_version())}\n'
                              f'{stw.I18n.get("info.embed.entry.host.pycv", desired_lang, discord.__version__)}```\u200b',
                        inline=False)
        embed.add_field(name=stw.I18n.get("info.embed.entry.cpu", desired_lang),
                        value=f'```yaml\n{cpu_model_filtered}\n'
                              f'{stw.I18n.get("info.embed.entry.cpu.usage", desired_lang, psutil.cpu_percent())}\n'
                              f'{stw.I18n.get("info.embed.entry.cpu.freq", desired_lang, round(cpuinfo.get_cpu_info()["hz_actual"][0] // 1000000000, 2))}\n'
                              f'{stw.I18n.get("info.embed.entry.cpu.cores", desired_lang, os.cpu_count())}```\u200b')
        embed.add_field(name=stw.I18n.get("info.embed.entry.ram", desired_lang),
                        value=f'```yaml\n{stw.I18n.get("info.embed.entry.free", desired_lang, round(psutil.virtual_memory().free // 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.used", desired_lang, round(psutil.virtual_memory().used // 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.total", desired_lang, round(psutil.virtual_memory().total // 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.usage", desired_lang, psutil.virtual_memory().percent)}```\u200b')
        embed.add_field(name=stw.I18n.get("info.embed.entry.disk", desired_lang),
                        value=f'```yaml\n{stw.I18n.get("info.embed.entry.free", desired_lang, round(psutil.disk_usage("/")[2] / 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.used", desired_lang, round(psutil.disk_usage("/")[1] / 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.total", desired_lang, round(psutil.disk_usage("/")[0] / 1000000000, 1))}\n'
                              f'{stw.I18n.get("info.embed.entry.usage", desired_lang, psutil.disk_usage("/")[3])}```\u200b')
        embed.add_field(name=stw.I18n.get("info.embed.entry.statistics", desired_lang),
                        value=f'```yaml\n'
                              f'{stw.I18n.get("info.embed.entry.statistics.shard", desired_lang, shard_name)}\n'
                              f'{stw.I18n.get("info.embed.entry.statistics.shard.id", desired_lang, shard_id)}\n'
                              f'{stw.I18n.get("info.embed.entry.statistics.shard.total", desired_lang, shards)}\n'
                              f'{stw.I18n.get("info.embed.entry.statistics.guilds", desired_lang, f"{len(self.client.guilds):,}")}```\u200b')
        websocket_ping = int(self.client.latency * 100)
        embed.add_field(name=stw.I18n.get("info.embed.entry.latency", desired_lang),
                        value=f'```yaml\n{stw.I18n.get("info.embed.entry.latency.websocket", desired_lang, f"{websocket_ping:,}")}\n'
                              f'{stw.I18n.get("info.embed.entry.latency.shard", desired_lang, f"{shard_ping:,}")}\n'
                              f'{stw.I18n.get("info.embed.entry.latency.actual", desired_lang, "...")}```\u200b',
                        inline=True)
        return embed, websocket_ping

    @ext.command(name='info',
                 aliases=['inffo', 'inro', 'infoi', 'infvo', 'infgo', 'inf9', 'nifo', 'infio', 'infko', 'onfo', 'ifno',
                          'inrfo', 'injfo', 'infpo', 'unfo', 'jnfo', 'inbfo', 'infdo', 'incfo', 'indfo', 'infco',
                          'infl', 'iknfo', 'ibfo', 'blinding-lights', 'i9nfo', 'imnfo', 'info9', 'ionfo', 'inflo',
                          'i8nfo', 'intfo', 'inf0o', '8nfo', 'uinfo', 'inco', 'infro', 'iinfo', '9info', 'infol',
                          'information', 'kinfo', 'nfo', 'infop', 'infk', 'innfo', 'infp', 'info0', 'indo', 'inhfo',
                          'ihfo', 'inof', 'ingo', 'inf9o', 'ifo', 'ijnfo', 'linfo', '9nfo', 'infoo', 'lnfo',
                          'inmfo', 'ibnfo', 'infto', 'imfo', 'inf0', 'knfo', 'infi', 'ilnfo', 'oinfo', 'ihnfo',
                          'ingfo', 'iunfo', 'jinfo', 'infok', 'le_bot_stuf', '8info', 'invfo', 'ijfo', 'into', 'inf',
                          'tats', 'sats', 'stts', 'stas', 'stat', 'sstats', 'sttats', 'staats', 'statts', 'statss',
                          'tsats', 'satts', 'sttas', 'stast', 'atats', 'wtats', 'etats', 'dtats', 'xtats', 'ztats',
                          'srats', 's5ats', 's6ats', 'syats', 'shats', 'sgats', 'sfats', 'stqts', 'stwts', 'ststs',
                          'stxts', 'stzts', 'stars', 'sta5s', 'sta6s', 'stays', 'stahs', 'stags', 'stafs', 'stata',
                          'statw', 'state', 'statd', 'statx', 'statz', 'astats', 'satats', 'wstats', 'swtats', 'estats',
                          'setats', 'dstats', 'sdtats', 'xstats', 'sxtats', 'zstats', 'sztats', 'srtats', 'strats',
                          's5tats', 'st5ats', 's6tats', 'st6ats', 'sytats', 'styats', 'shtats', 'sthats', 'sgtats',
                          'stgats', 'sftats', 'stfats', 'stqats', 'staqts', 'stwats', 'stawts', 'stsats', 'stasts',
                          'stxats', 'staxts', 'stzats', 'stazts', 'starts', 'statrs', 'sta5ts', 'stat5s', 'sta6ts',
                          'stat6s', 'stayts', 'statys', 'stahts', 'staths', 'stagts', 'statgs', 'stafts', 'statfs',
                          'statas', 'statsa', 'statws', 'statsw', 'states', 'statse', 'statds', 'statsd', 'statxs',
                          'statsx', 'statzs', 'statsz', '/inf', '/ping', '/info', '/information', 'stats', '/stats',
                          'bout', 'aout', 'abut', 'abot', 'abou', 'aabout', 'abbout', 'aboout', 'abouut', 'aboutt',
                          'baout', 'aobut', 'abuot', 'abotu', 'qbout', 'wbout', 'sbout', 'xbout', 'zbout', 'avout',
                          'agout', 'ahout', 'anout', 'abiut', 'ab9ut', 'ab0ut', 'abput', 'ablut', 'abkut', 'aboyt',
                          'abo7t', 'abo8t', 'aboit', 'abokt', 'abojt', 'aboht', 'abour', 'abou5', 'abou6', 'abouy',
                          'abouh', 'aboug', 'abouf', 'qabout', 'aqbout', 'wabout', 'awbout', 'sabout', 'asbout',
                          'xabout', 'axbout', 'zabout', 'azbout', 'avbout', 'abvout', 'agbout', 'abgout', 'ahbout',
                          'abhout', 'anbout', 'abnout', 'abiout', 'aboiut', 'ab9out', 'abo9ut', 'ab0out', 'abo0ut',
                          'abpout', 'aboput', 'ablout', 'abolut', 'abkout', 'abokut', 'aboyut', 'abouyt', 'abo7ut',
                          'abou7t', 'abo8ut', 'abou8t', 'abouit', 'aboukt', 'abojut', 'aboujt', 'abohut', 'abouht',
                          'abourt', 'aboutr', 'abou5t', 'about5', 'abou6t', 'about6', 'abouty', 'abouth', 'abougt',
                          'aboutg', 'abouft', 'aboutf', 'png', 'pig', 'pin', 'pping', 'piing', 'pinng', 'pingg', 'ipng',
                          'pnig', 'pign', 'oing', '0ing', 'pung', 'p8ng', 'p9ng', 'pong', 'plng', 'pkng',
                          'pjng', 'pibg', 'pihg', 'pijg', 'pimg', 'pinf', 'pint', 'piny', 'pinh', 'pinb',
                          'oping', 'poing', '0ping', 'p0ing', 'lping', 'pling', 'puing', 'piung', 'p8ing', 'pi8ng',
                          'p9ing', 'pi9ng', 'piong', 'pilng', 'pking', 'pikng', 'pjing', 'pijng', 'pibng', 'pinbg',
                          'pihng', 'pinhg', 'pinjg', 'pimng', 'pinmg', 'pinfg', 'pingf', 'pintg', 'pingt', 'pinyg',
                          'pingy', 'pingh', 'pingb', 'pinvg', 'pingv', 'emory', 'mmory', 'meory', 'memry', 'memoy',
                          'memor', 'mmemory', 'meemory', 'memmory', 'memoory', 'memorry', 'memoryy', 'emmory', 'mmeory',
                          'meomry', 'memroy', 'memoyr', 'nemory', 'jemory', 'kemory', 'mwmory', 'm3mory', 'm4mory',
                          'mrmory', 'mfmory', 'mdmory', 'msmory', 'menory', 'mejory', 'mekory', 'memiry', 'mem9ry',
                          'mem0ry', 'mempry', 'memlry', 'memkry', 'memoey', 'memo4y', 'memo5y', 'memoty', 'memogy',
                          'memofy', 'memody', 'memort', 'memor6', 'memor7', 'memoru', 'memorj', 'memorh', 'memorg',
                          'nmemory', 'mnemory', 'jmemory', 'mjemory', 'kmemory', 'mkemory', 'mwemory', 'mewmory',
                          'm3emory', 'me3mory', 'm4emory', 'me4mory', 'mremory', 'mermory', 'mfemory', 'mefmory',
                          'mdemory', 'medmory', 'msemory', 'mesmory', 'menmory', 'memnory', 'mejmory', 'memjory',
                          'mekmory', 'memkory', 'memiory', 'memoiry', 'mem9ory', 'memo9ry', 'mem0ory', 'memo0ry',
                          'mempory', 'memopry', 'memlory', 'memolry', 'memokry', 'memoery', 'memorey', 'memo4ry',
                          'memor4y', 'memo5ry', 'memor5y', 'memotry', 'memorty', 'memogry', 'memorgy', 'memofry',
                          'memorfy', 'memodry', 'memordy', 'memoryt', 'memor6y', 'memory6', 'memor7y', 'memory7',
                          'memoruy', 'memoryu', 'memorjy', 'memoryj', 'memorhy', 'memoryh', 'memoryg', 'atency',
                          'ltency', 'laency', 'latncy', 'latecy', 'lateny', 'latenc', 'llatency', 'laatency',
                          'lattency', 'lateency', 'latenncy', 'latenccy', 'latencyy', 'altency', 'ltaency', 'laetncy',
                          'latnecy', 'latecny', 'latenyc', 'katency', 'oatency', 'patency', 'lqtency', 'lwtency',
                          'lstency', 'lxtency', 'lztency', 'larency', 'la5ency', 'la6ency', 'layency', 'lahency',
                          'lagency', 'lafency', 'latwncy', 'lat3ncy', 'lat4ncy', 'latrncy', 'latfncy', 'latdncy',
                          'latsncy', 'latebcy', 'latehcy', 'latejcy', 'latemcy', 'latenxy', 'latendy', 'latenfy',
                          'latenvy', 'latenct', 'latenc6', 'latenc7', 'latencu', 'latencj', 'latench', 'latencg',
                          'klatency', 'lkatency', 'olatency', 'loatency', 'platency', 'lpatency', 'lqatency',
                          'laqtency', 'lwatency', 'lawtency', 'lsatency', 'lastency', 'lxatency', 'laxtency',
                          'lzatency', 'laztency', 'lartency', 'latrency', 'la5tency', 'lat5ency', 'la6tency',
                          'lat6ency', 'laytency', 'latyency', 'lahtency', 'lathency', 'lagtency', 'latgency',
                          'laftency', 'latfency', 'latwency', 'latewncy', 'lat3ency', 'late3ncy', 'lat4ency',
                          'late4ncy', 'laterncy', 'latefncy', 'latdency', 'latedncy', 'latsency', 'latesncy',
                          'latebncy', 'latenbcy', 'latehncy', 'latenhcy', 'latejncy', 'latenjcy', 'latemncy',
                          'latenmcy', 'latenxcy', 'latencxy', 'latendcy', 'latencdy', 'latenfcy', 'latencfy',
                          'latenvcy', 'latencvy', 'latencty', 'latencyt', 'latenc6y', 'latency6', 'latenc7y',
                          'latency7', 'latencuy', 'latencyu', 'latencjy', 'latencyj', 'latenchy', 'latencyh',
                          'latencgy', 'latencyg', 'nformation', 'iformation', 'inormation', 'infrmation', 'infomation',
                          'inforation', 'informtion', 'informaion', 'informaton', 'informatin', 'informatio',
                          'iinformation', 'innformation', 'infformation', 'infoormation', 'inforrmation',
                          'informmation', 'informaation', 'informattion', 'informatiion', 'informatioon',
                          'informationn', 'niformation', 'ifnormation', 'inofrmation', 'infromation', 'infomration',
                          'inforamtion', 'informtaion', 'informaiton', 'informatoin', 'informatino', 'unformation',
                          '8nformation', '9nformation', 'onformation', 'lnformation', 'knformation', 'jnformation',
                          'ibformation', 'ihformation', 'ijformation', 'imformation', 'indormation', 'inrormation',
                          'intormation', 'ingormation', 'invormation', 'incormation', 'infirmation', 'inf9rmation',
                          'inf0rmation', 'infprmation', 'inflrmation', 'infkrmation', 'infoemation', 'info4mation',
                          'info5mation', 'infotmation', 'infogmation', 'infofmation', 'infodmation', 'infornation',
                          'inforjation', 'inforkation', 'informqtion', 'informwtion', 'informstion', 'informxtion',
                          'informztion', 'informarion', 'informa5ion', 'informa6ion', 'informayion', 'informahion',
                          'informagion', 'informafion', 'informatuon', 'informat8on', 'informat9on', 'informatoon',
                          'informatlon', 'informatkon', 'informatjon', 'informatiin', 'informati9n', 'informati0n',
                          'informatipn', 'informatiln', 'informatikn', 'informatiob', 'informatioh', 'informatioj',
                          'informatiom', 'uinformation', 'iunformation', '8information', 'i8nformation', '9information',
                          'i9nformation', 'oinformation', 'ionformation', 'linformation', 'ilnformation',
                          'kinformation', 'iknformation', 'jinformation', 'ijnformation', 'ibnformation',
                          'inbformation', 'ihnformation', 'inhformation', 'injformation', 'imnformation',
                          'inmformation', 'indformation', 'infdormation', 'inrformation', 'infrormation',
                          'intformation', 'inftormation', 'ingformation', 'infgormation', 'invformation',
                          'infvormation', 'incformation', 'infcormation', 'infiormation', 'infoirmation',
                          'inf9ormation', 'info9rmation', 'inf0ormation', 'info0rmation', 'infpormation',
                          'infoprmation', 'inflormation', 'infolrmation', 'infkormation', 'infokrmation',
                          'infoermation', 'inforemation', 'info4rmation', 'infor4mation', 'info5rmation',
                          'infor5mation', 'infotrmation', 'infortmation', 'infogrmation', 'inforgmation',
                          'infofrmation', 'inforfmation', 'infodrmation', 'infordmation', 'infornmation',
                          'informnation', 'inforjmation', 'informjation', 'inforkmation', 'informkation',
                          'informqation', 'informaqtion', 'informwation', 'informawtion', 'informsation',
                          'informastion', 'informxation', 'informaxtion', 'informzation', 'informaztion',
                          'informartion', 'informatrion', 'informa5tion', 'informat5ion', 'informa6tion',
                          'informat6ion', 'informaytion', 'informatyion', 'informahtion', 'informathion',
                          'informagtion', 'informatgion', 'informaftion', 'informatfion', 'informatuion',
                          'informatiuon', 'informat8ion', 'informati8on', 'informat9ion', 'informati9on',
                          'informatoion', 'informatlion', 'informatilon', 'informatkion', 'informatikon',
                          'informatjion', 'informatijon', 'informatioin', 'informatio9n', 'informati0on',
                          'informatio0n', 'informatipon', 'informatiopn', 'informatioln', 'informatiokn',
                          'informatiobn', 'informationb', 'informatiohn', 'informationh', 'informatiojn',
                          'informationj', 'informatiomn', 'informationm', 'tatistics', 'satistics', 'sttistics',
                          'staistics', 'statstics', 'statitics', 'statisics', 'statistcs', 'statistis', 'statistic',
                          'sstatistics', 'sttatistics', 'staatistics', 'stattistics', 'statiistics', 'statisstics',
                          'statisttics', 'statistiics', 'statisticcs', 'statisticss', 'tsatistics', 'sattistics',
                          'sttaistics', 'staitstics', 'statsitics', 'statitsics', 'statisitcs', 'statistcis',
                          'statistisc', 'atatistics', 'wtatistics', 'etatistics', 'dtatistics', 'xtatistics',
                          'ztatistics', 'sratistics', 's5atistics', 's6atistics', 'syatistics', 'shatistics',
                          'sgatistics', 'sfatistics', 'stqtistics', 'stwtistics', 'ststistics', 'stxtistics',
                          'stztistics', 'staristics', 'sta5istics', 'sta6istics', 'stayistics', 'stahistics',
                          'stagistics', 'stafistics', 'statustics', 'stat8stics', 'stat9stics', 'statostics',
                          'statlstics', 'statkstics', 'statjstics', 'statiatics', 'statiwtics', 'statietics',
                          'statidtics', 'statixtics', 'statiztics', 'statisrics', 'statis5ics', 'statis6ics',
                          'statisyics', 'statishics', 'statisgics', 'statisfics', 'statistucs', 'statist8cs',
                          'statist9cs', 'statistocs', 'statistlcs', 'statistkcs', 'statistjcs', 'statistixs',
                          'statistids', 'statistifs', 'statistivs', 'statistica', 'statisticw', 'statistice',
                          'statisticd', 'statisticx', 'statisticz', 'astatistics', 'satatistics', 'wstatistics',
                          'swtatistics', 'estatistics', 'setatistics', 'dstatistics', 'sdtatistics', 'xstatistics',
                          'sxtatistics', 'zstatistics', 'sztatistics', 'srtatistics', 'stratistics', 's5tatistics',
                          'st5atistics', 's6tatistics', 'st6atistics', 'sytatistics', 'styatistics', 'shtatistics',
                          'sthatistics', 'sgtatistics', 'stgatistics', 'sftatistics', 'stfatistics', 'stqatistics',
                          'staqtistics', 'stwatistics', 'stawtistics', 'stsatistics', 'stastistics', 'stxatistics',
                          'staxtistics', 'stzatistics', 'staztistics', 'startistics', 'statristics', 'sta5tistics',
                          'stat5istics', 'sta6tistics', 'stat6istics', 'staytistics', 'statyistics', 'stahtistics',
                          'stathistics', 'stagtistics', 'statgistics', 'staftistics', 'statfistics', 'statuistics',
                          'statiustics', 'stat8istics', 'stati8stics', 'stat9istics', 'stati9stics', 'statoistics',
                          'statiostics', 'statlistics', 'statilstics', 'statkistics', 'statikstics', 'statjistics',
                          'statijstics', 'statiastics', 'statisatics', 'statiwstics', 'statiswtics', 'statiestics',
                          'statisetics', 'statidstics', 'statisdtics', 'statixstics', 'statisxtics', 'statizstics',
                          'statisztics', 'statisrtics', 'statistrics', 'statis5tics', 'statist5ics', 'statis6tics',
                          'statist6ics', 'statisytics', 'statistyics', 'statishtics', 'statisthics', 'statisgtics',
                          'statistgics', 'statisftics', 'statistfics', 'statistuics', 'statistiucs', 'statist8ics',
                          'statisti8cs', 'statist9ics', 'statisti9cs', 'statistoics', 'statistiocs', 'statistlics',
                          'statistilcs', 'statistkics', 'statistikcs', 'statistjics', 'statistijcs', 'statistixcs',
                          'statisticxs', 'statistidcs', 'statisticds', 'statistifcs', 'statisticfs', 'statistivcs',
                          'statisticvs', 'statisticas', 'statisticsa', 'statisticws', 'statisticsw', 'statistices',
                          'statisticse', 'statisticsd', 'statisticsx', 'statisticzs', 'statisticsz', '/statistics',
                          '/latency', '/about', '/memory', 'uptime', 'getmtime', 'inligting', 'المعلومات', 'информация',
                          'তথ্য', 'informació', 'πληροφορίες', 'información', 'اطلاعات', 'tiedot', 'માહિતી', 'bayani',
                          'מידע', 'जानकारी', '情報', '정보', 'informacija', 'माहिती', 'maklumat', 'ਜਾਣਕਾਰੀ', 'инфо',
                          'habari', 'தகவல்', 'సమాచారం', 'ข้อมูล', 'bilgi', 'інформація', 'معلومات', 'thông tin', '信息',
                          'thôngtin', 'thông', 'infom', 'nnfo', 'idfo', 'infqo', 'isnfo', 'inmo', 'inqo', 'injo',
                          'iafo', 'ipnfo', 'inko', 'ianfo', 'ipfo', 'ignfo', 'inoo', 'ainfo', 'inwfo', 'wnfo', 'infy',
                          'ixfo', 'irfo', 'finfo', 'iufo', 'infjo', 'infzo', 'zinfo', 'infod', 'iffo', 'inbo', 'minfo',
                          'inft', 'inio', 'infou', 'icnfo', 'infho', 'ikfo', 'infxo', 'infc', 'infow', 'infno',
                          'infe', 'infr', 'inufo', 'cnfo', 'sinfo', 'infof', 'ivfo', 'ginfo', 'infor', 'infog', 'inofo',
                          'cinfo', 'inzo', 'inefo', 'ivnfo', 'inuo', 'inyo', 'inso', 'rnfo', 'ynfo', 'infob', 'infoa',
                          'infoy', 'infu', 'vinfo', 'iwnfo', 'infa', 'infg', 'infoc', 'inyfo', 'iefo', 'infoe', 'infso',
                          'pinfo', 'infuo', 'znfo', 'iqfo', 'enfo', 'inlfo', 'anfo', 'inwo', 'inao', 'infon', 'dnfo',
                          'infj', 'inzfo', 'hnfo', 'inqfo', 'iifo', 'hinfo', 'snfo', 'infot', 'infox', 'infmo', 'xinfo',
                          'infao', 'infd', 'ninfo', 'ienfo', 'insfo', 'inxfo', 'infx', 'infos', 'pnfo', 'inifo', 'gnfo',
                          'tnfo', 'qinfo', 'iwfo', 'dinfo', 'inho', 'infb', 'infs', 'qnfo', 'idnfo', 'iqnfo', 'infeo',
                          'infoj', 'infq', 'infw', 'infyo', 'izfo', 'inlo', 'infm', 'ixnfo', 'inff', 'infoq', 'isfo',
                          'inno', 'mnfo', 'inpfo', 'infwo', 'ilfo', 'einfo', 'infov', 'yinfo', 'inpo', 'iofo', 'itfo',
                          'iyfo', 'bnfo', 'vnfo', 'inkfo', 'inafo', 'igfo', 'infbo', 'infoz', 'rinfo', 'inxo', 'infh',
                          'infoh', 'tinfo', 'irnfo', 'binfo', 'infz', 'fnfo', 'itnfo', 'iynfo', 'ineo', 'infn', 'icfo',
                          'ifnfo', 'iznfo', 'xnfo', 'winfo', '7nfo', '&nfo', '*nfo', '(nfo', 'i,fo', 'i<fo', 'inf8',
                          'inf;', 'inf*', 'inf(', 'inf)', 'stacts', 'rstats', 'stpts', 'statl', 'stuts', 'stgts',
                          'statc', 'sjats', 'staxs', 'stits', 'ptats', 'sotats', 'sptats', 'styts', 'staps', 'stamts',
                          'stajts', 'stkts', 'statsl', 'stazs', 'stants', 'kstats', 'sctats', 'sthts', 'stacs', 'statb',
                          'fstats', 'qtats', 'stfts', 'statso', 'stads', 'stalts', 'staos', 'staws', 'utats', 'rtats',
                          'staks', 'ltats', 'sntats', 'ctats', 'statsr', 'statps', 'statst', 'hstats', 'statns',
                          'stcats', 'stots', 'statsk', 'statr', 'statvs', 'statsi', 'statsp', 'stjts', 'otats', 'sxats',
                          'statks', 'suats', 'stbts', 'ssats', 'stans', 'cstats', 'swats', 'svtats', 'ktats', 'stavs',
                          'staas', 'btats', 'stapts', 'status', 'statv', 'itats', 'skats', 'stets', 'istats', 'statsg',
                          'stcts', 'spats', 'stlts', 'lstats', 'stkats', 'sltats', 'pstats', 'stadts', 'stvats',
                          'stajs', 'statg', 'stass', 'staes', 'siats', 'tstats', 'strts', 'scats', 'seats',
                          'stams', 'statsc', 'statsj', 'sttts', 'stais', 'staots', 'nstats', 'svats', 'szats', 'statsn',
                          'sdats', 'staets', 'stabs', 'saats', 'jtats', 'stlats', 'vtats', 'ntats', 'mtats', 'statqs',
                          'htats', 'statt', 'stabts', 'stals', 'statsh', 'slats', 'stdts', 'ftats', 'statf', 'sitats',
                          'statm', 'stmts', 'sqtats', 'gstats', 'stuats', 'stath', 'statu', 'ttats', 'statbs', 'stati',
                          'sutats', 'sbtats', 'gtats', 'stbats', 'stnats', 'staits', 'statn', 'staty', 'statk', 'sqats',
                          'steats', 'qstats', 'vstats', 'smats', 'statsm', 'soats', 'sjtats', 'stvts', 'stato',
                          'stakts', 'stjats', 'statsu', 'snats', 'ostats', 'statq', 'statp', 'statsq', 'staus', 'statj',
                          'smtats', 'statsy', 'stoats', 'jstats', 'statsb', 'stdats', 'statis', 'statjs', 'sktats',
                          'stavts', 'mstats', 'statls', 'ystats', 'stiats', 'ustats', 'stmats', 'sbats', 'stauts',
                          'statsf', 'statcs', 'ytats', 'bstats', 'statos', 'statsv', 'staqs', 'stpats', 'statms',
                          's4ats', 's$ats', 's%ats', 's^ats', 'sta4s', 'sta$s', 'sta%s', 'sta^s', 'zmemory', 'memovy',
                          'memorp', 'mehory', 'memcory', 'ymemory', 'membory', 'memorx', 'memhry', 'memyry', 'memorky',
                          'muemory', 'memorc', 'memvry', 'memoryo', 'memors', 'vemory', 'memoryz', 'memorly', 'memorcy',
                          'memwry', 'memory', 'memouy', 'meomory', 'memsory', 'xmemory', 'mxemory', 'memdory',
                          'memoryb', 'bemory', 'mcmory', 'eemory', 'mecmory', 'mzmory', 'memoky', 'memhory', 'momory',
                          'memzory', 'mlmory', 'vmemory', 'meymory', 'memoqry', 'mimory', 'mecory', 'hemory', 'memoryi',
                          'megory', 'memtory', 'tmemory', 'meqmory', 'meiory', 'memoriy', 'memosry', 'mehmory',
                          'memozry', 'memoly', 'mgemory', 'memorf', 'membry', 'memary', 'memora', 'memoroy', 'oemory',
                          'memvory', 'mezory', 'uemory', 'cmemory', 'mkmory', 'mymory', 'meyory', 'memoxry', 'mebmory',
                          'memorya', 'memobry', 'meuory', 'wmemory', 'omemory', 'yemory', 'mtemory', 'memorym',
                          'memtry', 'memorby', 'mpmory', 'memoryp', 'memopy', 'mexmory', 'mpemory', 'mamory', 'memojry',
                          'merory', 'memoryf', 'metmory', 'memoqy', 'memoryx', 'qmemory', 'qemory', 'melmory', 'memorm',
                          'pmemory', 'mevory', 'mtmory', 'pemory', 'memoiy', 'memaory', 'memorzy', 'mqmory', 'memorz',
                          'memosy', 'memgory', 'memoyy', 'mvmory', 'memorsy', 'melory', 'temory', 'memorr', 'smemory',
                          'mebory', 'memore', 'mvemory', 'meqory', 'mumory', 'mmmory', 'memoryl', 'memorwy', 'mepory',
                          'memoro', 'memxry', 'memormy', 'memoary', 'mezmory', 'memozy', 'memoryd', 'megmory',
                          'moemory', 'amemory', 'mlemory', 'memocy', 'memoray', 'dmemory', 'mxmory', 'memoxy', 'memjry',
                          'ememory', 'aemory', 'mgmory', 'iemory', 'umemory', 'meaory', 'medory', 'memoryc', 'memowy',
                          'fmemory', 'cemory', 'memovry', 'memdry', 'memorye', 'memcry', 'xemory', 'memoay', 'lmemory',
                          'memxory', 'semory', 'memorxy', 'mcemory', 'memrory', 'memori', 'mhemory', 'memury', 'mesory',
                          'memoryw', 'memfry', 'mefory', 'memsry', 'memorny', 'metory', 'memomy', 'memqory', 'memyory',
                          'memoby', 'gemory', 'memwory', 'imemory', 'mexory', 'miemory', 'memohry', 'memorl', 'memorb',
                          'demory', 'memony', 'memorq', 'memgry', 'memoryr', 'memfory', 'memuory', 'mbmory', 'zemory',
                          'hmemory', 'wemory', 'memqry', 'memorys', 'memord', 'memooy', 'memoyry', 'mqemory', 'mhmory',
                          'mepmory', 'memohy', 'memmry', 'memery', 'memorpy', 'memoury', 'mbemory', 'memeory',
                          'meimory', 'memrry', 'mjmory', 'lemory', 'mzemory', 'myemory', 'memorqy', 'memnry', 'mevmory',
                          'memomry', 'memorn', 'remory', 'memoryq', 'mnmory', 'memocry', 'memorv', 'memoryn', 'meeory',
                          'memork', 'memowry', 'memorvy', 'memoryv', 'mewory', 'meamory', 'bmemory', 'memonry',
                          'memojy', 'memoryk', 'maemory', 'rmemory', 'memzry', 'femory', 'meoory', 'meumory', 'memorw',
                          'gmemory', ',emory', '<emory', 'm2mory', 'm$mory', 'm#mory', 'm@mory', 'me,ory', 'me<ory',
                          'mem8ry', 'mem;ry', 'mem*ry', 'mem(ry', 'mem)ry', 'memo3y', 'memo#y', 'memo$y', 'memo%y',
                          'memor5', 'memor%', 'memor^', 'memor&', 'radm', 'rxm', 'arm', 'rnm', 'aam', 'rma', 'kram',
                          'rm', 'rvm', 'ra', 'dam', 'rac', 'rau', 'oam', 'rom', 'rjam', 'iram',
                          'tam', 'rat', 'ruam', 'raw', 'racm', 'qam', 'qram', 'lram', 'rai', 'raj', 'rmam', 'am',
                          'raum', 'ramb', 'rdam', 'ratm', 'ramn', 'rsm', 'rkm', 'rav', 'raam',
                          'rrm', 'rkam', 'rax', 'oram', 'rjm', 'ram', 'rarm', 'rhm', 'rmm', 'rpm', 'dram', 'bram',
                          'ramx', 'lam', 'ramu', 'raf', 'rami', 'cam', 'gram', 'ramm', 'raq', 'raa', 'rxam', 'raz',
                          'ramj', 'rcam', 'rama', 'rap', 'rawm', 'ramy', 'ramr', 'ream', 'ramh', 'cram', 'xam', 'rapm',
                          'vram', 'razm', 'jam', 'rgm', 'eam', 'rah', 'raom', 'raxm', 'rym', 'hram', 'rao',
                          'zam', 'rfm', 'rabm', 'kam', 'ramd', 'ran', 'rqm', 'yam', 'raym', 'rcm', 'gam', 'ral',
                          'rlam', 'rdm', 'rad', 'rasm', 'ramz', 'rag', 'raml', 'uram', 'rame', 'sam', 'rzm', 'rwm',
                          'rpam', 'rahm', 'aram', 'rbam', 'pam', 'fram', 'uam', 'bam', 'fam', 'ramo', 'rar', 'vam',
                          'nam', 'rakm', 'rajm', 'rqam', 'raim', 'sram', 'mram', 'ham', 'ragm', 'rwam', 'rram',
                          'ramv', 'ramw', 'rim', 'raqm', 'ramt', 'ralm', 'ramp', 'jram', 'zram', 'wram', 'rvam', 'ramg',
                          'rnam', 'nram', 'rzam', 'mam', 'ramq', 'wam', 'rem', 'rbm', 'rlm', 'rfam', 'rtam', 'rams',
                          'ravm', 'roam', 'raem', 'rsam', 'yram', 'riam', 'rham', 'ryam', 'rae', 'rab', 'ramc', 'ramf',
                          'eram', 'pram', 'rgam', 'tram', 'rafm', '3am', '4am', '5am', '#am', '$am', '%am', 'ra,',
                          'ra<', 'ajbout', 'dbout', 'habout', 'awout', 'abobt', 'oabout', 'aboutq', 'about', 'aboui',
                          'aboaut', 'abaut', 'aborut', 'abqout', 'abobut', 'abouq', 'abouvt', 'lbout', 'cabout',
                          'aboue', 'abyout', 'abosut', 'abouk', 'abouat', 'babout', 'aboup', 'abmut', 'abtut', 'ybout',
                          'aboxt', 'aboua', 'aboft', 'kbout', 'vbout', 'ambout', 'abouj', 'aboutl', 'ubout', 'afout',
                          'abouz', 'aboutp', 'axout', 'abjut', 'labout', 'aboqt', 'aboct', 'abwout', 'bbout', 'abdout',
                          'abouc', 'abort', 'aboat', 'abouot', 'abocut', 'abott', 'obout', 'abouv', 'rabout', 'abhut',
                          'abxut', 'atbout', 'vabout', 'abouct', 'abqut', 'absout', 'abofut', 'atout', 'ayout', 'abyut',
                          'acout', 'abcut', 'aboux', 'abouqt', 'dabout', 'aboutc', 'aboun', 'abgut', 'abeout', 'abfout',
                          'abuout', 'amout', 'albout', 'abouti', 'abous', 'ebout', 'abouwt', 'ibout', 'aboot', 'aboeut',
                          'abonut', 'aqout', 'azout', 'aybout', 'aeout', 'mbout', 'fabout', 'pbout', 'aboqut', 'aboutu',
                          'abogt', 'aboutk', 'arbout', 'abjout', 'rbout', 'abzut', 'fbout', 'abdut', 'gbout', 'apout',
                          'jbout', 'abrout', 'aboult', 'abouto', 'asout', 'adbout', 'abouu', 'abbut', 'gabout',
                          'abaout', 'abount', 'abvut', 'aibout', 'abouet', 'tabout', 'aboutb', 'eabout', 'abotut',
                          'aboutj', 'aboumt', 'jabout', 'acbout', 'abozt', 'aboudt', 'abouta', 'akout', 'abwut',
                          'aobout', 'aboum', 'abont', 'aboul', 'abcout', 'abodt', 'abxout', 'aiout', 'abovt', 'aboust',
                          'aebout', 'aboutx', 'abomut', 'cbout', 'abtout', 'arout', 'aboute', 'nabout', 'abmout',
                          'iabout', 'uabout', 'pabout', 'abeut', 'tbout', 'aboutv', 'aboutz', 'abost', 'abzout',
                          'aboutw', 'yabout', 'mabout', 'abouzt', 'abomt', 'abopt', 'abuut', 'abolt', 'aboxut', 'hbout',
                          'abouw', 'abogut', 'nbout', 'abovut', 'adout', 'aboud', 'aboub', 'abouts', 'abodut', 'aboutm',
                          'abrut', 'abfut', 'aboupt', 'ajout', 'abozut', 'kabout', 'aboutd', 'aboubt', 'aboet', 'auout',
                          'absut', 'apbout', 'abouxt', 'aboutn', 'akbout', 'aoout', 'aaout', 'abowut', 'alout', 'abowt',
                          'aubout', 'abouo', 'afbout', 'abnut', 'ab8ut', 'ab;ut', 'ab*ut', 'ab(ut', 'ab)ut', 'abo6t',
                          'abo^t', 'abo&t', 'abo*t', 'abou4', 'abou$', 'abou%', 'abou^', 'aping', 'piag', 'pcng',
                          'pinga', 'pbng', 'qing', 'pinr', 'piang', 'hing', 'piig', 'wing', 'pwing', 'ving', 'pingo',
                          'pmng', 'pning', 'pisg', 'ppng', 'piyg', 'pzng', 'pigng', 'jing', 'pming', 'pdng',
                          'pina', 'uing', 'pingm', 'pixng', 'pingz', 'pingc', 'pizg', 'picg', 'fping', 'pting', 'pidng',
                          'pzing', 'pingx', 'rping', 'pging', 'pine', 'nping', 'ping', 'pifng', 'pirg', 'pying',
                          'sping', 'aing', 'eping', 'cing', 'pinq', 'psng', 'pixg', 'pinx', 'pinxg', 'pding',
                          'pins', 'pinge', 'qping', 'pinz', 'yping', 'pifg', 'pinw', 'ding', 'ring', 'piqg', 'zping',
                          'pinig', 'bing', 'pingq', 'pind', 'pang', 'zing', 'peng', 'fing', 'pingk', 'pinqg', 'ging',
                          'pipg', 'pinu', 'pisng', 'phing', 'pieg', 'iing', 'ning', 'pingp', 'pini', 'pinm', 'hping',
                          'eing', 'pirng', 'uping', 'pinsg', 'piyng', 'pqing', 'pinpg', 'pivg', 'pqng', 'pbing', 'pwng',
                          'pingj', 'pingl', 'piog', 'pgng', 'pingn', 'mping', 'pikg', 'ptng', 'wping', 'pinn', 'pyng',
                          'pfng', 'pindg', 'gping', 'pieng', 'jping', 'pinzg', 'picng', 'pinag', 'pizng', 'pfing',
                          'pving', 'piqng', 'pingr', 'pipng', 'iping', 'kping', 'piwng', 'pidg', 'pring', 'ming',
                          'paing', 'pcing', 'pinug', 'ying', 'ting', 'pincg', 'king', 'pinog', 'phng', 'dping', 'pxng',
                          'pinj', 'pnng', 'pinc', 'piwg', 'pinp', 'psing', 'pinkg', 'pino', 'pinl', 'pineg', 'pingu',
                          'pitng', 'pigg', 'cping', 'sing', 'prng', 'xping', 'pilg', 'pingi', 'pxing', 'pingw', 'xing',
                          'pvng', 'pingd', 'pivng', 'pinrg', 'peing', 'pitg', 'bping', 'pinlg', 'tping', 'pinwg',
                          'vping', 'piug', 'pings', '9ing', '-ing', '[ing', ']ing', ';ing', '(ing', ')ing', '_ing',
                          '=ing', '+ing', '{ing', '}ing', ':ing', 'p7ng', 'p&ng', 'p*ng', 'p(ng', 'pi,g', 'pi<g',
                          'icformation', 'inforhation', 'infoqrmation', 'informatpon', 'inyformation', 'inforbmation',
                          'informatiqn', 'inqormation', 'informatmon', 'inuformation', 'informatimn', 'informatioun',
                          'infxrmation', 'informatifon', 'infomrmation', 'vnformation', 'infgrmation', 'infurmation',
                          'informatinon', 'informationa', 'infommation', 'inaormation', 'infosmation', 'informatiaon',
                          'infocrmation', 'informatiok', 'inforhmation', 'ivnformation', 'informatiot', 'infopmation',
                          'informatiyon', 'informution', 'informatiof', 'ifformation', 'xinformation', 'infcrmation',
                          'informatton', 'inforpation', 'inforeation', 'sinformation', 'inforration', 'infoomation',
                          'ifnformation', 'informatidn', 'informatiwn', 'idformation', 'inforqmation', 'hinformation',
                          'informhation', 'informpation', 'informatiotn', 'inforcation', 'informamion', 'informiation',
                          'informationz', 'yinformation', 'inforzmation', 'informatifn', 'informaption', 'informaeion',
                          'iaformation', 'informjtion', 'infobmation', 'informationt', 'informatiod', 'infjormation',
                          'informrtion', 'informauion', 'inforaation', 'informatiown', 'inforxmation', 'informfation',
                          'informatieon', 'infoimation', 'informatidon', 'iiformation', 'infoarmation', 'informaaion',
                          'informatiofn', 'informatsion', 'informalion', 'inforuation', 'informatiton', 'informaiion',
                          'inforfation', 'zinformation', 'informytion', 'informbtion', 'informatiyn', 'informatibon',
                          'informatiol', 'informatign', 'informationp', 'inforwmation', 'informatirn', 'informftion',
                          'informationy', 'informatioyn', 'informaktion', 'finformation', 'informatqon', 'infokmation',
                          'informntion', 'inoormation', 'inforvation', 'informatfon', 'inforlation', 'informatbion',
                          'infjrmation', 'ixformation', 'infeormation', 'infyrmation', 'informantion', 'informatiodn',
                          'inkormation', 'informatibn', 'infohrmation', 'iyformation', 'informanion', 'informgtion',
                          'inmormation', 'ninformation', 'informatnion', 'informamtion', 'infobrmation', 'infsormation',
                          'informatxon', 'iwformation', 'ainformation', 'informration', 'informition', 'isnformation',
                          'informadion', 'inforymation', 'qinformation', 'inlformation', 'inwormation', 'infuormation',
                          'informaxion', 'informmtion', 'wnformation', 'informatdon', 'informeation', 'informatihon',
                          'inwformation', 'informatioc', 'insformation', 'informhtion', 'informaltion', 'infoyrmation',
                          'informatzion', 'informadtion', 'inzormation', 'inbormation', 'infolmation', 'infourmation',
                          'inforgation', 'gnformation', 'informgation', 'infoumation', 'informlation', 'informationx',
                          'informatios', 'informaution', 'informoation', 'informationd', 'infozrmation', 'infzrmation',
                          'ilformation', 'informatpion', 'inforcmation', 'iynformation', 'infojrmation', 'informatwion',
                          'inforyation', 'minformation', 'informatiosn', 'informetion', 'xnformation', 'informatvon',
                          'informcation', 'inoformation', 'infoqmation', 'informktion', 'informavtion', 'irnformation',
                          'infohmation', 'infhormation', 'informaoion', 'informatitn', 'informationu', 'infortation',
                          'inforsmation', 'informatiop', 'infoymation', 'informaticon', 'inxformation', 'informttion',
                          'informativn', 'insormation', 'informatyon', 'ieformation', 'inlormation', 'informationi',
                          'informationr', 'informationo', 'informatson', 'infarmation', 'idnformation', 'mnformation',
                          'informatiqon', 'inpformation', 'infocmation', 'informatiocn', 'izformation', 'fnformation',
                          'icnformation', 'iznformation', 'inforomation', 'iqformation', 'infzormation', 'infdrmation',
                          'informajion', 'winformation', 'nnformation', 'infovrmation', 'informationl', 'inpormation',
                          'inforsation', 'anformation', 'ixnformation', 'inforqation', 'informatixn', 'informataon',
                          'informakion', 'informatiox', 'inforoation', 'inkformation', 'informatioxn', 'inforpmation',
                          'informatiou', 'informyation', 'infordation', 'informatbon', 'informatiow', 'informaetion',
                          'ipnformation', 'informations', 'infoamation', 'iniormation', 'infhrmation', 'informatioen',
                          'infmrmation', 'informatiov', 'informatior', 'informatiron', 'infrrmation', 'snformation',
                          'informatqion', 'informathon', 'inforxation', 'informatizn', 'infaormation', 'informationq',
                          'infqormation', 'irformation', 'ienformation', 'inftrmation', 'qnformation', 'pinformation',
                          'einformation', 'enformation', 'informatxion', 'infbormation', 'informatijn', 'informawion',
                          'informatiwon', 'inxormation', 'infozmation', 'informaqion', 'informatnon', 'ynformation',
                          'informption', 'informatzon', 'informatioz', 'cnformation', 'informatioq', 'informatron',
                          'informatimon', 'informatioi', 'informataion', 'hnformation', 'infwormation', 'informotion',
                          'informatioa', 'inforbation', 'inyormation', 'informativon', 'informatcon', 'igformation',
                          'itformation', 'inforumation', 'infsrmation', 'informatiog', 'infoxmation', 'informuation',
                          'inuormation', 'ikformation', 'informateon', 'informationk', 'informapion', 'infonrmation',
                          'rnformation', 'informavion', 'informatioy', 'informasion', 'bnformation', 'binformation',
                          'informateion', 'infnrmation', 'isformation', 'infonmation', 'vinformation', 'informatien',
                          'dinformation', 'informltion', 'informazion', 'informabtion', 'iuformation', 'inqformation',
                          'znformation', 'infosrmation', 'informatgon', 'ignformation', 'itnformation', 'inforimation',
                          'informationc', 'infbrmation', 'informction', 'ioformation', 'infoxrmation', 'dnformation',
                          'tinformation', 'infqrmation', 'informatizon', 'informajtion', 'infovmation', 'informationv',
                          'inforamation', 'ivformation', 'informatiun', 'ginformation', 'informatioo', 'informationf',
                          'inforvmation', 'informatigon', 'informabion', 'informtation', 'inforlmation', 'inforwation',
                          'iniformation', 'informationg', 'infyormation', 'infwrmation', 'informatioe', 'inforiation',
                          'iwnformation', 'informatwon', 'infvrmation', 'informatiogn', 'informatioqn', 'ianformation',
                          'informdtion', 'tnformation', 'informbation', 'inaformation', 'ipformation', 'informatvion',
                          'infowmation', 'injormation', 'infnormation', 'informatioan', 'infmormation', 'ineormation',
                          'informatdion', 'informatinn', 'informatiovn', 'informaotion', 'pnformation', 'informatison',
                          'informatihn', 'infojmation', 'inffrmation', 'cinformation', 'informaticn', 'informationw',
                          'informatione', 'iqnformation', 'informvation', 'informdation', 'infermation', 'informatian',
                          'informatisn', 'informatixon', 'inhormation', 'rinformation', 'inforzation', 'inzformation',
                          'informaition', 'ineformation', 'informacion', 'informaction', 'informatcion', 'informatiorn',
                          'innormation', 'informatmion', 'informatiozn', 'informvtion', 'infowrmation', 'infxormation',
                          '7nformation', '&nformation', '*nformation', '(nformation', 'i,formation', 'i<formation',
                          'inf8rmation', 'inf;rmation', 'inf*rmation', 'inf(rmation', 'inf)rmation', 'info3mation',
                          'info#mation', 'info$mation', 'info%mation', 'infor,ation', 'infor<ation', 'informa4ion',
                          'informa$ion', 'informa%ion', 'informa^ion', 'informat7on', 'informat&on', 'informat*on',
                          'informat(on', 'informati8n', 'informati;n', 'informati*n', 'informati(n', 'informati)n',
                          'informatio,', 'informatio<', 'verfiy', 'jverify', 'verifd', 'verifyd', 'vrify', 'aerify',
                          'vprify', 'veriy', 'veriyf', 'vervfy', 'verifym', 'sverify', 'terify', 'veridy', 'veirfy',
                          'eerify', 'verpfy', 'evrify', 'verif', 'vericy', 'vrrify', 'vreify', 'verifj', 'vcrify',
                          'verify', 'verefy', 'verifyr', 'veriyy', 'velrify', 'vergify', 'vebify', 'verfy', 'veorify',
                          'perify', 'verifvy', 'verifzy', 'erify', 'kverify', 'veify', 'verifye', 'verifhy', 'vzerify',
                          'vedify', 'rverify', 'verimy', 'verifyz', 'verifa', 'serify', 'fverify', 'vermify', 'verifyv',
                          'vkerify', 'verxify', 'vuerify', 'voerify', 'verifg', 'verikfy', 'iverify', 'verifry',
                          'vierify', 'verifyw', 'vyerify', 'ierify', 'vyrify', 'verifb', 'vercify', 'verifwy',
                          'verifyy', 'vverify', 'vezrify', 'verwfy', 'verifyj', 'verifyx', 'verifdy', 'vergfy',
                          'veridfy', 'verifi', 'verifv', 'vesrify', 'veriqfy', 'vernfy', 'nerify', 'verigfy', 'verijy',
                          'ferify', 'verifny', 'verifyu', 'werify', 'verifyq', 'kerify', 'veriefy', 'vevify', 'vetrify',
                          'veriafy', 'veruify', 'verxfy', 'verifiy', 'vdrify', 'vaerify', 'verqfy', 'verimfy', 'verifh',
                          'verlify', 'vfrify', 'verivy', 'vderify', 'hverify', 'veritfy', 'vserify', 'verdify',
                          'veriwfy', 'cerify', 'vgerify', 'veriqy', 'veroify', 'verjify', 'verifyl', 'verrify',
                          'vetify', 'verizy', 'verbfy', 'verifty', 'zerify', 'veryify', 'lerify', 'vwrify', 'verifay',
                          'verinfy', 'veyify', 'verifyf', 'verzify', 'verioy', 'veriify', 'verifo', 'veaify', 'vnerify',
                          'veripy', 'veriuy', 'vorify', 'vgrify', 'verifcy', 'vlerify', 'vemrify', 'vhrify', 'verifq',
                          'verbify', 'verifly', 'verihfy', 'vegify', 'herify', 'dverify', 'vqrify', 'jerify', 'everify',
                          'vperify', 'vjrify', 'veiify', 'vertify', 'veriky', 'virify', 'berify', 'oerify', 'vezify',
                          'vmrify', 'veoify', 'averify', 'nverify', 'varify', 'vermfy', 'verifuy', 'verifys', 'verifx',
                          'vercfy', 'veurify', 'vcerify', 'veriwy', 'verkfy', 'gverify', 'vereify', 'verifu', 'vejify',
                          'vevrify', 'veriffy', 'uerify', 'merify', 'vkrify', 'vberify', 'vwerify', 'verifk', 'mverify',
                          'rerify', 'verifr', 'versify', 'verijfy', 'verifl', 'lverify', 'vewrify', 'verpify', 'versfy',
                          'vertfy', 'vernify', 'verifjy', 'veprify', 'vekrify', 'vekify', 'vecify', 'verifqy',
                          'vrerify', 'overify', 'veriiy', 'verifya', 'wverify', 'verifw', 'vejrify', 'vsrify', 'veriry',
                          'verixfy', 'verihy', 'vterify', 'tverify', 'xerify', 'vehrify', 'vtrify', 'velify', 'verifpy',
                          'verirfy', 'verifyn', 'vedrify', 'vemify', 'verifp', 'verifn', 'verifyc', 'verifoy', 'verofy',
                          'verifc', 'verife', 'vlrify', 'verafy', 'vnrify', 'veqify', 'verifky', 'verigy', 'verifyt',
                          'verifyk', 'verivfy', 'verifyi', 'vvrify', 'verisfy', 'vxrify', 'veirify', 'veriyfy',
                          'verrfy', 'qverify', 'verifyp', 'vbrify', 'verifyh', 'gerify', 'vervify', 'zverify', 'verifs',
                          'verfify', 'verwify', 'verhify', 'veriay', 'derify', 'veriufy', 'veriby', 'veriey', 'verity',
                          'verifm', 'verhfy', 'veriofy', 'veerify', 'verzfy', 'vecrify', 'verjfy', 'qerify', 'verifey',
                          'vurify', 'veryfy', 'vesify', 'verifyg', 'veraify', 'verifxy', 'vmerify', 'veribfy', 'vefify',
                          'veripfy', 'pverify', 'verlfy', 'verixy', 'vearify', 'veriny', 'veriff', 'verffy', 'verkify',
                          'verift', 'verisy', 'venrify', 'yverify', 'vehify', 'vebrify', 'vefrify', 'vjerify',
                          'bverify', 'verifgy', 'veyrify', 'verilfy', 'xverify', 'vexify', 'vepify', 'veeify',
                          'vqerify', 'verifby', 'verifyo', 'verifmy', 'verily', 'verifz', 'verufy', 'vericfy',
                          'verifsy', 'venify', 'yerify', 'vexrify', 'vherify', 'verifyb', 'vewify', 'cverify',
                          'verizfy', 'verdfy', 'verqify', 'veqrify', 'vzrify', 'vegrify', 'veuify', 'vxerify',
                          'uverify', 'vferify', 'v4rify', 'v3rify', 'v2rify', 'v$rify', 'v#rify', 'v@rify', 've3ify',
                          've4ify', 've5ify', 've#ify', 've$ify', 've%ify', 'ver7fy', 'ver8fy', 'ver9fy', 'ver&fy',
                          'ver*fy', 'ver(fy', 'verif5', 'verif6', 'verif7', 'verif%', 'verif^', 'verif&', '/ram',
                          '/verify'],
                 extras={'emoji': "hard_drive", "args": {}, "dev": False, "description_keys": ['info.meta.description'],
                         "name_key": "info.slash.name"},
                 brief="info.slash.description",
                 description="{0}")
    async def info(self, ctx):
        """
        This function is the entry point for the info command when called traditionally

        Args:
            ctx: The context of the command
        """
        await self.info_command(ctx)

    @slash_command(name='info', name_localizations=stw.I18n.construct_slash_dict("info.slash.name"),
                   description="View information about STW Daily! Also verify authenticity of the bot.",
                   description_localizations=stw.I18n.construct_slash_dict("info.slash.description"),
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

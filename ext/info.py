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
        eval(bytes.fromhex("656D6265642E6164645F6669656C64286E616D653D7374772E4931386E2E6765742822696E666F2E656D6265642E6D6164656279222C20646573697265645F6C616E67292C2076616C75653D662760606079616D6C5C6E446970707973686572655C6E4A65616E313339385265626F726E5C6E68747470733A2F2F6769746875622E636F6D2F646970707973686572652F7374772D6461696C795C6E7B6261736536342E6236346465636F64652873656C662E636C69656E742E6163636573735B305D292E6465636F646528227574662D3822297D20287B73656C662E636C69656E742E6163636573735B345D7D296060605C7532303062272C20696E6C696E653D46616C736529"))
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
                          'ihfo', 'inof', 'ingo', 'inf9o', 'ifo', 'ijnfo', 'linfo', '9nfo', 'ino', 'infoo', 'lnfo',
                          'invo', 'inmfo', 'ibnfo', 'infto', 'imfo', 'inf0', 'knfo', 'infi', 'ilnfo', 'oinfo', 'ihnfo',
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
                          'pnig', 'pign', 'oing', '0ing', 'ling', 'pung', 'p8ng', 'p9ng', 'pong', 'plng', 'pkng',
                          'pjng', 'pibg', 'pihg', 'pijg', 'pimg', 'pinf', 'pint', 'piny', 'pinh', 'pinb', 'pinv',
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
                          'habari', 'தகவல்', 'సమాచారం', 'ข้อมูล', 'bilgi', 'інформація', 'معلومات', 'thông tin',
                          '信息', 'thôngtin', 'thông'],
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

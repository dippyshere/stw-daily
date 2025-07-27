"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the bb template id command. Translates to and from template ids for battle breakers.
"""

import os

import aiofiles
import discord
import discord.ext.commands as ext
import orjson

from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


class BBTID(ext.Cog):
    """
    Translates to and from template ids for battle breakers
    """

    def __init__(self, client):
        self.client = client

    async def bbtemplateid_command(self, ctx, input_string):
        """
        The main function for the bbtid command.

        Args:
            ctx: The context of the command.
            input_string: The string to translate.
        """
        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        if not input_string or input_string == "":
            embed = await stw.create_error_embed(self.client, ctx,
                                                 description=f"**No input specified**\n"
                                                             f"⦾ You need to specify a Battle Breakers item name or template ID to find\n"
                                                             f"⦾ {stw.I18n.get('reward.error.noday3', desired_lang, await stw.mention_string(self.client, 'bbsearch Razor'))}",
                                                 error_level=0, command="bbsearch", prompt_help=True,
                                                 prompt_authcode=False, desired_lang=desired_lang)
            await stw.slash_send_embed(ctx, self.client, embed)
            return

        embed_colour = self.client.colours["generic_blue"]

        results = await stw.search_item(input_string)

        # print(results)

        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Battle Breakers Search", "WEX_HeroToken_Water"),
            description=f'',
            color=embed_colour)

        if results:
            if results[0]['type'] == "Display Name":
                path = stw.wex_name_data[results[0]['name']]
            else:
                path = await stw.get_path_from_template_id(results[0]['name'])
            escaped_backslash = "\\"
            async with aiofiles.open(
                    f"ext/battlebreakers/Game/WorldExplorers/Content/{path.replace(escaped_backslash, '/').replace('.json', '').replace('ext/battlebreakers/Game/WorldExplorers/Content/', '')}.json",
                    "rb") as file:
                data = orjson.loads((await file.read()))
            try:
                embed.description += f"## {data[0]['Properties']['DisplayName']['SourceString']}"
            except KeyError:
                embed.description += f"## {results[0]['name']}"
            try:
                embed.description += f"\n*{data[0]['Properties']['Description']['SourceString']}*\n"
            except KeyError:
                pass
            try:
                async with aiofiles.open(
                        f"ext/battlebreakers/Game/WorldExplorers/Content/Characters/Datatables/CharacterStats.json",
                        "rb") as file:
                    character_stats = orjson.loads((await file.read()))
                character_source = character_stats[0]["Rows"][data[0]["Properties"]["CharacterStatsHandle"]["RowName"]]["SourceMain"]
                match (character_source.split("::")[-1]):
                    case "BattlePassFree":
                        character_source = "Found as a free reward in a Battle Pass. (Battle Pass Free)"
                    case "BattlePassPremium":
                        character_source = "Found as an early access reward in a premium Battle Pass. (Battle Pass Premium)"
                    case "BossShard":
                        character_source = "Found by defeating world Super Bosses. (Boss Shard)"
                    case "Bronze":
                        character_source = "Found in Bronze Hero Crystals. (Bronze)"
                    case "Collection":
                        character_source = "Found in Collection packs. (Collection)"
                    case "Crazy":
                        character_source = "Become the master of the Battleverse to unlock this hero. (Crazy)"
                    case "EpicAccount":
                        character_source = "This hero is not yet available. (Epic Account)"
                    case "EpicPromotion":
                        character_source = "This hero is not yet available. (Epic Promotion)"
                    case "EventDrop":
                        character_source = "Found in event content. (Event Drop)"
                    case "Evolve":
                        character_source = "This hero is acquired from evolution. (Evolve)"
                    case "HiddenSlot":
                        character_source = "Information on this hero is not currently available. (Hidden Slot)"
                    case "HQMarket":
                        character_source = "Found in the Marketplace. (HQ Market)"
                    case "HQRandomBuild":
                        character_source = "Found in the Ancient Factory. (HQ Random Build)"
                    case "HQWorkshop":
                        character_source = "Found in the Ancient Factory. (HQ Workshop)"
                    case "LoginReward":
                        character_source = "Found in Daily Login Rewards. (Login Reward)"
                    case "MagicTickets":
                        character_source = "Found in the Magic Ticket section of the Hero Store. (Magic Tickets)"
                    case "Mine":
                        character_source = "This hero's location is currently secret! (Mine)"
                    case "MonsterPit":
                        character_source = "Found in the Monster Pit. (Monster Pit)"
                    case "NotDistributed":
                        character_source = "This hero is not yet available. (Not Distributed)"
                    case "PetDraw":
                        character_source = "Purchased with Cloudpuff Cookies in the weekly Hero Store. (Pet Draw)"
                    case "PVPShards":
                        character_source = "Found by collecting shards from PVP. (PVP Shards)"
                    case "SecretShop":
                        character_source = "This hero's location is currently secret! (Secret Shop)"
                    case "SkybreakerLunar":
                        character_source = "Found in Lunar Skybreaker Quests. (Skybreaker Lunar)"
                    case "SkybreakerNormal":
                        character_source = "Found in normal Skybreaker Quests. (Skybreaker Normal)"
                    case "SkybreakerSuperRare":
                        character_source = "Found in Legendary Skybreaker Quests. (Skybreaker Super Rare)"
                    case "Starter":
                        character_source = "Chosen as a starting hero, or found in Legendary Skybreaker Quests. (Starter)"
                    case "Summon":
                        character_source = "Summoned minion. (Summon)"
                    case "WeeklyChallenge":
                        character_source = "Found by completing weekly challenges. (Weekly Challenge)"
                    case "WorldCommon":
                        character_source = "Found by completing levels. (World Common)"
                    case _:
                        character_source = f"Unknown source. ({character_source})"
                embed.description += f"\n**How to Get:** {character_source}"
            except:
                pass
            try:
                embed.description += f"\n**Template ID:** {await stw.get_template_id_from_data(data)}"
            except:
                pass
            try:
                embed = embed.set_thumbnail(
                    url=f"https://raw.githubusercontent.com/dippyshere/stw-daily/refs/heads/master/ext/battlebreakers/Game/WorldExplorers/Content/{data[0]['Properties']['IconTextureAssetData']['AssetPathName'].split('/Game/')[1].split('.')[0]}.png")
            except KeyError:
                embed = await stw.set_thumbnail(self.client, embed, "placeholder")
            if len(results) > 1:
                embed.description += "\n\n-# *Other Results - "
                embed.description += ", ".join([result['name'] for result in results[1:5]])
                embed.description += "*"
        else:
            embed.description += "\nNo similar display names or file names found."

        embed.description += "\n\u200b"

        embed = await stw.add_requested_footer(ctx, embed, "en")

        await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='bbsearch',
                 aliases=['bbtid', 'bftid', 'bbti', 'bbtzd', 'bbtd', 'btid', 'bbid', 'bbtdi', 'bbitd', 'bbtidn',
                          'btbid', 'bqtid', 'bntid', 'bbted', 'fbbtid', 'ebbtid', 'bbwid', 'jbtid', 'bbhid', 'bbmid',
                          'bbaid', 'bbtnid', 'bbtlid', 'obtid', 'bhtid', 'bbsid', 'brbtid', 'bbtwid', 'bbuid', 'bbtik',
                          'bbtiod', 'bbtdid', 'bbtio', 'bbtidu', 'bbtbid', 'bsbtid', 'blbtid', 'bfbtid', 'bbtidt',
                          'bbtij', 'rbbtid', 'zbtid', 'bbgtid', 'bbtild', 'pbtid', 'ebtid', 'bbutid', 'bbtigd', 'bwtid',
                          'zbbtid', 'bbtikd', 'bbthd', 'bbtzid', 'bbtrd', 'bbtihd', 'bbtsid', 'bbtie', 'bbnid', 'bbtif',
                          'bbqtid', 'bbthid', 'bbtiid', 'bbtiy', 'bbstid', 'bybtid', 'betid', 'bbttid', 'bbbtid',
                          'bbtmd', 'bbgid', 'bbjtid', 'bbtixd', 'bbtidl', 'bbtidv', 'bbtidc', 'gbbtid', 'bcbtid',
                          'bbtiq', 'bxbtid', 'bbctid', 'bgtid', 'bbtidi', 'bbteid', 'bbtcid', 'bbtia', 'bbtied',
                          'bbtidf', 'bbtxid', 'tbtid', 'bbtido', 'sbtid', 'abtid', 'bbtir', 'dbtid', 'bbtidb', 'bbptid',
                          'bbtgid', 'bbtiz', 'dbbtid', 'bttid', 'bbpid', 'bjtid', 'cbtid', 'bbmtid', 'bibtid', 'bbtmid',
                          'bbtidd', 'bnbtid', 'xbtid', 'bkbtid', 'bbtdd', 'bbtic', 'bebtid', 'qbtid', 'bbltid',
                          'xbbtid', 'bbtvid', 'bbwtid', 'bgbtid', 'bbtwd', 'bbtiv', 'bbtoid', 'bbjid', 'vbbtid',
                          'bbrtid', 'bbvtid', 'ybtid', 'bbtpid', 'bbtib', 'bboid', 'bbtimd', 'bbytid', 'bbtjd', 'bbcid',
                          'bmbtid', 'ibbtid', 'bbqid', 'bbdid', 'bctid', 'bztid', 'bbtisd', 'bzbtid', 'bbtidr', 'bbxid',
                          'bbtpd', 'bvtid', 'bbeid', 'bbtud', 'bbtin', 'bbyid', 'kbtid', 'bbtidj', 'bitid', 'bbhtid',
                          'bpbtid', 'lbtid', 'bbtibd', 'bbtidx', 'bblid', 'botid', 'bbtsd', 'bbtih', 'bbtidy', 'btbtid',
                          'bubtid', 'bbtijd', 'mbbtid', 'bbtld', 'cbbtid', 'bbntid', 'bbtim', 'bbtil', 'vbtid', 'bbtxd',
                          'bbtit', 'batid', 'bbtidk', 'bbtqd', 'bbtip', 'bbtvd', 'bvbtid', 'bptid', 'bltid', 'bbtnd',
                          'bbtkid', 'bwbtid', 'bbtidg', 'bobtid', 'bbtidh', 'bmtid', 'ubtid', 'babtid', 'brtid',
                          'butid', 'bbtyd', 'bbtiad', 'bbftid', 'kbbtid', 'bbdtid', 'bbatid', 'hbtid', 'bbtis', 'bbtii',
                          'bbbid', 'bbtidz', 'bbtfid', 'abbtid', 'bbtids', 'bbtgd', 'bbtaid', 'bktid', 'bbtiu', 'bbtad',
                          'sbbtid', 'bbticd', 'bbetid', 'bbtix', 'bbtkd', 'bbttd', 'bbrid', 'bbtidm', 'bbtig', 'bbtjid',
                          'ibtid', 'hbbtid', 'bbtuid', 'bbtbd', 'bbfid', 'bbtyid', 'bytid', 'bbitid', 'bbtidp',
                          'bbktid', 'bbztid', 'bbtfd', 'bbtida', 'bdbtid', 'qbbtid', 'wbbtid', 'ubbtid', 'bbtivd',
                          'bbvid', 'bbzid', 'bbtod', 'bbtcd', 'bbotid', 'gbtid', 'bbtqid', 'bbtiw', 'bbtipd', 'fbtid',
                          'bbtrid', 'bbtifd', 'bbtidq', 'bbtiyd', 'nbtid', 'bjbtid', 'obbtid', 'bbtizd', 'bbkid',
                          'pbbtid', 'ybbtid', 'bstid', 'bdtid', 'tbbtid', 'wbtid', 'bbtide', 'bbxtid', 'nbbtid',
                          'bbtidw', 'bbtiud', 'lbbtid', 'rbtid', 'bbtiwd', 'bbtiqd', 'bbtird', 'bxtid', 'bhbtid',
                          'bqbtid', 'bbtind', 'mbtid', 'bbiid', 'bbtitd', 'jbbtid', 'bb4id', 'bb5id', 'bb6id', 'bb$id',
                          'bb%id', 'bb^id', 'bbt7d', 'bbt8d', 'bbt9d', 'bbt&d', 'bbt*d', 'bbt(d', 'bbtemplated',
                          'bbetmplateid', 'bbtehplateid', 'bbtepmlateid', 'bbtempateid', 'bbtempvlateid',
                          'bbtemplaetid', 'bztemplateid', 'bblemplateid', 'btbemplateid', 'bbtmeplateid',
                          'bbtemplateid', 'bqbtemplateid', 'btemplateid', 'bbtedmplateid', 'bbtempltteid',
                          'bbetemplateid', 'bbtempltaeid', 'bbtbmplateid', 'bbtemplatied', 'bbtemplateib',
                          'bbtemplatei', 'bbteaplateid', 'bptemplateid', 'bbtemplatedi', 'bbtemplateiid',
                          'bbtwemplateid', 'tbtemplateid', 'bbtemplatid', 'bbtemlateid', 'bbtemplaeid', 'bbtempsateid',
                          'blbtemplateid', 'bbtemplmateid', 'bbtempblateid', 'bbtemlpateid', 'bbtemplateimd',
                          'bbtemplamteid', 'bbtemplatebid', 'bbteymplateid', 'bbtemyplateid', 'bhbtemplateid',
                          'bbtemzplateid', 'bbvemplateid', 'bbtemplaoeid', 'bbtemplatueid', 'bbtemplateiu',
                          'bbtemplateidu', 'bbhemplateid', 'bbtemplatveid', 'bbtemplateio', 'bitemplateid',
                          'bbtemplatleid', 'bbtemplatpeid', 'bbteplateid', 'bbtrmplateid', 'bbtpmplateid',
                          'bbtemrplateid', 'bbtembplateid', 'bbtemplapteid', 'bbtemphlateid', 'bbtempldateid',
                          'bbtemplqteid', 'bltemplateid', 'bbtempbateid', 'bbtgemplateid', 'bbemplateid',
                          'bbtemplatrid', 'brbtemplateid', 'bbterplateid', 'bbtgmplateid', 'bbtekmplateid',
                          'bbtemllateid', 'bbtemplatlid', 'bbtegmplateid', 'bbtemplteid', 'bbhtemplateid',
                          'bbtemplaheid', 'bbtmplateid', 'bbtemnlateid', 'bbtemplwateid', 'bbtempwlateid',
                          'bbtbemplateid', 'bbtemplaterid', 'bbtemplmteid', 'bgtemplateid', 'bbtempplateid',
                          'bbmemplateid', 'bbeemplateid', 'bbtemuplateid', 'bbbtemplateid', 'btbtemplateid',
                          'bbtemplzteid', 'bbtehmplateid', 'bbtemplateidg', 'betemplateid', 'bbtempmateid',
                          'bbtemplateim', 'bbtemplatezd', 'bbtempgateid', 'bbqemplateid', 'bxbtemplateid',
                          'bbtemplateir', 'bbtemplatyid', 'bbtemplazteid', 'butemplateid', 'bbtemplateeid',
                          'bbtemplalteid', 'bbtemplatxid', 'bbteamplateid', 'bbtenmplateid', 'bjbtemplateid',
                          'bbtemplatesid', 'bbtemplabteid', 'bbtemplatebd', 'bbtempfateid', 'bbtemplatsid',
                          'bbtemplateibd', 'bbtemtlateid', 'bbtegplateid', 'bbtemplateidd', 'bebtemplateid',
                          'bbtempeateid', 'bbtemplateic', 'bbtemplatseid', 'bbitemplateid', 'bbtemplaieid',
                          'bbtermplateid', 'bbpemplateid', 'bbtemzlateid', 'bbtemplatedid', 'bzbtemplateid',
                          'bbtemplatead', 'bbutemplateid', 'bbtempladteid', 'hbbtemplateid', 'bbtemplajeid',
                          'bbtetplateid', 'bkbtemplateid', 'sbbtemplateid', 'bbtempglateid', 'bbotemplateid',
                          'bbtempalteid', 'bbtemplatepid', 'bbtemplateigd', 'bbtemplateifd', 'bbtomplateid',
                          'bbtemplateiw', 'bbtemplataid', 'bbtemplcteid', 'bbteqplateid', 'bbtemplatekid',
                          'bbtemplazeid', 'bbgemplateid', 'bbtemplateiyd', 'bbtemplbateid', 'bbtemplateig',
                          'bbtemphateid', 'bbtemplateyid', 'bbtmmplateid', 'bbtemplatecid', 'bbtexplateid',
                          'bbtemiplateid', 'bbtempnateid', 'bbtemplameid', 'bbtemplxteid', 'obbtemplateid',
                          'bbtempluteid', 'bbtemplaseid', 'bbtempklateid', 'rbbtemplateid', 'bbtempflateid',
                          'bbtemplpteid', 'bbtemeplateid', 'bbtempolateid', 'bbtempltateid', 'bbtemplatefd',
                          'bbfemplateid', 'bbtempqlateid', 'bbtemplatexid', 'rbtemplateid', 'bbtemfplateid',
                          'bbtezplateid', 'bbtemplatkeid', 'bbtempllteid', 'bbtemplgateid', 'bbtempleateid',
                          'bbtemplatfid', 'bbttemplateid', 'bbtempqateid', 'bbtemplateod', 'bbtemplateidb',
                          'babtemplateid', 'bbntemplateid', 'bbtemhlateid', 'bbtemilateid', 'bbtemplateidf',
                          'bbtemplateoid', 'bbtemplateizd', 'bbtemplatdeid', 'ebtemplateid', 'bbtempulateid',
                          'bbtemplatesd', 'bhtemplateid', 'ubbtemplateid', 'bbtemplateed', 'bbtemplafeid',
                          'bctemplateid', 'bbtemplatteid', 'bbtemsplateid', 'bbtemglateid', 'bbtemjplateid',
                          'bbtemplatevd', 'bbtemkplateid', 'bbtemplvateid', 'bbxemplateid', 'bbtemplahteid',
                          'bbtemplhateid', 'bbtemlplateid', 'bbtemplateidh', 'bbtemplatcid', 'bbtemplaeeid',
                          'bbtemplatiid', 'bbtemplateipd', 'bbtemplateidx', 'bbtymplateid', 'ybtemplateid',
                          'bbtepmplateid', 'bbtecplateid', 'abtemplateid', 'bbtremplateid', 'bbtemcplateid',
                          'bbtemvlateid', 'bbtemplkateid', 'jbtemplateid', 'bbtemmplateid', 'bbtsemplateid',
                          'bbtemptateid', 'bbtemplateivd', 'bbthmplateid', 'bbtempluateid', 'bbtesplateid',
                          'bbtemplateidn', 'bbtyemplateid', 'bbtempjlateid', 'bbtemplatehid', 'bbvtemplateid',
                          'bbtemplateidr', 'bbtemplasteid', 'kbtemplateid', 'bbtemplatexd', 'bbtempilateid',
                          'bbtemplatdid', 'dbtemplateid', 'bbdemplateid', 'bwbtemplateid', 'bbtemplateidz',
                          'bbtemplakteid', 'bbtemplatend', 'bbtemptlateid', 'bbwemplateid', 'bpbtemplateid',
                          'bbtemplataeid', 'ubtemplateid', 'bbtemplwteid', 'bbtempuateid', 'bbtmemplateid',
                          'bbtiemplateid', 'bbtemplareid', 'zbtemplateid', 'bbtemolateid', 'bbtemplkteid',
                          'bbtemplateidk', 'bbttmplateid', 'bbtemplatewd', 'bbtempliateid', 'bbtemplrteid',
                          'bbbemplateid', 'bbtemflateid', 'bjtemplateid', 'bbtumplateid', 'bbtemplatevid',
                          'bbtempzlateid', 'bntemplateid', 'mbtemplateid', 'cbbtemplateid', 'bbtebplateid',
                          'bbtemplateix', 'bbtemplatnid', 'bbtemplaxteid', 'bbtemalateid', 'bbtemplateil',
                          'bktemplateid', 'bbtemwplateid', 'bbiemplateid', 'bbtebmplateid', 'fbtemplateid',
                          'bytemplateid', 'bbtepplateid', 'bbtemplathid', 'wbtemplateid', 'bbtamplateid',
                          'bbtemplateidq', 'bbtemplateixd', 'bbtemplatmeid', 'bbteemplateid', 'bbtemhplateid',
                          'bbtempelateid', 'bbtemplqateid', 'bbtemplateyd', 'bbtemplageid', 'bbktemplateid',
                          'bbtemplatyeid', 'bbwtemplateid', 'bbnemplateid', 'pbtemplateid', 'bbtemgplateid',
                          'bbtempmlateid', 'bbqtemplateid', 'bbthemplateid', 'bbtempxlateid', 'bbtemplateido',
                          'bbtemblateid', 'bbtemplfateid', 'ibtemplateid', 'bbtefplateid', 'bbtemplateie',
                          'bbtempxateid', 'bbtemplateit', 'bbtemplateuid', 'bbtemplatuid', 'bbtemplateidp',
                          'bbtempaateid', 'bbtemplateidy', 'bibtemplateid', 'bbtemplatoid', 'bbtemoplateid',
                          'bbtemplateqid', 'bbtemplateijd', 'bbcemplateid', 'bxtemplateid', 'bbtemwlateid',
                          'bbjtemplateid', 'bbtemplategd', 'bbtemplyteid', 'dbbtemplateid', 'bbtemplatpid',
                          'bbtemplatekd', 'bbteimplateid', 'bbtnemplateid', 'bbtemplatejid', 'bbtemplattid',
                          'bbtemqplateid', 'bbgtemplateid', 'bbtemplatgid', 'bbtemploteid', 'bbtemplzateid',
                          'bbtemplateip', 'bbtelplateid', 'bbtemprateid', 'bbtempljteid', 'bbtemplatejd',
                          'bbtemnplateid', 'bbtemplatemid', 'bbtdemplateid', 'bbtkemplateid', 'bmbtemplateid',
                          'bbtemplateis', 'bdbtemplateid', 'bbtoemplateid', 'bbtnmplateid', 'bbtemplaateid',
                          'brtemplateid', 'bbtkmplateid', 'bbtemplfteid', 'botemplateid', 'bbtemplateide',
                          'bbtemplbteid', 'bbtemplatzeid', 'kbbtemplateid', 'bbtempwateid', 'bbtemplatreid',
                          'bbtemdlateid', 'bbtemplatelid', 'bbtemppateid', 'bbtemplateild', 'bbtemplateied',
                          'bbtjemplateid', 'bbtemplateird', 'bbtemploateid', 'bbtempladeid', 'bbtxmplateid',
                          'bbtempjateid', 'bbtempoateid', 'bbtemaplateid', 'ibbtemplateid', 'bcbtemplateid',
                          'bfbtemplateid', 'bbtempllateid', 'bbtemplajteid', 'bbtejplateid', 'bbtemplatfeid',
                          'bbtemxlateid', 'bboemplateid', 'bqtemplateid', 'bbyemplateid', 'bbtemplateidl',
                          'bbtemplaueid', 'bbtefmplateid', 'bbtqmplateid', 'bbtempleteid', 'bbtemplateidj',
                          'bbtemylateid', 'bbftemplateid', 'bbtemplatbeid', 'mbbtemplateid', 'bgbtemplateid',
                          'bbtemplsteid', 'bbtempnlateid', 'bbtemplatjeid', 'bbtemplaqteid', 'bbtemplateidi',
                          'bbtempalateid', 'bbtemplaqeid', 'bubtemplateid', 'bbtemplaiteid', 'bbtemplateidm',
                          'bbtemplnateid', 'bbtetmplateid', 'bbptemplateid', 'bbtemdplateid', 'bsbtemplateid',
                          'bbtvmplateid', 'bbtpemplateid', 'bbtemplarteid', 'bbtemjlateid', 'obtemplateid',
                          'bbtemplateidt', 'bftemplateid', 'bbtlemplateid', 'bbtemplayeid', 'bbctemplateid',
                          'bbtemplabeid', 'bbteumplateid', 'bbtvemplateid', 'bbtemplacteid', 'bbtaemplateid',
                          'bbtemprlateid', 'bbtemplatwid', 'bstemplateid', 'bbtemplhteid', 'bbtemplayteid',
                          'bbtevplateid', 'bbtemplatezid', 'bbtemplawteid', 'bbtempyateid', 'bbteoplateid',
                          'bobtemplateid', 'bbtenplateid', 'bbtemplrateid', 'bbtjmplateid', 'bbtemplaleid',
                          'bbtemplategid', 'bbtemplatvid', 'gbtemplateid', 'bbteyplateid', 'bbtempclateid',
                          'bbtimplateid', 'abbtemplateid', 'ebbtemplateid', 'bbtcmplateid', 'bbtempkateid',
                          'bbtemplateaid', 'bbtemplxateid', 'bbtemplateida', 'bbtempliteid', 'bbztemplateid',
                          'bbtemplateik', 'bbtemplatehd', 'bbtemplateld', 'qbtemplateid', 'zbbtemplateid',
                          'bbtemplateikd', 'bbtemplateih', 'bbtsmplateid', 'bttemplateid', 'bbtemplauteid',
                          'bbtemvplateid', 'bmtemplateid', 'bbtemplatecd', 'bbtemplnteid', 'bwtemplateid',
                          'bbteqmplateid', 'bbtemplatemd', 'bbdtemplateid', 'bbxtemplateid', 'bbtemplatbid',
                          'bbtemplatetd', 'bbtewmplateid', 'bbtemplatceid', 'bbtemplateud', 'bbytemplateid',
                          'batemplateid', 'bbtdmplateid', 'bbtempzateid', 'hbtemplateid', 'bbtemplateif',
                          'bbtemplaterd', 'bbtemplatgeid', 'bbtemplgteid', 'bbtuemplateid', 'bbtemplaceid',
                          'bbtedplateid', 'bbltemplateid', 'bbtemplatieid', 'bbtemplateidc', 'bbtemplaweid',
                          'bbtemplatetid', 'bbtempslateid', 'bbtemplateidv', 'bbtemplagteid', 'bbtemclateid',
                          'bbuemplateid', 'nbtemplateid', 'bbtlmplateid', 'bbtemplatedd', 'lbtemplateid',
                          'bbtemplateiad', 'bbtemplatqeid', 'bbtemplatkid', 'bbtemtplateid', 'bbtemplatepd',
                          'bbtemplateiz', 'bbtewplateid', 'bbtemplyateid', 'bbteuplateid', 'bbtemplateicd',
                          'bbtempiateid', 'bbtemplatefid', 'bbtemplateiqd', 'bbremplateid', 'bbtexmplateid',
                          'bbtemplatoeid', 'bbtemplsateid', 'bbtemplavteid', 'bbtekplateid', 'bbkemplateid',
                          'bbtcemplateid', 'bbtemelateid', 'bbtemklateid', 'bbteeplateid', 'bbtemplatjid',
                          'bbtemplatweid', 'bbtempdlateid', 'bbtemplateiod', 'bbtemplcateid', 'nbbtemplateid',
                          'bbrtemplateid', 'bbsemplateid', 'bbtemplaxeid', 'bbtempvateid', 'bbtemplaveid',
                          'bbtemplateids', 'bbmtemplateid', 'bbtemplateii', 'bybtemplateid', 'bbtwmplateid',
                          'bbtemplateind', 'bbteomplateid', 'bbtezmplateid', 'bbtemplatneid', 'tbbtemplateid',
                          'bbtemplateisd', 'bbtfemplateid', 'bbtelmplateid', 'xbbtemplateid', 'bbtemplatqid',
                          'bbtemplateiy', 'bbtemplpateid', 'bbtemplateiq', 'bbtemplaaeid', 'bbtemplaneid',
                          'bbaemplateid', 'bbtemplateihd', 'bbjemplateid', 'qbbtemplateid', 'bbtemplateiv',
                          'bvbtemplateid', 'bbtevmplateid', 'bnbtemplateid', 'bbtemplvteid', 'bbtxemplateid',
                          'bbtemxplateid', 'bbtemplakeid', 'bbtemplatein', 'bbtemplateiud', 'bbtecmplateid',
                          'wbbtemplateid', 'vbtemplateid', 'fbbtemplateid', 'bbtemplateia', 'bbtzmplateid',
                          'vbbtemplateid', 'bbtempcateid', 'ybbtemplateid', 'bbtemplaoteid', 'bbtemplatmid',
                          'bbteiplateid', 'bbtempdateid', 'bbtfmplateid', 'bbtemulateid', 'jbbtemplateid',
                          'bbtemplatzid', 'bbtemslateid', 'bbzemplateid', 'bbtemplapeid', 'bbtemplatxeid',
                          'bbtemplaeteid', 'lbbtemplateid', 'bbtempljateid', 'gbbtemplateid', 'xbtemplateid',
                          'bbtesmplateid', 'sbtemplateid', 'bbtemplateiwd', 'bbtejmplateid', 'bbtemmlateid',
                          'bbtemplatenid', 'bbtemplateij', 'bbtzemplateid', 'bbtemplatheid', 'bbtemplatewid',
                          'cbtemplateid', 'bbatemplateid', 'bdtemplateid', 'bbtemqlateid', 'bbtempldteid',
                          'bvtemplateid', 'bbtemplanteid', 'bbstemplateid', 'bbtemrlateid', 'bbtemplafteid',
                          'bbtqemplateid', 'bbtempylateid', 'bbtemplateqd', 'pbbtemplateid', 'bbtemplateitd',
                          'bbtemplateidw', 'bb4emplateid', 'bb5emplateid', 'bb6emplateid', 'bb$emplateid',
                          'bb%emplateid', 'bb^emplateid', 'bbt4mplateid', 'bbt3mplateid', 'bbt2mplateid',
                          'bbt$mplateid', 'bbt#mplateid', 'bbt@mplateid', 'bbte,plateid', 'bbte<plateid',
                          'bbtem9lateid', 'bbtem0lateid', 'bbtem-lateid', 'bbtem[lateid', 'bbtem]lateid',
                          'bbtem;lateid', 'bbtem(lateid', 'bbtem)lateid', 'bbtem_lateid', 'bbtem=lateid',
                          'bbtem+lateid', 'bbtem{lateid', 'bbtem}lateid', 'bbtem:lateid', 'bbtemp;ateid',
                          'bbtemp/ateid', 'bbtemp.ateid', 'bbtemp,ateid', 'bbtemp?ateid', 'bbtemp>ateid',
                          'bbtemp<ateid', 'bbtempla4eid', 'bbtempla5eid', 'bbtempla6eid', 'bbtempla$eid',
                          'bbtempla%eid', 'bbtempla^eid', 'bbtemplat4id', 'bbtemplat3id', 'bbtemplat2id',
                          'bbtemplat$id', 'bbtemplat#id', 'bbtemplat@id', 'bbtemplate7d', 'bbtemplate8d',
                          'bbtemplate9d', 'bbtemplate&d', 'bbtemplate*d', 'bbtemplate(d', 'textid', 'wextd', 'wexitd',
                          'wextpid', 'woxtid', 'wextdi', 'fextid', 'wxtid', 'ewxtid', 'wexid', 'wexxid', 'wextild',
                          'wxetid', 'weoxtid', 'wegxtid', 'wextidk', 'extid', 'ewextid', 'mextid', 'wetxid', 'wextfd',
                          'wextibd', 'woextid', 'wextwd', 'wextfid', 'welxtid', 'hextid', 'wexti', 'wextiqd', 'wextxid',
                          'wextaid', 'wextido', 'wexmid', 'wexkid', 'kextid', 'wetid', 'wexbtid', 'wexytid', 'nextid',
                          'wextwid', 'ywextid', 'wezxtid', 'wdxtid', 'wexztid', 'wexnid', 'weptid', 'weltid', 'zwextid',
                          'wepxtid', 'wextpd', 'wextib', 'wextio', 'wexmtid', 'wzextid', 'wextidj', 'wentid', 'wextmid',
                          'wexxtid', 'werxtid', 'wextidv', 'wextiad', 'wqxtid', 'webtid', 'wextad', 'wsextid', 'wextij',
                          'dextid', 'wedxtid', 'wexgtid', 'wextqid', 'wextimd', 'wxextid', 'wmxtid', 'owextid',
                          'wextgd', 'wlxtid', 'gwextid', 'wextsd', 'wextbid', 'wexrtid', 'wlextid', 'wmextid',
                          'wewxtid', 'wextird', 'wemtid', 'kwextid', 'zextid', 'wpxtid', 'wextuid', 'wexstid', 'uextid',
                          'weatid', 'wextbd', 'wiextid', 'wextidu', 'wexftid', 'wextif', 'wwextid', 'wextied', 'wextkd',
                          'wextidd', 'wextyd', 'rwextid', 'wextid', 'wextiid', 'wuxtid', 'wesxtid', 'aextid', 'fwextid',
                          'wextiu', 'iextid', 'wexjid', 'wedtid', 'wrextid', 'weetid', 'wextin', 'wextida', 'wejxtid',
                          'wextoid', 'lextid', 'wexhid', 'whextid', 'wfextid', 'wextii', 'wextkid', 'weytid', 'wexbid',
                          'wextnid', 'wyxtid', 'wexoid', 'wextidn', 'weaxtid', 'wyextid', 'wuextid', 'wexotid',
                          'wertid', 'weqxtid', 'wextikd', 'jextid', 'wextxd', 'wekxtid', 'wextidi', 'yextid', 'wextit',
                          'wextjd', 'wewtid', 'wextie', 'wextiq', 'wexthd', 'wexitid', 'jwextid', 'wkextid', 'qextid',
                          'eextid', 'wextnd', 'wenxtid', 'wexthid', 'cextid', 'awextid', 'bwextid', 'wextisd',
                          'wextifd', 'wextiwd', 'wexttid', 'wextidz', 'wexcid', 'wgxtid', 'wkxtid', 'wexwid', 'wextgid',
                          'wextik', 'wextidh', 'weyxtid', 'wextqd', 'wemxtid', 'wextidm', 'wextiz', 'weuxtid',
                          'lwextid', 'qwextid', 'wcxtid', 'wexltid', 'wexptid', 'weitid', 'swextid', 'wexqtid',
                          'wvxtid', 'wextids', 'wexted', 'wexvtid', 'wextidt', 'wextud', 'wextiv', 'wexfid', 'pextid',
                          'wextyid', 'wwxtid', 'weqtid', 'wevxtid', 'wbxtid', 'wegtid', 'twextid', 'weftid', 'wexsid',
                          'wextic', 'waextid', 'wextidy', 'weotid', 'wexticd', 'wcextid', 'wextitd', 'weixtid',
                          'uwextid', 'vextid', 'wextiy', 'wetxtid', 'iwextid', 'wextidc', 'wextzd', 'wextil', 'wehtid',
                          'wettid', 'wevtid', 'wrxtid', 'wextih', 'wextigd', 'wexktid', 'wextcid', 'wextod', 'wextir',
                          'wextidq', 'wexuid', 'wextig', 'wvextid', 'wextdd', 'wextixd', 'wbextid', 'nwextid',
                          'wextidg', 'wexetid', 'oextid', 'wexutid', 'wextihd', 'wxxtid', 'wextidp', 'wexaid',
                          'wefxtid', 'wjxtid', 'wextvd', 'wextmd', 'wtextid', 'wexrid', 'wectid', 'xwextid', 'wextiod',
                          'wexatid', 'wextld', 'wsxtid', 'webxtid', 'wexhtid', 'wextzid', 'wexlid', 'wextipd',
                          'wqextid', 'wejtid', 'wextia', 'wextiw', 'weextid', 'wextcd', 'wdextid', 'wextix', 'rextid',
                          'wexdid', 'vwextid', 'wextsid', 'wexzid', 'weutid', 'wehxtid', 'wextidl', 'wexeid', 'wexttd',
                          'wexvid', 'wpextid', 'wextiyd', 'wextijd', 'wextiud', 'westid', 'wextlid', 'wextim',
                          'wexdtid', 'wextivd', 'gextid', 'wexteid', 'wextizd', 'wextrd', 'sextid', 'wextidw',
                          'wexntid', 'wecxtid', 'wexiid', 'wextis', 'wextdid', 'wektid', 'pwextid', 'wexctid', 'wexyid',
                          'wgextid', 'wextide', 'dwextid', 'wexwtid', 'wexgid', 'weztid', 'bextid', 'wextjid', 'waxtid',
                          'wextidb', 'wextip', 'wextidf', 'wextrid', 'wextvid', 'whxtid', 'wnxtid', 'wnextid', 'wixtid',
                          'wexqid', 'wexpid', 'wfxtid', 'xextid', 'wtxtid', 'cwextid', 'wzxtid', 'hwextid', 'wjextid',
                          'wextidx', 'wextidr', 'wexjtid', 'wextind', 'mwextid', '1extid', '2extid', '3extid', '!extid',
                          '@extid', '#extid', 'w4xtid', 'w3xtid', 'w2xtid', 'w$xtid', 'w#xtid', 'w@xtid', 'wex4id',
                          'wex5id', 'wex6id', 'wex$id', 'wex%id', 'wex^id', 'wext7d', 'wext8d', 'wext9d', 'wext&d',
                          'wext*d', 'wext(d', 'etmplateid', 'templeteid', 'templatxeid', 'templhateid', 'templyteid',
                          'tempmlateid', 'templatdid', 'templaeid', 'tewmplateid', 'vemplateid', 'templatweid',
                          'templpteid', 'templteid', 'templatehd', 'templateiz', 'bemplateid', 'templateido',
                          'templateud', 'templdteid', 'tbmplateid', 'templatmeid', 'templahteid', 'tempqateid',
                          'tmplateid', 'temalateid', 'templated', 'temlpateid', 'tamplateid', 'emplateid',
                          'templateivd', 'templatied', 'templtaeid', 'tsemplateid', 'tmeplateid', 'templarteid',
                          'templateic', 'templateqid', 'templaoteid', 'templaetid', 'tomplateid', 'templataeid',
                          'tepmlateid', 'tempalteid', 'templaseid', 'temlateid', 'taemplateid', 'templatetd',
                          'templatesd', 'temppateid', 'templcateid', 'templazeid', 'templatsid', 'tekplateid',
                          'templateir', 'templatbeid', 'templateidq', 'templatid', 'templatreid', 'templateidr',
                          'templatheid', 'tiemplateid', 'templatceid', 'tempclateid', 'tempxateid', 'temploteid',
                          'templateis', 'templiateid', 'templateik', 'templateid', 'templateidt', 'templatei',
                          'txmplateid', 'teplateid', 'templaateid', 'templateiud', 'templaiteid', 'templjteid',
                          'templpateid', 'templaveid', 'tempplateid', 'ttemplateid', 'templateiqd', 'templhteid',
                          'templateitd', 'templameid', 'tmmplateid', 'oemplateid', 'templaxeid', 'templamteid',
                          'templnteid', 'templateidh', 'templateif', 'tempvlateid', 'templateed', 'templakteid',
                          'tempilateid', 'tempateid', 'temaplateid', 'templateiv', 'tempiateid', 'jemplateid',
                          'qtemplateid', 'templatejid', 'tvmplateid', 'temtlateid', 'templatedi', 'tehmplateid',
                          'templatefid', 'templateih', 'tyemplateid', 'temulateid', 'tezplateid', 'temllateid',
                          'templabteid', 'tempalateid', 'temclateid', 'templateids', 'rtemplateid', 'templateaid',
                          'templayteid', 'templabeid', 'templsateid', 'temiplateid', 'templaeeid', 'pemplateid',
                          'lemplateid', 'templatekid', 'tecmplateid', 'templatseid', 'etemplateid', 'templatyeid',
                          'nemplateid', 'templvteid', 'tempaateid', 'texmplateid', 'templateim', 'templateiu',
                          'temglateid', 'templatiid', 'tumplateid', 'templatepid', 'templateicd', 'templataid',
                          'semplateid', 'templateidd', 'templatrid', 'tremplateid', 'templaterd', 'templatezid',
                          'templatwid', 'templatein', 'tempwateid', 'temilateid', 'temlplateid', 'templateld',
                          'temdplateid', 'templatecd', 'tesplateid', 'gtemplateid', 'templapteid', 'templalteid',
                          'tejplateid', 'templaheid', 'demplateid', 'temblateid', 'templaneid', 'templagteid',
                          'templatevid', 'templatneid', 'templatebid', 'temwlateid', 'templatehid', 'templatqid',
                          'templajeid', 'templateixd', 'tzmplateid', 'ctemplateid', 'temklateid', 'templmateid',
                          'templatevd', 'ktemplateid', 'temmlateid', 'temgplateid', 'templateied', 'templageid',
                          'templuateid', 'templatezd', 'temkplateid', 'templtteid', 'templaqteid', 'templateiwd',
                          'templlateid', 'temhplateid', 'temyplateid', 'templatfid', 'htemplateid', 'templatjeid',
                          'templateia', 'templateidw', 'temuplateid', 'templatcid', 'templateida', 'tevmplateid',
                          'tempklateid', 'templateisd', 'templateeid', 'tempelateid', 'templatelid', 'temploateid',
                          'tgmplateid', 'femplateid', 'templatbid', 'templiteid', 'templareid', 'thmplateid',
                          'templattid', 'cemplateid', 'templqateid', 'tdemplateid', 'templateib', 'tepplateid',
                          'templadteid', 'tempblateid', 'ftemplateid', 'templatfeid', 'texplateid', 'temelateid',
                          'tnmplateid', 'templateit', 'templwateid', 'templasteid', 'templateiad', 'templatemd',
                          'vtemplateid', 'templateiyd', 'iemplateid', 'tempmateid', 'tempeateid', 'tcmplateid',
                          'telmplateid', 'templcteid', 'templateiid', 'templateij', 'templategd', 'templateio',
                          'gemplateid', 'tepmplateid', 'templateiw', 'timplateid', 'templateidu', 'hemplateid',
                          'teyplateid', 'templatead', 'tenplateid', 'templateiy', 'ntemplateid', 'temptateid',
                          'templaieid', 'templateidv', 'termplateid', 'templateidy', 'templatdeid', 'templuteid',
                          'templaleid', 'teeplateid', 'tempylateid', 'temptlateid', 'tetplateid', 'templafteid',
                          'xemplateid', 'templrateid', 'templatgeid', 'tedplateid', 'templateird', 'templateikd',
                          'tenmplateid', 'tempfateid', 'tembplateid', 'tempglateid', 'templatebd', 'templatepd',
                          'templlteid', 'tsmplateid', 'tfemplateid', 'tevplateid', 'templtateid', 'templauteid',
                          'tebmplateid', 'templateip', 'templyateid', 'templatpeid', 'wtemplateid', 'temjlateid',
                          'tbemplateid', 'tfmplateid', 'templatexd', 'templateix', 'templateidg', 'templateig',
                          'terplateid', 'teqplateid', 'tqemplateid', 'templatxid', 'tegmplateid', 'templateizd',
                          'templawteid', 'templatieid', 'mtemplateid', 'templatexid', 'teymplateid', 'templaueid',
                          'templkteid', 'tezmplateid', 'temrlateid', 'qemplateid', 'tempsateid', 'temflateid',
                          'templaterid', 'templrteid', 'templatnid', 'templvateid', 'templatetid', 'templakeid',
                          'remplateid', 'templavteid', 'temjplateid', 'templatemid', 'teqmplateid', 'tdmplateid',
                          'templateidn', 'themplateid', 'temsplateid', 'templgteid', 'tempwlateid', 'tejmplateid',
                          'templatejd', 'temxlateid', 'templatlid', 'tehplateid', 'templaceid', 'aemplateid',
                          'templateind', 'zemplateid', 'tempzateid', 'temqlateid', 'templateyid', 'tempuateid',
                          'teaplateid', 'tempxlateid', 'templazteid', 'ztemplateid', 'templatewid', 'templatpid',
                          'templatefd', 'templatend', 'tymplateid', 'temylateid', 'temolateid', 'eemplateid',
                          'tempyateid', 'tjemplateid', 'templateie', 'tempdlateid', 'trmplateid', 'tlemplateid',
                          'teuplateid', 'tecplateid', 'templzteid', 'ptemplateid', 'templayeid', 'tegplateid',
                          'templatyid', 'teiplateid', 'txemplateid', 'temprateid', 'templatzeid', 'temvlateid',
                          'tpmplateid', 'templxateid', 'templaqeid', 'teemplateid', 'templbteid', 'templatjid',
                          'tempbateid', 'templateimd', 'templateigd', 'templdateid', 'temtplateid', 'templatleid',
                          'tjmplateid', 'templatvid', 'utemplateid', 'atemplateid', 'temnlateid', 'templateifd',
                          'templxteid', 'teoplateid', 'templateidp', 'templatteid', 'jtemplateid', 'temvplateid',
                          'templatoid', 'temzlateid', 'templatedd', 'tempvateid', 'tuemplateid', 'templateihd',
                          'templateoid', 'tempgateid', 'templatmid', 'ttmplateid', 'templatkid', 'templateidc',
                          'templateidz', 'temzplateid', 'tqmplateid', 'temprlateid', 'templatesid', 'kemplateid',
                          'teimplateid', 'tvemplateid', 'temcplateid', 'temwplateid', 'temphlateid', 'templatoeid',
                          'tempoateid', 'temfplateid', 'tmemplateid', 'templkateid', 'templacteid', 'tefplateid',
                          'teumplateid', 'templatenid', 'templategid', 'templateyd', 'temphateid', 'templwteid',
                          'templaweid', 'twmplateid', 'templatzid', 'teamplateid', 'templfteid', 'tcemplateid',
                          'templgateid', 'templanteid', 'templateuid', 'tempnlateid', 'templateidb', 'templateod',
                          'templateibd', 'templateil', 'temxplateid', 'dtemplateid', 'templateiod', 'tzemplateid',
                          'templadeid', 'templfateid', 'temrplateid', 'templateidf', 'temnplateid', 'templateijd',
                          'templatgid', 'tempjateid', 'templbateid', 'yemplateid', 'templateipd', 'uemplateid',
                          'memplateid', 'tempqlateid', 'tempolateid', 'templaeteid', 'templatekd', 'temeplateid',
                          'tesmplateid', 'tempkateid', 'tedmplateid', 'tgemplateid', 'tkemplateid', 'templateidx',
                          'otemplateid', 'templatkeid', 'tlmplateid', 'tkmplateid', 'templatuid', 'templateidj',
                          'templateidi', 'templajteid', 'templatedid', 'tempflateid', 'temslateid', 'templateii',
                          'templatewd', 'templatqeid', 'temdlateid', 'ltemplateid', 'templateide', 'teomplateid',
                          'tempslateid', 'templateild', 'tempnateid', 'templathid', 'stemplateid', 'temmplateid',
                          'templaaeid', 'templmteid', 'templatueid', 'templateqd', 'templqteid', 'templatveid',
                          'itemplateid', 'templateidl', 'tefmplateid', 'templeateid', 'tempjlateid', 'temoplateid',
                          'tekmplateid', 'templateidm', 'templateidk', 'templnateid', 'tewplateid', 'twemplateid',
                          'telplateid', 'tempulateid', 'templafeid', 'templateiq', 'ytemplateid', 'templsteid',
                          'toemplateid', 'templatecid', 'templjateid', 'templzateid', 'temqplateid', 'temhlateid',
                          'tpemplateid', 'templaxteid', 'xtemplateid', 'tnemplateid', 'templapeid', 'tempcateid',
                          'tetmplateid', 'tempzlateid', 'tempdateid', 'tebplateid', 'wemplateid', 'templaoeid',
                          '4emplateid', '5emplateid', '6emplateid', '$emplateid', '%emplateid', '^emplateid',
                          't4mplateid', 't3mplateid', 't2mplateid', 't$mplateid', 't#mplateid', 't@mplateid',
                          'te,plateid', 'te<plateid', 'tem9lateid', 'tem0lateid', 'tem-lateid', 'tem[lateid',
                          'tem]lateid', 'tem;lateid', 'tem(lateid', 'tem)lateid', 'tem_lateid', 'tem=lateid',
                          'tem+lateid', 'tem{lateid', 'tem}lateid', 'tem:lateid', 'temp;ateid', 'temp/ateid',
                          'temp.ateid', 'temp,ateid', 'temp?ateid', 'temp>ateid', 'temp<ateid', 'templa4eid',
                          'templa5eid', 'templa6eid', 'templa$eid', 'templa%eid', 'templa^eid', 'templat4id',
                          'templat3id', 'templat2id', 'templat$id', 'templat#id', 'templat@id', 'template7d',
                          'template8d', 'template9d', 'template&d', 'template*d', 'template(d', '/bbtid',
                          '/bbtemplateid', '/wextid', '/templateid', 'bbseavrch', 'bbslarch', 'bbsefrch', 'bbseorch',
                          'bbsearh', 'bcbsearch', 'bbsearc', 'bbsearhc', 'bbseargh', 'bbsecarch', 'bbserch', 'bbsearoh',
                          'bbsegrch', 'bbserach', 'bbqsearch', 'bxbsearch', 'bbearch', 'bbsearwch',
                          'bbsearcq', 'bbuearch', 'bbiearch', 'ibsearch', 'bsearch', 'bbsqarch', 'bbsaerch', 'bbseprch',
                          'bbseaxrch', 'bbsarch', 'bbseacrh', 'btsearch', 'bbfsearch', 'bbsearchq', 'jbsearch',
                          'bsbearch', 'obsearch', 'bbseach', 'bbseaerch', 'bbseerch', 'bbsfearch', 'bbesarch',
                          'bbmsearch', 'bbsefarch', 'bwbsearch', 'bbdearch', 'bbsyarch', 'bbselrch', 'bhsearch',
                          'bbseadch', 'bbseaqch', 'bbserarch', 'bbrsearch', 'bnbsearch', 'bbsearcch',
                          'bbsearcht', 'bbseasch', 'bbtsearch', 'bbsejrch', 'bbsmarch', 'zbsearch', 'bbsetrch',
                          'bysearch', 'bbseatch', 'bbxsearch', 'bbsearcp', 'bbsearcrh', 'bbseazrch', 'bbsearchc',
                          'bbsearzh', 'bbsearcjh', 'bbsewrch', 'lbsearch', 'blbsearch', 'bbssarch', 'bbseaqrch',
                          'kbbsearch', 'bbsaearch', 'bbsoearch', 'bbsearcx', 'bbsearcv', 'bbsparch', 'bbseaich',
                          'bbsearcdh', 'bbsearchk', 'bgbsearch', 'bbsearrch', 'bbsehrch', 'wbsearch', 'bbsevarch',
                          'bbsearsch', 'bbsearchn', 'bbsesarch', 'bbsbarch', 'bbsearcn', 'nbbsearch', 'bbsearchz',
                          'bbsearcs', 'cbbsearch', 'bbseabch', 'bbsgarch', 'bqbsearch', 'bbsearcd', 'fbsearch',
                          'bfsearch', 'bbsearchr', 'bbseaach', 'bbsearmh', 'bbsearchh', 'bbsearcph', 'bbsearcfh',
                          'bbsearfch', 'bbcsearch', 'bbseaoch', 'bbseirch', 'bbslearch', 'bbsearchg', 'bvsearch',
                          'bbseaarch', 'bbsearcyh', 'bbsearcr', 'bbsearech', 'bbsharch', 'bbjearch', 'bbsfarch',
                          'bbsekrch', 'bbbsearch', 'tbsearch', 'bbsearchw', 'bbsearchx', 'bkbsearch', 'bbselarch',
                          'bboearch', 'bbsetarch', 'bbsearsh', 'bbseabrch', 'zbbsearch', 'bbseaprch', 'bcsearch',
                          'bbsearuh', 'bbsearbch', 'bbpearch', 'bbsearcxh', 'bjsearch', 'bbseearch', 'bbsewarch',
                          'bbsearfh', 'bybsearch', 'bbseamrch', 'bbshearch', 'bbseafch', 'bbseagrch', 'bbstarch',
                          'bsbsearch', 'vbsearch', 'bbsuearch', 'bbzsearch', 'bbsearih', 'bbsealch', 'bbsuarch',
                          'bbnearch', 'bbsearchm', 'bbsekarch', 'bbseqrch', 'bbsegarch', 'bbseuarch', 'bbsearcvh',
                          'bbseharch', 'bbsearcy', 'bvbsearch', 'bbsemrch', 'bbsearclh', 'bbcearch', 'bbkearch',
                          'bbsearrh', 'bbsearcoh', 'kbsearch', 'bbqearch', 'mbsearch', 'bbseaech', 'bbsearchv',
                          'bdsearch', 'nbsearch', 'bbsearoch', 'bbseadrch', 'bbvearch', 'bbsearach', 'bbsearnch',
                          'bbusearch', 'bbsexrch', 'bbsearcl', 'bbsearjch', 'obbsearch', 'bbskearch', 'bobsearch',
                          'bbseardh', 'bbsdearch', 'sbsearch', 'sbbsearch', 'bbseauch', 'bqsearch', 'bbrearch',
                          'bbszearch', 'brsearch', 'bbsjarch', 'bbseapch', 'bbssearch', 'bbsearxh', 'bbsyearch',
                          'bbsearckh', 'bbvsearch', 'bbseaych', 'pbbsearch', 'bbsearchb', 'bbsedrch', 'bbseairch',
                          'bbsearlh', 'bbsearci', 'bbseazch', 'bbseparch', 'bbsenrch', 'bbsearcbh', 'bbsevrch',
                          'ubbsearch', 'bbsearche', 'bbsearkch', 'bbseawrch', 'bbseardch', 'vbbsearch', 'bwsearch',
                          'bbasearch', 'bbsearcf', 'bbseaorch', 'bbsearct', 'bbseartch', 'bbsearck', 'bbsezrch',
                          'bbsearcc', 'hbsearch', 'bbsearchl', 'bbseqarch', 'bisearch', 'bbesearch', 'bksearch',
                          'bbxearch', 'bbpsearch', 'bbseyrch', 'bbswearch', 'bblearch', 'bebsearch', 'bbsearcg',
                          'bfbsearch', 'bbsaarch', 'rbbsearch', 'bbsvarch', 'bhbsearch', 'bbfearch', 'bmsearch',
                          'bbseafrch', 'babsearch', 'bxsearch', 'bbjsearch', 'bbseurch', 'bbsearcah', 'bzbsearch',
                          'bbsqearch', 'bbsearmch', 'bbserrch', 'bbsearpch', 'ubsearch', 'bdbsearch', 'bbsearnh',
                          'bbsearcho', 'hbbsearch', 'busearch', 'bbeearch', 'bbsearyh', 'bbsearcha', 'bbisearch',
                          'bbstearch', 'bbsearcu', 'bbskarch', 'absearch', 'qbbsearch', 'bbsearcb', 'bbsearvh',
                          'bbsearuch', 'bbsjearch', 'bbsearvch', 'brbsearch', 'cbsearch', 'bbsearcmh', 'bbsearcm',
                          'bibsearch', 'bbsxearch', 'bubsearch', 'bbscarch', 'xbbsearch', 'bbsearcw', 'bbaearch',
                          'abbsearch', 'bbsearchd', 'bbsearbh', 'bbsebrch', 'bbzearch', 'bbseajrch', 'bbszarch',
                          'gbsearch', 'bbsearth', 'bbsearqh', 'bbsearlch', 'bbseahch', 'bbsdarch', 'bbsvearch',
                          'bbsbearch', 'bbsearchf', 'bbsezarch', 'bbwsearch', 'bbsiearch', 'bbseagch', 'bbsgearch',
                          'bbsearqch', 'bpsearch', 'bbsrearch', 'bbsearah', 'ibbsearch', 'bbsedarch',
                          'bbsesrch', 'bbsearchi', 'ebsearch', 'bmbsearch', 'btbsearch', 'bbspearch', 'bbscearch',
                          'wbbsearch', 'bbsearcwh', 'bbsearchu', 'bbsearich', 'bosearch', 'bbsecrch', 'bbseakch',
                          'bbsearcih', 'bbsearchj', 'bbmearch', 'bbosearch', 'bbseamch', 'bbsearczh', 'bbseayrch',
                          'dbbsearch', 'bbseaxch', 'bbseacrch', 'bbsearcz', 'bbwearch', 'bssearch', 'gbbsearch',
                          'bnsearch', 'bbsearcgh', 'bbsearjh', 'bbsearhch', 'bbsemarch', 'bbsoarch', 'bbseanch',
                          'bjbsearch', 'bbsejarch', 'qbsearch', 'ybsearch', 'basearch', 'bbseyarch', 'bbsearca',
                          'bbsealrch', 'xbsearch', 'bbsearph', 'bbsmearch', 'bbswarch', 'bbseasrch', 'bbseanrch',
                          'bbsearych', 'bbseaurch', 'bbksearch', 'bbseahrch', 'bbsearchs', 'bbsearhh', 'bbseakrch',
                          'bbsearcj', 'bbseatrch', 'bbsxarch', 'bbsearcnh', 'bbseareh', 'bbsnarch', 'bblsearch',
                          'bbbearch', 'bbnsearch', 'bbsexarch', 'bbsearkh', 'bpbsearch', 'bbseajch', 'bbdsearch',
                          'bgsearch', 'bbsearcsh', 'bbsearchp', 'bbsearxch', 'mbbsearch', 'bbtearch', 'bbsenarch',
                          'bbsearceh', 'bbsiarch', 'bbysearch', 'bbseacch', 'bbyearch', 'dbsearch', 'bbsearzch',
                          'bbsearchy', 'fbbsearch', 'bbsearcqh', 'bbseiarch', 'ybbsearch', 'bbseavch', 'blsearch',
                          'tbbsearch', 'bbhearch', 'bbsebarch', 'bbsearce', 'bbsearwh', 'bbsnearch', 'pbsearch',
                          'bbseawch', 'bzsearch', 'jbbsearch', 'ebbsearch', 'bbsearco', 'bbseargch', 'bbsearcth',
                          'bbgsearch', 'lbbsearch', 'bbsearcuh', 'bbhsearch', 'bbgearch', 'bbseoarch', 'bbsrarch',
                          'bbs4arch', 'bbs3arch', 'bbs2arch', 'bbs$arch', 'bbs#arch', 'bbs@arch', 'bbsea3ch',
                          'bbsea4ch', 'bbsea5ch', 'bbsea#ch', 'bbsea$ch', 'bbsea%ch', '/bbsearch', 'search', '/search'],
                 extras={'emoji': "WEX_HeroToken_Water", "args": {'input': 'The name/template id to find'},
                         "dev": False},
                 brief="Finds items in Battle Breakers",
                 description="This command finds items in Battle Breakers to help translate between names and Template IDs.")
    async def bb_tid(self, ctx, *, input_string=None):
        """
        This function is the entry point for the bbtid command when called traditionally

        Args:
            ctx: The context of the command.
            input_string: The input string to translate.
        """
        await self.bbtemplateid_command(ctx, input_string)

    @slash_command(
        name="bbsearch",
        description="Translates between names and Template IDs for Battle Breakers",
        guild_ids=stw.guild_ids,
    )
    async def slashbbtid(
            self,
            ctx: discord.ApplicationContext,
            input_string: Option(
                description="The name/template id to translate.",
                required=True,
            ) = "",
    ):
        """
        This function is the entry point for the playtime command when called via slash commands

        Args:
            ctx: The context of the slash command.
            input_string: The input string to translate.
        """
        await self.bbtemplateid_command(ctx, input_string)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(BBTID(client))

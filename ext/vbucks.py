"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the vbucks command. Displays total v-bucks count, breakdown + x-ray tickets
"""

import asyncio
import orjson

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


class Vbucks(ext.Cog):
    """
    Cog for the vbucks command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.

        Returns:
            True if an error is found, False otherwise.
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "vbucks", acc_name, error_code,
                                                       verbiage_action="get V-Bucks info")
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def vbuck_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the vbucks command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the account.
            auth_opt_out: Whether the user has opted out of auth.

        Returns:
            None
        """
        vbucc_colour = self.client.colours["vbuck_blue"]

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "vbucks", authcode, auth_opt_out, True)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except IndexError:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # get common core profile
        core_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_core")
        core_json_response = orjson.loads(await core_request.read())
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, core_json_response, auth_info, final_embeds):
            return

        vbucks = await asyncio.gather(
            asyncio.to_thread(stw.extract_profile_item, profile_json=orjson.loads(await core_request.read()),
                              item_string="Currency:Mtx"))

        # fetch x-ray ticket count TODO: can this be done in the same request as the vbucks?
        stw_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="stw")
        stw_json_response = orjson.loads(await stw_request.read())

        # check for le error code
        error_check = await self.check_errors(ctx, stw_json_response, auth_info, final_embeds)
        if error_check:
            return

        xray = await asyncio.gather(
            asyncio.to_thread(stw.extract_profile_item, profile_json=orjson.loads(await stw_request.read()),
                              item_string="AccountResource:currency_xrayllama"))

        # fetch vbucks total
        vbucks_total = await stw.calculate_vbucks(vbucks)

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, stw.I18n.get("vbucks.embed.title", desired_lang),
                                            "vbuck_book"),
            description=f"\u200b\n{stw.I18n.get('vbucks.embed.description.total', desired_lang, vbucks_total)}\u200b\n",
            colour=vbucc_colour)

        # add entry for each platform detected
        if vbucks_total != 0:
            for item in vbucks:
                for attr, val in item.items():
                    name, emoji = await stw.resolve_vbuck_source(val["templateId"])
                    embed.description += f"{self.emojis[emoji]} {name}: {val['quantity']}\n"
        else:
            embed.description += f"{stw.I18n.get('vbucks.embed.description.zerovbucks', desired_lang, self.emojis['spongebob'], self.emojis['megamind'])}\n"

        # add entry for x-ray if detected
        if xray:
            for item in xray:
                for attr, val in item.items():
                    embed.description += f"\u200b\n{stw.I18n.get('vbucks.embed.description.xray', desired_lang, self.emojis['xray'], val['quantity'])}\n"

        embed.description += "\u200b"

        if vbucks_total != 0:
            embed = await stw.set_thumbnail(self.client, embed, "vbuck_book")
        else:
            embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        return

    @ext.slash_command(name='vbucks', name_localizations=stw.I18n.construct_slash_dict("vbucks.slash.name"),
                       description='View your V-Bucks and X-Ray Tickets balance (authentication required)',
                       description_localizations=stw.I18n.construct_slash_dict("vbucks.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashvbucks(self, ctx: discord.ApplicationContext,
                          token: Option(str,
                                        description="Your Epic Games authcode. Required unless you have an active "
                                                    "session.",
                                        description_localizations=stw.I18n.construct_slash_dict(
                                            "generic.slash.token")) = "",
                          auth_opt_out: Option(bool, description="Opt out of starting an authentication session",
                                               description_localizations=stw.I18n.construct_slash_dict(
                                                   "generic.slash.optout")) = False):
        """
        This function is the entry point for the vbucks command when called via slash

        Args:
            ctx: The context of the command.
            token: The authcode to use for authentication.
            auth_opt_out: Whether to opt out of starting an authentication session.
        """
        await self.vbuck_command(ctx, token, not auth_opt_out)

    @ext.command(name='vbucks',
                 aliases=['v', 'vb', 'vbuck', 'vbucc', 'v-bucks', 'balance', 'bucks', 'vucks', 'vbcks', 'vbuks',
                          'vbucs', 'vvbucks', 'vbbucks', 'vbuucks', 'vbuccks', 'vbuckks', 'vbuckss', 'bvucks', 'vubcks',
                          'vbcuks', 'vbukcs', 'vbucsk', 'cbucks', 'fbucks', 'gbucks', 'bbucks', 'vvucks', 'vgucks',
                          'vhucks', 'vnucks', 'vbycks', 'vb7cks', 'vb8cks', 'vbicks', 'vbkcks', 'vbjcks', 'vbhcks',
                          'vbuxks', 'vbudks', 'vbufks', 'vbuvks', 'vbucjs', 'vbucis', 'vbucos', 'vbucls', 'vbucms',
                          'vbucka', 'vbuckw', 'vbucke', 'vbuckd', 'vbuckx', 'vbuckz', 'cvbucks', 'vcbucks', 'fvbucks',
                          'vfbucks', 'gvbucks', 'vgbucks', 'bvbucks', 'vbvucks', 'vbgucks', 'vhbucks', 'vbhucks',
                          'vnbucks', 'vbnucks', 'vbyucks', 'vbuycks', 'vb7ucks', 'vbu7cks', 'vb8ucks', 'vbu8cks',
                          'vbiucks', 'vbuicks', 'vbkucks', 'vbukcks', 'vbjucks', 'vbujcks', 'vbuhcks', 'vbuxcks',
                          'vbucxks', 'vbudcks', 'vbucdks', 'vbufcks', 'vbucfks', 'vbuvcks', 'vbucvks', 'vbucjks',
                          'vbuckjs', 'vbuciks', 'vbuckis', 'vbucoks', 'vbuckos', 'vbuclks', 'vbuckls', 'vbucmks',
                          'vbuckms', 'vbuckas', 'vbucksa', 'vbuckws', 'vbucksw', 'vbuckes', 'vbuckse', 'vbuckds',
                          'vbucksd', 'vbuckxs', 'vbucksx', 'vbuckzs', 'vbucksz', 'buck', 'vuck', 'vbck', 'vbuk', 'vbuc',
                          'vvbuck', 'vbbuck', 'vbuuck', 'vbucck', 'vbuckk', 'bvuck', 'vubck', 'vbcuk', 'vbukc', 'cbuck',
                          'fbuck', 'gbuck', 'bbuck', 'vvuck', 'vguck', 'vhuck', 'vnuck', 'vbyck', 'vb7ck', 'vb8ck',
                          'vbick', 'vbkck', 'vbjck', 'vbhck', 'vbuxk', 'vbudk', 'vbufk', 'vbuvk', 'vbucj', 'vbuci',
                          'vbuco', 'vbucl', 'vbucm', 'cvbuck', 'vcbuck', 'fvbuck', 'vfbuck', 'gvbuck', 'vgbuck',
                          'bvbuck', 'vbvuck', 'vbguck', 'vhbuck', 'vbhuck', 'vnbuck', 'vbnuck', 'vbyuck', 'vbuyck',
                          'vb7uck', 'vbu7ck', 'vb8uck', 'vbu8ck', 'vbiuck', 'vbuick', 'vbkuck', 'vbukck', 'vbjuck',
                          'vbujck', 'vbuhck', 'vbuxck', 'vbucxk', 'vbudck', 'vbucdk', 'vbufck', 'vbucfk', 'vbuvck',
                          'vbucvk', 'vbucjk', 'vbuckj', 'vbucik', 'vbucki', 'vbucok', 'vbucko', 'vbuclk', 'vbuckl',
                          'vbucmk', 'vbuckm', '-bucks', 'v-ucks', 'v-bcks', 'v-buks', 'v-bucs', 'v-buck', 'vv-bucks',
                          'v--bucks', 'v-bbucks', 'v-buucks', 'v-buccks', 'v-buckks', 'v-buckss', '-vbucks', 'vb-ucks',
                          'v-ubcks', 'v-bcuks', 'v-bukcs', 'v-bucsk', 'c-bucks', 'f-bucks', 'g-bucks', 'b-bucks',
                          'v-vucks', 'v-gucks', 'v-hucks', 'v-nucks', 'v-bycks', 'v-b7cks', 'v-b8cks', 'v-bicks',
                          'v-bkcks', 'v-bjcks', 'v-bhcks', 'v-buxks', 'v-budks', 'v-bufks', 'v-buvks', 'v-bucjs',
                          'v-bucis', 'v-bucos', 'v-bucls', 'v-bucms', 'v-bucka', 'v-buckw', 'v-bucke', 'v-buckd',
                          'v-buckx', 'v-buckz', 'cv-bucks', 'vc-bucks', 'fv-bucks', 'vf-bucks', 'gv-bucks', 'vg-bucks',
                          'bv-bucks', 'vb-bucks', 'v-vbucks', 'v-bvucks', 'v-gbucks', 'v-bgucks', 'v-hbucks',
                          'v-bhucks', 'v-nbucks', 'v-bnucks', 'v-byucks', 'v-buycks', 'v-b7ucks', 'v-bu7cks',
                          'v-b8ucks', 'v-bu8cks', 'v-biucks', 'v-buicks', 'v-bkucks', 'v-bukcks', 'v-bjucks',
                          'v-bujcks', 'v-buhcks', 'v-buxcks', 'v-bucxks', 'v-budcks', 'v-bucdks', 'v-bufcks',
                          'v-bucfks', 'v-buvcks', 'v-bucvks', 'v-bucjks', 'v-buckjs', 'v-buciks', 'v-buckis',
                          'v-bucoks', 'v-buckos', 'v-buclks', 'v-buckls', 'v-bucmks', 'v-buckms', 'v-buckas',
                          'v-bucksa', 'v-buckws', 'v-bucksw', 'v-buckes', 'v-buckse', 'v-buckds', 'v-bucksd',
                          'v-buckxs', 'v-bucksx', 'v-buckzs', 'v-bucksz', 'alance', 'blance', 'baance', 'balnce',
                          'balace', 'balane', 'balanc', 'bbalance', 'baalance', 'ballance', 'balaance', 'balannce',
                          'balancce', 'balancee', 'ablance', 'blaance', 'baalnce', 'balnace', 'balacne', 'balanec',
                          'valance', 'galance', 'halance', 'nalance', 'bqlance', 'bwlance', 'bslance', 'bxlance',
                          'bzlance', 'bakance', 'baoance', 'bapance', 'balqnce', 'balwnce', 'balsnce', 'balxnce',
                          'balznce', 'balabce', 'balahce', 'balajce', 'balamce', 'balanxe', 'balande', 'balanfe',
                          'balanve', 'balancw', 'balanc3', 'balanc4', 'balancr', 'balancf', 'balancd', 'balancs',
                          'vbalance', 'bvalance', 'gbalance', 'bgalance', 'hbalance', 'bhalance', 'nbalance',
                          'bnalance', 'bqalance', 'baqlance', 'bwalance', 'bawlance', 'bsalance', 'baslance',
                          'bxalance', 'baxlance', 'bzalance', 'bazlance', 'baklance', 'balkance', 'baolance',
                          'baloance', 'baplance', 'balpance', 'balqance', 'balaqnce', 'balwance', 'balawnce',
                          'balsance', 'balasnce', 'balxance', 'balaxnce', 'balzance', 'balaznce', 'balabnce',
                          'balanbce', 'balahnce', 'balanhce', 'balajnce', 'balanjce', 'balamnce', 'balanmce',
                          'balanxce', 'balancxe', 'balandce', 'balancde', 'balanfce', 'balancfe', 'balanvce',
                          'balancve', 'balancwe', 'balancew', 'balanc3e', 'balance3', 'balanc4e', 'balance4',
                          'balancre', 'balancer', 'balancef', 'balanced', 'balancse', 'balances', '/v', '/vb',
                          '/vbucks', '/v-bucks', 'chucks', '/chucks', '/balance'],
                 extras={'emoji': "vbuck_book", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": False},
                 brief="View your V-Bucks and X-Ray Tickets balance (authentication required)",
                 description=(
                         "This command displays your total V-Bucks, provide a breakdown on the source(s) of those "
                         "V-Bucks, and additionally display how many X-Ray tickets you have. You must be "
                         "authenticated to use this command."))
    async def vbucks(self, ctx, authcode='', optout=None):
        """
        This function is the entry point for the vbucks command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode provided by the user
            optout: Any text provided will opt the user out of starting an authentication session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.vbuck_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Vbucks(client))

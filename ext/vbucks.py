import asyncio

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


# cog for the daily command.
class Vbucks(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, slash):
        try:
            # general error
            error_code = public_json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "vbucks", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return True
        except:
            # no error
            return False

    async def vbuck_command(self, ctx, slash, authcode, auth_opt_out):
        vbucc_colour = self.client.colours["vbuck_blue"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "vbucks", authcode, slash, auth_opt_out,
                                                         True)
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # get common core profile
        core_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_core")
        core_json_response = await core_request.json()
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if await self.check_errors(ctx, core_json_response, auth_info, final_embeds, slash):
            return

        vbucks = await asyncio.gather(asyncio.to_thread(stw.extract_item, profile_json=await core_request.json(),
                                                        item_string="Currency:Mtx"))

        # fetch x-ray ticket count
        stw_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="stw")
        stw_json_response = await stw_request.json()

        # check for le error code
        error_check = await self.check_errors(ctx, stw_json_response, auth_info, final_embeds, slash)
        if error_check:
            return

        xray = await asyncio.gather(asyncio.to_thread(stw.extract_item, profile_json=await stw_request.json(),
                                                      item_string="AccountResource:currency_xrayllama"))

        # fetch vbucks total
        vbucks_total = await stw.calculate_vbucks(vbucks)

        # With all info extracted, create the output
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "V-Bucks", "vbuck_book"),
                              description=f"\u200b\n**Total V-Bucks: {vbucks_total}**\u200b\n",
                              colour=vbucc_colour)

        # add entry for each platform detected
        if vbucks_total != 0:
            for item in vbucks:
                for attr, val in item.items():
                    name, emoji = await stw.resolve_vbuck_source(val["templateId"])
                    embed.description += f"""{self.emojis[emoji]} {name}: {val["quantity"]}\n"""
        else:
            embed.description += f"""{self.emojis["spongebob"]} No V-Bucks? {self.emojis["megamind"]}\n"""

        # add entry for x-ray if detected
        if xray:
            for item in xray:
                for attr, val in item.items():
                    embed.description += f"""\u200b\n{self.emojis["xray"]} X-Ray Tickets: {val["quantity"]}\n"""

        embed.description += "\u200b"

        if vbucks_total != 0:
            embed = await stw.set_thumbnail(self.client, embed, "vbuck_book")
        else:
            embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        return

    @ext.slash_command(name='vbucks',
                       description='Lets you view your V-Bucks balance',
                       guild_ids=stw.guild_ids)
    async def slashvbucks(self, ctx: discord.ApplicationContext,
                          token: Option(str,
                                        "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                          auth_opt_out: Option(bool, "Opt Out of Authentication session") = False, ):
        await self.vbuck_command(ctx, True, token, not auth_opt_out)

    @ext.command(name='vbucks',
                 aliases=['v', 'vb', 'vbuck', 'vbuc', 'vbucc', 'v-bucks', 'balance'],
                 extras={'emoji': "vbuck_book", "args": {
                     'authcode': 'The authcode to start an authentication session with if one does not exist, if an auth session already exists this argument is optional (Optional)',
                     'opt-out': 'Any value inputted into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
                 brief="View your V-Bucks balance (auth req.)",
                 description="""This command allows you to view your V-Bucks balance and breakdown accross platforms, you must be authenticated to use this command.
                \u200b
                """)
    async def vbucks(self, ctx, authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.vbuck_command(ctx, False, authcode, not optout)


def setup(client):
    client.add_cog(Vbucks(client))

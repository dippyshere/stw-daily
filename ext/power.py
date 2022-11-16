import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


# cog for the daily command.
class Power(ext.Cog):

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

    async def power_command(self, ctx, slash, authcode, auth_opt_out):
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
        stw_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="stw")
        stw_json_response = await stw_request.json()
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # stw2_request = await stw.profile_request(self.client, "llamas", auth_info[1], profile_id="stw")
        # stw2_json_response = await stw2_request.json()
        # print(stw2_json_response)

        # stw3_request = await stw.profile_request(self.client, "refresh_expeditions", auth_info[1], profile_id="stw")
        # stw3_json_response = await stw3_request.json()
        # print(stw3_json_response)

        # check for le error code
        if await self.check_errors(ctx, stw_json_response, auth_info, final_embeds, slash):
            return

        power_level, total, total_stats = stw.calculate_homebase_rating(stw_json_response)

        # With all info extracted, create the output
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Power Level", "power_level"),
                              description=f"\u200b\n**Your powerlevel is: {self.emojis['power_level']}{power_level}**\u200b\n"
                                          f"\u200b\n**Total FORT stats: {self.emojis['power_level']}{total}**\u200b\n"
                                          f"\u200b\n**Fortitude: {self.emojis['fortitude']} {total_stats['fortitude']}**\u200b\n"
                                          f"\u200b\n**Offense: {self.emojis['offense']} {total_stats['offense']}**\u200b\n"
                                          f"\u200b\n**Resistance: {self.emojis['resistance']} {total_stats['resistance']}**\u200b\n"
                                          f"\u200b\n**Technology: {self.emojis['technology']} {total_stats['technology']}**\u200b\n",
                              colour=vbucc_colour)

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        return

    @ext.slash_command(name='power',
                       description='View your Power level (authentication required)',
                       guild_ids=stw.guild_ids)
    async def slashpower(self, ctx: discord.ApplicationContext,
                         token: Option(str,
                                       "Your Epic Games authcode. Required unless you have an active session.") = "",
                         auth_opt_out: Option(bool, "Opt out of starting an authentication session") = False, ):
        await self.power_command(ctx, True, token, not auth_opt_out)

    @ext.command(name='power',
                 aliases=['pow', 'powerlevel', 'rating', 'level', 'pwr'],
                 extras={'emoji': "power_level", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": False},
                 brief="View your Power level (authentication required)",
                 description="""This command allows you to view the power level of your STW homebase, you must be authenticated to use this command for now.
                \u200b
                """)
    async def power(self, ctx, authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.power_command(ctx, False, authcode, not optout)


def setup(client):
    client.add_cog(Power(client))

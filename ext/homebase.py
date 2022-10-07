import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


# cog for the daily command.
class Homebase(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def hbrename_command(self, ctx, slash, authcode, auth_opt_out, name):
        error_colour = self.client.colours["error_red"]
        succ_colour = self.client.colours["success_green"]
        yellow = self.client.colours["warning_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "homebase", authcode, slash, auth_opt_out,
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

        public_request = await stw.profile_request(self.client, "query_public", auth_info[1], profile_id="common_public")
        public_json_response = await public_request.json()
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        current = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["homebase_name"]
        homebase_colour = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_color"]
        homebase_icon = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_icon"]

        # set homebase name
        # request = await stw.profile_request(self.client, "homebase", auth_info[1], profile_id="common", data={"homebaseName": f"{name}"})
        # json_response = await request.json()

        # check for le error code
        try:
            error_code = json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            # daily_feedback = json_response["notifications"]

            # for notification in daily_feedback:
            #     if notification["type"] == "daily_rewards":
            #         daily_feedback = notification
            #         break

            # day = daily_feedback["daysLoggedIn"]

            # try:
            #     self.client.temp_auth[ctx.author.id]["day"] = day
            # except:
            #     pass

            # items = daily_feedback["items"]
            # Empty name should fetch current name
            if name == "":
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, "Homebase Name", "teammatexpboost"), description=
                    f"""\u200b
                **Your current Homebase name is:**
                ```{current}```
                \u200b
                """, colour=yellow)
                # embed = await stw.set_thumbnail(self.client, embed, "warn")
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/banners/{homebase_icon}/icon.png")
                embed = await stw.add_requested_footer(ctx, embed)
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return

            # Initialise the claimed embed
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                                  description="\u200b",
                                  colour=succ_colour)

            embed.add_field(name=f'Changed Homebase name from:', value=f"```{current}```\u200b",
                            inline=False)

            embed.add_field(name=f'To:', value=f"```{name}```\u200b",
                            inline=False)

            embed = await stw.set_thumbnail(self.client, embed, "check")
            # set embed thumbnail
            # embed.set_thumbnail(url=f"https://fortnite-api.com/images/banners/{homebase_icon}/icon.png")
            embed = await stw.add_requested_footer(ctx, embed)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

    @ext.slash_command(name='homebase',
                       description='Let\'s you change your STW Homebase name, or view your current Homebase name',
                       guild_ids=stw.guild_ids)
    async def slashhbrename(self, ctx: discord.ApplicationContext,
                            name: Option(str, "The new name for your Homebase; to view current, leave blank") = "",
                            token: Option(str,
                                          "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                            auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
        await self.hbrename_command(ctx, True, token, not auth_opt_out, name)

    @ext.command(name='hbrename',
                 aliases=['homebase', 'hbrn', 'rename', 'changehomebase'],
                 extras={'emoji': "teammatexpboost", "args": {
                     'name': 'The new name for your Homebase, if left blank it will give you your current Homebase name (Optional)',
                     'authcode': 'The authcode to start an authentication session with if one does not exist, if an auth session already exists this argument is optional (Optional)',
                     'opt-out': 'Any value inputted into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
                 brief="Let's you change your STW Homebase name",
                 description="""This command allows you to change the name of your Homebase in Save The World, you must be authenticated to use this command.
                \u200b
                ⦾ There are limitations on what your Homebase name can be, placeholer ^[0-9a-zA-Z '\\-._~]{1,16}$
                """)
    async def hbrename(self, ctx, authcode='', optout=None, name=''):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.hbrename_command(ctx, False, authcode, not optout, name)


def setup(client):
    client.add_cog(Homebase(client))

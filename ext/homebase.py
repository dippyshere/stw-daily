import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


# cog for the daily command.
class Homebase(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, slash):
        try:
            error_code = public_json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", acc_name, error_code, support_url)
            final_embeds.append(embed)
            return await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            return False

    async def hbrename_command(self, ctx, slash, name, authcode, auth_opt_out):
        succ_colour = self.client.colours["success_green"]
        white = self.client.colours["auth_white"]

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

        # get public info about current Homebase name
        public_request = await stw.profile_request(self.client, "query_public", auth_info[1], profile_id="common_public")
        public_json_response = await public_request.json()
        # ROOT.profileChanges[0].profile.stats.attributes.homebase_name

        # check for le error code
        if not await self.check_errors(ctx, public_json_response, auth_info, final_embeds, slash):
            return

        # extract info from response
        current = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["homebase_name"]
        homebase_colour = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_color"]
        homebase_icon = public_json_response["profileChanges"][0]["profile"]["stats"]["attributes"]["banner_icon"]

        # Empty name should fetch current name
        if name == "":
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, "Homebase Name", "storm_shield"), description=
                f"""\u200b
            **Your current Homebase name is:**
            ```{current}```
            \u200b
            """, colour=white)
            # embed = await stw.set_thumbnail(self.client, embed, "warn")
            # set thumbnail to user's banner
            # TODO: screen filter banner and change to user's colour
            embed.set_thumbnail(url=f"https://fortnite-api.com/images/banners/{homebase_icon}/icon.png")
            embed = await stw.add_requested_footer(ctx, embed)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

        # failing this check means the name has problems thus we cannot accept it
        if not await stw.is_legal_homebase_name(name):
            if name > 16:
                error_code = "errors.stwdaily.homebase_long"
                embed = await stw.post_error_possibilities(ctx, self.client, "homebase", name, error_code,
                                                           self.client.config["support_url"])
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return
            error_code = "errors.stwdaily.homebase_illegal"
            embed = await stw.post_error_possibilities(ctx, self.client, "homebase", name, error_code,
                                                       self.client.config["support_url"])
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

        # wih all checks passed, we may now attempt to change name
        request = await stw.profile_request(self.client, "set_homebase", auth_info[1], profile_id="common_public", data={"homebaseName": f"{name}"})
        json_response = await request.json()
        print(json_response)

        # check for le error code
        if not await self.check_errors(ctx, json_response, auth_info, final_embeds, slash):
            return

        # If passed all checks and changed name, present success embed
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                              description="\u200b",
                              colour=succ_colour)

        embed.add_field(name=f'{self.emojis["broken_heart"]} Changed Homebase name from:', value=f"```{current}```\u200b",
                        inline=False)

        embed.add_field(name=f'{self.emojis["placeholder"]} To:', value=f"```{name}```\u200b",
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
        await self.hbrename_command(ctx, True, name, token, not auth_opt_out)

    @ext.command(name='homebase',
                 aliases=['hbrename', 'hbrn', 'rename', 'changehomebase', 'homebasename', 'hbname', 'hb'],
                 extras={'emoji': "storm_shield", "args": {
                     'name': 'The new name for your Homebase, if left blank it will give you your current Homebase name (Optional)',
                     'authcode': 'The authcode to start an authentication session with if one does not exist, if an auth session already exists this argument is optional (Optional)',
                     'opt-out': 'Any value inputted into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
                 brief="Let's you change your STW Homebase name",
                 description="""This command allows you to change the name of your Homebase in Save The World, you must be authenticated to use this command.
                \u200b
                **Please note there are limitations on what your Homebase name can be:**
                ⦾ It must be between 1-16 characters
                ⦾ It may only contain alphanumerics (0-9, a-z) + additional characters ('\\-._~) + spaces
                ⦾ When entering a name with spaces while not using slash commands, please put "quote marks" around the new name
                ⦾ Support for other languages will be available in the future
                ⦾ Please note that this command is still experimental <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>
                """)
    async def hbrename(self, ctx, name='', authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.hbrename_command(ctx, False, name, authcode, not optout)


def setup(client):
    client.add_cog(Homebase(client))

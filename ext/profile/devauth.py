import asyncio

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw


# cog for the device auth login command.
class ProfileAuth(ext.Cog):

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

    async def devauth_command(self, ctx, slash, authcode, auth_opt_out):
        vbucc_colour = self.client.colours["vbuck_blue"]
        # veebu cc
        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "device", authcode, slash, auth_opt_out,
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

        # hi there :3
        # create device auth
        device_request = await stw.device_request(self.client, "deviceAuth", auth_info[1])
        device_json_response = await device_request.json()

        # # get common core profile
        core_request = await stw.profile_request(self.client, "query", auth_info[1], profile_id="common_core")
        # core_json_response = await core_request.json()
        # # ROOT.profileChanges[0].profile.stats.attributes.homebase_name
        #
        # # check for le error code
        # if await self.check_errors(ctx, core_json_response, auth_info, final_embeds, slash):
        #     return

        # With all info extracted, create the output
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Device auth", "link_acc"),
                              description=f"\u200b\n",
                              colour=vbucc_colour)

        # add entry for each platform detected
        if True:
            embed.description += f"""{self.emojis["checkmark"]} Successfully made device auth idk\n"""
        else:
            embed.description += f"""{self.emojis["spongebob"]} Failed creating device auth\n"""

        embed.description += "\u200b"

        embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        return

    @ext.slash_command(name='deviceauth',
                       description='Test device auth login :D',
                       guild_ids=stw.guild_ids)
    async def slashcreatedev(self, ctx: discord.ApplicationContext,
                             token: Option(str,
                                           "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                             auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
        await self.devauth_command(ctx, True, token, not auth_opt_out)

    @ext.command(name='device',
                 aliases=['devauth', 'dev', 'deviceauth', 'deviceauthcode', 'profileauth', 'proauth'],
                 extras={'emoji': "link_acc", "args": {
                     'authcode': 'The authcode which will be linked to authentication of the currently selected profile, can also be entered later in the process. (Optional)'}},
                 brief="Add permanent authentication to a profile",
                 description="""This command allows you to create a device auth session, which will keep you logged in while utilising the profile which has been linked to the account specified by the device authentication.
                \u200b
                """)
    async def device(self, ctx, authcode=''):
        await self.devauth_command(ctx, False, authcode)


def setup(client):
    client.add_cog(ProfileAuth(client))

    # why do we have auto_trial thing hm i guess i mean it makes sense but seems kinda redundant why not just have one flag thats like auto_trial claimed and grant them auto_claim days
    # there is a lot of redudant data in that json :D but true we could do that
    # just wanted it as a separate thing if we want to stop the trial grant in the future / change it for future users (e.g. default profile for chrissy is 3 months autoclaim, after holiday season its only 1 month) whats digest
    # hi im going to write this here cause ur more likely to read it on discord than here :3
    """

    so i had this idea to sort of make it alot easier to deal with data issues relating to concurrency
    whenever a user say adds data to the database we should have some sort of check to prevent that their new data
    that they've entered wont like really interfere with data that is still being entered
    say some old bit of data to update takes longer than a new bit so the old data would overwrite the new data
    to prevent this i say we add some kind of queue thing? which i've now added as client.processing_queue
    (in reality its not really a queue and more of just a system to check if there is still a "command" 
    to add something to the database in process)
    so my idea is that whenever a user updates their mongodb document their snowflake should be added to this processing_queue
    and while it is in the queue the user will be met with an error message that says soemthing like currently processing account data
    when they try to get their data or update/write to it, this just helps prevent the issue where somehow the user is met with
    old data that they just updated or somehow overwrite their new data with old data 

    tldr;
    new processing_queue system for mongodb is going to be added which helps prevent issues related to concurrency and
    prevents old data from overwriting new data though it does slightly impact the user experience but modern internet
    speed should just easily prevent it from impacting that much

    um wouldnt it be possible to like display the processing embed then just try their action again?

    yes it would be possible to display the processing embed but what about if they like try to read their data while its 
    being updated? it would just read the old data or something? idk lol idk how mongodb works
    ummm mongo pretty fast, but ya i guess we could  hi just idk also was very funny watching you retype eaktiphmalkertymjhlkae4mydtjgak,lertdmhjgnblkoamedtlokhhmablkiortgdjmahlokiryfmjlk oh wait ctrl z exists my question
    do u have any other ideas 

    here are stuff that we need idea for:
    default document when they dont have stuff in mongodb already
        - store in a table thing with their id being their snowflake or something, then try to get _id using snowflake, if not found then create
    how to store their stuff safely (security)
        - um railway will probs not have a static ip so yolo only protection is the username and password stored in env var
    how to store their stuff efficiently (storage)
        - this was probably a github question but
        - i think we should just store their stuff in a table with their id being their snowflake or something, then try to get _id using snowflake, if not found then create
    how to store their stuff in a way that is easy to access (readability)
        - this was probably a github question too idk but
        - i think we should just store their stuff in a table with their id being their snowflake or something, then try to get _id using snowflake, if not found then create
    how to update stuff so that there is no weird merge or overwriting issues
        - im sure its ok but we should probably add some sort of queue system to prevent weird issues ok github
        - no its not okay its never okay
        - 
    features github needs:
        - add a way to add vbucks to their account
        - add a way to add xray tickets to their account
        - add a way to add vbucks to their account
        - add a way to add vbucks to their account
        what github??
    features wii need:
        - easy to access with their snowflake or sumthn idk # we have already achieved this # we need to loop through the entire thing to fetch the value of user_snowflake rather than idk how mongo works frick    why do we need to do that idk how mango works hi
        - stores multiple device auth profiles # yes i also thought of this
        - stores settings for the snowflake # should this be global or per user profile um per profile rather than per server for now
            - per profile as in per snowflake not per device account :D
            - settings only added to mongo if they are changd  from defaults because epic loves to do this :sob:

        so should we just  ugh i dont want to hard code defaults TwT how else can we do it?? 
        :( i guess we havee to rightt atleast can we make a seperate file TwT yeah ofc we dont HAVE to keep stuff out of mongo if it doesnt have its default changed or whatever idk
        its fine if we hard code it as long as we do it outside of the code :thumbs_up: true
        wouldnt it be easier to loop through if it was profile0 profile1 no ok starting from 1 annoys me fine we should limit profiles to 6?
        {
            'user_snowflake': 349076896266452995,
            'profile_0': {
                '_id': 0,
                'friendly_name': 'whos steve jobs? 🤔',
                'stw_daily_data': {
                    'total_times_claimed_manual': 0,
                    'total_times_claimed_auto': 0,
                    'vbucks_claimed': 0,

                    'donation_source': 'none',
                    'donation_tier': 0,

                    'auto_claim': {
                      'days_remaining': 0,
                    },

                    'banned': False,
                    'banned_reason': 'none',
                    'banned_by': 'none',
                    'banned_date': 'none',
                    'banned_duration': 'none',

                    'tos_accepted': False,
                    'tos_accepted_date': 'none',
                    'tos_accepted_version': 'none',


                    'auto_trial': {
                        'eligible': False,
                        'claimed': False,
                        'claimed_date': 'none',
                        'enabled': False,
                        'start_time': 0,
                        'end_time': 0,
                        'vbucks_claimed': 0,
                        'total_times_claimed': 0,
                    },

                    'isServerBoosting': False,
                    'isServerBoostingSince': None,
                    'isServerBoostingUntil': None,
                    'isServerMember': None,
                    'isServerMemberSince': None,
                    'first_claimed': None,

                    // dinner brb tell me what u hve for dinner ttoo even though u already had dinner chicken sumthn

                    # ALRIGHT SO
                    # wanna make like idk get profiles working?
                    # sure idk
                    # hmm ok so
                    # um i think this is most of the data we need
                    # only thing really left to do with this "schema" is uh just stats for the digest and other things per account rather than all chucked into profile0 
                    'settings': {
                        'data_opt_out': False,
                        'upcoming_display': False,
                        'upcoming_display_days': 7, 
                        'display_epic': False,
                        'claim_research': False,
                        'claim_free_llamas': False,
                        'auto_settings': {
                            'enabled': False,
                            'start_time': 0,
                            'end_time': 0,
                            'claim_research': False,
                            'claim_free_llamas': False,
                            'claim_daily': False,
                            'dm_on_claim': False, // disallow if digest is interval <7 (weekly)
                            'digest': {
                                'enabled': False,
                                'interval': 0,
                                'channel': 'none',
                            },
                    },
                    'authentication': {
                        'accountId': 'a1b2c3d4e5f6g7h8i9j0',
                        'deviceId': 'a1b2c3d4e5f6g7h8i9j0',
                        'secret': 'a1b2c3d4e5f6g7h8i9j0',
                        'expires': 'a1b2c3d4e5f6g7h8i9j0'
                    }
                },
                'profile_1': {
                    'id': 1,
                    'friendly_name': 'ligma balls 🤡😂👍',
                    'authentication': {}
                },
        }

        what we already get document by user snowflake like ? hm ok then i see
        use the bongo test command thing it will add new document and anytime u fetch it'll fetch by ur user_snowflake thing
    wow lmao github
    """
    """
    @ext.slash_command(name='addvbucks',
                          description='Lets you add V-Bucks to your account',
                            guild_ids=stw.guild_ids)
    async def slashaddvbucks(self, ctx: discord.ApplicationContext,
                                vbucks: Option(int, "The amount of V-Bucks to add to your account"),
                                source: Option(str, "The source of the V-Bucks"),
                                token: Option(str,
                                                "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                                    auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
            await self.addvbuck_command(ctx, True, vbucks, source, token, not auth_opt_out)
        ":( i dont know how to do this"
    https://preview.redd.it/7wcrh5iiylt91.jpg?width=640&crop=smart&auto=webp&s=5371d507cc1597cbf3075cfb942f3eccd1b110d1
    @ext.slash_command(name='addxray',
                            description='Lets you add X-Ray Tickets to your account',
                            guild_ids=stw.guild_ids)
    async def slashaddxray(self, ctx: discord.ApplicationContext,
                                xray: Option(int, "The amount of X-Ray Tickets to add to your account"),
                                source: Option(str, "The source of the X-Ray Tickets"),
                                token: Option(str,
                                                "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                                    auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
            await self.addxray_command(ctx, True, xray, source, token, not auth_opt_out)
        ":( i dont know how to do this"
    https://preview.redd.it/7wcrh5iiylt91.jpg?width=640&crop=smart&auto=webp&s=5371d507cc1597cbf3075cfb942f3eccd1b110d1
    tickets? like from roblox?
    @ext.slash_command(name='addtickets',
                            description='Lets you add Tickets to your account',
                            guild_ids=stw.guild_ids)
    async def slashaddtickets(self, ctx: discord.ApplicationContext,
                                tickets: Option(int, "The amount of Tickets to add to your account"),
                                source: Option(str, "The source of the Tickets"),
                                token: Option(str,
                                                "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                                    auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
            await self.addtickets_command(ctx, True, tickets, source, token, not auth_opt_out)
        ":( i dont know how to do this"
    """
    """
    https://preview.redd.it/7wcrh5iiylt91.jpg?width=640&crop=smart&auto=webp&s=5371d507cc1597cbf3075cfb942f3eccd1b110d1
    """
    """
    @ext.slash_command(name='addtickets',
                       )()                 :( i dont know how to do this" :()
    github wants vbucks
    thank you
    you are welcome sorry i forgor what githubs questions were
    """

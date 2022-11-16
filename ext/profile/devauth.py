import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw
from ext.profile.bongodb import get_user_document

async def tos_acceptance_embed(client, ctx):
    # TODO: Create proper TOS, Privacy Policy & EULA for this command
    embed_colour = client.colours["profile_lavendar"]
    embed = discord.Embed(title=await stw.add_emoji_title(client, "User Agreement", "pink_link"),
                          description=f"""\u200b
                          
                          **slap**
                          ***slap***
                          ~~grab~~
                          __choke__
                          *shut up*
                          `bitch`
                          ```sex```
                          
                          
                          \u200b""",
                          colour=embed_colour)

    embed = await stw.set_thumbnail(client, embed, "pink_link")
    embed = await stw.add_requested_footer(ctx, embed)
    return embed

async def handle_dev_auth(client, ctx, slash, authcode=None):

    # Retrieve information on the currently selected profile of the user accociated with this ctx

    if from_interaction:
        current_author_id = ctx.user.id
    else:
        current_author_id = ctx.author.id

    user_document = await get_user_document(client, current_author_id)

    # Get the currently selected profile
    currently_selected_profile_id = user_document["global"]["selected_profile"]


    embed = await tos_acceptance_embed(client, ctx)
    await stw.slash_send_embed(ctx, slash, embed)

# cog for the device auth login command.
class ProfileAuth(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def devauth_command(self, ctx, slash, authcode=None):
        await handle_dev_auth(self.client, ctx, slash, authcode)

    @ext.slash_command(name='device',
                       description='Add permanent authentication to the currently selected or another profile(PENDING)',
                       guild_ids=stw.guild_ids)
    async def slash_device(self, ctx: discord.ApplicationContext,
                           token: Option(str,
                                         "An authcode (can be entered later), used to link a profile to an account(PENDING)") = ""
                           ):
        await self.devauth_command(ctx, True, token)

    @ext.command(name='device',
                 aliases=['devauth', 'dev', 'deviceauth', 'deviceauthcode', 'profileauth', 'proauth'],
                 extras={'emoji': "link_acc", "args": {
                        'authcode': 'The authcode which will be linked to authentication of the currently selected profile, can also be entered later in the process. (Optional)(PENDING)'},
                        "dev": False},
                 brief="Add permanent authentication to the currently selected or another profile(PENDING)",
                 description="""This command allows you to create a device auth session, keeping you logged in.(PENDING)
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
                                                "Your Epic Games authcode. Required unless you have an active session.") = "",
                                    auth_opt_out: Option(bool, "Opt out of starting an authentication session") = True, ):
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
                                                "Your Epic Games authcode. Required unless you have an active session.") = "",
                                    auth_opt_out: Option(bool, "Opt out of starting an authentication session") = True, ):
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
                                                "Your Epic Games authcode. Required unless you have an active session.") = "",
                                    auth_opt_out: Option(bool, "Opt out of starting an authentication session") = True, ):
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

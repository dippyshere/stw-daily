import asyncio
import time

import discord
import discord.ext.commands as ext
from discord import Option

import stwutil as stw
from ext.profile.bongodb import get_user_document, replace_user_document, generate_profile_select_options

TOS_VERSION = 1


async def tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx):
    # TODO: Create proper TOS, Privacy Policy & EULA for this command
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    embed = discord.Embed(title=await stw.add_emoji_title(client, "User Agreement", "pink_link"),
                          description=f"""\u200b
                              **Currently Selected Profile {currently_selected_profile_id}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b\n""",
                          color=embed_colour)
    embed.description += f"""**You have not accepted the user agreement on profile {currently_selected_profile_id}**
                          ```Agreement:\n\u200b\nUsage of these STW Daily features is governed by the following additional set of terms:\n\u200b\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Purus in mollis nunc sed id semper risus. Quis enim lobortis scelerisque fermentum dui faucibus in. Et sollicitudin ac orci phasellus. Orci dapibus ultrices in iaculis nunc. Turpis egestas pretium aenean pharetra magna ac placerat vestibulum. Sapien faucibus et molestie ac feugiat sed. Ut ornare lectus sit amet est placerat in egestas. Non quam lacus suspendisse faucibus interdum posuere lorem. Urna id volutpat lacus laoreet non curabitur gravida arcu ac. Neque ornare aenean euismod elementum. Ultricies leo integer malesuada nunc vel risus commodo viverra maecenas. Donec massa sapien faucibus et molestie ac feugiat sed lectus. In fermentum et sollicitudin ac orci. Ut ornare lectus sit amet est placerat in egestas. Viverra adipiscing at in tellus. Eget velit aliquet sagittis id consectetur purus ut faucibus.\n\u200b\nEst ultricies integer quis auctor. Pulvinar elementum integer enim neque volutpat. At in tellus integer feugiat scelerisque varius morbi enim. Ipsum dolor sit amet consectetur adipiscing elit pellentesque. Proin sed libero enim sed faucibus turpis in eu mi. Eleifend donec pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Volutpat sed cras ornare arcu dui vivamus arcu felis. Suspendisse interdum consectetur libero id. Molestie nunc non blandit massa enim nec dui. Aliquam eleifend mi in nulla posuere sollicitudin. A condimentum vitae sapien pellentesque habitant morbi tristique. Suspendisse sed nisi lacus sed viverra tellus in hac. Vitae congue eu consequat ac felis donec et.\n\u200b\nA erat nam at lectus urna. Mi tempus imperdiet nulla malesuada pellentesque. Laoreet id donec ultrices tincidunt arcu. Enim praesent elementum facilisis leo vel. Nibh cras pulvinar mattis nunc sed blandit libero. Pretium fusce id velit ut tortor. Sociis natoque penatibus et magnis dis. Commodo odio aenean sed adipiscing. Tincidunt id aliquet risus feugiat in ante metus dictum at. Morbi tincidunt ornare massa eget egestas purus viverra accumsan. Phasellus egestas tellus rutrum tellus. Eu ultrices vitae auctor eu augue ut lectus arcu bibendum. Iaculis nunc sed augue lacus viverra vitae congue. Commodo sed egestas egestas fringilla. Consequat semper viverra nam libero justo. In mollis nunc sed id semper risus in. Sollicitudin aliquam ultrices sagittis orci. Pretium aenean pharetra magna ac placerat vestibulum lectus.
                          ```
                          *Waiting for acceptance of agreement*
                          \u200b
                          """

    embed = await stw.set_thumbnail(client, embed, "pink_link")
    embed = await stw.add_requested_footer(ctx, embed)
    return embed


async def add_enslaved_user_accepted_license(view, interaction):
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"]["tos_accepted"] = True
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_date"] = time.time_ns()  # how to get unix timestamp i forgor time.time is unix
    view.user_document["profiles"][str(view.currently_selected_profile_id)]["statistics"][
        "tos_accepted_version"] = TOS_VERSION
    view.client.processing_queue[view.user_document["user_snowflake"]] = True
    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)


async def pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction=None, exchange_auth_session=None):
    embed_colour = client.colours["profile_lavendar"]
    selected_profile_data = user_document["profiles"][str(currently_selected_profile_id)]

    page_embed = discord.Embed(title=await stw.add_emoji_title(client, "Device Authentication", "pink_link"),
                               description=f"""\u200b
                              **Currently Selected Profile {currently_selected_profile_id}:**
                              ```{selected_profile_data["friendly_name"]}```\u200b""",
                               color=embed_colour)
    page_embed = await stw.set_thumbnail(client, page_embed, "pink_link")
    page_embed = await stw.add_requested_footer(ctx, page_embed)

    if selected_profile_data["authentication"]["accountId"] == None:
        # Not authenticated yet data stuffy ;p

        auth_session = False
        if exchange_auth_session == None:
            try:
                temp_auth = client.temp_auth[ctx.author.id]
                auth_session = temp_auth

                embed = await stw.processing_embed(client, ctx)

                message = None
                if interaction is None:
                    message = await stw.slash_send_embed(ctx, embeds=embed)
                else:
                    await interaction.edit_original_response(embed=embed)

                asyncio.get_event_loop().create_task(attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction, message))
                return False
            except:
                pass
        elif exchange_auth_session != False:
            auth_session = True

        auth_session_found_message = f"[**To begin click here**](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode)\nThen copy your authentication code and enter it into the modal which appears from pressing the **{client.config['emojis']['locked']} Authenticate** Button below."
        if auth_session != False:
            auth_session_found_message = f"Found an existing authentication session, you can proceed utilising the account associated with this authentication session by pressing the **{client.config['emojis']['library_input']} Auth With Session** Button below\n\u200b\nYou can use a different account by copying the authentication code from [this link](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode) and then type your authentication code into the modal that appears from pressing the the **{client.config['emojis']['locked']} Authenticate** Button"

        page_embed.add_field(name=f"No device authentication found for current profile",
                             value=f"""
                             \u200b
                             {auth_session_found_message}
                             \u200b
                             *Waiting for action*
                             \u200b
                             """,
                             inline=False)

    return page_embed

async def attempt_to_exchange_session(temp_auth, user_document, client, ctx, interaction=None, message=None):
    get_ios_auth = await stw.exchange_games(client, temp_auth["token"], "ios")
    try:
        response_json = await get_ios_auth.json()
        await handle_dev_auth(client, ctx, interaction, user_document, response_json["access_token"], message)
    except:
        await handle_dev_auth(client, ctx, interaction, user_document, False, message)

async def handle_dev_auth(client, ctx, interaction=None, user_document=None, exchange_auth_session=None, message=None):
    current_author_id = ctx.author.id

    if user_document is None:
        user_document = await get_user_document(client, current_author_id)

    # Get the currently selected profile
    currently_selected_profile_id = user_document["global"]["selected_profile"]
    current_profile = user_document["profiles"][str(currently_selected_profile_id)]

    if current_profile["statistics"]["tos_accepted"] is False:
        embed = await tos_acceptance_embed(user_document, client, currently_selected_profile_id, ctx)
        button_accept_view = EnslaveUserLicenseAgreementButton(user_document, client, ctx,
                                                               currently_selected_profile_id)

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=button_accept_view)
        else:
            await interaction.edit_original_response(embed=embed, view=button_accept_view)

    elif current_profile["authentication"]["accountId"] is None:

        embed = await pre_authentication_time(user_document, client, currently_selected_profile_id, ctx, interaction, exchange_auth_session)


        if embed == False:
            return

        account_stealing_view = EnslaveAndStealUserAccount(user_document, client, ctx, currently_selected_profile_id, exchange_auth_session)

        if message != None:
            await stw.slash_edit_original(ctx, message, embeds=embed, view=account_stealing_view)
            return

        if interaction is None:
            await stw.slash_send_embed(ctx, embeds=embed, view=account_stealing_view)
        else:
            await interaction.edit_original_response(embed=embed, view=account_stealing_view)


class EnslaveAndStealUserAccount(discord.ui.View):
    def __init__(self, user_document, client, ctx, currently_selected_profile_id, ios_token):
        super().__init__()

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}
        self.ios_token = ios_token

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

        if self.ios_token == None:
            del self.children[2]

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        await select_change_profile(self, select, interaction)

    async def interaction_check(self, interaction):
        return await stw.view_interaction_check(self, interaction, "devauth")

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Authenticate", emoji="locked")
    async def enter_your_account_to_be_stolen_button(self, button, interaction):
        modal = StealAccountLoginDetailsModal(self, self.user_document, self.client, self.ctx,
                                              self.currently_selected_profile_id, self.ios_token)
        await interaction.response.send_modal(modal)

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Auth With Session", emoji="library_input")
    async def existing_account_that_we_already_stole_button(self, button, interaction):
        modal = StealAccountLoginDetailsModal(self, self.user_document, self.client, self.ctx,
                                              self.currently_selected_profile_id, self.ios_token)
        await interaction.response.send_modal(modal)

class EnslaveUserLicenseAgreementButton(discord.ui.View):
    def __init__(self, user_document, client, ctx, currently_selected_profile_id):
        super().__init__()

        self.currently_selected_profile_id = currently_selected_profile_id
        self.client = client
        self.user_document = user_document
        self.ctx = ctx
        self.interaction_check_done = {}

        self.children[0].options = generate_profile_select_options(client, int(self.currently_selected_profile_id),
                                                                   user_document)
        self.children[1:] = list(map(lambda button: stw.edit_emoji_button(self.client, button), self.children[1:]))

    @discord.ui.select(
        placeholder="Select another profile here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def profile_select(self, select, interaction):
        await select_change_profile(self, select, interaction)

    async def interaction_check(self, interaction):
        return await stw.view_interaction_check(self, interaction, "devauth")

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Accept Agreement", emoji="library_handshake")
    async def soul_selling_button(self, button, interaction):
        await add_enslaved_user_accepted_license(self, interaction)
        await handle_dev_auth(self.client, self.ctx, interaction, self.user_document)


# cog for the device auth login command.
class ProfileAuth(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def devauth_command(self, ctx):
        await handle_dev_auth(self.client, ctx)

    @ext.slash_command(name='device',
                       description='Add permanent authentication to the currently selected or another profile(PENDING)',
                       guild_ids=stw.guild_ids)
    async def slash_device(self, ctx: discord.ApplicationContext):
        await self.devauth_command(ctx)

    @ext.command(name='device',
                 aliases=['devauth', 'dev', 'deviceauth', 'deviceauthcode', 'profileauth', 'proauth'],
                 extras={'emoji': "link_acc", "args": {"dev": False}},
                 brief="Add permanent authentication to the currently selected or another profile(PENDING)",
                 description="""This command allows you to create a device auth session, keeping you logged in.(PENDING)
                \u200b
                """)
    async def device(self, ctx):
        await self.devauth_command(ctx)


async def select_change_profile(view, select, interaction):
    view.client.processing_queue[view.user_document["user_snowflake"]] = True

    new_profile_selected = int(select.values[0])
    view.user_document["global"]["selected_profile"] = new_profile_selected

    for child in view.children:
        child.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()

    await replace_user_document(view.client, view.user_document)
    await handle_dev_auth(view.client, view.ctx, interaction, view.user_document)

    del view.client.processing_queue[view.user_document["user_snowflake"]]


class StealAccountLoginDetailsModal(discord.ui.Modal):
    def __init__(self, view, user_document, client, ctx, currently_selected_profile_id, ios_token):
        self.client = client
        self.view = view
        self.user_document = user_document
        self.ctx = ctx
        self.currently_selected_profile_id = currently_selected_profile_id
        self.ios_token = ios_token

        super().__init__(title="Please enter authcode here")

        # aliases default description modal_title input_label check_function emoji input_type req_string

        setting_input = discord.ui.InputText(style=discord.InputTextStyle.long,
                                             label="Enter authcode",
                                             placeholder="Enter authcode here",
                                             min_length=1,
                                             max_length=500,
                                             required=True)

        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await interaction.response.edit_message(view=self.view)

        value = self.children[0].value
        print(value, self.children)

        auth_session_result = await stw.get_or_create_auth_session(self.client, self.ctx, "devauth", value, False, False, True)
        try:
            auth_session_result[1]
        except:
            pass


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

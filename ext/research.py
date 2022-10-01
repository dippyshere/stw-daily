import asyncio

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

import stwutil as stw


async def add_fort_fields(client, embed, current_levels, extra_white_space=False):
    print(current_levels)
    offense = current_levels["offense"]
    fortitude = current_levels["fortitude"]
    resistance = current_levels["resistance"]
    technology = current_levels["technology"]

    embed.add_field(name="\u200B", value="\u200B", inline=True)
    embed.add_field(name=f'**{client.config["emojis"]["fortitude"]} Fortitude: **',
                    value=f'```{fortitude}```\u200b', inline=True)
    embed.add_field(name=f'**{client.config["emojis"]["offense"]} Offense: **',
                    value=f'```{offense}```\u200b', inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=True)
    embed.add_field(name=f'**{client.config["emojis"]["resistance"]} Resistance: **',
                    value=f'```{resistance}```\u200b', inline=True)

    extra_white_space = "\u200b\n\u200b\n\u200b" if extra_white_space is True else ""
    embed.add_field(name=f'**{client.config["emojis"]["technology"]} Technology: **',
                    value=f'```{technology}```{extra_white_space}', inline=True)
    return embed


class ResearchView(discord.ui.View):

    def map_button_emojis(self, button):
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def on_timeout(self):
        gren = self.client.colours["research_green"]

        for child in self.children:
            child.disabled = True
        total_points = self.total_points
        current_levels = self.current_levels
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Research", "research_point"),
            description=f"""\u200b
            You currently have **{total_points['quantity']}** research point{'s' if total_points['quantity'] > 1 else ''} available.\n\u200b\n\u200b""",
            colour=gren
        )

        embed = await stw.set_thumbnail(self.client, embed, "research")
        embed = await stw.add_requested_footer(self.context, embed)
        embed = await add_fort_fields(self.client, embed, current_levels)
        embed.add_field(name=f"\u200b", value=f"*Timed out, please reuse the command to continue.*\n\u200b")
        await self.message.edit(embed=embed, view=self)
        return

    async def universal_stat_process(self, button, interaction, stat):
        gren = self.client.colours["research_green"]

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        stat_purchase = await stw.profile_request(self.client, "purchase_research", self.auth_info[1],
                                                  json={'statId': stat})
        purchased_json = await stat_purchase.json()

        total_points = self.total_points
        current_levels = self.current_levels

        for child in self.children:
            child.disabled = False

        try:
            if purchased_json['errorCode'] == 'errors.com.epicgames.fortnite.item_consumption_failed':
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, "Research", "research_point"),
                    description=f"""\u200b
                    You currently have **{total_points['quantity']}** research point{'s' if total_points['quantity'] > 1 else ''} available.\n\u200b\n\u200b""",
                    colour=gren
                )

                embed = await stw.set_thumbnail(self.client, embed, "research")
                embed = await stw.add_requested_footer(interaction, embed)
                embed = await add_fort_fields(self.client, embed, current_levels)
                embed.add_field(name=f"\u200b", value=f"*You do not have enough points to level up **{stat}***\n\u200b")
                await interaction.edit_original_message(embed=embed, view=self)
                return
        except:
            pass

        current_research_statistics_request = await stw.profile_request(self.client, "query", self.auth_info[1])
        json_response = await current_research_statistics_request.json()
        current_levels = await research_query(interaction, self.client, self.auth_info, self.slash, [], json_response)
        if current_levels is None:
            return

        self.current_levels = current_levels

        # What I believe happens is that epic games removes the research points item if you use it all... not to sure if they change the research token guid
        try:
            research_points_item = purchased_json['profileChanges'][0]['profile']['items'][self.research_token_guid]
        except:
            print(purchased_json)
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, "Research", "research_point"),
                description=f"""\u200b
                You currently have **0** research points available.\n\u200b\n\u200b""",
                colour=gren
            )

            embed = await add_fort_fields(self.client, embed, current_levels)
            embed.add_field(name=f"\u200b", value=f"*No more research points!*\n\u200b")
            embed = await stw.set_thumbnail(self.client, embed, "research")
            embed = await stw.add_requested_footer(interaction, embed)
            for child in self.children:
                child.disabled = True
            await interaction.edit_original_message(embed=embed, view=self)
            return

        spent_points = self.total_points['quantity'] - research_points_item['quantity']
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Research", "research_point"),
            description=f"""\u200b
            You currently have **{research_points_item['quantity']}** research point{'s' if research_points_item['quantity'] > 1 else ''} available.\n\u200b\n\u200b""",
            colour=gren
        )

        embed = await add_fort_fields(self.client, embed, current_levels)
        embed.add_field(name=f"\u200b", value=f"*Spent **{spent_points}** to level up **{stat}***\n\u200b")
        embed = await stw.set_thumbnail(self.client, embed, "research")
        embed = await stw.add_requested_footer(interaction, embed)
        self.total_points = research_points_item

        await interaction.edit_original_message(embed=embed, view=self)

    # creo kinda fire though ngl
    def __init__(self, client, auth_info, author, total_points, current_levels, research_token_guid, context, slash):
        super().__init__()
        self.client = client
        self.context = context
        self.auth_info = auth_info
        self.author = author
        self.interaction_check_done = {}
        self.total_points = total_points
        self.current_levels = current_levels
        self.research_token_guid = research_token_guid
        self.slash = slash

        self.button_emojis = {
            'fortitude': self.client.config["emojis"]["fortitude"],
            'offense': self.client.config["emojis"]['offense'],
            'resistance': self.client.config["emojis"]['resistance'],
            'technology': self.client.config["emojis"]['technology']
        }

        self.children = list(map(self.map_button_emojis, self.children))

    async def interaction_check(self, interaction):
        if self.author == interaction.user:
            return True
        else:
            try:
                already_notified = self.interaction_check_done[interaction.user.id]
            except:
                already_notified = False
                self.interaction_check_done[interaction.user.id] = True

            if not already_notified:
                support_url = self.client.config["support_url"]
                acc_name = ""
                error_code = "errors.stwdaily.not_author_interaction_response"
                embed = await stw.post_error_possibilities(interaction, self.client, "research", acc_name, error_code,
                                                           support_url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            else:
                return False

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="fortitude")
    async def fortitude_button(self, button, interaction):
        await self.universal_stat_process(button, interaction, "fortitude")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="offense")
    async def offense_button(self, button, interaction):
        await self.universal_stat_process(button, interaction, "offense")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="resistance")
    async def resistance_button(self, button, interaction):
        await self.universal_stat_process(button, interaction, "resistance")

    @discord.ui.button(style=discord.ButtonStyle.success, emoji="technology")
    async def technology_button(self, button, interaction):
        await self.universal_stat_process(button, interaction, "technology")


async def research_query(ctx, client, auth_info, slash, final_embeds, json_response):
    error_colour = client.colours["error_red"]
    gren = client.colours["research_green"]
    yellow = client.colours["warning_yellow"]
    crown_yellow = client.colours["crown_yellow"]

    support_url = client.config["support_url"]
    acc_name = auth_info[1]["account_name"]

    try:
        error_code = json_response["errorCode"]
        embed = await stw.post_error_possibilities(ctx, client, "research", acc_name, error_code, support_url)
        final_embeds.append(embed)
        await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        return
    except:
        pass

    current_levels = {}
    try:
        current_levels = json_response['profileChanges'][0]['profile']['stats']['attributes']['research_levels']
    except Exception as e:
        print(e, "assuming max research level im not sure??", json_response)
        current_levels = {'fortitude': 120, 'offense': 120, 'resistance': 120, 'technology': 120}
        pass

    # I'm not too sure what happens here but if current_levels doesn't exist im assuming its at maximum.
    proc_max = False
    try:
        if current_levels["offense"] + current_levels["fortitude"] + current_levels["resistance"] + current_levels["technology"] == 480:
            proc_max = True
    except:

        for stat in ["offense", "fortitude", "resistance", "technology"]:
            if stat not in current_levels:
                current_levels[stat] = 0

        pass

    if proc_max:
        embed = discord.Embed(
            title=await stw.add_emoji_title(client, "Max", "crown"),
            description="""\u200b
                Congratulations, you have **maximum** FORT stats.\n\u200b\n\u200b""",
            colour=crown_yellow
        )

        await add_fort_fields(client, embed, current_levels, True)
        embed = await stw.set_thumbnail(client, embed, "crown")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        return None

    return current_levels


# cog for the research related commands.
class Research(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        self.token_guid_research = "Token_collectionresource_nodegatetoken01"
        self.item_templateid_research = "Token:collectionresource_nodegatetoken01"

    def check_for_research_points_item(self, query_json):

        # Yes you can use the itemGuid from the notifications response from the claimcollectedresources response
        # but, you do not get notifications when you are at maximum research points!
        items = query_json['profileChanges'][0]['profile']['items']

        for key, item in items.items():
            try:
                if item['templateId'] == f"{self.item_templateid_research}":
                    return item, key
            except:
                pass

        return None

    def check_for_research_guid_key(self, query_json):

        items = query_json['profileChanges'][0]['profile']['items']
        for key, item in items.items():
            try:
                if item['templateId'] == f"CollectedResource:{self.token_guid_research}":
                    return key
            except:
                pass

        return None

    async def research_command(self, ctx, slash, authcode, auth_opt_out):
        error_colour = self.client.colours["error_red"]
        gren = self.client.colours["research_green"]
        yellow = self.client.colours["warning_yellow"]
        crown_yellow = self.client.colours["crown_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "daily", authcode, slash, auth_opt_out, True)
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

        current_research_statistics_request = await stw.profile_request(self.client, "query", auth_info[1])
        json_response = await current_research_statistics_request.json()
        current_levels = await research_query(ctx, self.client, auth_info, slash, final_embeds, json_response)
        if current_levels is None:
            return

        # Find research guid to post too required for ClaimCollectedResources json
        research_guid_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_guid_key, json_response))
        print(research_guid_check)
        if research_guid_check[0] is None:
            print("errors.stwdaily.failed_guid_research encountered:", json_response)
            error_code = "errors.stwdaily.failed_guid_research"
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

        research_guid = research_guid_check[0]
        pass

        current_research_statistics_request = await stw.profile_request(self.client, "resources", auth_info[1],
                                                                        json={"collectorsToClaim": [research_guid]})
        json_response = await current_research_statistics_request.json()

        try:
            error_code = json_response["errorCode"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            pass

        # Get total points
        total_points_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_points_item, json_response))
        if total_points_check[0] is None:
            print("errors.stwdaily.failed_total_points encountered:", json_response)
            error_code = "errors.stwdaily.failed_total_points"
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

        total_points, rp_token_guid = total_points_check[0][0], total_points_check[0][1]

        # I do believe that after some testing if you are at le maximum research points
        # you do not recieve notifications so this must be wrapped in a try statement
        # assume that research points generated is none since it is at max!
        research_points_claimed = None
        try:
            research_feedback, check = json_response["notifications"], False

            for notification in research_feedback:
                if notification["type"] == "collectedResourceResult":
                    research_feedback, check = notification, True
                    break

            if not check:
                error_code = "errors.stwdaily.failed_get_collected_resource_type"
                embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                           support_url)
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return

            available_research_items, check = research_feedback["loot"]["items"], False
            for research_item in available_research_items:
                try:
                    if research_item["itemType"] == self.item_templateid_research:
                        research_item, check = research_item, True
                        break
                except:
                    pass

            if not check:
                error_code = "errors.stwdaily.failed_get_collected_resource_item"
                embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code,
                                                           support_url)
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return

            research_points_claimed = research_item['quantity']
        except:
            pass

        # Create the embed for displaying nyaa~

        claimed_text = ""

        if research_points_claimed is not None:
            if research_points_claimed == 1:
                claimed_text = f"*Claimed **{research_points_claimed}** research point*\n\u200b"
            else:
                claimed_text = f"*Claimed **{research_points_claimed}** research points*\n\u200b"
        else:
            claimed_text = f"*Did not claim any research points*\n\u200b"
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Research", "research_point"),
            description=f"""\u200b
            You currently have **{total_points['quantity']}** research point{'s' if total_points['quantity'] > 1 else ''} available. \n\u200b\n\u200b""",
            colour=gren
        )

        embed = await add_fort_fields(self.client, embed, current_levels)
        embed.add_field(name=f"\u200b", value=claimed_text)
        embed = await stw.set_thumbnail(self.client, embed, "research")
        embed = await stw.add_requested_footer(ctx, embed)

        final_embeds.append(embed)
        research_view = ResearchView(self.client, auth_info, ctx.author, total_points, current_levels, rp_token_guid,
                                     ctx, slash)
        research_view.message = await stw.slash_edit_original(auth_info[0], slash, final_embeds, view=research_view)

    @ext.command(name='research',
                 aliases=['rse', 'des', 'rgesearch', 'r4es', 'reas',
                          'resd', 'resa', 're', 're4s', 'researtch', 're3search',
                          'rexearch', 'resw', 'rfesearch', 'researhc', 'rea', 'rers',
                          'reswarch', 'resdarch', 'resarch', 'redearch', 'researchh',
                          'researfh', 'reseach', 'reseatrch', 'rsesearch', 'r3s', 'rews',
                          'reseadrch', 'ers', 'rewearch', 'rese3arch', 'rssearch', 'gesearch',
                          'esearch', 'resezrch', 're3s', 'reseearch', 'reasearch', 'rew', 'reds',
                          'rses', 'researcyh', 'researdh', 'res4arch', 'ressearch', '5esearch', 'rezearch',
                          'reseatch', 'researcfh', 'rrsearch', 'ees', 'researcgh', 'rseearch', 'reesarch', 'resaearch',
                          'resear4ch', 'rds', 'rewsearch', 'tresearch', 'resefarch', 'reseaarch', 'researcxh', '4res', 'resx',
                          'resesrch', 'resexarch', 'r4search', 'r4esearch', '4es', 'rresearch', 'resrearch', 'rs', 'resea4ch', 'fes',
                          'gresearch', 'reseagch', 'es', 'r5es', 'rsearch', 'researvh', 'r3esearch', 'res4earch', 'researcjh', 'researech',
                          'researchn', 'resesarch', 'researcy', 'researrch', 'resfearch', 'researcj', 'reseasrch', 'resear5ch', 'rez', 'r3es',
                          'r3search', 'researc', 'res', 'researchj', 'refsearch', 'dres', 'rex', 'researchg', 'rrs', 'researchu', 'redsearch', 'rersearch',
                          'reseafch', 'reesearch', 'researcvh', 'eesearch', 'resezarch', '5research', 'res3earch', 'resewarch', 'fesearch', 'reearch', 'resxearch',
                          'rwes', 'rees', 'reswearch', 'reseaxrch', 'researcuh', 'refs', 'reseaqrch', 'resea4rch', 'rfs', 'fres', 'researgch', 'gres', 'reeearch',
                          'resea5ch', 'rtes', 'resexrch', 'rws', 'tres', 'researchy', 'researcnh', 'rdesearch', 'researcch', 'rexs', 'rges', 'reserch',
                          'resaerch', 'rese4arch', 'reserarch', 'researcu', 'researcbh', 'fresearch', 'rdes', 'rwesearch', 'rexsearch', 'desearch',
                          'reseqarch', 'dresearch', 'rezsearch', 'researchb', 'reseaech', 'eresearch', 'researxch', 'researdch', 'r4s',
                          'rfsearch', 'rres', 'reseagrch', 'reseaerch', 'ress', 'resaesaer', 'reseqrch', 'rfes', '4esearch',
                          'rwsearch', 'resea5rch', 'rtesearch', 'researfch', '5res', 'researcdh', 'eres', 'ressarch',
                          'resfarch', 'reseadch', 'rss', 'reszearch', 'reserach', 'reach', 'ersearch', 'reseazrch',
                          'rdsearch', 'ges', 'researcn', 'researcg', '4research', 'researcb', 'ree', 'resz',
                          'reseacrh', 'red', 'resdearch', 'reseawrch', '5es', 'rese', 'reseafrch', 'reaearch',
                          'researh', 'tesearch', 'researxh', 'r5esearch', 'resrarch', 'researvch', 'res3arch',
                          'resewrch', 'rezs', 're4search', 'tes', 'resedarch'],
                 extras={'emoji': "research_point", "args": {
                     'authcode': 'The authcode to start an authentication session with if one does not exist, if an auth session already exists this argument is optional (Optional)',
                     'opt-out': 'Any value inputted into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
                 brief="Allows you to distribute and claim your research points (auth req.)",
                 description="""This command allows you to claim your Fortnite: Save The World research points for the FORT (Fortification, Offence, Resistance, Tech) stats, You can view how many currently available research points you have and then distribute them to your choosing through the interface provided by the embed.
                """)
    async def research(self, ctx, authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.research_command(ctx, False, authcode, not optout)

    @slash_command(name='research',
                   description="Allows you to distribute and claim your research points (auth req.)",
                   guild_ids=stw.guild_ids)
    async def slashresearch(self, ctx: discord.ApplicationContext,
                            token: Option(str,
                                          "The authcode to start an authentication session with if one does not exist, else this is optional") = "",
                            auth_opt_out: Option(bool, "Opt Out of Authentication session") = True, ):
        await self.research_command(ctx, True, token, not auth_opt_out)


def setup(client):
    client.add_cog(Research(client))

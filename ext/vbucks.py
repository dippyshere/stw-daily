"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the vbucks command. Displays total v-bucks count, breakdown + x-ray tickets
"""

import asyncio
import orjson
import logging

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw
from ext.profile.bongodb import get_user_document

logger = logging.getLogger(__name__)


class VbucksCalculatorModal(discord.ui.Modal):
    """
    The modal for the calculator button command.
    """

    def __init__(self, client, ctx, desired_lang, current_total, message, embeds, auth_entry, view, goal):
        super().__init__(title=stw.I18n.get("vbucks.modal.title", desired_lang), timeout=480)
        self.client = client
        self.ctx = ctx
        self.desired_lang = desired_lang
        self.current_total = current_total
        self.message = message
        self.embeds = embeds
        self.auth_entry = auth_entry
        self.view = view
        self.goal = goal
        self.calculator_embed = None
        self.interaction_check_done = {}
        setting_input = discord.ui.InputText(placeholder=stw.I18n.get("vbucks.modal.placeholder", desired_lang,
                                                                      current_total),
                                             label=stw.I18n.get("vbucks.modal.label", desired_lang),
                                             min_length=len(str(current_total)), max_length=8)
        self.add_item(setting_input)

    async def callback(self, interaction: discord.Interaction):
        """
        This is the function that is called when the user submits the modal.

        Args:
            interaction: The interaction that the user did.
        """
        value = self.children[0].value
        try:
            if int(value) >= 10000:
                await interaction.response.defer()
        except:
            pass
        if value == "" or not str(value).isnumeric():
            embed = await stw.vbucks_goal_embed(self.client, self.ctx, desired_lang=self.desired_lang)
        elif int(value) <= self.current_total:
            embed = await stw.vbucks_goal_embed(self.client, self.ctx, current_total=self.current_total,
                                                desired_lang=self.desired_lang)
        else:
            total, days = (await asyncio.gather(asyncio.to_thread(stw.calculate_vbuck_goals, self.current_total,
                                                                  0 if self.auth_entry['day'] is None else
                                                                  self.auth_entry['day'], int(value))))[0]
            embed = await stw.vbucks_goal_embed(self.client, self.ctx, total, days, True, self.current_total,
                                                self.auth_entry['vbucks'], value, self.desired_lang)
        try:
            self.embeds[0]
            if self.goal:
                send_embed = self.embeds[:-1] + [embed]
            else:
                send_embed = self.embeds + [embed]
        except:
            send_embed = [self.embeds, embed]
        logger.debug(f"Sending embed: {send_embed}")
        try:
            return await interaction.edit_original_response(embeds=send_embed, view=self.view) if int(value) >= 10000 else await interaction.response.edit_message(embeds=send_embed, view=self.view)
        except:
            return await interaction.response.edit_message(embeds=send_embed, view=self.view)


# view for the invite command.
class VbucksCalculatorView(discord.ui.View):
    """
    discord UI View for the invite command.
    """

    def __init__(self, client, ctx, desired_lang, current_total, message, embeds, auth_entry, goal):
        super().__init__(timeout=480)
        self.client = client
        self.ctx = ctx
        self.desired_lang = desired_lang
        self.current_total = current_total
        self.message = message
        self.embeds = embeds
        self.auth_entry = auth_entry
        self.goal = goal
        self.calculator_embed = None
        self.interaction_check_done = {}

        self.button_emojis = {
            'library_banknotes': self.client.config["emojis"]["library_banknotes"]
        }

        self.children = list(map(self.map_button_emojis, self.children))
        self.children[0].label = stw.I18n.get('vbucks.button.calculator', self.desired_lang)

    def map_button_emojis(self, button):
        """
        Map the button emojis to the buttons.

        Args:
            button: The button to map the emoji to.

        Returns:
            The button with the emoji mapped.
        """
        button.emoji = self.button_emojis[button.emoji.name]
        return button

    async def on_timeout(self):
        """
        Called when the view times out

        Returns:
            None
        """
        for button in self.children:
            button.disabled = True
        return await stw.slash_edit_original(self.ctx, self.message, embeds=None, view=self)

    async def interaction_check(self, interaction):
        """
        This is the function that is called when the user interacts with the view.

        Args:
            interaction: The interaction that the user did.

        Returns:
            bool: True if the interaction is created by the view author, False if notifying the user
        """
        return await stw.view_interaction_check(self, interaction, "vbucks")

    @discord.ui.button(label="Calculator", style=discord.ButtonStyle.blurple, emoji="library_banknotes")
    async def calculate(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Button to open the vbucks calculator.

        Args:
            button: The button that was pressed.
            interaction: The interaction object.

        Returns:
            None
        """
        modal = VbucksCalculatorModal(self.client, self.ctx, self.desired_lang, self.current_total, self.message,
                                      self.embeds, self.auth_entry, self, self.goal)
        await interaction.response.send_modal(modal)


class Vbucks(ext.Cog):
    """
    Cog for the vbucks command.
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def check_errors(self, ctx, public_json_response, auth_info, final_embeds, desired_lang):
        """
        Checks for errors in the public_json_response and edits the original message if an error is found.

        Args:
            ctx: The context of the command.
            public_json_response: The json response from the public API.
            auth_info: The auth_info tuple from get_or_create_auth_session.
            final_embeds: The list of embeds to be edited.
            desired_lang: The desired language of the user.

        Returns:
            True if an error is found, False otherwise.
        """
        try:
            # general error
            error_code = public_json_response["errorCode"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "vbucks", acc_name, error_code,
                                                       verbiage_action="getmtx", desired_lang=desired_lang)
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

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "vbucks", authcode, auth_opt_out, True,
                                                         desired_lang=desired_lang)
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
        if await self.check_errors(ctx, core_json_response, auth_info, final_embeds, desired_lang):
            return

        vbucks = await asyncio.gather(
            asyncio.to_thread(stw.extract_profile_item, profile_json=orjson.loads(await core_request.read()),
                              item_string="Currency:Mtx"))

        # fetch x-ray ticket count TODO: can this be done in the same request as the vbucks?
        stw_request = await stw.profile_request(self.client, "query", auth_info[1])
        stw_json_response = orjson.loads(await stw_request.read())

        # check for le error code
        error_check = await self.check_errors(ctx, stw_json_response, auth_info, final_embeds, desired_lang)
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
            description=f"\u200b\n{stw.I18n.get('vbucks.embed.description.total', desired_lang, int(vbucks_total))}\u200b\n",
            colour=vbucc_colour)

        # add entry for each platform detected
        if vbucks_total != 0:
            for item in vbucks:
                for attr, val in item.items():
                    name, emoji = await stw.resolve_vbuck_source(val["templateId"], desired_lang)
                    embed.description += f"{self.emojis[emoji]} {name}: {stw.I18n.fmt_num(int(val['quantity']), desired_lang)}\n"
        else:
            embed.description += f"{stw.I18n.get('vbucks.embed.description.zerovbucks', desired_lang, self.emojis['spongebob'], self.emojis['megamind'])}\n"

        # add entry for x-ray if detected
        if xray:
            for item in xray:
                for attr, val in item.items():
                    embed.description += f"\u200b\n{stw.I18n.get('vbucks.embed.description.xray', desired_lang, self.emojis['xray'], int(val['quantity']))}\n"

        embed.description += "\u200b"

        if vbucks_total != 0:
            embed = await stw.set_thumbnail(self.client, embed, "vbuck_book")
        else:
            embed = await stw.set_thumbnail(self.client, embed, "clown")
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        final_embeds.append(embed)
        try:
            user_document = await get_user_document(ctx, self.client, ctx.author.id)
            try:
                goal = user_document["profiles"][str(user_document["global"]["selected_profile"])]["settings"]["mtxgoal"]
            except:
                goal = 0
        except:
            goal = 0
        try:
            if goal > 0:
                try:
                    _ = int(goal)
                except:
                    goal = ""
                if goal == "":
                    embed = await stw.vbucks_goal_embed(self.client, ctx, desired_lang=desired_lang, goal=True)
                elif int(goal) <= vbucks_total:
                    embed = await stw.vbucks_goal_embed(self.client, ctx, current_total=vbucks_total,
                                                        desired_lang=desired_lang, goal=True, assert_value=False,
                                                        target=goal)
                else:
                    total, days = (await asyncio.gather(asyncio.to_thread(stw.calculate_vbuck_goals, vbucks_total,
                                                                          0 if auth_info[1]['day'] is None else
                                                                          auth_info[1]['day'], int(goal))))[0]
                    embed = await stw.vbucks_goal_embed(self.client, ctx, total, days, True, vbucks_total,
                                                        auth_info[1]['vbucks'], goal, desired_lang, True)
                final_embeds.append(embed)
        except:
            pass
        vbuck_view = VbucksCalculatorView(self.client, ctx, desired_lang, vbucks_total, auth_info[0], final_embeds,
                                          auth_info[1], True if goal > 0 else False)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, view=vbuck_view)
        return

    @ext.slash_command(name='vbucks', name_localizations=stw.I18n.construct_slash_dict("vbucks.slash.name"),
                       # yay (say yay if you're yay yay) 😱
                       description='View your V-Bucks and X-Ray Tickets balance',
                       description_localizations=stw.I18n.construct_slash_dict("vbucks.slash.description"),
                       guild_ids=stw.guild_ids)
    async def slashvbucks(self, ctx: discord.ApplicationContext,
                          token: Option(
                              description="Your Epic Games authcode. Required unless you have an active session.",
                              description_localizations=stw.I18n.construct_slash_dict(
                                  "generic.slash.token"),
                              name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
                              min_length=32) = "",
                          auth_opt_out: Option(default="False",
                                               description="Opt out of starting an authentication session",
                                               description_localizations=stw.I18n.construct_slash_dict(
                                                   "generic.slash.optout"),
                                               name_localizations=stw.I18n.construct_slash_dict(
                                                   "generic.meta.args.optout"),
                                               choices=[OptionChoice("Do not start an authentication session", "True",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.true")),
                                                        OptionChoice("Start an authentication session (Default)",
                                                                     "False",
                                                                     stw.I18n.construct_slash_dict(
                                                                         "generic.slash.optout.false"))]) = "False"):
        """
        This function is the entry point for the vbucks command when called via slash

        Args:
            ctx: The context of the command.
            token: The authcode to use for authentication.
            auth_opt_out: Whether to opt out of starting an authentication session.
        """
        await self.vbuck_command(ctx, token, not eval(auth_opt_out))

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
                          '/vbucks', '/v-bucks', 'chucks', '/chucks', '/balance', 'money', 'currency', 'cash', 'vbu',
                          'vbucks\\', 'vbuck\\', 'v\\', 'monedas', 'ビーバックス', 'vdolce', 'вбуцкс', '雄鹿队', '雄鹿隊',
                          'vrbucks', 'vbaucks', 'vbuckys', 'rbucks', 'vbucksv', 'xbucks', 'vbpucks', 'vbueks',
                          'vjucks', 'vbuwks', 'vbuckc', 'jvbucks', 'vbuckcs', 'vbuhks', 'vbucksm', 'vbuckns', 'vfucks',
                          'ybucks', 'vbuckrs', 'vbucksf', 'vbccks', 'vbuckt', 'vjbucks', 'vbuckh', 'vcucks', 'vuucks',
                          'vbujks', 'tvbucks', 'zvbucks', 'vbuccs', 'vbucbs', 'lbucks', 'vbuckvs', 'vbukks', 'vbncks',
                          'vbucys', 'kbucks', 'vwbucks', 'vbfucks', 'vbubks', 'voucks', 'vbwucks', 'vqbucks', 'vbucfs',
                          'vbumks', 'vibucks', 'vbuocks', 'vbuqks', 'vbucrs', 'vrucks', 'dbucks', 'vtbucks', 'vbmcks',
                          'vbxucks', 'vbuctks', 'qbucks', 'ivbucks', 'vbucqs', 'vbucrks', 'vbuyks', 'vdbucks',
                          'vbuwcks', 'vbuckst', 'vbucksk', 'vbulks', 'vbuuks', 'ebucks', 'pvbucks', 'vbucts', 'vbucaks',
                          'vubucks', 'vbucksi', 'vbuckso', 'vbfcks', 'vbuoks', 'vbqcks', 'vbutcks', 'vxbucks',
                          'vbucwks', 'vbucksq', 'vbucws', 'vbuqcks', 'nbucks', 'vbucuks', 'evbucks', 'mbucks', 'vlucks',
                          'vbucksg', 'vbuscks', 'vbumcks', 'vbzucks', 'vbucgs', 'vbuzcks', 'vsucks', 'vbocks', 'vbtcks',
                          'viucks', 'veucks', 'vbuncks', 'ubucks', 'vkbucks', 'vbuckqs', 'vbuaks', 'vbducks', 'vbucns',
                          'vzbucks', 'ibucks', 'hbucks', 'vybucks', 'vbupks', 'vbuckp', 'zbucks', 'vbucksl', 'vbuckn',
                          'vbucky', 'svbucks', 'vbucksy', 'vbuceks', 'vblucks', 'vbxcks', 'nvbucks', 'vbutks', 'vbuczs',
                          'vbacks', 'vtucks', 'vburcks', 'vbuczks', 'vbuckf', 'vbucvs', 'vbucnks', 'vxucks', 'lvbucks',
                          'vbuces', 'dvbucks', 'vbuckg', 'vbwcks', 'vbuckbs', 'vpucks', 'vbucps', 'vebucks', 'vbucbks',
                          'vbugcks', 'vbucqks', 'vbucpks', 'yvbucks', 'vmucks', 'vbuckts', 'vzucks', 'rvbucks',
                          'vbzcks', 'obucks', 'vbuchs', 'vbuecks', 'vbpcks', 'vbucsks', 'vbuckb', 'vqucks', 'vbuckq',
                          'vbubcks', 'vbucksr', 'pbucks', 'vbupcks', 'vbuiks', 'vpbucks', 'vbqucks', 'vbusks',
                          'vbuchks', 'vbuckhs', 'wbucks', 'vaucks', 'vbunks', 'hvbucks', 'vbmucks', 'jbucks', 'vbvcks',
                          'qvbucks', 'vbuckgs', 'vbuzks', 'avbucks', 'vbucksu', 'vbbcks', 'vbgcks', 'vobucks',
                          'vlbucks', 'vyucks', 'vbucksb', 'vbucus', 'xvbucks', 'vburks', 'tbucks', 'vbeucks', 'vbuacks',
                          'vwucks', 'vbucds', 'sbucks', 'vbscks', 'vbucas', 'vbucksh', 'vsbucks', 'vbsucks', 'vbrucks',
                          'vbucgks', 'vducks', 'vbucksp', 'vbulcks', 'vbecks', 'vmbucks', 'vboucks', 'vbuckv', 'vbugks',
                          'vabucks', 'uvbucks', 'wvbucks', 'vbuckps', 'vbrcks', 'vbucyks', 'vbuckr', 'mvbucks',
                          'vkucks', 'vblcks', 'vbucksj', 'vbucksc', 'vbuckus', 'vbuckfs', 'vbtucks', 'vbucxs',
                          'kvbucks', 'vbdcks', 'vbucss', 'abucks', 'vbucku', 'vbucksn', 'vbcucks', 'ovbucks', 'vb6cks',
                          'vb^cks', 'vb&cks', 'vb*cks', 'vbuc.s', 'vbuc,s', 'vbuc>s', 'vbuc<s', 'bvucc', 'vbuccz',
                          'vucc', 'ovbucc', 'vbuccb', 'vbcuc', 'vbucca', 'vubcc', 'bucc', 'vbucjc', 'vbutc', 'dbucc',
                          'vbccc', 'veucc', 'vbcc', 'vbucch', 'vbuccf', 'vbgucc', 'vbocc', 'vsucc', 'vbtucc', 'vbucic',
                          'vbumc', 'vwucc', 'vbuhc', 'vbucuc', 'vbdcc', 'vibucc', 'ebucc', 'qvbucc', 'vtbucc', 'gbucc',
                          'pvbucc', 'vbucd', 'vxucc', 'vbubcc', 'vbuucc', 'rbucc', 'vybucc', 'vboucc', 'vbhcc',
                          'vbuccc', 'vbuccv', 'vpbucc', 'vbuoc', 'vbuca', 'vbuvcc', 'vbqcc', 'vbuocc', 'vbucu',
                          'vbucmc', 'vbupcc', 'vbeucc', 'vvbucc', 'vbucn', 'vblcc', 'uvbucc', 'jvbucc', 'vbnucc',
                          'vbkucc', 'hvbucc', 'vfbucc', 'vbukcc', 'vcucc', 'vbucw', 'vbaucc', 'vbufcc', 'vbqucc',
                          'vbuec', 'vbuctc', 'vhucc', 'vbubc', 'vbuvc', 'vbucce', 'vbuac', 'voucc', 'vbbcc', 'vbucx',
                          'vbuic', 'vbuacc', 'vbzcc', 'dvbucc', 'vgucc', 'vbpucc', 'qbucc', 'vbucpc', 'tbucc', 'vbuuc',
                          'nbucc', 'vtucc', 'vbuhcc', 'vbugc', 'vbucr', 'vbbucc', 'xbucc', 'vbrcc', 'vbucfc', 'vbucdc',
                          'vbrucc', 'vbucqc', 'vjucc', 'vducc', 'vbuct', 'jbucc', 'vbvucc', 'vbuxcc', 'vaucc', 'fvbucc',
                          'vkbucc', 'vbyucc', 'vbujc', 'vbudcc', 'vbuyc', 'vbzucc', 'vbuxc', 'vbucz', 'vbicc', 'vvucc',
                          'vbucec', 'vbucg', 'vbusc', 'vbucq', 'rvbucc', 'abucc', 'vbducc', 'vzucc', 'vbucac', 'vpucc',
                          'vbtcc', 'vbecc', 'zvbucc', 'vbulcc', 'vbuccq', 'yvbucc', 'vlucc', 'vbucvc', 'vbxucc',
                          'vbcucc', 'vbuwc', 'vbhucc', 'vbfcc', 'vbuqc', 'vbulc', 'vbucv', 'xvbucc', 'vbfucc', 'vblucc',
                          'vbycc', 'vburc', 'vbucnc', 'pbucc', 'kbucc', 'vbjcc', 'vbupc', 'vnucc', 'vbucy', 'wbucc',
                          'vbuecc', 'hbucc', 'vjbucc', 'nvbucc', 'vqucc', 'ivbucc', 'vbuccn', 'gvbucc', 'tvbucc',
                          'vburcc', 'vbunc', 'vyucc', 'vbucsc', 'vbuscc', 'vbuccp', 'cbucc', 'vkucc', 'vbsucc',
                          'vbuccj', 'vobucc', 'mvbucc', 'vbucp', 'vuucc', 'ibucc', 'vebucc', 'vbucyc', 'vbujcc',
                          'obucc', 'vmucc', 'vbvcc', 'vbutcc', 'vbuncc', 'vbmucc', 'mbucc', 'vbmcc', 'vabucc', 'vrucc',
                          'fbucc', 'vbscc', 'vbuccm', 'vbncc', 'vbuccw', 'vbuce', 'vcbucc', 'zbucc', 'vbuclc', 'vbuccy',
                          'vbuccx', 'ybucc', 'vbuccr', 'viucc', 'vrbucc', 'vgbucc', 'vbucct', 'vsbucc', 'avbucc',
                          'vbucb', 'vbuwcc', 'vbxcc', 'vbjucc', 'vbudc', 'vbucxc', 'vbumcc', 'vbuycc', 'kvbucc',
                          'vbuzcc', 'vmbucc', 'vubucc', 'svbucc', 'evbucc', 'vbucco', 'vqbucc', 'vbuccg', 'lvbucc',
                          'vbuicc', 'vdbucc', 'ubucc', 'vbucf', 'vbuccl', 'vbucgc', 'vbucrc', 'vfucc', 'vxbucc',
                          'vbucoc', 'vbwcc', 'vbugcc', 'vbgcc', 'vbiucc', 'vnbucc', 'vbuccu', 'sbucc', 'vbuch',
                          'wvbucc', 'vbuccd', 'vbuczc', 'lbucc', 'vbufc', 'vbuchc', 'vbucbc', 'vbacc', 'vbpcc',
                          'vbuqcc', 'vlbucc', 'vhbucc', 'cvbucc', 'vbucwc', 'vbuzc', 'vzbucc', 'vbucci', 'vbkcc',
                          'bbucc', 'bvbucc', 'vbwucc', 'vwbucc', 'vb6cc', 'vb7cc', 'vb8cc', 'vb^cc', 'vb&cc', 'vb*cc',
                          'v-sucks', 'v-buckqs', 'v-bukks', 'v-bmucks', 'v-bucksq', 'kv-bucks', 'v-bucqks', 'v-bgcks',
                          'v-bucts', 'v-wbucks', 'v-buchks', 'q-bucks', 'e-bucks', 'x-bucks', 'v-bqcks', 'v-oucks',
                          'v-jucks', 'v-bujks', 'v-buckns', 'mv-bucks', 'vp-bucks', 'v-buiks', 'v-bucksv', 'v-buckus',
                          'v-kbucks', 'v-buctks', 'v-iucks', 'v-bucksy', 'u-bucks', 'l-bucks', 'v-bqucks', 'v-rucks',
                          'v-ybucks', 'v-bucvs', 'v-bucpks', 'v-mbucks', 'v-buuks', 'v-bucgs', 'v-brcks', 'v-bucsks',
                          'v-mucks', 'v-buczks', 'vm-bucks', 'v-buckn', 'v-buoks', 'v-ducks', 'v-buwcks', 'v-qucks',
                          'v-buckb', 'v-bxucks', 'v-kucks', 'v-bugcks', 'v-bucxs', 'v-bupcks', 'v-bscks', 'v-buzks',
                          'v-ebucks', 'iv-bucks', 'v-bupks', 'v-bubcks', 'v-bucrks', 'v-ubucks', 'v-bucbks', 'h-bucks',
                          'v-bucksb', 'vh-bucks', 'vl-bucks', 'v-eucks', 'v-backs', 'v-zbucks', 'v-xucks', 'v-buckm',
                          'v-lucks', 'xv-bucks', 'v-bucaks', 'ev-bucks', 'v-burks', 'v-bucki', 'i-bucks', 'vy-bucks',
                          'v-bucfs', 'v-bccks', 'vk-bucks', 'v-bocks', 'o-bucks', 's-bucks', 'd-bucks', 'qv-bucks',
                          'vs-bucks', 'v-baucks', 'v-buczs', 'v-buckso', 'v-blucks', 'v-xbucks', 'v-cbucks', 'v-buccs',
                          'vi-bucks', 'v-zucks', 'v-bucksg', 'v-becks', 'v-bncks', 'v-buckys', 'zv-bucks', 'vw-bucks',
                          'v-bucksm', 'v-ibucks', 'v-bpcks', 'v-bucnks', 'v-bucgks', 'v-bucyks', 'v-blcks', 'j-bucks',
                          'v-wucks', 'vz-bucks', 'v-buces', 'v-buckfs', 'v-bbcks', 'v-buckv', 'uv-bucks', 'v-bucys',
                          'v-buckhs', 'v-yucks', 'v-bucrs', 'wv-bucks', 'dv-bucks', 'vj-bucks', 'v-buscks', 'vt-bucks',
                          'v-fucks', 'v-bpucks', 'v-bucus', 'v-buceks', 'v-bucko', 'rv-bucks', 'vr-bucks', 'y-bucks',
                          'v-bucksc', 'p-bucks', 'v-btcks', 'v-bucss', 'v-buaks', 'v-buckst', 'v-bmcks', 'v-bucky',
                          'v-bucksn', 'v-bucds', 'sv-bucks', 'v-bfcks', 'n-bucks', 'v-uucks', 'v-bumks', 'v-buckr',
                          'v-buckf', 'v-cucks', 'v-bucksh', 'v-buckh', 'ov-bucks', 'v-bwucks', 'hv-bucks', 'v-bueks',
                          'tv-bucks', 'z-bucks', 'v-bucksj', 'v-tbucks', 'v-bunks', 'v-burcks', 'v-butcks', 'v-buacks',
                          'v-bucksr', 'v-buckbs', 'v-bulks', 'v-buckgs', 'v-buncks', 'v-buckc', 'v-bucps', 'va-bucks',
                          'v-bucku', 'v-buckj', 'v-bucws', 'v-btucks', 'vn-bucks', 'v-buwks', 'k-bucks', 'v-sbucks',
                          'vu-bucks', 'jv-bucks', 'v-lbucks', 'v-brucks', 'v-bucksu', 'v-bucksl', 'v-bucas', 'v-bucwks',
                          'av-bucks', 'v-buckps', 'v-buyks', 'v-buckts', 'nv-bucks', 'v-bfucks', 'v-bvcks', 't-bucks',
                          'v-buckq', 'v-bulcks', 'v-bducks', 'v-dbucks', 'v-aucks', 'v-bsucks', 'v-buqcks', 'v-pucks',
                          'v-buchs', 'm-bucks', 'v-bzucks', 'v-bucksi', 'vd-bucks', 'v-buocks', 'v-bumcks', 'v-buckt',
                          'v-bucuks', 'v-bcucks', 'v-bucqs', 'v-bucns', 'vx-bucks', 'v-buqks', 'v-bdcks', 'v-buzcks',
                          'yv-bucks', 'v-obucks', 'v-pbucks', 'v-buckk', 'v-buecks', 'w-bucks', 'v-bxcks', 'v-buckl',
                          'v-bzcks', 've-bucks', 'v-bwcks', 'v-busks', 'v-buckvs', 'v-buckp', 'lv-bucks', 'vq-bucks',
                          'v-jbucks', 'v-bucksk', 'vo-bucks', 'v-fbucks', 'v-abucks', 'v-qbucks', 'pv-bucks',
                          'v-buckrs', 'v-bubks', 'v-bucksp', 'v-buckg', 'a-bucks', 'v-butks', 'v-beucks', 'r-bucks',
                          'v-bucbs', 'v-rbucks', 'v-buhks', 'v-tucks', 'v-boucks', 'v-bucksf', 'v-buckcs', 'v-bugks',
                          'v0bucks', 'v)bucks', 'v_bucks', 'v=bucks', 'v[bucks', 'v]bucks', 'v;bucks', 'v(bucks',
                          'v+bucks', 'v{bucks', 'v-b6cks', 'v-b^cks', 'v-b&cks', 'v-b*cks', 'v-buc.s', 'v-buc,s',
                          'v-buc>s', 'v-buc<s', 'v-buc', '-bucc', 'v-buec', 'v-ubcc', 'v-bcuc', 'v-bucvc', 'v-buecc',
                          'w-bucc', 'v-pucc', 'v-bucf', 'v-buyc', 'v-bducc', '-vbucc', 'v-bujc', 'h-bucc', 'cv-bucc',
                          'v-bscc', 'v-buca', 'v-tbucc', 'v-bcc', 'v-bjucc', 'v-bucn', 'vm-bucc', 'v-bufc', 'v-gucc',
                          'v-zucc', 'kv-bucc', 'v-ucc', 'v-bvcc', 'v-buclc', 'v-buucc', 'v-bxcc', 'v-blcc', 'v-buccy',
                          'v-buccq', 'v-bucc', 'vi-bucc', 'v-nbucc', 'v-baucc', 'v-bucz', 'v-bucr', 'v-bucic',
                          'v-buscc', 'v-bucm', 'v-bfucc', 'v-buac', 'v-buccc', 'v-bubcc', 'v-mbucc', 'v-mucc', 'v-buvc',
                          'v-bfcc', 'v-butc', 'x-bucc', 'vb-ucc', 'fv-bucc', 'v-blucc', 'v-bcucc', 'd-bucc', 'v-bucce',
                          't-bucc', 'v-rbucc', 'v-buccx', 'av-bucc', 'vw-bucc', 'v-tucc', 'v-nucc', 'v-biucc',
                          'v-byucc', 'v-bucrc', 'u-bucc', 'n-bucc', 'v-buhcc', 'v-bccc', 'v-bvucc', 'c-bucc', 'v-bycc',
                          'v-btcc', 'v-boucc', 'v-bucec', 'k-bucc', 'v-buccn', 'v-buci', 'v-buccd', 'iv-bucc', 'v-bdcc',
                          'v-buwc', 'v-vucc', 'v-buhc', 'dv-bucc', 'v-zbucc', 'mv-bucc', 'v-bkcc', 'v-abucc', 'xv-bucc',
                          'v-eucc', 'v-bucw', 'v-buccz', 'v-buccp', 'v-bxucc', 'v-aucc', 'v-bicc', 'v-bubc', 'v-buccr',
                          'y-bucc', 'vb-bucc', 'va-bucc', 'v-pbucc', 'v-bbcc', 'v-bkucc', 'v-lbucc', 'vd-bucc',
                          'v-kucc', 'v-bujcc', 'p-bucc', 'vq-bucc', 'v-bpucc', 'v-bocc', 'v-buvcc', 'vv-bucc',
                          'v-buctc', 'v-oucc', 'v-buqc', 'v-bncc', 'v-bucch', 'e-bucc', 'tv-bucc', 'v-bucjc', 've-bucc',
                          'v-bucck', 'o-bucc', 'r-bucc', 'v-bucqc', 'v-bnucc', 'v-bucct', 'v-buxc', 'v-bqucc', 'v-bmcc',
                          'v-ibucc', 'v-brucc', 'v-iucc', 'hv-bucc', 'v-buuc', 'v-bugc', 'v-bqcc', 'v-buce', 'yv-bucc',
                          'v-sbucc', 'v-bucv', 'v-jucc', 'v-qbucc', 'v-bwcc', 'v-bucci', 'v-bucl', 'vh-bucc', 'ev-bucc',
                          'v-bgcc', 'v-bucg', 'v-bzucc', 'v-bucx', 'a-bucc', 'v-lucc', 'z-bucc', 'vt-bucc', 'v-buic',
                          'v-cbucc', 'vk-bucc', 'v-bzcc', 'v-jbucc', 'v-bukcc', 'v-rucc', 'v-bucp', 'v-buccg', 'v-bukc',
                          'v-burcc', 'v-budc', 'g-bucc', 'v-vbucc', 'v-bgucc', 'v-bwucc', 'vj-bucc', 'v-kbucc',
                          'v-cucc', 'v-ebucc', 'v-bupc', 'v-buccl', 'v-bucoc', 'v-yucc', 'v-buccv', 'v-bucj', 'v-buacc',
                          'vf-bucc', 'v-bucnc', 'v-budcc', 'v-buzc', 'q-bucc', 'v-bucgc', 's-bucc', 'v-bumc', 'nv-bucc',
                          'vo-bucc', 'vy-bucc', 'v-dbucc', 'bv-bucc', 'v-buct', 'v-bucbc', 'v-bucdc', 'jv-bucc',
                          'v-bbucc', 'v-buocc', 'v-bmucc', 'v-buccu', 'v-ducc', 'ov-bucc', 'v-buco', 'v-bulcc',
                          'v-beucc', 'v-bunc', 'lv-bucc', 'rv-bucc', 'vp-bucc', 'v-bucmc', 'v-bumcc', 'v-burc',
                          'v-xbucc', 'v-busc', 'v-becc', 'v-buccj', 'v-xucc', 'vs-bucc', 'v-buchc', 'v-qucc', 'v-bucyc',
                          'v-buczc', 'v-bucy', 'v-bucfc', 'v-bugcc', 'gv-bucc', 'v-hucc', 'v-buycc', 'v-fucc', 'v-bpcc',
                          'qv-bucc', 'v-fbucc', 'v-bucwc', 'v-bucu', 'v-bucca', 'b-bucc', 'v-bucb', 'v-bucpc',
                          'sv-bucc', 'v-bucd', 'v-uucc', 'v-bucxc', 'v-buccb', 'v-bucsc', 'vx-bucc', 'm-bucc',
                          'v-buccf', 'uv-bucc', 'v-wbucc', 'v-buccm', 'v-buccw', 'vr-bucc', 'v-obucc', 'wv-bucc',
                          'v-wucc', 'v-ybucc', 'v-ubucc', 'v-buch', 'v-hbucc', 'vg-bucc', 'v-buncc', 'v-bucco',
                          'v-bufcc', 'v-bhcc', 'v-bucac', 'v-bucq', 'v-btucc', 'v-bhucc', 'v-buzcc', 'vu-bucc',
                          'v-bjcc', 'vl-bucc', 'v-gbucc', 'vc-bucc', 'v-butcc', 'v-buwcc', 'v-buoc', 'v-bulc', 'i-bucc',
                          'l-bucc', 'vz-bucc', 'v-bucuc', 'zv-bucc', 'v-buqcc', 'v-buxcc', 'v-succ', 'v-brcc',
                          'v-bupcc', 'vn-bucc', 'v-buicc', 'v-bacc', 'pv-bucc', 'j-bucc', 'v-bsucc', 'f-bucc', 'v0bucc',
                          'v)bucc', 'v_bucc', 'v=bucc', 'v[bucc', 'v]bucc', 'v;bucc', 'v(bucc', 'v--bucc', 'v+bucc',
                          'v{bucc', 'v-b6cc', 'v-b7cc', 'v-b8cc', 'v-b^cc', 'v-b&cc', 'v-b*cc', 'balanceg', 'balcance',
                          'bawance', 'balancen', 'balangce', 'balancq', 'badance', 'qalance', 'bauance', 'balacnce',
                          'balakce', 'bpalance', 'batance', 'baliance', 'balince', 'balunce', 'ibalance', 'balantce',
                          'palance', 'balatnce', 'balazce', 'barance', 'balanceo', 'balanzce', 'bdlance', 'balancl',
                          'balancev', 'balanace', 'baclance', 'balanco', 'balancme', 'bailance', 'balancej', 'baleance',
                          'balancp', 'bolance', 'balpnce', 'baladnce', 'balbance', 'bjlance', 'balonce', 'baylance',
                          'balancqe', 'bahance', 'baelance', 'bayance', 'balafce', 'zalance', 'balanse', 'balapnce',
                          'walance', 'byalance', 'balavce', 'bualance', 'balanee', 'balancze', 'calance', 'talance',
                          'balatce', 'bralance', 'balagce', 'baladce', 'ealance', 'balancx', 'balanoe', 'balanwce',
                          'balanre', 'baljnce', 'balalnce', 'ralance', 'balante', 'boalance', 'bahlance', 'balynce',
                          'bglance', 'ialance', 'balknce', 'balancne', 'bacance', 'baldnce', 'brlance', 'balanue',
                          'babance', 'balgnce', 'ualance', 'balanck', 'balanct', 'balange', 'balanceb', 'balaoce',
                          'baltance', 'bamance', 'balawce', 'balaince', 'balancb', 'balaece', 'balanoce', 'jbalance',
                          'balauce', 'cbalance', 'bmlance', 'dbalance', 'balanch', 'balancec', 'belance', 'yalance',
                          'bklance', 'bajlance', 'balancex', 'balanae', 'bazance', 'qbalance', 'wbalance', 'balanye',
                          'salance', 'balanke', 'baluance', 'balaqce', 'balcnce', 'bplance', 'balaace', 'ubalance',
                          'kbalance', 'balanyce', 'balanceh', 'baaance', 'baqance', 'balanpe', 'baltnce', 'oalance',
                          'bjalance', 'bylance', 'balancg', 'bkalance', 'balancm', 'balavnce', 'balyance', 'balancte',
                          'balanhe', 'balanceq', 'balfance', 'bavlance', 'abalance', 'balanpce', 'baxance', 'basance',
                          'balancu', 'bflance', 'balancue', 'balarce', 'balancae', 'malance', 'balnnce', 'balancbe',
                          'balmance', 'balanje', 'baglance', 'banlance', 'baldance', 'baulance', 'zbalance', 'bagance',
                          'balvance', 'bilance', 'balanceu', 'bafance', 'balancle', 'balancc', 'balaice', 'balanbe',
                          'btalance', 'balancpe', 'balarnce', 'bnlance', 'balbnce', 'balmnce', 'balancoe', 'xbalance',
                          'rbalance', 'bvlance', 'tbalance', 'balancel', 'btlance', 'balancea', 'pbalance', 'ybalance',
                          'balaence', 'bialance', 'balaonce', 'bablance', 'baljance', 'balancn', 'balancey', 'balancez',
                          'bdalance', 'dalance', 'balancj', 'bmalance', 'balvnce', 'balanme', 'balacce', 'bulance',
                          'bhlance', 'balaynce', 'balanche', 'mbalance', 'bavance', 'balancke', 'balansce', 'balancei',
                          'bfalance', 'balaknce', 'balancje', 'baiance', 'balankce', 'aalance', 'balancv', 'bajance',
                          'lalance', 'balanuce', 'falance', 'balanwe', 'balayce', 'balaunce', 'balafnce', 'balanle',
                          'balanne', 'balnance', 'balanie', 'balancie', 'balasce', 'balanlce', 'balanece', 'balancem',
                          'blalance', 'bamlance', 'banance', 'sbalance', 'balagnce', 'balanca', 'balfnce', 'obalance',
                          'batlance', 'balrance', 'bblance', 'balancy', 'balaxce', 'kalance', 'balanci', 'balhance',
                          'bclance', 'balrnce', 'balanrce', 'ballnce', 'bcalance', 'balancye', 'balhnce', 'balancge',
                          'jalance', 'balalce', 'bealance', 'balanqe', 'balancek', 'lbalance', 'baeance', 'balgance',
                          'baflance', 'bllance', 'ebalance', 'balanze', 'badlance', 'balence', 'xalance', 'balanqce',
                          'fbalance', 'barlance', 'balanice', 'balancep', 'balancz', 'balapce', 'balancet', 'ba;ance',
                          'ba/ance', 'ba.ance', 'ba,ance', 'ba?ance', 'ba>ance', 'ba<ance', 'bala,ce', 'bala<ce',
                          'balanc2', 'balanc$', 'balanc#', 'balanc@', 'mtl', 'max', 'mxt', 'tmx', 'mtz', 'tx', 'mtrx',
                          'xtx', 'mdtx', 'motx', 'mtxg', 'mtfx', 'myx', 'mt', 'qmtx', 'mx', 'mtp', 'etx', 'mfx', 'mlx',
                          'mtxr', 'ltx', 'mtxw', 'mtb', 'mcx', 'mwx', 'cmtx', 'mtj', 'mtxx', 'omtx', 'mtd', 'mtkx',
                          'mtsx', 'mtg', 'gmtx', 'stx', 'mta', 'imtx', 'mhx', 'smtx', 'mtxd', 'mtn', 'mkx', 'mtx',
                          'mwtx', 'mtxb', 'gtx', 'mgtx', 'ztx', 'mvx', 'hmtx', 'msx', 'mtxc', 'ktx', 'mtq', 'mvtx',
                          'htx', 'mtxq', 'mtxu', 'mtpx', 'ftx', 'mtex', 'mtxt', 'kmtx', 'mztx', 'mtc', 'wmtx', 'mltx',
                          'pmtx', 'mytx', 'mutx', 'mtxo', 'nmtx', 'mtox', 'mox', 'mhtx', 'mktx', 'mptx', 'ymtx', 'mstx',
                          'mtxl', 'mtqx', 'mitx', 'atx', ',tx', '<tx', 'm4x', 'm5x', 'm6x', 'm$x', 'm%x', 'm^x',
                          'cuhcks', 'hucks', 'chupks', 'chucsk', 'ihucks', 'chlucks', 'shucks', 'clhucks', 'cucks',
                          'chcuks', 'chukcs', 'chuck', 'hhucks', 'chukcks', 'chbucks', 'chuks', 'hcucks', 'chuceks',
                          'czhucks', 'chrcks', 'chucs', 'hchucks', 'chqucks', 'chcks', 'chucksy', 'chnucks', 'chuqcks',
                          'chuccs', 'chuvks', 'chucksm', 'chuctks', 'tchucks', 'chucksc', 'chumks', 'chucjks',
                          'chuecks', 'chuicks', 'chuzks', 'chubcks', 'chucgs', 'cahucks', 'chjucks', 'chaucks',
                          'chgucks', 'lhucks', 'chucoks', 'chzcks', 'chtucks', 'chuckt', 'fhucks', 'chufcks', 'chocks',
                          'cvhucks', 'chucksi', 'thucks', 'chunks', 'chutks', 'csucks', 'chucys', 'chvcks', 'kchucks',
                          'chuxcks', 'cjucks', 'cyhucks', 'mhucks', 'chuccks', 'chuckz', 'chuckas', 'chqcks', 'vchucks',
                          'ceucks', 'dhucks', 'uhucks', 'chucmks', 'chucxks', 'chucka', 'chujks', 'chkcks', 'chudks',
                          'chucpks', 'wchucks', 'czucks', 'cxhucks', 'chucss', 'chusks', 'chuckx', 'chuycks', 'chwucks',
                          'chuncks', 'chucqs', 'cyucks', 'chupcks', 'chulcks', 'chcucks', 'cihucks', 'chucis',
                          'chuckds', 'chtcks', 'chhucks', 'chwcks', 'chuucks', 'choucks', 'khucks', 'chucksw', 'cxucks',
                          'chzucks', 'chvucks', 'chucki', 'chucas', 'cchucks', 'chuclks', 'chucksq', 'cohucks',
                          'chulks', 'chjcks', 'chucksp', 'chucaks', 'coucks', 'chuckxs', 'chucksx', 'chuckss',
                          'chsucks', 'cshucks', 'chucps', 'chucksz', 'crhucks', 'ehucks', 'chuqks', 'chuckrs', 'ciucks',
                          'chuckvs', 'chucts', 'chucksl', 'fchucks', 'cnhucks', 'ichucks', 'chpcks', 'chacks',
                          'cjhucks', 'chuhcks', 'chucky', 'chuchks', 'chuckl', 'cmucks', 'chuvcks', 'chucus', 'chccks',
                          'chuckls', 'chuckcs', 'chuyks', 'rhucks', 'chumcks', 'chucksr', 'chuckj', 'chxucks', 'chuckn',
                          'chucksn', 'chucksv', 'chducks', 'xhucks', 'chucws', 'chuckr', 'chuckhs', 'chuckm', 'chuckes',
                          'chucqks', 'chuckfs', 'chuces', 'cvucks', 'chucls', 'uchucks', 'chlcks', 'chuczs', 'chucksg',
                          'chuckws', 'chuckv', 'mchucks', 'chuxks', 'chuckk', 'ctucks', 'chuckst', 'chuhks', 'chucksu',
                          'chscks', 'chncks', 'chucxs', 'cmhucks', 'chpucks', 'chucns', 'chyucks', 'chuacks', 'chufks',
                          'chucke', 'chucksd', 'cehucks', 'chucyks', 'gchucks', 'chucds', 'cghucks', 'chuckf', 'chucrs',
                          'chuckks', 'chuckb', 'chutcks', 'chuckd', 'zhucks', 'cphucks', 'cuucks', 'ccucks', 'chbcks',
                          'chucms', 'chucvs', 'chuckms', 'clucks', 'cheucks', 'chudcks', 'chuckg', 'chuckq', 'chmcks',
                          'chuscks', 'chucuks', 'chuckis', 'cqucks', 'chucnks', 'chuwcks', 'chuckns', 'cdhucks',
                          'chucbks', 'whucks', 'chfcks', 'yhucks', 'chmucks', 'chuckys', 'ckucks', 'chucsks', 'chycks',
                          'chubks', 'chucksf', 'cuhucks', 'cwucks', 'chucos', 'chuckps', 'dchucks', 'cthucks',
                          'zchucks', 'chuckse', 'chiucks', 'chucfs', 'chucku', 'qhucks', 'chuckc', 'chrucks', 'chucbs',
                          'bhucks', 'pchucks', 'chucko', 'chucrks', 'chucwks', 'chucksk', 'phucks', 'cgucks', 'chugks',
                          'chdcks', 'cbhucks', 'chhcks', 'cfhucks', 'chuckw', 'cnucks', 'chucksj', 'qchucks', 'cfucks',
                          'cwhucks', 'chicks', 'chuckqs', 'chuczks', 'ahucks', 'chucdks', 'lchucks', 'chgcks', 'chucjs',
                          'crucks', 'ychucks', 'achucks', 'chuckzs', 'nhucks', 'chueks', 'schucks', 'chfucks',
                          'ckhucks', 'caucks', 'chukks', 'chucvks', 'chuciks', 'chucksb', 'chuckh', 'churks', 'chuzcks',
                          'chuckso', 'chuckus', 'jhucks', 'chucksa', 'chuwks', 'chugcks', 'chucfks', 'cducks',
                          'echucks', 'jchucks', 'chxcks', 'chuckbs', 'bchucks', 'ohucks', 'chujcks', 'ghucks', 'chuchs',
                          'chuocks', 'chuoks', 'ochucks', 'chuaks', 'chuuks', 'checks', 'chuckts', 'cqhucks', 'chuckos',
                          'rchucks', 'chuckgs', 'cpucks', 'chucgks', 'nchucks', 'chucksh', 'chuiks', 'churcks',
                          'xchucks', 'chuckjs', 'chuckp', 'chkucks', 'ch6cks', 'ch7cks', 'ch8cks', 'ch^cks', 'ch&cks',
                          'ch*cks', 'chuc.s', 'chuc,s', 'chuc>s', 'chuc<s', 'monkey', 'mone', 'mony', 'mnoey', 'zmoney',
                          'poney', 'movney', 'moncey', 'mgney', 'wmoney', 'monet', 'monky', 'moneya', 'modey', 'mney',
                          'monny', 'monye', 'moey', 'qoney', 'moeny', 'moxney', 'mqoney', 'monejy', 'oney', 'monmey',
                          'moneye', 'emoney', 'qmoney', 'mjoney', 'moneyy', 'maney', 'mouney', 'mcney', 'monjy',
                          'omney', 'monsey', 'moneyp', 'monesy', 'joney', 'monely', 'monyey', 'yoney', 'smoney',
                          'monez', 'monney', 'mouey', 'zoney', 'monej', 'monby', 'moneyd', 'moaey', 'monhey', 'moneiy',
                          'mozey', 'moneqy', 'motey', 'moneyi', 'moneyq', 'monep', 'mtney', 'monfey', 'mmoney', 'moqey',
                          'soney', 'monefy', 'boney', 'moxey', 'mogney', 'monqey', 'moneym', 'aoney', 'moneky',
                          'monedy', 'mxoney', 'mogey', 'monef', 'moyey', 'mponey', 'mones', 'monen', 'gmoney', 'moneyk',
                          'monwy', 'doney', 'moneyx', 'mofey', 'monly', 'moyney', 'mokey', 'foney', 'movey', 'mkney',
                          'mioney', 'monel', 'moneny', 'moner', 'monfy', 'mzney', 'muoney', 'mmney', 'maoney', 'momney',
                          'honey', 'moley', 'mnney', 'moniy', 'moneg', 'mzoney', 'mvoney', 'monewy', 'momey', 'monepy',
                          'mwney', 'voney', 'mdoney', 'monwey', 'mobney', 'monoey', 'mrney', 'moneh', 'mopney', 'monek',
                          'montey', 'muney', 'monezy', 'mfoney', 'monery', 'monew', 'mowey', 'monzy', 'kmoney', 'monvy',
                          'mofney', 'moneyf', 'mohey', 'moiney', 'monuy', 'mgoney', 'meoney', 'moeney', 'molney',
                          'moneyv', 'amoney', 'omoney', 'moneyh', 'mjney', 'miney', 'monhy', 'tmoney', 'moneyl',
                          'mongey', 'dmoney', 'koney', 'mocney', 'mojney', 'monevy', 'monty', 'mqney', 'mconey',
                          'lmoney', 'imoney', 'monex', 'mowney', 'moned', 'moneu', 'rmoney', 'moneyu', 'loney',
                          'monxey', 'moqney', 'monjey', 'monsy', 'hmoney', 'monegy', 'mpney', 'monety', 'mobey',
                          'mosey', 'morney', 'moniey', 'woney', 'moiey', 'moneyb', 'monexy', 'noney', 'monzey', 'msney',
                          'ooney', 'monyy', 'meney', 'mnoney', 'xmoney', 'mtoney', 'toney', 'myney', 'bmoney', 'coney',
                          'monecy', 'moaney', 'mopey', 'uoney', 'morey', 'monpy', 'mhoney', 'moeey', 'monxy', 'mongy',
                          'monay', 'monea', 'mooney', 'modney', 'mokney', 'mooey', 'monry', 'monev', 'moneuy', 'xoney',
                          'mloney', 'monmy', 'mkoney', 'monpey', 'mhney', 'monee', 'monuey', 'moneyr', 'monoy', 'mdney',
                          'moneyo', 'moneby', 'jmoney', 'fmoney', 'moneyn', 'moneys', 'mvney', 'moneyt', 'moneyc',
                          'goney', 'moneey', 'moneo', 'msoney', 'mwoney', 'mroney', 'mbney', 'cmoney', 'moneq', 'moncy',
                          'monemy', 'monec', 'mboney', 'mxney', 'monley', 'monaey', 'mocey', 'mondey', 'ioney',
                          'umoney', 'myoney', 'moneyg', 'vmoney', 'mlney', 'roney', 'moneoy', 'motney', 'monem',
                          'mosney', 'mohney', 'moneay', 'mondy', 'monvey', 'eoney', 'monei', 'monqy', 'nmoney', 'moneb',
                          'mojey', 'moneyz', 'moneyw', 'mfney', 'mozney', 'monehy', 'pmoney', 'monbey', 'monrey',
                          'ymoney', 'moneyj', ',oney', '<oney', 'm8ney', 'm9ney', 'm0ney', 'm;ney', 'm*ney', 'm(ney',
                          'm)ney', 'mo,ey', 'mo<ey', 'mon4y', 'mon3y', 'mon2y', 'mon$y', 'mon#y', 'mon@y', 'mone5',
                          'mone6', 'mone7', 'mone%', 'mone^', 'mone&', 'currdency', 'currezcy', 'currencyr', 'curency',
                          'curredcy', 'currenc', 'currefncy', 'currebncy', 'curreyncy', 'crrency', 'ccurrency',
                          'currnecy', 'ucrrency', 'crrrency', 'curhency', 'currecy', 'currenyc', 'currescy', 'curvency',
                          'crurency', 'currwncy', 'curruncy', 'curlency', 'curreny', 'currepncy', 'churrency',
                          'xurrency', 'curreuncy', 'curerncy', 'acurrency', 'kcurrency', 'cuwrency', 'eurrency',
                          'currenacy', 'curarency', 'curcrency', 'currekcy', 'currncy', 'cuarency', 'currenkcy',
                          'currecny', 'currbncy', 'currsncy', 'curruency', 'zcurrency', 'currencqy', 'currencd',
                          'currewcy', 'cvrrency', 'currencye', 'urrency', 'purrency', 'currenmy', 'cerrency',
                          'ckrrency', 'currcncy', 'curyrency', 'currehncy', 'ourrency', 'currenlcy', 'currencyo',
                          'ncurrency', 'currelncy', 'durrency', 'cuerrency', 'currencay', 'currvency', 'currencn',
                          'curregncy', 'nurrency', 'currdncy', 'curorency', 'curbrency', 'cuhrency', 'curreccy',
                          'currancy', 'ecurrency', 'cfrrency', 'curfrency', 'cururency', 'currencuy', 'currencj',
                          'cmrrency', 'currencya', 'currencyc', 'wcurrency', 'curqrency', 'cxrrency', 'curreqcy',
                          'currekncy', 'curreqncy', 'cuarrency', 'curdency', 'currenvcy', 'curwency', 'currefcy',
                          'currengy', 'lcurrency', 'currmency', 'curxency', 'currencry', 'cuurrency', 'curnency',
                          'currlncy', 'scurrency', 'currenqcy', 'curmency', 'cuorency', 'cursency', 'currenrcy',
                          'currgency', 'currencyh', 'cdrrency', 'currxncy', 'currqncy', 'cuyrrency', 'cwurrency',
                          'gurrency', 'curroency', 'currencv', 'cjrrency', 'curgrency', 'currenuy', 'currencyp',
                          'curryency', 'cufrrency', 'currenry', 'currencyd', 'cuzrrency', 'cirrency', 'curuency',
                          'currencwy', 'curxrency', 'currenscy', 'currenqy', 'hurrency', 'cqurrency', 'curreincy',
                          'curqency', 'murrency', 'currfency', 'currxency', 'pcurrency', 'curgency', 'curroncy',
                          'curvrency', 'curzrency', 'clrrency', 'czrrency', 'currenchy', 'czurrency', 'curreniy',
                          'rurrency', 'cvurrency', 'currencsy', 'currlency', 'curiency', 'currenicy', 'cunrency',
                          'curresncy', 'currencu', 'cdurrency', 'cubrency', 'currencc', 'cuerency', 'currkncy',
                          'currencs', 'currencb', 'currenbcy', 'ceurrency', 'curmrency', 'currencyg', 'currencq',
                          'currpency', 'curzency', 'currenca', 'cucrency', 'currpncy', 'currejncy', 'cunrrency',
                          'curretcy', 'currelcy', 'currencr', 'currrency', 'cutrrency', 'currenjy', 'currmncy',
                          'cursrency', 'lurrency', 'currincy', 'currenct', 'curjency', 'zurrency', 'currencx',
                          'cudrrency', 'curreucy', 'currepcy', 'currencyn', 'cuyrency', 'curnrency', 'corrency',
                          'currerncy', 'curyency', 'cjurrency', 'iurrency', 'currenciy', 'currenycy', 'currexncy',
                          'currezncy', 'cbrrency', 'aurrency', 'curprency', 'currencyy', 'currencxy', 'kurrency',
                          'currencyz', 'curraency', 'currenby', 'curredncy', 'qurrency', 'cubrrency', 'cumrency',
                          'currencyx', 'currengcy', 'currtency', 'ctrrency', 'currencjy', 'wurrency', 'currencny',
                          'cxurrency', 'dcurrency', 'cugrency', 'currencw', 'cmurrency', 'currenck', 'chrrency',
                          'curdrency', 'curreoncy', 'currencoy', 'currenyy', 'currenay', 'curaency', 'currevcy',
                          'cujrency', 'cukrency', 'cgurrency', 'currenjcy', 'currenxy', 'currzncy', 'ucurrency',
                          'curerency', 'currenccy', 'currhncy', 'currexcy', 'currgncy', 'curryncy', 'currjncy',
                          'icurrency', 'currwency', 'cusrrency', 'courrency', 'curremncy', 'currencz', 'fcurrency',
                          'ckurrency', 'furrency', 'currvncy', 'yurrency', 'cuxrency', 'currenzy', 'currenncy',
                          'currencky', 'currnncy', 'cuxrrency', 'curirency', 'cutrency', 'currjency', 'currcency',
                          'burrency', 'currencyw', 'cuvrency', 'gcurrency', 'currenwy', 'caurrency', 'curtency',
                          'cuprrency', 'cureency', 'surrency', 'currencys', 'currenmcy', 'cgrrency', 'ocurrency',
                          'csrrency', 'currtncy', 'currencyv', 'currenzcy', 'currencp', 'currencvy', 'cuqrency',
                          'cuqrrency', 'curremcy', 'cuurency', 'curreocy', 'currencm', 'curkency', 'xcurrency',
                          'currenwcy', 'clurrency', 'currzency', 'qcurrency', 'currenxcy', 'currencey', 'cucrrency',
                          'currenvy', 'currenpcy', 'vurrency', 'curpency', 'carrency', 'cuzrency', 'bcurrency',
                          'curreecy', 'cudrency', 'currencyf', 'ycurrency', 'currenpy', 'cuvrrency', 'currencl',
                          'curcency', 'currencyl', 'currendy', 'curreacy', 'cprrency', 'currqency', 'currentcy',
                          'currence', 'cuwrrency', 'cyurrency', 'currenco', 'currencpy', 'mcurrency', 'currenny',
                          'crurrency', 'currkency', 'cqrrency', 'currenocy', 'currendcy', 'curfency', 'currebcy',
                          'currenucy', 'currencly', 'curreney', 'currenczy', 'cuirency', 'cumrrency', 'currenfcy',
                          'currencym', 'cuirrency', 'culrrency', 'currenhy', 'cfurrency', 'currbency', 'curreicy',
                          'currencg', 'currencyk', 'currensy', 'currehcy', 'currencyj', 'cwrrency', 'currenecy',
                          'curkrency', 'currenci', 'currench', 'currercy', 'turrency', 'currencdy', 'currencyu',
                          'currhency', 'curoency', 'cturrency', 'currevncy', 'cyrrency', 'jcurrency', 'cukrrency',
                          'currenly', 'cuprency', 'curbency', 'currencby', 'currencyi', 'tcurrency', 'cusrency',
                          'currenhcy', 'curregcy', 'cuorrency', 'curtrency', 'currejcy', 'cnurrency', 'hcurrency',
                          'curhrency', 'curreancy', 'cnrrency', 'currenky', 'culrency', 'cugrrency', 'uurrency',
                          'currencmy', 'currfncy', 'cufrency', 'curreycy', 'currenty', 'jurrency', 'ccrrency',
                          'ciurrency', 'cburrency', 'curretncy', 'currecncy', 'currencyq', 'curreency', 'vcurrency',
                          'currencty', 'currencyb', 'cuhrrency', 'rcurrency', 'csurrency', 'curwrency', 'cpurrency',
                          'currenfy', 'currencf', 'currencfy', 'currencyt', 'currewncy', 'currencgy', 'curlrency',
                          'cujrrency', 'curjrency', 'currsency', 'currnency', 'currrncy', 'curriency', 'currenoy',
                          'c6rrency', 'c7rrency', 'c8rrency', 'c^rrency', 'c&rrency', 'c*rrency', 'cu3rency',
                          'cu4rency', 'cu5rency', 'cu#rency', 'cu$rency', 'cu%rency', 'cur3ency', 'cur4ency',
                          'cur5ency', 'cur#ency', 'cur$ency', 'cur%ency', 'curr4ncy', 'curr3ncy', 'curr2ncy',
                          'curr$ncy', 'curr#ncy', 'curr@ncy', 'curre,cy', 'curre<cy', 'currenc5', 'currenc6',
                          'currenc7', 'currenc%', 'currenc^', 'currenc&', 'cah', 'cashp', 'cas', 'yash', 'csh', 'ash',
                          'cask', 'casmh', 'cahsh', 'ncash', 'zcash', 'rcash', 'caswh', 'caoh', 'cafh', 'hash', 'cosh',
                          'cahs', 'crsh', 'acsh', 'canh', 'chash', 'uash', 'casz', 'caush', 'ciash', 'cagsh', 'aash',
                          'clsh', 'csah', 'casnh', 'caslh', 'cawh', 'ckash', 'cajsh', 'cawsh', 'kash', 'casuh', 'cysh',
                          'kcash', 'cpsh', 'cashh', 'cast', 'casoh', 'cach', 'cqash', 'cashe', 'cqsh', 'ctash', 'cksh',
                          'casch', 'casi', 'casa', 'ceash', 'coash', 'cashx', 'czash', 'cath', 'cazsh', 'camh', 'casj',
                          'mcash', 'casyh', 'cashn', 'cjsh', 'cadsh', 'cashm', 'ecash', 'cashu', 'casha', 'cayh',
                          'casn', 'tash', 'cxash', 'cass', 'cwsh', 'casc', 'caash', 'caesh', 'cjash', 'cbsh', 'casv',
                          'pcash', 'iash', 'casbh', 'cish', 'cfsh', 'caah', 'casq', 'cnsh', 'cashl', 'cabsh', 'casu',
                          'casah', 'caeh', 'caseh', 'cwash', 'cabh', 'cafsh', 'casgh', 'lcash', 'caskh', 'rash', 'pash',
                          'mash', 'caxh', 'acash', 'cashr', 'ccash', 'wash', 'cagh', 'xash', 'cmash', 'cnash', 'calsh',
                          'casy', 'casp', 'casm', 'casr', 'caih', 'vcash', 'dash', 'icash', 'caqh', 'cdsh', 'cashd',
                          'casfh', 'clash', 'cadh', 'camsh', 'casx', 'casph', 'hcash', 'wcash', 'xcash', 'cashb',
                          'catsh', 'carsh', 'caszh', 'crash', 'bash', 'czsh', 'ocash', 'cashj', 'lash', 'carh', 'casb',
                          'case', 'scash', 'ycash', 'cavh', 'cashv', 'caxsh', 'cvash', 'cavsh', 'cashi', 'cashq',
                          'nash', 'cakh', 'cdash', 'zash', 'eash', 'cssh', 'cashy', 'cuash', 'vash', 'capsh', 'jcash',
                          'casth', 'ctsh', 'cacsh', 'casht', 'caph', 'calh', 'casxh', 'fcash', 'casvh', 'cahh', 'cgash',
                          'casho', 'tcash', 'cansh', 'casw', 'caksh', 'casg', 'qash', 'cassh', 'casl', 'cajh', 'casd',
                          'cgsh', 'casih', 'ccsh', 'bcash', 'caysh', 'cyash', 'gash', 'fash', 'cpash', 'cashc', 'casf',
                          'caosh', 'cauh', 'cashw', 'caqsh', 'casqh', 'caish', 'caso', 'casjh', 'cashs', 'cush',
                          'casrh', 'cesh', 'sash', 'oash', 'cazh', 'casdh', 'cashk', 'gcash', 'cfash', 'cashg', 'cbash',
                          'jash', 'cmsh', 'cvsh', 'qcash', 'ucash', 'cxsh', 'cashz', 'csash', 'chsh', 'dcash', 'cashf',
                          'vyx', 'vcbx', 'jbx', 'vnx', 'vbxt', 'vbk', 'uvbx', 'vxb', 'dvbx', 'bx', 'vbxf', 'kbx',
                          'vbxs', 'bvx', 'vbq', 'vbp', 'sbx', 'vbnx', 'zvbx', 'cvbx', 'vbr', 'evbx', 'ybx', 'zbx',
                          'hvbx', 'vbxy', 'vx', 'vbe', 'vbm', 'vbl', 'vbyx', 'wbx', 'kvbx', 'vnbx', 'bvbx', 'qvbx',
                          'vvx', 'vbjx', 'vbax', 'vbxk', 'vwx', 'vbxh', 'vvbx', 'fbx', 'ubx', 'ivbx', 'vbwx', 'vbf',
                          'vbxm', 'vbix', 'vbxe', 'jvbx', 'vzx', 'vbx', 'vby', 'vlbx', 'vbex', 'vex', 'vbxq', 'vbbx',
                          'vbxj', 'pbx', 'vbqx', 'vpbx', 'vhx', 'gbx', 'vxbx', 'vba', 'vbcx', 'wvbx', 'vbxd', 'ovbx',
                          'rbx', 'lbx', 'vbxu', 'dbx', 'vbzx', 'vjx', 'vqbx', 'vbw', 'vcx', 'vkx', 'ebx', 'vfbx', 'obx',
                          'vbdx', 'vix', 'bbx', 'vbxg', 'vsx', 'vbrx', 'vmbx', 'vubx', 'vbi', 'vbxr', 'nvbx', 'vbs',
                          'vdx', 'vwbx', 'cbx', 'abx', 'vbg', 'vbd', 'vgx', 'vbz', 'vbpx', 'vbxx', 'qbx', 'vbxb',
                          'vbfx', 'vbmx', 'vxx', 'vbj', 'vmx', 'vbux', 'vbxv', 'vbb', 'vax', 'hbx', 'vrx', 'vox', 'vbn',
                          'vbxo', 'tvbx', 'vjbx', 'vbhx', 'vybx', 'vzbx', 'vbtx', 'lvbx', 'vbvx', 'vblx', 'vbv', 'vbxw',
                          'vlx', 'vdbx', 'svbx', 'vrbx', 'gvbx', 'rvbx', 'vbh', 'vabx', 'vbxl', 'vhbx', 'vbox', 'mvbx',
                          'vbt', 'vobx', 'vbsx', 'xbx', 'vbc', 'nbx', 'vqx', 'vsbx', 'vbxz', 'pvbx', 'ibx', 'avbx',
                          'vpx', 'vbkx', 'vbxa', 'vux', 'tbx', 'vbo', 'vbxi', 'vkbx', 'vbgx', 'vfx', 'vtbx', 'vebx',
                          'vgbx', 'vibx', 'fvbx', 'xvbx', 'vbxn', 'vbxp', 'yvbx', 'vbxc', 'cedits', 'crdeits',
                          'crwdits', 'credit', 'crediwts', 'credts', 'creiits', 'cerdits', 'crtedits', 'crfdits',
                          'creidts', 'cyredits', 'credits', 'crjedits', 'creditzs', 'creits', 'crrdits', 'credtis',
                          'credist', 'crbdits', 'bredits', 'rcedits', 'credyits', 'crediks', 'creditqs', 'credis',
                          'crdits', 'creditms', 'yredits', 'cretdits', 'creditq', 'cqedits', 'czedits', 'creditds',
                          'csedits', 'cremdits', 'credhits', 'crkdits', 'credrts', 'credjts', 'credbits', 'rredits',
                          'credixts', 'crewdits', 'redits', 'creduts', 'crediyts', 'crediuts', 'crfedits', 'credids',
                          'credizs', 'ctedits', 'crediats', 'credyts', 'crgedits', 'ciredits', 'creditsc', 'crnedits',
                          'creqits', 'creditk', 'crefits', 'creditp', 'crvedits', 'dcredits', 'crmedits', 'creditss',
                          'crediys', 'nredits', 'creditsm', 'coredits', 'wcredits', 'crjdits', 'kredits', 'creditsp',
                          'ccedits', 'lredits', 'crledits', 'creditos', 'creditsy', 'ecredits', 'creidits', 'credkts',
                          'crecits', 'qcredits', 'aredits', 'crdedits', 'cretits', 'curedits', 'credvts', 'credite',
                          'crudits', 'fcredits', 'credsts', 'iredits', 'credita', 'crediqs', 'cwredits', 'crezits',
                          'creditls', 'creditys', 'creditsi', 'lcredits', 'crehits', 'tredits', 'creditis', 'gredits',
                          'credsits', 'credigs', 'creldits', 'crndits', 'cuedits', 'crediti', 'crediis', 'creditvs',
                          'xredits', 'creditd', 'jredits', 'cregdits', 'vredits', 'creditsv', 'credidts', 'creditw',
                          'creaits', 'jcredits', 'cresits', 'crediits', 'creditgs', 'creditsg', 'credpts', 'credims',
                          'wredits', 'cruedits', 'creduits', 'creditsh', 'creyits', 'creditg', 'xcredits', 'creditsr',
                          'hredits', 'qredits', 'cregits', 'crediets', 'creditsf', 'credivts', 'credwts', 'oredits',
                          'cjredits', 'cnedits', 'credimts', 'hcredits', 'credmts', 'crerits', 'crzedits', 'cpedits',
                          'caedits', 'creditj', 'crbedits', 'credots', 'fredits', 'creedits', 'cyedits', 'ckredits',
                          'crqedits', 'creudits', 'credqts', 'crekits', 'credius', 'scredits', 'sredits', 'credibs',
                          'creditcs', 'creditsj', 'creditl', 'credpits', 'credixs', 'crmdits', 'crepits', 'cledits',
                          'clredits', 'credirts', 'crsdits', 'credifts', 'crenits', 'ycredits', 'crevdits', 'creditsu',
                          'gcredits', 'crsedits', 'mcredits', 'crxdits', 'creditt', 'credhts', 'crediqts', 'creditm',
                          'credies', 'creditsw', 'credzts', 'creditsb', 'crddits', 'crediws', 'crhedits', 'cxedits',
                          'creditsl', 'chedits', 'creditsa', 'credils', 'acredits', 'creditns', 'credith', 'cvredits',
                          'credtts', 'ccredits', 'crekdits', 'creditst', 'credcts', 'credoits', 'credios', 'crepdits',
                          'credihts', 'crexits', 'chredits', 'creditsx', 'crldits', 'creditx', 'creditr', 'pcredits',
                          'crodits', 'cbedits', 'ckedits', 'crednits', 'crqdits', 'cgedits', 'credigts', 'credivs',
                          'mredits', 'credity', 'crerdits', 'crejdits', 'dredits', 'credijs', 'creditsk', 'creditts',
                          'creditfs', 'creditz', 'credfts', 'cridits', 'creoits', 'credists', 'credets', 'creqdits',
                          'creydits', 'croedits', 'credjits', 'cfedits', 'crefdits', 'creditf', 'creuits', 'crvdits',
                          'creditbs', 'crexdits', 'cvedits', 'creditc', 'credqits', 'credikts', 'creditps', 'creditso',
                          'cryedits', 'crebdits', 'credizts', 'credifs', 'crednts', 'credgits', 'crtdits', 'cpredits',
                          'crwedits', 'zcredits', 'crediss', 'credites', 'creditws', 'cqredits', 'crpedits', 'kcredits',
                          'cxredits', 'crevits', 'credeits', 'craedits', 'credbts', 'crewits', 'cresdits', 'creditxs',
                          'cradits', 'creditjs', 'crediths', 'crebits', 'credirs', 'creditks', 'coedits', 'creditrs',
                          'ncredits', 'creddts', 'crcedits', 'credvits', 'crkedits', 'credkits', 'crehdits', 'cdedits',
                          'ceredits', 'ciedits', 'cbredits', 'credints', 'credtits', 'crxedits', 'cnredits', 'cmedits',
                          'credxits', 'cgredits', 'ctredits', 'credihs', 'creditsz', 'criedits', 'icredits', 'credxts',
                          'ceedits', 'creditv', 'zredits', 'tcredits', 'credias', 'caredits', 'ucredits', 'crgdits',
                          'creditsq', 'credgts', 'credito', 'crredits', 'creodits', 'creddits', 'eredits', 'crpdits',
                          'credicts', 'creditse', 'cwedits', 'czredits', 'cmredits', 'crejits', 'crzdits', 'credfits',
                          'crezdits', 'predits', 'cjedits', 'credipts', 'ocredits', 'credwits', 'crelits', 'crecdits',
                          'credins', 'creditas', 'cfredits', 'creditn', 'creditu', 'creditus', 'creadits', 'credics',
                          'crhdits', 'rcredits', 'credrits', 'uredits', 'crydits', 'creditsd', 'cremits', 'credlits',
                          'credmits', 'crendits', 'credaits', 'credcits', 'crcdits', 'credilts', 'creditb', 'credlts',
                          'bcredits', 'cdredits', 'credzits', 'credats', 'vcredits', 'csredits', 'crediots', 'credijts',
                          'creeits', 'credibts', 'creditsn', 'credips', 'c3edits', 'c4edits', 'c5edits', 'c#edits',
                          'c$edits', 'c%edits', 'cr4dits', 'cr3dits', 'cr2dits', 'cr$dits', 'cr#dits', 'cr@dits',
                          'cred7ts', 'cred8ts', 'cred9ts', 'cred&ts', 'cred*ts', 'cred(ts', 'credi4s', 'credi5s',
                          'credi6s', 'credi$s', 'credi%s', 'credi^s', '/vbucc', '/v-bucc', '/mtx', '/money',
                          '/currency', '/cash', '/vbx', '/credits'],
                 extras={'emoji': "vbuck_book", "args": {
                     'generic.meta.args.authcode': ['generic.slash.token', True],
                     'generic.meta.args.optout': ['generic.slash.optout', True]
                 }, "dev": False, "description_keys": ["vbucks.meta.description"], "name_key": "vbucks.slash.name"},
                 brief="vbucks.meta.brief",
                 description="{0}")
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

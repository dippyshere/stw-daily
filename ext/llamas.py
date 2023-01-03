"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the homebase command. renames homebase / displays current name + renders banner
"""
import asyncio
import time

import discord
import discord.ext.commands as ext
from discord import Option, SelectOption
import orjson

import stwutil as stw


class LlamasView(discord.ui.View):
    """
    The view for the llama command.
    """

    def __init__(self, ctx, client, message, author, llama_store, free_llama, preroll_data, llama_options, auth_info):
        super().__init__()
        self.ctx = ctx
        self.client = client
        self.message = message
        self.author = author
        self.llama_store = llama_store
        self.free_llama = free_llama
        self.preroll_data = preroll_data
        self.interaction_check_done = {}
        self.children[0].options = llama_options
        self.auth_info = auth_info

    async def llama_purchase_embed(self, ctx, offer_id, select=True):
        """
        Creates an embed for the llama purchase command.

        Args:
            ctx: The context of the command.
            offer_id: The offer id of the llama to be purchased.
            select: Whether the embed is for the select menu.

        Returns:
            The embed with the llama details
        """
        if select:
            if offer_id == "back":
                self.children[0].options = await self.llamas.select_options_llamas(self.llama_store)
                return await self.llamas.llama_embed(ctx, self.free_llama, self.llama_store, self.preroll_data)
            else:
                self.children[0].options = await self.llamas.select_options_llamas(self.llama_store, True)
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Store", "llama"),
            description=f"\u200b\n",
            colour=self.client.colours["generic_blue"])
        for entry in self.llama_store["catalogEntries"]:
            if entry["offerId"] == offer_id:
                llama_datatable = await stw.get_llama_datatable(self.client, entry['displayAssetPath'].split('/Game/Items/CardPacks/')[-1].split('.')[0])
                embed.description = f"\u200b\n{llama_datatable[2]}{llama_datatable[3]} **{llama_datatable[0]}**\n"
                embed.description += f"Price: {'~~' + str(entry['prices'][0]['regularPrice']) + '~~ ' if entry['prices'][0]['regularPrice'] != entry['prices'][0]['finalPrice'] else ''}**{entry['prices'][0]['finalPrice']:,}** {stw.get_item_icon_emoji(self.client, entry['prices'][0]['currencySubType'])}\n"  # TODO: make this sale_sticker_store
                for attr, val in self.preroll_data.items():
                    if offer_id == val["attributes"]["offerId"]:
                        embed.description += "Contents: " + stw.llama_contents_render(self.client,
                                                                                      val["attributes"]["items"])
                        break
                embed.description += f"\n\n*{llama_datatable[1]}*\n"
                break
        embed.description += f"\u200b\n"
        embed.description = stw.truncate(embed.description, 3999)
        embed = await stw.set_thumbnail(self.client, embed, "upgrade_llama")
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command.

        Args:
            interaction: The interaction to check.

        Returns:
            True if the interaction is from the author of the command, False otherwise.
        """
        return await stw.view_interaction_check(self, interaction, "llamas")

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        if isinstance(self.ctx, discord.ApplicationContext):
            try:
                return await self.message.edit_original_response(view=self)
            except:
                return await self.ctx.edit(view=self)
        else:
            return await self.message.edit(view=self)

    @discord.ui.select(
        placeholder="Choose a Llama to purchase",
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a help page is selected.

        Args:
            select: The select menu that was used.
            interaction: The interaction that was used.
        """
        embed = await self.llama_purchase_embed(self.ctx, select.values[0])
        view = LlamasPurchaseView(self.ctx, self.client, self.message, self.author, self.llama_store, self.free_llama,
                                  self.preroll_data, select.values[0], self.auth_info)
        view.llamas = self.llamas
        view.llamaview = self
        await interaction.response.edit_message(embed=embed, view=view)


class LlamasPurchaseView(discord.ui.View):
    """
    The view for the llama purchase command.
    """

    def __init__(self, ctx, client, message, author, llama_store, free_llama, preroll_data, offer_id, auth_info):
        super().__init__()
        self.ctx = ctx
        self.client = client
        self.message = message
        self.author = author
        self.llama_store = llama_store
        self.free_llama = free_llama
        self.preroll_data = preroll_data
        self.offer_id = offer_id
        self.auth_info = auth_info
        self.confirm_stage = 0
        self.price = 0
        self.interaction_check_done = {}
        self.currency = ""
        self.contents = ""
        # self.children[0].options = await self.llamas.select_options_llamas(self.llama_store, True)

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        if isinstance(self.ctx, discord.ApplicationContext):
            try:
                return await self.message.edit_original_response(view=self)
            except:
                return await self.ctx.edit(view=self)
        else:
            return await self.message.edit(view=self)

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command.

        Args:
            interaction: The interaction to check.

        Returns:
            True if the interaction is from the author of the command, False otherwise.
        """
        return await stw.view_interaction_check(self, interaction, "llamas")

    @discord.ui.button(label="Purchase", style=discord.ButtonStyle.success)
    async def buy_button(self, button, interaction):
        """
        Called when the buy button is pressed.

        Args:
            button: The button that was pressed.
            interaction: The interaction that was used.
        """
        self.confirm_stage += 1
        if self.confirm_stage == 1:
            embed = await self.llama_purchase_confirm(self.ctx, self.offer_id)
            await interaction.response.edit_message(embed=embed, view=self)
        elif self.confirm_stage >= 2:
            embed = await self.llama_purchase_buy_embed(self.ctx, self.offer_id)
            await interaction.response.edit_message(embed=embed, view=None)
            shop_json_response = await stw.shop_request(self.client, self.auth_info["token"])
            populate_preroll_request = await stw.profile_request(self.client, "llamas", self.auth_info)
            populate_preroll_json = orjson.loads(await populate_preroll_request.read())
            self.preroll_data = stw.extract_profile_item(populate_preroll_json, "PrerollData")
            self.llama_store = await stw.get_llama_store(shop_json_response)
            self.free_llama = await stw.free_llama_count(self.llama_store)
            self.llamaview.preroll_data, self.llamaview.llama_store, self.llamaview.free_llama = self.preroll_data, self.llama_store, self.free_llama
            await asyncio.sleep(5.8)
            embed = await self.llamaview.llama_purchase_embed(self.ctx, "back")
            await stw.slash_edit_original(self.ctx, msg=self.message, embeds=embed, view=self.llamaview)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, button, interaction):
        """
        Called when the cancel button is pressed.

        Args:
            button: The button that was pressed.
            interaction: The interaction that was used.
        """
        self.confirm_stage -= 1
        if self.confirm_stage < 0:
            embed = await self.llamaview.llama_purchase_embed(self.ctx, "back")
            await interaction.response.edit_message(embed=embed, view=self.llamaview)
        else:
            embed = await self.llamaview.llama_purchase_embed(self.ctx, self.offer_id, False)
            await interaction.response.edit_message(embed=embed, view=self)

    async def llama_purchase_confirm(self, ctx, offer_id):
        """
        Creates an embed for the llama purchase confirmation.

        Args:
            ctx: The context of the command.
            offer_id: The offer id of the llama to be purchased.

        Returns:
            The embed with the llama purchase
        """
        article = "a"
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Store", "llama"),
            description=f"\u200b\n",
            colour=self.client.colours["generic_blue"])
        for entry in self.llama_store["catalogEntries"]:
            if entry["offerId"] == offer_id:
                llama_datatable = await stw.get_llama_datatable(self.client, entry['displayAssetPath'].split('/Game/Items/CardPacks/')[-1].split('.')[0])
                self.price = entry['prices'][0]['finalPrice']
                self.currency = entry['prices'][0]['currencySubType']
                for attr, val in self.preroll_data.items():
                    if offer_id == val["attributes"]["offerId"]:
                        self.contents = stw.llama_contents_render(self.client, val["attributes"]["items"])
                        break
                if llama_datatable[0][0].lower() in "aeiou":
                    article = "an"
                break
        embed.description += f"**Are you sure you want to purchase {article} {llama_datatable[0]} for {self.price} {stw.get_item_icon_emoji(self.client, self.currency)}?**\n\u200b"
        embed = await stw.set_thumbnail(self.client, embed, "upgrade_llama")
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def llama_purchase_buy_embed(self, ctx, offer_id):
        """
        Creates an embed for the llama purchase.

        Args:
            ctx: The context of the command.
            offer_id: The offer id of the llama to be purchased.

        Returns:
            The embed with the llama purchase
        """
        purchase = await stw.purchase_llama(self.client, self.auth_info, offer_id, currencySubType=self.currency,
                                            expectedTotalPrice=self.price)
        try:
            error_code = purchase["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = self.auth_info["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "llamas", acc_name, error_code, support_url)
            print("Error:", purchase)
        except:
            embed = discord.Embed(
                title=await stw.add_emoji_title(self.client, "Store", "llama"),
                description=f"\u200b\n**Successfully purchased Llama!**\n"
                            f"{'You got: ' + self.contents if self.contents != '' else ''}\nReturning <t:{int(time.time()) + 6}:R>\n\u200b",
                colour=self.client.colours["generic_blue"])
            # print("Success:", purchase)
        embed = await stw.set_thumbnail(self.client, embed, "upgrade_llama")
        embed = await stw.add_requested_footer(ctx, embed)
        return embed


# ok i have no clue how sets work in python ok now i do prepare for your cpu to explode please explode already smhhh nya hi
class Llamas(ext.Cog):
    """
    Cog for the llama command
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
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "llamas", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
            return True
        except KeyError:
            # no error
            return False

    async def select_options_llamas(self, llama_store, return_visible=False):
        """
        Creates the options for the select menu for the llamas command.

        Args:
            llama_store: The llama store data.
            return_visible: Whether the return value should be the visible options or the hidden options.

        Returns:
            The options for the select menu.
        """
        options = []
        if return_visible:
            options.append(SelectOption(label="Return", value="back", emoji=self.emojis["left_arrow"],
                                        description="Return to the shop"))
        for entry in llama_store["catalogEntries"]:
            if entry['devName'] == "Always.UpgradePack.03":
                continue
            llama_datatable = await stw.get_llama_datatable(self.client,
                                                            entry['displayAssetPath'].split('/Game/Items/CardPacks/')[
                                                                -1].split('.')[0])
            options.append(discord.SelectOption(label=llama_datatable[0], value=entry['offerId'],
                                                description=f"Price: {entry['prices'][0]['finalPrice']:,}",
                                                emoji=llama_datatable[2]))
        return options

    async def llama_entry(self, catalog_entry, client):
        """
        Creates an embed entry string for a single llama catalog entry.

        Args:
            catalog_entry: The catalog entry to be processed.
            client: The bot client.

        Returns:
            The embed entry string.
        """
        llama_datatable = await stw.get_llama_datatable(self.client, catalog_entry['displayAssetPath'].split('/Game/Items/CardPacks/')[-1].split('.')[0])
        entry_string = f"\u200b\n{llama_datatable[2]}{llama_datatable[3]} **{llama_datatable[0]}**\n"
        # entry_string += f"Rarity: {catalog_entry['itemGrants'][0]['templateId'].split('CardPack:cardpack_')[1]}\n"
        entry_string += f"Price: {'~~' + str(catalog_entry['prices'][0]['regularPrice']) + '~~ ' if catalog_entry['prices'][0]['regularPrice'] != catalog_entry['prices'][0]['finalPrice'] else ''}**{catalog_entry['prices'][0]['finalPrice']:,}** {stw.get_item_icon_emoji(client, catalog_entry['prices'][0]['currencySubType'])} \n"
        # entry_string += f"OfferID: {catalog_entry['offerId']}\n"
        # entry_string += f"Dev name: {catalog_entry['devName']}\n"
        # entry_string += f"Daily limit: {catalog_entry['dailyLimit']}\n"
        # entry_string += f"Event limit: {catalog_entry['meta']['EventLimit']}\n"
        # entry_string += f"Icon: {catalog_entry['displayAssetPath'].split('/Game/Items/CardPacks/')[-1].split('.')[0]}\n"
        return entry_string

    async def llama_embed(self, ctx, free_llama, llama_store, preroll_data):
        """
        Creates the embed for the llama command.

        Args:
            ctx: The context of the command.
            free_llama: The free llama data.
            llama_store: The llama store data.
            preroll_data: The preroll data.

        Returns:
            The embed.
        """
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Store", "llama"),
            description=f"\u200b\nHere's the current shop:\u200b\n\u200b",
            colour=self.client.colours["generic_blue"])
        if free_llama[0] > 0:
            embed.description += f"\u200b\n{self.client.config['emojis']['new_item_store']} **There is a free llama available!** {self.client.config['emojis']['new_item_store']}\n"
        for entry in llama_store["catalogEntries"]:
            if entry['devName'] == "Always.UpgradePack.03":
                continue
            embed.description += await self.llama_entry(entry, self.client)
            for attr, val in preroll_data.items():  # :>
                if entry["offerId"] == val["attributes"]["offerId"]:
                    embed.description += "Contents: " + stw.llama_contents_render(self.client,
                                                                                  val["attributes"]["items"])
                    break
            embed.description += f"\n"
        embed.description += f"\u200b\n"
        embed.description = stw.truncate(embed.description, 3999)
        embed = await stw.set_thumbnail(self.client, embed, "upgrade_llama")
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def llamas_command(self, ctx, authcode, auth_opt_out):
        """
        The main function for the llamas command.

        Args:
            ctx: The context of the command.
            authcode: The authcode of the account.
            auth_opt_out: Whether the user has opted out of auth.

        Returns:
            None
        """
        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "llamas", authcode, auth_opt_out, True)
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

        shop_json_response = await stw.shop_request(self.client, auth_info[1]["token"])

        populate_preroll_request = await stw.profile_request(self.client, "llamas", auth_info[1])
        populate_preroll_json = orjson.loads(await populate_preroll_request.read())
        preroll_data = stw.extract_profile_item(populate_preroll_json, "PrerollData")

        # preroll_file = io.BytesIO()
        # preroll_file.write(orjson.dumps(preroll_data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS))
        # preroll_file.seek(0)
        #
        # json_file = discord.File(preroll_file,
        #                          filename=f"PrerollData-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")

        # check for le error code
        if await self.check_errors(ctx, shop_json_response, auth_info, final_embeds):
            return

        llama_store = await stw.get_llama_store(shop_json_response)

        free_llama = await stw.free_llama_count(llama_store)

        llama_option = await self.select_options_llamas(llama_store)
        # TODO: hide llamas that are not available, or cannot be bought
        # With all info extracted, create the output

        embed = await self.llama_embed(ctx, free_llama, llama_store, preroll_data)

        final_embeds.append(embed)
        llama_view = LlamasView(ctx, self.client, auth_info[0], ctx.author, llama_store, free_llama, preroll_data,
                                llama_option, auth_info[1])
        llama_view.llamas = self
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, view=llama_view)
        return

    @ext.slash_command(name='llamas',
                       description='View and purchase Llamas in the Llama shop',
                       guild_ids=stw.guild_ids)
    async def slashllamas(self, ctx: discord.ApplicationContext,
                          token: Option(str,
                                        "Your Epic Games authcode. Required unless you have an active session.") = "",
                          auth_opt_out: Option(bool, "Opt out of starting an authentication session") = False, ):
        """
        This function is the entry point for the llama command when called via slash

        Args:
            ctx (discord.ApplicationContext): The context of the slash command
            token: Your Epic Games authcode. Required unless you have an active session.
            auth_opt_out: Opt out of starting an authentication session
        """
        await self.llamas_command(ctx, token, not auth_opt_out)

    @ext.command(name='llamas',
                 aliases=['lama', 'llma', 'llaa', 'llam', 'lllama', 'llaama', 'llamma', 'llamaa', 'lalma', 'llmaa',
                          'llaam', 'klama', 'olama', 'plama', 'lkama', 'loama', 'lpama', 'llqma', 'llwma', 'llsma',
                          'llxma', 'llzma', 'llana', 'llaja', 'llaka', 'llamq', 'llamw', 'llams', 'llamx', 'llamz',
                          'kllama', 'lklama', 'ollama', 'lolama', 'pllama', 'lplama', 'llkama', 'lloama', 'llpama',
                          'llqama', 'llaqma', 'llwama', 'llawma', 'llsama', 'llasma', 'llxama', 'llaxma', 'llzama',
                          'llazma', 'llanma', 'llamna', 'llajma', 'llamja', 'llakma', 'llamka', 'llamqa', 'llamaq',
                          'llamwa', 'llamaw', 'llamsa', 'llamxa', 'llamax', 'llamza', 'llamaz', 'lamas',
                          'llmas', 'llaas', 'llama', 'lllamas', 'llaamas', 'llammas', 'llamaas', 'llamass', 'lalmas',
                          'llmaas', 'llaams', 'klamas', 'olamas', 'plamas', 'lkamas', 'loamas', 'lpamas', 'llqmas',
                          'llwmas', 'llsmas', 'llxmas', 'llzmas', 'llanas', 'llajas', 'llakas', 'llamqs', 'llamws',
                          'llamss', 'llamxs', 'llamzs', 'llamae', 'llamad', 'kllamas', 'lklamas', 'ollamas', 'lolamas',
                          'pllamas', 'lplamas', 'llkamas', 'lloamas', 'llpamas', 'llqamas', 'llaqmas', 'llwamas',
                          'llawmas', 'llsamas', 'llasmas', 'llxamas', 'llaxmas', 'llzamas', 'llazmas', 'llanmas',
                          'llamnas', 'llajmas', 'llamjas', 'llakmas', 'llamkas', 'llamqas', 'llamaqs', 'llamwas',
                          'llamaws', 'llamsas', 'llamxas', 'llamaxs', 'llamzas', 'llamazs', 'llamasa', 'llamasw',
                          'llamaes', 'llamase', 'llamads', 'llamasd', 'llamasx', 'llamasz', 'hop', 'sop', 'shp', 'sho',
                          'sshop', 'shhop', 'shoop', 'shopp', 'hsop', 'sohp', 'shpo', 'ahop', 'whop', 'ehop', 'dhop',
                          'xhop', 'zhop', 'sgop', 'syop', 'suop', 'sjop', 'snop', 'sbop', 'ship', 'sh9p', 'sh0p',
                          'shpp', 'shlp', 'shkp', 'shoo', 'sho0', 'shol', 'ashop', 'sahop', 'wshop', 'swhop', 'eshop',
                          'sehop', 'dshop', 'sdhop', 'xshop', 'sxhop', 'zshop', 'szhop', 'sghop', 'shgop', 'syhop',
                          'shyop', 'suhop', 'shuop', 'sjhop', 'shjop', 'snhop', 'shnop', 'sbhop', 'shbop', 'shiop',
                          'shoip', 'sh9op', 'sho9p', 'sh0op', 'sho0p', 'shpop', 'shlop', 'sholp', 'shkop', 'shokp',
                          'shopo', 'shop0', 'shopl', 'tore', 'sore', 'stre', 'stoe', 'stor', 'sstore', 'sttore',
                          'stoore', 'storre', 'storee', 'tsore', 'sotre', 'stroe', 'stoer', 'atore', 'wtore', 'etore',
                          'dtore', 'xtore', 'ztore', 'srore', 's5ore', 's6ore', 'syore', 'shore', 'sgore', 'sfore',
                          'stire', 'st9re', 'st0re', 'stpre', 'stlre', 'stkre', 'stoee', 'sto4e', 'sto5e', 'stote',
                          'stoge', 'stofe', 'stode', 'storw', 'stor3', 'stor4', 'storr', 'storf', 'stord', 'stors',
                          'astore', 'satore', 'wstore', 'swtore', 'estore', 'setore', 'dstore', 'sdtore', 'xstore',
                          'sxtore', 'zstore', 'sztore', 'srtore', 'strore', 's5tore', 'st5ore', 's6tore', 'st6ore',
                          'sytore', 'styore', 'shtore', 'sthore', 'sgtore', 'stgore', 'sftore', 'stfore', 'stiore',
                          'stoire', 'st9ore', 'sto9re', 'st0ore', 'sto0re', 'stpore', 'stopre', 'stlore', 'stolre',
                          'stkore', 'stokre', 'stoere', 'sto4re', 'stor4e', 'sto5re', 'stor5e', 'stotre', 'storte',
                          'stogre', 'storge', 'stofre', 'storfe', 'stodre', 'storde', 'storwe', 'storew', 'stor3e',
                          'store3', 'store4', 'storer', 'storef', 'stored', 'storse', 'stores', 'inata', 'pnata',
                          'piata', 'pinta', 'pinaa', 'pinat', 'ppinata', 'piinata', 'pinnata', 'pinaata', 'pinatta',
                          'pinataa', 'ipnata', 'pniata', 'pianta', 'pintaa', 'pinaat', 'oinata', '0inata', 'linata',
                          'punata', 'p8nata', 'p9nata', 'ponata', 'plnata', 'pknata', 'pjnata', 'pibata', 'pihata',
                          'pijata', 'pimata', 'pinqta', 'pinwta', 'pinsta', 'pinxta', 'pinzta', 'pinara', 'pina5a',
                          'pina6a', 'pinaya', 'pinaha', 'pinaga', 'pinafa', 'pinatq', 'pinatw', 'pinats', 'pinatx',
                          'pinatz', 'opinata', 'poinata', '0pinata', 'p0inata', 'lpinata', 'plinata', 'puinata',
                          'piunata', 'p8inata', 'pi8nata', 'p9inata', 'pi9nata', 'pionata', 'pilnata', 'pkinata',
                          'piknata', 'pjinata', 'pijnata', 'pibnata', 'pinbata', 'pihnata', 'pinhata', 'pinjata',
                          'pimnata', 'pinmata', 'pinqata', 'pinaqta', 'pinwata', 'pinawta', 'pinsata', 'pinasta',
                          'pinxata', 'pinaxta', 'pinzata', 'pinazta', 'pinarta', 'pinatra', 'pina5ta', 'pinat5a',
                          'pina6ta', 'pinat6a', 'pinayta', 'pinatya', 'pinahta', 'pinatha', 'pinagta', 'pinatga',
                          'pinafta', 'pinatfa', 'pinatqa', 'pinataq', 'pinatwa', 'pinataw', 'pinatsa', 'pinatas',
                          'pinatxa', 'pinatax', 'pinatza', 'pinataz', 'ray', 'xay', 'xry', 'xra', 'xxray', 'xrray',
                          'xraay', 'xrayy', 'rxay', 'xary', 'xrya', 'zray', 'sray', 'dray', 'cray', 'xeay', 'x4ay',
                          'x5ay', 'xtay', 'xgay', 'xfay', 'xday', 'xrqy', 'xrwy', 'xrsy', 'xrxy', 'xrzy', 'xrat',
                          'xra6', 'xra7', 'xrau', 'xraj', 'xrah', 'xrag', 'zxray', 'xzray', 'sxray', 'xsray', 'dxray',
                          'xdray', 'cxray', 'xcray', 'xeray', 'xreay', 'x4ray', 'xr4ay', 'x5ray', 'xr5ay', 'xtray',
                          'xrtay', 'xgray', 'xrgay', 'xfray', 'xrfay', 'xrday', 'xrqay', 'xraqy', 'xrway', 'xrawy',
                          'xrsay', 'xrasy', 'xrxay', 'xraxy', 'xrzay', 'xrazy', 'xraty', 'xrayt', 'xra6y', 'xray6',
                          'xra7y', 'xray7', 'xrauy', 'xrayu', 'xrajy', 'xrayj', 'xrahy', 'xrayh', 'xragy', 'xrayg',
                          'l', 'ahoura', '🙄'],
                 extras={'emoji': "llama", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         'dev': False},
                 brief="View and purchase Llamas in the Llama shop",
                 description="This command allows you to view the available Llamas in the Llama shop, the contents of "
                             "the available llamas purchase them. As this information is specific to your account, "
                             "you will need an active session or to provide your authcode.\n⦾ Please note that this "
                             "command is still experimental <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def llamas(self, ctx, authcode='', optout=None):
        """
        This is the entry point for the llama command when called traditionally

        Args:
            ctx: The context of the command
            authcode: The authcode for the account
            optout: Any text given will opt out of starting an auth session
        """
        if optout is not None:
            optout = True
        else:
            optout = False

        await self.llamas_command(ctx, authcode, not optout)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Llamas(client))

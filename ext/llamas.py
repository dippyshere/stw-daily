"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the homebase command. renames homebase / displays current name + renders banner
"""

import discord
import discord.ext.commands as ext
from discord import Option
import orjson
import io
import datetime

import stwutil as stw


async def llama_entry(catalog_entry):
    """
    Creates an embed entry string for a single llama catalog entry.

    Args:
        catalog_entry: The catalog entry to be processed.

    Returns:
        The embed entry string.
    """
    try:
        entry_string = f"\u200b\n**{catalog_entry['title']}**\n"
    except:
        entry_string = f"\u200b\n**{catalog_entry['devName']}**\n"
    entry_string += f"Rarity: {catalog_entry['itemGrants'][0]['templateId'].split('CardPack:cardpack_')[1]}\n"
    entry_string += f"Cost: {catalog_entry['prices'][0]['currencySubType'].split('AccountResource:')[1]} **{catalog_entry['prices'][0]['finalPrice']}**\n"
    entry_string += f"OfferID: {catalog_entry['offerId']}\n"
    entry_string += f"Dev name: {catalog_entry['devName']}\n"
    entry_string += f"Daily limit: {catalog_entry['dailyLimit']}\n"
    try:
        entry_string += f"Event limit: {catalog_entry['meta']['EventLimit']}\n"
    except:
        pass
    entry_string += f"Icon: {catalog_entry['displayAssetPath'].split('/Game/Items/CardPacks/')[-1].split('.')[0]}\n"
    return entry_string


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
        generic_colour = self.client.colours["generic_blue"]

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

        populate_preroll_request = await stw.profile_request(self.client, "llamas", auth_info[1], profile_id="stw")
        populate_preroll_json = orjson.loads(await populate_preroll_request.read())
        preroll_data = stw.extract_profile_item(populate_preroll_json, "PrerollData")

        preroll_file = io.BytesIO()
        preroll_file.write(orjson.dumps(preroll_data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS))
        preroll_file.seek(0)

        json_file = discord.File(preroll_file,
                                 filename=f"PrerollData-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")

        # check for le error code
        if await self.check_errors(ctx, shop_json_response, auth_info, final_embeds):
            return

        llama_store = await stw.get_llama_store(shop_json_response)

        free_llama = await stw.free_llama_count(llama_store)

        # With all info extracted, create the output
        embed = discord.Embed(
            title=await stw.add_emoji_title(self.client, "Store", "llama"),
            description=f"\u200b\nHere's the current shop:\u200b\n\u200b",
            colour=generic_colour)

        embed.description += f"\u200b\n**There are {free_llama[0]} Free Llama{'s'[:free_llama[0] ^ 1]}:**"
        if free_llama[0] > 0:
            embed.description += f"\n{free_llama[1]}"
        embed.description += f"\u200b\n\u200b"

        for entry in llama_store["catalogEntries"]:
            embed.add_field(name="\u200b", value=await llama_entry(entry), inline=False)

        # profile_file = io.BytesIO()
        # profile_file.write(orjson.dumps(llama_store, option=orjson.OPT_INDENT_2))
        # profile_file.seek(0)
        #
        # json_file = discord.File(profile_file,
        #                          filename=f"llama_store-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json")

        embed = await stw.set_thumbnail(self.client, embed, "meme")
        embed = await stw.add_requested_footer(ctx, embed)
        final_embeds.append(embed)
        await stw.slash_edit_original(ctx, auth_info[0], final_embeds, file=json_file)
        return

    @ext.slash_command(name='llamas',
                       description='Get llamas info from stw',
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
                 extras={'emoji': "llama", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         'dev': False},
                 brief="Get llamas info from stw",
                 description="Get llamas info from stw")
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

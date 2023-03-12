"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the main utility library for stw daily. It contains a lot of functions that are used throughout the bot.
"""
import base64
import datetime
import os
import random
import re
import time
import math
from difflib import SequenceMatcher
import logging
from typing import Tuple, Union, Any, Optional
import functools

import aiofiles
import aiohttp.client_reqrep
import blendmodes.blend
import deprecation
from Crypto.Cipher import AES
from PIL import Image, ImageDraw, ImageFont
import asyncio
import io
import orjson
from cache import AsyncLRU

import discord
from PIL.ImageFont import FreeTypeFont
from discord import Client
from discord.ext import commands
from discord.ext.commands import Command, Context

import items
import ext.battlebreakers.BBLootTable  # dinnerbrb its been much too long
from lang.stwi18n import I18n
from ext.profile.bongodb import get_user_document, replace_user_document

logger = logging.getLogger(__name__)


async def load_item_data() -> Tuple[dict, dict, dict, dict, dict, dict, dict, int, dict, dict, dict, FreeTypeFont]:
    """
    Loads the item data from the item data file

    Returns:
        The item data

    Raises:
        Exception: If the item data file is not found.
    """
    async with aiofiles.open("ext/battlebreakers/LoginRewards.json", "r") as f:
        bbLoginRewards: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/SurvivorItemRating.json') as f:
        SurvivorItemRating: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/HomebaseRatingMapping.json') as f:
        HomebaseRatingMapping: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/ResearchSystem.json') as f:
        ResearchSystem: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/AccountLevels.json') as f:
        AccountLevels: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/BannerColorMap.json') as f:
        BannerColorMap: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/BannerColors.json') as f:
        BannerColors: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/STW_Accolade_Tracker.json') as f:
        max_daily_stw_accolade_xp: int = orjson.loads(await f.read())[0]["Properties"]["MaxDailyXP"]
    async with aiofiles.open('ext/DataTables/allowed-name-chars.json') as f:
        allowed_chars: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/DailyRewards.json') as f:
        stwDailyRewards: dict = orjson.loads(await f.read())
    async with aiofiles.open('ext/DataTables/DailyFoundersRewards.json') as f:
        stwFounderDailyRewards: dict = orjson.loads(await f.read())
    async with aiofiles.open('res/burbank-big-condensed-black.otf', 'rb') as f:
        burbank: FreeTypeFont = ImageFont.truetype(io.BytesIO(await f.read()), 90)
    return bbLoginRewards, SurvivorItemRating, HomebaseRatingMapping, ResearchSystem, AccountLevels, BannerColorMap, \
        BannerColors, max_daily_stw_accolade_xp, allowed_chars, stwDailyRewards, stwFounderDailyRewards, burbank


bbLoginRewards, SurvivorItemRating, HomebaseRatingMapping, ResearchSystem, AccountLevels, BannerColorMap, BannerColors, max_daily_stw_accolade_xp, allowed_chars, stwDailyRewards, stwFounderDailyRewards, burbank = asyncio.get_event_loop().run_until_complete(
    load_item_data())
logger.debug("Loaded item data")
banner_d = Image.open("ext/homebase-textures/banner_texture_div.png").convert("RGB")
banner_m = Image.open("ext/homebase-textures/banner_shape_standard.png").convert("RGBA")
logger.debug("Loaded banner textures")

I18n = I18n()

guild_ids = None


def reverse_dict_with_list_keys(dictionary: dict[str, list[str]]) -> dict[str, str]:
    """
    Reverses a dictionary with list keys

    Args:
        dictionary: the dictionary to reverse

    Returns:
        A dictionary with the keys and values reversed
    """
    new_dict = {}

    for key, value in dictionary.items():
        if isinstance(value, list):
            for item in value:
                new_dict[item.lower()] = key
        else:
            new_dict[value.lower()] = key

    logger.debug(f"Reversed dictionary with list and non-list keys: {new_dict}")
    return new_dict


async def view_interaction_check(view, interaction: discord.Interaction, command: str) -> bool:
    """
    Checks if the interaction is created by the view author

    Args:
        view: the view
        interaction: the interaction
        command: the command

    Returns:
        True if the interaction is created by the view author, False if notifying the user

    Raises:
        Exception: If the interaction is not created by the view author and notifying the user failed.
    """
    if view.ctx.author == interaction.user:
        logger.debug("Interaction check passed")
        return True
    else:
        try:
            already_notified = view.interaction_check_done[interaction.user.id]
        except:
            already_notified = False
            view.interaction_check_done[interaction.user.id] = True

        if not already_notified:
            acc_name = ""
            error_code = "errors.stwdaily.not_author_interaction_response"
            try:
                interaction_language = interaction.locale
                if interaction_language.lower() in ["en-us", "en-gb", "en"]:
                    interaction_language = "en"
                elif interaction_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn",
                                                      "zh-hans-sg"]:
                    interaction_language = "zh-CHS"
                elif interaction_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                      "zh-hant-hk", "zh-hant-mo"]:
                    interaction_language = "zh-CHT"
                if not I18n.is_lang(interaction_language):
                    interaction_language = None
            except:
                interaction_language = None
            try:
                guild_language = interaction.guild.preferred_locale
                if guild_language.lower() in ["en-us", "en-gb", "en"]:
                    guild_language = "en"
                elif guild_language.lower() in ["zh-cn", "zh-sg", "zh-chs", "zh-hans", "zh-hans-cn", "zh-hans-sg"]:
                    guild_language = "zh-CHS"
                elif guild_language.lower() in ["zh-tw", "zh-hk", "zh-mo", "zh-cht", "zh-hant", "zh-hant-tw",
                                                "zh-hant-hk", "zh-hant-mo"]:
                    guild_language = "zh-CHT"
                if not I18n.is_lang(guild_language):
                    guild_language = None
            except:
                guild_language = None
            try:
                user_profile = await get_user_document(view.ctx, view.client, interaction.user.id,
                                                       desired_lang=interaction_language or guild_language or "en")
                profile_language = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"]["language"]
                if profile_language == "auto" or not I18n.is_lang(profile_language):
                    profile_language = None
            except:
                profile_language = None
            logger.debug(f"Interaction check notify languages: interaction={interaction_language}, guild={guild_language}, profile={profile_language}")
            embed = await post_error_possibilities(interaction, view.client, command, acc_name, error_code,
                                                   desired_lang=profile_language or interaction_language or guild_language or "en")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.debug("Interaction check failed, user notified")
            return False
        else:
            logger.debug("Interaction check failed, user already notified")
            return False

@functools.cache
def edit_emoji_button(client: Client, button: discord.ui.Button) -> discord.ui.Button:
    """
    Adds an emoji to a button

    Args:
        client: the client
        button: the button to add the emoji to

    Returns:
        The button with the emoji edited

    Raises:
        Exception: If the emoji is not found in the config.
    """
    try:
        button.emoji = client.config["emojis"][button.emoji.name]
        logger.debug(f"Edited emoji button: {button}")
        return button
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        return button
    except TypeError as e:
        logger.error(f"TypeError: {e}")
        return button


global_quotes = discord.ext.commands.view._all_quotes


# rip the one line dream
# def process_quotes_in_message(message_content): """Handles quotes in a message's content by replacing them with the appropriate unicode character\n\n\u200b\n\n**Args:**\n\n*message: the message to process*\n\n\n**Returns:**\n\n*The processed message*"""; [message_content := message_content[:character_index+(index*2)]+rf'\\{message_content[character_index+(index*2)]}'+message_content[(character_index+1+(index*2)):] for index, character_index in enumerate([character_index.start(0) for character_index in re.finditer(rf'["＂]', message_content)][1:-1])];     [message_content := message_content[:character_index+(index*2)]+rf'\\{message_content[character_index+(index*2)]}'+message_content[(character_index+1+(index*2)):] for index, character_index in enumerate([character_index.start(0) for character_index in re.finditer(rf'[‘,’,“,”,„,‟,⹂,⹂,「,」,『,』,〝,〞,﹁,﹂,﹃,﹄,｢,｣,«,»,‹,›,《,》,〈,〉]', message_content)])]; return message_content


def process_quotes_in_message(message_content: str) -> str:
    """
    Handles quotes in a message's content by replacing them with the appropriate unicode character

    Args:
        message_content: the message to process

    Returns:
        The processed message hi?

    Raises:
        Exception: If the message content is None.

    Notes:
        This is a mess, but it works.

        I'm not sure if this is the best way to do this, but it works.

        GitHub wrote this, not me.
    """
    logging.debug(f"Processing quotes in message content: {message_content}")
    message_content = re.sub(rf'[‘’“”„‟⹂「」『』〝〞﹁﹂﹃﹄｢｣«»‹›《》〈〉"＂]', lambda match: rf'\\{match.group()}', message_content)

    starting, ending = None, None
    try:
        starting = re.search(r'(^| )\\\\["＂]', message_content).span()[1] - 1
        ending = len(message_content) - re.search(r'(^| )["＂]', message_content[::-1]).span()[0] - 1
    except:
        pass

    # just gotta make sure None is None
    if starting != ending and starting is not None and ending is not None and None is None:
        message_content = message_content[:starting - 2] + message_content[starting:]
        message_content = message_content[:ending - 4] + message_content[ending - 2:]
    logger.debug(f"Result: {message_content}")
    return message_content


async def slash_send_embed(ctx: Context, client: discord.Client, embeds: discord.Embed | list[discord.Embed],
                           view: discord.ui.View = None,
                           interaction: discord.Interaction = False) -> Union[discord.Message, None]:
    """
    A small bridging function to send embeds to a slash, view, normal command, or interaction

    Args:
        client:
        ctx: the context
        embeds: the embeds to send
        view: the view to send the embeds with
        interaction: whether or not the embeds are being sent to an interaction

    Returns:
        The message sent

    Raises:
        Exception: If the context is not a message, interaction, or application context.
    """
    try:
        embeds[0]
    except:
        embeds = [embeds]
    try:
        user_document = await get_user_document(ctx, client, ctx.author.id)
        currently_selected_profile_id = user_document["global"]["selected_profile"]
        try:
            silent = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["silent"]
        except:
            silent = False
        try:
            ephemeral = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["ephemeral"]
        except:
            ephemeral = False
    except:
        silent = False
        ephemeral = False
    if isinstance(ctx, discord.Message):
        if view is not None:
            return await ctx.channel.send(embeds=embeds, view=view, silent=silent)
        else:
            return await ctx.channel.send(embeds=embeds, silent=silent)
    elif isinstance(ctx, discord.Interaction):
        if view is not None:
            return await ctx.response.send_message(embeds=embeds, view=view, ephemeral=ephemeral)
        else:
            return await ctx.response.send_message(embeds=embeds, ephemeral=ephemeral)
    elif isinstance(ctx, discord.ApplicationContext):
        if view is not None:
            return await ctx.respond(embeds=embeds, view=view, ephemeral=ephemeral)
        else:
            return await ctx.respond(embeds=embeds, ephemeral=ephemeral)
    elif interaction:
        try:
            if view is not None:
                return await ctx.response.send_message(embeds=embeds, view=view, ephemeral=ephemeral)
            else:
                return await ctx.response.send_message(embeds=embeds, ephemeral=ephemeral)
        except:
            if view is not None:
                return await ctx.send_message(embeds=embeds, view=view)
            else:
                return await ctx.send_message(embeds=embeds)
    else:
        if view is not None:
            return await ctx.send(embeds=embeds, view=view, silent=silent)
        else:
            return await ctx.send(embeds=embeds, silent=silent)


async def retrieve_shard(client: Client, shard_id: int) -> int | str:
    """
    Retrieves the current shard name. Fallback to current shard id if no name is available

    Args:
        client: the client
        shard_id: the shard id

    Returns:
        The shard name if available, else the shard id

    Raises:
        Exception: If the shard id is greater than the number of shards
    """
    if shard_id > len(client.config["shard_names"]):
        logger.warning(f"Shard {shard_id} is out of range")
        return shard_id

    try:
        return client.config["shard_names"][shard_id]
    except (KeyError, IndexError):
        logger.warning(f"Unable to find shard name for shard {shard_id}")
        return shard_id


def time_until_end_of_day() -> str:
    """
    a string representing the time until the end of the day for the bot's status.
    this is one of the oldest surviving functions from the old bot.

    Returns:
        The time until the end of the day in hours, minutes

    Raises:
        Exception: If the time until the end of the day is less than 0
    """
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    a = datetime.datetime.combine(tomorrow, datetime.time.min) - datetime.datetime.utcnow()
    hours, remainder = divmod(int(a.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = ''
    if hours == 1:
        fmt += '{h} hour, '
    elif hours > 1:
        fmt += '{h} hours, '
    if minutes == 1:
        fmt += '{m} minute'
    else:
        fmt += '{m} minutes'
    return fmt.format(h=hours, m=minutes)


async def processing_queue_error_check(client: Client, ctx: discord.Message, user_snowflake: int, desired_lang: str) -> discord.Embed | bool:
    """
    Checks if a user is in the processing queue

    Args:
        client: the client
        ctx: the context
        user_snowflake: the user's snowflake
        desired_lang: the desired language

    Returns:
        an embed if the user is in the processing queue, else False

    Raises:
        Exception: If the user is in the processing queue
    """
    try:
        if client.processing_queue[user_snowflake]:
            logger.warning(f"User {user_snowflake} is in the processing queue. Queue: {client.processing_queue}")
            try:
                return await create_error_embed(client, ctx,
                                                description=f"{I18n.get('util.processingqueue.description1', desired_lang)}\n"
                                                            f"⦾ {I18n.get('util.processingqueue.description2', desired_lang)}",
                                                prompt_authcode=False, error_level=0, desired_lang=desired_lang)
            except Exception as e:
                logger.error(f"Error creating error embed for processing queue. Error: {e}")
                return False
    except:
        logger.debug(f"User {user_snowflake} is not in the processing queue. Queue: {client.processing_queue}")
        return True


async def mention_string(client: Client, prompt: str = "") -> str:
    """
    A function to compile a mention string for the bot

    Args:
        client: the client
        prompt: the prompt to use

    Returns:
        The mention string (@STW Daily prompt)

    Raises:
        Exception: If the bot is not ready
    """
    try:
        return f"{client.user.mention} {prompt}"
    except Exception as e:
        logger.debug(f"Bot not ready, using fallback mention string. Error: {e}")
        # this is a fallback for when the bot is not ready, i guess
        # could probably make this an f string /shrug
        return f"@STW Daily {prompt}"


async def add_requested_footer(ctx: Context | discord.ApplicationContext, embed: discord.Embed, desired_lang: str) -> discord.Embed:
    """
    Adds the requested by user to the footer of the embed

    Args:
        ctx: the context
        embed: the embed to add the footer to
        desired_lang: the desired language

    Returns:
        The embed with the footer added

    Raises:
        Exception: If the footer cannot be added
    """
    try:
        embed.set_footer(text=
                         f"\n{I18n.get('util.footer.requested', desired_lang, ctx.author.name)}"
                         , icon_url=ctx.author.display_avatar.url)
    except:
        embed.set_footer(text=
                         f"\n{I18n.get('util.footer.requested', desired_lang, ctx.user.name)}"
                         , icon_url=ctx.user.display_avatar.url)

    embed.timestamp = datetime.datetime.now()

    return embed


@AsyncLRU(maxsize=8192)
async def add_emoji_title(client: Client, title: str, emoji: str) -> str:
    """
    Adds emojis surrounding the title of an embed

    Args:
        client: the client
        title: the title to add the emojis to
        emoji: the emoji to add

    Returns:
        The title with the emojis added

    Raises:
        Exception: If the emoji is not found in the config
    """
    try:
        emoji = client.config["emojis"][emoji]
    except KeyError:
        logger.warning(f"Emoji {emoji} not found in config. Using placeholder emoji instead")
        emoji = client.config["emojis"]["placeholder"]
    return f"{emoji}  {title}  {emoji}"


@AsyncLRU(maxsize=8192)
async def split_emoji_title(client: Client, title: str, emoji_1: str, emoji_2: str) -> str:
    """
    Adds two separate emojis surrounding the title of an embed

    Args:
        client: the client
        title: the title to add the emojis to
        emoji_1: the first emoji to add
        emoji_2: the last emoji to add

    Returns:
        The title with the emojis added

    Raises:
        Exception: If the emoji is not found in the config
    """
    try:
        emoji_1 = client.config["emojis"][emoji_1]
    except:
        logger.warning(f"Title emoji {emoji_1} not found in config. Using placeholder emoji instead")
        emoji_1 = client.config["emojis"]["placeholder"]
    try:
        emoji_2 = client.config["emojis"][emoji_2]
    except:
        logger.warning(f"Title emoji {emoji_2} not found in config. Using placeholder emoji instead")
        emoji_2 = client.config["emojis"]["placeholder"]
    return f"{emoji_1}  {title}  {emoji_2}"


@AsyncLRU(maxsize=8192)
async def set_thumbnail(client: discord.Client, embed: discord.Embed, thumb_type: str) -> discord.Embed:
    """
    sets the thunbnail of an embed from the config key

    Args:
        client: the client
        embed: the embed
        thumb_type: the key of the thumbnail to set

    Returns:
        the embed with the thumbnail set

    Raises:
        Exception: If the thumbnail is not found in the config
    """
    try:
        embed.set_thumbnail(url=client.config["thumbnails"][thumb_type])
    except KeyError:
        logger.warning(f"Thumbnail type {thumb_type} not found, using placeholder")
        embed.set_thumbnail(url=client.config["thumbnails"]["placeholder"])
    return embed


def get_reward(client: discord.Client, day: int | str, vbucks: bool = True, desired_lang: str = "en") -> list[str, ...]:
    """
    gets the reward for the given day, accounting for non founders

    Args:
        client: the client
        day: the day to get the reward for
        vbucks: whether to get vbucks or not
        desired_lang: the desired language

    Returns:
        the reward for the given day and emoji key

    Raises:
        Exception: If the reward is not found in the item dictionary

    Notes:
        * Get rewards from the DataTables
        * Localise rewards
    """
    day_mod = int(day) % 336
    if day_mod == 0:
        day_mod = 336
    elif day_mod > 336:
        day_mod -= 336

    asset_path_name = stwDailyRewards[0]["Rows"][str(day_mod - 1)]["ItemDefinition"]["AssetPathName"]
    quantity = stwDailyRewards[0]['Rows'][str(day_mod - 1)]['ItemCount']
    if asset_path_name == "/Game/Items/PersistentResources/Currency_MtxSwap.Currency_MtxSwap":
        if vbucks:
            asset_path_name = "/Game/Items/PersistentResources/Currency_Hybrid_MTX_XRayLlama.Currency_Hybrid_MTX_XRayLlama"
        else:
            asset_path_name = "/Game/Items/PersistentResources/Currency_XRayLlama.Currency_XRayLlama"
    emoji, name, description = items.LootTable[asset_path_name]

    try:
        if asset_path_name.split('.')[1] in ["Voucher_BasicPack", "Reagent_C_T01", "SmallXpBoost", "CardPack_Bronze", "SmallXpBoost_Gift"]:
            if quantity != 1:
                name = I18n.get(f"stw.item.{asset_path_name.split('.')[1]}.name.plural", desired_lang)
            else:
                name = I18n.get(f"stw.item.{asset_path_name.split('.')[1]}.name.singular", desired_lang)
        else:
            name = I18n.get(f"stw.item.{asset_path_name.split('.')[1]}.name", desired_lang)
        description = I18n.get(f"stw.item.{asset_path_name.split('.')[1]}.desc", desired_lang)
    except:
        logger.warning(f"Could not find translation for {asset_path_name}")

    emoji_text = f"{client.config['emojis']['celebrate']} {client.config['emojis'][emoji]} {client.config['emojis']['celebrate']}" if quantity == 1000 else client.config['emojis'][emoji]
    logger.debug(f"Returning reward info: {name}, {emoji_text}, {description}, {quantity}")
    return [name, emoji_text, description, quantity]


def get_bb_reward_data(client: Client, response: Optional[dict] = None, error: bool = False, pre_calc_day: int = 0, desired_lang: str = "en") -> list[int | str | Any]:
    """
    gets the reward data for battle breakers rewards

    Args:
        client: the client
        response: the epic api response to get the data from
        error: whether there was an error or not
        pre_calc_day: the day to calculate the reward for
        desired_lang: the desired language

    Returns:
        the reward day, name, emoji key, description, quantity

    Raises:
        Exception: If the reward is not found in the item dictionary
    """
    if error:
        day = int(response['messageVars'][0]) - 1  # hello world explorer hi
    elif pre_calc_day > 0:  # do u see me minimizing it no
        day = pre_calc_day
    else:
        day = response["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"] - 1

    # im not sure if it actually loops after day 1800, but just in case not like anyone will use this command anyway
    # hello, future dippy here -
    # now that I have made a private server, we can finally determine what happens after day 1800...
    # since the game was never available for 1800+ days, there is no legitimate way to encounter this, however:
    # after day 1800, the game will crash upon login.
    # Presumably, the game would be patched to loop after 1800,
    # or a serverside implementation would prevent daily rewards notification from displaying / going above 1800
    day_mod = int(day) % 1800
    if day_mod == 0:
        day_mod = 1800

    # done FORTIFICAITION OF THE NIGHT hmm i see folders
    asset_path_name = bbLoginRewards[0]["Rows"][str(day_mod)]["ItemDefinition"]["AssetPathName"]
    quantity = bbLoginRewards[0]['Rows'][str(day_mod)]['ItemCount']

    emoji, name, description = ext.battlebreakers.BBLootTable.BBLootTable[asset_path_name]

    try:
        name = I18n.get(f"wex.item.{asset_path_name.split('.')[1]}.name", desired_lang)
        description = I18n.get(f"wex.item.{asset_path_name.split('.')[1]}.desc", desired_lang)
    except:
        logger.warning(f"Could not find translation for {asset_path_name}")

    emoji_text = client.config["emojis"][emoji]

    return [day, name, emoji_text, description, quantity]


@functools.cache
def get_game_headers(game: str) -> dict[str, str]:
    """
    gets the http auth headers for the given game/context
    Args:
        game: bb, ios, fn pc client

    Returns:
        the headers

    Raises:
        Exception: If the game is not found
    """
    if game == "bb":
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic M2NmNzhjZDNiMDBiNDM5YTg3NTVhODc4YjE2MGM3YWQ6YjM4M2UwZjQtZjBjYy00ZDE0LTk5ZTMtODEzYzMzZmMxZTlk="
        }
    elif game == "ios":
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
        }
    else:
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
        }
    return h


async def get_token(client: discord.Client, auth_code: str, game: str = "fn") -> aiohttp.client_reqrep.ClientResponse:
    """
    gets an access token for the given game/context
    Args:
        client: the client
        auth_code: the auth code to get the token for
        game: bb, ios, fn pc client

    Returns:
        the access token response

    Raises:
        Exception: If the game is not found
    """
    h = get_game_headers(game)
    d = {
        "grant_type": "authorization_code",
        "code": auth_code
    }
    url = client.config["endpoints"]["token"]

    return await client.stw_session.post(url, headers=h, data=d)


def decrypt_user_data(user_snowflake: int | str, authentication_information: dict) -> dict:
    """
    decrypts the user data

    Args:
        user_snowflake: the user snowflake
        authentication_information: the authentication information

    Returns:
        the decrypted user data

    Raises:
        Exception: If the decryption fails
    """

    battle_breakers_id = base64.b64decode(authentication_information["battleBreakersId"])
    battle_breakers_token = authentication_information["battleBreakersAuthToken"]
    authentication = authentication_information["authentication"]
    aes_cipher = AES.new(bytes(os.environ["STW_DAILY_KEY"], "ascii"), AES.MODE_GCM,
                         nonce=battle_breakers_id)  # Yes, i know this isnt secure, but it is better than storing stuff in plaintext.
    aes_cipher.update(bytes(str(user_snowflake), "ascii"))
    auth_information = aes_cipher.decrypt_and_verify(authentication, battle_breakers_token)
    decrypted_json = orjson.loads(auth_information)
    logger.debug(f"Decrypted json: {decrypted_json}")
    return decrypted_json


async def get_token_devauth(client: discord.Client, user_document: dict, game: str = "ios", auth_info_thread: Optional[Tuple[BaseException]] = None) -> aiohttp.client_reqrep.ClientResponse:
    """
    gets an access token for the given game/context

    Args:
        client: the client
        user_document: the document of the user to get the access token for
        game: bb, ios, fn pc client
        auth_info_thread: the thread to get the auth info from

    Returns:
        the access token response

    Raises:
        Exception: If the game is not found
    """

    client.processing_queue[user_document["user_snowflake"]] = True
    currently_selected_profile_id = user_document["global"]["selected_profile"]
    snowflake = user_document["user_snowflake"]

    h = get_game_headers(game)

    if auth_info_thread is None:
        auth_info_thread = await asyncio.gather(asyncio.to_thread(decrypt_user_data, snowflake,
                                                                  user_document["profiles"][
                                                                      str(currently_selected_profile_id)][
                                                                      "authentication"]))

    del client.processing_queue[user_document["user_snowflake"]]
    dev_auth = auth_info_thread[0]
    d = {
        "grant_type": "device_auth",
        "account_id": dev_auth["accountId"],
        "device_id": dev_auth["deviceId"],
        "secret": dev_auth["secret"],
    }

    url = client.config["endpoints"]["token"]
    return await client.stw_session.post(url, headers=h, data=d)


# hi
async def exchange_games(client: discord.Client, auth_token: str, game: str = "fn") -> aiohttp.client_reqrep.ClientResponse:
    """
    exchanges the given auth token for the given game

    Args:
        client: the client
        auth_token: the auth token to exchange
        game: the game to exchange for

    Returns:
        the new auth token response

    Raises:
        Exception: If the game is not found
    """
    h = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {auth_token}"
    }
    url = client.config["endpoints"]["exchange"]
    response = await client.stw_session.get(url, headers=h)

    exchange_json = orjson.loads(await response.read())
    exchange_code = exchange_json["code"]

    h = get_game_headers(game)
    d = {
        "grant_type": "exchange_code",
        "exchange_code": exchange_code
    }
    url = client.config["endpoints"]["token"]

    return await client.stw_session.post(url, headers=h, data=d)


async def processing_embed(client: discord.Client, ctx: discord.ext.commands.Context, desired_lang: str, title: str | None = None, description: str | None = None) -> discord.Embed:
    """
    Constructs the processing embed

    Args:
        client: the client
        ctx: the context
        desired_lang: the desired language
        title: the title of the embed
        description: the description of the embed

    Returns:
        the processing embed
    """
    colour = client.colours["success_green"]
    if title is None:
        title = I18n.get('util.processing.title', desired_lang)
    if description is None:
        description = I18n.get('util.processing.description', desired_lang)

    embed = discord.Embed(title=await add_emoji_title(client, f"{title}", "processing"),
                          description=f"```{description}```", colour=colour)
    embed = await add_requested_footer(ctx, embed, desired_lang)
    return embed


def random_error(client: Client, desired_lang: str = "en") -> str:
    """
    Gets a random error message

    Args:
        client: the client
        desired_lang: the desired language

    Returns:
        the randomly chosen error message

    Raises:
        Exception: If the language is not found
    """
    return I18n.get(random.choice(client.config["error_messages"]), desired_lang)


def random_waiting_message(client: Client, desired_lang: str = "en") -> str:
    """
    Gets a random waiting message

    Args:
        client: the client
        desired_lang: the desired language

    Returns:
        the randomly chosen error message

    Raises:
        Exception: If the language is not found
    """
    return I18n.get(random.choice(client.config["wait_on_user_messages"]), desired_lang)


async def check_for_auth_errors(client: Client, request: dict, ctx: Context, message: discord.Message, command: str, auth_code: str, send_error_message: bool = True, desired_lang: str = None) -> Tuple[bool, Optional[str], Optional[str]] | discord.Embed:
    """
    Checks for auth errors and sends the appropriate message

    Args:
        client: the client
        request: the request to check
        ctx: the context
        message: the message to edit
        command: the command that was run
        auth_code: the auth code used
        send_error_message: whether to send the error message or not
        desired_lang: the desired language

    Returns:
        If there was no error, returns True, access token, account id
        If there was an error, returns False, None, None

    Raises:
        Exception: If the language is not found
    """
    try:
        return True, request["access_token"], request["account_id"]
    except:
        error_code = request["errorCode"]
        error_message = request["errorMessage"]

    if auth_code == "":
        auth_code = "[saved session]"  # hell o hi

    logger.debug(f"Epic Error code: {error_code}")
    if error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
        # login error
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.expired.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.expired.description2', desired_lang)}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)

    elif error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
        # invalid grant error
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.invalidclient.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.invalidclient.description2', desired_lang)}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)
    elif error_code == 'errors.com.epicgames.account.invalid_account_credentials':
        # invalid grant error
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.devauth.expired.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.devauth.expired.description2', desired_lang, await mention_string(client, 'kill'), await mention_string(client, 'device'))}\n"
                                                     f"⦾ {I18n.get('util.error.auth.devauth.expired.description3', desired_lang)}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)

    elif error_code == 'errors.com.epicgames.accountportal.date_of_birth_verification_required':
        # cabined account error
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.cabined.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.cabined.description2', desired_lang, 'https://www.epicgames.com/fortnite')}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)

    elif re.match(r"[0-9a-f]{32}", error_code):
        # this is a bug stemming from a function in the chain returning an access token instead of anything incorrect
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.nostw.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description2', desired_lang, f'`{command.capitalize()}`')}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description3', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description4', desired_lang)}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)

    else:
        shrug = u'¯\\\_(ツ)\_/¯'
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                     f"```{truncate(auth_code)}```\n"
                                                     f"{I18n.get('util.error.auth.unknown.description1', desired_lang, shrug)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.unknown.description2', desired_lang)}\n"
                                                     f"```{error_code}\n\n{error_message}```",
                                         prompt_help=True, command=command, auth_push_strong=False,
                                         desired_lang=desired_lang)
        logger.critical(f"Unknown error code: {request}")

    embed = await set_thumbnail(client, embed, "error")
    embed = await add_requested_footer(ctx, embed, desired_lang)

    if send_error_message:
        await slash_edit_original(ctx, message, embed)
    else:
        return embed

    return False, None, None


# hi?
async def slash_edit_original(ctx: Context, msg: discord.Message | discord.Interaction, embeds: discord.Embed | list[discord.Embed], view: discord.ui.View = None, files: list[discord.File] = None):
    """
    Edits the original message sent by the bot

    Args:
        ctx: The context of the command
        msg: The message to edit
        embeds: The embeds to edit the message with
        view: The view to edit the message with
        files: The files to add to the message

    Returns:
        The edited message

    Raises:
        discord.errors.HTTPException: If the message is not found
    """
    try:
        embeds[0]
    except:
        embeds = [embeds]
    if files is not None:
        try:
            files[0]
        except:
            files = [files]

    if isinstance(msg, discord.Interaction):
        method = msg.edit_original_response
    else:
        try:
            method = msg.edit
        except:
            method = ctx.edit

    if isinstance(ctx, discord.ApplicationContext):
        if view is not None and files is not None:
            try:
                return await method(embeds=embeds, view=view, files=files)
            except:
                return await ctx.edit(embeds=embeds, view=view, files=files)
        if view is not None:
            try:
                return await method(embeds=embeds, view=view)
            except:
                return await ctx.edit(embeds=embeds, view=view)
        if files is not None:
            try:
                return await method(embeds=embeds, files=files)
            except:
                return await ctx.edit(embeds=embeds, files=files)
        else:
            try:
                return await method(embeds=embeds)
            except:
                return await ctx.edit(embeds=embeds)
    else:
        if view is not None and files is not None:
            return await method(embeds=embeds, view=view, files=files)
        if view is not None:
            return await method(embeds=embeds, view=view)
        if files is not None:
            return await method(embeds=embeds, files=files)
        else:
            return await method(embeds=embeds)


async def device_auth_request(client: Client, account_id: str, token: str) -> aiohttp.client_reqrep.ClientResponse:
    """
    Sends a device auth request to epic

    Args:
        client: The client to use
        account_id: The account id to use
        token: The token to use

    Returns:
        The response from epic

    Raises:
        HTTPException: If the request fails
    """
    url = client.config["endpoints"]["device_auth"].format(account_id)
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    return await client.stw_session.post(url, headers=header, json="")


async def profile_request(client: Client, req_type: str, auth_entry: dict[str, str | bool | float | None | list[str]], data: str | dict | bytes = "{}", json: dict = None, profile_id: str = "stw", game: str = "fn", profile_type: str = "profile0") -> aiohttp.client_reqrep.ClientResponse:
    """
    Request a profile from epic api
    Args:
        client: The client
        req_type: The type of profile related request to make
        auth_entry: The auth entry to use
        data: The data to send with the request
        json: The json to send with the request
        profile_id: The profile id to use in the request
        game: The game to use in the request
        profile_type: The profile type to use in the request

    Returns:
        The response from the request

    Raises:
        HTTPException: If the request fails
    """
    if game == "bb":
        token = auth_entry["bb_token"]
        url = client.config["endpoints"]["bb_profile"].format(auth_entry["account_id"],
                                                              client.config["profile"][req_type], profile_type)
    else:
        token = auth_entry["token"]
        url = client.config["endpoints"]["profile"].format(auth_entry["account_id"], client.config["profile"][req_type],
                                                           client.config["profileid"][profile_id])
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    if json is None:
        return await client.stw_session.post(url, headers=header, data=data)
    else:
        return await client.stw_session.post(url, headers=header, json=json)


async def shop_request(client: Client, token: str) -> dict:
    """
    Makes a request to the shop endpoint

    Args:
        client: discord client
        token: The auth token to use

    Returns:
        json response from the endpoint

    Raises:
        HTTPException: If the request fails
    """

    h = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }

    async with client.stw_session.get(client.config["endpoints"]["store"], headers=h) as resp:
        return orjson.loads(await resp.read())


async def get_llama_store(shop: dict) -> dict | None:
    """
    Gets the llama store from the shop request

    Args:
        shop: The shop request

    Returns:
        The llama store

    Raises:
        ValueError: If the store is not found
    """
    for store in shop["storefronts"]:
        if store["name"] == "CardPackStorePreroll":
            return store
    logger.warning("Could not find llama store")
    return None


async def free_llama_count(store: dict) -> Tuple[int, list]:
    """
    Gets the amount of free llamas in the store, and any related info if available

    Args:
        store: The llama store from the shop query

    Returns:
        The amount of free llamas

    Raises:
        ValueError: If the store is not found
    """
    free_llamas = []
    for entry in store["catalogEntries"]:
        if "Always" not in entry["devName"] and entry["prices"][0]["finalPrice"] == 0:
            free_llamas.append(entry)
    return len(free_llamas), free_llamas


async def purchase_llama(client: Client, auth_entry: dict[str, str | bool | float | None | list[str]], offer_id: str, currency: str = "GameItem", currencySubType: str = "AccountResource:currency_xrayllama", expectedTotalPrice: int = 0) -> dict:
    """
    Purchases a llama from the store

    Args:
        client: The client
        auth_entry: The auth entry to use
        offer_id: The offer id to use
        currency: The currency to use
        currencySubType: The currency subtype to use
        expectedTotalPrice: The expected total price to use

    Returns:
        The response from the request

    Raises:
        HTTPException: If the request fails
    """
    json = {"offerId": offer_id,
            "purchaseQuantity": 1,
            "currency": currency,
            "currencySubType": currencySubType,
            "expectedTotalPrice": expectedTotalPrice,
            "gameContext": ""}
    req_buy_free_llama = await profile_request(client, "purchase", auth_entry, json=json,
                                               profile_id="common_core")
    return orjson.loads(await req_buy_free_llama.read())


async def get_llama_datatable(client: Client, path: str, desired_lang: str = 'en') -> tuple[str, str, str, str, str]:
    """
    Gets the llama datatable from the game files

    Args:
        client: The client
        path: The path to the cardpack
        desired_lang: The desired language to use

    Returns:
        Name, Description, image emoji, pack image emoji, and rarity of the llama

    Raises:
        ValueError: If the datatable is not found
    """
    try:
        path = path.split("/")[-1]
    except:
        pass
    try:
        outcome = max(os.listdir("./ext/DataTables/CardPacks/"),
                      key=lambda file_name: SequenceMatcher(a=file_name, b=path).ratio())
        similarity = SequenceMatcher(a=outcome, b=path).ratio()
        if similarity < 0.4:
            # if the first 4 characters match in outcome and filtered, then it's probably a match
            if outcome[:13] == path[:13]:
                pass
            else:
                outcome = 'CardPack_Bronze.json'
        logger.debug(f"Chose DataTable: {outcome} for item: {path} (Similarity: {similarity})")
        async with aiofiles.open(f"./ext/DataTables/CardPacks/{outcome}", "r") as f:
            llama_file = orjson.loads(await f.read())[0]["Properties"]
        return llama_file["DisplayName"]["SourceString"], llama_file["Description"]["SourceString"], \
            get_item_icon_emoji(client, llama_file["LargePreviewImage"]["AssetPathName"].split(".")[-1]), \
            get_item_icon_emoji(client, llama_file["PackImage"]["AssetPathName"].split(".")[-1]), \
            llama_file["Rarity"].split("::")[-1]
    except Exception as e:
        logger.warning(f"Could not find DataTable for {path}, using default llama values. Error: {e}")
        return I18n.get("stw.item.CardPack_Bronze.name.singular", desired_lang), \
            I18n.get("stw.item.CardPack_Bronze.desc", desired_lang), "<:PinataStandardPack:947728062739542036>", \
            "<:T_CardPack_Upgrade_IconMask:1055049365426819092>", \
            "Rare"


async def claim_free_llamas(client: Client, auth_entry: dict[str, str | bool | float | None | list[str]], store: dict, prerolled_offers: dict[str, ...]) -> None:
    """
    Claims the free llamas in the store

    Args:
        client: The client
        auth_entry: The auth entry to use
        store: The llama store from the shop query
        prerolled_offers: The response to the populate prerolled offers request

    Returns:
        The response from the request

    Raises:
        HTTPException: If the request fails
    """
    already_opened_free_llamas = 0
    free_llamas_count, free_llamas_list = await free_llama_count(store)
    if not free_llamas_count:
        logger.info("No free llamas to open")
        return None
    else:
        items_from_llamas = []
        opened_llamas = 0
        for llama in free_llamas_list:
            llama_to_claim_offer_id = llama['offerId']
            try:
                llama_to_claim_title = llama['title']
            except:
                llama_to_claim_title = []
            llama_to_claim_template_id = llama['itemGrants'][0]['templateId']
            while True:
                req_populate_llamas = prerolled_offers  # llamas
                llama_tier = []
                for key in req_populate_llamas['profileChanges'][0]['profile']['items']:
                    if req_populate_llamas['profileChanges'][0]['profile']['items'][key][
                        'templateId'].lower().startswith("prerolldata") and \
                            req_populate_llamas['profileChanges'][0]['profile']['items'][key]['attributes'][
                                'offerId'] == llama_to_claim_offer_id:
                        try:
                            llama_tier = \
                                req_populate_llamas['profileChanges'][0]['profile']['items'][key]['attributes'][
                                    'highest_rarity']
                        except:
                            llama_tier = 0
                json = {"offerId": llama_to_claim_offer_id,
                        "purchaseQuantity": 1,
                        "currency": "GameItem",
                        "currencySubType": "AccountResource:currency_xrayllama",
                        "expectedTotalPrice": 0,
                        "gameContext": ""}
                req_buy_free_llama = await profile_request(client, "purchase", auth_entry, json=json,
                                                           profile_id="common_core")
                req_buy_free_llama_json = orjson.loads(await req_buy_free_llama.read())
                if "errorMessage" in req_buy_free_llama_json:
                    if "limit of" in req_buy_free_llama_json['errorMessage']:
                        if opened_llamas == 0:
                            already_opened_free_llamas += 1
                    if "because fulfillment" in req_buy_free_llama_json['errorMessage']:
                        logger.warning("account is unable to claim free llama")
                    break
                else:
                    logger.info("opening llama_to_claim_name tier llama_tier")
                    llama_loot = req_buy_free_llama_json['notifications'][0]['lootResult']['items']
                    llama_loot_count = 0
                    opened_llamas += 1
                    for key in llama_loot:
                        template_id = key['itemType']
                        item_guid = key['itemGuid']
                        item_quantity = key['quantity']
                        item_name = template_id
                        try:
                            item_rarity = 'rarity'
                            item_type = 'type'
                        except:
                            item_rarity = "Unknown rarity"
                            item_type = "Unknown type"
                        llama_loot_count += 1
                        if item_rarity in ("common", "uncommon", "rare", "epic"):
                            items_from_llamas.append(
                                {"itemName": item_name, "itemType": item_type, "templateId": template_id,
                                 "itemGuid": item_guid, "itemRarity": item_rarity, "itemQuantity": item_quantity})
                        logger.info(f"{llama_loot_count}: {item_rarity} | {item_type}: {item_quantity}x {item_name}")
        if int(already_opened_free_llamas) == free_llamas_count:
            logger.info("alreadyclaimed")
        else:
            if opened_llamas > 0:
                logger.info("successfully opened opened_llamas")
            else:
                logger.info("opening failed")


async def recycle_free_llama_loot(client: Client, auth_entry: dict[str, str | bool | float | None | list[str]], items_from_llamas: dict | list, already_opened_free_llamas: int, free_llamas_count: int, recycle_config: Optional[dict] = None) -> None:
    """
    Recycles the free llama loot

    Args:
        client: The client
        auth_entry: The auth entry to use
        items_from_llamas: The items from the free llama loot
        already_opened_free_llamas: The amount of free llamas already opened
        free_llamas_count: The amount of free llamas
        recycle_config: The config for what to recycle

    Returns:
        The response from the request

    Raises:
        HTTPException: If the request fails
    """

    if recycle_config is None:
        recycle_config = {'weapon': [''], 'trap': [''], 'survivor': [''], 'defender': [''], 'hero': ['']}
    rarities = {"off": "",
                "common": "common",
                "uncommon": "common, uncommon",
                "rare": "common, uncommon, rare",
                "epic": "common, uncommon, rare, epic"
                }
    item_rarities = {
        "weapon": rarities["off".lower()].split(", "),
        "trap": rarities["off".lower()].split(", "),
        "survivor": rarities["off".lower()].split(", "),
        "defender": rarities["off".lower()].split(", "),
        "hero": rarities["off".lower()].split(", ")
    }
    resources_message = ""

    tracked_resources = ["AccountResource:heroxp", "AccountResource:personnelxp", "AccountResource:phoenixxp",
                         "AccountResource:phoenixxp_reward", "AccountResource:reagent_alteration_ele_fire",
                         "AccountResource:reagent_alteration_ele_nature",
                         "AccountResource:reagent_alteration_ele_water",
                         "AccountResource:reagent_alteration_gameplay_generic",
                         "AccountResource:reagent_alteration_generic", "AccountResource:reagent_alteration_upgrade_r",
                         "AccountResource:reagent_alteration_upgrade_sr",
                         "AccountResource:reagent_alteration_upgrade_uc",
                         "AccountResource:reagent_alteration_upgrade_vr", "AccountResource:reagent_c_t01",
                         "AccountResource:reagent_c_t02", "AccountResource:reagent_c_t03",
                         "AccountResource:reagent_c_t04", "AccountResource:reagent_evolverarity_r",
                         "AccountResource:reagent_evolverarity_sr", "AccountResource:reagent_evolverarity_vr",
                         "AccountResource:reagent_people", "AccountResource:reagent_promotion_heroes",
                         "AccountResource:reagent_promotion_survivors", "AccountResource:reagent_promotion_traps",
                         "AccountResource:reagent_promotion_weapons", "AccountResource:reagent_traps",
                         "AccountResource:reagent_weapons", "AccountResource:schematicxp"]

    if int(already_opened_free_llamas) != free_llamas_count:
        items_to_recycle = []
        item_guids_to_recycle = []
        recycle_resources = []
        recycled_items_count = 0
        recycle_resources_count = 0
        for item in items_from_llamas:
            item_type = item['itemType']
            item_rarity = item['itemRarity']
            item_guid = item['itemGuid']
            try:
                if item_rarity in item_rarities[item_type]:
                    item_guids_to_recycle.append(item_guid)
                    items_to_recycle.append(item)
            except:
                pass
        if len(item_guids_to_recycle) != 0:
            # free llamas
            # Recycling and retiring selected items from opened_llamas free llamas...
            req_get_resources = await profile_request(client, "query", auth_entry)
            req_get_resources_json = orjson.loads(await req_get_resources.read())
            for resource in tracked_resources:
                for item in req_get_resources_json['profileChanges'][0]['profile']['items']:
                    if req_get_resources_json['profileChanges'][0]['profile']['items'][item]['templateId'] == resource:
                        recycle_resources.append({"itemGuid": item,
                                                  "templateId": resource,
                                                  "quantity":
                                                      req_get_resources_json['profileChanges'][0]['profile']['items'][
                                                          item]['quantity']
                                                  })
            json = {"targetItemIds": item_guids_to_recycle}
            recycle_request = await profile_request(client, "batch_recycle", auth_entry, json=json)
            recycle_request_json = orjson.loads(await recycle_request.read())
            req_get_resources2 = await profile_request(client, "query", auth_entry)
            req_get_resources2_json = orjson.loads(await req_get_resources2.read())
            # resources receive
            for resource in recycle_resources:
                resource_quantity = int(
                    req_get_resources2_json['profileChanges'][0]['profile']['items'][resource['itemGuid']][
                        'quantity']) - int(resource['quantity'])
                if resource_quantity > 0:
                    recycle_resources_count += 1
                    resources_message += f"{recycle_resources_count}: {resource_quantity}x {resource['itemName']}. " \
                                         f"Total ammount: {req_get_resources2_json['profileChanges'][0]['profile']['items'][resource['itemGuid']]['quantity']}\n"
            logger.info(resources_message)


async def validate_existing_session(client: Client, token: str) -> bool:
    """
    Validates an existing session

    Args:
        client: The client
        token: The token to validate

    Returns:
        The response from the request
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {token}"
    }
    endpoint = client.config["endpoints"]["verify"]
    valid = await client.stw_session.get(endpoint, headers=header, data="{}")
    # returns code 200 if valid, 401 if invalid
    if valid.status == 200:
        logger.debug(f"Valid session for {token}")
        return True
    logger.debug(f"Invalid session for {token}")
    return False


def vbucks_query_check(profile_text: str | dict) -> bool:
    """
    Checks if the profile can claim vbucks or not

    This takes approximately 0.00016141ms to execute on a 1mb profile

    Args:
        profile_text: text of the target profile json

    Returns:
        True if the profile can claim vbucks, False if not
    """
    if not profile_text:
        logger.error("No profile received")
        return False
    if not isinstance(profile_text, str):
        logger.error("Profile was not a string")
        return False
    if 'Token:receivemtxcurrency' in profile_text:
        logger.debug("Profile can claim vbucks")
        return True
    logger.debug("Profile cannot claim vbucks")
    return False


async def auto_stab_stab_session(client: Client, author_id: int, expiry_time: float) -> None:
    """
    Automatically logs out the user and clears data after a set amount of time

    Args:
        client: the client
        author_id: the id of the user
        expiry_time: the time to wait before logging out

    Returns:
        None
    """
    patience_is_a_virtue = expiry_time - time.time()
    try:
        await asyncio.sleep(patience_is_a_virtue)
        await manslaughter_session(client, author_id, expiry_time)
    except asyncio.CancelledError:
        logger.debug('auto_stab_stab_session was cancelled')
    except Exception as e:
        logger.debug(f"Error in auto_stab_stab_session: {e}")
    return


async def manslaughter_session(client: Client, account_id: int, kill_stamp: int | float | str) -> bool:
    """
    Logs out the user and clears data

    Args:
        client: the client
        account_id: the id of the user to clear
        kill_stamp: the time the user was logged out

    Returns:
        True if the user was logged out, False if not
    """
    try:
        info = client.temp_auth[account_id]
        if kill_stamp == "override" or info['expiry'] == kill_stamp:
            client.temp_auth.pop(account_id, None)

            header = {
                "Content-Type": "application/json",
                "Authorization": f"bearer {info['token']}"
            }
            endpoint = client.config["endpoints"]["kill_token"].format(info['token'])
            await client.stw_session.delete(endpoint, headers=header, data="{}")
            logger.debug(f"Logged out {account_id}")
            return True
    except:
        logger.debug(f"Failed to log out {account_id}, no session found")
        return False
        # 😳 they will know 😳
        # now they know :D


async def entry_profile_req(client: Client, entry: dict[str, str | bool | float | None | list[str]], game: str) -> dict[str, str | bool | float | None | list[str]]:
    """
    Gets the profile of the user for an auth session entry

    Args:
        client: The client
        entry: The auth session entry
        game: The game to get the profile for

    Returns:
        The entry of the user
    """
    profile = await profile_request(client, "query", entry, game=game)
    profile_json = orjson.loads(await profile.read())

    if game == "fn":
        vbucks = await asyncio.gather(asyncio.to_thread(vbucks_query_check, await profile.text()))
        others = await asyncio.gather(asyncio.to_thread(json_query_check, profile_json))
        if others[0] is not None:
            entry["day"] = others[0]
        if not vbucks[0]:
            entry["vbucks"] = False

    if game == "bb":
        others = await asyncio.gather(asyncio.to_thread(bb_day_query_check, profile_json))
        if others[0] is not None:
            entry["bb_day"] = others[0] - 1

    return entry


async def add_other_game_entry(client: Client, user_id: int, entry: dict[str, str | bool | float | None | list[str]], game: str, other_games: list) -> dict[str, str | bool | float | None | list[str]]:
    """
    Adds an entry for another game to the user's auth session

    Args:
        client: The client
        user_id: The id of the user (unused)
        entry: The entry to add to
        game: The game to add the entry for
        other_games: The other games to add an entry for

    Returns:
        The entry of the user
    """
    token = entry[client.config["entry_token_key_for_game"][game]]
    logger.debug(f"Adding entry for {other_games} to {user_id}")

    for other_game in other_games:
        exchange = await exchange_games(client, token, other_game)
        exchange_json = orjson.loads(await exchange.read())
        new_token = exchange_json["access_token"]

        entry[client.config["entry_token_key_for_game"][other_game]] = new_token

        entry["games"].append(other_game)
        entry = await entry_profile_req(client, entry, other_game)
        # This should definitely return the entry so we can allow opt-out
    return entry


async def add_temp_entry(client: Client, ctx: Context, auth_token: str, account_id: str, response: dict, add_entry: bool, bb_token: str = None, game: str = "fn", original_token: str = "") -> dict[str, str | bool | float | None | list[str]]:
    """
    Adds a temporary authentication session entry for the user

    Args:
        client: The client
        ctx: The context
        auth_token: The fortnite access token to store
        account_id: The epic account id
        response: The response (to grab display name)
        add_entry: Whether to start or opt out of an auth session
        bb_token: The battlebreakers access token to store
        game: The game to add the entry for
        original_token: The original token to store (to ignore the token in the future)

    Returns:
        The authentication session entry of the user
    """
    display_name = response["displayName"]

    entry = {
        "token": auth_token,
        "account_id": account_id,
        "vbucks": True,
        "account_name": f"{display_name}",
        'expiry': time.time() + client.config["auth_expire_time"],
        "day": None,
        "bb_token": bb_token,
        "bb_day": None,
        "games": [game],
        "original_token": original_token
    }
    if add_entry:
        asyncio.get_event_loop().create_task(auto_stab_stab_session(client, ctx.author.id, entry['expiry']))

    entry = await entry_profile_req(client, entry, game)
    other_games = list(client.config["entry_token_key_for_game"].keys())
    other_games.remove(game)
    entry = await add_other_game_entry(client, ctx.author.id, entry, game, other_games)

    if add_entry:
        client.temp_auth[ctx.author.id] = entry
    logger.debug(f"Added entry for {ctx.author.id}: {entry}")
    return entry


def json_query_check(profile_text: dict) -> str | int | None:
    """
    Checks if the profile has a days logged in value

    This takes approximately 0.0002796ms to execute on a 1mb profile

    Args:
        profile_text: The profile json object

    Returns:
        The days logged in value if it exists, None if not
    """
    try:
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["daily_rewards"]["totalDaysLoggedIn"]
    except:
        return None


def bb_day_query_check(profile_text: dict) -> str | int | None:
    """
    Checks if the profile has a next login reward level value

    Args:
        profile_text: The profile json object

    Returns:
        The day for tomorrows reward if it exists, None if not
    """
    try:
        # ROOT.profileChanges[0].profile.stats.attributes.login_reward.next_level
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"]
    except:
        return None


def extract_profile_item(profile_json: dict, item_string: str = "Currency:Mtx") -> dict[int, dict[str, Union[str, int]]]:
    """
    Extracts an item from the profile json

    This takes approximately 0.13383596ms to execute on a 1mb profile

    Args:
        profile_json: The profile json object
        item_string: The item to extract

    Returns:
        A dictionary of found items

    Example:
        {
            0: {
                "templateId": "Currency:Mtx",
                "quantity": 1000
            },
            1: {
                "templateId": "Currency:Mtx",
                "quantity": 1000
            }
        }
    """
    found_items = {}
    num = 0
    try:
        for attribute, value in profile_json["profileChanges"][0]["profile"]["items"].items():
            if item_string in value["templateId"]:
                found_items.update({num: value})
                num += 1
    except:
        pass
    logger.debug(f"Found {num} items for {item_string}. Returning {found_items}")
    return found_items


async def get_stw_news(client: Client, locale: str = "en") -> aiohttp.client_reqrep.ClientResponse:
    """
    Gets the news for stw from epic games

    Args:
        client: The client
        locale: The locale to get the news for

    Returns:
        The news for stw from epic games

    Notes:
        This supports the following languages:
        "CompiledCultures": [
            "ar",
            "de",
            "en",
            "es",
            "es-419",
            "fr",
            "it",
            "ja",
            "ko",
            "pl",
            "pt-BR",
            "ru",
            "tr",
            "zh-CN",
            "zh-Hant"
      ]
    """
    logger.debug(f"Getting STW news for {locale}")
    endpoint = client.config["endpoints"]["stw_news"]
    # if locale == "es-ES":
    #     locale = "es"  # TODO: es, es-419, or es-ES?
    if locale == "zh-CHS":
        locale = "zh-CN"
    elif locale == "zh-CHT":
        locale = "zh-CN"  # no traditional unfortunately
    # if locale not in ["ar", "de", "en", "es", "es-419", "fr", "it", "ja", "ko", "pl", "pt-BR", "ru", "tr", "zh-CN", "zh-Hant"]:
    #     locale = "en"
    return await client.stw_session.get(endpoint.format(locale))


async def get_br_news(client: Client, locale: str = "en") -> aiohttp.client_reqrep.ClientResponse:
    """
    Gets the news for br from fortnite-api as its personalised from epic games

    Args:
        client: The client
        locale: The locale to get the news for

    Returns:
        The news for br from fortnite-api

    Notes:
        This supports the following languages:
        - English
        - German
        - Italian
        - French
        - Spanish
        - Russian
        - Japanese
        - Brazilian Portuguese
        - Polish
        - Turkish
        - Arabic
        - Korean
        - Mexican Spanish
    """
    # TODO: This should be changed to use the epic games api
    # We can't use the epic games api as it requires a personalised request
    endpoint = client.config["endpoints"]["br_news"]
    if locale not in ["en", "de", "it", "fr", "es", "ru", "ja", "pt-BR", "pl", "tr", "ar", "ko", "es-419"]:
        locale = "en"
    return await client.stw_session.get(endpoint.format(locale))


async def create_news_page(self, ctx: Context, news_json: dict, current: int, total: int, desired_lang: str = "en") -> discord.Embed:
    """
    Creates a news page embed

    Args:
        self: The client
        ctx: The context
        news_json: The news json
        current: The current page
        total: The total pages
        desired_lang: The desired language

    Returns:
        the constructed news embed
    """
    generic = self.client.colours["generic_blue"]
    try:
        embed = discord.Embed(
            title=await add_emoji_title(self.client, I18n.get("util.news.embed.title", desired_lang), "bang"),
            description=f"\u200b\n{I18n.get('util.news.embed.description', desired_lang, current, total)}\u200b\n"
                        f"**{news_json[current - 1]['title']}**"
                        f"\n{news_json[current - 1]['body']}",
            colour=generic)
    except:
        logger.warning(f"News page {current} is missing from the news json")
        embed = discord.Embed(
            title=await add_emoji_title(self.client, I18n.get("util.news.embed.title", desired_lang), "bang"),
            description=f"\u200b\n{I18n.get('util.news.embed.missing', desired_lang)}",
            colour=generic)

    embed.description += "\u200b"

    # set embed image
    try:
        embed = await set_embed_image(embed, news_json[current - 1]["image"])
    except:
        logger.warning(f"News page {current} is missing an image from the news json")
        embed = await set_embed_image(embed, self.client.config["thumbnails"]["placeholder"])
    embed = await set_thumbnail(self.client, embed, "newspaper")
    embed = await add_requested_footer(ctx, embed, desired_lang)
    return embed


async def battle_breakers_deprecation(client: discord.Client, ctx: commands.Context, command_key: str = "util.battlebreakers.deprecation.embed.description2.generic", desired_lang: str = "en") -> discord.Embed:
    """
    Creates a warning embed for deprecated battle breakers commands

    Args:
        client: The client
        ctx: The context
        command_key: The language key to use for the first line of the embed
        desired_lang: The desired language

    Returns:
        the constructed bb deprecation warning embed
    """
    generic = client.colours["generic_blue"]
    embed = discord.Embed(
        title=await add_emoji_title(client, I18n.get('util.battlebreakers.deprecation.embed.title', desired_lang), "broken_heart"),
        description=f"\u200b\n{I18n.get(command_key, desired_lang)}\u200b\n"
                    f"\n{I18n.get('util.battlebreakers.deprecation.embed.description3', desired_lang, '<t:1672425127:R>')}\n"
                    f"{I18n.get('util.battlebreakers.deprecation.embed.description4', desired_lang, 'https://github.com/dippyshere/battle-breakers-private-server')}",
        colour=generic)
    embed.description += "\u200b\n\u200b"
    embed = await set_thumbnail(client, embed, "disconnected")
    embed = await add_requested_footer(ctx, embed, desired_lang)
    return embed


async def set_embed_image(embed: discord.Embed, image_url: str) -> discord.Embed:
    """
    Sets the embed image to the given url

    Args:
        embed: The embed to set the image for
        image_url: The image url to set

    Returns:
        The embed with the image set
    """
    return embed.set_image(url=image_url)


@AsyncLRU(maxsize=8192)
async def resolve_vbuck_source(vbuck_source: str, desired_lang: str) -> Tuple[str, str]:
    """
    Resolves the vbuck source to a user friendly name and emoji

    Args:
        vbuck_source: The vbuck source
        desired_lang: The desired language

    Returns:
        The user friendly name, and emoji
    """
    if vbuck_source == "Currency:MtxGiveaway":
        return I18n.get('util.vbucks.sources.bp', desired_lang), "bp_icon2"
    elif vbuck_source == "Currency:MtxComplimentary":
        return I18n.get('generic.stw', desired_lang), "library_cal"
    elif vbuck_source == "Currency:MtxPurchased":
        return I18n.get('util.vbucks.sources.purchased', desired_lang), "vbuck_icon"
    elif vbuck_source.lower() == "currency:mtxpurchasebonus":  # idk the casing for this
        return I18n.get('util.vbucks.sources.purchased.bonus', desired_lang), "vbuck_icon"
    elif vbuck_source == "Currency:MtxDebt":
        return I18n.get('util.vbucks.sources.debt', desired_lang), "LMAO"
    else:
        logger.warning(f"Unknown vbuck source: {vbuck_source}")
        return vbuck_source, "placeholder"


async def calculate_vbucks(item: dict) -> int:
    """
    Calculates the total vbucks from a dict of items

    Args:
        item: The dict of items

    Returns:
        The total vbucks quantity
    """
    vbucks = 0
    if item:
        for item in item:
            for attr, val in item.items():
                if "debt" in val["templateId"].lower():
                    vbucks -= val["quantity"]
                else:
                    vbucks += val["quantity"]
    logger.debug(f"Calculated vbucks: {vbucks}")
    return vbucks


@AsyncLRU(maxsize=8192)
async def get_banner_colour(colour: str, colour_format: str = "hex", colour_type: str = "Primary") -> str | tuple[int, ...] | None:
    """
    Gets the banner colour from the banner name

    Args:
        colour: The colour of the banner (e.g. DefaultColor1)
        colour_format: The format to return the colour in (hex, rgb)
        colour_type: The colour to fetch (Primary, Secondary)

    Returns:
        The banner colour in the specified format (default hex)

    Example:
        >>> get_banner_colour("DefaultColor1")
        '#ff0000'
        >>> get_banner_colour("DefaultColor1", colour_format="rgb")
        (255, 0, 0)
    """
    colour_key = BannerColors[0]["Rows"][colour]["ColorKeyName"]
    colour_hex = f'#{BannerColorMap[0]["Properties"]["ColorMap"][colour_key][f"{colour_type}Color"]["Hex"][2:]}'
    if colour_format == "hex":
        return colour_hex
    elif colour_format == "rgb":
        return tuple(int(colour_hex[i:i + 2], 16) for i in (1, 3, 5))
    else:
        logging.error(f"Invalid colour_format {colour_format}. Must be 'hex' or 'rgb'.")
        return None


def truncate(string: str, length: int = 100, end: str = "...") -> str:
    """
    Truncates a string to a certain length

    Args:
        string: The string to truncate
        length: The length to truncate to
        end: The end of the string to use when truncated

    Returns:
        The truncated string

    Example:
        >>> truncate("Hello World", 8)
        'Hello...'
    """
    if len(string) > length:
        logger.debug(f"Truncating string: {string} to {length} characters")
    return (string[:length - len(end)] + end) if len(string) > length else string


def get_tomorrow_midnight_epoch() -> int:
    """
    Gets the epoch for tomorrow UTC midnight, independent of timezone

    Returns:
        The epoch for tomorrow UTC midnight in seconds

    Example:
        >>> get_tomorrow_midnight_epoch()
        1632508800
    """
    return int(time.time() + 86400 - time.time() % 86400)


@functools.cache
def get_item_icon_emoji(client: Client, template_id: str) -> str:
    """
    Gets the emoji for the item icon

    Args:
        client: The client
        template_id: The template id of the item

    Returns:
        The emoji for the item icon

    Example:
        >>> get_item_icon_emoji(client, "AthenaCharacter:cid_028_athena_commando_f")
        '<:cid_028_athena_commando_f:8675309>'
    """
    try:
        try:
            filtered = re.split(r"[/:\s]|_t0", template_id)[1]
        except:
            filtered = template_id
        if 'bow' in filtered:
            logger.debug(f"Matched {filtered} to bow with a similarity of 1.0")
            return client.config['emojis']['bow']
        outcome = max(client.config['emojis'], key=lambda emoji: SequenceMatcher(a=emoji, b=filtered).ratio())
        similarity = SequenceMatcher(a=outcome, b=filtered).ratio()
        if similarity < 0.5:
            # if the first 5 characters match in outcome and filtered, then it's probably a match
            if outcome[:4] == filtered[:4]:
                pass
            else:
                outcome = 'placeholder'
        logger.debug(f"Matched {filtered} to {outcome} with a similarity of {similarity}")
        return client.config['emojis'][outcome]
    except:
        logger.warning(f"Failed to match {template_id} to an emoji")
        return client.config['emojis']['placeholder']


def llama_contents_render(client: Client, llama_items: dict) -> str:
    """
    Renders the contents of a llama

    Args:
        client: The client
        llama_items: The items in the llama

    Returns:
        The rendered contents of the llama

    Example:
        >>> llama_contents_render(client, {"itemType": "AthenaCharacter:cid_028_athena_commando_f", "quantity": 1})
        '<:cid_028_athena_commando_f:8675309> '

        >>> llama_contents_render(client, {"itemType": "AthenaCharacter:cid_028_athena_commando_f", "quantity": 2})
        '<:cid_028_athena_commando_f:8675309> x2 '
    """
    string = ""
    for item in llama_items:
        string += f"{get_item_icon_emoji(client, item['itemType'])}{' x' + str(item['quantity']) if item['quantity'] > 1 else ''} "
    return string


@functools.cache
def get_rating(data_table: dict = SurvivorItemRating, row: str = "Default_C_T01", time_input: float = 0) -> float:
    """
    Calculates the power level of an item in stw

    Args:
        data_table: The data table to use
        row: The row to use
        time_input: The time input

    Returns:
        The power level of the item
    """
    row_data = data_table[0]['Rows'][row]
    # ROOT[0].Rows.Default_C_T01.Keys[0].Time
    # clamp to lower bound.
    if time_input < row_data['Keys'][0]['Time']:
        logger.debug(f"Clamped {time_input} to {row_data['Keys'][0]['Time']}")
        return row_data['Keys'][0]['Value']

    # clamp to upper bound.
    if time_input >= row_data['Keys'][-1]['Time']:
        logger.debug(f"Clamped {time_input} to {row_data['Keys'][-1]['Time']}")
        return row_data['Keys'][-1]['Value']

    # find the two keys that the time_input is between.
    for i in range(len(row_data['Keys']) - 1):
        if row_data['Keys'][i]['Time'] <= time_input < row_data['Keys'][i + 1]['Time']:
            # interpolate between the two keys.
            logger.debug(
                f"Interpolated {time_input} between {row_data['Keys'][i]['Time']} and {row_data['Keys'][i + 1]['Time']} to get {row_data['Keys'][i]['Value'] + (time_input - row_data['Keys'][i]['Time']) / (row_data['Keys'][i + 1]['Time'] - row_data['Keys'][i]['Time']) * (row_data['Keys'][i + 1]['Value'] - row_data['Keys'][i]['Value'])}")
            return row_data['Keys'][i]['Value'] + (time_input - row_data['Keys'][i]['Time']) / (
                    row_data['Keys'][i + 1]['Time'] - row_data['Keys'][i]['Time']) * (
                    row_data['Keys'][i + 1]['Value'] - row_data['Keys'][i]['Value'])


@functools.cache
def parse_survivor_template_id(template_id: str) -> Tuple[str, str, str, str]:
    """
    Parses the template id of a survivor

    Examples of template id's that may be passed:
    Worker:managerexplorer_sr_eagle_t05
    Worker:workerbasic_sr_t05;
    Worker:worker_halloween_smasher_sr_t05
    Worker:worker_joel_ur_t05

    Args:
        template_id: The template id to parse

    Returns:
        The type of survivor (e.g. worker, manager, basic), The tier of survivor (e.g. t01, t02, t03, t04, t05), The rarity of survivor (e.g. c, uc, r, vr, sr, ur), The name of the survivor if available (e.g. eagle, smasher, joel)

    Example:
        >>> parse_survivor_template_id("Worker:managerexplorer_sr_eagle_t05")
        ('manager', 't05', 'sr', 'eagle')

        >>> parse_survivor_template_id("Worker:workerbasic_sr_t05")
        ('basic', 't05', 'sr', None)

        >>> parse_survivor_template_id("Worker:worker_halloween_smasher_sr_t05")
        ('special', 't05', 'sr', 'smasher')

        >>> parse_survivor_template_id("Worker:worker_joel_ur_t05")
        ('special', 't05', 'ur', 'joel')
    """
    tid = template_id.split(":")[1]
    fields = tid.split("_")

    if fields[0] == "worker":
        survivor_type = "special"
        fields.pop(0)
    elif "manager" in fields[0]:
        survivor_type = "manager"
        fields[0] = fields[0].split("manager")[1]
    else:
        survivor_type = "basic"
        fields.pop(0)

    tier = fields.pop(-1)

    if "halloween" in fields[0]:
        fields.pop(0)

    if len(fields) == 1:
        rarity = fields.pop(0)
    else:
        rarity = fields.pop(1)

    # if survivor_type == "manager":
    #     rarity = fields.pop(-2)
    # else:
    #     rarity = fields.pop(-1)

    name = ""
    for val in fields:
        name += val + "_"
    logger.debug(f"Survivor type: {survivor_type}, Tier: {tier}, Rarity: {rarity}, Name: {name[:-1]}")
    return survivor_type, tier, rarity, name[:-1]


# print(parse_survivor_template_id("Worker:managerexplorer_sr_eagle_t05"))
# print(parse_survivor_template_id("Worker:workerbasic_sr_t05"))
# print(parse_survivor_template_id("Worker:worker_halloween_smasher_sr_t05"))
# print(parse_survivor_template_id("Worker:worker_joel_ur_t05"))

# print(get_rating(data_table=HomebaseRatingMapping, row="UIMonsterRating", time_input=52025))
# print(get_rating(data_table=SurvivorItemRating, row="Default_C_T01", time_input=50))

# leader = {
#     'templateId': 'Worker:managergadgeteer_sr_fixer_t05',
#     'attributes': {
#         'squad_id': 'squad_attribute_scavenging_gadgeteers',
#         'personality': 'Homebase.Worker.Personality.IsAnalytical',
#         'level': 50,
#         'squad_slot_idx': 0,
#         'item_seen': True,
#         'managerSynergy': 'Homebase.Manager.IsGadgeteer',
#         'portrait': 'WorkerPortrait:IconDef-ManagerPortrait-SR-Gadgeteer-fixer',
#         'favorite': True,
#         'building_slot_used': -1
#     },
#     'quantity': 1
# }
# worker = {
#     'templateId': 'Worker:workerbasic_sr_t05',
#     'attributes': {
#         'personality': 'Homebase.Worker.Personality.IsAnalytical',
#         'gender': '1',
#         'squad_id': 'squad_attribute_scavenging_gadgeteers',
#         'level': 50,
#         'squad_slot_idx': 5,
#         'item_seen': True,
#         'portrait': 'WorkerPortrait:IconDef-WorkerPortrait-Analytical-M03',
#         'building_slot_used': -1,
#         'set_bonus': 'Homebase.Worker.SetBonus.IsAbilityDamageLow'
#     },
#     'quantity': 1
# }


def get_survivor_rating(survivor: dict) -> Tuple[float, Tuple[str | Any, ...]]:
    """
    Gets the power level of a survivor from a profile's survivor entry dict

    An example of a survivor dict:

    worker = {
        'templateId': 'Worker:workerbasic_sr_t05',

        'attributes': {
            'personality': 'Homebase.Worker.Personality.IsAnalytical',
            'gender': '1',
            'squad_id': 'squad_attribute_scavenging_gadgeteers',
            'level': 50,
            'squad_slot_idx': 5,
            'item_seen': True,
            'portrait': 'WorkerPortrait:IconDef-WorkerPortrait-Analytical-M03',
            'building_slot_used': -1,
            'set_bonus': 'Homebase.Worker.SetBonus.IsAbilityDamageLow'
        },

        'quantity': 1
        }

    Args:
        survivor: The survivor dict. This must have: templateId, attributes.level

    Returns:
        Tuple: (The power level of the survivor, (The type of survivor (e.g. worker, manager, basic), The tier of survivor (e.g. t01, t02, t03, t04, t05), The rarity of survivor (e.g. c, uc, r, vr, sr, ur), The name of the survivor if available (e.g. eagle, smasher, joel)))
    """
    survivor_info = parse_survivor_template_id(survivor["templateId"])
    if survivor_info[0] == "manager":
        survivor_type = "Manager"
    else:
        survivor_type = "Default"
    logger.debug(
        f"Survivor Power Level: {get_rating(data_table=SurvivorItemRating, row=f'{survivor_type}_{survivor_info[2].upper()}_{survivor_info[1].upper()}', time_input=survivor['attributes']['level'])}")
    return get_rating(data_table=SurvivorItemRating,
                      row=f"{survivor_type}_{survivor_info[2].upper()}_{survivor_info[1].upper()}",
                      time_input=survivor["attributes"]["level"]), survivor_info


# print(get_survivor_rating(leader))
# print(get_survivor_rating(worker))

@functools.cache
def get_survivor_bonus(leader_personality: str, survivor_personality: str, leader_rarity: str, survivor_rating: float | int) -> int:
    """
    Gets the bonus to the powerlevel of a survivor based on the leader's personality and rarity, and the survivor's personality and rating

    Args:
        leader_personality: The personality of the leader (e.g. Homebase.Worker.Personality.IsAnalytical)
        survivor_personality: The personality of the survivor (e.g. Homebase.Worker.Personality.IsAnalytical)
        leader_rarity: The rarity of the leader (e.g. c, uc, r, vr, sr, ur)
        survivor_rating: The power level of the survivor (e.g. 50)

    Returns:
        The bonus delta to the power level of the survivor (e.g. 8)
    """
    if leader_personality == survivor_personality:
        if leader_rarity == 'sr' or leader_rarity == 'ur':
            return 8
        if leader_rarity == 'vr':
            return 5
        if leader_rarity == 'r':
            return 4
        if leader_rarity == 'uc':
            return 3
        if leader_rarity == 'c':
            return 2

    elif leader_rarity == 'sr':
        if survivor_rating <= 2:
            return 0
        return -2

    return 0


@functools.cache
def get_lead_bonus(lead_synergy: str, squad_name: str, rating: float | int) -> float:
    """
    Gets the bonus to the power level of a lead survivor based on the leader's synergy, squad and rating

    Args:
        lead_synergy: The synergy of the leader (e.g. Homebase.Manager.IsGadgeteer)
        squad_name: The name of the squad (e.g. squad_attribute_scavenging_gadgeteers)
        rating: The power level of the leader (e.g. 50)

    Returns:
        The lead's rating (to effectively double it) if applicable, otherwise 0, (to effectively do nothing)
    """
    # TODO: move this to a better location
    stw_lead_synergy = {
        "trainingteam": 'IsTrainer',
        "fireteamalpha": 'IsSoldier',
        "closeassaultsquad": 'IsMartialArtist',
        "thethinktank": 'IsInventor',
        "emtsquad": 'IsDoctor',
        "corpsofengineering": 'IsEngineer',
        "scoutingparty": 'IsExplorer',
        "gadgeteers": 'IsGadgeteer'
    }
    if stw_lead_synergy[squad_name] == lead_synergy:
        return rating
    return 0


def calculate_homebase_rating(profile: dict[Any]) -> Tuple[float, int, dict[str, int]]:
    """
    Calculates the power level of a profile's homebase by calculating FORT stats

    Formula to calculate should be something like:

    1. FORT stat calculation
    - query (public) profile campaign
        - loop through items
            - templateId Worker:workerx_xx_xxx
                x - usually 'basic'; Halloween survivors are '_halloween_type'
                xx - rarity; vr - epic, sr - legendary, etc
                xxx - tier; t01-t05, evolution
            - templateId Worker:managerx_xx_xxx_xxxx
                x - leader synergy, doctor, martialartist, trainer etc
                xx - rarity; vr, sr
                xxx - portrait; treky, dragon, yoglattes etc
                xxxx - tier; t01-t05, evolution
        - get rarity, tier, level to calculate power level of survivor (use SurvivorItemRating.json)
            - row 	- Default_C_T01 -> Default_UR_T06
                    - Manager_C_T01 -> Manager_SR_T06
            - mapping appears to be a keys list with the input (time) being level, and output (value) being power level
                - ROOT[0].Rows.{type_rarity_tier}.Keys[point0].Time/Value //linear curve
        - leader job match bonus for each squad
            - (value doubled on correct squad)
        - follower personality match bonus
            - (increased/decreased with leader personality (amount depends on leader rarity))
        - fort stat bonus from research stats
            There are separate items for individual and team stats
    - add up and multiply by 4
    - use HomebaseRatingMapping.json to map value

    # TODO: Ventures stats
    ventures - same mapping, fort stats from phoenix stats

    Args:
        profile: The profile json to calculate the power level of

    Returns:
        The power level of the profile's homebase, total FORT stats, and dict of FORT stats by type
    """
    # ROOT.profileChanges[0].profile.items
    logger.debug("Calculating homebase rating")
    logger.debug(f"Profile: {profile}")
    workers = extract_profile_item(profile, "Worker:")
    survivors = {}
    total_stats = {"fortitude": 0,
                   "offense": 0,
                   "resistance": 0,
                   "technology": 0}
    stw_role_map = {
        "IsTrainer": 'fortitude',
        "IsSoldier": 'offense',
        "IsMartialArtist": 'offense',
        "IsInventor": 'technology',
        "IsDoctor": 'fortitude',
        "IsEngineer": 'technology',
        "IsExplorer": 'resistance',
        "IsGadgeteer": 'resistance'
    }
    # organise into a dict
    for attr, val in workers.items():
        if val["attributes"]["squad_slot_idx"] == -1:
            continue

        # if val["attributes"]["squad_slot_idx"] == 0:
        #     survivors.update({"leader": val})
        # else:
        #     survivors.update({val["attributes"]["squad_slot_idx"]: val})
        # print(val)
        personality = val["attributes"]["personality"].split(".")[-1]
        try:
            squad = val["attributes"]["squad_id"]
        except:
            continue
        if squad == '':
            continue
        rating, info = get_survivor_rating(val)
        if info[0] == "manager":
            synergy = val["attributes"]["managerSynergy"]
            try:
                survivors[squad].update({f"Leader": [rating, info, personality, synergy]})
            except:
                survivors.update({squad: {f"Leader": [rating, info, personality, synergy]}})
        else:
            try:
                survivors[squad]["Followers"].update({f"Follower{attr}": [rating, info, personality]})
            except:
                survivors.update({squad: {"Followers": {f"Follower{attr}": [rating, info, personality]}}})
        # survivors.update()
        # print(rating, personality, squad)
        logger.debug(f"Survivor: {attr} - {val} - {rating} - {personality} - {squad} - {info}")
    logger.debug(f"Survivors before processing: {survivors}")
    # leader / survivor bonuses
    for attr, val in survivors.items():
        try:
            val["Leader"][0] += get_lead_bonus(val["Leader"][-1].split(".")[-1], attr.split("_")[-1], val["Leader"][0])
        except Exception as e:
            logger.error(f"Error calculating leader bonus for {attr}. Error: {e}")
        try:
            for follower, stats in val["Followers"].items():
                try:
                    stats[0] += get_survivor_bonus(val["Leader"][-2], stats[-1], val["Leader"][1][-2], stats[0])
                except Exception as e:
                    logger.error(f"Error calculating follower bonus for {follower}. Error: {e}")
        except Exception as e:
            logger.error(f"Error calculating follower bonus for attr:{attr} val:{val}. Error: {e}")
    # research stats
    # ROOT.profileChanges[0].profile.stats.attributes.research_levels
    research_levels = extract_profile_item(profile, "Stat:")
    logger.debug(f"Research levels: {research_levels}")
    for attr, val in research_levels.items():
        if "_team" in val["templateId"]:
            if "phoenix" in val['templateId'].lower():
                continue
            # total_stats[val['templateId'].split(':')[1].split("_")[0].lower()] += get_rating(data_table=ResearchSystem,
            #                                                                                  row=f"{val['templateId'].split(':')[1]}_cumulative",
            #                                                                                  time_input=val["quantity"])
            total_stats[val['templateId'].split(':')[1].split("_")[0].lower()] += val["quantity"]
            logger.debug(
                f"Research stat: {val['templateId'].split(':')[1].split('_')[0].lower()} ({val['templateId'].split(':')[1]}) - quantity: {val['quantity']} rating: {get_rating(data_table=ResearchSystem, row='{0}_cumulative'.format(val['templateId'].split(':')[1]), time_input=val['quantity'])}")
        else:
            # exclude phoenix stats
            if "phoenix" in val['templateId'].lower():
                continue
            # total_stats[val['templateId'].split(':')[1].lower()] += get_rating(data_table=ResearchSystem,
            #                                                                    row=f"{val['templateId'].split(':')[1]}_personal_cumulative",
            #                                                                    time_input=val["quantity"])
            total_stats[val['templateId'].split(':')[1].lower()] += val["quantity"]
            logger.debug(
                f"Research stat: {val['templateId'].split(':')[1].lower()} ({val['templateId'].split(':')[1]}) - quantity: {val['quantity']} rating: {get_rating(data_table=ResearchSystem, row='{0}_personal_cumulative'.format(val['templateId'].split(':')[1]), time_input=val['quantity'])}")
    # for attr, val in research_levels.items():
    #     total_stats += val
    for attr, val in survivors.items():
        try:
            total_stats[stw_role_map[val["Leader"][-1].split(".")[-1]]] += val["Leader"][0]
        except Exception as e:
            logger.error(f"Error calculating leader stat for {attr}. Error: {e}")
            continue
        for follower, stats in val["Followers"].items():
            try:
                total_stats[stw_role_map[val["Leader"][-1].split(".")[-1]]] += stats[0]
            except Exception as e:
                logger.error(f"Error calculating follower stat for {follower}. Error: {e}")
                continue

    logger.debug(f"Survivors after processing: {survivors}")
    logger.debug(f"Worker stats: {workers}")

    # cmd_level = profile["profileChanges"][0]["profile"]["stats"]["attributes"]["level"]
    #
    # logger.debug(f"Commander level: {cmd_level}")
    # logger.debug(f"Total stats before commander level: {total_stats}")
    # for attr, val in AccountLevels[0]["Rows"].items():
    #     if int(attr) <= cmd_level:
    #         if val["Rewards"][0]["TemplateId"] == "Stat:fortitude":
    #             total_stats['fortitude'] += val["Rewards"][0]["Quantity"]
    #         if val["Rewards"][0]["TemplateId"] == "Stat:offense":
    #             total_stats['offense'] += val["Rewards"][0]["Quantity"]
    #         if val["Rewards"][0]["TemplateId"] == "Stat:resistance":
    #             total_stats['resistance'] += val["Rewards"][0]["Quantity"]
    #         if val["Rewards"][0]["TemplateId"] == "Stat:technology":
    #             total_stats['technology'] += val["Rewards"][0]["Quantity"]

    # combine total stats into one number
    total = 0
    for attr, val in total_stats.items():
        total += val
    logger.debug(f"Total stats: {total_stats}")
    logger.debug(f"Total FORT: {total}")
    logger.debug(
        f"Power level: {get_rating(data_table=HomebaseRatingMapping, row='UIMonsterRating', time_input=total * 4)}")
    return get_rating(data_table=HomebaseRatingMapping, row="UIMonsterRating",
                      time_input=total * 4), total, total_stats


async def check_devauth_user_auth_input(client: Client, ctx: Context, desired_lang: str) -> bool:
    """
    Checks if the user is authorised to use the devauth command

    Args:
        client (discord.Client): The discord client
        ctx: The discord context
        desired_lang (str): The desired language

    Returns:
        bool: True if authorised, False if not
    """
    try:
        user_document = await get_user_document(ctx, client, ctx.author.id, desired_lang=desired_lang)
        currently_selected_profile_id = user_document["global"]["selected_profile"]

        current_profile = user_document["profiles"][str(currently_selected_profile_id)]

        if current_profile["authentication"] is None:
            raise Exception

        return True
    except:
        return False


async def create_error_embed(client: Client, ctx: Context, title: str = None, description: str = None, prompt_help: bool = False, prompt_authcode: bool = True, prompt_newcode: bool = False, command: str = "", error_level: int = 1, title_emoji: str = None, thumbnail: str = None, colour: str = None, add_auth_gif: bool = False, auth_push_strong: bool = True, desired_lang: str = "en", promptauth_key: str = "util.error.embed.promptauth.strong1") -> discord.Embed:
    """
    Creates an embed with the error colour and the error emoji

    Args:
        add_auth_gif:
        client (discord.Client): The discord client
        ctx: The discord context
        title (str): The title of the embed
        description (str): The description of the embed
        prompt_help (bool): If the embed should prompt the user to use the help command
        prompt_authcode (bool): If the embed should prompt the user to get a new code
        prompt_newcode (bool): If the embed should prompt the user to get a new code each time
        command (str): The command to prompt the user to use
        error_level (int): The error level, 0 = warning, 1 = error
        title_emoji (str): The emoji to use for the title
        thumbnail (str): The thumbnail to use
        colour (str): The colour to use
        add_auth_gif (bool): If the embed should add the auth tutorial gif
        auth_push_strong (bool): If the authcode prompt should be forceful or not
        desired_lang (str): The desired language
        promptauth_key (str): The key to use for the promptauth string

    Returns:
        discord.Embed: The created embed
    """
    if error_level:
        if title_emoji is None:
            title_emoji = "error"
        if thumbnail is None:
            thumbnail = "error"
        if colour is None:
            colour = "error_red"
    else:
        if title_emoji is None:
            title_emoji = "warning"
        if thumbnail is None:
            thumbnail = "warn"
        if colour is None:
            colour = "warning_yellow"
    if title is None:
        title = random_error(client, desired_lang)

    embed = discord.Embed(title=await add_emoji_title(client, title, title_emoji), description=f"\u200b\n{description}",
                          colour=client.colours[colour])
    if prompt_authcode and auth_push_strong:
        if embed.description[-3:] != "```":
            embed.description += "\n"
        embed.description += f"\u200b\n{I18n.get(promptauth_key, desired_lang, client.config['login_links']['login_fortnite_pc'])}\n" \
                             f"{I18n.get('util.error.embed.promptauth.strong2', desired_lang, client.config['login_links']['logout_login_fortnite_pc'])}"
    if prompt_authcode and not auth_push_strong:
        if embed.description[-3:] != "```":
            embed.description += "\n"
        embed.description += f"\u200b\n{I18n.get('util.error.embed.promptauth.weak1', desired_lang, client.config['login_links']['login_fortnite_pc'])}\n" \
                             f"{I18n.get('util.error.embed.promptauth.strong2', desired_lang, client.config['login_links']['logout_login_fortnite_pc'])}"
    if prompt_help:
        if embed.description[-3:] != "```":
            embed.description += "\n"
        embed.description += f"\u200b\n{I18n.get('util.error.embed.prompthelp', desired_lang)}\n" \
                             f"{await mention_string(client, 'help {0}'.format(command))}  •  {I18n.get('util.error.embed.prompthelp.1', desired_lang, bytes.fromhex('68747470733A2F2F646973636F72642E67672F51596741425044717A48').decode('utf-8'))}"
    if prompt_newcode:
        embed.description += f"\n{I18n.get('util.error.embed.promptnewcode', desired_lang)}"
    if add_auth_gif:
        embed = await set_embed_image(embed, client.config["thumbnails"]["auth_tutorial"])
    else:
        embed.description += f"\n\u200b"
    embed = await set_thumbnail(client, embed, thumbnail)
    embed = await add_requested_footer(ctx, embed, desired_lang)
    return embed


async def get_or_create_auth_session(client: Client, ctx: Context, command: str, original_auth_code: str, add_entry: bool = False, processing: bool = True, dont_send_embeds: bool = False, desired_lang: str = None) -> list[discord.Message | None, dict, list]:  # hi bye
    """
    I no longer understand this function, its ways of magic are beyond me, but to the best of my ability this is what it returns

    If an authcode is found in the system (aka for this user they are currently authenticated) then one of these two options will be selected:


    A Processing embed should be created:

                [ the message object of the processing ... embed,
                the existing authentication info,
                an empty list which represents no embeds or something?]

    A processing embed should not be created:

                [ None to represent the missing message object for the processing embed,
                The existing authentication information,
                another empty list to represent something]


    If existing authentication information is not found then it will attempt to detect any pre-epic game api request errors, basically input sanitization,
    if an error is found then it returns a list of [False], because obviously past me decided that was a good idea.

    Now if an error does not happen then it returns a list of:
    [ The message object of the processing ... embed,
    the authentication information,
    some sort of embed which represents the successful authentication]

    That hopefully covers everything,
    if you're reading this then say hello in the STW-Daily discord server general channel. ;D

    Args:
        client (discord.Client): The discord client object
        ctx (discord.ext.commands.Context): The context of the command
        command (str): The command that is being executed
        original_auth_code (str): The authcode that was provided by the user
        add_entry (bool, optional): Whether or not to add an entry to the database. Defaults to False.
        processing (bool, optional): Whether or not to create a processing embed. Defaults to True.
        dont_send_embeds: if this is true then it will not send the embeds, this is used for the device auth command
        desired_lang: the language to use for the embeds

    Returns:
        If successfully created auth session, a list - [processing embed, auth info, success embed] <br></br> returns a list - [processing embed, existing auth entry, embed] if auth exists <br></br> returns a list - [False] if an error occurs
    """

    # extract auth code from auth_code
    logger.debug(f"get_or_create_auth_session called with {original_auth_code}")
    extracted_auth_code = extract_auth_code(original_auth_code)
    logger.debug(f"extracted auth code: {extracted_auth_code}")
    embeds = []

    # Attempt to retrieve the existing auth code.
    try:
        existing_auth = client.temp_auth[ctx.author.id]
        existing_token = existing_auth["original_token"]
    except:
        existing_auth = None
        existing_token = None

    # Return auth code if it exists
    if existing_auth is not None and (
            extracted_auth_code == "" or extracted_auth_code == existing_token):  # does that work idk
        if await validate_existing_session(client, existing_auth["token"]):
            # Send the logging in & processing if given-
            if processing and not dont_send_embeds:
                proc_embed = await processing_embed(client, ctx, desired_lang)
                return [await slash_send_embed(ctx, client, proc_embed),
                        existing_auth,
                        embeds]

            return [None, existing_auth, embeds]
        else:
            try:
                del client.temp_auth[ctx.author.id]
            except:
                pass

    white_colour = client.colours["auth_white"]
    error_embed = None

    auth_with_devauth = False
    user_document = None

    # Basic checks so that we don't stab stab epic games so much
    if extracted_auth_code == "":
        try:
            user_document = await get_user_document(ctx, client, ctx.author.id, desired_lang=desired_lang)
            currently_selected_profile_id = user_document["global"]["selected_profile"]

            current_profile = user_document["profiles"][str(currently_selected_profile_id)]

            if current_profile["authentication"] is None:
                raise Exception

            auth_with_devauth = True
        except:
            error_embed = await create_error_embed(client, ctx, title=I18n.get('util.error.createsession.nocode.title',
                                                                               desired_lang),
                                                   description=f"{I18n.get('util.error.createsession.nocode.description1', desired_lang)}\n"
                                                               f"⦾ {I18n.get('util.error.createsession.nocode.description2', desired_lang, client.config['login_links']['login_fortnite_pc'])}\n"
                                                               f"⦾ {I18n.get('util.error.createsession.nocode.description3', desired_lang)}\n"
                                                               f"⦾ {I18n.get('util.error.createsession.nocode.description4', desired_lang, await mention_string(client, '{0} `code`'.format(command)))}",
                                                   prompt_help=True, prompt_authcode=False, prompt_newcode=True,
                                                   command=command, add_auth_gif=True, desired_lang=desired_lang)
    elif extracted_auth_code in client.config["known_client_ids"]:
        error_embed = await create_error_embed(client, ctx,
                                               description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                           f"```{truncate(extracted_auth_code) if len(extracted_auth_code) != 0 else ' '}```\n"
                                                           f"{I18n.get('util.error.createsession.knownid.description1', desired_lang)}\n"
                                                           f"⦾ {I18n.get('util.error.createsession.knownid.description2', desired_lang)}",
                                               prompt_help=True, command=command, add_auth_gif=True,
                                               auth_push_strong=False, desired_lang=desired_lang)

    elif extracted_auth_code == "errors.stwdaily.illegal_auth_code" or (re.sub('[ -~]', '', extracted_auth_code)) != "":
        error_embed = await create_error_embed(client, ctx,
                                               description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                           f"```{truncate(original_auth_code) if len(original_auth_code) != 0 else ' '}```\n"
                                                           f"{I18n.get('util.error.createsession.illegalcode.description1', desired_lang)}\n"
                                                           f"⦾ {I18n.get('util.error.createsession.illegalcode.description2', desired_lang)}\n\n"
                                                           f"{I18n.get('util.error.createsession.illegalcode.description3', desired_lang)}\n"
                                                           f"```a51c1f4d35b1457c8e34a1f6026faa35```",
                                               prompt_help=True, command=command, auth_push_strong=False,
                                               desired_lang=desired_lang)

    elif len(extracted_auth_code) != 32:
        try:
            try:
                extracted_auth_code = extracted_auth_code.replace("token:", "")
            except:
                pass
            user_document = await get_user_document(ctx, client, ctx.author.id, desired_lang=desired_lang)
            current_profile = user_document["profiles"][str(extracted_auth_code)]
            currently_selected_profile_id = int(extracted_auth_code)
            user_document["global"]["selected_profile"] = currently_selected_profile_id
            await replace_user_document(client, user_document)

            if current_profile["authentication"] is None:
                error_embed = await create_error_embed(client, ctx,
                                                       description=f"{I18n.get('util.error.createsession.devauth.noauth.description1', desired_lang)}\n"
                                                                   f"```{current_profile['friendly_name'].replace('`', '')}```\n"
                                                                   f"{I18n.get('util.error.createsession.devauth.noauth.description2', desired_lang)}\n"
                                                                   f"⦾ {I18n.get('util.error.createsession.devauth.noauth.description3', desired_lang, await mention_string(client, 'device'))}"
                                                                   f"",
                                                       prompt_help=True, prompt_authcode=False, command=command,
                                                       desired_lang=desired_lang)

            auth_with_devauth = True
        except:
            error_embed = await create_error_embed(client, ctx,
                                                   description=f"{I18n.get('util.error.auth.title', desired_lang)}\n"
                                                               f"```{truncate(extracted_auth_code)}```\n"
                                                               f"{I18n.get('util.error.createsession.incomplete.description1', desired_lang)}\n"
                                                               f"⦾ {I18n.get('util.error.createsession.incomplete.description2', desired_lang)}\n\n"
                                                               f"{I18n.get('util.error.createsession.illegalcode.description3', desired_lang)}\n"
                                                               f"```a51c1f4d35b1457c8e34a1f6026faa35```",
                                                   prompt_help=True, command=command, add_auth_gif=True,
                                                   auth_push_strong=False, desired_lang=desired_lang)

    if error_embed is not None:
        if not dont_send_embeds:
            await slash_send_embed(ctx, client, error_embed)
            return [False]
        else:
            return error_embed

    if not dont_send_embeds:
        proc_embed = await processing_embed(client, ctx, desired_lang)
        message = await slash_send_embed(ctx, client, proc_embed)
    else:
        message = None

    if not auth_with_devauth:
        token_req = await get_token(client,
                                    extracted_auth_code)  # we auth for fn regardless of the game because exchange
    else:
        token_req = await get_token_devauth(client, user_document)

    response = orjson.loads(await token_req.read())

    if auth_with_devauth:
        try:
            display_name = response["displayName"]
            if display_name != user_document["profiles"][str(currently_selected_profile_id)]["authentication"][
                "displayName"]:
                client.processing_queue[ctx.author.id] = True
                user_document["profiles"][str(currently_selected_profile_id)]["authentication"][
                    "displayName"] = display_name
                await replace_user_document(client, user_document)
                del client.processing_queue[ctx.author.id]
        except:
            pass

    check_auth_error_result = await check_for_auth_errors(client, response, ctx, message, command,
                                                          extracted_auth_code, not dont_send_embeds, desired_lang)

    try:
        success, auth_token, account_id = check_auth_error_result
    except:
        return check_auth_error_result

    if not success:
        return [success]

    # # if authing for battle breakers
    # if game == "bb":
    #     # if session already exists
    #     try:
    #         # if existing fn session exists
    #         if client.temp_auth[ctx.author.id]["token"] is not None:
    #             entry = await add_temp_entry(client, ctx, client.temp_auth[ctx.author.id]["token"],
    #                                          account_id, response, add_entry, bb_token=auth_token, game=game)
    #         # no fn session, set fn token to none
    #         else:
    #             entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
    #                                          game=game)
    #     # no session at all
    #     except:
    #         entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
    #                                      game=game)
    # # if authing for fn
    # else:
    #     # if session already exists
    #     try:
    #         # if existing bb session exists
    #         if client.temp_auth[ctx.author.id]["bb_token"] is not None:
    #             entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry,
    #                                          bb_token=client.temp_auth[ctx.author.id]["bb_token"], game=game)
    #         # no bb session, set bb token to None
    #         else:
    #             entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)
    #     # no session at all (most common outcome of all this junk 🫠)
    #     except:
    #         entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)

    entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry,
                                 original_token=extracted_auth_code)  # authing for fn first
    # print(entry)
    # print(game)
    # if game != "fn":
    #     print("bb")
    #     entry = await add_temp_entry(client, ctx, entry["token"], account_id, response, add_entry,
    #                                  bb_token=auth_token, game=game)  # now auth for desired game
    #     print(entry)

    try:
        display_name_on_auth = user_document["profiles"][str(currently_selected_profile_id)]["settings"][
            "display_name_on_auth"]
    except:
        display_name_on_auth = True

    if display_name_on_auth:
        description = f"```{I18n.get('util.createsession.welcome', desired_lang, entry['account_name'])}```\n"
    else:
        description = "\u200b\n"

    title = I18n.get('util.createsession.welcome.title', desired_lang)
    if auth_with_devauth:
        title = I18n.get('util.createsession.welcome1.title.profile', desired_lang, currently_selected_profile_id)

    embed = discord.Embed(title=await add_emoji_title(client, title, "whitekey"),
                          description=description, colour=white_colour)

    if add_entry:
        expiry = f"<t:{math.floor(client.config['auth_expire_time'] + time.time())}:R>"
        if auth_with_devauth:
            embed.description += f"{I18n.get('util.createsession.welcome.expiry.devauth', desired_lang, client.config['emojis']['stopwatch_anim'], expiry)}\n\u200b\n"
        else:
            embed.description += f"{I18n.get('util.createsession.welcome.expiry', desired_lang, client.config['emojis']['stopwatch_anim'], expiry)}\n\u200b\n"
    else:
        embed.description += f"{I18n.get('util.createsession.welcome.optout', desired_lang, client.config['emojis']['cross'])}\n\u200b\n"

    if auth_with_devauth:
        embed.description += f"{I18n.get('util.createsession.welcome.devauth', desired_lang, client.config['emojis']['link_icon'], 'https://github.com/dippyshere/stw-daily/wiki')}\n\u200b\n"

    if not entry['vbucks']:
        embed.description += f"• {I18n.get('util.createsession.welcome.nonfounder', desired_lang, client.config['emojis']['xray'], client.config['emojis']['vbucks'], 'https://github.com/dippyshere/stw-daily/wiki')}\n\u200b"
    if not entry['vbucks'] and not entry['day']:
        embed.description += "\n"
    if not entry['day']:
        embed.description += f"• {I18n.get('util.createsession.welcome.nostw', desired_lang, 'https://github.com/dippyshere/stw-daily/wiki')}\n\u200b"

    # if add_entry and not auth_with_devauth and original_auth_code != "":
    #     try:
    #         user_document = await get_user_document(ctx, client, ctx.author.id)
    #         for profile in user_document["profiles"]:
    #             if profile["authentication"] is not None:
    #                 auth_info_thread = await asyncio.gather(
    #                     asyncio.to_thread(decrypt_user_data, ctx.author.id, profile["authentication"]))
    #                 dev_auth_info = auth_info_thread[0]
    #                 if dev_auth_info["accountId"] == entry["accountId"]:
    #
    #     except:
    #         pass

    try:
        keycard = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["keycard"]
    except:
        keycard = "keycard"

    embed = await set_thumbnail(client, embed, keycard)
    embed = await add_requested_footer(ctx, embed, desired_lang)

    embeds.append(embed)
    return [message, entry, embeds]


async def post_error_possibilities(ctx: Context | discord.Interaction, client: Client,
                                   command: str, acc_name: str, error_code: str,
                                   error_level: int = 1, response: str = None,
                                   verbiage_action: str = None, hb_badchars: str | list[str] = None,
                                   desired_lang: str = None) -> discord.Embed:
    """
    Handle errors that could occur when posting to the api, and present an embed with possible solutions

    Args:
        ctx: The context of the command
        client: The client
        command: The command that was run
        acc_name: The account name of the user
        error_code: The error code that was returned
        error_level: The level of error, either error or warning
        response: The response from the api
        verbiage_action: The action that was being performed (as an i18n key - util.error.posterrors.title.{})
        hb_badchars: The bad characters that were found in the homebase name
        desired_lang: The language that the user wants to use

    Returns:
        an error embed
    """
    logger.debug(f"Epic Games Error Code: {error_code}. Response: {response}")
    reattempt_for_devauth = False
    if verbiage_action is None:
        verbiage_action = "generic"

    # Epic Games Error Codes
    if error_code == "errors.com.epicgames.common.missing_action":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get(f'util.error.posterrors.failto.{verbiage_action}', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.nofortnite.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.nofortnite.description2', desired_lang)}",
                                         prompt_help=True, command=command, auth_push_strong=False,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.account.account_not_active":
        embed = await create_error_embed(client, ctx,
                                         description=f"Attempted to {verbiage_action} for account:\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get(f'util.error.posterrors.failto.{verbiage_action}', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.inactive.description1', desired_lang)}",
                                         prompt_help=True, command=command, auth_push_strong=False,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.fortnite.check_access_failed":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.auth.nostw.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description2', desired_lang, f'`{command.capitalize()}`')}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description3', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.nostw.description4', desired_lang)}",
                                         prompt_help=True, command=command, auth_push_strong=False,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.common.authentication.token_verification_failed":
        reattempt_for_devauth = True
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors1.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get(f'util.error.posterrors.failto.{verbiage_action}.session', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.expiredsession.description2', desired_lang, await mention_string(client, 'auth `code`'))}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.expiredsession.description3', desired_lang, await mention_string(client, 'kill'), await mention_string(client, command))}",
                                         prompt_help=True, command=command, auth_push_strong=False,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.validation.validation_failed" or error_code == "errors.com.epicgames.common.unsupported_media_type":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors1.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.stwscrewedup.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stwscrewedup.description1', desired_lang)}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)
        logger.critical(f"Error Code: {error_code}. Response: {response}")
    elif error_code == "errors.com.epicgames.accountportal.date_of_birth_verification_required":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors1.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.auth.cabined.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.cabined.description2', desired_lang, 'https://www.epicgames.com/fortnite')}",
                                         prompt_help=True, command=command,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.modules.gamesubcatalog.purchase_not_allowed":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.purchase.notallowed.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.purchase.notallowed.description2', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.purchase.returning', desired_lang, f'<t:{int(time.time()) + 7}:R>')}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.modules.gamesubcatalog.cannot_afford_purchase":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.purchase.cannotafford.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.purchase.returning', desired_lang, f'<t:{int(time.time()) + 7}:R>')}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == "errors.com.epicgames.modules.gamesubcatalog.catalog_out_of_date":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.purchase.outdated.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.purchase.outdated.description2', desired_lang, await mention_string(client, command))}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.purchase.returning', desired_lang, f'<t:{int(time.time()) + 7}:R>')}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)
    elif error_code == 'errors.com.epicgames.account.invalid_account_credentials':
        # invalid grant error
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.auth.devauth.expired.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.auth.devauth.expired.description2', desired_lang, await mention_string(client, 'kill'), await mention_string(client, 'device'))}\n"
                                                     f"⦾ {I18n.get('util.error.auth.devauth.expired.description3', desired_lang)}",
                                         prompt_help=True, command=command, desired_lang=desired_lang)

    elif error_code == "errors.com.epicgames.fortnite.town_name_validation":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.posterrors1.title.hbrn', desired_lang)}\n\u200b\n"
                                                     f"{I18n.get('util.error.posterrors.stw.homebase.illegal.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description2.generic', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description4', desired_lang, 'https://github.com/dippyshere/stw-daily/wiki')}",
                                         prompt_authcode=False, command=command, prompt_help=True,
                                         error_level=error_level, desired_lang=desired_lang)

    # battle breakers error codes
    elif error_code == "errors.com.epicgames.world_explorers.login_reward_not_available":
        reward = get_bb_reward_data(client, response, True, desired_lang=desired_lang)
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.posterrors.wex.daily.claimed.description1', desired_lang, reward[0])}\n"
                                                     f"\u200b\n"
                                                     f"{I18n.get('daily.embed.alreadyclaimed.description2', desired_lang, reward[2])}\n"
                                                     f"```{reward[4]} {reward[1]}```\n"
                                                     f"{I18n.get('daily.embed.alreadyclaimed.description2', desired_lang, f'<t:{get_tomorrow_midnight_epoch()}:R>')}",
                                         prompt_authcode=False, command=command, error_level=0, desired_lang=desired_lang)

    # STW Daily Error Codes
    elif error_code == "errors.stwdaily.failed_guid_research":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.research.guidfail.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.research.guidfail.description2', desired_lang)}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.failed_get_collected_resource_item":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.research.failitem.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.research.guidfail.description2', desired_lang)}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.failed_get_collected_resource_type":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.research.failresource.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.research.guidfail.description2', desired_lang)}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.failed_total_points":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                     f"```{acc_name}```\n"
                                                     f"{I18n.get('util.error.posterrors.research.failtotal.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.research.guidfail.description2', desired_lang)}",
                                         prompt_help=True, prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.not_author_interaction_response":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.posterrors.stw.notauthor.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stw.notauthor.description2', desired_lang, command)}",
                                         prompt_authcode=False, command=command,
                                         error_level=0, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.homebase_long":
        embed = await create_error_embed(client, ctx,
                                         description=f"{I18n.get('util.error.posterrors.title.hbrn', desired_lang)}\n"
                                                     f"```{truncate(acc_name)}```\n"
                                                     f"{I18n.get('util.error.posterrors.stw.homebase.long.description1', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stw.homebase.long.description2', desired_lang)}\n"
                                                     f"⦾ {I18n.get('util.error.posterrors.stw.homebase.long.description3', desired_lang, await mention_string(client, 'help {0}'.format(command)))}",
                                         prompt_authcode=False, command=command,
                                         error_level=error_level, desired_lang=desired_lang)

    elif error_code == "errors.stwdaily.homebase_illegal":
        if hb_badchars is None or len(hb_badchars) == 0:
            embed = await create_error_embed(client, ctx,
                                             description=f"{I18n.get('util.error.posterrors.title.hbrn', desired_lang)}\n"
                                                         f"```{truncate(acc_name)}```\n"
                                                         f"{I18n.get('util.error.posterrors.stw.homebase.illegal.description1', desired_lang)}\n"
                                                         f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description2.generic', desired_lang)}\n"
                                                         f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description4', desired_lang, 'https://github.com/dippyshere/stw-daily/wiki')}",
                                             prompt_authcode=False, command=command, prompt_help=True,
                                             error_level=error_level, desired_lang=desired_lang)
        else:
            hb_badchars = f'`{", ".join(hb_badchars)}`'
            embed = await create_error_embed(client, ctx,
                                             description=f"{I18n.get('util.error.posterrors.title.hbrn', desired_lang)}\n"
                                                         f"```{truncate(acc_name)}```\n"
                                                         f"{I18n.get('util.error.posterrors.stw.homebase.illegal.description1', desired_lang)}\n"
                                                         f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description2.specific', desired_lang, hb_badchars)}\n"
                                                         f"⦾ {I18n.get('util.error.posterrors.stw.homebase.illegal.description4', desired_lang, 'https://github.com/dippyshere/stw-daily/wiki')}",
                                             prompt_authcode=False, command=command, prompt_help=True,
                                             error_level=error_level, desired_lang=desired_lang)

    else:
        shrug = u'¯\\\_(ツ)\_/¯'
        logger.warning(f"Unknown error code: {error_code}. Response: {response}")
        try:
            embed = await create_error_embed(client, ctx,
                                             description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                         f"```{acc_name}```\n"
                                                         f"{I18n.get('util.error.auth.unknown.description1', desired_lang, shrug)}\n"
                                                         f"⦾ {I18n.get('util.error.auth.unknown.description2', desired_lang)}\n"
                                                         f"```{error_code}\n\n{response['errorMessage']}```",
                                             prompt_help=True, command=command, auth_push_strong=False,
                                             error_level=error_level, desired_lang=desired_lang)
        except:
            embed = await create_error_embed(client, ctx,
                                             description=f"{I18n.get(f'util.error.posterrors.title.{verbiage_action}', desired_lang)}\n"
                                                         f"```{acc_name}```\n"
                                                         f"{I18n.get('util.error.auth.unknown.description1', desired_lang, shrug)}\n"
                                                         f"⦾ {I18n.get('util.error.auth.unknown.description2', desired_lang)}\n"
                                                         f"```{error_code}```",
                                             prompt_help=True, command=command, auth_push_strong=False,
                                             error_level=error_level, desired_lang=desired_lang)
    return embed


async def strip_string(string: str) -> str:
    """
    Strips a string of all non-alphanumeric characters

    Args:
        string: string to be stripped

    Returns:
        regex stripped string
    """
    return re.sub("[^0-9a-zA-Z]+", "", string)


@AsyncLRU(maxsize=8192)
async def slash_name(client: Client, command: Command) -> str | Command:
    """
    Tries to find the name of a slash command from the command's normal name

    Args:
        client: discord client
        command: slash name of command

    Returns:
        string of slash name
    """
    commands = client._application_commands.values()
    for slash in commands:
        if slash.name == command:
            logger.debug(f"Found slash name for {command}: {slash.name}")
            return slash.name
    # run hardcoded checks here if the slash name differs from real name :D
    logger.debug(f"Could not find slash name for {command}")
    return command


@AsyncLRU(maxsize=8192)
async def slash_mention_string(client: Client, command: Command, return_placeholder: bool = False) -> str | None:
    """
    Returns a string with the slash command and mention

    Args:
        client: discord client
        command: slash name of command
        return_placeholder: if true, returns a placeholder string if the command is not found

    Returns:
        string with slash command and mention
    """
    for x in client._application_commands.values():
        if x.name == command:
            logger.debug(f"Found slash name for {command}: {x.name}")
            return f"</{x.name}:{x.id}>"
    if return_placeholder:
        logger.debug(f"Could not find slash name for {command}")
        return f"`/{command}`"
    else:
        logger.debug(f"Could not find slash name for {command}")
        return None


def create_command_dict(client: Client) -> Tuple[dict, dict, list]:
    """
    Creates a dictionary of all commands and their aliases

    Args:
        client: discord client

    Returns:
        a dictionary of command names, dictionary of commands, and list of command names
    """
    command_name_dict = {}
    command_dict = {}

    # Gets aliases and adds them to command_name_dict so we can match for aliases too in the command arg
    for command in client.commands:
        command_name_dict[command.name] = command.name
        for alias in command.aliases:
            command_name_dict[alias] = command.name

        # Adds the command to the command dict
        command_dict[command.name] = command
    logger.debug(f"Created command dictionary: {command_name_dict} and {command_dict}")
    return command_name_dict, command_dict, list(command_name_dict)


def extract_auth_code(string: str) -> str:
    """
    Extracts the auth code from a string

    Args:
        string: string to extract from

    Returns:
        The extracted auth code if possible, else an error code if the string is the correct length, finally just returns the string
    """
    try:
        return re.search(r"[0-9a-f]{32}", string)[0]  # hi
    except TypeError:
        if len(string) == 32:
            return "errors.stwdaily.illegal_auth_code"
        return string


@deprecation.deprecated(details="Use `validate_homebase_name` instead")
async def is_legal_homebase_name(string: str) -> bool:
    """
    Checks if a string is a legal homebase name

    Homebase names must be alphanumeric, with limited support for extra characters.

    Deprecated: Use `validate_homebase_name` instead

    Args:
        string: string to check

    Returns:
        True if legal, else False
    """
    # TODO: add obfuscated filter for protected homebase names
    return re.match(r"^[0-9a-zA-Z '\-._~]{1,16}$", string) is not None


async def validate_homebase_name(string: str) -> Tuple[bool, list[str]]:
    """
    validate a homebase name against the allowed characters datatable

    Args:
        string (str): the name to validate

    Returns:
        bool: True if the string is valid, False if the string is not valid
        tuple: a tuple containing the list of invalid characters used

    Example:
        >>> validate_homebase_name("test")
        (True, [])
        >>> validate_homebase_name("test!")
        (False, ['!'])
    """

    list_of_invalid_chars_used = []

    # loop through the string
    for char in string:
        # get the unicode decimal value of the character
        char_value = ord(char)

        # check if the character is in the excluded points list
        if char_value in allowed_chars["excludedPoints"]:
            # the character is in the excluded points list
            list_of_invalid_chars_used.append(char)
            continue

        # check if the character is in the single points list
        if char_value in allowed_chars["singlePoints"]:
            # the character is in the single points list
            continue

        # check if the character is within the ranges
        for i in range(0, len(allowed_chars["ranges"]), 2):
            # check if the character is in the range
            if allowed_chars["ranges"][i] <= char_value <= allowed_chars["ranges"][i + 1]:
                # the character is in the range
                break
        else:
            # the character is not in the range
            list_of_invalid_chars_used.append(char)
            continue

    # check if there are any invalid characters used
    if len(list_of_invalid_chars_used) > 0:
        # there are invalid characters used
        logger.debug(f"String {string} is not valid, invalid characters used: {list_of_invalid_chars_used}")
        return False, list_of_invalid_chars_used

    # the string is valid
    logger.debug(f"String {string} is valid")
    return True, list_of_invalid_chars_used


@functools.lru_cache(maxsize=8)
async def generate_banner(client: discord.Client, embed: discord.Embed, homebase_icon: str,
                          homebase_colour: str, author_id: int | str) -> tuple[
    discord.Embed, discord.File]:
    """
    Generates a banner thumbnail for the embed

    Args:
        client: discord client
        embed: embed to add the banner to
        homebase_icon: homebase icon to use (e.g. ot7banner)
        homebase_colour: homebase colour to use (e.g. defaultcolor15)
        author_id: author id to use for the banner

    Returns:
        Embed with thumbnail set to the banner, discord attachment of file generated

    Example:
        >>> embed = discord.Embed()
        >>> embed = await generate_banner(client, embed, "ot7banner", "defaultcolor15", 123456789)
        >>> embed.thumbnail.url
        'attachment://banner.png'
    """
    banner_url = f"https://fortnite-api.com/images/banners/{homebase_icon}/icon.png"
    async with client.stw_session.get(banner_url) as resp:
        data = io.BytesIO(await resp.read())
        banner_screen = blendmodes.blend.blendLayers(Image.open(data).convert("RGB").resize((256, 256)),
                                                     Image.new("RGB", (256, 256),
                                                               await get_banner_colour(homebase_colour, "rgb")),
                                                     blendmodes.blend.BlendType.SCREEN)
        banner_texture = blendmodes.blend.blendLayers(banner_screen, banner_d, blendmodes.blend.BlendType.DIVIDE)
        banner_masked = blendmodes.blend.blendLayers(banner_texture, banner_m, blendmodes.blend.BlendType.DESTIN)
        att_img = io.BytesIO()
        banner_masked.save(att_img, format='PNG')
        att_img.seek(0)
        file = discord.File(att_img, filename=f"{author_id}banner.png")
    embed.set_thumbnail(url=f"attachment://{author_id}banner.png")
    return embed, file


@functools.lru_cache(maxsize=8)
async def generate_power(client: discord.Client, embed: discord.Embed, power_level: int | float,
                         author_id: int | str) -> tuple[discord.Embed, discord.File]:
    """
    Generates a banner thumbnail for the embed

    Args:
        client: discord client
        embed: embed to add the banner to
        power_level: power level to use
        author_id: author id to use for the banner

    Returns:
        Embed with thumbnail set to the banner, discord attachment of file generated

    Example:
        >>> embed = discord.Embed()
        >>> embed = await generate_banner(client, embed, "ot7banner", "defaultcolor15", 123456789)
        >>> embed.thumbnail.url
        'attachment://banner.png'
    """
    power_level_float, power_level_int = math.modf(power_level)
    width, height = (200, 200)
    power_level_str = str(int(power_level_int))
    power_level_display = Image.new(mode="RGBA", size=(width, height), color=(30, 30, 1, 1))
    draw_image = ImageDraw.Draw(power_level_display, 'RGBA')
    _, _, w, _ = draw_image.textbbox((0, 0), power_level_str, font=burbank)
    draw_image.text(((width - w) / 2, 40), power_level_str, fill=(255, 255, 255), font=burbank)
    draw_image.rounded_rectangle((20, 130, 180, 170), radius=3, outline=(255, 255, 255), width=4)
    percentage = 180 * power_level_float
    draw_image.rounded_rectangle((20, 130, percentage, 170), radius=3, fill=(255, 255, 255), outline=(255, 255, 255),
                                 width=4)
    arr = io.BytesIO()
    power_level_display.save(arr, format='PNG')
    arr.seek(0)
    file = discord.File(arr, filename=f"{author_id}power.png")
    embed.set_thumbnail(url=f"attachment://{author_id}power.png")
    return embed, file


@AsyncLRU(maxsize=8192)
async def research_stat_rating(stat: str, level: int) -> tuple[float, float, float]:
    """
    Calculates the % stat buff given to player + team from a research level

    Args:
        stat: string of the stat (e.g. fortitude, offense, resistance, technology)
        level: level of the stat

    Returns:
        tuple: The combined rating of the stat, the personal rating, the team rating

    Example:
        >>> research_stat_rating("fortitude", 10)
        (0.1, 0.05, 0.05)
    """
    personal_rating = get_rating(data_table=ResearchSystem, row=f"{stat}_personal_cumulative", time_input=level)
    team_rating = get_rating(data_table=ResearchSystem, row=f"{stat}_team_cumulative", time_input=level)
    logger.debug(
        f"Research stat {stat} level {level} rating: {personal_rating + team_rating} (personal: {personal_rating}, team: {team_rating})")
    return personal_rating + team_rating, personal_rating, team_rating


@functools.cache
def research_stat_cost(stat: str, level: int) -> float:
    """
    Calculates the cost to upgrade a research stat
    I'm not sure if the level given is the current level, or the next level, assume the next level

    Args:
        stat: string of the stat (e.g. fortitude, offense, resistance, technology)
        level: current level of the stat

    Returns:
        tuple: The cost to upgrade the stat

    Example:
        >>> research_stat_cost("fortitude", 10)
        100000
    """
    logger.debug(
        f"Research stat {stat} level {level} cost: {get_rating(data_table=ResearchSystem, row=f'{stat}_cost', time_input=sorted((0, level + 1, 120))[1])}")
    return get_rating(data_table=ResearchSystem, row=f"{stat}_cost", time_input=sorted((0, level + 1, 120))[1])


def convert_iso_to_unix(iso_timestamp: str) -> int:
    """
    Converts an ISO timestamp to a unix timestamp rounded to the nearest second

    Args:
        iso_timestamp: ISO timestamp to convert

    Returns:
        unix timestamp rounded to the nearest second

    Example:
        >>> convert_iso_to_unix("2021-01-01T00:00:00.000Z")
        1609459200

        >>> convert_iso_to_unix("2021-01-01T00:00:00.000+00:00")
        1609459200
    """
    logger.debug(
        f"Converted ISO timestamp {iso_timestamp} to unix timestamp: {round(datetime.datetime.fromisoformat(iso_timestamp).timestamp())}")
    return round(datetime.datetime.fromisoformat(iso_timestamp).timestamp())


@functools.lru_cache(maxsize=8)
def get_progress_bar(start: int, end: int, length: int) -> str:
    """
    Generates a progress bar

    Args:
        start: start of the progress bar
        end: end of the progress bar
        length: length of the progress bar

    Returns:
        progress bar string

    Example:
        >>> get_progress_bar(0, 100, 10)
        "[----------]"

        >>> get_progress_bar(50, 100, 10)
        "[====------]"

        >>> get_progress_bar(100, 100, 10)
        "[==========]"
    """
    return f"[{'=' * round((start / end) * length)}{'-' * (length - round((start / end) * length))}]"

# Utility library for STW daily.
import asyncio
import datetime
import random
import re
import time
import math
import json

import discord

import items
import ext.battlebreakers.BBLootTable  # dinnerbrb

with open("ext/battlebreakers/LoginRewards.json", "r") as LoginRewards:
    LoginRewards = json.load(LoginRewards)

guild_ids = None


def process_quotes_in_message(message):
    # do not question the ways of the regex
    re_iter = re.finditer(r'((?:(?:^|\s)\")|(?:\"(?:\s|$)))', message.content)

    indices = [m.start(0) for m in re_iter]
    content = list(message.content)

    if len(indices) == 1:
        indices = []

    else:

        rem_values = []

        # true represents an ending ", False represents a starting "
        temp_indices = [True if content[index] == '"' else False for index in indices]

        for index, value in enumerate(temp_indices[:-1]):

            if not value:
                indices[index] += 1
                if not temp_indices[index + 1]:
                    rem_values.append(index + 1)

            elif temp_indices[index + 1] and value:
                rem_values.append(index)

        for remove_index in rem_values:
            indices[remove_index] = 0

    # fear my list comprehension
    escaped_content = [r'\\"' if char == '"' and index not in indices else char for index, char in enumerate(content)]

    # reform list into a string
    message.content = "".join(escaped_content)

    return message


# a small bridge helper function between slash commands and normal commands
async def slash_send_embed(ctx, slash, embeds, view=None):
    try:
        embeds[0]
    except:
        embeds = [embeds]

    if slash:
        if view is not None:
            return await ctx.respond(embeds=embeds, view=view)
        else:
            return await ctx.respond(embeds=embeds)
    else:
        if view is not None:
            return await ctx.send(embeds=embeds, view=view)
        else:
            return await ctx.send(embeds=embeds)


async def retrieve_shard(client, shard_id):
    if shard_id > len(client.config["shard_names"]):
        return shard_id

    return client.config["shard_names"][shard_id]


# returns the time until the end of the day
def time_until_end_of_day():
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    a = datetime.datetime.combine(tomorrow, datetime.time.min) - datetime.datetime.utcnow()
    hours, remainder = divmod(int(a.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = ''
    if hours == 1:
        fmt += '{h} hour, '
    else:
        fmt += '{h} hours, '
    if minutes == 1:
        fmt += '{m} minute'
    else:
        fmt += '{m} minutes'
    return fmt.format(h=hours, m=minutes)


async def mention_string(client, prompt):
    me = client.user
    try:
        return f"{me.mention} {prompt}"
    except AttributeError:
        return "Mention me and then type {prompt} after!"


# adds the requested by person thing to the footer
async def add_requested_footer(ctx, embed):
    try:
        embed.set_footer(text=
                         f"\nRequested by: {ctx.author.name}"
                         , icon_url=ctx.author.display_avatar.url)
    except:
        embed.set_footer(text=
                         f"\nRequested by: {ctx.user.name}"
                         , icon_url=ctx.user.display_avatar.url)

    embed.timestamp = datetime.datetime.now()

    return embed


# adds emojis to either side of the title
async def add_emoji_title(client, title, emoji):
    emoji = client.config["emojis"][emoji]
    return f"{emoji}  {title}  {emoji}"


async def split_emoji_title(client, title, emoji_1, emoji_2):
    emoji_1 = client.config["emojis"][emoji_1]
    emoji_2 = client.config["emojis"][emoji_2]
    return f"{emoji_1}  {title}  {emoji_2}"


# shortens setting thumbnails for embeds
async def set_thumbnail(client, embed, thumb_type):
    embed.set_thumbnail(url=client.config["thumbnails"][thumb_type])
    return embed


def get_reward(client, day, vbucks=True):
    day_mod = int(day) % 336
    if day_mod == 0:
        day_mod = 336

    item = items.ItemDictionary[str(day_mod)]
    emojis = item[1:]

    if not vbucks:
        try:
            item = [item[0].replace('V-Bucks & ', '')]
            emojis.remove('vbucks')
        except:
            pass

    emoji_text = ""
    for emoji in emojis:
        emoji_text += client.config["emojis"][emoji]

    return [item[0], emoji_text]


def get_bb_reward_data(client, response=None, error=False, pre_calc_day=0):
    if error:
        day = response['messageVars'][0] - 1  # hello world explorer hi
    elif pre_calc_day > 0:  # do u see me minimizing it no
        day = pre_calc_day
    else:
        day = response["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"] - 1

    # im not sure if it actually loops after day 1800, but just in case not like anyone will use this command anyway
    day_mod = int(day) % 1800
    if day_mod == 0:
        day_mod = 1800

    # done FORTIFICAITION OF THE NIGHT hmm i see folders
    asset_path_name = LoginRewards[0]["Rows"][str(day_mod)]["ItemDefinition"]["AssetPathName"]
    quantity = LoginRewards[0]['Rows'][str(day_mod)]['ItemCount']

    emoji, name, description = ext.battlebreakers.BBLootTable.BBLootTable[asset_path_name]

    emoji_text = client.config["emojis"][emoji]

    return [day, name, emoji_text, description]


async def get_token(client, auth_code: str, game="fn"):
    if game == "bb":
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic M2NmNzhjZDNiMDBiNDM5YTg3NTVhODc4YjE2MGM3YWQ6YjM4M2UwZjQtZjBjYy00ZDE0LTk5ZTMtODEzYzMzZmMxZTlk="
        }
    else:
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
        }
    d = {
        "grant_type": "authorization_code",
        "code": auth_code
    }
    url = client.config["endpoints"]["token"]

    return await client.stw_session.post(url, headers=h, data=d)


async def processing_embed(client, ctx):
    colour = client.colours["success_green"]

    embed = discord.Embed(title=await add_emoji_title(client, "Logging In And Processing", "processing"),
                          description='```This shouldn\'t take long...```', colour=colour)
    embed = await add_requested_footer(ctx, embed)
    return embed


def ranerror(client):
    return random.choice(client.config["error_messages"])


async def check_for_auth_errors(client, request, ctx, message, command, auth_code, slash, invite_link):
    try:
        return True, request["access_token"], request["account_id"]
    except:
        error_code = request["errorCode"]

    error_colour = client.colours["error_red"]

    print(f'[ERROR]: {error_code}')
    # TODO: change links client id's
    if error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
        # login error
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to authenticate with authcode:
            ```{auth_code}```
            **This authcode is invalid, there are a few reasons why this can happen such as:**
            ⦾ Your authcode has expired, you need to enter your authcode into the auth command within about a minute after getting it.
            ⦾ You got the wrong type of authcode, such as the one from the url instead of the one from the body of the page
            \u200b
            You'll need to get a new auth code, you can get one by:
            [Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)
            \u200b
            An example of what your auth code should look like is:
            ```a51c1f4d35b1457c8e34a1f6026faa35```
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({invite_link})
            Note: You need a new code __every time you authenticate__\n\u200b
            """,
            colour=error_colour
        )

    elif error_code == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
        # invalid grant error
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to authenticate with authcode:
            ```{auth_code}```
            This authorisation code is invalid because it was created with the wrong link.
            [You'll need to get a new authcode using this link](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({invite_link})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour)

    elif len(error_code) == 32:
        # login error
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to authenticate with authcode:
            ```{auth_code}```
            **This authcode is invalid because this account does not own Fortnite: Save The World**
            ⦾ You need STW to claim your any rewards, Note: you can only get V-Bucks if you own a __Founders Pack__ which is no longer available.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({invite_link})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    else:
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to authenticate with:
            ```{auth_code}```
            Unknown reason for not being able to authenticate please try again, error received from epic:
            ```{error_code}```
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({invite_link})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    embed = await set_thumbnail(client, embed, "error")
    embed = await add_requested_footer(ctx, embed)
    await slash_edit_original(message, slash, embed)
    return False, None, None


async def slash_edit_original(msg, slash, embeds, view=None):
    try:
        embeds[0]
    except:
        embeds = [embeds]

    if not slash:
        if view is not None:
            return await msg.edit(embeds=embeds, view=view)
        else:
            return await msg.edit(embeds=embeds)
    else:
        if view is not None:
            return await msg.edit_original_response(embeds=embeds, view=view)
        else:
            return await msg.edit_original_response(embeds=embeds)


async def profile_request(client, req_type, auth_entry, data="{}", json=None, profile_id="stw", game="fn"):
    if game == "bb":
        token = auth_entry["bb_token"]
        url = client.config["endpoints"]["bb_profile"].format(auth_entry["account_id"],
                                                              client.config["profile"][req_type])
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


def vbucks_query_check(profile_text):
    if 'Token:receivemtxcurrency' in profile_text:
        return True
    return False


async def auto_stab_stab_session(client, author_id, expiry_time):
    patience_is_a_virtue = expiry_time - time.time()
    await asyncio.sleep(patience_is_a_virtue)
    await manslaughter_session(client, author_id, expiry_time)
    return


async def manslaughter_session(client, account_id, kill_stamp):
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
    except:
        pass
        # 😳 they'll never know 😳


async def add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, bb_token=None, game="fn"):
    display_name = response["displayName"]

    entry = {
        "token": auth_token,
        "account_id": account_id,
        "vbucks": True,
        "account_name": f"{display_name}",
        'expiry': time.time() + client.config["auth_expire_time"],
        "day": None,
        "bb_token": bb_token,
        "bb_day": None
    }

    if add_entry:
        asyncio.get_event_loop().create_task(auto_stab_stab_session(client, ctx.author.id, entry['expiry']))
    profile = await profile_request(client, "query", entry, game=game)
    if game == "fn":
        vbucks = await asyncio.gather(asyncio.to_thread(vbucks_query_check, await profile.text()))
        others = await asyncio.gather(asyncio.to_thread(json_query_check, await profile.json()))
        if others[0] is not None:
            entry["day"] = others[0]
        if not vbucks[0]:
            entry["vbucks"] = False
    if game == "bb":
        others = await asyncio.gather(asyncio.to_thread(bb_day_query_check, await profile.json()))
        if others[0] is not None:
            entry["bb_day"] = others[0] - 1

    if add_entry:
        client.temp_auth[ctx.author.id] = entry

    return entry


def json_query_check(profile_text):
    try:
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["daily_rewards"]["totalDaysLoggedIn"]
    except:
        return None


def bb_day_query_check(profile_text):
    try:
        # ROOT.profileChanges[0].profile.stats.attributes.login_reward.next_level
        return profile_text["profileChanges"][0]["profile"]["stats"]["attributes"]["login_reward"]["next_level"]
    except:
        return None


# method to extract desired item from items
def extract_item(profile_json, item_string="Currency:Mtx"):
    found_items = {}
    num = 0
    try:
        for attribute, value in profile_json["profileChanges"][0]["profile"]["items"].items():
            if item_string in value["templateId"]:
                found_items.update({num: value})
                num += 1
    except:
        pass
    return found_items


# method to get stw news from epic
async def get_stw_news(client):
    endpoint = client.config["endpoints"]["stw_news"]
    return await client.stw_session.get(endpoint)


# method to get br news from fortnite-api
async def get_br_news(client):
    endpoint = client.config["endpoints"]["br_news"]
    return await client.stw_session.get(endpoint)


# news page embed
async def create_news_page(self, ctx, news_json, current, total):
    generic = self.client.colours["generic_blue"]
    embed = discord.Embed(title=await add_emoji_title(self.client, "News", "bang"),
                          description=f"\u200b\n**News page {current} of {total}:**\u200b\n"
                                      f"**{news_json[current - 1]['title']}**"
                                      f"\n{news_json[current - 1]['body']}",
                          colour=generic)

    embed.description += "\u200b\n\u200b"

    # set embed image
    embed = await set_embed_image(embed, news_json[current - 1]["image"])
    embed = await set_thumbnail(self.client, embed, "newspaper")
    embed = await add_requested_footer(ctx, embed)
    return embed


async def set_embed_image(embed, image_url):
    return embed.set_image(url=image_url)


# method to resolve internal name -> user-friendly name + emoji
async def resolve_vbuck_source(vbuck_source):
    if vbuck_source == "Currency:MtxGiveaway":
        return "Battle Pass", "bp_icon2"
    elif vbuck_source == "Currency:MtxComplimentary":
        return "Save the World", "library_cal"
    elif vbuck_source == "Currency:MtxPurchased":
        return "Purchased", "vbuck_icon"
    # idk the casing for this
    elif vbuck_source.lower() == "currency:mtxpurchasebonus":
        return "Purchase Bonus", "vbuck_icon"
    elif vbuck_source == "Currency:MtxDebt":
        return "Debt", "LMAO"
    else:
        return vbuck_source, "placeholder"


# method to calculate total vbucks from a list of items
async def calculate_vbucks(items):
    vbucks = 0
    if items:
        for item in items:
            for attr, val in item.items():
                if "debt" in val["templateId"].lower():
                    vbucks -= val["quantity"]
                else:
                    vbucks += val["quantity"]
    return vbucks


# alexanda  now who is she
async def get_or_create_auth_session(client, ctx, command, original_auth_code, slash, add_entry=False, processing=True,
                                     epic_auth_client="PC", game="fn"):  # hi bye
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
    """

    # extract auth code from auth_code
    extracted_auth_code = await extract_auth_code(original_auth_code)
    embeds = []

    # Attempt to retrieve the existing auth code.
    try:
        if game == "bb":
            existing_auth = client.temp_auth[ctx.author.id]["bb_token"]
        else:
            existing_auth = client.temp_auth[ctx.author.id]["token"]
    except:
        existing_auth = None

    # Return auth code if it exists
    if existing_auth is not None and extracted_auth_code == "":

        # Send the logging in & processing if given
        if processing:
            proc_embed = await processing_embed(client, ctx)
            return [await slash_send_embed(ctx, slash, proc_embed),
                    existing_auth,
                    embeds]

        return [None, existing_auth, embeds]

    error_colour = client.colours["error_red"]
    white_colour = client.colours["auth_white"]
    error_embed = None
    support_url = client.config["support_url"]
    if game == "bb":
        clientId = "3cf78cd3b00b439a8755a878b160c7ad"
    else:
        clientId = "ec684b8c687f479fadea3cb2ad83f5c6"

    # Basic checks so that we don't stab stab epic games so much
    if extracted_auth_code == "":
        error_embed = discord.Embed(title=await add_emoji_title(client, f"No Auth Code", "error"), description=f"""\u200b\n**You need an auth code, you can get one from:**
          [Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D{clientId}%2526responseType%253Dcode)
          [Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId={clientId}&responseType=code)\n
            **Need Help? Run**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""", colour=error_colour)

    elif extracted_auth_code in client.config["known_auth_codes"]:
        error_embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to authenticate with authcode:
            ```{extracted_auth_code}```
            **This authcode is from the URL & not from the body of the page:**
            ⦾ The authcode you need is the one from the pages body, not the one from the url.
            \u200b
            If you need a new authcode you can get one by:
            [Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={clientId}&responseType=code)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif extracted_auth_code == "errors.stwdaily.illegal_auth_code" or (re.sub('[ -~]', '', extracted_auth_code)) != "":
        error_embed = discord.Embed(title=await add_emoji_title(client, ranerror(client), "error"), description=f"""\u200b
        Attempted to authenticate with authcode:
        ```{original_auth_code}```
        Your auth code contains characters not present in auth codes. Please try copying your code again, or getting a new one\n
        **An Example:**
        ```a51c1f4d35b1457c8e34a1f6026faa35```
        If you need a new authcode you can get one by:
        [Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={clientId}&responseType=code)
        \u200b
        **If you need any help try:**
        {await mention_string(client, f"help {command}")}
        Or [Join the support server]({support_url})
        Note: You need a new code __every time you authenticate__\n\u200b""",
                                    colour=error_colour)

    elif len(extracted_auth_code) != 32:
        error_embed = discord.Embed(title=await add_emoji_title(client, ranerror(client), "error"), description=f"""\u200b
        Attempted to authenticate with authcode:
        ```{extracted_auth_code}```
        Your authcode should only be 32 characters long, and only contain numbers and letters. Check if you have any stray quotation marks\n
        **An Example:**
        ```a51c1f4d35b1457c8e34a1f6026faa35```
        If you need a new authcode you can get one by:
        [Refreshing the page to get a new code or by clicking here](https://www.epicgames.com/id/api/redirect?clientId={clientId}&responseType=code)
        \u200b
        **If you need any help try:**
        {await mention_string(client, f"help {command}")}
        Or [Join the support server]({support_url})
        Note: You need a new code __every time you authenticate__\n\u200b""",
                                    colour=error_colour)

    if error_embed is not None:
        embed = await set_thumbnail(client, error_embed, "error")
        embed = await add_requested_footer(ctx, embed)
        await slash_send_embed(ctx, slash, embed)
        return [False]

    proc_embed = await processing_embed(client, ctx)
    message = await slash_send_embed(ctx, slash, proc_embed)

    token_req = await get_token(client, extracted_auth_code, game)
    response = await token_req.json()
    success, auth_token, account_id = await check_for_auth_errors(client, response, ctx, message, command,
                                                                  extracted_auth_code,
                                                                  slash, support_url)

    if not success:
        return [False]

    # if authing for battle breakers
    if game == "bb":
        # if session already exists
        try:
            # if existing fn session exists
            if client.temp_auth[ctx.author.id]["token"] is not None:
                entry = await add_temp_entry(client, ctx, client.temp_auth[ctx.author.id]["token"],
                                             account_id, response, add_entry, bb_token=auth_token, game=game)
            # no fn session, set fn token to none
            else:
                entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
                                             game=game)
        # no session at all
        except:
            entry = await add_temp_entry(client, ctx, None, account_id, response, add_entry, bb_token=auth_token,
                                         game=game)
    # if authing for fn
    else:
        # if session already exists
        try:
            # if existing bb session exists
            if client.temp_auth[ctx.author.id]["bb_token"] is not None:
                entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry,
                                             bb_token=client.temp_auth[ctx.author.id]["bb_token"], game=game)
            # no bb session, set bb token to None
            else:
                entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)
        # no session at all (most common outcome of all this junk 🫠)
        except:
            entry = await add_temp_entry(client, ctx, auth_token, account_id, response, add_entry, game=game)

    embed = discord.Embed(title=await add_emoji_title(client, "Successfully Authenticated", "whitekey"),
                          description=f"""```Welcome, {entry['account_name']}```
    """, colour=white_colour)

    if add_entry:
        embed.description += f"{client.config['emojis']['stopwatch_anim']} Your session will expire <t:{math.floor(client.config['auth_expire_time'] + time.time())}:R>\n\u200b\n"
    else:
        embed.description += f"{client.config['emojis']['cross']} Did not start an auth session\n\u200b\n"

    if not entry['vbucks']:
        embed.description += f"""⦾ You cannot receive {client.config['emojis']['vbucks']} V-Bucks from claiming daily rewards only {client.config['emojis']['xray']} X-Ray tickets.\n\u200b"""

    embed = await set_thumbnail(client, embed, "keycard")
    embed = await add_requested_footer(ctx, embed)

    embeds.append(embed)
    return [message, entry, embeds]


async def post_error_possibilities(ctx, client, command, acc_name, error_code, support_url, error_level="error",
                                   response=None):
    error_colour = client.colours["error_red"]
    yellow = client.colours["warning_yellow"]

    # Epic Games Error Codes
    if error_code == "errors.com.epicgames.common.missing_action":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to claim daily because:**
            ⦾ Your account has not yet opened Fortnite before
            ⦾ Your account has been banned and therefore you cannot claim your daily rewards.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.fortnite.check_access_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to claim daily because this account does not own Fortnite: Save The World:**
            ⦾ You need STW to claim your any rewards, Note: you can only get V-Bucks if you own a __Founders Pack__ which is no longer available.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.common.authentication.token_verification_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to claim daily because your token has expired**
            ⦾ Please reauthenticate your account, you can get an auth code from:

            [Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)
            [Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )
    elif error_code == "errors.com.epicgames.validation.validation_failed":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Uh oh! Ran into an error with STW Daily or Epic Games**
            ⦾ Validation for a request has failed
            ⦾ Please ask for support in the support server about this.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )
    # battle breakers error codes
    elif error_code == "errors.com.epicgames.world_explorers.login_reward_not_available":
        reward = get_bb_reward_data(client, response, True)
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "warning"), description=
            f"""\u200b
                        You have already claimed your reward for day **{reward[0]}**.
                        \u200b
                        **{reward[1]} Todays reward was:**
                        ```{reward[2]}```
                        You can claim tomorrow's reward <t:{int(datetime.datetime.combine(datetime.datetime.utcnow() + datetime.timedelta(days=1), datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).timestamp())}:R>
                        \u200b
                        """, colour=yellow)
        error_level = "warn"

    # STW Daily Error Codes
    elif error_code == "errors.stwdaily.failed_guid_research":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to find GUID for research item**
            ⦾ Please ensure you have claimed research points at least once in-game

            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_get_collected_resource_item":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to get item from notifications using token_guid_research**
            ⦾ Please ensure you have claimed research points at least once in-game
            ⦾ If this continues please ask for support in the support server.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_get_collected_resource_type":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to get collectedResourceResult type from notifications**
            ⦾ Please ensure you have claimed research points at least once in-game
            ⦾ If this continues please ask for support in the support server.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.failed_total_points":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Failed to find total research points item from query profile**
            ⦾ You could be out of research points, please just wait a few seconds and re run the command.
            ⦾ Please ensure you have claimed research points at least once in-game
            ⦾ If this continues please ask for support in the support server.
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.not_author_interaction_response":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Not the author:```You need to be the author to utilise the {command} view!```
            **If you want to utilise this view, please use the command yourself.**

            NOTE: *This message is only sent one time, attempting to use buttons after receiving this will return with `` interaction failed ``*
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.homebase_long":
        # TODO: limit size
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
                Attempted to change Homebase name to:
                ```{acc_name}```
                **This name is too long.**
                ⦾ Homebase names must be under 16 characters
                ⦾ Homebase names also have additional criteria, to check them, try running {await mention_string(client, f"help {command}")}
                \u200b
                **If you need any help try:**
                {await mention_string(client, f"help {command}")}
                Or [Join the support server]({support_url})
                Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    elif error_code == "errors.stwdaily.homebase_illegal":
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
                Attempted to change Homebase name to:
                ```{acc_name}```
                **This name contains unacceptable characters.**
                ⦾ Homebase names must be alphanumeric, with limited support for extra characters.
                ⦾ Homebase names also have additional criteria, to check them, try running {await mention_string(client, f"help {command}")}
                \u200b
                **If you need any help try:**
                {await mention_string(client, f"help {command}")}
                Or [Join the support server]({support_url})
                Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    else:
        embed = discord.Embed(
            title=await add_emoji_title(client, ranerror(client), "error"),
            description=f"""\u200b
            Attempted to claim daily for account:
            ```{acc_name}```
            **Unknown error received from epic games:**
            ```{error_code}```
            
            You may have signed into the wrong account, try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)
            \u200b
            **If you need any help try:**
            {await mention_string(client, f"help {command}")}
            Or [Join the support server]({support_url})
            Note: You need a new code __every time you authenticate__\n\u200b""",
            colour=error_colour
        )

    embed = await set_thumbnail(client, embed, error_level)
    embed = await add_requested_footer(ctx, embed)
    return embed


async def strip_string(string):
    return re.sub("[^0-9a-zA-Z]+", "", string)


def create_command_dict(client):
    command_name_dict = {}
    command_dict = {}

    # Gets aliases and adds them to commmand_name_dict so we can match for aliases too in the command arg
    for command in client.commands:
        command_name_dict[command.name] = command.name
        for alias in command.aliases:
            command_name_dict[alias] = command.name

        # Adds the command to the 
        command_dict[command.name] = command

    return command_name_dict, command_dict, list(command_name_dict)


# regex for 32 character hex
async def extract_auth_code(string):
    try:
        return re.search(r"[0-9a-f]{32}", string)[0]

    except TypeError:
        if len(string) == 32:
            return "errors.stwdaily.illegal_auth_code"

        return string


# regex for under 16 character alphanumeric with extra allowed chars
async def is_legal_homebase_name(string):
    # TODO: add obfuscated filter for protected homebase names
    return re.match(r"^[0-9a-zA-Z '\-._~]{1,16}$", string)

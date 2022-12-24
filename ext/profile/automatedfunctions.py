"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for automatic functions :3
"""
import asyncio
import datetime
import random

import discord
import discord.ext.commands as ext
from discord.ext import tasks
from orjson import orjson

import stwutil as stw
from ext.profile.bongodb import get_autoclaim_user_cursor

claimed_account_ids = []


# a function to autoclaim daily rewards on epic games accounts
async def auto_authenticate(client, auth_entry):
    """
    A function called per account to claim the daily reward using provided auth info i guess

    Args:
        client: The client
        auth_entry: The auth entry

    Returns:
        True if successful, False if not
    """
    # TODO: with time, we can optimise / add more features to this function
    snowflake = auth_entry['user_snowflake']
    print(f"AUTO-AUTHENTICATING FOR USER: {snowflake}")

    for profile in auth_entry["profiles"]:
        current_profile = auth_entry["profiles"][profile]
        if current_profile["authentication"] is not None:
            auth_entry["global"]["selected_profile"] = profile

            auth_info_thread = await asyncio.gather(
                asyncio.to_thread(stw.decrypt_user_data, snowflake, current_profile["authentication"]))
            dev_auth_info = auth_info_thread[0]

            account_id = dev_auth_info["accountId"]
            if account_id not in claimed_account_ids:
                claimed_account_ids.append(account_id)
                await asyncio.sleep(random.randint(2, 10))
                print(f"DISPLAY NAME: {current_profile['authentication']['displayName']}")
                token_req = await stw.get_token_devauth(client, auth_entry, game="ios",
                                                        auth_info_thread=auth_info_thread)
                response = orjson.loads(await token_req.read())

                try:
                    access_token = response["access_token"]
                    # Simulate temp entry so we can do profile request stuff i guess lol
                    entry = {
                        "token": access_token,
                        "account_id": account_id,
                        "vbucks": True,
                        "account_name": "",
                        'expiry': "",
                        "day": None,
                        "bb_token": "",
                        "bb_day": None,
                        "games": "",
                    }
                    await asyncio.sleep(random.randint(2, 10))
                    request = await stw.profile_request(client, "daily", entry)
                    json_response = orjson.loads(await request.read())
                    try:
                        error_code = json_response["errorCode"]
                        print(f"FAILED TO CLAIM DAILY FOR PROFILE {profile} ERROR: {error_code}")
                    except:
                        print(
                            f"SUCCESSFULLY CLAIMED DAILY FOR PROFILE {profile} ON DAY {json_response['notifications'][0]['daysLoggedIn']}")
                except Exception as E:
                    print(f"FAILED TO AUTHENTICATE FOR PROFILE {profile} EPIC REQUEST: {response} PYTHON ERROR: {E}")


async def get_auto_claim(client):
    """
    A function to get the auto claim cursor

    Args:
        client: The client
    """
    user_cursor = await get_autoclaim_user_cursor(client)

    async for user in user_cursor:
        await auto_authenticate(client, user)

    claimed_account_ids.clear()


class AutoFunction(ext.Cog):
    """
    Cog for the Reminder task
    """

    def __init__(self, client):
        self.client = client
        self.autoclaim_task.start()  # hi

    @tasks.loop(time=datetime.time(0, 0, random.randint(11, 39), tzinfo=datetime.timezone.utc))
    async def autoclaim_task(self):
        """
        The autoclaim task
        """
        await get_auto_claim(self.client)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(AutoFunction(client))

"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for automatic functions :3
"""
import asyncio
import datetime
import random
import logging

import discord
import discord.ext.commands as ext
from discord.ext import tasks
from orjson import orjson

import stwutil as stw
from ext.profile.bongodb import get_autoclaim_user_cursor, replace_user_document

claimed_account_ids = []
logger = logging.getLogger(__name__)


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
    current_selected_profile = auth_entry["global"]["selected_profile"]
    logger.info(f"Auto authenticating for: {snowflake}")

    for profile in auth_entry["profiles"]:
        current_profile = auth_entry["profiles"][profile]
        if current_profile["authentication"] is not None:
            auth_entry["global"]["selected_profile"] = profile

            try:
                if auth_entry["profiles"][profile]["authentication"]["hasExpired"]:
                    continue
            except:
                pass

            auth_info_thread = await asyncio.gather(
                asyncio.to_thread(stw.decrypt_user_data, snowflake, current_profile["authentication"]))
            dev_auth_info = auth_info_thread[0]

            account_id = dev_auth_info["accountId"]
            if account_id not in claimed_account_ids:
                claimed_account_ids.append(account_id)
                await asyncio.sleep(random.randint(2, 10))
                logger.info(f"Display name: {current_profile['authentication']['displayName']}")
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
                        logger.warning(f"Failed to autoclaim for profile {profile}! Error: {error_code}")
                    except:
                        logger.info(
                            f"Success for profile {profile} on day {json_response['notifications'][0]['daysLoggedIn']}")
                except Exception as E:
                    try:
                        if response["errorCode"] == "errors.com.epicgames.account.invalid_account_credentials":
                            if len(auth_entry["profiles"]) <= 1:
                                auth_entry["auto_claim"] = None
                            auth_entry["profiles"][profile]["authentication"]["hasExpired"] = True
                            auth_entry["global"]["selected_profile"] = current_selected_profile
                            await replace_user_document(client, auth_entry)
                            logger.warning(f"Auto-Claim authentication expired for profile {profile}")
                    except:
                        pass
                    logger.warning(f"Failed to authenticate for profile {profile}: Epic: {response} | Python: {E}")


async def get_auto_claim(client):
    """
    A function to get the auto claim cursor

    Args:
        client: The client
    """
    user_cursor = await get_autoclaim_user_cursor(client)

    async for user in user_cursor:
        try:
            await auto_authenticate(client, user)
        except Exception as e:
            logger.error(f"Auto-Claim authentication error: {e}")
            pass
    try:
        await user_cursor.close()
    except:
        pass
    claimed_accs = len(claimed_account_ids)
    claimed_account_ids.clear()
    return claimed_accs


class AutoFunction(ext.Cog):
    """
    Cog for the Reminder task
    """

    def __init__(self, client):
        self.client = client
        # self.autoclaim_task.start()  # hi

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

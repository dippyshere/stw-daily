"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file checks ~~something~~ EVERYTHING! you really should know :3
This file validates inputs for the settings command
"""

# ---- CHECK FUNCTIONS ----


def check_upcoming_display_days(client, ctx, value):
    """
    Checks if the value is a valid number of days to display upcoming events for.

    Args:
        client (discord.ext.commands.Bot): The bot client. (unused)
        ctx: The context of the command. (unused)
        value: The value to check.

    Returns:
        bool: True if the value is valid, False otherwise.
    """
    try:
        integer_value = int(value)
        if 51 > integer_value > 0:
            return integer_value
        else:
            return False
    except:
        return False


boolean_string_representation = {'true': True, 't': True, '1': True,
                                 'false': False, 'f': False, '0': False}


def check_bool(client, ctx, value):
    """
    Checks if the value is a valid boolean.

    Args:
        client: The bot client. (unused)
        ctx: The context of the command. (unused)
        value: The value to check.

    Returns:
        bool: True if the value is valid, False otherwise.
    """
    try:
        # what is this??????
        boolean_string_representation[value]
        return True
    except:
        return False


def check_localisation(client, ctx, value):
    """
    Checks if the value is a valid localisation.

    Args:
        client: The bot client.
        ctx: The context of the command. (unused)
        value: The value to check.

    Returns:
        bool: True if the value is valid, False otherwise.
    """
    if value.lower() in client.localisation:
        return client.localisation[value.lower()]
    else:
        return False


def sex_check(client, ctx, value):
    """
    Checks sex i guess

    Args:
        client: The bot client. (unused)
        ctx: The context of the command. (unused)
        value: The value to check.

    Returns:
        bool: True if the value is valid, False otherwise.
    """
    try:
        return str(value)
    except:
        return False

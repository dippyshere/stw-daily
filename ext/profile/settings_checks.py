"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file checks ~~something~~ EVERYTHING! you really should know :3
This file validates inputs for the settings command
"""
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


# ---- CHECK FUNCTIONS ----


def check_upcoming_display_days(client, ctx, value) -> tuple[bool | int, bool]:
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
        if 60 >= integer_value >= 0:
            return integer_value, True
        else:
            return False, False
    except:
        return False, False


boolean_string_representation = {'true': True, 't': True, '1': True, 'yes': True, 'y': True, 'on': True, 'enable': True, 'enabled': True, 'o': True, 'active': True, 'all': True, '✅': True, '☑️': True, '✔️': True, 'ye': True, 'yeah': True,
                                 'false': False, 'f': False, '0': False, 'no': False, 'n': False, 'off': False, 'disable': False, 'disabled': False, 'x': False, 'inactive': False, 'none': False, '✖️': False, '❌': False, '❎': False, 'na': True, 'nah': False}


def check_bool(client, ctx, value) -> tuple[bool, bool]:
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
        boolean_string_representation[value.lower()]
        return True, True
    except:
        return False, False


def check_localisation(client, ctx, value) -> tuple[bool | str, bool]:
    """
    Checks if the value is a valid localisation.

    Args:
        client: The bot client.
        ctx: The context of the command. (unused)
        value: The value to check.

    Returns:
        bool: True if the value is valid, False otherwise.
    """
    if value.lower() == "auto":
        return "auto", True
    if value.lower() in client.localisation:
        logger.debug(f"Localisation check: {value.lower()} -> {value.lower()} (1.0)")
        return client.localisation[value.lower()], True
    else:
        for attempt in [" ", "-", "_", ".", ",", ";", ":", "/", "\\", "|", "!", "?", "@", "#", "$", "%", "^", "&", "*", "(", ")", "[", "]", "{", "}", "<", ">", "`", "~", "+", "=", "’", "‘", "“", "”", "—", "–", "…", "•", "°", "²", "³", "¹", "⁰", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹", "₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉", "₊", "₋", "₌", "₍", "₎", "ₐ", "ₑ", "ₒ", "ₓ", "ₔ", "ₕ", "ₖ", "ₗ", "ₘ", "ₙ", "ₚ", "ₛ", "ₜ"]:
            for i in value.lower().split(attempt):
                if i in client.localisation:
                    logger.debug(f"Localisation check: {value.lower()} -> {i} (1.0) [attempt: {attempt}]")
                    return client.localisation[i], True
        outcome = max(client.localisation, key=lambda x: SequenceMatcher(None, x, value.lower()).ratio())
        similarity = SequenceMatcher(None, outcome, value.lower()).ratio()
        logger.debug(f"Localisation check: {value.lower()} -> {outcome} ({similarity})")
        if similarity > 0.5:
            return client.localisation[outcome], True
        return False, False


def check_default(client, ctx, value) -> tuple[bool, bool]:
    """
    Always returns true.

    Args:
        client: The bot client. (unused)
        ctx: The context of the command. (unused)
        value: The value to check. (unused)

    Returns:
        bool: True.
    """
    return True, True


def check_keycard(client, ctx, value) -> tuple[bool, bool]:
    """
    Always returns true.

    Args:
        client: The bot client. (unused)
        ctx: The context of the command. (unused)
        value: The value to check. (unused)

    Returns:
        bool: True.
    """
    if value.lower() in ['donut_keycard', 'hightower_date_keycard', 'mountainbase_keycard', 'junkyard_keycard',
                         'alter_keycard', 'hightower_tomato_keycard', 'ego_keycard', 'island_keycard', 'oilrig_keycard',
                         'sleek_keycard']:
        return value.lower(), True
    return False, False

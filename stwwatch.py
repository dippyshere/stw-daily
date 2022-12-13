"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file watches for changes in the ext folder and reloads the cogs if they are changed.
"""
import asyncio
import pathlib

from watchfiles import awatch

changed = set(())


def stw_extension_changed(changes):
    """
    This function is called when a change is detected in the ext folder.

    Args:
        changes: The changes detected.
    """
    changed_files = []

    for file_change in changes:

        # 2 is modified
        if file_change[0] == 2:
            if file_change[1][-3:] == ".py":
                path = file_change[1].split("./ext")[1][:-3].replace("\\", ".")
                changed_files.append(f"ext{path}")

    changed.update(changed_files)


async def watch_stw_extensions():
    """
    This function watches for changes in the ext folder.

    Ah... free at last. O Gabriel... now dawns thy reckoning, and thy gore shall glisten before the temples of man! Creature of steel, my gratitude upon thee for my freedom. But the crimes thy kind have committed against humanity are not forgotten! And thy punishment... is death!
    """

    async for changes in awatch('./ext'):
        stw_extension_changed(changes)

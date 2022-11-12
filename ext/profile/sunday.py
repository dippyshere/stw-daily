# it doesnt matter if its sunday

import asyncio
import json
import os
import discord
import discord.ext.commands as ext
from discord import Option, slash_command

import stwutil as stw

# did u install motor no :) :( :c oh lmao sorry racism
# access monogodb async

import motor.motor_asyncio

from ext.profile.bongodb import get_user_document




# cog for the profile related settings & Disclosure - You & Me (Flume Remix)
class ProfileSettings(ext.Cog):

    def __init__(self, client):
        self.client = client

    async def devauth_command(self, ctx, slash, authcode=None):
        await handle_dev_auth(self.client, ctx, slash, authcode)

    @ext.slash_command(name='settings',
                       description='Change or view the settings associated with your currently selected profile',
                       guild_ids=stw.guild_ids)
    async def slash_device(self, ctx: discord.ApplicationContext,
                            # i am unsure on the limits of like how many options you can select in one of those fancy slash command things so i am just going to leave it as like a text entry thing
                           profile: Option(str,
                                           "The name of the setting you wish to change as listed in this commands embed",
                                           autocomplete=)
                            ):
        await self.devauth_command(ctx, True, token)

    @ext.command(name='settings',
                 aliases=['boy'],
                 extras={'emoji': "pink_link", "args": {
                     'setting': 'The setting you wish to change',
                     'value': 'The new value for the setting you wish to change',
                     'profile': 'The profile which to switch to so these new changes are applied to that profile, else just uses the current selected profile (Optional)'}},
                 brief="Change or view the settings associated with your currently selected profile",
                 description="""
                 [ REDACTED ] please write this for me someone i dont even have the motivation to work on this stupid settings stuff how am i meant to describe the garbage i am about to birth
                \u200b
                """)
    async def device(self, ctx, setting=None, value=None, profile=None):
        await self.settings_command(ctx, False, setting, value, profile)


def setup(client):
    client.add_cog(ProfileSettings(client))

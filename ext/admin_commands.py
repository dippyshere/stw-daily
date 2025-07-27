"""
STW Daily Discord bot Copyright 2021-2025 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the reload command. It is used to reload and load cogs for development.
"""

import asyncio
import logging

import discord
import discord.ext.commands as ext
from ext.profile.automatedfunctions import get_auto_claim, auto_authenticate
from ext.profile.bongodb import get_user_document, replace_user_document, get_accounts_with_auth_data_cursor, \
    get_all_users_cursor, insert_default_document

import stwutil as stw

logger = logging.getLogger(__name__)


class ForceAutoClaim(ext.Cog):
    """
    Forces all account autoclaims to run
    """

    def __init__(self, client):
        self.client = client

    async def manual_auto_command(self, ctx, snowflake):
        """
        The main function for the manual autoclaim command.

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to force auto claim for.
        """
        if ctx.author.id in self.client.config["devs"]:
            try:
                user_document = await stw.get_user_document(ctx, self.client, ctx.author.id)
                currently_selected_profile_id = user_document["global"]["selected_profile"]
                keycard = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["keycard"]
            except:
                keycard = "keycard"
            try:
                embed_colour = self.client.colours["auth_white"]
                if snowflake is not None:
                    snowflake = int(snowflake)
                    claimed_accs = 0
                    user_profile = await get_user_document(ctx, self.client, snowflake)
                    if user_profile is not None:
                        for profile in user_profile["profiles"]:
                            if user_profile["profiles"][profile]["authentication"] is not None:
                                claimed_accs += 1
                        proc_msg = await stw.slash_send_embed(ctx, self.client,
                                                              await stw.processing_embed(self.client, ctx, "en",
                                                                                         "Auto-claiming...",
                                                                                         f"Please wait, we have "
                                                                                         f"{claimed_accs} accounts"
                                                                                         f" to claim for."))
                        await auto_authenticate(self.client, user_profile)
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Forced Auto Claim",
                                                                          "experimental"),
                                          description=f'\u200b\nAuto-claimed {claimed_accs} accounts '
                                                      f'for <@{snowflake}>\n\u200b',
                                          color=embed_colour)
                else:
                    proc_msg = await stw.slash_send_embed(ctx, self.client, await stw.processing_embed(self.client, ctx,
                                                                                                       "en",
                                                                                                       "Auto-claiming...",
                                                                                                       f"Please wait, we have "
                                                                                                       f"many accounts"
                                                                                                       f" to claim for."))
                    claimed_accs = await get_auto_claim(self.client)
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Forced Auto Claim",
                                                                          "experimental"),
                                          description=f'\u200b\nAuto-claimed for {claimed_accs} accounts\n\u200b',
                                          color=embed_colour)
            except Exception as e:
                proc_msg = await stw.slash_send_embed(ctx, self.client,
                                                      await stw.processing_embed(self.client, ctx, "en",
                                                                                 "Auto-claiming..."))
                embed_colour = self.client.colours["error_red"]
                embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Forced Auto Claim", "experimental"),
                                      description=f'\u200b\nFailed to run the auto-claim task\n\u200b',
                                      color=embed_colour)
                embed.add_field(name="Error:", value=f"```{e}```", inline=False)

            embed = await stw.set_thumbnail(self.client, embed, keycard)
            embed = await stw.add_requested_footer(ctx, embed, "en")
            await asyncio.sleep(0.25)
            await stw.slash_edit_original(ctx, proc_msg, embed)

    @ext.command(name='forceautoclaim',
                 extras={'emoji': "experimental", "args": {'snowflake': 'The discord user id to force autoclaim on'},
                         "dev": True},
                 brief="Runs the autoclaim task manually",
                 description="Run autoclaim right now for registered accounts\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def forceauto(self, ctx, snowflake=None):
        """
        This function is the entry point for the forced autoclaim command when called traditionally

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to force autoclaim for.
        """
        await self.manual_auto_command(ctx, snowflake)


class ClearSavedAuths(ext.Cog):
    """
    Clears saved auths for all stw daily users, or only a certain user
    """

    def __init__(self, client):
        self.client = client

    async def clear_auths_command(self, ctx, snowflake):
        """
        The main function for the clear auth command.

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to clear autoclaim for.
        """
        if ctx.author.id in self.client.config["devs"]:
            try:
                user_document = await stw.get_user_document(ctx, self.client, ctx.author.id)
                currently_selected_profile_id = user_document["global"]["selected_profile"]
                keycard = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["keycard"]
            except:
                keycard = "keycard"
            try:
                embed_colour = self.client.colours["auth_white"]
                if snowflake is not None:
                    snowflake = int(snowflake)
                    user_profile = await get_user_document(ctx, self.client, snowflake)
                    if user_profile is not None:
                        for profile in user_profile["profiles"]:
                            if user_profile["profiles"][profile]["authentication"] is not None:
                                user_profile["profiles"][profile]["authentication"] = None
                        await replace_user_document(self.client, user_profile)
                        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Clear Saved Auths",
                                                                              "experimental"),
                                              description=f'\u200b\nSuccessfully cleared saved auths '
                                                          f'for <@{snowflake}>\n\u200b',
                                              color=embed_colour)
                    else:
                        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Clear Saved Auths",
                                                                              "experimental"),
                                              description=f'\u200b\nUser '
                                                          f'<@{snowflake}> doesn\'t exist!\n\u200b',
                                              color=embed_colour)
                else:
                    auth_data_cursor = await get_accounts_with_auth_data_cursor(self.client)
                    count = 0
                    async for user in auth_data_cursor:
                        try:
                            user_profile = await get_user_document(ctx, self.client, user["user_snowflake"],
                                                                   silent_error=True)
                            if user_profile is not None:
                                for profile in user_profile["profiles"]:
                                    if user_profile["profiles"][profile]["authentication"] is not None:
                                        user_profile["profiles"][profile]["authentication"] = None
                                await replace_user_document(self.client, user_profile)
                        except:
                            pass
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Clear Saved Auths",
                                                                          "experimental"),
                                          description=f'\u200b\nCleared {count:,} accounts\' auth data\n\u200b',
                                          color=embed_colour)
            except Exception as e:
                embed_colour = self.client.colours["error_red"]
                embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Clear Saved Auths", "experimental"),
                                      description=f'\u200b\nFailed to clear auths 😱\n\u200b',
                                      color=embed_colour)
                embed.add_field(name="Error:", value=f"```{e}```", inline=False)

            embed = await stw.set_thumbnail(self.client, embed, keycard)
            embed = await stw.add_requested_footer(ctx, embed, "en")
            await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='clearsavedauths',
                 extras={'emoji': "experimental", "args": {'snowflake': 'The discord user id to clear auth data'},
                         "dev": True},
                 brief="Clears all auth data for all users / a specific user",
                 description="Clear all auth data saved for all users, or just a specific user\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def clearauth(self, ctx, snowflake=None):
        """
        This function is the entry point for the delete auth data command when called traditionally

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to delete data for.
        """
        await self.clear_auths_command(ctx, snowflake)


class DisableAutoClaim(ext.Cog):
    """
    Disables autoclaim for everyone
    """

    def __init__(self, client):
        self.client = client

    async def disable_autoclaim_command(self, ctx, snowflake):
        """
        The main function for the disable autoclaim command.

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to disable autoclaim for.
        """
        if ctx.author.id in self.client.config["devs"]:
            try:
                user_document = await stw.get_user_document(ctx, self.client, ctx.author.id)
                currently_selected_profile_id = user_document["global"]["selected_profile"]
                keycard = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["keycard"]
            except:
                keycard = "keycard"
            try:
                embed_colour = self.client.colours["auth_white"]
                if snowflake is not None:
                    snowflake = int(snowflake)
                    user_profile = await get_user_document(ctx, self.client, snowflake)
                    if user_profile is not None:
                        user_profile["auto_claim"] = None
                        await replace_user_document(self.client, user_profile)
                        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Disable Auto Claim",
                                                                              "experimental"),
                                              description=f'\u200b\nSuccessfully disabled autoclaim '
                                                          f'for <@{snowflake}>\n\u200b',
                                              color=embed_colour)
                    else:
                        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Disable Auto Claim",
                                                                              "experimental"),
                                              description=f'\u200b\nUser '
                                                          f'<@{snowflake}> doesn\'t exist!\n\u200b',
                                              color=embed_colour)
                else:
                    auto_claim_cursor = await get_all_users_cursor(self.client)
                    count = 0
                    async for user in auto_claim_cursor:
                        try:
                            user_profile = await get_user_document(ctx, self.client, user["user_snowflake"],
                                                                   silent_error=True)
                            if user_profile is not None:
                                user_profile["auto_claim"] = None
                                count += 1
                                logger.warning(f"Disabled auto-claim for {user['user_snowflake']}")
                                await replace_user_document(self.client, user_profile)
                        except:
                            pass
                    try:
                        await auto_claim_cursor.close()
                    except:
                        pass
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Disable Auto Claim",
                                                                          "experimental"),
                                          description=f'\u200b\nDisabled Auto Claim on {count:,} accounts\n\u200b',
                                          color=embed_colour)
            except Exception as e:
                embed_colour = self.client.colours["error_red"]
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, "Disable Auto Claim", "experimental"),
                    description=f'\u200b\nFailed to disable Auto Claim 😱\n\u200b',
                    color=embed_colour)
                embed.add_field(name="Error:", value=f"```{e}```", inline=False)

            embed = await stw.set_thumbnail(self.client, embed, keycard)
            embed = await stw.add_requested_footer(ctx, embed, "en")
            await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='disableautoclaim',
                 extras={'emoji': "experimental", "args": {'snowflake': 'The discord user id to disable autoclaim for(Optional)'},
                         "dev": True},
                 brief="Disables auto-claim for all users / a specific user",
                 description="Disable auto-claim for all users, or just a specific user\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def disableclaimer(self, ctx, snowflake=None):
        """
        This function is the entry point for the disable autoclaim command when called traditionally

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to disable autoclaim for.
        """
        await self.disable_autoclaim_command(ctx, snowflake)


class EnableAutoClaim(ext.Cog):
    """
    Enables autoclaim for everyone
    """

    def __init__(self, client):
        self.client = client

    async def enable_autoclaim_command(self, ctx, snowflake):
        """
        The main function for the enable autoclaim command.

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to enable autoclaim for.
        """
        if ctx.author.id in self.client.config["devs"]:
            try:
                user_document = await stw.get_user_document(ctx, self.client, ctx.author.id)
                currently_selected_profile_id = user_document["global"]["selected_profile"]
                keycard = user_document["profiles"][str(currently_selected_profile_id)]["settings"]["keycard"]
            except:
                keycard = "keycard"
            try:
                embed_colour = self.client.colours["auth_white"]
                snowflake = int(snowflake)
                user_profile = await get_user_document(ctx, self.client, snowflake)
                if user_profile is not None:
                    user_profile["auto_claim"] = {
                        "enabled": True,
                    }
                    await replace_user_document(self.client, user_profile)
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Enable Auto Claim",
                                                                          "experimental"),
                                          description=f'\u200b\nSuccessfully enabled autoclaim '
                                                      f'for <@{snowflake}>\n\u200b',
                                          color=embed_colour)
                else:
                    embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Enable Auto Claim",
                                                                          "experimental"),
                                          description=f'\u200b\nUser '
                                                      f'<@{snowflake}> doesn\'t exist!\n\u200b',
                                          color=embed_colour)
            except Exception as e:
                embed_colour = self.client.colours["error_red"]
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, "Enable Auto Claim", "experimental"),
                    description=f'\u200b\nFailed to enable Auto Claim 😱\n\u200b',
                    color=embed_colour)
                embed.add_field(name="Error:", value=f"```{e}```", inline=False)

            embed = await stw.set_thumbnail(self.client, embed, keycard)
            embed = await stw.add_requested_footer(ctx, embed, "en")
            await stw.slash_send_embed(ctx, self.client, embed)

    @ext.command(name='enableautoclaim',
                 extras={'emoji': "experimental", "args": {'snowflake': 'The discord user id to enable autoclaim for'},
                         "dev": True},
                 brief="Enables auto-claim for a specific user",
                 description="Enable auto-claim for a specific user\n"
                             "⦾ Please note that this command is for development purposes only"
                             " <:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def enableclaimer(self, ctx, snowflake):
        """
        This function is the entry point for the enable autoclaim command when called traditionally

        Args:
            ctx: The context of the command.
            snowflake: The snowflake of the user to enable autoclaim for.
        """
        await self.enable_autoclaim_command(ctx, snowflake)


class ProfileAdminCommands(ext.Cog):
    """
    Admin commands for profiles
    """

    def __init__(self, client):
        self.client = client

    @ext.command(name='pprint',
                 extras={'emoji': "junkyard_keycard", "args": {'kitty': 'cat (Optional)'},
                         "dev": True},
                 brief="Prints your profile",
                 description="meow\n"
                             "i literally have no brain cells"
                             "<:TBannersIconsBeakerLrealesrganx4:1028513516589682748>")
    async def profileprint(self, ctx):
        """
        This function is the entry point for the print profile command

        Args:
            ctx: The context of the command.
        """
        await ctx.send(await get_user_document(ctx, self.client, ctx.author.id))


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(ForceAutoClaim(client))
    client.add_cog(ClearSavedAuths(client))
    client.add_cog(DisableAutoClaim(client))
    client.add_cog(ProfileAdminCommands(client))

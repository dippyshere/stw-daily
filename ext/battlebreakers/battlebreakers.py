"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the battle breakers daily reward command. claims battle breakers dailies

BATTLE BREAKERS!

WOAH-OH-OH, OOH-WOAH-OH OOH-WOAH-OH, OOH-WOAH-OH
Monsters from the sky, Want us all to die. Hiding underground, now they all must be found.
Break the crystals, set them free. Battle your way to victory.

BATTLE BREAKERS!

OH-WOAH-OH, OH-WOAH-OH
ctrl + shift + o what does that do :o
BATTLE BREAKERS!
:D"""

import asyncio
import orjson

import discord
import discord.ext.commands as ext
from discord import Option, OptionChoice

import stwutil as stw


# auth session for bb should we bother?
# eh ill try it later

class BattleBreakersDaily(ext.Cog):
    """
    Cog for the battle breaker daily command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def bbdaily_command(self, ctx):
        """
        The main function of the Battle Breakers Daily command

        Args:
            ctx: the context of the command

        Returns:
            None
        """
        embed = await stw.battle_breakers_deprecation(self.client, ctx, "BB Daily", "is")
        return await stw.slash_send_embed(ctx, embed)

        # succ_colour = self.client.colours["success_green"]
        #
        # auth_info = await stw.get_or_create_auth_session(self.client, ctx, "bbdaily", authcode, auth_opt_out, True)
        # if not auth_info[0]:
        #     return
        #
        # final_embeds = []
        #
        # ainfo3 = ""
        # try:
        #     ainfo3 = auth_info[3]
        # except:
        #     pass
        #
        # # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        # if ainfo3 != "logged_in_processing" and auth_info[2] != []:
        #     final_embeds = auth_info[2]
        #
        # # ok now we have the authcode information stuff, so it's time to attempt to claim daily on the road
        # request = await stw.profile_request(self.client, "daily", auth_info[1], game="bb")
        # json_response = orjson.loads(await request.read())
        #
        # # check for le error code
        # try:
        #     error_code = json_response["errorCode"]
        #     support_url = self.client.config["support_url"]
        #     acc_name = auth_info[1]["account_name"]
        #     # TODO: determine what happens here after 30th December 2022
        #     # Answer: WEX 504 gateway timeout
        #     embed = await stw.post_error_possibilities(ctx, self.client, "bbdaily", acc_name, error_code, support_url,
        #                                                response=json_response)
        #     final_embeds.append(embed)
        #     await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        # except KeyError:
        #     day = await asyncio.gather(asyncio.to_thread(stw.bb_day_query_check, json_response))
        #
        #     try:
        #         self.client.temp_auth[ctx.author.id]["bb_day"] = day[0]
        #     except KeyError:
        #         pass
        #
        #     if ctx.channel.id != 762864224334381077:
        #         dumb_useless_crap, name, emoji_text, description, amount = stw.get_bb_reward_data(self.client,
        #                                                                                           json_response,
        #                                                                                           pre_calc_day=day[0])
        #         # already claimed is handled in error since wex does that
        #
        #         # Initialise the claimed embed
        #         embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
        #                               description="\u200b",
        #                               colour=succ_colour)
        #
        #         embed.add_field(name=f'{emoji_text} On day **{day[0]}**, you received:', value=f"```{amount} {name}```",
        #                         inline=True)
        #     else:
        #         embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
        #                               description=f"\u200b\n<:Check:812201301843902474> "
        #                                           f"Successfully claimed daily reward"
        #                                           f"\n\u200b\n{self.emojis['check_mark']} **Please claim in "
        #                                           f"<#757768833946877992> for more detail** "
        #                                           f"\n\u200b",
        #                               colour=succ_colour)
        #     if ctx.channel.id != 762864224334381077:
        #         rewards = ''
        #         for i in range(1, 8):
        #             data = stw.get_bb_reward_data(self.client, pre_calc_day=day[0] + i)
        #             rewards += str(data[4]) + " " + str(data[1])
        #             if not (i + 1 == 8):
        #                 rewards += ', '
        #             else:
        #                 rewards += '.'
        #
        #         calendar = self.client.config["emojis"]["calendar"]
        #         embed.add_field(name=f'\u200b\n{calendar} Rewards for the next 7 days:', value=f'```{rewards}```\u200b',
        #                         inline=False)
        #     embed = await stw.set_thumbnail(self.client, embed, "check")
        #
        #     embed = await stw.add_requested_footer(ctx, embed)
        #     final_embeds.append(embed)
        #     await stw.slash_edit_original(ctx, auth_info[0], final_embeds)
        #     return

    # Battle Breakers is a new tactical role-playing game developed by Epic Games for mobile and PC.
    @ext.command(name='bbdaily',
                 aliases=['bbd', 'battlebreakersdaily', 'wex', 'bd', 'bb', 'bbbd', 'bbdd', 'bdb', 'vbd', 'gbd', 'hbd',
                          'nbd', 'bvd', 'bgd', 'bhd', 'bnd', 'bbs', 'bbe', 'bbf', 'bbc', 'bbx', 'vbbd', 'bvbd', 'gbbd',
                          'bgbd', 'hbbd', 'bhbd', 'nbbd', 'bnbd', 'bbvd', 'bbgd', 'bbhd', 'bbnd', 'bbsd', 'bbds',
                          'bbed', 'bbde', 'bbrd', 'bbdr', 'bbfd', 'bbdf', 'bbcd', 'bbdc', 'bbxd', 'bbdx', 'bdaily',
                          'bbaily', 'bbdily', 'bbdaly', 'bbdaiy', 'bbdail', 'bbbdaily', 'bbddaily', 'bbdaaily',
                          'bbdaiily', 'bbdailly', 'bbdailyy', 'bdbaily', 'bbadily', 'bbdialy', 'bbdaliy', 'bbdaiyl',
                          'vbdaily', 'gbdaily', 'hbdaily', 'nbdaily', 'bvdaily', 'bgdaily', 'bhdaily', 'bndaily',
                          'bbsaily', 'bbeaily', 'bbraily', 'bbfaily', 'bbcaily', 'bbxaily', 'bbdqily', 'bbdwily',
                          'bbdsily', 'bbdxily', 'bbdzily', 'bbdauly', 'bbda8ly', 'bbda9ly', 'bbdaoly', 'bbdally',
                          'bbdakly', 'bbdajly', 'bbdaiky', 'bbdaioy', 'bbdaipy', 'bbdailt', 'bbdail6', 'bbdail7',
                          'bbdailu', 'bbdailj', 'bbdailh', 'bbdailg', 'vbbdaily', 'bvbdaily', 'gbbdaily', 'bgbdaily',
                          'hbbdaily', 'bhbdaily', 'nbbdaily', 'bnbdaily', 'bbvdaily', 'bbgdaily', 'bbhdaily',
                          'bbndaily', 'bbsdaily', 'bbdsaily', 'bbedaily', 'bbdeaily', 'bbrdaily', 'bbdraily',
                          'bbfdaily', 'bbdfaily', 'bbcdaily', 'bbdcaily', 'bbxdaily', 'bbdxaily', 'bbdqaily',
                          'bbdaqily', 'bbdwaily', 'bbdawily', 'bbdasily', 'bbdaxily', 'bbdzaily', 'bbdazily',
                          'bbdauily', 'bbdaiuly', 'bbda8ily', 'bbdai8ly', 'bbda9ily', 'bbdai9ly', 'bbdaoily',
                          'bbdaioly', 'bbdalily', 'bbdakily', 'bbdaikly', 'bbdajily', 'bbdaijly', 'bbdailky',
                          'bbdailoy', 'bbdaiply', 'bbdailpy', 'bbdailty', 'bbdailyt', 'bbdail6y', 'bbdaily6',
                          'bbdail7y', 'bbdaily7', 'bbdailuy', 'bbdailyu', 'bbdailjy', 'bbdailyj', 'bbdailhy',
                          'bbdailyh', 'bbdailgy', 'bbdailyg', '/bbd', 'battlebreakers', '/battlebreakers', '/wex',
                          '/bd', '/bbdaily'],
                 extras={'emoji': "T_MTX_Gem_Icon", "args": {
                     'authcode': 'Your Epic Games authcode. Required unless you have an active session. (Optional)',
                     'opt-out': 'Any text given will opt you out of starting an authentication session (Optional)'},
                         "dev": True},
                 brief="Claim your Battle Breakers daily reward (authentication required)",
                 description=(
                         f"This command allowed you to claim your Battle Breakers daily rewards\n"
                         f"\u200b\nAs of <t:1672425127:R>, this command is no longer available, as Battle "
                         "Breakers has been shut down. 💔\nIf you'd like to continue playing Battle Breakers from your "
                         "profile dump, or just want to play it again, check out "
                         "https://github.com/dippyshere/battle-breakers-private-server.\n\u200b\n"
                         f"⦾ Looking for Fortnite daily rewards? Check out the `daily` command.\n"))
    async def bbdaily(self, ctx):
        """
        This function is the entry point for the bbdaily command when called traditionally

        Args:
            ctx: the context of the command
        """

        await self.bbdaily_command(ctx)

    # @ext.slash_command(name='bbdaily', name_localizations=stw.I18n.construct_slash_dict("bbdaily.slash.name"),
    #                    description='Claim your Battle Breakers daily reward',
    #                    description_localizations=stw.I18n.construct_slash_dict("bbdaily.slash.description"),
    #                    guild_ids=stw.guild_ids)
    # async def slashbbdaily(self, ctx: discord.ApplicationContext,
    #                        token: Option(
    #                            description="Your Epic Games authcode. Required unless you have an active session.",
    #                            description_localizations=stw.I18n.construct_slash_dict(
    #                                "generic.slash.token"),
    #                            name_localizations=stw.I18n.construct_slash_dict("generic.meta.args.token"),
    #                            min_length=32) = "",
    #                        auth_opt_out: Option(default="False",
    #                                             description="Opt out of starting an authentication session",
    #                                             description_localizations=stw.I18n.construct_slash_dict(
    #                                                 "generic.slash.optout"),
    #                                             name_localizations=stw.I18n.construct_slash_dict(
    #                                                 "generic.meta.args.optout"),
    #                                             choices=[OptionChoice("Do not start an authentication session", "True",
    #                                                                   stw.I18n.construct_slash_dict(
    #                                                                       "generic.slash.optout.true")),
    #                                                      OptionChoice("Start an authentication session (Default)",
    #                                                                   "False",
    #                                                                   stw.I18n.construct_slash_dict(
    #                                                                       "generic.slash.optout.false"))]) = "False"):
    #     """
    #     This function is the entry point for the bbdaily command when called via slash
    #
    #     Args:
    #         ctx: The context of the slash command
    #         token: The authcode of the user
    #         auth_opt_out: Whether the user wants to opt out of starting an authentication session
    #     """
    #     await self.bbdaily_command(ctx)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(BattleBreakersDaily(client))

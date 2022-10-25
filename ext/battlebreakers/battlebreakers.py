# BATTLE BREAKERS!
#
# WOAH-OH-OH, OOH-WOAH-OH OOH-WOAH-OH, OOH-WOAH-OH
# Monsters from the sky, Want us all to die. Hiding underground, now they all must be found.
# Break the crystals, set them free. Battle your way to victory.
#
# BATTLE BREAKERS!
#
# OH-WOAH-OH, OH-WOAH-OH
# ctrl + shift + o what does that do :o
# BATTLE BREAKERS!
# :D
import datetime

import discord
import discord.ext.commands as ext
from discord import Option
import asyncio

import stwutil as stw


# auth session for bb should we bother?
# eh ill try it later

# cog for the daily command.
class BattleBreakersDaily(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def bbdaily_command(self, ctx, slash, authcode, auth_opt_out):
        succ_colour = self.client.colours["success_green"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "bbdaily", authcode, slash, auth_opt_out,
                                                         True, game="bb")
        if not auth_info[0]:
            return

        final_embeds = []

        ainfo3 = ""
        try:
            ainfo3 = auth_info[3]
        except:
            pass

        # what is this black magic???????? I totally forgot what any of this is and how is there a third value to the auth_info??
        # okay I discovered what it is, it's basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # ok now we have the authcode information stuff, so it's time to attempt to claim daily on the road
        request = await stw.profile_request(self.client, "daily", auth_info[1], game="bb")
        json_response = await request.json()

        # check for le error code
        try:
            error_code = json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "bbdaily", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            day = await asyncio.gather(asyncio.to_thread(stw.bb_day_query_check, json_response))

            try:
                self.client.temp_auth[ctx.author.id]["bb_day"] = day[0]
            except:
                pass

            dumb_useless_crap, name, emoji_text, description, amount = stw.get_bb_reward_data(self.client, json_response, pre_calc_day=day)

            # already claimed is handled in error since wex does that

            # Initialise the claimed embed
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                                  description="\u200b",
                                  colour=succ_colour)

            embed.add_field(name=f'{emoji_text} On day **{day[0]}**, you received:', value=f"```{amount} {name}```",
                            inline=True)

            print('Successfully claimed battle breaker daily:')
            print(name)

            rewards = ''
            for i in range(1, 8):
                data = stw.get_bb_reward_data(self.client, pre_calc_day=day[0] + i)
                rewards += data[4] + " " + data[1]
                if not (i + 1 == 8):
                    rewards += ', '
                else:
                    rewards += '.'

            calendar = self.client.config["emojis"]["calendar"]
            embed.add_field(name=f'\u200b\n{calendar} Rewards for the next 7 days:', value=f'```{rewards}```\u200b',
                            inline=False)
            embed = await stw.set_thumbnail(self.client, embed, "check")

            embed = await stw.add_requested_footer(ctx, embed)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

    @ext.slash_command(name='bbdaily',
                       description='Allows you to claim your Battle Breakers daily rewards (rip)',
                       guild_ids=stw.guild_ids)
    async def slashbbdaily(self, ctx: discord.ApplicationContext,
                           token: Option(str,
                                         "A Battle-Breakers auth code (different to a normal code)") = "",
                           auth_opt_out: Option(bool, "Opt Out of Authentication session") = False, ):
        await self.bbdaily_command(ctx, True, token, not auth_opt_out)

    # Battle Breakers is a new tactical role-playing game developed by Epic Games for mobile and PC.
    @ext.command(name='bbdaily',
                 aliases=['bb', 'bbd', 'battlebreakersdaily', 'wex', 'bd'],
                 extras={'emoji': "placeholder", "args": {
                     'authcode': 'The authcode to use (Optional)',
                     'opt-out': 'Any value entered into this field will opt you out of an authentication session (Optional)'}},
                 brief="Allows you to claim your Battle Breakers daily rewards (BB auth req.)",
                 description="""This command allows you to claim your Battle Breakers daily rewards, you must be authenticated to use this command.
                \u200b
                ⦾ You can check when you can claim your daily again by checking the bots status
                ⦾ This command requires getting an auth code from a different link, please use the ones provided by the bot.
                """)
    async def bbdaily(self, ctx, authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.bbdaily_command(ctx, False, authcode, not optout)


def setup(client):
    client.add_cog(BattleBreakersDaily(client))

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
        yellow = self.client.colours["warning_yellow"]

        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "bbdaily", authcode, slash, auth_opt_out,
                                                         True)
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
        vbucks = auth_info[1]["vbucks"]

        # check for le error code
        try:
            error_code = json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "daily", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            daily_feedback = json_response["notifications"]

            for notification in daily_feedback:
                if notification["type"] == "daily_rewards":
                    daily_feedback = notification
                    break

            day = daily_feedback["daysLoggedIn"]

            try:
                self.client.temp_auth[ctx.author.id]["day"] = day
            except:
                pass

            items = daily_feedback["items"]

            # Empty items means that daily was already claimed
            if len(items) == 0:
                reward = stw.get_reward(self.client, day, vbucks)
                embed = discord.Embed(
                    title=await stw.add_emoji_title(self.client, stw.ranerror(self.client), "warning"), description=
                    f"""\u200b
                You have already claimed your reward for day **{day}**.
                \u200b
                **{reward[1]} Todays reward was:**
                ```{reward[0]}```
                You can claim tomorrow's reward <t:{int(datetime.datetime.combine(datetime.datetime.utcnow() + datetime.timedelta(days=1), datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).timestamp())}:R>
                \u200b
                """, colour=yellow)
                embed = await stw.set_thumbnail(self.client, embed, "warn")
                embed = await stw.add_requested_footer(ctx, embed)
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return

            # Initialise the claimed embed
            embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Success", "checkmark"),
                                  description="\u200b",
                                  colour=succ_colour)

            # First item is the default daily reward, add it using the get_reward method
            reward = stw.get_reward(self.client, day, vbucks)

            # Add any excess items + the default daily reward
            for item in items[2:]:
                try:
                    amount = item["quantity"]
                    itemtype = item["itemType"]
                    reward[0] += f", {amount} {itemtype}"
                except:
                    pass

            embed.add_field(name=f'{reward[1]} On day **{day}**, you received:', value=f"```{reward[0]}```",
                            inline=True)

            # Second item is founders reward
            try:
                founders = items[1]
                amount = founders["quantity"]
                itemtype = founders["itemType"]

                if itemtype == 'CardPack:cardpack_event_founders':
                    display_itemtype = "Founder's Llama"
                elif itemtype == 'CardPack:cardpack_bronze':
                    display_itemtype = "Upgrade Llama (bronze)"
                else:
                    display_itemtype = itemtype

                embed.add_field(name=f'{self.client.config["emojis"]["founders"]} Founders rewards:',
                                value=f"```{amount} {display_itemtype}```",
                                inline=True)
            except:
                pass

            print('Successfully claimed daily:')
            print(reward[0])

            rewards = ''
            for i in range(1, 8):
                rewards += stw.get_reward(self.client, int(day) + i, vbucks)[0]
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
                                         "Rip") = "",
                           auth_opt_out: Option(bool, "Opt Out of Authentication session") = False, ):
        await self.bbdaily_command(ctx, True, token, not auth_opt_out)

    # Battle Breakers is a new tactical role-playing game developed by Epic Games for mobile and PC.
    @ext.command(name='bbdaily',
                 aliases=['bb'],
                 extras={'emoji': "vbucks", "args": {
                     'authcode': 'The authcode to use (Optional)',
                     'opt-out': 'Any value inputted D: into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
                 brief="Allows you to claim your Battle Breakers daily rewards (auth req.)",
                 description="""This command allows you to claim your Battle Breakers daily rewards, you must be authenticated to use this command.
                \u200b
                ⦾ You can check when you can claim your daily again by checking the bots status
                """)
    async def bbdaily(self, ctx, authcode='', optout=None):

        if optout is not None:
            optout = True
        else:
            optout = False

        await self.bbdaily_command(ctx, False, authcode, not optout)


def setup(client):
    client.add_cog(BattleBreakersDaily(client))

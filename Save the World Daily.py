import datetime
import json
import time
import discord
import requests
from discord.ext import commands

client = commands.AutoShardedBot(command_prefix='stw ', shard_count=1, case_insensetive=True)
client.remove_command('help')


class endpoints:
    ac = "https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode"
    token = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
    reward = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{0}/client/ClaimLoginReward?profileId=campaign"


def getToken(authCode: str):
    h = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
    }
    d = {
        "grant_type": "authorization_code",
        "code": authCode
    }
    r = requests.post(endpoints.token, headers=h, data=d)
    # print(r.text)
    r = json.loads(r.text)
    if "access_token" in r:
        access_token = r["access_token"]
        account_id = r["account_id"]
        print(f"access_token: {access_token}\naccount_id: {account_id}\nexpires_at: {r['expires_at']}")
        return access_token, account_id
    else:
        if "errorCode" in r:
            print(r)
            print(f"[ERROR] {r['errorCode']}")
            err = r['errorCode']
            reason = r['errorMessage']
        else:
            print("[ERROR] Unknown error")
        return False, err, reason


@client.event
async def on_ready():
    print('Client open')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('your dailies'))


# noinspection PyShadowingBuiltins,SpellCheckingInspection
@client.command()
async def help(message):
    embed = discord.Embed(title='Help', description='Commands:', colour=discord.Colour.red())
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/448073494660644884/757803329027047444/Asset_2.24x.1.png')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name='stw daily [AUTH TOKEN]',
                    value="Collect your daily reward without even opening the game\nDefeats the whole point of the "
                          "system but who cares?\n**Requires: Auth Token**\n[You can get an auth token by following this "
                          "link](https://tinyurl.com/epicauthcode)\nThen just simply copy your code from the response"
                          "and append to your command.\n'https://accounts.epicgames.com/fnauth?code=CODE'",
                    inline=False)
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


# noinspection PyUnboundLocalVariable
@client.command()
async def daily(message):
    msg = await message.channel.send(embed=discord.Embed(title='Processing', colour=discord.Color.blurple()))
    global daily_feedback, r
    amount = "Unknown"
    item = ""
    day = "Unknown"
    daily_feedback = ""
    r = ''
    token = str(message.message.content)[10:]
    if str(message.message.content)[9:] == "":
        await msg.edit(
            embed=discord.Embed(title="Specify Auth Token. [You can get yours here](https://tinyurl.com/epicauthcode)"))
    elif len(token) != 32:
        await msg.edit(embed=discord.Embed(title='Please provide a valid token'))
    else:
        await msg.edit(embed=discord.Embed(title=f"Using Auth token: {token}"))
        gtResult = getToken(token)
        if not gtResult[0]:
            # print(str(gtResult))
            embed = discord.Embed(
                title='We hit a roadblock',
                description='Failed to lock profile.',
                colour=0xf63a32
            )
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
            embed.add_field(name="Reason provided by the server:",
                            value=f"{gtResult[1]}",
                            inline=False)
            embed.add_field(name="Description provided by the server:",
                            value=f"{gtResult[2]}",
                            inline=False)
        else:
            h = {
                "Authorization": f"bearer {gtResult[0]}",
                "Content-Type": "application/json"
            }
            r = requests.post(endpoints.reward.format(gtResult[1]), headers=h, data="{}")
            await msg.edit(embed=discord.Embed(title='Claimed your daily.'))
        try:
            if str(r.text).find('{"errorCode":"') == '-1':
                embed = discord.Embed(
                    title='We hit a roadblock',
                    description='Failed to lock profile.',
                    colour=0xf63a32
                )
                embed.set_thumbnail(
                    url='https://cdn2.iconfinder.com/data/icons/mix-color-5/100/Mix_color_5__info-512.png')
                embed.add_field(name="Reason provided by the server:",
                                value=str(r.text).split('{"errorCode":"', 1)[1].split('","errorMessage":"', 1)[0],
                                inline=False)
                embed.add_field(name="Description provided by the server:",
                                value=str(r.text).split('","errorMessage":"', 1)[1].split('","messageVars"', 1)[0],
                                inline=False)
            else:
                try:
                    # print(str(str(r.text).split("notifications", 1)[1][2:].split('],"profile', 1)[0]))
                    daily_feedback = str(r.text).split("notifications", 1)[1][4:].split("], 'profile", 1)[0]
                    day = str(daily_feedback).split('"daysLoggedIn":', 1)[1].split(',"items":[', 1)[0]
                    try:
                        item = str(daily_feedback).split('[{"itemType":"', 1)[1].split('","itemGuid"', 1)[0]
                        amount = str(daily_feedback).split('","quantity":', 1)[1].split("}]}", 1)[0]
                        embed = discord.Embed(title='Success',
                                              colour=0x00c113)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/757803334198624336/Asset_2.1.14x2.png')
                        embed.add_field(name=f'On day **{day}**, you received:', value=f"**{amount}** **{item}**",
                                        inline=False)
                        # print(item)
                        # print(amount)
                    except:
                        embed = discord.Embed(title='Hmm',
                                              colour=0xeeaf00)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/757803329299415163/Asset_1.14x2.png')
                        embed.add_field(name='It appears that you have **already claimed** todays reward.',
                                        value=f"You are on day **{day}**", inline=False)
                except:
                    embed = discord.Embed(
                        title='We hit a roadblock',
                        description='Failed to lock profile.',
                        colour=0xf63a32
                    )
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                    embed.add_field(name="Reason provided by the server:", value=f"{gtResult[1]}", inline=False)
                    embed.add_field(name="Description provided by the server:", value=f"{gtResult[1]}", inline=False)
        except:
            pass
        # embed.set_author(name=str(message.message.content)[9:],
        #                 icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/31'
        #                          '/Epic_Games_logo.svg/1200px-Epic_Games_logo.svg.png')
        embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        # await message.channel.send(embed=embed)
        await msg.edit(embed=embed)


client.run('NzU3Nzc2OTk2NDE4NzE1NjUx.X2lU0g.QmLf_ATPRcRLT4gYXeP_TaRQBvA')

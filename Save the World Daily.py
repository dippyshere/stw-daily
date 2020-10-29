import asyncio
import datetime
import json
# noinspection PyUnresolvedReferences
import os
import time
import psutil

import discord
import requests
from discord.ext import commands
import discord.member
from discord.utils import get


def mixedCase(*args):
    """
    Generates a completely random number
    Guaranteed to be random 100% **WORKING 2020** FREE HD 4k
    """
    total = []
    import itertools
    for string in args:
        a = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in string)))
        for x in list(a): total.append(x)
    return list(total)


client = commands.AutoShardedBot(case_insensetive=True, command_prefix=mixedCase('stw '), shard_count=1)
client.remove_command('help')
uptime_start = datetime.datetime.utcnow()
daily_feedback = ""
r = ''
last_error_py = 'Nothing'
last_error_server = 'Nothing'

"""
im really sorry that this is
so scuffed but whatever ~~report
"""
report_aliases = mixedCase('report')
report_aliases.extend(['debug'])
if 'Report' in report_aliases: report_aliases.remove('Report')
reply_aliases = mixedCase('reply')
if 'Reply' in reply_aliases: reply_aliases.remove('Reply')
info_aliases = mixedCase('info')
info_aliases.extend(['infomation'])
if 'Info' in info_aliases: info_aliases.remove('Info')
temp_aliases = mixedCase('temp')
if 'Temp' in temp_aliases: temp_aliases.remove('Temp')
getmtime_aliases = mixedCase('getmtime')
getmtime_aliases.extend(['update'])
if 'Getmtime' in getmtime_aliases: getmtime_aliases.remove('getmtime')
help_aliases = mixedCase('help')
help_aliases.extend(['halp', 'holp', 'how', 'hel', 'h', '?'])
if 'Help' in help_aliases: help_aliases.remove('Help')
uptime_aliases = mixedCase('uptime')
uptime_aliases.extend(['downtime'])
if 'Uptime' in uptime_aliases: uptime_aliases.remove('Uptime')
instruction_aliases = mixedCase('instruction')
instruction_aliases.extend(['detailed'])
if 'Instruction' in instruction_aliases: instruction_aliases.remove('Instruction')
ping_aliases = mixedCase('ping')
ping_aliases.extend(['pong'])
if 'Ping' in ping_aliases: ping_aliases.remove('ping')
emoji_aliases = mixedCase('emoji')
emoji_aliases.extend(['animate'])
if 'Emoji' in emoji_aliases: emoji_aliases.remove('Emoji')
daily_aliases = mixedCase('daily')
daily_aliases.extend(['collect', 'dailt', 'daliy', 'dail', 'd', 'daiyl', 'day', 'reward', 'dialy'])
if 'Daily' in daily_aliases: daily_aliases.remove('Daily')


class endpoints:
    ac = "https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode"
    token = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
    reward = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{0}/client/ClaimLoginReward?profileId=campaign"


# noinspection PyUnboundLocalVariable,PyShadowingNames
def getToken(authCode: str):
    global last_error_py, last_error_server
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
        # print(f"access_token: {access_token}\naccount_id: {account_id}\nexpires_at: {r['expires_at']}")
        return access_token, account_id
    else:
        if "errorCode" in r:
            # print(r)
            print(f"[ERROR] {r['errorCode']}")
            err = r['errorCode']
            reason = r['errorMessage']
            last_error_server = err
        else:
            print("[ERROR] Unknown error")
        return False, err, reason


def get_bot_uptime():
    now = datetime.datetime.utcnow()
    delta = now - uptime_start
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
    return fmt.format(d=days, h=hours, m=minutes, s=seconds)


def time_until_end_of_day():
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    a = datetime.datetime.combine(tomorrow, datetime.time.min) - datetime.datetime.utcnow()
    hours, remainder = divmod(int(a.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = ''
    if hours == 1:
        fmt += '{h} hour, '
    else:
        fmt += '{h} hours, '
    if minutes == 1:
        fmt += '{m} minute'
    else:
        fmt += '{m} minutes'
    return fmt.format(h=hours, m=minutes)
    # print(fmt.format(h=hours, m=minutes))


def lastmfunction():
    try:
        lastm = datetime.datetime.utcfromtimestamp(os.path.getmtime(r'/app/stw-daily-heroku.py')).strftime(
            '%I:%M %p - %d/%m/%Y')
    except:
        try:
            lastm = datetime.datetime.utcfromtimestamp(os.path.getmtime(
                r'C:\Users\dippy\OneDrive - NSW Department of Education\Desktop\discord bots\STW Daily bot.py')).strftime(
                '%I:%M %p - %d/%m/%Y')
        except:
            lastm = 'Not available'
    return lastm


@client.event
async def on_ready():
    print('Client open')
    sum = 0
    # Loop through the servers, get all members and add them up
    for s in client.guilds:
        sum += len(s.members)
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name=f"stw help  |  Reset in: \n{time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds  |  Last update at: {lastmfunction()} (UTC +0)"))


async def update_status():
    await client.wait_until_ready()
    while True:
        sum = 0
        # Loop through the servers, get all members and add them up
        for s in client.guilds:
            sum += len(s.members)
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening,
                                      name=f"stw help  |  Reset in: \n{time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds with {sum} members |  Last update at: {lastmfunction()} (UTC +0)"))
        await asyncio.sleep(60)


@client.command(name='Report', aliases=report_aliases, description='Used to send reports.')
async def report(message):
    if message.message.content[10:] == '':
        await message.channel.send(embed=discord.Embed(title="I'm gonna need a little more detail than that i'm afraid"
                                                             " :/", description='This command is used to report errors'
                                                                                ' to the developer. Append your report '
                                                                                'content.',
                                                       color=discord.Colour.blue()))
    else:
        await message.message.add_reaction('👍')
        user = client.get_user(349076896266452994)
        message_content = str(message.message.content)
        author_id = message.author.id
        print(f'Report Created by {client.get_user(message.author.id)}. Content: {message_content}')
        embed = discord.Embed(title='Information', description='_ _', colour=discord.Colour.red())
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.add_field(name='Report Content:', value=f'{message_content}', inline=False)
        embed.add_field(name='Invoker ID:', value=f'{author_id} | {client.get_user(message.author.id)}', inline=False)
        embed.add_field(name='Channel ID:', value=f'{message.channel.id}', inline=False)
        embed.add_field(name='Last Py Error:', value=f'{last_error_py}', inline=True)
        embed.add_field(name='Last Server Error:', value=f'{last_error_server}', inline=True)
        embed.set_footer(text=f"\nReport generated on behalf of: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await user.send(embed=embed)


@client.command(name='Reply', aliases=reply_aliases, description='Used to reply to reports. Exclusive to bot owner')
async def reply(message, id=None):
    if message.author.id == 349076896266452994:
        await message.message.add_reaction('👍')
        user = client.get_user(int(id))
        embed = discord.Embed(title='RE: Report', description='_ _', colour=discord.Colour.red())
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.add_field(name='Content:', value=f'{message.message.content[29:]}', inline=False)
        embed.add_field(name='Want to reply?', value='Simply create a new report. You can even do it here.',
                        inline=True)
        embed.set_footer(text=f"\nReply generated on behalf of: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await user.send(embed=embed)
    else:
        await message.channel.send('Access is denied. Maybe you were looking for ``stw report``?')


# noinspection PyBroadException
@client.command(name='Info', aliases=info_aliases,
                description='Used to see stats and info about the bot hosting service')
async def info(message):
    print(f'info requested by: {message.author.name}')
    try:
        osgetlogin = os.getlogin()
    except:
        osgetlogin = 'Not Available'
    embed = discord.Embed(title='Information', description='Statistics:', colour=discord.Colour.red())
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/695117839383920641/759372935676559400/Asset_4.14x.png')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name='Host statistics:', value=f'os.name: {os.name}\nos.cpu_count: {os.cpu_count()}\n'
                                                   f'os.getcwd: {os.getcwd()}\nos.getlogin: {osgetlogin}\n'
                                                   f'CPU usage: {psutil.cpu_percent()}%\nCPU Freq: {int(psutil.cpu_freq().current)}mhz\nRAM Usage:\nTotal: '
                                                   f'{psutil.virtual_memory().total // 1000000}mb\nUsed: '
                                                   f'{psutil.virtual_memory().used // 1000000}mb\nFree: '
                                                   f'{psutil.virtual_memory().free // 1000000}mb\nUtilisation: '
                                                   f'{psutil.virtual_memory().percent}%')
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


@client.command(name='Temp', aliases=temp_aliases, description='Used')
async def temp(message):
    print(f'temp requested by: {message.author.name}')
    try:
        psutilsensors_temperatures = psutil.sensors_temperatures()
    except:
        psutilsensors_temperatures = 'Not available'
    await message.channel.send(psutilsensors_temperatures)


@client.command(name='Member Count', aliases=["mc"], description='Used')
async def membercount(message):
    print(f'membercount requested by: {message.author.name}')
    member_count = len(message.guild.members)  # includes bots
    true_member_count = len([m for m in message.guild.members if not m.bot])
    bot_count = len([m for m in message.guild.members if m.bot])
    sum = 0
    # Loop through the servers, get all members and add them up
    for s in client.guilds:
        sum += len(s.members)
    embed = discord.Embed(title=f"Member count", description='Number of users and bots in all servers', color=discord.Color(0xffff00))
    embed.add_field(name=f'Members in {message.guild.name}', value=f'Users: {true_member_count}\nBots: {bot_count}\nTotal: {message.guild.member_count}')
    embed.add_field(name=f'Members in all servers', value=f'Total: {sum}')
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


@client.command(name='getmtime', aliases=getmtime_aliases,
                description='Used to get the last modified date of the python file')
async def getmtime(message):
    print(f'getmtime requested by: {message.author.name}')
    await message.channel.send(lastmfunction())


# noinspection PyShadowingBuiltins
@client.command(name='Help', aliases=help_aliases, description='Well, this tells you what commands are available.')
async def help(message):
    print(f'help requested by: {message.author.name}')
    embed = discord.Embed(title='Help', description='Commands:', colour=discord.Colour.red())
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/448073494660644884/757803329027047444/Asset_2.24x.1.png')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name='**stw daily** [AUTH TOKEN]',
                    value="Collect your daily reward without even opening the game\nDefeats the whole point of the "
                          "system but who cares?\n**Requires: Auth Token**\n[You can get an auth token by following this "
                          "link](https://tinyurl.com/epicauthcode)\nThen just simply copy your code from the response "
                          "and append to your command.\n'https://accounts.epicgames.com/fnauth?code=CODE'",
                    inline=False)
    embed.add_field(name='**stw instruction**', value='More detailed instructions for using the bot', inline=False)
    embed.add_field(name='**stw ping**',
                    value='Sends the WebSocket latency and actual latency.')
    embed.add_field(name='**stw info**', value='Returns information about the bots host')
    embed.add_field(name='Want to quickly see some relevant information?',
                    value='Have a look at the bot playing status')
    embed.add_field(name='**Encountered an issue?**',
                    value='**Use **``stw report``** to send a report.**\nUsage: ``stw report [info about your issue]``.\nIf I need to reply to you, I will try to do it through DMs.',
                    inline=False)
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


@client.command(name='Uptime', aliases=uptime_aliases,
                description='Send bot uptime. Note that on heroku, dynos are cycled every 24 hours')
async def uptime(message):
    print(f'uptime requested by: {message.author.name}')
    """Tells you how long the bot has been up for."""
    await message.send('Uptime: **{}**'.format(get_bot_uptime()))


@client.command(name='Instruction', aliases=instruction_aliases,
                description='Detailed instructions to get auth token and claim daily')
async def instruction(message):
    print(f'instruction requested by: {message.author.name}')
    embed = discord.Embed(title='How to use "STW Daily"', color=discord.Color.blurple())
    embed.set_footer(text='This bot was made by Dippy is not here', icon_url=message.author.avatar_url)
    embed.add_field(name='Welcome',
                    value='I will collect your daily rewards for you, without the need to launch the game.\n\n'
                          'To get started, [Visit this link](https://tinyurl.com/epicauthcode), and copy **only** the '
                          'authorisation code that it gives you.\n\nFor example,\n```js'
                          '\n{"redirectUrl":"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b14'
                          '57c8e34a1f6026faa35","sid":null}\n```\nwill become\n```\n'
                          'a51c1f4d35b1457c8e34a1f6026faa35\n```\n\nThen, just simply copy paste that into '
                          'your command, like so:\n``stw daily a51c1f4d35b1457c8e34a1f6026faa35``\n:bulb: '
                          'Pro tip: In most browsers, double click on or below the code and it should '
                          'highlight just the code\n\nIf there is any error, please do not hesitate to ask '
                          '<@!349076896266452994> and I will try to resolve the issue.\n\n```cs\n# WARNING\n'
                          '"Your Authorisation code can potentially be used maliciously. '
                          'It is only temporary and will expire after use, however that does not mean you '
                          'shouldn\'t be careful who you give it to."\n```\n```css\n# NOT AFFILIATED'
                          ' WITH EPIC GAMES\n```')
    await message.channel.send(embed=embed)


# noinspection SpellCheckingInspection,PyShadowingNames
@client.command(name='ping', aliases=ping_aliases, description='Send websocket ping and embed edit latency')
async def ping(message):
    print(f'ping requested by: {message.author.name}')
    websocket_ping = '{0}'.format(int(client.latency * 100)) + ' ms'
    before = time.monotonic()
    # msg = await message.send("Pong!")
    # await msg.edit(content=f"Pong!  `{int(ping)}ms`")
    # await message.channel.send(f'websocket latency: {client.latency*100}ms')
    # await message.send('websocket: {0}'.format(int(client.latency * 100)) + ' ms')
    embed = discord.Embed(title='Latency', color=discord.Color.blurple())
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    embed.add_field(name='Websocket :electric_plug:', value=websocket_ping, inline=True)
    embed.add_field(name='Actual :microphone:',
                    value='<a:loadin:759293511475527760>', inline=True)
    # embed.add_field(name='Uptime :alarm_clock:', value=f'{get_bot_uptime()}', inline=True)
    embed2 = discord.Embed(title='Latency', color=discord.Color.blurple())
    embed2.set_footer(text=f"\nRequested by: {message.author.name} • "
                           f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                      , icon_url=message.author.avatar_url)
    embed2.add_field(name='Websocket :electric_plug:', value=websocket_ping, inline=True)
    msg = await message.channel.send(embed=embed)
    ping = (time.monotonic() - before) * 1000
    embed2.add_field(name='Actual :microphone:',
                     value=f'{int(ping)}ms', inline=True)
    await asyncio.sleep(4)
    # embed2.add_field(name='Uptime :alarm_clock:', value=f'{get_bot_uptime()}', inline=True)
    await msg.edit(embed=embed2)


@client.command(name='Emoji', aliases=emoji_aliases, description='Sends an animated loading emoji')
async def emoji(message):
    print(f'emoji requested by: {message.author.name}')
    # await message.channel.send('<a:loading:759292972784418800>')
    # await message.channel.send(f'<a:god:424520269315440650>')
    await message.channel.send('<a:loadin:759293511475527760>')


# noinspection PyUnboundLocalVariable,PyUnusedLocal,PyBroadException
@client.command(name='Daily', aliases=daily_aliases, description='The main star of the show. parses daily command')
async def daily(message, token=''):
    global last_error_py, last_error_server
    print(f'daily requested by: {message.author.name}')
    msg = await message.channel.send(embed=discord.Embed(title='Processing', colour=discord.Color.blurple()))
    global daily_feedback, r
    daily_feedback = ""
    r = ''
    # token = str(message.message.content)[10:]
    if token == "":
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
            last_error_server = gtResult[1]
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
                print('error')
                print(str(r.text).split('{"errorCode":"', 1)[1].split('","errorMessage":"', 1)[0])
                last_error_server = str(r.text).split('{"errorCode":"', 1)[1].split('","errorMessage":"', 1)[0]
            else:
                try:
                    # print(str(str(r.text).split("notifications", 1)[1][2:].split('],"profile', 1)[0]))
                    daily_feedback = str(r.text).split("notifications", 1)[1][4:].split('],"profile', 1)[0]
                    day = str(daily_feedback).split('"daysLoggedIn":', 1)[1].split(',"items":[', 1)[0]
                    try:
                        # await message.channel.send(f'Debugging info because sometimes it breaks:\n{daily_feedback}')
                        item = str(daily_feedback).split('[{"itemType":"', 1)[1].split('","itemGuid"', 1)[0]
                        amount = str(daily_feedback).split('"quantity":', 1)[1].split("}]}", 1)[0]
                        embed = discord.Embed(title='Success',
                                              colour=0x00c113)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/757803334198624336/Asset_2.1.14x2.png')
                        if "}" in amount:
                            amount2 = str(amount).split("},", 1)[0]
                            fndr_item = str(amount).split('itemType":"', 1)[1].split('","', 1)[0]
                            fndr_amount = str(amount).split('quantity":', 1)[1]
                            embed.add_field(name=f'On day **{day}**, you received:', value=f"**{amount2}** **{item}**",
                                            inline=False)
                            embed.add_field(name=f'Founders rewards:', value=f"**{fndr_amount}** **{fndr_item}**",
                                            inline=False)
                        else:
                            embed.add_field(name=f'On day **{day}**, you received:', value=f"**{amount}** **{item}**",
                                            inline=False)
                        print('success')
                        print(item)
                        print(amount)
                    except Exception as e:
                        # await message.channel.send(f'Debugging info because sometimes it breaks:\n{e}')
                        embed = discord.Embed(title='Hmm',
                                              colour=0xeeaf00)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/757803329299415163/Asset_1.14x2.png')
                        embed.add_field(name='It appears that you have **already claimed** todays reward.',
                                        value=f"You are on day **{day}**", inline=False)
                        print('Daily was already claimed or i screwed up')
                        print(f'Error info: {e}')
                        last_error_py = str(e)
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
                    print(f'error: {gtResult[1]}')
                    last_error_server = gtResult[1]
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


# noinspection SpellCheckingInspection
client.loop.create_task(update_status())
client.run('token')

import asyncio
import datetime
import json
# noinspection PyUnresolvedReferences
import os
import time
import random
import discord
import discord.member
import psutil
import requests
from discord.ext import commands
import items
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

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
slash = SlashCommand(client, sync_commands=True)

guild_ids = [390680124418162689]
uptime_start = datetime.datetime.utcnow()
daily_feedback = ""
r = ''
amount2 = ''
rewards = ''
last_error_py = 'Nothing'
last_error_server = 'Nothing'
errorList = ["That wasn't supposed to happen", "Whoops!", "We hit a roadblock", "Not the llama you're looking for",
             "Uh-oh! Something goofed"]
tipsList = [
    "You can [refresh the final page](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code) to get a new code (if you're signed in)",
    "Follow [@STW_Daily](https://twitter.com/STW_Daily) on Twitter for the latest updates in your timeline",
    "Found a problem? Report it by using stw report!",
    "Found problems with the translation feature? Let me know with stw report!", "You are epic! Keep doing you! ❤"]

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
help_aliases.extend(['halp', 'holp', 'how', 'hel', 'h', '?', 'helpp'])
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
daily_aliases.extend(['collect', 'dailt', 'daliy', 'dail', 'd', 'daiyl', 'day', 'dialy'])
if 'Daily' in daily_aliases: daily_aliases.remove('Daily')


class endpoints:
    ac = "https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode"
    token = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
    reward = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{0}/client/ClaimLoginReward?profileId=campaign"

def lastmfunction():
    try:
        lastm = datetime.datetime.utcfromtimestamp(os.path.getmtime(r'/app/stw-daily-heroku.py')).strftime(
            '%I:%M %p - %d/%m/%Y')
    except:
        try:
            lastm = datetime.datetime.utcfromtimestamp(os.path.getmtime(
                r'C:\Users\dippy\OneDrive - NSW Department of Education\Desktop\discord bots\Save The world Daily\Save the World Daily.py')).strftime(
                '%I:%M %p - %d/%m/%Y')
        except:
            lastm = 'Not available'
    return lastm

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


@client.event
async def on_ready():
    print('Client open')
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name=f"stw help  |  Reset in: \n{time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds"))


async def update_status():
    await client.wait_until_ready()
    while True:
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening,
                                      name=f"stw help  |  Reset in: \n{time_until_end_of_day()}\n  |  In {len(client.guilds)} guilds"))
        await asyncio.sleep(60)



# noinspection PyBroadException
async def info_command(message):
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
                                                   f'CPU usage: {psutil.cpu_percent()}%\n'
                                                   f'CPU Freq: {int(psutil.cpu_freq().current)}mhz\nRAM Usage:\nTotal: '
                                                   f'{psutil.virtual_memory().total // 1000000}mb\nUsed: '
                                                   f'{psutil.virtual_memory().used // 1000000}mb\nFree: '
                                                   f'{psutil.virtual_memory().free // 1000000}mb\nUtilisation: '
                                                   f'{psutil.virtual_memory().percent}%')
    embed.add_field(name='Bot statistics:', value=f'Last update at: {lastmfunction()}')
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)

@client.command(name='Info',
                aliases=info_aliases,
                description='Used to see stats and info about the bot hosting service')
async def info(ctx):
    await info_command(ctx)

@slash.slash(name='info',
             description='Used to see stats and info about the bot hosting service',
             guild_ids = guild_ids)
async def slashinfo(ctx):
    await info_command(ctx)
    





def getReward(day):
    day_mod = int(day) % 336
    if day_mod == 0:
        day_mod = 336
    return items.ItemDictonary[str(day_mod)]

async def reward_command(message, day, limit):
    global rewards
    print(f'reward info requested by: {message.author.name}')
    if day == 'Uhoh-stinky':
        await message.channel.send('specify the day (number) of which you would like to see.')
    elif not day.isnumeric():
        await message.channel.send('specify a number only please. your argument is what day you want to know about.')
    else:
        embed = discord.Embed(title=f"Reward info", description=f'For day **{day}**', color=discord.Color(0xff00ff))
        embed.add_field(name=f'**Item: **', value=f'{getReward(day)}')
        for day1 in items.ItemDictonary:
            if 'vBucks' in items.ItemDictonary[day1]:
                if int(day) % 336 < int(day1):
                    if int(day1) - int(day) % 336 == 1:
                        embed.add_field(name=f'**Next vBuck reward in: **',
                                        value=f'**{int(day1) - int(day) % 336}** day.')
                    else:
                        embed.add_field(name=f'**Next vBuck reward in: **',
                                        value=f'**{int(day1) - int(day) % 336}** days.')
                    break
        rewards = ''
        if limit < 1:
            limit = 7
        for day2 in range(1, limit):
            rewards += getReward(day2 + int(day))
            if not (day2 + 1 == limit):
                rewards += ', '
            else:
                rewards += '.'
        if limit == 1:
            embed.add_field(name=f'**Tomorrow\'s reward:**', value=f'{getReward(int(day) + 1)}', inline=False)
        else:
            embed.add_field(name=f'Rewards for the next **{limit}** days:', value=f'{rewards}', inline=False)
        embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)

@client.command(name='reward',
                aliases=["rwrd"],
                description='Sends info based on a dictionary of items')
async def reward(ctx, day='Uhoh-stinky', limit=7):
    await reward_command(ctx, day, limit)

@slash.slash(name='reward',
             description='Sends info based on a dictionary of items to view rewards at any amount of days.',
             options = [
                    create_option(name="day",
                    description="The day of which you would like to see.",
                    option_type=4,  
                    required=True),

                    create_option(name="limit",
                    description="Amount of rewards to view from set day.",
                    option_type=4,
                    required=False),
                
                  ],  guild_ids=guild_ids
             )
async def slashreward(ctx, day='Uhoh-stinky', limit=7):
    await reward_command(ctx, str(day), limit)





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
                          "and append to your command.",
                    inline=False)
    embed.add_field(name='**stw instruction**', value='More detailed instructions for using the bot', inline=False)
    embed.add_field(name='**stw rwrd [day] [future day]**',
                    value='Sends the friendly name of a reward for the given day.')
    embed.add_field(name='**stw ping**',
                    value='Sends the WebSocket latency and actual latency.')
    embed.add_field(name='**stw info**', value='Returns information about the bots host')
    embed.add_field(name='Want to quickly see some relevant information?',
                    value='Have a look at the bot playing status')
    embed.add_field(name='**Encountered an issue?**',
                    value='**Use **``stw report``** to send a report.**\nUsage: ``stw report [info about your issue]``.',
                    inline=False)
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


    



async def instruction_command(message, arg):
    print(f'instruction requested by: {message.author.name}')

    examples = {'norm': 'stw daily a51c1f4d35b1457c8e34a1f6026faa35',
                'slash': '/daily a51c1f4d35b1457c8e34a1f6026faa35'
                }
    embed = discord.Embed(title='How to use "STW Daily"', color=discord.Color.blurple())
    embed.set_footer(text='This bot was made by Dippy is not here', icon_url=message.author.avatar_url)
    embed.add_field(name='Welcome',
                    value='This will show you how to use the bot.\n\n'
                          'To get started, [Visit this link](https://tinyurl.com/epicauthcode), and copy **only** the '
                          'authorisation code that it gives you. **(not the code from the URL)**.'
                          '\nIf you are already signed into Epic Games on your browser, you can just '
                          '[refresh the final page](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)'
                          ' to get a new code\n\nFor example,\n```js'
                          '\n{"redirectUrl":"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b14'
                          '57c8e34a1f6026faa35","sid":null}\n```\nwill become\n```\n'
                          'a51c1f4d35b1457c8e34a1f6026faa35\n```\n\nThen, just simply copy paste that into '
                          f'your command, like so:\n``{examples.get(arg)}``\n:bulb: '
                          'Pro tip: In most browsers, double click on or below the code and it should '
                          'highlight just the code\n\nIf you need help, [join the server](https://discord.gg/MtSgUu).'
                          ' Don\'t be afraid to ask!',
                    inline=False)
    embed.add_field(name='Important Disclaimers',
                    value='AFAIK, your auth code can be used maliciously, if you are sceptical,'
                          ' [read the source code](https://github.com/dippyshere/stw-daily), or check out '
                          '<#771902446737162240> over in [STW Dailies](https://discord.gg/MtSgUu)',
                    inline=False)
    await message.channel.send(embed=embed)

@client.command(name='Instruction', aliases=instruction_aliases,
                description='Detailed instructions to get auth token and claim daily')
async def instruction(ctx):
    await instruction_command(ctx, 'norm')

@slash.slash(name='Instruction',
                description='Detailed instructions to get auth token and claim daily',
             guild_ids = guild_ids)
async def slashinstruction(ctx):
    await instruction_command(ctx, 'slash')




    
# noinspection SpellCheckingInspection,PyShadowingNames
async def ping_command(message):
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

@client.command(name='ping',
                aliases=ping_aliases,
                description='Send websocket ping and embed edit latency')
async def ping(ctx):
    await ping_command(ctx)

@slash.slash(name='ping',
                description='Send websocket ping and embed edit latency',
             guild_ids = guild_ids)
async def slashping(ctx):
    await ping_command(ctx)


async def report_command(ctx):
    await ctx.send('If you need help or want to report a bug join https://discord.gg/Mt7SgUu')

@client.command(name='report',
                aliases=['rprt'],
                description='why do i exist, only to suffer?')
async def report(ctx):
    await report_command(ctx)

@slash.slash(name='report',
                description='If you need help or want to report.',
             guild_ids = guild_ids)
async def slashreport(ctx):
    await ctx.send('If you need help or want to report a bug join https://discord.gg/Mt7SgUu')

# noinspection PyUnboundLocalVariable,PyUnusedLocal,PyBroadException
async def daily_command(message, token=''):
    global last_error_py, last_error_server, amount2, rewards
    print(f'daily requested by: {message.author.name}')
    global daily_feedback, r
    daily_feedback = ""
    r = ''
    if token == "":
        embed = discord.Embed(title="No auth code", description='', colour=discord.Color.red())
        embed.add_field(name='You can get it from:',
                        value='[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)\n[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)',
                        inline=False)
        embed.add_field(name='Need help? Run ``stw instruction``',
                        value='Or [Join the support server](https://discord.gg/Mt7SgUu).', inline=True)
        embed.add_field(name='Note: You need a new code __every day__.',
                        value='Thank you for using my bot ❤', inline=True)
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}",
                         icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    elif len(token) != 32:
        embed = discord.Embed(title="Incorrect formatting", description='', colour=discord.Color.red())
        embed.add_field(name='It should be 32 characters long, and only contain numbers and letters',
                        value='Check if you have any stray quotation marks')
        embed.add_field(name='An Example:',
                        value='a51c1f4d35b1457c8e34a1f6026faa35')
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Logging in and processing <a:loadin:759293511475527760>",
                              description='This shouldn\'t take long...', colour=discord.Color.green())
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        msg = await message.channel.send(embed=embed)
        gtResult = getToken(token)
        if not gtResult[0]:
            # print(str(gtResult))
            errorType = str(gtResult[1])
            if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
                # login error
                embed = discord.Embed(
                    title=errorList[random.randint(0, 4)],
                    description='Your authorisation code is invalid',
                    colour=0xf63a32
                )
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                embed.add_field(name="Why this happens:",
                                value='Your code is expired, or of the wrong type\n(e.g. from url instead of page body)',
                                inline=False)
                embed.add_field(name="How to fix:",
                                value='[Refresh the page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)',
                                inline=False)
                embed.add_field(name="What it should look like:",
                                value='32 characters of only numbers and letters.\ne.g. a51c1f4d35b1457c8e34a1f6026faa35',
                                inline=False)
            if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
                # invalid grant error
                embed = discord.Embed(
                    title=errorList[random.randint(0, 4)],
                    description='Your authorisation code was created with the wrong link',
                    colour=0xf63a32
                )
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                embed.add_field(name="Why this happens:",
                                value='You used a different link to get your token',
                                inline=False)
                embed.add_field(name="How to fix:",
                                value='[Use this page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n[Join the support server for further help](https://discord.gg/mt7sguu)',
                                inline=False)
            if len(errorType) == 32:
                # login error
                embed = discord.Embed(
                    title=errorList[random.randint(0, 4)],
                    description='You probably don\'t have Save the World',
                    colour=0xf63a32
                )
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                embed.add_field(name="Why this happens:",
                                value='You signed into the wrong or a different Epic Games account',
                                inline=False)
                embed.add_field(name="How to fix:",
                                value='Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                inline=False)
                embed.add_field(
                    name="But I do have Save the world, and I\'m absolutely sure I used the correct account.",
                    value='This message may be a mistake then. If it is, let the owner know somehow. Join the'
                          ' [support server](https://discord.gg/mt7sguu)',
                    inline=False)
            last_error_server = gtResult[1]
        else:
            h = {
                "Authorization": f"bearer {gtResult[0]}",
                "Content-Type": "application/json"
            }
            r = requests.post(endpoints.reward.format(gtResult[1]), headers=h, data="{}")
            # await msg.edit(embed=discord.Embed(title='Claimed your daily.'))
        try:
            if str(r.text).find('{"errorCode":"') == '-1':
                errorType = str(gtResult[1])
                if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
                    # login error
                    embed = discord.Embed(
                        title=errorList[random.randint(0, 4)],
                        description='Your authorisation code is invalid',
                        colour=0xf63a32
                    )
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                    embed.add_field(name="Why this happens:",
                                    value='Your code is expired, or of the wrong type\n(e.g. from url instead of page body)',
                                    inline=False)
                    embed.add_field(name="How to fix:",
                                    value='[Refresh the page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)',
                                    inline=False)
                    embed.add_field(name="What it should look like:",
                                    value='32 characters of only numbers and letters.\ne.g. a51c1f4d35b1457c8e34a1f6026faa35',
                                    inline=False)
                if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
                    # invalid grant error
                    embed = discord.Embed(
                        title=errorList[random.randint(0, 4)],
                        description='Your authorisation code was created with the wrong link',
                        colour=0xf63a32
                    )
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                    embed.add_field(name="Why this happens:",
                                    value='You used a different link to get your token',
                                    inline=False)
                    embed.add_field(name="How to fix:",
                                    value='[Use this page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n[Join the support server for further help](https://discord.gg/mt7sguu)',
                                    inline=False)
                if len(errorType) == 32:
                    # login error
                    embed = discord.Embed(
                        title=errorList[random.randint(0, 4)],
                        description='You probably don\'t have Save the World',
                        colour=0xf63a32
                    )
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                    embed.add_field(name="Why this happens:",
                                    value='You signed into the wrong or a different Epic Games account',
                                    inline=False)
                    embed.add_field(name="How to fix:",
                                    value='Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                    inline=False)
                    embed.add_field(
                        name="But I do have Save the world, and I\'m absolutely sure I used the correct account.",
                        value='This message may be a mistake then. If it is, let the owner know somehow. Join the'
                              ' [support server](https://discord.gg/mt7sguu)',
                        inline=False)
                last_error_server = gtResult[1]
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
                        try:
                            if "}" in amount:
                                amount2 = str(amount).split("},", 1)[0]
                                fndr_item = str(amount).split('itemType":"', 1)[1].split('","', 1)[0]
                                fndr_amount = str(amount).split('quantity":', 1)[1]
                                if fndr_item == 'CardPack:cardpack_event_founders':
                                    fndr_item_f = "Founder's Llama"
                                elif fndr_item == 'CardPack:cardpack_bronze':
                                    fndr_item_f = "Upgrade Llama (bronze)"
                                else:
                                    fndr_item_f = fndr_item
                                embed.add_field(name=f'On day **{day}**, you received:', value=f"**{getReward(day)}**",
                                                inline=False)
                                embed.add_field(name=f'Founders rewards:', value=f"**{fndr_amount}** **{fndr_item_f}**",
                                                inline=False)
                                embed.add_field(name=f'Internal names:', value=f"**{amount2}** **{item}**",
                                                inline=False)
                                embed.add_field(name=f'Founders:', value=f"**{fndr_amount}** **{fndr_item}**",
                                                inline=False)
                            else:
                                embed.add_field(name=f'On day **{day}**, you received:', value=f"**{getReward(day)}**",
                                                inline=False)
                                embed.add_field(name=f'Internal name:', value=f"**{amount}** **{item}**",
                                                inline=False)
                        except:
                            if "}" in amount:
                                amount2 = str(amount).split("},", 1)[0]
                                fndr_item = str(amount).split('itemType":"', 1)[1].split('","', 1)[0]
                                fndr_amount = str(amount).split('quantity":', 1)[1]
                                embed.add_field(name=f'On day **{day}**, you received:',
                                                value=f"**{amount2}** **{item}**",
                                                inline=False)
                                embed.add_field(name=f'Founders rewards:', value=f"**{fndr_amount}** **{fndr_item}**",
                                                inline=False)
                                embed.add_field(name=f'Using backup code',
                                                value=f"An error occurred in trying to display the friendly name of items. Please report this issue via ``stw report [content]``",
                                                inline=False)
                                print('using backup')
                            else:
                                embed.add_field(name=f'On day **{day}**, you received:',
                                                value=f"**{amount}** **{item}**",
                                                inline=False)
                                embed.add_field(name=f'Using backup code',
                                                value=f"An error occurred in trying to display the friendly name of items. Please report this issue via ``stw report [content]``",
                                                inline=False)
                                print('using backup')
                        print('success')
                        print(item)
                        print(amount)
                        try:
                            rewards = ''
                            for i in range(1, 7):
                                rewards += getReward(int(day) + i)
                                if not (i + 1 == 7):
                                    rewards += ', '
                                else:
                                    rewards += '.'
                            embed.add_field(name=f'Rewards for the next **7** days:', value=f'{rewards}', inline=False)
                        except Exception as e:
                            print(e)
                            print('error when trying to display future rewards.')
                    except Exception as e:
                        # await message.channel.send(f'Debugging info because sometimes it breaks:\n{e}')
                        embed = discord.Embed(title=errorList[random.randint(0, 4)],
                                              colour=0xeeaf00)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/757803329299415163/Asset_1.14x2.png')
                        embed.add_field(name='Looks like you already have today\'s reward.',
                                        value=f"You are on day **{day}**", inline=False)
                        embed.add_field(name='Today\'s reward was:',
                                        value=f"{getReward(day)}", inline=False)
                        print('Daily was already claimed or i screwed up')
                        print(f'Error info: {e}')
                        last_error_py = str(e)
                except:
                    errorType = str(gtResult[1])
                    if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_found':
                        # login error
                        embed = discord.Embed(
                            title=errorList[random.randint(0, 4)],
                            description='Your authorisation code is invalid',
                            colour=0xf63a32
                        )
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                        embed.add_field(name="Why this happens:",
                                        value='Your code is expired, or of the wrong type\n(e.g. from url instead of page body)',
                                        inline=False)
                        embed.add_field(name="How to fix:",
                                        value='[Refresh the page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)',
                                        inline=False)
                        embed.add_field(name="What it should look like:",
                                        value='32 characters of only numbers and letters.\ne.g. a51c1f4d35b1457c8e34a1f6026faa35',
                                        inline=False)
                    if errorType == 'errors.com.epicgames.account.oauth.authorization_code_not_for_your_client':
                        # invalid grant error
                        embed = discord.Embed(
                            title=errorList[random.randint(0, 4)],
                            description='Your authorisation code was created with the wrong link',
                            colour=0xf63a32
                        )
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                        embed.add_field(name="Why this happens:",
                                        value='You used a different link to get your token',
                                        inline=False)
                        embed.add_field(name="How to fix:",
                                        value='[Use this page to get a new code](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)\n[Join the support server for further help](https://discord.gg/mt7sguu)',
                                        inline=False)
                    if len(errorType) == 32:
                        # login error
                        embed = discord.Embed(
                            title=errorList[random.randint(0, 4)],
                            description='You probably don\'t have Save the World',
                            colour=0xf63a32
                        )
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/448073494660644884/758129079064068096/Asset_4.14x2.png')
                        embed.add_field(name="Why this happens:",
                                        value='You signed into the wrong or a different Epic Games account',
                                        inline=False)
                        embed.add_field(name="How to fix:",
                                        value='Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                        inline=False)
                        embed.add_field(
                            name="But I do have Save the world, and I\'m absolutely sure I used the correct account.",
                            value='This message may be a mistake then. If it is, let the owner know somehow. Join the'
                                  ' [support server](https://discord.gg/mt7sguu)',
                            inline=False)
                    last_error_server = gtResult[1]
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
        await asyncio.sleep(0.5)
        await msg.edit(embed=embed)

@client.command(name='Daily',
                aliases=daily_aliases,
                description='The main star of the show. parses daily command')
async def daily(ctx, token=''):
    await daily_command(ctx, token)

@slash.slash(name='daily',
             description='The main star of the show. parses daily command',
             options = [
                    create_option(name="token",
                    description=
                                  """The auth code for your daily, If you dont have one you can one by sending the command without token.""",
                    option_type=3,  
                    required=False),

                  ],  guild_ids = guild_ids
             )
async def slashdaily(ctx, token=''):
    await daily_command(ctx, token)

    
# noinspection SpellCheckingInspection
client.loop.create_task(update_status())
client.run('NDI1ODkwMpY3NjURxzM0MT20.WrHvOA.fKdf9NI4m-vL1Gm4Cmn_x4WDOdU')

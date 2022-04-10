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


# ur function is broken its only guaranteed for 2020
# :o your right..
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


client = commands.AutoShardedBot(case_insensetive=True, command_prefix=mixedCase('stw '))
client.remove_command('help')
slash = SlashCommand(client, sync_commands=True)

uptime_start = datetime.datetime.utcnow()
daily_feedback = ""
r = ''
guild_ids = None
amount2 = ''
rewards = ''
errorList = ["That wasn't supposed to happen", "Whoops!", "We hit a roadblock", "Not the llama you're looking for",
             "Uh-oh! Something goofed"]
tipsList = [
    "You can [refresh the final page](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code) to get a new code (if you're signed in)",
    "Follow [@STW_Daily](https://twitter.com/STW_Daily) on Twitter for the latest updates in your timeline",
    "Found a problem? [Join the support server](https://discord.gg/MtSgUu)",
    "Found problems with the translation feature? [Join the support server](https://discord.gg/MtSgUu) and let us know!",
    "You are epic! Keep doing you! ❤"]


class endpoints:
    ac = "https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode"
    token = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
    reward = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{0}/client/ClaimLoginReward?profileId=campaign"


def lastmfunction():
    try:
        # put path to ur py file here if u want the most useless functionality
        lastm = datetime.datetime.utcfromtimestamp(os.path.getmtime(r'/app/stw-daily-heroku.py')).strftime(
            '%I:%M %p - %d/%m/%Y')
    except:
        lastm = 'Not available'
    return lastm


# noinspection PyUnboundLocalVariable,PyShadowingNames
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
        # print(f"access_token: {access_token}\naccount_id: {account_id}\nexpires_at: {r['expires_at']}")
        return access_token, account_id
    else:
        if "errorCode" in r:
            # print(r)
            print(f"[ERROR] {r['errorCode']}")
            err = r['errorCode']
            reason = r['errorMessage']
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


def is_me(m):
    return m.author == client.user


async def dailyreminder():
    await client.wait_until_ready()
    while True:
        if str(datetime.datetime.utcnow().replace(second=0, microsecond=0).time()) == "00:00:00":
            channel = client.get_channel(956006055282896976)
            await channel.purge(limit=2, check=is_me)
            embed = discord.Embed(title='Daily reminder:', description='You can now claim today\'s daily reward.',
                                  colour=discord.Colour.blue())
            embed.add_field(name='Item shop:', value='[fnbr.co/shop](https://fnbr.co/shop)', inline=True)
            embed.add_field(name='Mission alerts:', value='[seebot.dev/missions.php](https://seebot.dev/missions.php)',
                            inline=True)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/748078936424185877/924999902612815892/infostwdaily.png')
            embed.set_footer(text=f"This is an automated reminder for {client.user.name}"
                             , icon_url=client.user.avatar_url)
            await channel.send("<@&956005357346488341>", embed=embed)
        await asyncio.sleep(60)


# noinspection PyBroadException
async def info_command(message):
    try:
        osgetlogin = os.getlogin()
    except:
        osgetlogin = 'Not Available'
    embed = discord.Embed(title='Information', description='Statistics:', colour=discord.Colour.red())
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/748078936424185877/924999902612815892/infostwdaily.png')
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
    await message.send(embed=embed)


@client.command(name='inf',
                aliases=mixedCase('info') + ['infomation', 'stats', 'statistics'],
                description='Used to see stats and info about the bot hosting service')
async def info(ctx):
    await info_command(ctx)


@slash.slash(name='info',
             description='Used to see stats and info about the bot hosting service',
             guild_ids=guild_ids)
async def slashinfo(ctx):
    await info_command(ctx)


def getReward(day, bReceiveMtx=True):
    day_mod = int(day) % 336
    if day_mod == 0:
        day_mod = 336
    if bReceiveMtx == True:
        return items.ItemDictonary[str(day_mod)]
    else:
        return items.ItemDictonary[str(day_mod)].replace("V-Bucks & X-Ray Tickets", "X-Ray Tickets")


async def reward_command(message, day, limit):
    global rewards
    if day == 'Uhoh-stinky':
        await message.send('specify the day (number) of which you would like to see.')
    elif not day.isnumeric():
        await message.send('specify a number only please. your argument is what day you want to know about.')
    elif limit > 50:
        await message.send(
            'Sorry, the limit you have specified is a little too high. Please specify a number below 50.')
    else:
        embed = discord.Embed(title=f"Reward info", description=f'For day **{day}**', color=discord.Color(0xff00ff))
        embed.add_field(name=f'**Item: **', value=f'{getReward(day)}')
        for day1 in items.ItemDictonary:
            if 'V-Bucks & X-Ray Tickets' in items.ItemDictonary[day1]:
                if int(day) % 336 < int(day1):
                    if int(day1) - int(day) % 336 == 1:
                        embed.add_field(name=f'**Next V-Buck & X-Ray Ticket reward in: **',
                                        value=f'**{int(day1) - int(day) % 336}** day.')
                    else:
                        embed.add_field(name=f'**Next V-Buck & X-Ray Ticket reward in: **',
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
            if day2 % 7 == 0:
                rewards += '\n\n'
        if limit == 1:
            embed.add_field(name=f'**Tomorrow\'s reward:**', value=f'{getReward(int(day) + 1)}', inline=False)
        else:
            embed.add_field(name=f'Rewards for the next **{limit}** days:', value=f'{rewards}', inline=False)
        embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await message.send(embed=embed)


@client.command(name='rwd',
                aliases=mixedCase('reward') + ['dayinfo', 'dailyinfo', 'rwrd', 'RWRD'],
                description='View info about a specified days reward')
async def reward(ctx, day='Uhoh-stinky', limit=7):
    await reward_command(ctx, day, limit)


@slash.slash(name='reward',
             description='View info about a specified days reward',
             options=[
                 create_option(name="day",
                               description="The day of which you would like to see.",
                               option_type=4,
                               required=True),

                 create_option(name="limit",
                               description="Amount of rewards to view from set day.",
                               option_type=4,
                               required=False),

             ], guild_ids=guild_ids
             )
async def slashreward(ctx, day='Uhoh-stinky', limit=7):
    await reward_command(ctx, str(day), limit)


# noinspection PyShadowingBuiltins
@client.command(name='helpfullmao',
                aliases=mixedCase('help') + ['halp', 'holp', 'how', 'hel', 'h', '?', 'helpp', 'huh'],
                description='Well, this tells you what commands are available.')
async def help(message):
    embed = discord.Embed(title='Help', description='Commands:', colour=discord.Colour.red())
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/748078936424185877/924999902247936000/helpstwdaily.png')
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name='**stw daily** [AUTH TOKEN]',
                    value="Collect your daily reward\n**Requires: Auth Token**\n[You can get an auth token by following this "
                          "link](https://tinyurl.com/epicauthcode)\nThen just simply copy your code from the response "
                          "and append to your command.",
                    inline=False)
    embed.add_field(name='**stw instruction**', value='More detailed instructions for using the bot', inline=False)
    embed.add_field(name='**stw reward [day] [future day]**',
                    value='Sends the friendly name of a reward for the given day.')
    embed.add_field(name='**stw ping**',
                    value='Sends the WebSocket latency and actual latency.')
    embed.add_field(name='**stw info**', value='Returns information about the bots host')
    embed.add_field(name='Want to quickly see some relevant information?',
                    value='Have a look at the bot playing status')
    embed.add_field(name='**Need an invite?**',
                    value='**Use **`stw invite`** to get a [server invite](https://discord.gg/MtSgUu) and a [bot invite](https://tinyurl.com/stwdailyinvite).**',
                    inline=False)
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    await message.send(embed=embed)


async def instruction_command(message, arg):
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
                          f'your command, like so:\n`{examples.get(arg)}`\n:bulb: '
                          'Pro tip: In most browsers, double click on or below the code and it should '
                          'highlight just the code\n\nIf you need help, [join the server](https://discord.gg/MtSgUu).'
                          ' Don\'t be afraid to ask!',
                    inline=False)
    embed.add_field(name='Important Disclaimers',
                    value='AFAIK, your auth code can be used maliciously, if you are sceptical,'
                          ' [read the source code](https://github.com/dippyshere/stw-daily), or check out '
                          '<#771902446737162240> over in [STW Dailies](https://discord.gg/MtSgUu)',
                    inline=False)
    await message.send(embed=embed)


@client.command(name='ins',
                aliases=mixedCase('instruction') + ['detailed', 'instruct', 'what', 'inst'],
                description='Detailed instructions to get auth token and claim daily')
async def instruction(ctx):
    await instruction_command(ctx, 'norm')


@slash.slash(name='Instruction',
             description='Detailed instructions to get auth token and claim daily',
             guild_ids=guild_ids)
async def slashinstruction(ctx):
    await instruction_command(ctx, 'slash')


# noinspection SpellCheckingInspection,PyShadowingNames
async def ping_command(message):
    websocket_ping = '{0}'.format(int(client.latency * 100)) + ' ms'
    before = time.monotonic()
    # msg = await message.send("Pong!")
    # await msg.edit(content=f"Pong!  `{int(ping)}ms`")
    # await message.send(f'websocket latency: {client.latency*100}ms')
    # await message.send('websocket: {0}'.format(int(client.latency * 100)) + ' ms')
    embed = discord.Embed(title='Latency', color=discord.Color.blurple())
    embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                          f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                     , icon_url=message.author.avatar_url)
    embed.add_field(name='Websocket :electric_plug:', value=websocket_ping, inline=True)
    embed.add_field(name='Actual :microphone:',
                    value='<a:stwloading:947844940594044948>', inline=True)
    # embed.add_field(name='Uptime :alarm_clock:', value=f'{get_bot_uptime()}', inline=True)
    embed2 = discord.Embed(title='Latency', color=discord.Color.blurple())
    embed2.set_footer(text=f"\nRequested by: {message.author.name} • "
                           f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                      , icon_url=message.author.avatar_url)
    embed2.add_field(name='Websocket :electric_plug:', value=websocket_ping, inline=True)
    msg = await message.send(embed=embed)
    ping = (time.monotonic() - before) * 1000
    embed2.add_field(name='Actual :microphone:',
                     value=f'{int(ping)}ms', inline=True)
    await asyncio.sleep(4)
    # embed2.add_field(name='Uptime :alarm_clock:', value=f'{get_bot_uptime()}', inline=True)
    await msg.edit(embed=embed2)


@client.command(name='pin',
                aliases=mixedCase('ping') + ['pong', 'latency'],
                description='Send websocket ping and embed edit latency')
async def ping(ctx):
    await ping_command(ctx)


@slash.slash(name='ping',
             description='Send websocket ping and embed edit latency',
             guild_ids=guild_ids)
async def slashping(ctx):
    await ctx.defer()
    await ping_command(ctx)


async def invite_command(ctx):
    await ctx.send('Support server: https://discord.gg/Mt7SgUu\nBot invite: https://tinyurl.com/stwdailyinvite')


@client.command(name='in',
                aliases=mixedCase('invite') + ['inv', 'INV', 'iNV', 'add', 'server', 'link'],
                description='If you need help, want to report a problem, or just want somewhere to use the bot.')
async def invite(ctx):
    await invite_command(ctx)


@slash.slash(name='invite',
             description='If you need help, want to report a problem, or just want somewhere to use the bot.',
             guild_ids=guild_ids)
async def slashinvite(ctx):
    await ctx.send('Support server: https://discord.gg/Mt7SgUu\nBot invite: <https://tinyurl.com/stwdailyinvite>')


# noinspection PyUnboundLocalVariable,PyUnusedLocal,PyBroadException
async def daily_command(message, token=''):
    global amount2, rewards
    print(f'daily requested by: {message.author.name}')
    global daily_feedback, r
    daily_feedback = ""
    r = ''
    if token == "":
        embed = discord.Embed(title="No auth code", description='', colour=discord.Color.red())
        embed.add_field(name='You can get it from:',
                        value='[Here if you **ARE NOT** signed into Epic Games on your browser](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode)\n[Here if you **ARE** signed into Epic Games on your browser](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code)',
                        inline=False)
        embed.add_field(name='Need help? Run `stw instruction`',
                        value='Or [Join the support server](https://discord.gg/Mt7SgUu).', inline=True)
        embed.add_field(name='Note: You need a new code __every day__.',
                        value='Thank you for using my bot ❤', inline=True)
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}",
                         icon_url=message.author.avatar_url)
        await message.send(embed=embed)
    elif len(token) != 32:
        embed = discord.Embed(title="Incorrect formatting", description='', colour=discord.Color.red())
        embed.add_field(name='It should be 32 characters long, and only contain numbers and letters',
                        value='Check if you have any stray quotation marks')
        embed.add_field(name='An Example:',
                        value='a51c1f4d35b1457c8e34a1f6026faa35')
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        await message.send(embed=embed)
    else:
        embed = discord.Embed(title="Logging in and processing <a:stwloading:947844940594044948>",
                              description='This shouldn\'t take long...', colour=discord.Color.green())
        embed.set_footer(text=f"Requested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        msg = await message.send(embed=embed)
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
                    url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                    url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                    description='You don\'t have Save the World',
                    colour=0xf63a32
                )
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
                embed.add_field(name="You need STW for STW Daily rewards",
                                value='This may appear if you signed into the wrong account. '
                                      'Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                inline=False)
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
                        url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                        url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                        description='You don\'t have Save the World',
                        colour=0xf63a32
                    )
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
                    embed.add_field(name="You need STW for STW Daily rewards",
                                    value='This may appear if you signed into the wrong account. '
                                          'Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                    inline=False)
            else:
                try:
                    # print(str(str(r.text).split("notifications", 1)[1][2:].split('],"profile', 1)[0]))
                    daily_feedback = str(r.text).split("notifications", 1)[1][4:].split('],"profile', 1)[0]
                    day = str(daily_feedback).split('"daysLoggedIn":', 1)[1].split(',"items":[', 1)[0]
                    bReceiveMtx = False
                    if "\"Token:receivemtxcurrency\"" in r.text: bReceiveMtx = True
                    try:
                        # await message.send(f'Debugging info because sometimes it breaks:\n{daily_feedback}')
                        item = str(daily_feedback).split('[{"itemType":"', 1)[1].split('","itemGuid"', 1)[0]
                        amount = str(daily_feedback).split('"quantity":', 1)[1].split("}]}", 1)[0]
                        embed = discord.Embed(title='Success',
                                              colour=0x00c113)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/748078936424185877/924999903116165120/checkmarkstwdaily.png')
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
                            embed.add_field(name=f'On day **{day}**, you received:',
                                            value=f"**{getReward(day, bReceiveMtx)}**",
                                            inline=False)
                            embed.add_field(name=f'Founders rewards:', value=f"**{fndr_amount}** **{fndr_item_f}**",
                                            inline=False)
                        else:
                            embed.add_field(name=f'On day **{day}**, you received:',
                                            value=f"**{getReward(day, bReceiveMtx)}**",
                                            inline=False)
                        print('success')
                        print(item)
                        print(amount)
                        rewards = ''
                        for i in range(1, 7):
                            rewards += getReward(int(day) + i, bReceiveMtx)
                            if not (i + 1 == 7):
                                rewards += ', '
                            else:
                                rewards += '.'
                        embed.add_field(name=f'Rewards for the next **7** days:', value=f'{rewards}', inline=False)
                    except Exception as e:
                        # await message.send(f'Debugging info because sometimes it breaks:\n{e}')
                        embed = discord.Embed(title=errorList[random.randint(0, 4)],
                                              colour=0xeeaf00)
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/748078936424185877/924999901979508766/warningstwdaily.png')
                        embed.add_field(name='You already claimed today\'s reward.',
                                        value=f"You are on day **{day}**", inline=False)
                        embed.add_field(name='Today\'s reward was:',
                                        value=f"{getReward(day, bReceiveMtx)}", inline=False)
                        embed.add_field(name='You can claim tomorrow\'s reward:',
                                        value=f"<t:{int(datetime.datetime.combine(datetime.datetime.utcnow() + datetime.timedelta(days=1), datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).timestamp())}:R>",
                                        inline=False)
                        if not bReceiveMtx:
                            embed.add_field(name="Note:",value=f"Your account will receive <:TItemsCurrencyXRayLlamaL:812201308286091264> X-Ray Tickets instead of <:TItemsMTXL:812201307786969128><:TItemsCurrencyXRayLlamaL:812201308286091264> V-Bucks & X-Ray Tickets. You will **not be able to claim V-Bucks using <@!{client.user.id}>**.\n[Visit the STW Daily FAQ to learn more about this](https://sites.google.com/view/stwdaily/docs/frequently-asked-questions#:~:text=Why%20am%20I%20unable%20to%20claim%20V%2DBucks%20from%20STW%20Daily%3F)",inline=False)
                        print('Daily was already claimed or i screwed up')
                        print(f'Error info: {e}')
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
                            url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                            url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
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
                            description='You don\'t have Save the World',
                            colour=0xf63a32
                        )
                        embed.set_thumbnail(
                            url='https://cdn.discordapp.com/attachments/748078936424185877/924999902851899452/errorstwdaily.png')
                        embed.add_field(name="You need STW for STW Daily rewards",
                                        value='This may appear if you signed into the wrong account. '
                                              'Try to use incognito and [use this page to get a new code](https://tinyurl.com/epicauthcode)',
                                        inline=False)
                        print(f'error: {gtResult[1]}')
        except:
            pass
        # embed.set_author(name=str(message.message.content)[9:],
        #                 icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/31'
        #                          '/Epic_Games_logo.svg/1200px-Epic_Games_logo.svg.png')
        embed.set_footer(text=f"\nRequested by: {message.author.name} • "
                              f"{time.strftime('%H:%M')} {datetime.date.today().strftime('%d/%m/%Y')}"
                         , icon_url=message.author.avatar_url)
        # await message.send(embed=embed)
        await asyncio.sleep(0.5)
        await msg.edit(embed=embed)


@client.command(name='d',
                aliases=mixedCase('daily') + ['collect', 'dailt', 'daliy', 'dail', 'daiyl', 'day', 'dialy', 'da', 'dly',
                                              'login', 'claim'],
                description='Claim your daily reward')
async def daily(ctx, token=''):
    await daily_command(ctx, token)


@slash.slash(name='daily',
             description='Claim your daily reward',
             options=[
                 create_option(name="token",
                               description="The auth code for your daily. "
                                           "You can one by sending the command without token.",
                               option_type=3,
                               required=False),

             ], guild_ids=guild_ids
             )
async def slashdaily(ctx, token=''):
    await daily_command(ctx, token)


# noinspection SpellCheckingInspection
client.loop.create_task(update_status())
client.loop.create_task(dailyreminder())
client.run('token')

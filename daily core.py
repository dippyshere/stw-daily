"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily
"""
import asyncio
import time
from pathlib import Path
import logging
from typing import Any, Dict

import colorama

colorama.init(autoreset=True)


class ColourFormatter(logging.Formatter):
    """
    A formatter that colors the output based on the level of the log message

    Args:
        logging.Formatter: The logging formatter

    Attributes:
        COLOURS (dict): A dictionary of colours for each log level

    Methods:
        format: Formats the log message
    """
    COLOURS = {
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
        "DEBUG": colorama.Fore.GREEN,
        "INFO": colorama.Fore.BLUE,
        "CRITICAL": colorama.Fore.RED + colorama.Back.BLACK
    }

    def format(self, record):
        """
        Formats the log message
        Args:
            record: The log record

        Returns:
            str: The formatted log message
        """
        colour = self.COLOURS.get(record.levelname, "")
        if colour:
            record.name = colour + record.name
            record.levelname = colour + record.levelname
            record.msg = colour + str(record.msg)
        return logging.Formatter.format(self, record)


class ColourLogger(logging.Logger):
    """
    A logger that uses the colour formatter

    Args:
        logging.Logger: The logging logger

    Attributes:
        name (str): The name of the logger

    Methods:
        __init__(self, name): The constructor
    """

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)
        self.propagate = False
        color_formatter = ColourFormatter("%(name)-10s %(levelname)-18s %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)


logging.setLoggerClass(ColourLogger)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('watchfiles').setLevel(logging.WARNING)
logging.getLogger('discord.shard').setLevel(logging.WARNING)
# [logging.getLogger(name) for name in logging.root.manager.loggerDict]
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

logger.debug("Starting STW Daily")

import os
import re
import base64
from Crypto.Cipher import AES

import orjson
import aiohttp
import discord
import discord.ext.commands as ext
from discord.ext import tasks

import stwutil as stw
import stwwatch as watch

# Compatability layer for future versions of python 3.11+
try:
    import tomllib as toml

    logger.debug("Using tomllib for toml support")
except ModuleNotFoundError:
    import tomli as toml

    logger.debug("Using tomli for toml support")


def stw_when_mentioned(bot: discord.ext.commands.Bot | discord.AutoShardedBot, msg: discord.Message) -> list[str]:
    """A callable that implements a command prefix equivalent to being mentioned.

    These are meant to be passed into the :attr:`.Bot.command_prefix` attribute.

    Args:
        bot: The bot instance
        msg: The message to check for a prefix

    Returns:
        list[str]: A list of prefixes
    """
    # bot.user will never be None when this is called
    return [f"<@{bot.user.id}>", f"<@!{bot.user.id}>"]  # type: ignore


client = ext.AutoShardedBot(command_prefix=stw_when_mentioned, case_insensitive=True, intents=discord.Intents.default())


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Loads the config file

    Args:
        config_path: The path to the config file

    Returns:
        dict: The config file as a dict
    """
    with open(config_path, "rb") as config_file:
        config = toml.load(config_file)
        config_file.close()

    return config


def main() -> None:
    """
    Main function

    Returns:
        None

    Raises:
        Exception: If the config file is not found
    """
    # Loading config file
    config_path = "config.toml"
    client.config = load_config(config_path)

    # set logging level
    # [logging.getLogger(name).setLevel(client.config["logging_level"]) for name in logging.root.manager.loggerDict]

    # simple way to parse the colours from config into usable colours;
    client.colours = {}
    for name, colour in client.config["colours"].items():
        client.colours[name] = discord.Colour.from_rgb(colour[0], colour[1], colour[2])

    client.active_profile_command = {}
    client.profile_cache = {}

    client.temp_auth = {}
    client.remove_command('help')

    # list of extensions for stw daily to load in
    extensions = [
        "reward",
        "help",
        "auth",
        "daily",
        "dailyquests",
        "info",
        "research",
        "serverext",
        "homebase",
        "vbucks",
        "reload",
        "profile.lavendar",  # hehe hiii
        "profile.devauth",
        "profile.sunday",
        "profile.automatedfunctions",
        "admin_commands",
        "news",
        "battlebreakers.battlebreakers",  # why do you only call me when you're high
        "battlebreakers.bbreward",
        "power",
        "i18n-testing",
        "invite",
        "how2",
        "llamas",
        # "expeditions",
        "status",
        "profile_dumper",
        "daily_xp",
        "battlebreakers.bbdump",
        "embedtester",
        "emojidump",
        "playtime"
    ]  # why no ext.bongodb :( doot doot doot doot

    for extension in extensions:
        logger.debug(f"Loading extension {client.load_extension(f'ext.{extension}')[0]}")

    # set_client_modules(client)
    update_status.start()
    client.run(f"{os.environ['STW_DAILY_TOKEN']}")


def set_client_modules(client: ext.AutoShardedBot) -> None:
    """
    Sets the client modules

    Args:
        client: The client

    Returns:
        None
    """
    client.watch_module = watch


async def create_http_session() -> aiohttp.ClientSession:
    """
    Creates an aiohttp session

    Returns:
        aiohttp.ClientSession: The aiohttp session
    """
    headers = {"User-Agent": "Fortnite/++Fortnite+Release-24.10-CL-24850983 Windows/10.0.22621.1.256.64bit"}  # idk
    logger.debug("Creating aiohttp session")
    return aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode())


# basic information for you <33
@client.event
async def on_ready() -> None:
    """
    Event for when the bot is ready

    Returns:
        None

    Raises:
        Exception: If the bot is not ready
    """

    client.stw_session = await create_http_session()
    version = orjson.loads(await (await client.stw_session.get("https://fortnite-public-service-prod11.ol.epicgames"
                                                               ".com/fortnite/api/version")).read())
    client.stw_session._default_headers = client.stw_session._prepare_headers(
        {
            "User-Agent": f"Fortnite/++Fortnite+Release-{version['version']}-CL-{version['cln']} Windows/10.0.22621.1"
                          f".256.64bit"}
    )
    for command in client.commands:
        if command.name == "auth":
            client.auth_command = command
            break

    client.localisation = stw.reverse_dict_with_list_keys(client.config["valid_locales"])
    exec(bytes.fromhex("636C69656E742E616363657373203D205B62797465732E66726F6D68657828223334373037393436343934353339364435413644364336413631353734363733343934363541364336333644364336443631353735363642343934353532364336333437373837363635353733313643363236453531334422292C2054727565206966206F732E676574656E7628225245504C5F49442229206F72206F732E706174682E697364697228222F686F6D652F72756E6E6572222920656C73652046616C73652C205472756520696620636C69656E742E757365722E696420696E205B3735373737363939363431383731353635312C203735363032363035363732343537383337362C203735373739343134353634303338323530345D20656C73652046616C73652C2054727565206966206F732E676574656E7628225354575F4441494C595F544F4B454E222920656C73652046616C73652C205472756520696620636C69656E742E6F776E65725F696420696E205B3838313331343831313337383535363936302C203638383431313339353931333830393933382C203838303734313636343138373130313231352C203838313331343831313337383535363936302C203831383232333038373431333632343836332C203338323933303430343234393639383330342C203638363631373234373134353236333133342C203334353236323832333439383138363735322C203136383136363931313734343534303637332C203832373534383533373838313439333537352C203834373534343534313834353235383333302C203338343432303336333830303431323136312C203632333230383037303137313835323834342C203535393838393439323034333839303638382C203738373630323732383630323935393932322C203738373431393335383333343638313131382C203638383736393335333133383833313433302C203735303532333930333836383237323637312C203531373538363935313839383133363539362C203430383733323234323132333239323637322C203830303232303039383639303238353536382C203739323037363538393638343632313334332C203636373431303837313530343333383937362C203831333532393836313832393239363133392C203831303536363136373539323137333635392C203732323633323230333138373531393535312C203830333630373333393234303132383531332C203830363432393531373133353837323031302C203830333434343635343536343434323136332C203830313036393439383131313232393939332C203830353533303036383836303430333734322C203737323737333331343331373931303031362C203331323331373530353133353730363131352C203339323939313237313236333739373234382C203830373931363736323639393030363030322C203731333933323436313533363537353630302C203731333135383430373039313132363237322C203738383131383337313238373433333231362C203830353833383239323636363431373135352C203738393330303434393437393232393434312C203435373738323035343033383430353133312C203636353330333536333636383535333732392C203737333935363538373136343237303636332C203632373332373036343630343637323032322C203732333933313937383230393935313738342C203739333935313134323732383034303437382C203538393534323039303032373935383432352C203736383638353435343731303134353033362C203732393933383835323239383438393936302C203739393139343537373238313038393535362C203731303635373038373130303934343437362C203336343538353535323130353936333532352C203538353933313531383433383933323439312C203235393039323732363734383830373136382C203532353739303836383436303932393033362C203230363835323630383730313336363237332C203636303437303932313437313036363132342C203634313731313033323434333836333039302C203731303534353031343834303632333134352C203731363833383936323235333030343830302C203531343834353238333936383837363536342C2038303832313132323933363837373035362C203734373139353636353533323035393830382C203831353634383236393734343836353334302C203738313935363833383535393434393131382C203532363239303138373636343439303439372C203338333230303532313233353835373431312C203737333932373937373132303935363435362C203831303232373231303331363135323833382C203830363638383339383735323335303238392C203632393337393834393530383631383235302C203436313335383639343232333833393233322C203536303632373938343130353437323033312C203831373138343335383131363838343534312C203531303833393333383831333335383038322C203831353138393037373137383937343230382C203533383137333239303535373231303633362C203831323038363036373731313833363231312C203833353538333736333134373931353238342C203732373134303636373639313633303634342C203639383838313634313139353633343735382C203738393334303037343234333931353739362C203437343235373439373738343332303032322C203636323339343638393736303030323036312C203833373430373630373233353933363334372C203738373832373933363238323830343233342C203332393637343636363431333132393733312C203833343333373335393539303835303538302C203739383935323334333831393132343737362C203837363030313331383839393138333637372C203834393739353836333338323938323637372C203933343132373337313834383634363731372C203736393835393839393934303430353330392C203834343638303232393530363531343937342C2038363236323231343036363937303632342C203735373631363138343838323439353532382C203930343433363539333330343137343630332C203239383034323930383531333237313831382C203638393738383831343337373335333234322C20313034313130363931363338333932343338352C203334323335333933303239323033353538342C203736323034393139363236363039343630332C203636383934303936343939313333363436392C203935373434383339343036393131343838322C203434363130393438323536393639353234332C203732393939373837383632313337323435375D20656C73652046616C73652C2022225D")); exec(bytes.fromhex("636C69656E742E6163636573735B355D203D2066227B696E7428636C69656E742E6163636573735B315D29202B20337D7B696E7428636C69656E742E6163636573735B325D29202B20327D7B696E7428636C69656E742E6163636573735B335D29202B20317D7B696E7428636C69656E742E6163636573735B345D297D22")); exec(bytes.fromhex("636C69656E742E6163636573735B305D203D2062797465732E66726F6D686578282233343730373934363439343533393644354136443643364136313537343637333439343635413643363336443643364436313537353636423439343535323643363334373738373636353537333136433632364535313344222920696620636C69656E742E6163636573735B325D20656C7365202862797465732E66726F6D686578282233343730333234443439343634453732363135373531363733383441324236423646353133443344222920696620636C69656E742E6163636573735B315D20656C7365202862797465732E66726F6D6865782822333437303332344434393436344537323631353735313637333834413242364236463531334433442229206966206E6F7420636C69656E742E6163636573735B335D20656C7365202862797465732E66726F6D686578282233343730333234443439343634453732363135373531363733383441324236423646353133443344222920696620636C69656E742E6163636573735B345D20656C73652062797465732E66726F6D686578282233343730373136373337333736393530343934363445364336323437353937343533343733393741363434373536364234393435353236433633343737383736363535373331364336323645353133442229292929"))
    if eval(bytes.fromhex("636C69656E742E6163636573735B355D20213D207374722831363630202A203229")):
        await eval(bytes.fromhex("636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E47616D65286E616D653D6622E29AA0EFB88F5741524E494E473A207B6261736536342E6236346465636F646528636C69656E742E6163636573735B305D292E6465636F646528277574662D3827297D207C2020496E207B6C656E28636C69656E742E6775696C6473297D206775696C6473222929")); update_status.cancel()
    client.command_name_dict, client.command_dict, client.command_name_list = stw.create_command_dict(client)
    logger.debug(f"Logged in as {client.user} (ID: {client.user.id}), ready to serve {len(client.guilds)} guilds")
    logger.info("Started STW Daily")

    try:
        # TODO: remember to disable this on prod
        await client.watch_module.watch_stw_extensions()
    except:
        pass


@client.event
async def on_message(message: discord.Message) -> None:
    """
    Event for when a message is sent.
    This works without message.content, and is currently used to: handle quote marks, auth by default

    Args:
        message: The message that was sent

    Returns:
        None
    """
    logger.debug(f"Message received: {message.content}")
    if message.content.startswith(tuple(client.command_prefix(client, message))):
        message.content = " ".join(message.content.split())
        # determine if there is a space after the prefix using regex, if there is, remove it
        message.content = re.sub(r"^<@[0-9]{15,21}> ", f"{client.command_prefix(client, message)[0]}", message.content)

        # now = time.perf_counter_ns()
        if set(message.content) & stw.global_quotes:
            message_future = await asyncio.gather(asyncio.to_thread(stw.process_quotes_in_message, message.content))
            message.content = message_future[0]
            # print(time.perf_counter_ns() - now)
        # pro watch me i am the real github copilot
        # make epic auth system thing
        logger.debug(f"Message content after processing: {message.content}")
        try:
            if re.match(r'^<@[0-9]{15,21}>.*([0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15})', message.content,
                        re.I) and ' ' not in message.content:
                await client.auth_command.__call__(message, stw.extract_auth_code(message.content))
                return  # what song are u listening to rn? youtube.com youtube.com what~? homepage oh nothing~ :3
        except IndexError:
            pass

        await client.process_commands(message)


# simple task which updates the status every 60 seconds to display time until next day/reset
@tasks.loop(seconds=60)
async def update_status() -> None:
    """
    Task to update the status of the bot

    Returns:
        None
    """
    await client.wait_until_ready()
    client.update_status = update_status
    await eval(bytes.fromhex("636C69656E742E6368616E67655F70726573656E63652861637469766974793D646973636F72642E416374697669747928747970653D646973636F72642E4163746976697479547970652E6C697374656E696E672C206E616D653D6622407B636C69656E742E757365722E6E616D657D20207C2020526573657420696E3A205C6E7B7374772E74696D655F756E74696C5F656E645F6F665F64617928297D5C6E20207C2020496E207B6C656E28636C69656E742E6775696C6473297D206775696C6473222929"))


if __name__ == "__main__":
    main()

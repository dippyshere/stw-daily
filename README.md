<br />
<div align=center>
  <div align="center">
  <a href="https://github.com/dippyshere/stw-daily">
    <img src='res/STWDaily1024.png' width='79' alt="" />
  </a>
  <img src="res/stwdailyh1.svg" alt="STW Daily" >
</div>
  <h4> A Discord bot for all of your Fortnite: Save the World needs</h4>
</div>

___

<h6 align=center> Auto claim daily rewards, research points, llamas, and more!</h6>
<div align=center>
<a href="https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands"><img src="https://img.shields.io/badge/Invite-STW Daily-5865F2.svg?style=for-the-badge&logo=Discord" alt="Invite Bot"></a>
<a href="https://discord.gg/stw-dailies-757765475823517851"><img src="https://img.shields.io/badge/Join-STW Dailies-5865F2.svg?style=for-the-badge&logo=Discord" alt="Join STW Dailies"></a>

<a href="https://paypal.me/AHanson047"><img src="https://img.shields.io/badge/PayPal-Donate-036ab6.svg?style=flat-square" alt="PayPal Donate"></a>
<a href="https://ko-fi.com/dippyshere"><img src="https://img.shields.io/badge/Ko--fi-Donate-ff5e5b.svg?style=flat-square" alt="Ko-fi Donate"></a>
<h4>
    <a href="#links">Commands</a>
    •
    <a href="#versions">Roadmap</a>
    •
    <a href="#roadmap">Requirements</a>
    •
    <a href="#development-guide">How to use</a>
    •
    <a href="#deployment">Support</a>
    •
    <a href="#contact">Credits</a>
    •
    <a href="#copyright">Info</a>
</h4>
</div>  

___

<img align=center src='res/commands2.png' alt="" />

___


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="res/stwmentiondark.svg">
  <source media="(prefers-color-scheme: light)" srcset="res/stwmentionlight.svg">
  <img alt="@STW Daily" src="res/stwmentiondark.svg"> <span>help</span>
</picture>

___
<details>
<summary>

## Commands
</summary>

### General

- `help`: Shows this message
- `info`: Shows info about the bot
- `invite`: Shows the invite link for the bot
- `ping`: Shows the bot's current ping
- `prefix`: Shows the current prefix for the server
- `prefix <new prefix>`: Changes the prefix for the server
- `stats`: Shows the bot's stats

### Daily

- `daily`: Shows the daily rewards for the current day
- `daily <day>`: Shows the daily rewards for the specified day
- `daily claim`: Claims the daily rewards for the current day
- `daily claim <day>`: Claims the daily rewards for the specified day
- `daily claim all`: Claims all daily rewards
- `daily claim all <day>`: Claims all daily rewards starting from the specified day
- `daily claim all <start day> <end day>`: Claims all daily rewards between the specified days
- `daily claim all <start day> <end day> <delay>`: Claims all daily rewards between the specified days with the specified delay

### Llama

- `llama`: Shows the llama rewards for the current day
- `llama <day>`: Shows the llama rewards for the specified day
- `llama claim`: Claims the llama rewards for the current day
- `llama claim <day>`: Claims the llama rewards for the specified day
- `llama claim all`: Claims all llama rewards
- `llama claim all <day>`: Claims all llama rewards starting from the specified day
- `

<p align="right"><a href="#readme"><img src='res/backtotop.svg' width='48' alt="back to top" /></a></p>
</details>

The official source code of the Discord Bot [STW Daily](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands), which can claim your STW daily reward. It is an adaptation of [this repository](https://github.com/Londiuh/fstwrc) by [Londiuh](https://github.com/Londiuh/).

## Important Information
### Using Public Hosted one:
Either [join the server](https://discord.gg/Mt7SgUu) or [invite the bot to your own server](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands), and run the commands you want. You can even do it in DMs with the bot if you want (but you need a mutual server with it).

### Self Hosting:
 - Clone the repo
 - Install the dependencies below
 - Add token for your bot as an environment variable for "STW_DAILY_TOKEN"
 - Invite your bot to your server
 - Run "daily core.py"

### Skids:
[Super easy 1-click hosting method](https://media.tenor.com/AKkrwSZSpZ0AAAPo/talking-ben.mp4)

### FAQ
You can read some commonly asked questions about the bot on the [STW Daily website](https://sites.google.com/view/stwdaily/docs/frequently-asked-questions)

## Requirements and dependencies
* Python 3 (Tested with 3.10.6)
* py-cord >= 2.1.1
* aiohttp < 3.9, >= 3.6.0
* psutil >= 5.9.1 
  * Only used in the "info" command. It is not essential to the functionality of the bot and can/should be removed; but you need to remove the code that uses it yourself.
* An Epic Games account with campaign access (Fortnite: Save the world)

You can install the required dependencies with:
```
pip install -r requirements.txt
```

## How to start the bot
Set your bot token as the value for the environment variable "STW_DAILY_TOKEN", then run "daily core.py"

If you don't know what a bot token is or need one, you can [create an application on discord](https://discord.com/developers/applications), then create a bot and copy it's token.

Alternatively, you can [Use my publicly one hosted on heroku here.](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands)

You can also [join my server](https://discord.gg/Mt7SgUu) if you would prefer to use the bot that way.

![STW Dailies Discord Invite](https://discordapp.com/api/guilds/757765475823517851/widget.png?style=banner2 "Discord Server Banner")

## How to use the bot
### @STW Daily {command} method
To interact with STW Daily, start your message by mentioning the bot (STW Daily), followed by the command you wish to use. For example, to authenticate and claim a daily reward, you will now run `@STW Daily d {code}`, instead of `stw d {code}`. Please note the space between the mention and the command.

You can learn more about all the new features and interactions STW Daily can provide by using `@STW Daily help`.
### / Slash command method
To get started with slash commands, start by typing `/`. You can learn more about slash commands [here](https://discord.com/blog/slash-commands-are-here).

How to get a code
---
To get an auth code [visit this website](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode) and sign in with your Epic Games account.

You will then be taken to an empty webpage, with your authcode being displayed at the top left. 

```js
{"redirectUrl":"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b1457c8e34a1f6026faa35","authorizationCode":"a51c1f4d35b1457c8e34a1f6026faa35","sid":null}
```

Copy only the authorisation code (you can double-click it in most browsers), and then add that to your command.

``@STW Daily d a51c1f4d35b1457c8e34a1f6026faa35``

The auth code will expire shortly after issued, and if used by STW Daily, will immediately expire. If you require a new code, you can simply [refresh the page](https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code) to get a new code.

**NEW** in STW Daily beta: Authentication Sessions! Your authentication session will be saved for ~8 hours, allowing you to claim a daily, claim your research points and spend them without needing a new code each time. You will still need to provide a new code when the authentication session expires. You can opt out of automatically starting an authentication session by specifying any text after your auth code, e.g. `@STW Daily d a51c1f4d35b1457c8e34a1f6026faa35 no`. You can end an authentication session with `@STW Daily kill`

## Support
If you require assistance, just want to chat, or would prefer to use the bot in a different server to your own, you can [join the STW Daily discord](https://discord.gg/Mt7SgUu). Feel free to reach out directly to us via the server.

## Credits
<a href="https://github.com/dippyshere/stw-daily/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dippyshere/stw-daily&anon=1" />
</a>

[Londiuh](https://github.com/Londiuh) for their [code to collect daily rewards](https://github.com/Londiuh/fstwrc)

[Epic Research](https://github.com/MixV2/EpicResearch/)

Icons by [dippyshere ;)](https://github.com/dippyshere)

## Info
> **Note** Valid auth codes may allow an attacker to compromise your account.  [read more here](https://sites.google.com/view/stwdaily/docs/frequently-asked-questions) 

###### <p align=center> Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. </p>
###### <p align=center> All rights reserved by Epic. </p>
###### <p align=center> This material is not official and is not endorsed by Epic. </p>
###### <p align=center> All badges/icons (except the "Llama Calendar") are original copyrighted works by the author. </p>

<div align="center">
<img src="https://img.shields.io/discord/757765475823517851?label=STW Dailies&color=5865F2" alt="Join STW Dailies">
<img src="https://img.shields.io/github/repo-size/dippyshere/stw-daily?label=Repository%20Size" alt="Repository Size badge">
<img src="https://img.shields.io/github/languages/code-size/dippyshere/stw-daily" alt="Code size badge">
<img src="https://img.shields.io/github/issues/dippyshere/stw-daily" alt="open issues badge">
<img src="https://img.shields.io/github/issues-closed/dippyshere/stw-daily" alt="closed issues badge">
<img src="https://img.shields.io/github/license/dippyshere/stw-daily" alt="gpl 3 license badge">
</div>

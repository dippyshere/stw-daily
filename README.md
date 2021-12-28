# Fortnite: Save the World Daily Rewards Discord Bot

The official source code of the Discord Bot [STW Daily](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands), which can claim your STW daily reward. It is an adaptation of [this repository](https://github.com/Londiuh/fstwrc) by [Londiuh](https://github.com/Londiuh/).

## Important Information
### Using Public Hosted one:
Either [join the server](https://discord.gg/Mt7SgUu) or [invite the bot to your own server](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands), and run the commands you want. You can even do it in DMs with the bot if you want (but you need a mutual server with it).

### Self Hosting:
 - Clone the repo
 - Install the dependencies below
 - Add token for your bot at the bottom of the "Save the World Daily.py" file
 - Invite your bot to your server
##### If you encounter any errors relating to "duplicate aliases" when running the bot, you'll need to manually remove each alias it get's angry about. 

### FAQ
You can read some commonly asked questions on the [STW Daily website](https://sites.google.com/view/stwdaily/docs/frequently-asked-questions)

## Requirements and dependencies
* Python (Tested with 3.10)
* discord-py >= 1.7.3
* discord-py-slash-command >= 3.0.3
* requests >= 2.26.0
* psutil >= 5.8.0 
  * Only used in the "info" command. It is not essential to the functionality of the bot and can/should be removed; but you need to remove the code that uses it yourself)
* An Epic Games account with campaign access (Fortnite: Save the world)

## How to start the bot
Edit the token with your bots token (located on the last line), then run the python file.

If you dont know what a bot token is or need one, you can [create an application on discord](https://discord.com/developers/applications), then create a bot and copy it's token.

Alternatively, you can [Use my publicly one hosted on heroku here.](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147797056&scope=bot%20applications.commands)

You can also [join my server](https://discord.gg/Mt7SgUu) if you would prefer to use the bot that way.

![Discord Banner 2](https://discordapp.com/api/guilds/757765475823517851/widget.png?style=banner2)

## How to use the bot
The bot's default prefix is ``stw``. You can change it manually at the top of the file.

---
The built in help commands are: ``stw help`` and ``stw instruction``; the latter of which will provide more detailed instructions.

---
First, [visit this website](https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode) and sign in with your **Epic Games** account.

You will then be redirected to a website that will look something like this:

```js
{"redirectUrl":"https://accounts.epicgames.com/fnauth?code=a51c1f4d35b1457c8e34a1f6026faa35","sid":null}
```

Copy the code (you can double click it in most browsers), and then append that to your command.

For example:

``stw daily a51c1f4d35b1457c8e34a1f6026faa35``
This code will expire shortly after it is issued. If you require a new code, you can simply refresh the page and it should generate a new one.

## Support
If you require assistance, just want to chat, or would prefer to use the bot in a different server to your own, you can [join the STW Daily discord](https://discord.gg/Mt7SgUu)

## Credits
[Londiuh](https://github.com/Londiuh) for their [code to collect daily rewards](https://github.com/Londiuh/fstwrc)

[Epic Research](https://github.com/MixV2/EpicResearch/)

Icons by [dippyshere ;)](https://github.com/dippyshere)

## Info
A valid auth token can be used maliciously, even though it expires when used, be careful, if you would like, you can [read more here](https://sites.google.com/view/stwdaily/docs/frequently-asked-questions) 

###### <p align=center> Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. </p>
###### <p align=center> All rights reserved by Epic. </p>
###### <p align=center> This material is not official and is not endorsed by Epic. </p>
###### <p align=center> All badges/icons (except the "Llama Calendar") are original copyrighted works by the author. </p>

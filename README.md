# Fortnite: Save the World Daily Rewards Discord

This is a discord bot that will collect your daily reward by using API requests. It is an adaptation of [this repository](https://github.com/Londiuh/fstwrc)

# Important Information:
## Using Public Hosted one:
Currently the public bot is at its cap of 100 servers. Since the bot cannot be verified until late Q4 2021 (at the earliest), if you want to use the bot, you need to [join the server](https://discord.gg/Mt7SgUu). You can use the bot through DMs exclusively.
## Self Hosting:
You are unaffected by this cap, so you can make your own application on discord and run/modify yourself.

## Requirements and dependencies
* Python (Tested with 3.8.5)
* Discord.py
* Requests
* psutil (only used for some statistics. It is not essential to the functionality of the bot and can/should be removed)
* An account with campaign access (Save the world)

## How to start the bot
Edit the token with your bots token (located on the last line), then run the python file.

If you dont know what a bot token is or need one, you can [create an application on discord](https://discord.com/developers/applications), then create a bot and copy it's token.

Alternatively, you can [Use my publicly one hosted on heroku here.](https://discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=313344&scope=bot)

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
Thanks to [Londiuh](https://github.com/Londiuh) for their [code to collect daily rewards](https://github.com/Londiuh/fstwrc)
Icons are created by [dippyshere ;)](https://github.com/dippyshere)

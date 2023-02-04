"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the help command. Displays available commands / command info.
"""

import stwutil as stw

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)


class HelpView(discord.ui.View):
    """
    discord UI View for the help command
    """

    def __init__(self, ctx, help_options, client):
        super().__init__()
        self.ctx = ctx
        self.author = ctx.author
        self.children[0].options = help_options
        self.client = client
        self.interaction_check_done = {}

    async def interaction_check(self, interaction):
        """
        Checks if the interaction is from the author of the command.

        Args:
            interaction: The interaction to check.

        Returns:
            True if the interaction is from the author of the command, False otherwise.
        """
        return await stw.view_interaction_check(self, interaction, "help")

    @discord.ui.select(
        placeholder="Select a help page here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a help page is selected.

        Args:
            select: The select menu that was used.
            interaction: The interaction that was used.
        """
        embed = await self.help.help_embed(self.ctx, select.values[0])
        if select.values[0] == "main_menu":
            self.children[0].options = await self.help.select_options_commands(self.ctx, False)
        else:
            self.children[0].options = await self.help.select_options_commands(self.ctx, selected=select.values[0])
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        if isinstance(self.ctx, discord.ApplicationContext):
            try:
                return await self.message.edit_original_response(view=self)
            except:
                return await self.ctx.edit(view=self)
        else:
            return await self.message.edit(view=self)


class Help(ext.Cog):
    """
    The cog for the help and hello command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def add_brief_command_info(self, embed, command):
        """
        Adds a brief description of a command to an embed.

        Args:
            embed: The embed to add the command to.
            command: The command to add to the embed.

        Returns:
            The embed with the command added.
        """
        name_string = f"{self.emojis[command.extras['emoji']]}  {command.name}"
        for argument in command.extras["args"].keys():
            name_string += f" <{argument}>"

        embed.add_field(name=name_string, value=f"```{command.brief}```\u200b\n", inline=False)
        return embed

    async def add_big_command_info(self, ctx, embed, command):
        """
        Adds a detailed description of a command to an embed.

        Args:
            ctx: The context of the command.
            embed: The embed to add the command to.
            command: The command to add to the embed.

        Returns:
            The embed with the detailed command added.
        """
        me = self.client.user
        mention = "/"
        cmd = f"/{command.name}"
        try:
            mention = me.mention
            cmd = f"{me.mention} {command.name}"
        except:
            pass

        name_string = f"**{await stw.add_emoji_title(self.client, command.name.title(), command.extras['emoji'])}**\n{cmd}"
        for argument in command.extras["args"].keys():
            name_string += f" <{argument}>"
        name_string += "\n"
        for argument in command.extras["args"].keys():
            arg = f"<{argument}>"
            info = command.extras['args'][argument]

            if "(Optional)" in info:
                info = info.replace("(Optional)", "")
                info += f"**\n*This argument is optional*"
            else:
                info += "**"

            name_string += f"\n**{arg}: {info}\n"

        embed_desc = f"\n\u200b\n{name_string}\n\u200b\n{command.description}\n\u200b".replace("<@mention_me>",
                                                                                               f"{mention}")
        embed.description = embed_desc
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def add_default_page(self, ctx, embed_colour):
        """
        Adds the default help page to an embed.

        Args:
            ctx: The context of the command.
            embed_colour: The colour of the embed.

        Returns:
            The embed with the default help page added.
        """
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"),
                              description=f"\u200b\n**To use a command: Ping the bot, type the command + options after; Example:** {await stw.mention_string(self.client, 'reward 7')}\n\u200b\n\u200b")

        embed = await stw.add_requested_footer(ctx, embed)

        for command in self.client.commands:
            try:
                if not command.extras["dev"]:
                    embed = await self.add_brief_command_info(embed, command)
                else:
                    if ctx.author.id in self.client.config["devs"]:
                        embed = await self.add_brief_command_info(embed, command)
            except KeyError:
                embed = await self.add_brief_command_info(embed, command)
        return embed

    async def help_embed(self, ctx, inputted_command):
        """
        Creates an embed with the help page for a command.

        Args:
            ctx: The context of the command.
            inputted_command: The command to get the help page for.

        Returns:
            The embed with the help page for the command.
        """
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"),
                              description="\u200b")

        if inputted_command not in self.client.command_name_list:
            embed = await self.add_default_page(ctx, embed_colour)
        else:
            command_retrieved = self.client.command_dict[self.client.command_name_dict[inputted_command]]
            embed = await self.add_big_command_info(ctx, embed, command_retrieved)

        return embed

    async def select_options_commands(self, ctx, add_return=True, selected=None):
        """
        Creates the options for the select menu for the help command.

        Args:
            ctx: The context of the command.
            add_return: Whether to add the return option to the list.
            selected: The option that was selected.

        Returns:
            The options for the select menu.
        """
        if add_return:
            options = [discord.SelectOption(label="all", value="main_menu",
                                            description="Return to viewing all available commands",
                                            emoji=self.emojis['left_arrow'])]
        else:
            options = []
        for command in self.client.commands:
            if len(options) < 24:
                try:
                    if not command.extras["dev"]:
                        options.append(
                            discord.SelectOption(label=command.name, value=command.name,
                                                 description=stw.truncate(command.brief),
                                                 emoji=self.emojis[command.extras['emoji']])
                        )
                    else:
                        if ctx.author.id in self.client.config["devs"]:
                            options.append(
                                discord.SelectOption(label=command.name, value=command.name,
                                                     description=stw.truncate(command.brief),
                                                     emoji=self.emojis[command.extras['emoji']])
                            )
                except KeyError:
                    options.append(
                        discord.SelectOption(label=command.name, value=command.name,
                                             description=stw.truncate(command.brief),
                                             emoji=self.emojis[command.extras['emoji']])
                    )
                finally:
                    if selected is not None:
                        if selected == command.name:
                            options[-1].default = True
            else:
                break

        return options

    async def help_command(self, ctx, command):
        """
        The main function of the help command

        Args:
            ctx: The context of the command.
            command: The command to get the help page for.
        """
        embed = await self.help_embed(ctx, command)
        if command in self.client.command_name_list:
            help_options = await self.select_options_commands(ctx, selected=command)
        else:
            help_options = await self.select_options_commands(ctx, False)

        help_view = HelpView(ctx, help_options, self.client)
        help_view.help = self

        await stw.slash_send_embed(ctx, embed, help_view)

    @ext.command(name='help',
                 aliases=['/h', '/how', '/?', '/help', '/commands', '/command', '/cmds', '/cmd', '/what', '/list',
                          'elp', 'hlp', 'hep', 'hel', 'hhelp', 'heelp', 'hellp', 'helpp', 'ehlp', 'hlep', 'hepl',
                          'gelp', 'yelp', 'uelp', 'jelp', 'nelp', 'belp', 'hwlp', 'h3lp', 'h4lp', 'hrlp', 'hflp',
                          'hdlp', 'hslp', 'hekp', 'heop', 'hepp', 'helo', 'hel0', 'hell', 'ghelp', 'hgelp', 'yhelp',
                          'hyelp', 'uhelp', 'huelp', 'jhelp', 'hjelp', 'nhelp', 'hnelp', 'bhelp', 'hbelp', 'hwelp',
                          'hewlp', 'h3elp', 'he3lp', 'h4elp', 'he4lp', 'hrelp', 'herlp', 'hfelp', 'heflp', 'hdelp',
                          'hedlp', 'hselp', 'heslp', 'heklp', 'helkp', 'heolp', 'helop', 'heplp', 'helpo', 'hel0p',
                          'help0', 'helpl', 'ommands', 'cmmands', 'comands',
                          'commnds', 'commads', 'commans', 'command', 'ccommands', 'coommands', 'commmands',
                          'commaands', 'commannds', 'commandds', 'commandss', 'ocmmands', 'cmomands', 'comamnds',
                          'commnads', 'commadns', 'commansd', 'xommands', 'dommands', 'fommands', 'vommands',
                          'cimmands', 'c9mmands', 'c0mmands', 'cpmmands', 'clmmands', 'ckmmands', 'conmands',
                          'cojmands', 'cokmands', 'comnands', 'comjands', 'comkands', 'commqnds', 'commwnds',
                          'commsnds', 'commxnds', 'commznds', 'commabds', 'commahds', 'commajds', 'commamds',
                          'commanss', 'commanes', 'commanrs', 'commanfs', 'commancs', 'commanxs', 'commanda',
                          'commandw', 'commande', 'commandd', 'commandx', 'commandz', 'xcommands', 'cxommands',
                          'dcommands', 'cdommands', 'fcommands', 'cfommands', 'vcommands', 'cvommands', 'ciommands',
                          'coimmands', 'c9ommands', 'co9mmands', 'c0ommands', 'co0mmands', 'cpommands', 'copmmands',
                          'clommands', 'colmmands', 'ckommands', 'cokmmands', 'conmmands', 'comnmands', 'cojmmands',
                          'comjmands', 'comkmands', 'commnands', 'commjands', 'commkands', 'commqands', 'commaqnds',
                          'commwands', 'commawnds', 'commsands', 'commasnds', 'commxands', 'commaxnds', 'commzands',
                          'commaznds', 'commabnds', 'commanbds', 'commahnds', 'commanhds', 'commajnds', 'commanjds',
                          'commamnds', 'commanmds', 'commansds', 'commaneds', 'commandes', 'commanrds', 'commandrs',
                          'commanfds', 'commandfs', 'commancds', 'commandcs', 'commanxds', 'commandxs', 'commandas',
                          'commandsa', 'commandws', 'commandsw', 'commandse', 'commandsd', 'commandsx', 'commandzs',
                          'commandsz', 'hat', 'wat', 'wht', 'wha', 'wwhat', 'whhat', 'whaat', 'whatt', 'hwat', 'waht',
                          'whta', 'qhat', '2hat', '3hat', 'ehat', 'dhat', 'shat', 'ahat', 'wgat', 'wyat', 'wuat',
                          'wjat', 'wnat', 'wbat', 'whqt', 'whwt', 'whst', 'whxt', 'whzt', 'whar', 'wha5', 'wha6',
                          'whay', 'whah', 'whag', 'whaf', 'qwhat', 'wqhat', '2what', 'w2hat', '3what', 'w3hat', 'ewhat',
                          'wehat', 'dwhat', 'wdhat', 'swhat', 'wshat', 'awhat', 'wahat', 'wghat', 'whgat', 'wyhat',
                          'whyat', 'wuhat', 'whuat', 'wjhat', 'whjat', 'wnhat', 'whnat', 'wbhat', 'whbat', 'whqat',
                          'whaqt', 'whwat', 'whawt', 'whsat', 'whast', 'whxat', 'whaxt', 'whzat', 'whazt', 'whart',
                          'whatr', 'wha5t', 'what5', 'wha6t', 'what6', 'whayt', 'whaty', 'whaht', 'whath', 'whagt',
                          'whatg', 'whaft', 'whatf', 'lst', 'lit', 'lis', 'llist', 'liist', 'lisst', 'listt',
                          'ilst', 'lsit', 'lits', 'kist', 'oist', 'pist', 'lust', 'l8st', 'l9st', 'lost', 'llst',
                          'lkst', 'ljst', 'liat', 'liwt', 'liet', 'lidt', 'lixt', 'lizt', 'lisr', 'lis5', 'lis6',
                          'lisy', 'lish', 'lisg', 'lisf', 'klist', 'lkist', 'olist', 'loist', 'plist', 'lpist', 'luist',
                          'liust', 'l8ist', 'li8st', 'l9ist', 'li9st', 'liost', 'lilst', 'likst', 'ljist', 'lijst',
                          'liast', 'lisat', 'liwst', 'liswt', 'liest', 'liset', 'lidst', 'lisdt', 'lixst', 'lisxt',
                          'lizst', 'liszt', 'lisrt', 'listr', 'lis5t', 'list5', 'lis6t', 'list6', 'lisyt', 'listy',
                          'lisht', 'listh', 'lisgt', 'listg', 'lisft', 'listf', 'md', 'cd', 'cm', 'ccmd', 'cmmd',
                          'cmdd', 'mcd', 'cdm', 'xmd', 'dmd', 'fmd', 'vmd', 'cnd', 'cjd', 'ckd', 'cms', 'cme', 'cmr',
                          'cmf', 'cmc', 'cmx', 'xcmd', 'cxmd', 'dcmd', 'cdmd', 'fcmd', 'cfmd', 'vcmd', 'cvmd', 'cnmd',
                          'cmnd', 'cjmd', 'cmjd', 'ckmd', 'cmkd', 'cmsd', 'cmds', 'cmed', 'cmde', 'cmrd', 'cmdr',
                          'cmfd', 'cmdf', 'cmcd', 'cmdc', 'cmxd', 'cmdx', 'what', 'list', 'cmd', '?', 'h', 'commands'],
                 extras={'emoji': "info",
                         'args': {'command': "The name of a command to display detailed information on (Optional)"},
                         "dev": False},
                 brief="An interactive view of all available commands",
                 description="This command provides an interactive interface to view all available commands, and help "
                             "for how to use each command.\nThe select menu is only available to the author of the "
                             "command, and will display more detailed information of the selected command.\nIf no "
                             "command is selected, brief info about all available command will be displayed.")
    async def help(self, ctx, command=None):
        """
        This function is the entry point for the help command when called traditionally
        Args:
            ctx:
            command:
        """
        await self.help_command(ctx, str(command).lower())

    async def get_bot_commands(self, actx: discord.AutocompleteContext):
        """
        Gets the list of commands for the autocomplete function of the help command.

        Args:
            actx: The context of the autocomplete.

        Returns:
            The list of commands for autocomplete.
        """
        # how to get id pro tutorial ft jean1398reborn
        # first thing we must get ze interaction
        le_fishe_interaction = actx.interaction
        # le next step get the user
        le_user_of_fishe_interaction = le_fishe_interaction.user
        # finale step get ze id of the user
        le_id_of_the_user_of_the_fishe_interaction = le_user_of_fishe_interaction.id

        autocomplete_choices = []
        for command in self.client.commands:
            try:
                if not command.extras["dev"]:
                    autocomplete_choices.append(command.name)
                else:
                    if le_id_of_the_user_of_the_fishe_interaction in self.client.config["devs"]:
                        autocomplete_choices.append(command.name)
            except KeyError:
                autocomplete_choices.append(command.name)

        return autocomplete_choices

    @slash_command(name='help',
                   description='An interactive view of all available commands',
                   guild_ids=stw.guild_ids)
    async def slashhelp(
            self,
            ctx: discord.ApplicationContext,
            command: Option(str, "Choose a command to display detailed information on",
                            autocomplete=get_bot_commands) = None):
        """
        This function is the entry point for the help command when called via slash command.

        Args:
            ctx: The context of the slash command.
            command: The command to get the help page for.
        """
        await self.help_command(ctx, str(command).lower())

    # hello command

    async def hello_command(self, ctx):
        """
        The main function of the hello command

        Args:
            ctx: The context of the command.
        """
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour,
                              title=await stw.add_emoji_title(self.client, "STW Daily", "calendar"),
                              description=f"\u200b\n**👋 Hello! :D I'm STW Daily** - A bot for all things "
                                          f"Fortnite: Save the World (and more!)\n"
                                          f"Questions? Problems? Hit us up on our"
                                          f" [support server!](https://discord.gg/QYgABPDqzH)\n"
                                          f"Invite me to your server "
                                          f"[here](https://canary.discord.com/api/oauth2/authorize"
                                          f"?client_id=757776996418715651&permissions=2147798080"
                                          f"&scope=applications.commands%20bot)\n\u200b")

        embed = await stw.add_requested_footer(ctx, embed)

        embed.add_field(name=f"{self.emojis['library_clipboard']} To check out my commands, use:",
                        value=await stw.mention_string(self.client, "help") + "\n\u200b")
        embed.add_field(name=f"{self.emojis['library_list']} Important:",
                        value="*Portions of the materials used are trademarks and/or copyrighted works of Epic Games, "
                              "Inc. All rights reserved by Epic. This material is not official and is not endorsed by "
                              "Epic.\n\n"
                              "[Privacy Policy](https://sites.google.com/view/stwdaily/legal-info/privacy-policy)  •  "
                              "[Terms of Service](https://sites.google.com/view/stwdaily/legal-info/terms-of-service)*"
                              "\n\u200b",
                        inline=False)
        embed = await stw.set_thumbnail(self.client, embed, "calendar")
        await ctx.channel.send(embed=embed)

    # the harder you climb the harder you fall
    @ext.Cog.listener()
    async def on_message(self, message):
        """
        This function is called when a message is sent in a channel the bot can see.
        Determines whether to send hello message.

        Args:
            message: The message sent.

        Returns:
            None
        """
        self_id = self.client.user.id

        # simple checker to see if the hello command should be triggered or not
        if self_id in message.raw_mentions:
            stripped_message = await stw.strip_string(message.content)

            if len(stripped_message) == len(str(self_id)):
                await self.hello_command(message)
                return


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(Help(client))

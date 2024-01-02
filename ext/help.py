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
# from cache import AsyncLRU


class HelpView(discord.ui.View):
    """
    discord UI View for the help command
    """

    def __init__(self, ctx, help_options, client, desired_lang):
        super().__init__(timeout=480.0)
        self.ctx = ctx
        self.author = ctx.author
        self.children[0].options = help_options
        self.client = client
        self.desired_lang = desired_lang
        self.interaction_check_done = {}

        self.children[0].placeholder = stw.I18n.get("help.view.select.placeholder", desired_lang)

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
        options=[],
    )
    async def selected_option(self, select, interaction):
        """
        Called when a help page is selected.

        Args:
            select: The select menu that was used.
            interaction: The interaction that was used.
        """
        embed = await self.help.help_embed(self.ctx, select.values[0], self.desired_lang)
        if select.values[0] == "main_menu":
            self.children[0].options = await self.help.select_options_commands(self.ctx, False,
                                                                               desired_lang=self.desired_lang)
        else:
            self.children[0].options = await self.help.select_options_commands(self.ctx, selected=select.values[0],
                                                                               desired_lang=self.desired_lang)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        """
        Called when the view times out.
        """
        for child in self.children:
            child.disabled = True
        # if isinstance(self.ctx, discord.ApplicationContext):
        #     try:
        #         return await self.message.edit_original_response(view=self)
        #     except:
        #         return await self.ctx.edit(view=self)
        # else:
        #     return await self.message.edit(view=self)

        # if isinstance(self.message, discord.Interaction):
        #     method = self.message.edit_original_response
        # else:
        #     try:
        #         method = self.message.edit
        #     except:
        #         method = self.ctx.edit
        # if isinstance(self.ctx, discord.ApplicationContext):
        #     try:
        #         return await method(view=self)
        #     except:
        #         try:
        #             return await self.ctx.edit(view=self)
        #         except:
        #             return await method(view=self)
        # else:
        #     return await method(view=self)

        return await stw.slash_edit_original(self.ctx, self.message, embeds=None, view=self)


class Help(ext.Cog):
    """
    The cog for the help and hello command
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    # @AsyncLRU(maxsize=16)
    async def add_brief_command_info(self, embed, command, desired_lang):
        """
        Adds a brief description of a command to an embed.

        Args:
            embed: The embed to add the command to.
            command: The command to add to the embed.
            desired_lang: The language to use for the help page.

        Returns:
            The embed with the command added.
        """
        if len(embed.fields) > 23:
            return embed
        try:
            name_string = f"{self.emojis[command.extras['emoji']]}  {stw.I18n.get(command.extras['name_key'], desired_lang)}"
        except:
            name_string = f"{self.emojis[command.extras['emoji']]}  {command.name}"
        for argument in command.extras["args"].keys():
            try:
                if command.extras['args'][argument][1] is True:
                    name_string += f" *<{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>*"
                else:
                    name_string += f" <{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>"
            except:
                name_string += f" <{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>"

        embed.add_field(name=name_string,
                        value=f"```{stw.I18n.get(command.brief, desired_lang) if '.' in command.brief else command.brief}```\u200b\n",
                        inline=False)
        return embed

    # @AsyncLRU(maxsize=16)
    async def add_big_command_info(self, ctx, embed, command, desired_lang):
        """
        Adds a detailed description of a command to an embed.

        Args:
            ctx: The context of the command.
            embed: The embed to add the command to.
            command: The command to add to the embed.
            desired_lang: The language to use for the help page.

        Returns:
            The embed with the detailed command added.
        """
        me = self.client.user
        mention = "/"
        try:
            cmd = f"/{stw.I18n.get(command.extras['name_key'], desired_lang)}"
        except:
            cmd = f"/{command.name}"
        try:
            mention = me.mention
            try:
                cmd = f"{me.mention} {stw.I18n.get(command.extras['name_key'], desired_lang)}"
            except:
                cmd = f"{me.mention} {command.name}"
        except:
            pass
        try:
            name_string = f"**{await stw.add_emoji_title(self.client, stw.I18n.get(command.extras['name_key'], desired_lang).title(), command.extras['emoji'])}**\n{cmd}"
        except:
            name_string = f"**{await stw.add_emoji_title(self.client, command.name.title(), command.extras['emoji'])}**\n{cmd}"
        for argument in command.extras["args"].keys():
            try:
                if command.extras['args'][argument][1] is True:
                    name_string += f" *<{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>*"
                else:
                    name_string += f" <{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>"
            except:
                name_string += f" <{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>"
        name_string += "\n"
        for argument in command.extras["args"].keys():
            try:
                arg = f"<{stw.I18n.get(argument, desired_lang) if '.' in argument else argument}>"
            except:
                arg = f"<{argument}>"
            try:
                if command.extras['args'][argument][1] is True and isinstance(command.extras['args'][argument], list):
                    info = f"{stw.I18n.get(command.extras['args'][argument][0], desired_lang)}**\n*{stw.I18n.get('help.embed.optional', desired_lang)}*"
                else:
                    if '.' in command.extras['args'][argument][0] and isinstance(command.extras['args'][argument],
                                                                                 list):
                        info = f"{stw.I18n.get(command.extras['args'][argument][0], desired_lang)}**"
                    elif '.' in command.extras['args'][argument]:
                        info = f"{stw.I18n.get(command.extras['args'][argument], desired_lang)}**"
                    else:
                        info = command.extras['args'][argument]
                        if "(Optional)" in info:
                            info = info.replace("(Optional)", "")
                            info += f"**\n*{stw.I18n.get('help.embed.optional', desired_lang)}*"
                        else:
                            info += "**"
            except:
                try:
                    if '.' in command.extras['args'][argument][0] and isinstance(command.extras['args'][argument],
                                                                                 list):
                        info = f"{stw.I18n.get(command.extras['args'][argument][0], desired_lang)}**"
                    else:
                        info = command.extras['args'][argument]
                        if "(Optional)" in info:
                            info = info.replace("(Optional)", "")
                            info += f"**\n*{stw.I18n.get('help.embed.optional', desired_lang)}*"
                        else:
                            info += "**"
                except:
                    info = command.extras['args'][argument]
                    if "(Optional)" in info:
                        info = info.replace("(Optional)", "")
                        info += f"**\n*{stw.I18n.get('help.embed.optional', desired_lang)}*"
                    else:
                        info += "**"

            name_string += f"\n**{arg}: {info}\n"
        try:
            command_description = command.description.format(*[stw.I18n.get(key[0] if isinstance(key, list) else key, desired_lang, *key[1:]) for key in command.extras['description_keys']])
        except:
            command_description = command.description
        try:
            if command.extras["experimental"] is True:
                command_description += f"\n⦾ {stw.I18n.get('generic.help.experimental', desired_lang, self.client.config['emojis']['experimental'])}"
        except:
            pass
        try:
            if command.extras["battle_broken"] is True:
                command_description += f"\n\u200b\n{stw.I18n.get('bbdaily.meta.description.main2', desired_lang, '<t:1672425127:R>')}\n" \
                                       f"{stw.I18n.get('bbdaily.meta.description.main3', desired_lang, 'https://github.com/dippyshere/battle-breakers-private-server')}\n"
        except:
            pass
        embed_desc = f"\n\u200b\n{name_string}\n\u200b\n{command_description}\n\u200b".replace("<@mention_me>",
                                                                                               f"{mention}")
        embed.description = embed_desc
        embed = await stw.add_requested_footer(ctx, embed, desired_lang)
        return embed

    # @AsyncLRU(maxsize=16)
    async def add_default_page(self, ctx, embed_colour, desired_lang="en"):
        """
        Adds the default help page to an embed.

        Args:
            ctx: The context of the command.
            embed_colour: The colour of the embed.
            desired_lang: The language to use for the help page.

        Returns:
            The embed with the default help page added.
        """
        embed = discord.Embed(colour=embed_colour,
                              title=await stw.add_emoji_title(self.client,
                                                              stw.I18n.get('help.embed.title', desired_lang),
                                                              "info"),
                              description=f"\u200b\n{stw.I18n.get('help.embed.description', desired_lang, await stw.mention_string(self.client, 'reward 7'))}\n\u200b\n\u200b")

        embed = await stw.add_requested_footer(ctx, embed, desired_lang)

        for command in self.client.commands:
            try:
                if not command.extras["dev"]:
                    embed = await self.add_brief_command_info(embed, command, desired_lang)
                else:
                    if ctx.author.id in self.client.config["devs"]:
                        embed = await self.add_brief_command_info(embed, command, desired_lang)
            except KeyError:
                embed = await self.add_brief_command_info(embed, command, desired_lang)
        return embed

    # @AsyncLRU(maxsize=16)
    async def help_embed(self, ctx, inputted_command, desired_lang="en"):
        """
        Creates an embed with the help page for a command.

        Args:
            ctx: The context of the command.
            inputted_command: The command to get the help page for.
            desired_lang: The language to get the help page in.

        Returns:
            The embed with the help page for the command.
        """
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour,
                              title=await stw.add_emoji_title(self.client,
                                                              stw.I18n.get('help.embed.title', desired_lang),
                                                              "info"),
                              description="\u200b")

        if inputted_command not in self.client.command_name_list:
            embed = await self.add_default_page(ctx, embed_colour, desired_lang)
        else:
            command_retrieved = self.client.command_dict[self.client.command_name_dict[inputted_command]]
            embed = await self.add_big_command_info(ctx, embed, command_retrieved, desired_lang)

        return embed

    # @AsyncLRU(maxsize=8)
    async def select_options_commands(self, ctx, add_return=True, selected=None, desired_lang="en"):
        """
        Creates the options for the select menu for the help command.

        Args:
            ctx: The context of the command.
            add_return: Whether to add the return option to the list.
            selected: The option that was selected.
            desired_lang: The language to use for the help page.

        Returns:
            The options for the select menu.
        """
        if add_return:
            options = [discord.SelectOption(label=stw.I18n.get('help.view.select.all', desired_lang),
                                            value="main_menu",
                                            description=stw.I18n.get('help.view.select.main_menu.description', desired_lang),
                                            emoji=self.emojis['left_arrow'])]
        else:
            options = []
        for command in self.client.commands:
            if len(options) < 24:
                try:
                    if not command.extras["dev"]:
                        try:
                            options.append(
                                discord.SelectOption(
                                    label=stw.I18n.get(command.extras['name_key'], desired_lang) if '.' in command.extras['name_key'] else command.name,
                                    value=command.name,
                                    description=stw.truncate(stw.I18n.get(command.brief,
                                                                          desired_lang) if '.' in command.brief else command.brief),
                                    emoji=self.emojis[command.extras['emoji']])
                            )
                        except:
                            options.append(
                                discord.SelectOption(
                                    label=stw.I18n.get(command.name,
                                                       desired_lang) if '.' in command.name else command.name,
                                    value=command.name,
                                    description=stw.truncate(stw.I18n.get(command.brief,
                                                                          desired_lang) if '.' in command.brief else command.brief),
                                    emoji=self.emojis[command.extras['emoji']])
                            )
                    else:
                        if ctx.author.id in self.client.config["devs"]:
                            try:
                                options.append(
                                    discord.SelectOption(
                                        label=stw.I18n.get(command.extras['name_key'], desired_lang) if '.' in
                                                                                                        command.extras[
                                                                                                            'name_key'] else command.name,
                                        value=command.name,
                                        description=stw.truncate(stw.I18n.get(command.brief,
                                                                              desired_lang) if '.' in command.brief else command.brief),
                                        emoji=self.emojis[command.extras['emoji']])
                                )
                            except:
                                options.append(
                                    discord.SelectOption(
                                        label=stw.I18n.get(command.name,
                                                           desired_lang) if '.' in command.name else command.name,
                                        value=command.name,
                                        description=stw.truncate(stw.I18n.get(command.brief,
                                                                              desired_lang) if '.' in command.brief else command.brief),
                                        emoji=self.emojis[command.extras['emoji']])
                                )
                except:
                    try:
                        options.append(
                            discord.SelectOption(
                                label=stw.I18n.get(command.extras['name_key'], desired_lang) if '.' in command.extras[
                                    'name_key'] else command.name,
                                value=command.name,
                                description=stw.truncate(stw.I18n.get(command.brief,
                                                                      desired_lang) if '.' in command.brief else command.brief),
                                emoji=self.emojis[command.extras['emoji']])
                        )
                    except:
                        options.append(
                            discord.SelectOption(
                                label=stw.I18n.get(command.name,
                                                   desired_lang) if '.' in command.name else command.name,
                                value=command.name,
                                description=stw.truncate(stw.I18n.get(command.brief,
                                                                      desired_lang) if '.' in command.brief else command.brief),
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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        embed = await self.help_embed(ctx, command, desired_lang)
        if command not in self.client.command_name_list:
            help_options = await self.select_options_commands(ctx, False, desired_lang=desired_lang)
        else:
            help_options = await self.select_options_commands(ctx, selected=self.client.command_dict[
                self.client.command_name_dict[command]].name, desired_lang=desired_lang)

        help_view = HelpView(ctx, help_options, self.client, desired_lang)
        help_view.help = self

        await stw.slash_send_embed(ctx, self.client, embed, help_view)

    @ext.command(name='help',
                 aliases=['/h', '/?', '/help', '/commands', '/command', '/cmds', '/cmd', '/what', '/list',
                          'elp', 'hlp', 'hep', 'hel', 'hhelp', 'heelp', 'hellp', 'helpp', 'ehlp', 'hlep', 'hepl',
                          'gelp', 'yelp', 'uelp', 'jelp', 'nelp', 'belp', 'hwlp', 'h3lp', 'h4lp', 'hrlp', 'hflp',
                          'hdlp', 'hslp', 'hekp', 'heop', 'hepp', 'helo', 'hel0', 'hell', 'ghelp', 'hgelp', 'yhelp',
                          'hyelp', 'uhelp', 'huelp', 'jhelp', 'hjelp', 'nhelp', 'hnelp', 'bhelp', 'hbelp', 'hwelp',
                          'hewlp', 'h3elp', 'he3lp', 'h4elp', 'he4lp', 'hrelp', 'herlp', 'hfelp', 'heflp', 'hdelp',
                          'hedlp', 'hselp', 'heslp', 'heklp', 'helkp', 'heolp', 'helop', 'heplp', 'helpo', 'hel0p',
                          'help0', 'helpl', 'ommands', 'cmmands', 'comands', 'commnds', 'commads', 'commans', 'command',
                          'ccommands', 'coommands', 'commmands', 'commaands', 'commannds', 'commandds', 'commandss',
                          'ocmmands', 'cmomands', 'comamnds', 'commnads', 'commadns', 'commansd', 'xommands',
                          'dommands', 'fommands', 'vommands', 'cimmands', 'c9mmands', 'c0mmands', 'cpmmands',
                          'clmmands', 'ckmmands', 'conmands', 'cojmands', 'cokmands', 'comnands', 'comjands',
                          'comkands', 'commqnds', 'commwnds', 'commsnds', 'commxnds', 'commznds', 'commabds',
                          'commahds', 'commajds', 'commamds', 'commanss', 'commanes', 'commanrs', 'commanfs',
                          'commancs', 'commanxs', 'commanda', 'commandw', 'commande', 'commandd', 'commandx',
                          'commandz', 'xcommands', 'cxommands', 'dcommands', 'cdommands', 'fcommands', 'cfommands',
                          'vcommands', 'cvommands', 'ciommands', 'coimmands', 'c9ommands', 'co9mmands', 'c0ommands',
                          'co0mmands', 'cpommands', 'copmmands', 'clommands', 'colmmands', 'ckommands', 'cokmmands',
                          'conmmands', 'comnmands', 'cojmmands', 'comjmands', 'comkmands', 'commnands', 'commjands',
                          'commkands', 'commqands', 'commaqnds', 'commwands', 'commawnds', 'commsands', 'commasnds',
                          'commxands', 'commaxnds', 'commzands', 'commaznds', 'commabnds', 'commanbds', 'commahnds',
                          'commanhds', 'commajnds', 'commanjds', 'commamnds', 'commanmds', 'commansds', 'commaneds',
                          'commandes', 'commanrds', 'commandrs', 'commanfds', 'commandfs', 'commancds', 'commandcs',
                          'commanxds', 'commandxs', 'commandas', 'commandsa', 'commandws', 'commandsw', 'commandse',
                          'commandsd', 'commandsx', 'commandzs', 'commandsz', 'hat', 'wat', 'wht', 'wha', 'wwhat',
                          'whhat', 'whaat', 'whatt', 'hwat', 'waht', 'whta', 'qhat', '2hat', '3hat', 'ehat', 'dhat',
                          'shat', 'ahat', 'wgat', 'wyat', 'wuat', 'wjat', 'wnat', 'wbat', 'whqt', 'whwt', 'whst',
                          'whxt', 'whzt', 'whar', 'wha5', 'wha6', 'whay', 'whah', 'whag', 'whaf', 'qwhat', 'wqhat',
                          '2what', 'w2hat', '3what', 'w3hat', 'ewhat', 'wehat', 'dwhat', 'wdhat', 'swhat', 'wshat',
                          'awhat', 'wahat', 'wghat', 'whgat', 'wyhat', 'whyat', 'wuhat', 'whuat', 'wjhat', 'whjat',
                          'wnhat', 'whnat', 'wbhat', 'whbat', 'whqat', 'whaqt', 'whwat', 'whawt', 'whsat', 'whast',
                          'whxat', 'whaxt', 'whzat', 'whazt', 'whart', 'whatr', 'wha5t', 'what5', 'wha6t', 'what6',
                          'whayt', 'whaty', 'whaht', 'whath', 'whagt', 'whatg', 'whaft', 'whatf', 'lst', 'lit', 'lis',
                          'llist', 'liist', 'lisst', 'listt', 'ilst', 'lsit', 'lits', 'kist', 'oist', 'pist', 'lust',
                          'l8st', 'l9st', 'lost', 'llst', 'lkst', 'ljst', 'liat', 'liwt', 'liet', 'lidt', 'lixt',
                          'lizt', 'lisr', 'lis5', 'lis6', 'lisy', 'lish', 'lisg', 'lisf', 'klist', 'lkist', 'olist',
                          'loist', 'plist', 'lpist', 'luist', 'liust', 'l8ist', 'li8st', 'l9ist', 'li9st', 'liost',
                          'lilst', 'likst', 'ljist', 'lijst', 'liast', 'lisat', 'liwst', 'liswt', 'liest', 'liset',
                          'lidst', 'lisdt', 'lixst', 'lisxt', 'lizst', 'liszt', 'lisrt', 'listr', 'lis5t', 'list5',
                          'lis6t', 'list6', 'lisyt', 'listy', 'lisht', 'listh', 'lisgt', 'listg', 'lisft', 'listf',
                          'md', 'cd', 'cm', 'ccmd', 'cmmd', 'cmdd', 'mcd', 'cdm', 'xmd', 'dmd', 'fmd', 'vmd', 'cnd',
                          'cjd', 'ckd', 'cms', 'cme', 'cmr', 'cmf', 'cmc', 'cmx', 'xcmd', 'cxmd', 'dcmd', 'cdmd',
                          'fcmd', 'cfmd', 'vcmd', 'cvmd', 'cnmd', 'cmnd', 'cjmd', 'cmjd', 'ckmd', 'cmkd', 'cmsd',
                          'cmds', 'cmed', 'cmde', 'cmrd', 'cmdr', 'cmfd', 'cmdf', 'cmcd', 'cmdc', 'cmxd', 'cmdx',
                          'what', 'list', 'cmd', '?', 'h', 'commands', 'hulp te vertoon', 'التعليمات', 'помощ',
                          'সাহায্য', 'ajuda', 'Pomoc', 'hjælp', 'Hilfe', 'βοήθεια', 'ayuda', 'abi', 'کمک', 'auta',
                          'aide', 'મદદ', 'taimako', 'עֶזרָה', 'मदद', 'pomoći', 'Segítség', 'bantuan', 'ヘルプ', 'padėti',
                          'palīdzēt', 'मदत', 'ਮਦਦ ਕਰੋ', 'pomocy', 'Ajutor', 'справке', 'помоћ', 'hjälp', 'msaada',
                          'உதவி', 'సహాయం', 'yardım', 'довідка', 'مدد', 'trợ giúp', '帮助', '幫助', 'hulptevertoon',
                          'hulp', 'trợgiúp', 'halp', 'helxp', 'helps', 'helpt', 'helpb', 'helup', 'heblp', 'mhelp',
                          'helip', 'helrp', 'helsp', 'vhelp', 'hemp', 'hmlp', 'helgp', 'hielp', 'xelp', 'helnp', 'ielp',
                          'helj', 'helcp', 'hejp', 'held', 'hjlp', 'lelp', 'helpu', 'velp', 'hylp', 'celp',
                          'hetp', 'felp', 'hebp', 'heep', 'pelp', 'zhelp', 'helk', 'heqp', 'heilp', 'helpm', 'hetlp',
                          'hnlp', 'hvelp', 'helq', 'hglp', 'zelp', 'helep', 'khelp', 'hplp', 'helpw', 'helw', 'htlp',
                          'helpg', 'ihelp', 'qelp', 'eelp', 'helx', 'helpy', 'helpn', 'heulp', 'hesp', 'hele', 'lhelp',
                          'selp', 'telp', 'helc', 'helpv', 'hejlp', 'heip', 'rhelp', 'helap', 'hxelp', 'relp', 'herp',
                          'haelp', 'hexlp', 'heli', 'helpi', 'hlelp', 'helt', 'heljp', 'helvp', 'hewp', 'hqelp', 'hegp',
                          'helhp', 'helpj', 'chelp', 'heap', 'hevlp', 'helwp', 'helb', 'hedp', 'fhelp', 'ahelp', 'hecp',
                          'aelp', 'thelp', 'heltp', 'hehp', 'hels', 'hblp', 'helpa', 'hhlp', 'heyp', 'hclp', 'qhelp',
                          'helr', 'hklp', 'heup', 'helpc', 'helpk', 'helpr', 'ehelp', 'hezp', 'heln', 'kelp', 'helpx',
                          'hezlp', 'helfp', 'helg', 'hzlp', 'heglp', 'hexp', 'heqlp', 'helpz', 'hoelp', 'phelp',
                          'helyp', 'helm', 'hela', 'melp', 'helh', 'henlp', 'holp', 'hilp', 'helu', 'hzelp', 'hpelp',
                          'helpq', 'heldp', 'hely', 'heylp', 'helz', 'helph', 'helv', 'delp', 'hkelp', 'hllp', 'helpd',
                          'helf', 'hehlp', 'htelp', 'hxlp', 'helpe', 'hevp', 'hmelp', 'helpf', 'healp', 'henp', 'hvlp',
                          'hefp', 'helmp', 'heclp', 'dhelp', 'hqlp', 'xhelp', 'helqp', 'helzp', 'shelp', 'hcelp',
                          'ohelp', 'hemlp', 'oelp', 'helbp', 'whelp', 'h2lp', 'h$lp', 'h#lp', 'h@lp', 'he;p', 'he/p',
                          'he.p', 'he,p', 'he?p', 'he>p', 'he<p', 'hel9', 'hel-', 'hel[', 'hel]', 'hel;', 'hel(',
                          'hel)', 'hel_', 'hel=', 'hel+', 'hel{', 'hel}', 'hel:', 'commandj', 'coammands', 'commaonds',
                          'cohmands', 'commafds', 'coemmands', 'czommands', 'commatnds', 'commaxds', 'hommands',
                          'commyands', 'commandu', 'ocommands', 'commandqs', 'comfmands', 'rcommands', 'pcommands',
                          'commandi', 'commanks', 'uommands', 'commawds', 'commbnds', 'commfands', 'commandv',
                          'zommands', 'commandts', 'coymands', 'commgnds', 'commandb', 'comtmands', 'cormands',
                          'qommands', 'commagds', 'commarnds', 'iommands', 'cosmands', 'comzmands', 'wommands',
                          'commjnds', 'commakds', 'combmands', 'commapds', 'commanqs', 'cobmands', 'commanls',
                          'comoands', 'commaads', 'commandsg', 'commpnds', 'cwommands', 'commandsc', 'rommands',
                          'commandr', 'cogmands', 'cbommands', 'commandis', 'cymmands', 'commanms', 'commandus',
                          'cowmmands', 'commanvds', 'gommands', 'comgmands', 'cdmmands', 'cowmands', 'commbands',
                          'comxands', 'commandy', 'commangs', 'nommands', 'covmands', 'commrnds', 'codmmands',
                          'commandsk', 'scommands', 'comlmands', 'comomands', 'cummands', 'coymmands', 'commatds',
                          'comtands', 'commandbs', 'comhmands', 'commaends', 'kommands', 'commcnds', 'commanids',
                          'crmmands', 'covmmands', 'comdmands', 'commlands', 'comzands', 'cotmands', 'comqands',
                          'tcommands', 'commazds', 'comemands', 'ceommands', 'comrands', 'commanas', 'commdnds',
                          'cgommands', 'commgands', 'icommands', 'cocmands', 'cofmmands', 'commagnds', 'coamands',
                          'commandg', 'cnmmands', 'comyands', 'commandps', 'cwmmands', 'cogmmands', 'cyommands',
                          'commandq', 'comlands', 'ncommands', 'comimands', 'commandt', 'eommands', 'commandsn',
                          'coimands', 'cjmmands', 'ctommands', 'commards', 'pommands', 'communds', 'commandvs',
                          'commasds', 'cormmands', 'lommands', 'commaods', 'sommands', 'mommands', 'aommands',
                          'comfands', 'commoands', 'commandys', 'commafnds', 'commanis', 'commandgs', 'commaqds',
                          'comwmands', 'codmands', 'cqmmands', 'coemands', 'ecommands', 'cxmmands', 'coumands',
                          'commandsi', 'csmmands', 'cgmmands', 'commandsf', 'commvands', 'acommands', 'cobmmands',
                          'comxmands', 'colmands', 'tommands', 'jommands', 'commaknds', 'wcommands', 'commlnds',
                          'commants', 'commadds', 'comvands', 'commaunds', 'cmommands', 'yommands', 'commuands',
                          'commavds', 'commandso', 'comumands', 'commalnds', 'commaids', 'comymands', 'cemmands',
                          'commanzs', 'comsands', 'ycommands', 'mcommands', 'commanjs', 'commanvs', 'commanyds',
                          'commaeds', 'commavnds', 'commtnds', 'combands', 'commnnds', 'commapnds', 'commandls',
                          'commandsl', 'coxmmands', 'comvmands', 'cfmmands', 'comqmands', 'caommands', 'comdands',
                          'commanads', 'commanuds', 'cammands', 'cofmands', 'copmands', 'zcommands', 'commandn',
                          'commandks', 'commangds', 'cuommands', 'commanos', 'compands', 'commauds', 'jcommands',
                          'commandl', 'commonds', 'commanzds', 'coummands', 'commandsb', 'cozmands', 'commmnds',
                          'commcands', 'czmmands', 'commanus', 'comgands', 'coomands', 'commanhs', 'commanods',
                          'commalds', 'commantds', 'coqmands', 'commeands', 'commandms', 'cocmmands', 'commacnds',
                          'commandm', 'commandk', 'commadnds', 'comamands', 'commandsv', 'bommands', 'commrands',
                          'commaynds', 'commanbs', 'commpands', 'commandhs', 'commanys', 'commandsr', 'commandsh',
                          'commynds', 'cjommands', 'coxmands', 'commandos', 'commdands', 'commvnds', 'chmmands',
                          'comcmands', 'ucommands', 'cohmmands', 'commandns', 'commandp', 'cozmmands', 'comcands',
                          'ccmmands', 'cbmmands', 'commandjs', 'cvmmands', 'commandc', 'cnommands', 'comminds',
                          'chommands', 'crommands', 'commanns', 'commtands', 'commiands', 'commando', 'commanws',
                          'commfnds', 'commanlds', 'comrmands', 'comsmands', 'commhnds', 'commanpds', 'comhands',
                          'commends', 'commayds', 'comuands', 'comwands', 'cmmmands', 'compmands', 'bcommands',
                          'commacds', 'cotmmands', 'kcommands', 'gcommands', 'coqmmands', 'commandf', 'commknds',
                          'cosmmands', 'ctmmands', 'commhands', 'cqommands', 'commainds', 'commandsj', 'comiands',
                          'hcommands', 'oommands', 'commandsq', 'commanqds', 'comaands', 'commandsu', 'commanps',
                          'qcommands', 'commandsp', 'comeands', 'commandst', 'commandh', 'commankds', 'commandsm',
                          'lcommands', 'commanwds', 'csommands', 'commandsy', 'c8mmands', 'c;mmands', 'c*mmands',
                          'c(mmands', 'c)mmands', 'co,mands', 'co<mands', 'com,ands', 'com<ands', 'comma,ds',
                          'comma<ds', 'cds', 'ceds', 'smds', 'cmgs', 'cmos', 'cmms', 'cmzs', 'cdms', 'mmds', 'cmus',
                          'mcds', 'qcmds', 'mds', 'hcmds', 'cmdp', 'dmds', 'chmds', 'cmdi', 'cmdsx', 'cmdb', 'cmeds',
                          'cmdns', 'cyds', 'cmdes', 'nmds', 'cmdst', 'cmdsr', 'cgmds', 'csds', 'cads', 'cvmds', 'tcmds',
                          'czmds', 'qmds', 'cqmds', 'cmdsd', 'cmdsu', 'cmjs', 'pcmds', 'xmds', 'cmdso', 'ctds', 'cmcs',
                          'cmbds', 'cmvs', 'cgds', 'cmdsi', 'ctmds', 'cmdl', 'cmhs', 'cmhds', 'cmdv', 'jmds', 'cmdos',
                          'cids', 'cmdw', 'cmpds', 'cmfs', 'cmvds', 'cmdsf', 'cdmds', 'cnmds', 'cmdts', 'cmdjs', 'cbds',
                          'cpds', 'cmdsb', 'cmjds', 'cmdcs', 'cmdt', 'hmds', 'czds', 'zcmds', 'cmdq', 'cumds', 'cmdbs',
                          'cmdsj', 'zmds', 'cmdfs', 'clds', 'cqds', 'omds', 'cmrds', 'cmdsm', 'cnds', 'cmks', 'dcmds',
                          'wmds', 'gmds', 'cmdk', 'cmns', 'pmds', 'ccds', 'ckds', 'cfmds', 'cwmds', 'cmdn',
                          'cmdm', 'cmzds', 'amds', 'cmdsq', 'cmws', 'cemds', 'rmds', 'tmds', 'cmcds', 'cmnds', 'bmds',
                          'cmdms', 'cxds', 'cmbs', 'emds', 'jcmds', 'cmdss', 'ccmds', 'cpmds', 'csmds', 'cmdus',
                          'cmmds', 'cmys', 'cymds', 'cmis', 'cmdsw', 'fmds', 'cmxds', 'chds', 'cmsds', 'cmdy', 'cmdds',
                          'cmps', 'ycmds', 'crds', 'cmts', 'vcmds', 'cdds', 'cmes', 'cmdj', 'fcmds', 'cmods', 'ckmds',
                          'cvds', 'cwds', 'cmdis', 'umds', 'cmdsa', 'cmtds', 'cmqds', 'cmdsk', 'mcmds', 'vmds', 'cmrs',
                          'cmdws', 'cmads', 'cmas', 'cjmds', 'cmss', 'cmdvs', 'ocmds', 'lcmds', 'cmxs', 'cmdo', 'cmdks',
                          'cfds', 'scmds', 'camds', 'cmdsp', 'cmdas', 'cmda', 'acmds', 'cmls', 'ncmds', 'cmdsg',
                          'icmds', 'cmuds', 'clmds', 'cmdz', 'cbmds', 'cmdsz', 'cmdsh', 'crmds', 'cmdg', 'cmfds',
                          'lmds', 'cmqs', 'cmdgs', 'cmyds', 'rcmds', 'comds', 'cimds', 'cuds', 'cmdsc', 'ymds', 'cmdsn',
                          'cmwds', 'cmdls', 'gcmds', 'cmdqs', 'cmdse', 'imds', 'ucmds', 'bcmds', 'cmgds', 'cjds',
                          'kmds', 'kcmds', 'cmdu', 'ecmds', 'cmdsl', 'cmkds', 'cmdsv', 'cmdps', 'xcmds', 'cmdh',
                          'cmdzs', 'cmdhs', 'wcmds', 'cmlds', 'cmdxs', 'cmdrs', 'cmdsy', 'cxmds', 'cmdys', 'cmids',
                          'c,ds', 'c<ds', 'lhp', 'hdp', 'hlpa', 'ulp', 'hl', 'hup', 'lp', 'flp', 'hp', 'whlp', 'mhlp',
                          'clp', 'qlp', 'hlr', 'hlh', 'hlps', 'hpl', 'vlp', 'hlpq', 'hlv', 'thlp', 'hkp', 'hlop', 'hln',
                          'hlpt', 'hbp', 'hlq', 'hsp', 'hlpr', 'mlp', 'olp', 'hlxp', 'yhlp', 'xhlp', 'xlp', 'llp',
                          'hlo', 'hlpb', 'hnp', 'hlu', 'hap', 'hlpx', 'klp', 'hlt', 'hlip', 'hlpu', 'hlb', 'phlp',
                          'fhlp', 'hlmp', 'ohlp', 'hlpc', 'hlj', 'hljp', 'chlp', 'khlp', 'hlm', 'qhlp', 'hlpz',
                          'hlz', 'hlkp', 'hvp', 'hlbp', 'hxp', 'htp', 'jlp', 'hlzp', 'hjp', 'hla', 'zlp', 'tlp',
                          'hlpf', 'hlfp', 'hlap', 'hlpg', 'hlqp', 'hpp', 'hlx', 'hlg', 'hlgp', 'hlhp', 'hll',
                          'hgp', 'hli', 'hwp', 'hlpp', 'hlpo', 'ahlp', 'hyp', 'hlk', 'ghlp', 'rhlp', 'hlpj', 'hlnp',
                          'hlsp', 'hld', 'hhp', 'nlp', 'hly', 'vhlp', 'hzp', 'glp', 'blp', 'ihlp', 'hlpm', 'hmp',
                          'hip', 'ylp', 'hlf', 'hls', 'alp', 'jhlp', 'hlpk', 'hlrp', 'hlc', 'uhlp', 'hlpd', 'hrp',
                          'slp', 'hltp', 'hlvp', 'wlp', 'hlwp', 'bhlp', 'hfp', 'hlup', 'hlpy', 'hlpv', 'zhlp', 'hlcp',
                          'rlp', 'nhlp', 'hlpn', 'ilp', 'plp', 'hlpe', 'hqp', 'hle', 'hcp', 'hldp', 'dhlp', 'hlpi',
                          'hlpl', 'hlyp', 'hlph', 'lhlp', 'hlpw', 'h;p', 'h/p', 'h.p', 'h,p', 'h?p', 'h>p', 'h<p',
                          'hl9', 'hl0', 'hl-', 'hl[', 'hl]', 'hl;', 'hl(', 'hl)', 'hl_', 'hl=', 'hl+', 'hl{', 'hl}',
                          'hl:', 'wchat', 'whaj', 'wvhat', 'whatn', 'owhat', 'xhat', 'whav', 'ghat', 'whmt', 'zhat',
                          'wwat', 'whlt', 'wtat', 'zwhat', 'whatw', 'whal', 'whrt', 'whgt', 'kwhat', 'whax', 'whut',
                          'whavt', 'whatv', 'whnt', 'nwhat', 'ihat', 'whvt', 'wpat', 'rwhat', 'nhat', 'bwhat', 'mhat',
                          'wthat', 'whjt', 'jwhat', 'whet', 'wham', 'whaot', 'whaw', 'whyt', 'whatx', 'whata', 'yhat',
                          'whad', 'lhat', 'whatp', 'twhat', 'whatj', 'wfhat', 'woat', 'mwhat', 'wrhat', 'wrat', 'whao',
                          'whvat', 'whbt', 'xwhat', 'gwhat', 'whak', 'whadt', 'pwhat', 'whaa', 'wqat', 'whae', 'rhat',
                          'whato', 'weat', 'whats', 'whai', 'whatc', 'hwhat', 'whct', 'wfat', 'fhat', 'whcat', 'wsat',
                          'wxat', 'whmat', 'whatm', 'whdat', 'whab', 'whdt', 'hhat', 'whatb', 'whpt', 'wphat', 'whau',
                          'wzhat', 'whot', 'whit', 'whatq', 'ywhat', 'whaut', 'wohat', 'that', 'whatd', 'whatz', 'wzat',
                          'vwhat', 'wlat', 'whabt', 'fwhat', 'whan', 'whate', 'chat', 'whaz', 'whkat', 'wmhat', 'whtat',
                          'wcat', 'iwhat', 'whoat', 'wlhat', 'wihat', 'whht', 'whatl', 'wvat', 'whft', 'whas', 'whapt',
                          'jhat', 'wdat', 'vhat', 'wiat', 'whkt', 'uwhat', 'whamt', 'wkat', 'whac', 'bhat', 'whant',
                          'khat', 'whalt', 'whfat', 'wmat', 'waat', 'whaq', 'wxhat', 'whatk', 'whati', 'whait', 'cwhat',
                          'whlat', 'lwhat', 'wheat', 'whap', 'whrat', 'whakt', 'uhat', 'whtt', 'ohat', 'phat', 'whiat',
                          'whatu', 'whact', 'whpat', 'whajt', 'whaet', 'wkhat', '1hat', '!hat', '@hat', '#hat', 'wha4',
                          'wha$', 'wha%', 'wha^', '?e', 'x?', '?z', '?q', '?l', 'c?', '?h', '?y', 'p?', 'm?', '?c',
                          '?t', '?a', 'z?', '?s', 'f?', 'r?', 'e?', 'i?', 'j?', 'd?', '?n', 'b?', '?u', 't?', '?d',
                          'n?', 'y?', 'q?', '?p', 'h?', '?b', '?i', 'k?', 'w?', 'u?', 'o?', 'v?', '?j', '?f', '?r',
                          '?x', 'a?', 'l?', '?m', '?g', '?o', '?w', '?k', 's?', '?v', 'g?', '/', '.', '>', '<', ',',
                          'lismt', 'listu', 'lwst', 'leist', 'lisn', 'mlist', 'lnist',
                          'listn', 'eist', 'hlist', 'lvst', 'lirt', 'lispt', 'zist', 'xist', 'lijt', 'iist', 'liyst',
                          'listw', 'listo', 'dist', 'listq', 'lisb', 'mist', 'ldist', 'lism', 'liut', 'lisot', 'glist',
                          'lisi', 'sist', 'ldst', 'lyist', 'lisd', 'ltst', 'livst', 'uist', 'aist', 'listi',
                          'licst', 'fist', 'cist', 'lrst', 'ltist', 'lfst', 'lisit', 'rist', 'gist', 'ylist', 'livt',
                          'lqst', 'lisct', 'lihst', 'lisa', 'listz', 'lmst', 'lisp', 'clist', 'bist', 'lisu', 'libt',
                          'lxist', 'lisx', 'litst', 'lfist', 'lista', 'lisq', 'listc', 'lhst', 'lirst', 'tist',
                          'wist', 'ligt', 'lift', 'lyst', 'limst', 'lists', 'lcist', 'liyt', 'liht', 'last', 'lilt',
                          'liste', 'lbst', 'lisl', 'liqst', 'elist', 'liss', 'lisjt', 'liqt', 'listm', 'listx', 'liot',
                          'tlist', 'lisut', 'rlist', 'lrist', 'qist', 'vlist', 'lisc', 'lisnt',
                          'zlist', 'lipst', 'lisqt', 'lgist', 'lisv', 'lipt', 'likt', 'limt', 'lwist', 'lbist', 'litt',
                          'vist', 'laist', 'lisj', 'liso', 'lgst', 'listv', 'lhist',
                          'lqist', 'listk', 'lvist', 'lcst', 'lsist', 'blist', 'lisw', 'nlist', 'ulist', 'lict', 'lzst',
                          'lislt', 'lisz', 'jlist', 'lest', 'lifst', 'libst', 'yist', 'lisvt', 'listp', 'liskt', 'liit',
                          'xlist', 'lmist', 'dlist', 'lsst', 'listj', 'lxst', 'flist', 'wlist', 'alist', 'jist',
                          'qlist', 'lzist', 'lise', 'ilist', 'ligst', 'listd', 'listl', 'slist', ';ist', '/ist',
                          '.ist', ',ist', '?ist', '>ist', '<ist', 'l7st', 'l&st', 'l*st', 'l(st', 'lis4', 'lis$',
                          'lis%', 'lis^', 'cmdlits', 'rcmdlist', 'cmdrlist', 'cmdlis', 'cmdlpst', 'cdmlist', 'cmdsist',
                          'cmdlust', 'cvmdlist', 'cmdcist', 'cxmdlist', 'cmldist', 'cmdlit', 'cmdilst', 'cmdlyist',
                          'cmdlst', 'cmdlsit', 'cmdlisr', 'cmdlixt', 'cmdlitst', 'cdlist', 'cmdliste', 'cmclist',
                          'cmdliist', 'cmdlistp', 'cmdtist', 'cmlist', 'mdlist', 'ucmdlist', 'wmdlist', 'cmmdlist',
                          'cmdlisv', 'cmdmist', 'cmdliso', 'scmdlist', 'cudlist', 'cmdlxist', 'cmdist', 'cmdjlist',
                          'cmdltist', 'cmdliost', 'cmrdlist', 'cfdlist', 'cmdlisth', 'cmdlistf', 'mmdlist', 'cmdbist',
                          'cmdlisty', 'cmdlist', 'cmdqlist', 'cmxdlist', 'cmduist', 'cmdlisto', 'ocmdlist', 'mcdlist',
                          'cmdlvst', 'cmdlistg', 'cmdlisqt', 'czmdlist', 'xmdlist', 'cmdeist', 'jcmdlist', 'ncmdlist',
                          'cmdlhst', 'cpmdlist', 'lmdlist', 'cmdlgst', 'cmelist', 'cmjdlist', 'cmydlist', 'cmdlipst',
                          'cmdlisw', 'cmdltst', 'cjmdlist', 'cmgdlist', 'cmdlost', 'cmdlisf', 'cmdlistw', 'cmdlism',
                          'cmdlhist', 'cmdlista', 'icmdlist', 'cmdlihst', 'cmdliust', 'cmdlisut', 'vmdlist', 'cmdxlist',
                          'cmdlwist', 'cmdllist', 'cmdpist', 'cmdlisj', 'cmdlimt', 'cmdlispt', 'cmdlisd', 'cmdlistx',
                          'cmdliat', 'camdlist', 'cmdlisc', 'cmdlisot', 'cmtdlist', 'cmdslist', 'fmdlist', 'cmdlivst',
                          'cmllist', 'cmdfist', 'cmdlistc', 'cmdliyst', 'cgmdlist', 'wcmdlist', 'imdlist', 'cmdlaist',
                          'cmdnlist', 'cmdlisat', 'cmdlish', 'xcmdlist', 'cmdlicst', 'cqmdlist', 'cmdllst', 'cmdlisu',
                          'cmdlinst', 'crdlist', 'cmdnist', 'bmdlist', 'cmdlistu', 'cmdlise', 'lcmdlist', 'cmdliszt',
                          'cmdlnist', 'cmdliest', 'cmdlisx', 'cmdldist', 'zmdlist', 'cmdlxst', 'cmdqist', 'cmddist',
                          'cmdlisi', 'cmdlpist', 'cmnlist', 'cmdvlist', 'dcmdlist', 'cmdlast', 'cmdlrist', 'cmtlist',
                          'cmddlist', 'cmdlistt', 'cmdlisjt', 'csdlist', 'cmdaist', 'nmdlist', 'csmdlist', 'cmdvist',
                          'cbdlist', 'smdlist', 'cmdlisl', 'ccdlist', 'cmdclist', 'cmilist', 'cmdliet', 'cmdldst',
                          'cmdlistj', 'cmdlisq', 'crmdlist', 'cmdwist', 'ecmdlist', 'cmdlisb', 'ccmdlist', 'cmdlvist',
                          'zcmdlist', 'ycmdlist', 'cmdlislt', 'acmdlist', 'cqdlist', 'cmdlest', 'chdlist', 'cmdliskt',
                          'cmdolist', 'cmdlistq', 'cmcdlist', 'cmylist', 'gmdlist', 'cmdlisn', 'cymdlist', 'cmdlidt',
                          'cmdmlist', 'pmdlist', 'cmdlnst', 'cmolist', 'dmdlist', 'cmdlibst', 'cmdlistl', 'cmwlist',
                          'cldlist', 'cmdlzst', 'cmdlwst', 'cgdlist', 'cmdlisrt', 'cmdalist', 'cmdleist', 'cmdlict',
                          'cmdliot', 'ckmdlist', 'cmdgist', 'cmdflist', 'cmdlistz', 'cmdlistm', 'cmdjist', 'cmflist',
                          'cumdlist', 'kmdlist', 'bcmdlist', 'cmdrist', 'cmdlivt', 'cmdlcist', 'cmdluist', 'cmdlilt',
                          'cmdlisxt', 'ymdlist', 'cmalist', 'cmpdlist', 'cmdlitt', 'cmdlistk', 'hmdlist', 'cmdliut',
                          'cmdloist', 'kcmdlist', 'cmdlyst', 'cmdlipt', 'cmdoist', 'cmedlist', 'cfmdlist', 'cmdlfst',
                          'cydlist', 'cmklist', 'cmdlisg', 'cmmlist', 'cmdlijt', 'cmdlistd', 'cmvlist', 'cmdlisp',
                          'cemdlist', 'cmbdlist', 'omdlist', 'cmdlisa', 'cmdplist', 'cwmdlist', 'cmdlisvt', 'cmdlgist',
                          'cmzdlist', 'cmdlibt', 'cmdlkst', 'cxdlist', 'pcmdlist', 'cmvdlist', 'cmdelist', 'cmdlirst',
                          'cmjlist', 'rmdlist', 'cimdlist', 'cmdlistb', 'cmdlijst', 'cddlist', 'cmodlist', 'cmwdlist',
                          'cmslist', 'ckdlist', 'cmdlsst', 'cmdilist', 'cmdljist', 'tcmdlist', 'qmdlist', 'cmzlist',
                          'cadlist', 'cmdljst', 'cmrlist', 'umdlist', 'cmndlist', 'cmdlisct', 'cmidlist', 'cmdlisit',
                          'fcmdlist', 'jmdlist', 'cmdlisft', 'cmblist', 'codlist', 'cmldlist', 'cmdklist', 'ctdlist',
                          'cmkdlist', 'cmdliast', 'cmdliqt', 'cmdliwt', 'cnmdlist', 'cmfdlist', 'cmdlkist', 'cmadlist',
                          'cmdlilst', 'czdlist', 'cmdyist', 'cmhlist', 'cmdlzist', 'cmdlisst', 'cmqlist', 'cmdlizt',
                          'cmdlidst', 'cmdliswt', 'cmdlmist', 'cmdlimst', 'cmdlqist', 'cjdlist', 'cmdliwst', 'cmdlikst',
                          'cmdlqst', 'cndlist', 'cmdliqst', 'cmdligt', 'cmdwlist', 'cmudlist', 'cmdliss', 'cdmdlist',
                          'cmdlisk', 'qcmdlist', 'cmdlrst', 'cvdlist', 'cmdlfist', 'cmdlizst', 'cmdiist', 'cmdligst',
                          'amdlist', 'cmdglist', 'cmdlbst', 'cmdliset', 'chmdlist', 'cmdhist', 'cmdzist', 'cmdzlist',
                          'cmdlikt', 'mcmdlist', 'cmdlisti', 'cmdlisz', 'cmdlists', 'cmdliit', 'cmglist', 'cmqdlist',
                          'cmdhlist', 'cmdtlist', 'ctmdlist', 'cmdlint', 'cmdliht', 'cmdxist', 'cmdlisnt', 'cmdylist',
                          'cmdlcst', 'cmdkist', 'cmdlmst', 'cmdlisgt', 'cmdlisdt', 'cmdlifst', 'cmdlistr', 'cidlist',
                          'cmdlsist', 'hcmdlist', 'cmdlisyt', 'cpdlist', 'cmdlismt', 'cmdlistn', 'cmplist', 'cmdlbist',
                          'cmxlist', 'cmhdlist', 'comdlist', 'emdlist', 'cmdlisy', 'cwdlist', 'cedlist', 'cmdblist',
                          'cmdlistv', 'vcmdlist', 'tmdlist', 'cmdlixst', 'cmdliyt', 'cmdulist', 'cmulist', 'cbmdlist',
                          'clmdlist', 'cmdlirt', 'cmdlift', 'gcmdlist', 'cmsdlist', 'cmdlisbt', 'cmdlisht', 'c,dlist',
                          'c<dlist', 'cmd;ist', 'cmd/ist', 'cmd.ist', 'cmd,ist', 'cmd?ist', 'cmd>ist', 'cmd<ist',
                          'cmdl7st', 'cmdl8st', 'cmdl9st', 'cmdl&st', 'cmdl*st', 'cmdl(st', 'cmdlis4', 'cmdlis5',
                          'cmdlis6', 'cmdlis$', 'cmdlis%', 'cmdlis^', '/hlp', '/cmdlist'],
                 extras={'emoji': "info",
                         'args': {'help.meta.args.command': ['help.meta.args.command.description', True]},
                         "dev": False, "description_keys": ["help.meta.description"],
                         "name_key": "help.slash.name"},
                 brief="help.slash.description",
                 description="{0}")
    async def help(self, ctx, command=None):
        """
        This function is the entry point for the help command when called traditionally
        Args:
            ctx:
            command:
        """
        await self.help_command(ctx, str(command).lower())

    # @AsyncLRU(maxsize=16)
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

    @slash_command(name='help', name_localizations=stw.I18n.construct_slash_dict("help.slash.name"),
                   description='An interactive view of all available commands',
                   description_localizations=stw.I18n.construct_slash_dict("help.slash.description"),
                   guild_ids=stw.guild_ids)
    async def slashhelp(self, ctx: discord.ApplicationContext,
                        command: Option(description="Choose a command to display detailed information on",
                                        description_localizations=stw.I18n.construct_slash_dict("help.meta.args.command.description"),
                                        name_localizations=stw.I18n.construct_slash_dict("help.meta.args.command"),
                                        autocomplete=get_bot_commands) = None):  # TODO: Should this use autocomplete or choices?
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

        desired_lang = await stw.I18n.get_desired_lang(self.client, ctx)

        embed_colour = self.client.colours["generic_blue"]

        embed = discord.Embed(colour=embed_colour,
                              title=await stw.add_emoji_title(self.client,
                                                              stw.I18n.get('generic.stwdaily', desired_lang),
                                                              "calendar"),
                              description=f"\u200b\n{stw.I18n.get('help.hello.description1', desired_lang)}\n"
                                          f"{stw.I18n.get('help.hello.description2', desired_lang, 'https://discord.gg/QYgABPDqzH')}\n"
                                          f"{stw.I18n.get('help.hello.description3', desired_lang, 'https://canary.discord.com/api/oauth2/authorize?client_id=757776996418715651&permissions=2147798080&scope=applications.commands%20bot')}\n\u200b")

        embed = await stw.add_requested_footer(ctx, embed, desired_lang)

        embed.add_field(name=stw.I18n.get('help.hello.description4', desired_lang, self.emojis['library_clipboard']),
                        value=await stw.mention_string(self.client, "help") + "\n\u200b")
        embed.add_field(
            name=stw.I18n.get('help.hello.epic.fancontentdisclaimer.title', desired_lang, self.emojis['library_list']),
            value=f"{stw.I18n.get('help.hello.epic.fancontentdisclaimer.value', desired_lang)}\n\n"
                  f"{stw.I18n.get('help.hello.legal.view', desired_lang, 'https://sites.google.com/view/stwdaily/legal-info/privacy-policy', 'https://sites.google.com/view/stwdaily/legal-info/terms-of-service')}\n\u200b",
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

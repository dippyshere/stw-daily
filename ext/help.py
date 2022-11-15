import stwutil as stw

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)


class HelpView(discord.ui.View):
    def __init__(self, ctx, help_options, client):
        super().__init__()
        self.ctx = ctx
        self.author = ctx.author
        self.children[0].options = help_options
        self.client = client
        self.interaction_check_done = {}

    async def interaction_check(self, interaction):
        if self.author == interaction.user:
            return True
        else:
            try:
                already_notified = self.interaction_check_done[interaction.user.id]
            except:
                already_notified = False
                self.interaction_check_done[interaction.user.id] = True

            if not already_notified:
                support_url = self.client.config["support_url"]
                acc_name = ""
                error_code = "errors.stwdaily.not_author_interaction_response"
                embed = await stw.post_error_possibilities(interaction, self.client, "help", acc_name, error_code,
                                                           support_url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            else:
                return False

    @discord.ui.select(
        placeholder="Select a help page here",
        min_values=1,
        max_values=1,
        options=[],
    )
    async def selected_option(self, select, interaction):
        embed = await self.help.help_embed(self.ctx, select.values[0])
        await interaction.response.edit_message(embed=embed, view=self)


# cog for the help & hello command.
class Help(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def add_brief_command_info(self, embed, command):
        name_string = f"{self.emojis[command.extras['emoji']]}  {command.name}"
        for argument in command.extras["args"].keys():
            name_string += f" <{argument}>"

        embed.add_field(name=name_string, value=f"```{command.brief}```\u200b\n", inline=False)
        return embed

    async def add_big_command_info(self, ctx, embed, command):

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

            name_string += f"\n**{arg} : {info}\n"

        embed_desc = f"\n\u200b\n{name_string}\n\u200b\n{command.description}\n\u200b".replace("<@mention_me>",
                                                                                               f"{mention}")
        embed.description = embed_desc
        embed = await stw.add_requested_footer(ctx, embed)
        return embed

    async def add_default_page(self, ctx, embed_colour):
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"),
                              description=f"\u200b\n**To use a command mention the bot, then type the name and arguments after e.g:** {await stw.mention_string(self.client, 'reward 7')}\n\u200b\n\u200b")

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
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"),
                              description="\u200b")

        if inputted_command not in self.client.command_name_list:
            embed = await self.add_default_page(ctx, embed_colour)
        else:
            command_retrieved = self.client.command_dict[self.client.command_name_dict[inputted_command]]
            embed = await self.add_big_command_info(ctx, embed, command_retrieved)

        return embed

    async def select_options_commands(self, ctx):
        options = []

        for command in self.client.commands:
            try:
                if not command.extras["dev"]:
                    options.append(
                        discord.SelectOption(label=command.name, value=command.name, description=stw.truncate(command.brief, 100),
                                             emoji=self.emojis[command.extras['emoji']], default=False)
                    )
                else:
                    if ctx.author.id in self.client.config["devs"]:
                        options.append(
                            discord.SelectOption(label=command.name, value=command.name, description=stw.truncate(command.brief, 100),
                                                 emoji=self.emojis[command.extras['emoji']], default=False)
                        )
            except KeyError:
                options.append(
                    discord.SelectOption(label=command.name, value=command.name, description=stw.truncate(command.brief, 100),
                                         emoji=self.emojis[command.extras['emoji']], default=False)
                )

        return options

    async def help_command(self, ctx, command, slash=False):
        embed = await self.help_embed(ctx, command)
        help_options = [discord.SelectOption(label="all", value="main_menu",
                                             description="Return to viewing all available commands",
                                             emoji=self.emojis['blueinfo'], default=False)]
        help_options += await self.select_options_commands(ctx)

        help_view = HelpView(ctx, help_options, self.client)
        help_view.help = self

        await stw.slash_send_embed(ctx, slash, embed, help_view)

    @ext.command(name='help',
                 aliases=['heklp',
                          'ghelp', 'hgelp',
                          'h', 'hselp', 'uelp',
                          'halp', 'heflp', 'hel',
                          'yhelp', 'hyelp', 'heop',
                          'hrelp', 'hedlp', 'helpl',
                          'huelp', 'heelp', 'hhelp',
                          'hepl', 'jelp', 'hslp',
                          'hell', 'hlp', 'ehlp',
                          'holp', 'h3elp',
                          'heslp', 'nelp',
                          'heplp', 'hwlp', 'h4lp',
                          'hekp', 'helo', 'herlp', 'yelp',
                          'help0', 'nhelp', 'helpp', 'bhelp',
                          'heolp', 'huh', 'hbelp', 'he3lp', 'helop',
                          'hwelp', 'hdlp', '?', 'hnelp', 'hep', 'hlep',
                          'hewlp', 'h4elp', 'hrlp', 'hflp', 'jhelp', 'hdelp',
                          'hellp', 'elp', 'helkp', 'hjelp', 'helpo', 'how', 'hel0',
                          'hfelp', 'h3lp', 'hepp', 'hel0p', 'belp', 'uhelp', 'gelp', 'he4lp', '/help', '/h', '/how',
                          '/?'],
                 extras={'emoji': "info",
                         'args': {'command': "The name of a command to display detailed information on (Optional)"},
                         "dev": False},
                 brief="An interactive view of all available commands",
                 description="This command provides an interactive interface to view all available commands, and help for how to use each command. The select menu is only available to the author of the command, and will display more detailed information of the selected command. If no command is selected, brief info about all available command will be displayed.")
    async def help(self, ctx, command=None):
        await self.help_command(ctx, str(command).lower())

    async def get_bot_commands(self, actx: discord.AutocompleteContext):

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

        await self.help_command(ctx, str(command).lower(), True)

    # hello command

    async def hello_command(self, ctx):
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour,
                              title=await stw.add_emoji_title(self.client, "STW Daily", "calendar"),
                              description=f"""\u200b\nHello! I'm Save The World Daily, A bot which collects your Fortnite: Save The World daily rewards via Discord. [If you have any questions or issues join us here]({self.client.config["support_url"]}), [If you want to invite the bot press here!](https://tinyurl.com/stwdailyinvite)\n\u200b""")

        embed = await stw.add_requested_footer(ctx, embed)

        embed.add_field(name="To check out my commands use:", value=await stw.mention_string(self.client,
                                                                                             "help") + "\n\u200b\n[**To view the privacy policy and terms of use click here**](https://sites.google.com/view/stwdaily/legal-info)\n\u200b")
        embed.add_field(name="Disclaimer:",
                        value="Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. All rights reserved by Epic. This material is not official and is not endorsed by Epic.\n\u200b",
                        inline=False)
        embed = await stw.set_thumbnail(self.client, embed, "calendar")
        await ctx.channel.send(embed=embed)

    # the harder you climb the harder you fall
    @ext.Cog.listener()
    async def on_message(self, message):
        self_id = self.client.user.id

        # simple checker to see if the hello command should be triggered or not
        if self_id in message.raw_mentions:
            stripped_message = await stw.strip_string(message.content)

            if len(stripped_message) == len(str(self_id)):
                await self.hello_command(message)
                return


def setup(client):
    client.add_cog(Help(client))

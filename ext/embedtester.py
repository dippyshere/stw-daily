"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is the cog for the power level command. currently for testing only :3
"""

import orjson

import discord
import discord.ext.commands as ext
from discord import SelectOption as Option

import stwutil as stw


class ModalTest(discord.ui.Modal):
    """
    The view for the llama command.
    """

    def __init__(self, ctx, client):
        super().__init__(title="Modal Testing", timeout=0)
        self.ctx = ctx
        self.client = client
        setting_input = discord.ui.InputText(placeholder="placeholder", label="label", value="value")
        setting_input2 = discord.ui.InputText(placeholder="placeholder2", label="label2", required=False,
                                              value="value2")
        setting_input3 = discord.ui.InputText(placeholder="placeholder3", label="label3", required=False,
                                              value="value3", style=discord.InputTextStyle.long)
        self.add_item(setting_input)
        self.add_item(setting_input2)
        self.add_item(setting_input3)


class ViewTest(discord.ui.View):
    """
    The view for the llama command.
    """

    def __init__(self, ctx, client):
        super().__init__(timeout=0)
        self.ctx = ctx
        self.client = client

    # @discord.ui.select(
    #     placeholder="select menu testing",
    #     options=[
    #         Option(label="Option 1", value="1", description="This is option 1", emoji="👍", default=True),
    #         Option(label="Option 2", value="2", description="This is option 2", emoji="👎"),
    #         Option(label="Option 3", value="3", description="This is option 3", emoji="🤷"),
    #     ]
    # )
    # @discord.ui.select(discord.ComponentType.channel_select, placeholder="select menu testing", max_values=25)
    # async def selected_option(self, select, interaction):
    #     """
    #     Called when a help page is selected.
    #
    #     Args:
    #         select: The select menu that was used.
    #         interaction: The interaction that was used.
    #     """
    #     await interaction.response.send_message(f"You selected {select.values[0]}")
    @discord.ui.button(label="open modal", style=discord.ButtonStyle.primary)
    async def button_test(self, button, interaction):
        """
        Called when a help page is selected.

        Args:
            button: The button that was used.
            interaction: The interaction that was used.
        """
        await interaction.response.send_modal(modal=ModalTest(self.ctx, self.client))


class EmbedTester(ext.Cog):
    """
    Cog for the power level command idk
    """

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]

    async def et_command(self, ctx, title, desc, prompt_help, prompt_authcode, prompt_newcode, command, error_level,
                         title_emoji, thumbnail, colour, add_auth_gif, auth_push_strong, desired_lang, promptauth_key):
        """
        The embed tester command

        Args:
            ctx: The context of the command
            title: The title of the embed
            desc: The description of the embed
            prompt_help: The help prompt of the embed
            prompt_authcode: The authcode prompt of the embed
            prompt_newcode: The new authcode prompt of the embed
            command: The command to be run
            error_level: The error level of the embed
            title_emoji: The emoji to be used in the title
            thumbnail: The thumbnail of the embed
            colour: The colour of the embed
            add_auth_gif: Whether to add the auth gif to the embed
            auth_push_strong: Whether to push the authcode strong
            desired_lang: The desired language of the embed
            promptauth_key: The promptauth key of the embed

        Returns:
            None
        """
        prompt_help = prompt_help == "True"
        prompt_authcode = prompt_authcode == "True"
        prompt_newcode = prompt_newcode == "True"
        add_auth_gif = add_auth_gif == "True"
        auth_push_strong = auth_push_strong == "True"
        embed = await stw.create_error_embed(self.client, ctx, title, desc, prompt_help, prompt_authcode,
                                             prompt_newcode, command, error_level, title_emoji, thumbnail, colour,
                                             add_auth_gif, auth_push_strong, desired_lang, promptauth_key)
        view = ViewTest(ctx, self.client)
        return await stw.slash_send_embed(ctx, self.client, embed, view=view)

    @ext.command(name='embedtester',
                 aliases=['et'],
                 extras={'emoji': "spongebob", "args": {
                     'title': 'Title for the embed (Optional)',
                     'description': 'Description of the embed (Optional)',
                     'prompt_help': 'Help prompt for the embed (Optional)',
                     'prompt_authcode': 'Authcode prompt for the embed (Optional)',
                     'prompt_newcode': 'New authcode prompt for the embed (Optional)',
                     'command': 'Command to be run (Optional)',
                     'error_level': 'Error level of the embed (Optional)',
                     'title_emoji': 'Emoji to be used in the title (Optional)',
                     'thumbnail': 'Thumbnail of the embed (Optional)',
                     'colour': 'Colour of the embed (Optional)',
                     'add_auth_gif': 'Whether to add the auth tutorial gif to the embed (Optional)',
                     'auth_push_strong': 'Whether to strongly advise usor to get code (Optional)',
                     'desired_lang': 'Desired language of the embed (Optional)',
                     'promptauth_key': 'language key to use for prompt auth (Optional)'},
                         "dev": True},
                 brief="Construct and send an error embed from provided arguments",
                 description=(
                         "This command allows you to construct an error embed from provided arguments. "
                         "⦾ Please note that this for development purposes only "
                         "<:TBannersIconsBeakerLrealesrganx4:1028513516589682748>"))
    async def embedtester(self, ctx, title=None, desc=None, prompt_help=False, prompt_authcode=True,
                          prompt_newcode=False, command="", error_level=1, title_emoji=None, thumbnail=None,
                          colour=None, add_auth_gif=False, auth_push_strong=False, desired_lang="en",
                          promptauth_key="util.error.embed.promptauth.strong1"):
        """
        This function is the entry point for the embedtest command when called traditionally

        Args:
            ctx: The context of the command
            title: The title of the embed
            desc: The description of the embed
            prompt_help: The help prompt of the embed
            prompt_authcode: The authcode prompt of the embed
            prompt_newcode: The new authcode prompt of the embed
            command: The command to be run
            error_level: The error level of the embed
            title_emoji: The emoji to be used in the title
            thumbnail: The thumbnail of the embed
            colour: The colour of the embed
            add_auth_gif: Whether to add the auth gif to the embed
            auth_push_strong: Whether to push the authcode strong
            desired_lang: The desired language of the embed
            promptauth_key: The promptauth key of the embed
        """

        await self.et_command(ctx, title, desc, prompt_help, prompt_authcode, prompt_newcode, command,
                              int(error_level), title_emoji, thumbnail, colour, add_auth_gif, auth_push_strong,
                              desired_lang, promptauth_key)


def setup(client):
    """
    This function is called when the cog is loaded via load_extension

    Args:
        client: The bot client
    """
    client.add_cog(EmbedTester(client))

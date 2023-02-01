"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is a custom system for i18n (internationalisation) for STW Daily using a single JSON file
"""
import orjson
import babel
from ext.profile.bongodb import get_user_document


def get_plural_form(count):
    """
    Gets the plural form of a language

    Args:
        count (int): The count to use to determine the plural form

    Returns:
        str: The plural form of the language
    """

    if count == 1:
        return "one"
    else:
        return "many"


class I18n:
    """
    I18n class for internationalisation
    """

    def __init__(self):
        # load the i18n json file
        with open(f"lang/i18n.json", "rb") as f:
            self.i18n_json = orjson.loads(f.read())

    def get(self, key, lang, *args):  # hiiiiiiiiiiiiiiiii
        """
        Gets a string from the i18n json file

        Args:
            key (str): The key of the string in the i18n json file
            lang (str): The language to get the string in
            *args: The arguments to format the string with

        Returns:
            str: The string in the specified language
        """

        # args = [f"{arg:,}" if isinstance(arg, int) else arg for arg in args]

        try:
            # get the string from the i18n json file
            string = self.i18n_json[lang][key]
        except KeyError:
            # if string not found, first try to get the string in english
            try:
                string = self.i18n_json["en"][key]
            except KeyError:
                # if string not found in english, return the key
                return key

        try:
            # format the string with arguments
            return string.format(*args)
        except IndexError:
            # if the string has no arguments but arguments were given, just return the string
            return string

    def get_langs(self):
        """
        Gets a list of the available languages

        Returns:
            list: A list of the available languages
        """
        # get the list of available languages
        return list(self.i18n_json.keys())

    def get_langs_str(self):
        """
        Gets a string of the available languages

        Returns:
            str: A string of the available languages
        """
        # get the string of available languages
        return ", ".join(self.get_langs())

    def is_lang(self, lang):
        """
        Checks if a language is valid

        Args:
            lang (str): The language to check

        Returns:
            bool: True if the language is valid, False if the language is not valid
        """
        # check if the language is valid
        return lang in self.get_langs()

    def resolve_plural(self, lang, key, count):
        """
        Resolves a plural string from the i18n json file

        Args:
            lang (str): The language to get the string in
            key (str): The key of the string in the i18n json file
            count (int): The count to use to determine the plural form

        Returns:
            str: The plural string in the specified language
        """
        # get the plural string from the i18n json file
        plural_string = self.i18n_json[lang]["plural"][key]

        # get the plural form
        plural_form = get_plural_form(count)

        # get the plural string from the plural form
        plural_string = plural_string[plural_form]

        try:
            # format the string with the count
            return plural_string.format(count)
        except IndexError:
            # if the string has no arguments, return the string
            return plural_string

    async def get_desired_lang(self, client, ctx):
        """
        Calculates the language to use based on the user's preferred language and the server's preferred language

        Args:
            client (discord.Client): The discord client
            ctx (discord.ext.commands.Context): The context to get the language from

        Returns:
            str: The desired language
        """
        # get the user's preferred language
        try:
            user_profile = await get_user_document(ctx, client, ctx.author.id)
            profile_language = user_profile["profiles"][str(user_profile["global"]["selected_profile"])]["settings"][
                "language"]
            if profile_language == "auto" or not self.is_lang(profile_language):
                profile_language = None
        except:
            profile_language = None
        try:
            interaction_language = ctx.interaction.locale
            if not self.is_lang(interaction_language):
                interaction_language = None
        except:
            interaction_language = None
        try:
            guild_language = ctx.guild.preferred_locale
            if not self.is_lang(guild_language):
                guild_language = None
        except:
            guild_language = None

        # return the desired language
        return profile_language or interaction_language or guild_language or "en"

    def construct_slash_dict(self, key):
        """
        Constructs a dict of all the localised strings for a slash commands property

        Args:
            key (str): The key to build a dict for

        Returns:
            dict: The localised dict
        """
        # construct the slash dict
        slash_dict = {}
        for lang in self.get_langs():
            if lang == "en":
                slash_dict["en-US"] = self.get(key, lang)
                slash_dict["en-GB"] = self.get(key, lang)
            elif lang == "zh-CHS":
                slash_dict["zh-CN"] = self.get(key, lang)
            elif lang == "zh-CHT":
                slash_dict["zh-TW"] = self.get(key, lang)
            else:
                slash_dict[lang] = self.get(key, lang)
        return slash_dict

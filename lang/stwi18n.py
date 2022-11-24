"""
STW Daily Discord bot Copyright 2022 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file is a custom system for i18n (internationalisation) for STW Daily using a single JSON file
"""

import json
import os


class I18n:
    """
    I18n class for internationalisation
    """

    def __init__(self):
        # load the i18n json file
        with open(f"lang/i18n.json") as f:
            self.i18n_json = json.load(f)

    def get(self, key, lang, *args):
        """
        Gets a string from the i18n json file

        Args:
            key (str): The key of the string in the i18n json file
            lang (str): The language to get the string in
            *args: The arguments to format the string with

        Returns:
            str: The string in the specified language
        """

        # get the string from the i18n json file
        string = self.i18n_json[lang][key]

        # format the string with the arguments
        return string.format(*args)

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

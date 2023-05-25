"""
STW Daily Discord bot Copyright 2023 by the STW Daily team.
Please do not skid our hard work.
https://github.com/dippyshere/stw-daily

This file will compile all the individual pretty json files into one big json file.
"""

import json
import os


def main():
    """main function"""
    # delete i18n.json if it exists
    if os.path.exists('i18n.json'):
        os.remove('i18n.json')

    # get all json files in the current directory
    json_files = [pos_json for pos_json in os.listdir('.') if pos_json.endswith('.json')]

    # create a list of all the json files
    json_list = {}
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as file:
            json_list[json_file.split('.')[0]] = json.load(file)[json_file.split('.')[0]]

    # sort all the keys recursively but keep it a dict
    json_list = {key: json_list[key] for key in sorted(json_list)}
    json_list = {key: {key2: json_list[key][key2] for key2 in sorted(json_list[key])} for key in json_list}

    # make en the first language for performance reasons
    json_list = {'en': json_list['en'], **json_list}

    # write the combined json file
    with open('i18n.json', 'w', encoding='utf-8') as file:
        json.dump(json_list, file, ensure_ascii=True, separators=(',', ':'))


if __name__ == '__main__':
    main()

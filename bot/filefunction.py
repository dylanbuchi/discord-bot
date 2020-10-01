import json
import re
import urllib
import os


def get_file_size(file_name):
    return os.path.getsize(f'{file_name}')


def get_clean_trigger_from(user_msg, dic):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger
    lst = re.findall(r"(?=(" + '|'.join(dic) + r"))", user_msg)
    result = ''.join(lst)
    return result


def update_trigger_file(dic, trigger_file):
    # rewrite the file when deleting
    trigger_path = f"{trigger_file}"
    json.dump(
        dic,
        open(trigger_path, 'w'),
        sort_keys=True,
        indent=4,
    )


def load_triggers_file(path):
    #load the trigger.txt file in json format and return as a
    #dictionary that stores the key: trigger with value: response
    trigger_path = f"{path}"
    return json.load(open(trigger_path))


def is_user_trigger_valid(user_msg, dic):
    # check if the trigger is valid
    trigger = get_clean_trigger_from(user_msg, dic)
    return trigger in dic


def get_json_guild_file_name(guild_name, guild_id):
    return f'{guild_name}-{guild_id}.json'


def get_json_data_from(url_):
    # get json data from web link
    with urllib.request.urlopen(url_) as url:
        data = json.loads(url.read().decode())
    return data
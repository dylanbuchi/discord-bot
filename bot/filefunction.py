import json
import re
import urllib
import os


def get_cog_path(folder, filename):
    return os.path.join(os.getcwd(), f'{folder}.{filename}')


def get_file_size(file_name):
    return os.path.getsize(f'{file_name}')


def get_absolute_file_path(folder: str, filename: str):
    return os.path.join(os.getcwd(), folder, filename)


def checksUpper(string, trig):
    r = 'none'
    if string.lower() == trig.lower():
        r = ''
        for i, s in enumerate(trig):
            if s.isupper() and string[i].islower():
                r += s.upper()
            elif s.islower() and string[i].isupper():
                r += s.lower()
            else:
                r = trig
    print(r)
    return r


def get_clean_trigger_from(user_msg: str, data: dict):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger

    result = re.findall(
        r"(?=(" + '|'.join(dict(
            (k.lower(), v) for k, v in data.items())) + r"))",
        user_msg.lower())
    if len(result) >= 1:
        string = result[0]
        result = ''
        for k in data.keys():
            result = checksUpper(string, k)
            if result != 'none':
                return result
    return 'non'


def update_local_server_file(data: dict, path: str):
    # rewrite the file when deleting

    json.dump(
        data,
        open(path, 'w'),
        sort_keys=True,
        indent=4,
    )


def load_server_file(path: str):
    #load the trigger.txt file in json format and return as a
    #dictionary that stores the key: trigger with value: response
    return json.load(open(path))


def is_user_response_valid(user_msg: str, data: dict):
    # check if the trigger is valid
    trigger = get_clean_trigger_from(user_msg, data)
    return trigger in data


def get_server_data_file_name(guild_name: str, guild_id: int):
    # return file name in a correct format
    return f'{guild_name}-{guild_id}.json'


def get_json_data_from(url_: str):
    # get json data from web link
    with urllib.request.urlopen(url_) as url:
        data = json.loads(url.read().decode())
    return data
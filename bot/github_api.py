import github
import dotenv
import os
import json
dotenv.load_dotenv()
# access token
mygithub = github.Github(os.getenv('GITHUB_AUTH'))

# name of the github repository to work on
REPO_NAME = 'discord_bot'


def update_file_in_github_repo(path, data, msg='update'):
    github_update_file(f'{path}', f"{msg} data in file {path}",
                       json.dumps(data, sort_keys=True, indent=4))


def create_file_in_github_repo(path, data):
    github_create_file(f'{path}', f"create file in {path}",
                       json.dumps(data, sort_keys=True, indent=4))


def github_get_repo(name):
    # get a repo by name
    repo = mygithub.get_user().get_repo(name)
    return repo


def github_update_file(
    #updates a file in the user's repo name
    pathfile,
    msg,
    data,
):

    repo = github_get_repo(REPO_NAME)
    sha = repo.get_contents(pathfile).sha
    repo.update_file(pathfile, msg, data, sha)


def github_create_file(pathfile, msg, data):
    repo = github_get_repo(REPO_NAME)
    repo.create_file(pathfile, msg, data)


def github_get_raw_url(pathfile):
    # return raw url link from file
    repo = github_get_repo(REPO_NAME)
    temp = repo.get_contents(pathfile).raw_data
    raw_url = temp['download_url']
    return raw_url


def github_delete_file(pathfile, msg):
    repo = github_get_repo(REPO_NAME)
    sha = repo.get_contents(pathfile).sha
    repo.delete_file(pathfile, msg, sha)

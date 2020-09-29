import github
import dotenv
import os
dotenv.load_dotenv()
# using username and passw

# access token
mygithub = github.Github(os.getenv('GITHUB_AUTH'))


def get_repo(name):
    # get a repo by name
    repo = mygithub.get_user().get_repo(name)
    return repo


def github_file_update(
    #updates a file in the user's repo name
    reponame,
    pathfile,
    update_message,
    data,
):

    repo = get_repo(reponame)
    sha = repo.get_contents(pathfile).sha
    repo.update_file(pathfile, update_message, data, sha)


def github_create_file(reponame, pathfile, msg, data):
    repo = get_repo(reponame)
    repo.create_file(pathfile, msg, data)


def get_raw_url(reponame, pathfile):

    repo = get_repo(reponame)
    dic = repo.get_contents(pathfile).raw_data
    raw_url = dic['download_url']
    return raw_url


def github_delete_file(reponame, pathfile, msg):
    repo = get_repo(reponame)
    sha = repo.get_contents(pathfile).sha
    repo.delete_file(pathfile, msg, sha)

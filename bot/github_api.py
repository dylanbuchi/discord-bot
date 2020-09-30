import github
import dotenv
import os

dotenv.load_dotenv()
# access token
mygithub = github.Github(os.getenv('GITHUB_AUTH'))


def github_get_repo(name):
    # get a repo by name
    repo = mygithub.get_user().get_repo(name)
    return repo


def github_update_file(
    #updates a file in the user's repo name
    reponame,
    pathfile,
    msg,
    data,
):

    repo = github_get_repo(reponame)
    sha = repo.get_contents(pathfile).sha
    repo.update_file(pathfile, msg, data, sha)


def github_create_file(reponame, pathfile, msg, data):
    repo = github_get_repo(reponame)
    repo.create_file(pathfile, msg, data)


def github_get_raw_url(reponame, pathfile):
    # return raw url link from file
    repo = github_get_repo(reponame)
    temp = repo.get_contents(pathfile).raw_data
    print(temp)
    raw_url = temp['download_url']
    return raw_url


def github_delete_file(reponame, pathfile, msg):
    repo = github_get_repo(reponame)
    sha = repo.get_contents(pathfile).sha
    repo.delete_file(pathfile, msg, sha)

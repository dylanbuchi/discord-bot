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
    reponame,
    pathfile,
    update_message,
    data,
):
    #updates a file in the user's repo name
    repo = get_repo(reponame)
    sha = repo.get_contents(pathfile).sha
    repo.update_file(pathfile, update_message, data, sha)
from models import db, TrendingRepos, TrendingDevs
from api import get_trending_repos, get_trending_devs


def fill_database():
    # drop the tables of the tb
    db.drop_all()

    # create
    db.create_all()

    # get trending repos from api file that uses beautifulsoup
    trending_repos = get_trending_repos()
    trending_devs = get_trending_devs()

    # fill the database with the retrieved repositories
    for repo_data in trending_repos:
        new_repo = TrendingRepos(
            developer=repo_data['developer'],
            repo_name=repo_data['repo_name'],
            description=repo_data['description'],
            language=repo_data['language'],
            repo_link=repo_data['repo_link'],
            stargazers=repo_data['stargazers'],
            stars_today=repo_data['stars_today']
        )
        db.session.add(new_repo)

    for dev_data in trending_devs:
        dev_username = dev_data['dev_username']
        profile_link = f"https://www.github.com/{dev_username}"
        new_dev = TrendingDevs(
            dev_name=dev_data['dev_name'],
            dev_username=dev_data['dev_username'],
            dev_avatar=dev_data['dev_avatar'],
            profile_link=profile_link,
            dev_pop_proj_name=dev_data['dev_pop_proj_name'],
            dev_proj_desc=dev_data['dev_proj_desc']
        )
        db.session.add(new_dev)

    db.session.commit()


def serialized_repos():
    repos = TrendingRepos.query.all()
    # devs = TrendingDevs.query.all()

    repos_data = [
        {
            'developer': repo.developer,
            'repo_name': repo.repo_name,
            'description': repo.description,
            'language': repo.language,
            'repo_link': repo.repo_link,
            'stargazers': repo.stargazers,
            'stars_today': repo.stars_today
        }
        for repo in repos
    ]

    return repos_data 

def serialized_devs():
    devs = TrendingDevs.query.all()

    devs_data = [
        {
            'dev_name': dev.dev_name,
            'dev_username': dev.dev_username,
            'dev_avatar': dev.dev_avatar,
            'profile_link': dev.profile_link,
            'dev_pop_proj_name': dev.dev_pop_proj_name,
            'dev_proj_desc': dev.dev_proj_desc
        }
        for dev in devs
    ]

    return devs_data
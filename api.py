import requests
from bs4 import BeautifulSoup


def get_trending_repos():
    url = 'https://github.com/trending'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    repo_titles = soup.find_all('h2', class_='h3 lh-condensed')

    repos = []
    for repo in repo_titles:
        title = repo.text.strip()
        # split up the title in the h2 to use values seperately
        title_parts = title.split('/', 1)
        developer = title_parts[0].strip()
        repo_name = title_parts[1].strip()

        # the parent element of the h2 tag
        parent_element = repo.find_parent('article')

        # the p element with the specified class within the parent element
        description_element = parent_element.find(
            'p', class_='col-9 color-fg-muted my-1 pr-4')

        # get the description text
        description = description_element.text.strip() if description_element else ""

        language = repo.find_next(
            'span', class_='d-inline-block ml-0 mr-3').text.strip()
        stargazers = repo.find_next(
            'a', class_='Link--muted d-inline-block mr-3').text.strip()
        stars_today = repo.find_next(
            'span', class_='d-inline-block float-sm-right').text.strip()
        href = repo.find_next('a')['href']

        repo_data = {
            'developer': developer,
            'repo_name': repo_name,
            'description': description,
            'language': language,
            'stargazers': stargazers,
            'stars_today': stars_today,
            'repo_link': f"https://github.com{href}"
        }
        repos.append(repo_data)

    return repos


def get_trending_devs():
    url = 'https://github.com/trending/developers'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    devs = soup.find_all('article', class_='Box-row')

    trending_devs = []
    for dev in devs:
        dev_name = dev.find('h1', class_='h3 lh-condensed').text.strip()

        dev_username = dev.find('p', class_='f4 text-normal mb-1')
        if dev_username:
            dev_username = dev_username.find(
                'a', class_='Link--secondary').text.strip()
        else:
            dev_username = 'N/A'

        dev_avatar = dev.find('img', class_='avatar-user')
        if dev_avatar:
            dev_avatar = dev_avatar['src']
        else:
            dev_avatar = 'N/A'

        dev_pop_proj_name_elem = dev.find('h1', class_='h4 lh-condensed')
        if dev_pop_proj_name_elem:
            dev_pop_proj_name = dev_pop_proj_name_elem.find(
                'a', class_='css-truncate-target').text.strip()
        else:
            dev_pop_proj_name = 'N/A'

        dev_proj_desc_elem = dev.find('div', class_='f6 color-fg-muted mt-1')
        if dev_proj_desc_elem:
            dev_proj_desc = dev_proj_desc_elem.text.strip()
        else:
            dev_proj_desc = 'N/A'

        dev_data = {
            'dev_name': dev_name,
            'dev_username': dev_username,
            'dev_avatar': dev_avatar,
            'dev_pop_proj_name': dev_pop_proj_name,
            'dev_proj_desc': dev_proj_desc
        }
        trending_devs.append(dev_data)

    return trending_devs

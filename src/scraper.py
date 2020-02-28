from requests import get
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup as soup
from re import search, sub, IGNORECASE
from sys import exit

class Show():
    def __init__(self, name, href, size, seeds):

        self._name = name
        self._href = href
        self._episode = None
        self._season = None
        self._seeds = int(seeds) if seeds != '-' else 0
        self._size = size
        self.set_season_and_episode()
        self.sanitize_name()

    def sanitize_name(self):
        """ RE = 'AMZN WEB-DL|x264-mSD|WEB h264-TRUMP|HDTV x264-AVS'
        self._name = sub(RE, '', self.get_name()) """
        self._name = self.get_name().strip()

    def get_href(self):
        return self._href

    def get_size(self):
        return self._size

    def get_seeds(self):
        return self._seeds

    def set_season_and_episode(self):
        RE = r's(\d{2})e(\d{2})|(\d{1,2})x(\d{1,2})'
        match = search(RE, self._name, IGNORECASE)
        if match:
            self._season, self._episode = (int(x) for x in match.groups() if x)

    def get_episode(self):
        return self._episode

    def get_season(self):
        return self._season

    def get_name(self):
        return self._name


def get_shows(show_name):
    try:
        response = get(f"https://eztv.io/search/{show_name}")
    except ConnectionError:
        return {
            "data": None,
            "status": "Connection Error"
        }

    html = response.content
    html = soup(html, "html.parser")

    # get links
    links = html.find_all("a", attrs={
        "class":  "epinfo",
    })
    
    # get seeds
    seeds = html.find_all("td", attrs={
        "class":  "forum_thread_post_end",
    })
    seeds = [ seed.text for seed in seeds ]

    # get sizes
    sizes = list()
    RE = r'\(([\d\.]+ [MGK]B)\)'
    for link in links:
        match = search(RE, link.get('title'), IGNORECASE)
        if match:
            sizes.append(match.group(1))
        else:
            sizes.append('Unknown')

    shows = [Show(link.text, "https://eztv.io" + link.get("href"), size, seed)
             for link,size, seed in zip(links, sizes, seeds) if link]

    seasons = list(set([show.get_season()
                        for show in shows if show.get_season()]))

    return {
        "data": shows,
        'seasons': seasons,
        "status": "Success"
    }
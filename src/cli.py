from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from scraper import get_shows, get_magnet
import webbrowser


def get_search_term():
  questions = [
    {
        'type': 'input',
        'name': 'query',
        'message': 'Search:',
    }
  ]
  answers = prompt(questions)
  return answers['query']


def filter_seasons(shows, season):
  return list(show for show in shows if show.get_season() == season)


def filter_episodes(shows, episode):
  return list(show for show in shows if show.get_episode() == episode)


def get_show(shows, seasons = None):
  if not seasons:
      seasons=sorted([int(show.get_season())
                        for show in shows if show.get_season()])
  questions=[
      {
          'type': 'list',
          'name': 'season',
          'message': 'Choose Season:',
          'choices': [str(season) for season in seasons],
          'filter': lambda x: int(x)
      }
  ]
  answers = prompt(questions)
  shows = filter_seasons(shows, answers['season'])
  episodes = list(set([show.get_episode() for show in shows if show.get_episode()]))
  episodes = list(set([show.get_episode() for show in shows if show.get_episode()]))
  episodes = sorted(episodes)
  episodes = [ str(episode) for episode in episodes]
  questions = [
      {
          'type': 'list',
          'name': 'episode',
          'message': 'Choose Episode:',
          'choices': episodes,
          'filter': lambda x: int(x)
      }
  ]
  answers = prompt(questions)
  shows = filter_episodes(shows, answers['episode'])
  questions = [
      {
          'type': 'list',
          'name': 'name',
          'message': 'Choose Link:',
          'choices': (f'{show._name.strip()} ( {show.get_size()} ) ( {show.get_seeds()} seeds )' for show in shows)
      }
  ]
  answers = prompt(questions)
  show = [show for show in shows if f'{show._name.strip()} ( {show.get_size()} ) ( {show.get_seeds()} seeds )' == answers['name']][0]
  return show


if __name__ == '__main__':
  # get the show to search
  query = get_search_term()
  # get the shows from eztv servers
  shows = get_shows(query)
  # sanity check
  if shows["status"] != 'Connection Error':
    # get the seasons
    seasons = shows['seasons']
    # get the show objects from the scraper
    shows = shows['data']
    # get the show the user wants to download
    show = get_show(shows, seasons)
    print(show)
    # get the magnet link from eztv servers
    link = show.get_href()
    print(link)
    magnet = get_magnet(link)
    # sanity check
    if magnet["status"] == "Success":
      magnet = magnet["data"]
      # open the magnet link in the default app to handle magnet links
      webbrowser.open(magnet, new=0, autoraise=True)
    elif magnet["status"] == "Connection Error":
      print("Please check your internet connection.")
    elif magnet["status"] == "No Magnet Links Found":
      print("Sorry but no magnet links were found for that torrent.")
  else:
      print("Please check your internet connection.")
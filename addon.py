from xbmcswift2 import Plugin, xbmcgui, xbmc

from resources.lib import Client

plugin = Plugin()

telkkarista = Client('telkkarista.com', plugin, xbmcgui)


@plugin.route('/cachehost')
def cachehost():
  telkkarista.ui.cacheHostDialog()

@plugin.route('/live/')
def live():
  return telkkarista.ui.LiveTVView()

@plugin.route('/programs/')
def programs():
  return []

@plugin.route('/search/')
def search():
  return []

@plugin.route('/movies/')
def movies():
  return telkkarista.ui.MoviesView()

@plugin.route('/')
def index():
    indexMenu = [
        {'label': plugin.get_string(30001), 'path': plugin.url_for('live'),     'is_playable': False },
        {'label': plugin.get_string(30002), 'path': plugin.url_for('programs'), 'is_playable': False },
        {'label': plugin.get_string(30005), 'path': plugin.url_for('movies'),   'is_playable': False },
        {'label': plugin.get_string(30003), 'path': plugin.url_for('search'),   'is_playable': False },
    ]

    return indexMenu


if __name__ == '__main__':
    plugin.run()

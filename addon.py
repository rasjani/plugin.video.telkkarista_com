from xbmcswift2 import Plugin, xbmcgui, xbmc

from resources.lib import Client

plugin = Plugin()

telkkarista = Client('telkkarista.com', plugin, xbmcgui)


@plugin.route('/cachehost')
def cachehost():
  telkkarista.cacheHostDialog()

@plugin.route('/live/')
def live():
  return telkkarista.LiveTVView()

@plugin.route('/programs/')
def programs():
  return []

@plugin.route('/search/')
def search():
  return []

@plugin.route('/')
def index():
    indexMenu = [
        {'label': plugin.get_string(30001), 'path': plugin.url_for('live'),     'is_playable': False },
        {'label': plugin.get_string(30002), 'path': plugin.url_for('programs'), 'is_playable': False },
        {'label': plugin.get_string(30003), 'path': plugin.url_for('search'),   'is_playable': False },
    ]

    return indexMenu


if __name__ == '__main__':
    plugin.run()

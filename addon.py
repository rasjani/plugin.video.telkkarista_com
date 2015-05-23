from xbmcswift2 import Plugin

from resources.lib import Client

telkkarista = Client('telkkarista.com')

plugin = Plugin()


@plugin.route('/live/')
def live():
  return []

@plugin.route('/programs/')
def programs():
  return []

@plugin.route('/search/')
def search():
  return []

@plugin.route('/settings/')
def settings():
  return []


@plugin.route('/')
def index():
    indexMenu = [
        {'label': plugin.get_string(30001), 'path': plugin.url_for('live'),     'is_playable': False },
        {'label': plugin.get_string(30002), 'path': plugin.url_for('programs'), 'is_playable': False },
        {'label': plugin.get_string(30003), 'path': plugin.url_for('search'),   'is_playable': False },
        {'label': plugin.get_string(30004), 'path': plugin.url_for('settings'), 'is_playable': False }
    ]

    return indexMenu


if __name__ == '__main__':
    plugin.run()

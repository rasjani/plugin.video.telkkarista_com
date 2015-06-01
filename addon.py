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

@plugin.route('/programs/<chanid>/<timescope>', name='programs_showprogramlist' )
@plugin.route('/programs/<chanid>', name='programs_showchannellist')
@plugin.route('/programs', name='programs')
def programs(chanid = None, timescope = None):
  menu = []

  if chanid == None and timescope == None:
    menu = telkkarista.ui.ProgramsChannelList()
  elif chanid != None and timescope == None:
    menu = telkkarista.ui.TimeScopeSelection(chanid)
  else:
    menu = telkkarista.ui.ProgramSelection(chanid, timescope)

  return menu



@plugin.route('/search/')
def search():
  return []

@plugin.route('/movies/')
def movies():
  return telkkarista.ui.MoviesView()

@plugin.route('/')
def index():
    return telkkarista.ui.MainMenu()


if __name__ == '__main__':
    plugin.run()

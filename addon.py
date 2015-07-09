from xbmcswift2 import Plugin, xbmcgui, xbmc

from resources.lib import Client

plugin = Plugin()

telkkarista = Client('telkkarista.com', plugin, xbmcgui, xbmc)


@plugin.route('/cachehost')
def cachehost():
  telkkarista.ui.cacheHostDialog()

@plugin.route('/live/')
def live():
  return telkkarista.ui.LiveTVView()

@plugin.route('/searchByKeyword/<token>', name="searchByKeyword")
def searchByKeyword(token = None):
  return telkkarista.ui.Search(token)

@plugin.route('/programs/<chanid>/<timescope>/<page>', name='programs_showprogramlist' )
@plugin.route('/programs/<chanid>', name='programs_showchannellist')
@plugin.route('/programs', name='programs')
def programs(chanid = None, timescope = None, page=0):
  menu = []

  if chanid == None and timescope == None:
    menu = telkkarista.ui.ProgramsChannelList()
  elif chanid != None and timescope == None:
    menu = telkkarista.ui.TimeScopeSelection(chanid)
  else:
    menu = telkkarista.ui.ProgramSelection(chanid, timescope, page)

  return menu


@plugin.route('/newsearchbykeyword')
def newsearchbykeyword():
  searchKeyword = telkkarista.ui.SearchDialog()
  if searchKeyword != None:
    telkkarista.ui.addSearchKeyword(searchKeyword)
    return searchByKeyword(searchKeyword)


@plugin.route('/search/')
def search():
  return telkkarista.ui.SearchView()

@plugin.route('/movies/<page>')
def movies( page = 0 ):
  return telkkarista.ui.MoviesView(page)

@plugin.route('/')
def index():
  if not telkkarista.user_logged_in:
    telkkarista.ui.login_fail_dialog(telkkarista.User.last_error)
    return []
  else:
    return telkkarista.ui.MainMenu()


if __name__ == '__main__':
    plugin.run()

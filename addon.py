from xbmcswift2 import Plugin, xbmcgui, xbmc

from resources.lib import Client

plugin = Plugin()

telkkarista = Client('telkkarista.com', plugin, xbmcgui, xbmc)


@plugin.route('/cachehost')
def cachehost():
  telkkarista.ui.cachehost_dialog()

@plugin.route('/live/')
def live():
  return telkkarista.ui.live_tv_view()

@plugin.route('/searchByKeyword/<token>', name="search_by_keyword")
def search_by_keyword(token=None):
  return telkkarista.ui.search(token)

@plugin.route('/programs/<chanid>/<timescope>/<page>', name='programs_showprogramlist')
@plugin.route('/programs/<chanid>', name='programs_showchannellist')
@plugin.route('/programs', name='programs')
def programs(chanid=None, timescope=None, page=0):
  menu = []

  if chanid == None and timescope == None:
    menu = telkkarista.ui.programs_channel_list()
  elif chanid != None and timescope == None:
    menu = telkkarista.ui.timescope_selection(chanid)
  else:
    menu = telkkarista.ui.program_selection(chanid, timescope, page)

  return menu


@plugin.route('/new_search_by_keyword')
def new_search_by_keyword():
  search_keyword = telkkarista.ui.search_dialog()
  if search_keyword != None:
    telkkarista.ui.add_search_keyword(search_keyword)
    return search_by_keyword(search_keyword)


@plugin.route('/search/')
def search():
  return telkkarista.ui.search_view()

@plugin.route('/movies/<page>')
def movies(page=0):
  return telkkarista.ui.movies_view(page)

@plugin.route('/')
def index():
  return telkkarista.ui.main_menu()


if __name__ == '__main__':
  plugin.run()

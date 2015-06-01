__author__ = "rasjani"
import random
import json

class Ui:
  def __init__(self, plugin, xbmcgui, client):
    self._plugin = plugin
    self._gui = xbmcgui
    self._client = client


  def ProgramsChannelList(self):
    menu = []
    streamData = sorted(self._client._streams['payload'], key=lambda k: k['streamOrder'])
    for stream in streamData:
      channelId = stream['name']
      channelName = stream['visibleName']
      menu.append({
        'label': channelName,
        'path': self._plugin.url_for('programs_showchannellist', chanid = channelId)
      })
    return menu


  def TimeScopeSelection(self, chanid):
    return [
        {'label': self._plugin.get_string(30500), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=0), 'is_playable': False },
        {'label': self._plugin.get_string(30501), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=1), 'is_playable': False },
        {'label': self._plugin.get_string(30502), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=2), 'is_playable': False },
        {'label': self._plugin.get_string(30503), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=3), 'is_playable': False },
    ]

  def ProgramSelection(self, chanid, timescope):
    timeRanges = self._client.generateTimeRange(timescope)
    menu = []
    tmp = self._client.Epg.range({"from": timeRanges[0], "to": timeRanges[1], "streams": [chanid] } )

    for program in tmp[chanid]:
      menuEntry = self._client.pidInfo(program)
      if menuEntry != None:
        menu.append(menuEntry)

    return menu


  def  MainMenu(self):
    return [
        {'label': self._plugin.get_string(30001), 'path': self._plugin.url_for('live'),     'is_playable': False },
        {'label': self._plugin.get_string(30002), 'path': self._plugin.url_for('programs'), 'is_playable': False },
        {'label': self._plugin.get_string(30005), 'path': self._plugin.url_for('movies'),   'is_playable': False },
        {'label': self._plugin.get_string(30003), 'path': self._plugin.url_for('search'),   'is_playable': False },
    ]

  def cacheHostDialog(self):
    dialog = self._gui.Dialog()
    hostList = self._client._cacheServers['payload']
    ret = dialog.select( self._plugin.get_string(30305), [u['host'] for u in hostList if u['status']=='up' ])
    if isinstance( ret, ( int, long ) ) and ret >= 0: ## cli xbmc returns non-int
      self._plugin.set_setting('cachehost', hostList[ret]['host'])

  def LiveTVView(self):
    menu = []
    streamData = self._client._streams['payload']
    currentlyRecord = self._client.Epg.current()

    streamData = sorted(streamData, key=lambda k: k['streamOrder'])

    for stream in streamData:
      channelId = stream['name']
      channelName = stream['visibleName']
      plot = ''

      try:
        tmp = currentlyRecord[channelId][0]
        plot  = tmp['title']['fi'] ## Config lang to use ?
      except Exception, e:
        plot = ''

      quality = self._plugin.get_setting('streamQuality', int)
      mediaUrl = ''
      if quality == 6: # autodetect
        mediaUrl = 'https://%s/%s/live/%s.m3u8' % (self._client.streamService, self._client._sessionId, channelId) ## TODO: fix later
      else:
        mediaUrl = 'https://%s/%s/live/%s_%s.m3u8' % (self._client.streamService, self._client._sessionId, channelId, self._client.quality[quality]) ## TODO: fix later

      iconUrl = 'https://%s/%s/live/%s_small.jpg?%i' % (self._client.streamService, self._client._sessionId, channelId, random.randint(0,2e9)) ## TODO: fix later
      menu.append({
        'label': channelName,
        'thumbnail': iconUrl,
        'icon': iconUrl,
        'path': mediaUrl,
        'info_type': 'video',
        'is_playable': True,
        'info': {
          'Plot': plot,
          'PlotOutline': plot
        }
      })

    return menu


  def MoviesView(self):
    menu = []
    tmp = self._client.Epg.searchMovies()
    for movie in tmp:
      menuEntry = self._client.pidInfo(movie)
      if menuEntry != None:
        menu.append(menuEntry)

    return menu

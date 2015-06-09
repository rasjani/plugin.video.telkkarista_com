__author__ = "rasjani"
import random
import json
import datetime,dateutil.parser, dateutil.tz

class Ui:
  def __init__(self, plugin, xbmcgui, client):
    self._plugin = plugin
    self._gui = xbmcgui
    self._client = client


  def _channelLogo(self, channelId):
    return 'special://home/addons/%s/resources/media/%s.png' % ( self._client.clientName, channelId )

  def ProgramsChannelList(self):
    menu = []
    streamData = sorted(self._client._streams['payload'], key=lambda k: k['streamOrder'])
    for stream in streamData:
      channelId = stream['name']
      channelName = stream['visibleName']
      menu.append({
        'label': channelName,
        'thumbnail': self._channelLogo(channelId),
        'path': self._plugin.url_for('programs_showchannellist', chanid = channelId)
      })
    return menu


  def TimeScopeSelection(self, chanid):
    return [
        {'label': self._plugin.get_string(30500), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=0, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30501), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=1, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30502), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=2, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30503), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=3, page=0), 'is_playable': False },
    ]

  def ProgramSelection(self, chanid, timescope, page=0):
    timeRanges = self._client.generateTimeRange(timescope)
    menu = []
    tmp = self._client.Epg.range({"from": timeRanges[0], "to": timeRanges[1], "streams": [chanid] } )

    programList = sorted(tmp[chanid], key=lambda k: k['start'])

    for program in programList:
      menuEntry = self._client.pidInfo(program, False)
      if menuEntry != None:
        menu.append(menuEntry)

    return menu


  def  MainMenu(self):
    return [
        {'label': self._plugin.get_string(30001), 'path': self._plugin.url_for('live'),     'is_playable': False },
        {'label': self._plugin.get_string(30002), 'path': self._plugin.url_for('programs'), 'is_playable': False },
        {'label': self._plugin.get_string(30005), 'path': self._plugin.url_for('movies', page=0),   'is_playable': False },
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

      # iconUrl = 'https://%s/%s/live/%s_small.jpg?%i' % (self._client.streamService, self._client._sessionId, channelId, random.randint(0,2e9)) ## TODO: fix later
      menu.append({
        'label': channelName,
        'thumbnail': self._channelLogo(channelId),
        'path': mediaUrl,
        'info_type': 'video',
        'is_playable': True,
        'info': {
          'ActualIcon': self._channelLogo(channelId),
          'Plot': plot,
          'PlotOutline': plot
        }
      })

    return menu


  def getMovieList(self):
    movieList = self._plugin.get_storage('moviecache', TTL=30)
    if len(movieList.items())==0:
      tmp = self._client.Epg.searchMovies()
      for item in tmp:
        pid = item['pid']
        item['start'] = dateutil.parser.parse(item['start'])
        item['stop'] = dateutil.parser.parse(item['stop'])
        movieList[pid] = item

      movieList.sync()

    return movieList

  def MoviesView(self, page):
    menu = []
    tmpArr = []

    page = int(page)
    itemsPerPage = self._client.itemsPerPage[self._plugin.get_setting('itemsperpage', int)]

    tmp = self.getMovieList()

    for movie in tmp:
      movieEntry = tmp[movie]
      tmpArr.append(tmp[movie])

    tmpArr = sorted(tmpArr, key=lambda k: k['start'])

    startIdx = page * itemsPerPage
    endIdx = startIdx + itemsPerPage

    if endIdx > len(tmpArr):
      endIdx = len(tmpArr) - 1

    for idx in range(startIdx, endIdx):
      movie = tmpArr[idx]
      menuEntry = self._client.pidInfo(movie, True)
      if menuEntry != None:
        menu.append(menuEntry)

    if endIdx < len(tmpArr)-1:
      menu.append({'label': self._plugin.get_string(30006), 'path': self._plugin.url_for('movies', page= page + 1 ),   'is_playable': False } )

    return menu

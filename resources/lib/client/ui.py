# -*- coding: utf-8 -*-
__author__ = "rasjani"
import random
import json
from .. import utils

class Ui:

  def __init__(self, plugin, xbmcgui, xbmc, client):
    self._plugin = plugin
    self._gui = xbmcgui
    self._client = client
    self._xbmc = xbmc

  def _imageUrl(self, channelId):
    return self._xbmc.translatePath('special://home/addons/%s/resources/media/%s.png' % ( self._client.clientName, channelId ))

  def ProgramsChannelList(self):
    menu = []
    streamData = sorted(self._client._streams['payload'], key=lambda k: k['streamOrder'])
    for stream in streamData:
      channelId = stream['name']
      channelName = stream['visibleName']
      menu.append({
        'label': channelName,
        'thumbnail': self._imageUrl(channelId),
        'path': self._plugin.url_for('programs_showchannellist', chanid = channelId)
      })
    return menu

  def fail_dialog(self, error_msg):
    dialog = self._gui.Dialog()
    message = self._plugin.get_string(utils.error_message_lookup(error_msg))
    dialog.notification(self._plugin.get_string(30000), message, self._gui.NOTIFICATION_ERROR, 5000, False)


  def TimeScopeSelection(self, chanid):
    return [
        {'label': self._plugin.get_string(30500), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=0, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30501), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=1, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30502), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=2, page=0), 'is_playable': False },
        {'label': self._plugin.get_string(30503), 'path': self._plugin.url_for('programs_showprogramlist', chanid = chanid, timescope=3, page=0), 'is_playable': False },
    ]

  def ProgramSelection(self, chanid, timescope, page=0):
    timeRanges = utils.generateTimeRange(timescope)

    tmp = self._client.Epg.range({"from": timeRanges[0], "to": timeRanges[1], "streams": [chanid] } )
    self._client.populateProgramEpgData(tmp[chanid])

    programList = sorted(tmp[chanid], key=lambda k: k['start'])
    return self.ProgramList(programList, False, { 'view': 'programs', 'chanid': chanid, 'page': int(page), 'timescope': timescope}) 

  def ProgramList(self, programList, fullDate, paginationData = {}):
    page  = int(paginationData['page'])
    itemsPerPage = self._client.itemsPerPage[self._plugin.get_setting('itemsperpage', int)]
    menu = []
    startIdx = page * itemsPerPage
    endIdx = startIdx + itemsPerPage

    if endIdx > len(programList):
      endIdx = len(programList) - 1

    for idx in range(startIdx, endIdx):
      menuEntry = self._client.pidInfo(programList[idx], fullDate)
      if menuEntry != None:
        menu.append(menuEntry)

    if endIdx < len(programList)-1:
      if paginationData['view'] == 'programs':
        menu.append({
          'label': self._plugin.get_string(30006),
          'path': self._plugin.url_for('programs_showprogramlist',
            chanid=paginationData['chanid'],
            timescope=paginationData['timescope'], page=page + 1 ),
          'is_playable': False
        })
      else: 
        menu.append({
          'label': self._plugin.get_string(30006),
          'path': self._plugin.url_for('searchByKeyword', page=page + 1, token=paginationData['token'] ),
          'is_playable': False
        })


    return menu

  def  MainMenu(self):
    return [
      {'label': self._plugin.get_string(30001), 'path': self._plugin.url_for('live'),     'is_playable': False,  'thumbnail': self._imageUrl('live') },
      {'label': self._plugin.get_string(30002), 'path': self._plugin.url_for('programs'), 'is_playable': False, 'thumbnail': self._imageUrl('programs') },
      {'label': self._plugin.get_string(30005), 'path': self._plugin.url_for('movies', page=0),   'is_playable': False, 'thumbnail': self._imageUrl('movies') },
      {'label': self._plugin.get_string(30003), 'path': self._plugin.url_for('search'),   'is_playable': False, 'thumbnail': self._imageUrl('search') },
    ]


  def SpeedTestDialog(self, hostlist):
    dialog  = self._gui.DialogProgress()
    dialog.create(self._plugin.get_string(30308))
    bytes = 719431

    for ix,server in enumerate(hostlist):
      progress = ix * 100 / len(hostlist)
      dialog.update(progress, server['country'], server['host'])
      if server['status'] == 'up':
        results = self._client.Cache.speedTest(server)
        hostlist[ix]['speedtest'] = results

      if dialog.iscanceled():
        break

    dialog.close()
    return hostlist

  def cacheHostDialog(self):

    hostList = self.SpeedTestDialog(self._client._cacheServers['payload'])
    dialog = self._gui.Dialog()

    selection = []
    for u in hostList:
      if 'speedtest' in u:
        if u['speedtest']['mbit'] == 0:
          u['status'] = 'error'

        line = "%s [%s] (%.2f mbits/s latency: %dms)" % (u['host'], u['status'].upper(), u['speedtest']['mbit'], u['speedtest']['latency'])
        selection.append(line)

    ret = dialog.select( self._plugin.get_string(30305), selection )
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
      mediaUrl = self._plugin.url_for('playlive', channel = channelId )

      fanartUrl = 'https://%s/%s/live/%s_large.jpg?%i' % (self._client.streamService, self._client._sessionId, channelId, random.randint(0,2e9)) ## TODO: fix later
      menu.append({
        'label': channelName,
        'thumbnail': self._imageUrl(channelId),
        'path': mediaUrl,
        'info_type': 'video',
        'is_playable': True,
        'properties': {
          'Fanart_Image': fanartUrl
        },
        'info': {
          'ActualIcon': self._imageUrl(channelId),
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
        item['start'] = utils.parseDate(item['start'])
        item['stop'] = utils.parseDate(item['stop'])
        movieList[pid] = item

      movieList.sync()

    return movieList

  def MoviesView(self, page):
    #TODO: if page is 0, repopulate the whole movie cache ? At the moment, im
    # relying only on TTL of the movie cache to expire to refetch a whole movie
    # list
    menu = []
    tmpArr = []

    page = int(page)
    itemsPerPage = self._client.itemsPerPage[self._plugin.get_setting('itemsperpage', int)]

    tmp = self.getMovieList()
    self._client.populateMovieEpgData(tmp)

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



  def addSearchKeyword(self, keyword):
    oldSearches = self._plugin.get_storage('searches')
    oldSearches[utils.now()] = keyword
    oldSearches.sync()

  def Search(self, searchKeyword, page):
    searchResults = self._plugin.get_storage('searchCache', TTL=30)

    if len(searchResults.items()) == 0 or searchKeyword not in searchResults:
      tmp = self._client.Epg.search( {"search": searchKeyword })
      searchResults[searchKeyword] = tmp
      searchResults.sync()

    searchResults[searchKeyword]

    return self.ProgramList(searchResults[searchKeyword], True, { 'view': 'search', 'token': searchKeyword, 'page': int(page)}) 

  def SearchDialog(self):
    keyboard =  self._xbmc.Keyboard()
    keyboard.doModal()
    searchEntry = keyboard.getText()
    if keyboard.isConfirmed() and searchEntry != '':
      return searchEntry
    else:
      return None

  def SearchView(self):
    oldSearches = self._plugin.get_storage('searches')
    menu = []
    menu.append({'label': self._plugin.get_string(30702), 'path': self._plugin.url_for('newsearchbykeyword' ),   'is_playable': False } )

    for searchEntry in oldSearches:
      entry = oldSearches[searchEntry]
      menu.append({'label': entry, 'path': self._plugin.url_for('searchByKeyword', page = 0, token=entry ), 'is_playable': False } )

    return menu
